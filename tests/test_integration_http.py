import pytest
import types
import server
from fastmcp import FastMCP, Client

@pytest.mark.asyncio
async def test_http_jsonrpc_ping():
	# Create FastMCP server with tools
	m = FastMCP(name="test-app")
	m.tool(server.ping)
	m.tool(server.list_oci_tags)
	
	# Use FastMCP Client with in-memory transport
	client = Client(m)
	async with client:
		# Call ping tool directly
		result = await client.call_tool("ping", {})
		assert result.data == "pong"


@pytest.mark.asyncio
async def test_http_jsonrpc_list_oci_alpine_tags():
	# Create FastMCP server with tools
	m = FastMCP(name="test-app-2")
	m.tool(server.ping)
	m.tool(server.list_oci_tags)
	
	# Use FastMCP Client with in-memory transport
	client = Client(m)
	async with client:
		# Call list_oci_tags tool
		result = await client.call_tool(
			"list_oci_tags",
			{
				"registry": "registry-1.docker.io",
				"repository": "library/alpine",
			},
		)
		tags = result.data
		assert isinstance(tags, list)
		assert len(tags) > 0
		
		# Assert that there are at least "edge", "3" and "latest" in the tags list
		assert "edge" in tags, "'edge' tag not found in tags"
		assert "3" in tags, "'3' tag not found in tags"
		assert "latest" in tags, "'latest' tag not found in tags"


@pytest.mark.asyncio
async def test_http_jsonrpc_get_oci_details():
	# Create FastMCP server with tools
	m = FastMCP(name="test-app-3")
	m.tool(server.ping)
	m.tool(server.list_oci_tags)
	m.tool(server.get_oci_details)
	
	# Use FastMCP Client with in-memory transport
	client = Client(m)
	async with client:
		# Call get_oci_details tool for alpine:3.22.2
		result = await client.call_tool(
			"get_oci_details",
			{
				"registry": "registry-1.docker.io",
				"repository": "library/alpine",
				"reference": "3.22.2",
			},
		)
		details = result.data
		
		# Validate architectures and digest from the actual response
		# Real alpine:3.22.2 has multiple architectures
		architectures = details.get("architectures", [])
		assert isinstance(architectures, list)
		assert len(architectures) > 0
		# Should include common architectures like amd64 and arm64
		assert "amd64" in architectures
		assert "arm64" in architectures
		# Validate digest is present and is a sha256 digest
		digest = details.get("digest")
		assert digest is not None
		assert digest.startswith("sha256:")
		# Validate annotations (may be empty)
		assert "annotations" in details
