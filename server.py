from fastmcp import FastMCP
from fastapi import FastAPI
from typing import List, Optional
import oras


mcp = FastMCP(name="fastmcp-skeleton")

def ping() -> str:
	"""
	Simple health-check tool that returns 'pong'.
	"""
	return "pong"

def list_oci_tags(
	registry: str,
	repository: str,
	username: Optional[str] = None,
	password: Optional[str] = None,
) -> List[str]:
	"""
	List tags for an OCI repository using the oras Python module.
	Args:
	- registry: e.g. "ghcr.io", "registry-1.docker.io", "localhost:5000"
	- repository: e.g. "owner/name" or "library/alpine"
	- username/password: optional basic auth
	"""
	ref = f"{registry}/{repository}"
	client = oras.client.OrasClient()
	if username and password:
		client.login(registry, username=username, password=password)
	return list(client.repo_tags(ref))

# Register tools with FastMCP without wrapping the function names
mcp.tool(ping)
mcp.tool(list_oci_tags)

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


