# FastMCP Quickstart Guidelines

## Essential Steps for AI Development

### 1. Basic Server Creation
```python
from fastmcp import FastMCP

mcp = FastMCP("My MCP Server")

@mcp.tool
def greet(name: str) -> str:
    """Greet a person by name"""
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run()
```

### 2. Client Interaction Pattern
```python
import asyncio
from fastmcp import Client

client = Client(mcp)

async def call_tool(name: str):
    async with client:
        result = await client.call_tool("greet", {"name": name})
        print(result)

asyncio.run(call_tool("Ford"))
```

## Server Execution Methods

### Direct Python Execution
```python
if __name__ == "__main__":
    mcp.run()
```

### CLI-Based Execution
```bash
fastmcp run my_server.py:mcp
```

## Key Development Patterns

### Tool Registration
- Use `@mcp.tool` decorator for function registration
- Automatic schema generation from type annotations
- Support for both sync and async functions

### Asynchronous Operations
- Client interactions are inherently asynchronous
- Use `async with` pattern for proper resource management
- Handle asyncio event loops appropriately

### Error Handling
```python
@mcp.tool
def divide(a: float, b: float) -> float:
    """Divide two numbers"""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

## Standards for Quickstart Implementation

### Server Configuration
- Always provide descriptive server names
- Use meaningful tool docstrings for AI understanding
- Implement proper type annotations for all parameters

### Client Usage
- Always use async context managers with clients
- Handle connection errors gracefully
- Implement proper cleanup in async operations

### Testing During Development
```python
# Quick test pattern
async def test_locally():
    async with Client(mcp) as client:
        result = await client.call_tool("greet", {"name": "Test"})
        assert result.data == "Hello, Test!"
```

## Best Practices for AI Projects
- Start with simple tools and gradually add complexity
- Test tool functionality before adding advanced features
- Use clear, descriptive function names and docstrings
- Implement proper error handling from the beginning