# FastMCP Testing Guidelines

## Core Testing Philosophy

FastMCP servers are designed to work seamlessly with standard Python testing tools and patterns. There's "nothing special" about testing FastMCP servers beyond standard Python testing practices.

## In-Memory Testing (Recommended)

The most efficient approach is direct in-memory testing using a `Client` passed directly to the server instance.

### Basic Test Setup
```python
import pytest
from fastmcp import FastMCP, Client

@pytest.fixture
def mcp_server():
    """Create a test server instance."""
    server = FastMCP("TestServer")
    
    @server.tool
    def greet(name: str) -> str:
        """Greet a person by name."""
        return f"Hello, {name}!"
    
    @server.tool
    def add_numbers(a: int, b: int) -> int:
        """Add two numbers."""
        return a + b
    
    return server

async def test_tool_functionality(mcp_server):
    """Test basic tool functionality."""
    async with Client(mcp_server) as client:
        result = await client.call_tool("greet", {"name": "World"})
        assert result.data == "Hello, World!"
```

### Testing Multiple Tools
```python
async def test_multiple_tools(mcp_server):
    """Test multiple tools in sequence."""
    async with Client(mcp_server) as client:
        # Test greeting tool
        greeting_result = await client.call_tool("greet", {"name": "Alice"})
        assert greeting_result.data == "Hello, Alice!"
        
        # Test math tool
        math_result = await client.call_tool("add_numbers", {"a": 5, "b": 3})
        assert math_result.data == 8
```

## Pytest Configuration

### Essential Configuration
Create `pytest.ini` or add to `pyproject.toml`:

```ini
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

This enables automatic async test handling without requiring `@pytest.mark.asyncio` decorators.

### Test Structure
```python
# test_mcp_server.py
import pytest
from fastmcp import FastMCP, Client, Context

class TestMCPServer:
    @pytest.fixture
    def server(self):
        """Create server for testing."""
        mcp = FastMCP("TestServer")
        
        @mcp.tool
        async def async_operation(data: str, ctx: Context) -> str:
            """Test async operation with context."""
            await ctx.info(f"Processing: {data}")
            return f"Processed: {data}"
        
        @mcp.tool
        def sync_operation(value: int) -> int:
            """Test synchronous operation."""
            return value * 2
        
        return mcp
    
    async def test_async_tool_with_context(self, server):
        """Test async tool that uses context."""
        async with Client(server) as client:
            result = await client.call_tool("async_operation", {"data": "test"})
            assert result.data == "Processed: test"
    
    async def test_sync_tool(self, server):
        """Test synchronous tool."""
        async with Client(server) as client:
            result = await client.call_tool("sync_operation", {"value": 5})
            assert result.data == 10
```

## Error Handling Tests

### Testing Tool Errors
```python
@pytest.fixture
def error_server():
    """Server with tools that can raise errors."""
    server = FastMCP("ErrorTestServer")
    
    @server.tool
    def divide(a: float, b: float) -> float:
        """Divide two numbers."""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
    
    @server.tool
    def validate_email(email: str) -> bool:
        """Validate email format."""
        from fastmcp import ToolError
        if "@" not in email:
            raise ToolError("Invalid email format")
        return True
    
    return server

async def test_tool_error_handling(error_server):
    """Test that tool errors are properly handled."""
    async with Client(error_server) as client:
        # Test standard Python exception
        with pytest.raises(Exception) as exc_info:
            await client.call_tool("divide", {"a": 10, "b": 0})
        assert "Cannot divide by zero" in str(exc_info.value)
        
        # Test ToolError
        with pytest.raises(Exception) as exc_info:
            await client.call_tool("validate_email", {"email": "invalid-email"})
        assert "Invalid email format" in str(exc_info.value)
```

## Mocking and External Dependencies

### Mocking External Services
```python
from unittest.mock import patch, AsyncMock
import aiohttp

