# TrialMatcher

TrialMatcher is an MCP Server that reads unstructured clinical notes and trial PDFs to infer patient eligibility in minutes using AI tools, cutting time and cost to find right candidates for trials.

Este servidor MCP utiliza la librería FastMCP con transporte SSE (Server-Sent Events), lo que ofrece una comunicación más eficiente y una arquitectura de código más limpia comparada con el enfoque streamable_http de referencia. Para la integración, basta con exponer el servidor vía Ngrok y apuntar el cliente de PromptOpinion al endpoint /sse de la URL generada
