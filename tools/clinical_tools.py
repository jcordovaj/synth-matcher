from mcp.server.fastmcp import FastMCP
from managers.context_manager import ContextManager

def setup_tools(mcp: FastMCP):
    @mcp.tool()
    def match_clinical_trial(protocol_text: str, patient_data: str, fhir_context: dict = None) -> str:
        """
        Punto de unión: Recibe el protocolo del Trial Agent y el historial del General Agent.
        No tiene reglas pre-cargadas; razona sobre lo que recibe.
        """
        full_patient = ContextManager.simplify_patient_data(fhir_data=fhir_context, clinical_notes=patient_data)
        full_protocol = ContextManager.format_protocol(protocol_text)
        
        # El prompt que se le devuelve al LLM de PO para que ejecute el match
        return f"""
        INSTRUCCIÓN DE RAZONAMIENTO MÉDICO:
        Compara el {full_protocol} contra el {full_patient}.
        
        PASOS:
        1. Identifica cada criterio (Inclusión/Exclusión).
        2. Busca evidencia en los datos del paciente. Si hay fechas, calcula duraciones.
        3. Si falta información crítica, indícalo como 'PENDIENTE DE CLARIFICACIÓN'.
        4. Si los datos son suficientes, concluye con ELEGIBLE o NO ELEGIBLE.
        """