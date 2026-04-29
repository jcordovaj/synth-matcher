class ContextManager:
    @staticmethod
    def simplify_patient_data(fhir_data=None, clinical_notes=None):
        # Combina FHIR y notas en un solo perfil clínico para el LLM
        profile = "PERFIL CLÍNICO DEL PACIENTE:\n"
        if clinical_notes: profile += f"Notas: {clinical_notes}\n"
        if fhir_data: profile += f"Datos FHIR: {fhir_data}\n"
        return profile

    @staticmethod
    def format_protocol(protocol_raw):
        # Convierte cualquier formato de protocolo en una lista de reglas
        return f"PROTOCOLO DE ESTUDIO:\n{protocol_raw}"