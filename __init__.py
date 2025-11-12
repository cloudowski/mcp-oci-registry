"""
MCP OCI Registry Server

A Model Context Protocol server for querying OCI container registries.
"""
try:
	from .server import mcp, asgi_app
except ImportError:
	# Allow importing when run as a script directly
	from server import mcp, asgi_app

__all__ = ["mcp", "asgi_app"]

