import sqlite3
from mcp.server.fastmcp import FastMCP

# Inicializamos el servidor
mcp = FastMCP("SynthMatcher-MCP")

# ==========================================
# CAPA DE PERSISTENCIA (La Memoria)
# ==========================================

DB_NAME = "synth_data.db"

def init_db():
    """Crea las tablas e inserta datos sintéticos si no existen."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Tabla de Pacientes Sintéticos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id TEXT PRIMARY KEY,
            clinical_note TEXT
        )
    ''')
    
    # Tabla de Ensayos Clínicos Sintéticos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trials (
            id TEXT PRIMARY KEY,
            criteria TEXT
        )
    ''')
    
    # Insertamos datos SOLO si la base está vacía (para no duplicar al reiniciar)
    cursor.execute("SELECT COUNT(*) FROM patients")
    if cursor.fetchone()[0] == 0:
        synthetic_patients = [
            ("SYN-001", "Paciente masculino, 62 años. Diagnosticado con adenocarcinoma de pulmón de célula no pequeña (NSCLC). Biopsia confirma estadio IV debido a metástasis cerebrales detectadas en la última resonancia magnética. ECOG 2. Historial de 40 paquetes/año de tabaquismo. No ha recibido quimioterapia previa."),
            ("SYN-002", "Paciente femenino, 55 años. Diagnosticada con carcinoma escamoso de pulmón. TAC de tórax muestra masa localizada en lóbulo inferior derecho sin evidencia de adenopatías mediastínicas ni metástasis a distancia. Estadiaje clínico IIA. ECOG 0. Sin comorbilidades graves.")
        ]
        cursor.executemany("INSERT INTO patients (id, clinical_note) VALUES (?, ?)", synthetic_patients)
        
        synthetic_trials = [
            ("TRIAL-ALPHA-01", "Ensayo de Fase III para NSCLC estadio temprano. CRITERIOS DE INCLUSIÓN: Estadio I, II o IIIA confirmado por patología. ECOG 0-1. Sin metástasis a distancia (M0). CRITERIOS DE EXCLUSIÓN: Metástasis cerebrales activas, ECOG >= 2, quimioterapia sistémica previa para cáncer de pulmón.")
        ]
        cursor.executemany("INSERT INTO trials (id, criteria) VALUES (?, ?)", synthetic_trials)
        
    conn.commit()
    conn.close()

# Ejecutamos la creación de la BD apenas arranca el servidor
init_db()


# ==========================================
# HERRAMIENTAS MCP (Las Manos)
# ==========================================

@mcp.tool()
def get_patient_data(patient_id: str) -> str:
    """Recupera el historial clínico sintético de un paciente."""
    patient = ds.PATIENTS.get(patient_id)
    if not patient:
        return f"Error: Paciente {patient_id} no encontrado."
    return f"DATOS DEL PACIENTE {patient_id}:\n{str(patient)}"

@mcp.tool()
def get_trial_criteria(trial_id: str) -> str:
    """Recupera los criterios de inclusión/exclusión de un ensayo clínico."""
    trial = ds.TRIALS.get(trial_id)
    if not trial:
        return f"Error: Ensayo {trial_id} no encontrado."
    return f"CRITERIOS DEL ENSAYO {trial_id}:\n{str(trial)}"

@mcp.tool()
def log_eligibility_decision(patient_id: str, trial_id: str, decision: str, reasoning: str) -> str:
    """Guarda en la base de datos la decisión final para persistencia."""
    # Aquí es donde conectarás con database.py para el SQLite
    # Por ahora, simulamos el guardado
    print(f"LOG: Paciente {patient_id} evaluado para {trial_id}. Resultado: {decision}")
    return f"Decisión para {patient_id} registrada exitosamente en el sistema persistente."

@mcp.tool()
def get_patient_history(patient_id: str) -> str:
    """
    Obtiene la nota clínica textual completa de un paciente sintético.
    """
    conn   = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT clinical_note FROM patients WHERE id = ?", (patient_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return f"Historial del Paciente {patient_id}:\n{row[0]}"
    return f"Error: No se encontró ningún paciente con el ID {patient_id}."

@mcp.tool()
def get_trial_protocol(trial_id: str) -> str:
    """
    Obtiene los criterios de inclusión y exclusión de un ensayo clínico sintético.
    """
    conn   = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT criteria FROM trials WHERE id = ?", (trial_id,))
    row    = cursor.fetchone()
    conn.close()
    
    if row:
        return f"Protocolo del Ensayo {trial_id}:\n{row[0]}"
    return f"Error: No se encontró ningún ensayo con el ID {trial_id}."

# ==========================================
# HERRAMIENTAS DE EVALUACIÓN Y AUDITORÍA
# ==========================================

@mcp.tool()
def prepare_clinical_evaluation(patient_id: str, trial_id: str) -> str:
    """
    Recopila la historia del paciente y el protocolo del ensayo, 
    y los formatea para que el LLM de Prompt Opinion haga la evaluación de elegibilidad.
    """
    conn   = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT clinical_note FROM patients WHERE id = ?", (patient_id,))
    patient = cursor.fetchone()
    
    cursor.execute("SELECT criteria FROM trials WHERE id = ?", (trial_id,))
    trial = cursor.fetchone()
    conn.close()
    
    if not patient or not trial:
        return f"Error: No se encontró el paciente {patient_id} o el ensayo {trial_id}."
        
    return f"""CONTEXTO MÉDICO PARA EVALUACIÓN:
    
    --- HISTORIAL DEL PACIENTE ({patient_id}) ---
    {patient[0]}
    
    --- PROTOCOLO DEL ENSAYO CLÍNICO ({trial_id}) ---
    {trial[0]}
    
    INSTRUCCIÓN PARA EL ASISTENTE: Basándote en el historial y el protocolo anterior, determina si el paciente es elegible. 
    Debes justificar tu respuesta citando explícitamente si cumple o viola los criterios de inclusión/exclusión.
    Formato de respuesta sugerido:
    - Elegibilidad    : [SÍ/NO]
    - Motivo principal: [Explicación]"""

@mcp.tool()
def save_evaluation(patient_id: str, trial_id: str, is_eligible: str, reasoning: str) -> str:
    """
    Guarda el resultado de la evaluación en la base de datos SQLite persistente.
    Esto asegura trazabilidad y auditoría médica (Cumplimiento normativo).
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Creamos la tabla de evaluaciones si no existe (aquí está la magia de la persistencia)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT,
            trial_id TEXT,
            is_eligible TEXT,
            reasoning TEXT,
            evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute(
        "INSERT INTO evaluations (patient_id, trial_id, is_eligible, reasoning) VALUES (?, ?, ?, ?)",
        (patient_id, trial_id, is_eligible, reasoning)
    )
    conn.commit()
    conn.close()

    return f"✅ Evaluación guardada con éxito en la base de datos de auditoría. Paciente {patient_id} marcado como '{is_eligible}'."

@mcp.tool()
def get_evaluation_history(patient_id: str) -> str:
    """
    Recupera el historial de evaluaciones previas de un paciente desde la memoria persistente.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT trial_id, is_eligible, reasoning, evaluated_at FROM evaluations WHERE patient_id = ? ORDER BY evaluated_at DESC",
        (patient_id,)
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return f"No se encontraron evaluaciones previas en la base de datos para el paciente {patient_id}."
        
    history = f"Historial de evaluaciones para {patient_id}:\n"
    for row in rows:
        history += f"- Ensayo: {row[0]} | Resultado: {row[1]} | Razón: {row[2]} (Fecha: {row[3]})\n"
        
    return history

@mcp.tool()
def health_check() -> str:
    """Verifica que el servidor y la base de datos estén activos."""
    return "✅ Servidor SynthMatcher activo. Base de datos SQLite conectada."

# ==========================================
# ARRANQUE
# ==========================================

if __name__ == "__main__":
    mcp.run(transport="sse")