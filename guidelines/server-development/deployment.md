# FastMCP Deployment Guidelines

## Server Execution Methods

### 1. Direct Python Execution (Recommended for Compatibility)
```python
if __name__ == "__main__":
    mcp.run()
```
- Maximum compatibility across environments
- Standard Python execution pattern
- Easy to debug and test locally

### 2. FastMCP CLI
```bash
fastmcp run server.py
```

CLI Configuration Options:
- Specify Python version
- Add runtime dependencies
- Configure transport protocols
- Set environment variables

## Transport Configuration

### STDIO Transport (Default)
```python
mcp.run()  # Uses STDIO by default
```
**Best for:**
- Local tools and utilities
- Command-line integrations
- Development and testing
- Client-managed server processes

### HTTP Transport (Recommended for Production)
```python
mcp.run(
    transport="http",
    host="127.0.0.1",
    port=8000,
    path="/mcp/"
)
```
**Best for:**
- Web-based deployments
- Production environments
- Load balancing scenarios
- RESTful API integrations

**Configuration Options:**
- `host`: Bind address (default: 127.0.0.1)
- `port`: Service port (default: 8000)
- `path`: URL path prefix (default: /mcp/)

### SSE Transport (Deprecated)
**Note**: Server-Sent Events transport is deprecated. Use HTTP transport for new projects.

## Deployment Patterns

### Local Development
```python
from fastmcp import FastMCP

mcp = FastMCP("DevServer")

@mcp.tool
def test_function():
    return "Development mode"

if __name__ == "__main__":
    mcp.run(transport="http", port=3000)
```

### Production Deployment
```python
import os
from fastmcp import FastMCP

mcp = FastMCP("ProductionServer")

# Load configuration from environment
HOST = os.getenv("MCP_HOST", "0.0.0.0")
PORT = int(os.getenv("MCP_PORT", "8000"))
PATH = os.getenv("MCP_PATH", "/mcp/")

if __name__ == "__main__":
    mcp.run(
        transport="http",
        host=HOST,
        port=PORT,
        path=PATH
    )
```

## Async Deployment Patterns

### Async Context Usage
```python
import asyncio
from fastmcp import FastMCP

async def main():
    mcp = FastMCP("AsyncServer")
    
    @mcp.tool
    async def async_operation():
        await asyncio.sleep(1)
        return "Async result"
    
    await mcp.run_async(transport="http")

if __name__ == "__main__":
    asyncio.run(main())
```

## Custom Web Routes

### Adding Custom Endpoints
```python
from fastapi import FastAPI
from fastmcp import FastMCP

app = FastAPI()
mcp = FastMCP("CustomServer")

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@mcp.tool
def business_logic():
    return "Server response"

# Integrate FastMCP with FastAPI
app.mount("/mcp", mcp.app)
```

## Configuration Management

### Environment Variables
```bash
export MCP_HOST=0.0.0.0
export MCP_PORT=8080
export MCP_PATH=/api/mcp/
export MCP_LOG_LEVEL=INFO
```

### Configuration Files
```python
import json
from pathlib import Path

def load_config():
    config_path = Path("config.json")
    if config_path.exists():
        return json.loads(config_path.read_text())
    return {}

config = load_config()
mcp.run(**config.get("transport", {}))
```

## Dependency Management

### Runtime Dependencies
```bash
fastmcp run server.py --dependency pandas --dependency numpy
```

### Development vs Production Dependencies
```python
# requirements-dev.txt
fastmcp[dev]
pytest
black
mypy

# requirements.txt
fastmcp==2.1.0
pandas>=1.3.0
requests>=2.25.0
```

## Standards for AI Deployment

### Production Readiness Checklist
- [ ] Environment-based configuration
- [ ] Proper error handling and logging
- [ ] Health check endpoints
- [ ] Resource monitoring
- [ ] Security configurations
- [ ] Graceful shutdown handling

### Performance Guidelines
- Use HTTP transport for production workloads
- Implement connection pooling for database operations
- Configure appropriate timeout values
- Monitor memory usage and implement proper cleanup

### Security Best Practices
- Bind to localhost (127.0.0.1) for local services
- Use reverse proxy for external access
- Implement authentication for sensitive operations
- Validate all inputs at the transport layer
- Use HTTPS in production environments

### Monitoring and Observability
- Implement comprehensive logging
- Add performance metrics collection
- Configure health check endpoints
- Set up alerting for critical failures