# FastMCP Tools Implementation Guidelines

## Core Tool Concepts

Tools are Python functions decorated with `@mcp.tool` that expose executable capabilities to LLMs. They automatically generate input/output schemas based on type annotations.

## Basic Tool Implementation

### Simple Tool Pattern
```python
@mcp.tool
def calculate_sum(a: int, b: int) -> float:
    """Add two numbers together."""
    return a + b
```

### Tool with Optional Parameters
```python
@mcp.tool
def calculate_sum(
    a: int, 
    b: int, 
    round_result: bool = False
) -> float:
    """Add two numbers with optional rounding."""
    result = a + b
    return round(result) if round_result else result
```

## Parameter Handling Standards

### Type Annotations (Required)
- Use explicit type hints for all parameters
- Support for basic types: `int`, `str`, `bool`, `float`
- Support for complex types: `list`, `dict`, custom classes
- Automatic type coercion and validation

### Parameter Validation with Pydantic
```python
from pydantic import Field

@mcp.tool
def process_data(
    data: list[float] = Field(description="List of numerical values"),
    threshold: float = Field(gt=0, description="Minimum threshold value")
) -> dict:
    """Process numerical data above threshold."""
    filtered = [x for x in data if x > threshold]
    return {
        "count": len(filtered),
        "average": sum(filtered) / len(filtered) if filtered else 0
    }
```

### Default Values and Optional Parameters
```python
@mcp.tool
def format_text(
    text: str,
    uppercase: bool = False,
    prefix: str = "",
    suffix: str = ""
) -> str:
    """Format text with optional transformations."""
    result = text
    if uppercase:
        result = result.upper()
    return f"{prefix}{result}{suffix}"
```

## Return Type Patterns

### Simple Return Types
```python
@mcp.tool
def get_timestamp() -> str:
    """Get current timestamp."""
    from datetime import datetime
    return datetime.now().isoformat()
```

### Structured Output
```python
@mcp.tool
def analyze_text(text: str) -> dict:
    """Analyze text and return statistics."""
    return {
        "word_count": len(text.split()),
        "char_count": len(text),
        "uppercase_ratio": sum(1 for c in text if c.isupper()) / len(text)
    }
```

### Content Block Generation
```python
@mcp.tool
def generate_report(data: dict) -> str:
    """Generate formatted report from data."""
    # Returns string that becomes a content block
    return f"Report: {data['title']}\nData: {data['content']}"
```

## Async Tool Implementation

### Async Tool Pattern
```python
import asyncio

@mcp.tool
async def fetch_data(url: str) -> dict:
    """Fetch data from external API."""
    # Simulated async operation
    await asyncio.sleep(0.1)
    return {"url": url, "status": "fetched"}
```

### Async with Error Handling
```python
import aiohttp

@mcp.tool
async def api_request(url: str, timeout: int = 30) -> dict:
    """Make HTTP request with timeout."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=timeout) as response:
                return {
                    "status": response.status,
                    "data": await response.json()
                }
    except asyncio.TimeoutError:
        raise ToolError("Request timed out")
    except Exception as e:
        raise ToolError(f"Request failed: {str(e)}")
```

## Error Handling Standards

### Standard Python Exceptions
```python
@mcp.tool
def divide_numbers(a: float, b: float) -> float:
    """Divide two numbers."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

### ToolError for Controlled Messaging
```python
from fastmcp import ToolError

@mcp.tool
def validate_email(email: str) -> bool:
    """Validate email format."""
    if "@" not in email:
        raise ToolError("Invalid email format: missing @ symbol")
    return True
```

### Error Detail Masking
```python
@mcp.tool
def secure_operation(data: str) -> str:
    """Perform secure operation."""
    try:
        # Sensitive operation
        result = process_sensitive_data(data)
        return result
    except Exception:
        # Mask detailed error information
        raise ToolError("Operation failed due to security constraints")
```

## Advanced Tool Features

### Dynamic Tool Management
```python
# Enable/disable tools based on conditions
@mcp.tool
def conditional_tool(input_data: str) -> str:
    """Tool that may be dynamically enabled."""
    if not tool_should_be_enabled():
        raise ToolError("Tool is currently disabled")
    return process_data(input_data)
```

### Tool Metadata and Hints
```python
@mcp.tool(
    name="custom_name",
    description="Override default description",
    tags=["data", "processing"]
)
def process_with_metadata(data: list) -> dict:
    """Process data with custom metadata."""
    return {"processed": len(data)}
```

## Standards for AI Tool Development

### Documentation Requirements
- Always provide clear, descriptive docstrings
- Document parameter purposes and constraints
- Explain return value structure and meaning
- Include usage examples in docstrings when helpful

### Type Safety
- Use strict type annotations for all parameters
- Validate inputs using Pydantic Field constraints
- Handle type coercion edge cases appropriately
- Test with various input types during development

### Error Handling Best Practices
- Provide meaningful error messages
- Use ToolError for user-facing error messages
- Log detailed errors internally while masking sensitive information
- Implement proper fallback mechanisms

### Performance Guidelines
- Use async patterns for I/O-bound operations
- Implement proper timeout handling
- Cache expensive computations when appropriate
- Monitor tool execution times and optimize bottlenecks

### Security Considerations
- Validate all inputs thoroughly
- Sanitize outputs to prevent injection attacks
- Implement rate limiting for expensive operations
- Never expose sensitive information in error messages