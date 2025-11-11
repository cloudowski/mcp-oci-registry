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

