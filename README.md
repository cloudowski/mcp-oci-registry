## Simple MCP Server (FastMCP Skeleton)

This is a minimal skeleton of a Model Context Protocol (MCP) server implemented with the `fastmcp` framework.

### Features
- Minimal server bootstrap using `fastmcp`
- One example tool: `ping`
- Ready to run over stdio (default) or uvicorn (optional)

### Requirements
- Python 3.10+

Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run (stdio mode)
By default, the server runs over stdio which is what most MCP clients expect.

```bash
python server.py
```

The process will wait for JSON-RPC requests over stdin/stdout. Typically you do not run it manually; it is launched by an MCP-compatible client.

### Optional: Run with uvicorn (HTTP)
If you prefer to experiment over HTTP, install uvicorn and run:

```bash
pip install uvicorn
uvicorn server:asgi_app --host 127.0.0.1 --port 8765
```

Note: HTTP transport may not be supported by all MCP clients.

### Example MCP Client Configuration (Claude Desktop)
Add an entry similar to this in your Claude Desktop MCP config:

```json
{
  "mcpServers": {
    "fastmcp-skeleton": {
      "command": "/Users/tomasz/projects/cloudowski/mcp-oci-registry/.venv/bin/python",
      "args": [
        "/Users/tomasz/projects/cloudowski/mcp-oci-registry/server.py"
      ],
      "env": {}
    }
  }
}
```

Adjust paths as needed for your environment.

### Project Layout
- `server.py` — MCP server entrypoint
- `requirements.txt` — Python dependencies

### Extending
- Add more tools by using the `@app.tool()` decorator on functions.
- Provide resources and prompts if supported by your `fastmcp` version.

### License
MIT (or your preferred license)


