class MatchEngine:
    @staticmethod
    def create_reasoning_prompt(protocol, patient):
        return f"""
        INSTRUCCIÓN CLÍNICA: Compara objetivamente:
        PROTOCOLO: {protocol}
        PACIENTE: {patient}
        
        Determina elegibilidad basándote SOLO en la evidencia proporcionada.
        """