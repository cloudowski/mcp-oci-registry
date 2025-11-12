## MCP OCI Registry Server

A Model Context Protocol (MCP) server for querying OCI container registries. Built with the `fastmcp` framework, this server provides tools and prompts for interacting with container registries like Docker Hub, GHCR, and other OCI-compatible registries.

### Features

**Tools:**
- `ping` - Health check tool
- `list_oci_tags` - List all tags for an OCI repository
- `get_oci_details` - Fetch manifest details including architectures, digest, and annotations

**Prompts:**
- `list_tags_prompt` - Instructions for listing repository tags
- `list_architectures_prompt` - Instructions for listing supported architectures
- `list_digests_prompt` - Instructions for retrieving image digests
- `list_annotations_prompt` - Instructions for listing OCI annotations

**Additional Features:**
- Custom `NonValidatingRegistry` class that bypasses jsonschema validation for manifest lists/indexes
- Support for multi-architecture images
- Optional authentication (username/password)
- HTTP health check endpoint (`/healthz`)
- Docker support with docker-compose for development

### Requirements
- Python 3.11+
- Docker (optional, for containerized deployment)

### Installation

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Usage

#### Run in stdio mode (default)
By default, the server runs over stdio which is what most MCP clients expect:

```bash
python server.py
```

The process will wait for JSON-RPC requests over stdin/stdout. Typically you do not run it manually; it is launched by an MCP-compatible client.

#### Run with uvicorn (HTTP)
For HTTP access, use the Makefile:

```bash
make run
```

Or manually:

```bash
uvicorn server:asgi_app --host 127.0.0.1 --port 8888
```

#### Run with Docker Compose
For development with hot reload:

```bash
make compose-up
```

Or manually:

```bash
docker compose up --build
```

### Example Tool Usage

**List tags:**
```python
# Using FastMCP Client
from fastmcp import Client, FastMCP
import server

client = Client(server.mcp)
async with client:
    tags = await client.call_tool("list_oci_tags", {
        "registry": "registry-1.docker.io",
        "repository": "library/alpine"
    })
    print(tags.data)  # ['latest', '3.22.2', 'edge', ...]
```

**Get OCI details:**
```python
details = await client.call_tool("get_oci_details", {
    "registry": "registry-1.docker.io",
    "repository": "library/alpine",
    "reference": "3.22.2"
})
print(details.data)
# {
#   "digest": "sha256:...",
#   "architectures": ["amd64", "arm64", ...],
#   "annotations": {...}
# }
```

### MCP Client Configuration (Claude Desktop)

Add an entry in your Claude Desktop MCP config (`~/.cursor/mcp.json` or similar):

```json
{
  "mcpServers": {
    "mcp-oci-registry": {
      "command": "/path/to/.venv/bin/python",
      "args": [
        "/path/to/mcp-oci-registry/server.py"
      ],
      "env": {}
    }
  }
}
```

Adjust paths as needed for your environment.

### Project Layout

```
mcp-oci-registry/
├── server.py          # MCP server entrypoint
├── tools.py           # Tool functions (ping, list_oci_tags, get_oci_details)
├── prompts.py         # Prompt templates
├── registry.py        # NonValidatingRegistry class
├── __init__.py        # Package initialization
├── requirements.txt   # Python dependencies
├── Dockerfile         # Container image definition
├── docker-compose.yml # Development environment
├── Makefile          # Common operations
└── tests/            # Test suite
    ├── test_tools.py
    └── test_integration_http.py
```

### Development

**Run tests:**
```bash
make test
```

**Available Make targets:**
- `make install` - Install dependencies
- `make run` - Run server with uvicorn
- `make test` - Run test suite
- `make docker-build` - Build Docker image
- `make docker-run` - Run Docker container
- `make compose-up` - Start with docker-compose
- `make compose-down` - Stop docker-compose
- `make compose-logs` - View docker-compose logs

### Testing

The project includes both unit tests and integration tests:

- **Unit tests** (`tests/test_tools.py`) - Test individual tool functions with mocked dependencies
- **Integration tests** (`tests/test_integration_http.py`) - Test full MCP protocol flow using FastMCP Client

Run all tests:
```bash
pytest -v
```

### Extending

**Add new tools:**
1. Add the function to `tools.py`
2. Register it in `server.py`: `mcp.tool(your_function)`

**Add new prompts:**
1. Add the prompt function to `prompts.py`
2. Register it in `server.py`: `mcp.prompt(your_prompt)`

### License
Apache