@pytest.fixture
def api_server():
    """Server with external API dependencies."""
    server = FastMCP("APITestServer")
    
    @server.tool
    async def fetch_user_data(user_id: int) -> dict:
        """Fetch user data from external API."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.example.com/users/{user_id}") as response:
                return await response.json()
    
    return server

async def test_external_api_mocking(api_server):
    """Test tool with mocked external API."""
    mock_response_data = {"id": 123, "name": "Test User"}
    
    with patch('aiohttp.ClientSession.get') as mock_get:
        # Setup mock
        mock_response = AsyncMock()
        mock_response.json.return_value = mock_response_data
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Test the tool
        async with Client(api_server) as client:
            result = await client.call_tool("fetch_user_data", {"user_id": 123})
            assert result.data == mock_response_data
```

### Database Mocking
```python
@pytest.fixture
def db_server():
    """Server with database operations."""
    server = FastMCP("DBTestServer")
    
    @server.tool
    def get_user(user_id: int) -> dict:
        """Get user from database."""
        # This would normally query a database
        return query_database("SELECT * FROM users WHERE id = ?", [user_id])
    
    return server

async def test_database_operations(db_server):
    """Test database operations with mocking."""
    mock_user_data = {"id": 1, "name": "John Doe", "email": "john@example.com"}
    
    with patch('__main__.query_database', return_value=mock_user_data):
        async with Client(db_server) as client:
            result = await client.call_tool("get_user", {"user_id": 1})
            assert result.data == mock_user_data
```

## Context Testing

### Testing Context Operations
```python
@pytest.fixture
def context_server():
    """Server with context-dependent tools."""
    server = FastMCP("ContextTestServer")
    
    @server.tool
    async def logged_operation(data: str, ctx: Context) -> str:
        """Operation that uses context for logging."""
        await ctx.info(f"Processing: {data}")
        await ctx.debug("Debug information")
        return f"Result: {data.upper()}"
    
    return server

async def test_context_logging(context_server):
    """Test that context operations work in tests."""
    async with Client(context_server) as client:
        result = await client.call_tool("logged_operation", {"data": "test"})
        assert result.data == "Result: TEST"
        # Note: Context logging is handled internally by the client
```

## Resource Testing

### Testing Resource Access
```python
@pytest.fixture
def resource_server():
    """Server with resources and tools that access them."""
    server = FastMCP("ResourceTestServer")
    
    @server.resource("text://config")
    def get_config() -> str:
        """Get configuration data."""
        return "config_value=123"
    
    @server.tool
    async def use_config(ctx: Context) -> dict:
        """Tool that accesses server resources."""
        config_data = await ctx.read_resource("text://config")
        return {"config": config_data}
    
    return server

async def test_resource_access(resource_server):
    """Test tool that accesses server resources."""
    async with Client(resource_server) as client:
        result = await client.call_tool("use_config", {})
        assert result.data["config"] == "config_value=123"
```

## Integration Testing

### Full Server Integration Tests
```python
@pytest.fixture
def full_server():
    """Complete server setup for integration testing."""
    server = FastMCP("IntegrationTestServer")
    
    # Add multiple tools, resources, and complex interactions
    @server.tool
    async def complex_workflow(input_data: dict, ctx: Context) -> dict:
        """Complex workflow with multiple steps."""
        await ctx.info("Starting complex workflow")
        
        # Step 1: Validate input
        if "required_field" not in input_data:
            raise ValueError("Missing required field")
        
        # Step 2: Process data
        processed = {"result": input_data["required_field"].upper()}
        await ctx.info("Processing complete")
        
        return processed
    
    return server

async def test_integration_workflow(full_server):
    """Test complete workflow integration."""
    test_input = {"required_field": "test_value"}
    
    async with Client(full_server) as client:
        result = await client.call_tool("complex_workflow", test_input)
        assert result.data["result"] == "TEST_VALUE"
```

## Performance Testing

### Load Testing Tools
```python
import asyncio
import time

async def test_tool_performance(mcp_server):
    """Test tool performance under load."""
    async def single_request():
        async with Client(mcp_server) as client:
            return await client.call_tool("add_numbers", {"a": 1, "b": 2})
    
    # Test concurrent requests
    start_time = time.time()
    tasks = [single_request() for _ in range(100)]
    results = await asyncio.gather(*tasks)
    end_time = time.time()
    
    # Verify all requests succeeded
    assert len(results) == 100
    assert all(result.data == 3 for result in results)
    
    # Check performance
    duration = end_time - start_time
    requests_per_second = 100 / duration
    print(f"Performance: {requests_per_second:.2f} requests/second")
```

## Standards for AI Testing

### Test Organization
- Group related tests in classes
- Use descriptive test names that explain what's being tested
- Create focused fixtures for different testing scenarios
- Separate unit tests from integration tests

### Coverage Guidelines
- Test both successful operations and error cases
- Test async and sync tools separately
- Verify context operations work correctly
- Test resource access patterns
- Include performance tests for critical tools

### Best Practices
- Use standard Python testing patterns and tools
- Leverage pytest fixtures for server setup
- Mock external dependencies appropriately
- Test error handling comprehensively
- Include integration tests for complex workflows
- Monitor test performance and optimize slow tests