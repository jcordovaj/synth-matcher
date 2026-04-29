import json
import sqlite3
import os
from mcp.server.fastmcp import FastMCP

# Inicializamos el servidor con el nombre exacto que verá el marketplace
mcp = FastMCP("SynthMatcher-MCP")

# Rutas a nuestros archivos de prueba (alineados al estándar FHIR y PO)
DB_NAME = "audit.db"
PROTOCOL_FILE = os.path.join("test", "protocolo_simulado.json")

# ==========================================
# CAPA DE PERSISTENCIA (La Memoria de Auditoría)
# ==========================================

def init_db():
    """Crea la tabla de auditoría usando el EXACTO esquema que PO espera."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Nota cómo el campo 'criteria_evaluation' guardará el JSON exacto 
    # que el LLM genere, cumpliendo con el estándar del hackathon.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS screening_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_mrn TEXT,
            trial_id TEXT,
            decision TEXT,
            reasoning TEXT,
            criteria_evaluation_json TEXT,
            logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()


# ==========================================
# HERRAMIENTAS MCP (El Contrato con Prompt Opinion)
# ==========================================

@mcp.tool()
def get_trial_protocol() -> str:
    """
    Obtiene el protocolo del ensayo clínico GLP-1.
    El agente de PO llamará a esto para saber qué está buscando.
    """
    try:
        with open(PROTOCOL_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        protocol_str = f"Protocolo: {data['title']} (ID: {data['trial_id']})\n\n"
        protocol_str += "CRITERIOS DE INCLUSIÓN:\n"
        for c in data["inclusion_criteria"]:
            protocol_str += f"- {c}\n"
        protocol_str += "\nCRITERIOS DE EXCLUSIÓN:\n"
        for c in data["exclusion_criteria"]:
            protocol_str += f"- {c}\n"
            
        return protocol_str
    except Exception as e:
        return f"Error leyendo el protocolo: {str(e)}"


@mcp.tool()
def prepare_fhir_evaluation(fhir_patient_string: str) -> str:
    """
    Recibe el contexto FHIR del paciente desde Prompt Opinion, lo cruza con el protocolo 
    y le da al LLM las instrucciones estrictas de razonamiento clínico (El 'AI Factor').
    """
    try:
        # Cargamos el protocolo para pasárselo junto con el paciente
        with open(PROTOCOL_FILE, "r", encoding="utf-8") as f:
            protocol = json.load(f)

        # Le damos un "System Prompt" temporal al LLM de Prompt Opinion 
        # para que sepa CÓMO debe razonar (especialmente la trampa de la metformina)
        instructions = f"""
        Eres un evaluador clínico experto. Debes evaluar al siguiente paciente para el ensayo '{protocol['title']}'.
        
        REGLA CRÍTICA DE RAZONAMIENTO: No busques solo palabras clave. Debes hacer cálculos temporales. 
        Ejemplo: Si el criterio dice '3 meses estables de metformina', debes restar la fecha de inicio del medicamento 
        de la fecha del laboratorio/evaluación para verificar si realmente han pasado al menos 90 días.
        
        CONTEXTO FHIR DEL PACIENTE (Proporcionado por Prompt Opinion):
        {fhir_patient_string}
        
        INSTRUCCIONES DE SALIDA:
        1. Analiza cada criterio de inclusión y exclusión.
        2. Formato tu respuesta al usuario de forma clara (Elegible / No Elegible).
        3. Si tienes suficientes datos, llama inmediatamente a la herramienta 'log_eligibility_decision' 
           para dejar constancia oficial en el sistema.
        """
        return instructions
    except Exception as e:
        return f"Error procesando el FHIR: {str(e)}"


@mcp.tool()
def log_eligibility_decision(
    patient_mrn: str, 
    trial_id: str, 
    decision: str, 
    reasoning: str, 
    criteria_evaluation_json: str
) -> str:
    """
    Registra la decisión final de elegibilidad en la base de datos SQLite.
    El campo 'criteria_evaluation_json' DEBE ser un string en formato JSON array 
    que siga el estándar de Prompt Opinion.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        # Validamos que el JSON que nos pasa el LLM sea válido antes de guardar
        parsed_json  = json.loads(criteria_evaluation_json)
        json_to_save = json.dumps(parsed_json) # Lo re-serializamos para asegurar formato limpio
        
        cursor.execute('''
            INSERT INTO screening_log 
            (patient_mrn, trial_id, decision, reasoning, criteria_evaluation_json) 
            VALUES (?, ?, ?, ?, ?)
        ''', (patient_mrn, trial_id, decision, reasoning, json_to_save))
        
        conn.commit()
        return f"✅ AUDITORÍA GUARDADA: Paciente {patient_mrn} marcado como '{decision}' en el ensayo {trial_id}. Registro seguro en base de datos."
    
    except json.JSONDecodeError:
        return "❌ Error de Auditoría: El LLM intentó guardar un criteria_evaluation_json inválido. Rechazado por seguridad."
    except Exception as e:
        return f"❌ Error en base de datos: {str(e)}"
    finally:
        conn.close()


# ==========================================
# ARRANQUE
# ==========================================

if __name__ == "__main__":
    mcp.run(transport="sse")