from fastmcp import FastMCP
from fastapi import FastAPI


mcp = FastMCP(name="fastmcp-skeleton")

@mcp.tool
def ping() -> str:
	"""
	Simple health-check tool that returns 'pong'.
	"""
	return "pong"


# FastAPI application (HTTP)
api = FastAPI(title="FastMCP + FastAPI")

@api.get("/healthz")
def healthz() -> dict:
	"""
	Liveness probe for HTTP server.
	"""
	return {"status": "ok"}

# Mount MCP HTTP transport under /mcp
api.mount("/mcp", mcp.http_app())

# Expose ASGI app for uvicorn/gunicorn
asgi_app = api

if __name__ == "__main__":
	# Default: run in stdio mode for MCP clients
	mcp.run()


