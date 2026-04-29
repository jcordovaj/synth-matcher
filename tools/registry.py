from mcp.server.fastmcp import FastMCP
from managers.logic_engine import MatchEngine

def register_tools(mcp: FastMCP):
    @mcp.tool()
    def execute_screening(protocol_context: str, patient_context: str):
        """Herramienta llamada por PO para cruzar datos de dos agentes."""
        return MatchEngine.create_reasoning_prompt(protocol_context, patient_context)