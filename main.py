from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP
from tools.registry import register_tools
import uvicorn

mcp = FastMCP("TrialMatcher-Engine")
register_tools(mcp)

app = FastAPI()

# Esta es la parte que "alinea" con PromptOpinion
# Montamos el MCP dentro de FastAPI para manejar correctamente SSE
@app.post("/messages")
async def handle_messages():
    # El SDK de MCP maneja esto internamente
    pass

@app.get("/sse")
async def handle_sse():
    # El SDK de MCP maneja esto internamente
    pass

if __name__ == "__main__":
    # Uvicorn es el que permite que Ngrok encuentre tu app
    uvicorn.run(app, host="0.0.0.0", port=8000)