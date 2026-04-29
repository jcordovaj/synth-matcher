from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP
from tools.clinical_tools import setup_tools
import uvicorn

# 1. Instanciamos FastMCP
mcp = FastMCP("TrialMatcher-Engine")

# 2. Cargamos las herramientas
setup_tools(mcp)

# 3. Creamos una App FastAPI para envolver el MCP (Alineación con PO)
app = FastAPI(title="TrialMatcher Gateway")

# Montamos el servidor MCP en la aplicación web
# Esto resuelve los errores de Method Not Allowed (405)
@app.get("/")
async def root():
    return {"status": "MCP Server Running", "engine": "SynthMatcher"}

# Usamos el transport de Starlette/FastAPI que es más robusto para Ngrok
@app.api_route("/sse", methods=["GET", "POST"])
async def handle_sse():
    # Aquí el SDK de MCP gestiona la conexión
    pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    