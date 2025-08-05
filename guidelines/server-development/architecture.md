# FastMCP Server Architecture Guidelines

## Core Architectural Components

### 1. Tools
- Executable functions that provide capabilities to LLMs
- Registered using decorators for clean code organization
- Support both synchronous and asynchronous operations

### 2. Resources
- Data sources accessible through standardized interfaces
- Static or dynamic content providers
- Support URI-based addressing

### 3. Resource Templates
- Parameterized data generators
- Enable dynamic resource creation based on parameters
- Useful for generating contextual data

### 4. Prompts
- Reusable message templates
- Define interaction patterns between AI and services
- Support parameterization for flexible usage

## Server Configuration Patterns

### Basic Server Setup
```python
from fastmcp import FastMCP

mcp = FastMCP(
    name="MyServer",
    instructions="Provides data analysis tools",
    include_tags={"public"}
)
```

### Configuration Options
- **name**: Server identifier
- **instructions**: Usage guidelines for AI
- **include_tags**: Filter components by tags
- **dependencies**: Specify external requirements

### Environment Configuration
- Global settings via environment variables
- Transport-specific configurations
- Authentication and security settings

## Component Registration Patterns

### Decorator-Based Registration
```python
@mcp.tool
def multiply(a: float, b: float) -> float:
    """Multiplies two numbers together."""
    return a * b

@mcp.resource("text://numbers")
def get_numbers() -> str:
    return "1, 2, 3, 4, 5"
```

### Tag-Based Organization
```python
@mcp.tool(tags=["math", "basic"])
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool(tags=["math", "advanced"])
def calculate_derivative(expression: str) -> str:
    """Calculate derivative of mathematical expression"""
    # Implementation here
    pass
```

## Modular Server Composition

### Server Combination
```python
# Combine multiple server instances
combined_server = server1 + server2 + server3
```

### Proxy Server Capabilities
- Route requests to different backend servers
- Implement load balancing and failover
- Enable service composition patterns

## Transport Architecture

### STDIO Transport (Default)
- Best for command-line integrations
- Managed by client processes
- Minimal configuration required

### HTTP Transport (Recommended)
- Modern web-based deployment
- Better for production environments
- Supports RESTful API patterns

### Configuration Example
```python
if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8000,
        path="/mcp/"
    )
```

## Advanced Architecture Features

### Middleware Support
- Request/response transformation
- Authentication and authorization
- Logging and monitoring integration

### OpenAPI Integration
- Automatic FastAPI integration
- Swagger documentation generation
- RESTful API exposure

### Custom Serialization
- Support for custom data types
- Flexible input/output formatting
- Integration with existing data models

## Standards for AI Server Architecture

### Design Principles
- Keep components loosely coupled
- Use clear naming conventions
- Implement proper error boundaries
- Design for scalability and maintainability

### Performance Considerations
- Use async operations for I/O-bound tasks
- Implement proper caching strategies
- Monitor resource usage and optimization opportunities

### Security Guidelines
- Validate all inputs at component boundaries
- Implement proper authentication mechanisms
- Use secure transport configurations
- Follow principle of least privilege