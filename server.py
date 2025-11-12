"""
MCP server entry point for OCI registry operations.

This module sets up the FastMCP server and registers all tools and prompts.
"""
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse

try:
	from . import tools
	from . import prompts
except ImportError:
	# Allow running as a script directly
	import tools
	import prompts


# Initialize FastMCP server
mcp = FastMCP(name="mcp-oci-registry")


@mcp.custom_route("/healthz", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
	"""Health check endpoint for HTTP deployments."""
	return PlainTextResponse("OK")


# Register tools
mcp.tool(tools.ping)
mcp.tool(tools.list_oci_tags)
mcp.tool(tools.get_oci_details)

# Register prompts
mcp.prompt(prompts.list_tags_prompt)
mcp.prompt(prompts.list_architectures_prompt)
mcp.prompt(prompts.list_digests_prompt)
mcp.prompt(prompts.list_annotations_prompt)

# Re-export tools for backward compatibility with tests
ping = tools.ping
list_oci_tags = tools.list_oci_tags
get_oci_details = tools.get_oci_details

# Expose ASGI app for uvicorn/gunicorn
asgi_app = mcp.http_app()

if __name__ == "__main__":
	# Default: run in stdio mode for MCP clients
	mcp.run()
	# mcp.run(transport="http", host="127.0.0.1", port=8888)


