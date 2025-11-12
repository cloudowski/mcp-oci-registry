import json
from starlette.testclient import TestClient
import types
import server
from fastmcp import FastMCP


def test_http_jsonrpc_ping():
	# Isolated FastMCP app per test to avoid reusing session manager
	m = FastMCP(name="test-app")
	m.tool(server.ping)
	m.tool(server.list_oci_tags)
	app = m.http_app()
	with TestClient(app) as client:
		# initialize session
		init_resp = client.post(
			"/mcp",
			headers={
				"Content-Type": "application/json",
				"Accept": "application/json, text/event-stream",
			},
			content=json.dumps({
				"jsonrpc": "2.0",
				"id": 1,
				"method": "initialize",
				"params": {
					"protocolVersion": "2025-06-18",
					"capabilities": {},
					"clientInfo": {"name": "pytest", "version": "0.0.1"}
				},
			}),
		)
		assert init_resp.status_code == 200
		session_id = init_resp.headers.get('mcp-session-id')
		assert session_id is not None
		assert session_id != ""

		# tools/call ping with session header
		resp = client.post(
			"/mcp",
			headers={
				"Content-Type": "application/json",
				"Accept": "application/json, text/event-stream",
				"mcp-session-id": session_id,
			},
			content=json.dumps({
				"jsonrpc": "2.0",
				"id": 2,
				"method": "tools/call",
				"params": {"name": "ping", "arguments": {}},
			}),
		)
		assert resp.status_code == 200
		lines = resp.text.split('\n')
		data_line = next((line for line in lines if line.startswith('data: ')), None)
		
		assert data_line is not None, "No data line found in response"
		data = json.loads(data_line.split('data: ')[1])

		assert data.get("jsonrpc") == "2.0"
		assert data.get("id") == 2
		# print(data)
		assert data.get("result").get("structuredContent").get("result") == "pong"


def test_http_jsonrpc_list_oci_alpine_tags(monkeypatch):
	m = FastMCP(name="test-app-2")
	m.tool(server.ping)
	m.tool(server.list_oci_tags)
	app = m.http_app()
	with TestClient(app) as client:
		# initialize session
		init_resp = client.post(
			"/mcp",
			headers={
				"Content-Type": "application/json",
				"Accept": "application/json, text/event-stream",
			},
			content=json.dumps({
				"jsonrpc": "2.0",
				"id": 1,
				"method": "initialize",
				"params": {
					"protocolVersion": "2025-06-18",
					"capabilities": {},
					"clientInfo": {"name": "pytest", "version": "0.0.1"}
				},
			}),
		)
		assert init_resp.status_code == 200
		session_id = init_resp.headers.get('mcp-session-id')
		assert session_id is not None
		assert session_id != ""

		# tools/call list_oci_tags with session header
		resp = client.post(
			"/mcp",
			headers={
				"Content-Type": "application/json",
				"Accept": "application/json, text/event-stream",
				"mcp-session-id": session_id,
			},
			content=json.dumps({
				"jsonrpc": "2.0",
				"id": 2,
				"method": "tools/call",
				"params": {
					"name": "list_oci_tags",
					"arguments": {
						"registry": "registry-1.docker.io",
						"repository": "library/alpine",
					},
				},
			}),
		)
		assert resp.status_code == 200
		lines = resp.text.split('\n')
		data_line = next((line for line in lines if line.startswith('data: ')), None)
		
		assert data_line is not None, "No data line found in response"
		data = json.loads(data_line.split('data: ')[1])

		assert data.get("jsonrpc") == "2.0"
		assert data.get("id") == 2
		assert "result" in data
		content = data["result"]["structuredContent"]["result"]
		print(content)
		assert isinstance(content, list)

		# assert that there are at least "edge", "3" and "latest" in the content list
		assert "edge" in content, "'edge' tag not found in content"
		assert "3" in content, "'3' tag not found in content"
		assert "latest" in content, "'latest' tag not found in content"


def test_http_jsonrpc_get_oci_details(monkeypatch):
	# Mock oras client get_manifest to emulate a multi-arch manifest list for alpine:3.22.2
	class FakeOrasClient:
		def login(self, registry: str, username: str, password: str):
			return None
		def get_manifest(self, ref: str):
			# Expect tag reference with colon
			assert ref == "registry-1.docker.io/library/alpine:3.22.2"
			manifest_list = {
				"schemaVersion": 2,
				"mediaType": "application/vnd.oci.image.index.v1+json",
				"manifests": [
					{
						"mediaType": "application/vnd.oci.image.manifest.v1+json",
						"digest": "sha256:111",
						"platform": {"architecture": "amd64", "os": "linux"},
					},
					{
						"mediaType": "application/vnd.oci.image.manifest.v1+json",
						"digest": "sha256:222",
						"platform": {"architecture": "arm64", "os": "linux"},
					},
				],
				"annotations": {"org.opencontainers.image.ref.name": "3.22.2"},
			}
			desc = {"digest": "sha256:topdigest"}
			return (manifest_list, desc)

	class FakeClientModule(types.SimpleNamespace):
		OrasClient = FakeOrasClient

	# don't monkeypatch the oras module, use the real one
	# monkeypatch.setattr(server.oras, "client", FakeClientModule)

	m = FastMCP(name="test-app-3")
	m.tool(server.ping)
	m.tool(server.list_oci_tags)
	m.tool(server.get_oci_details)
	app = m.http_app()

	with TestClient(app) as client:
		# initialize session
		init_resp = client.post(
			"/mcp",
			headers={
				"Content-Type": "application/json",
				"Accept": "application/json, text/event-stream",
			},
			content=json.dumps({
				"jsonrpc": "2.0",
				"id": 1,
				"method": "initialize",
				"params": {
					"protocolVersion": "2025-06-18",
					"capabilities": {},
					"clientInfo": {"name": "pytest", "version": "0.0.1"}
				},
			}),
		)
		assert init_resp.status_code == 200
		session_id = init_resp.headers.get('mcp-session-id')
		assert session_id

		# Call get_oci_details
		resp = client.post(
			"/mcp",
			headers={
				"Content-Type": "application/json",
				"Accept": "application/json, text/event-stream",
				"mcp-session-id": session_id,
			},
			content=json.dumps({
				"jsonrpc": "2.0",
				"id": 2,
				"method": "tools/call",
				"params": {
					"name": "get_oci_details",
					"arguments": {
						"registry": "registry-1.docker.io",
						"repository": "library/alpine",
						"reference": "3.22.2",
					},
				},
			}),
		)
		assert resp.status_code == 200
		# Parse SSE data line
		lines = resp.text.split('\n')
		data_line = next((line for line in lines if line.startswith('data: ')), None)
		assert data_line is not None, "No data line found in response"
		data = json.loads(data_line.split('data: ')[1])
		assert data.get("jsonrpc") == "2.0"
		assert data.get("id") == 2
		assert "result" in data
		result = data["result"]["structuredContent"]
		# Validate architectures and digest from the actual response
		# Real alpine:3.22.2 has multiple architectures
		architectures = result.get("architectures", [])
		assert isinstance(architectures, list)
		assert len(architectures) > 0
		# Should include common architectures like amd64 and arm64
		assert "amd64" in architectures
		assert "arm64" in architectures
		# Validate digest is present and is a sha256 digest
		digest = result.get("digest")
		assert digest is not None
		assert digest.startswith("sha256:")
		# Validate annotations (may be empty)
		assert "annotations" in result
