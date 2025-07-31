"""FastMCP server setup with all Project Kaizen MCP tools."""

from mcp.server.fastmcp import FastMCP

from .utils.logging import get_logger

# Import all tool modules to register their @mcp.tool() decorated functions
# These imports are required for side-effects (tool registration)
from .tools import knowledge, namespace, scope

# Create FastMCP server instance following CLAUDE.md pattern
mcp = FastMCP("project-kaizen")


def setup_server() -> FastMCP:
    """Configure and return the FastMCP server with all tools registered.
    
    Returns:
        FastMCP: Configured server instance with all 12 MCP tools registered.
    """
    logger = get_logger("server")
    logger.info("Initializing Project Kaizen MCP server", operation="server_setup")
    
    # Tools are automatically registered via @mcp.tool() decorators when modules are imported
    # FastMCP pattern: No explicit registration needed, decorators handle it
    
    # Reference imported modules to satisfy type checker
    tool_modules = [knowledge, namespace, scope]
    
    # Log successful tool registration (expected 12 tools total)
    expected_tool_count = 12  # 4 namespace + 3 scope + 5 knowledge tools
    logger.info(
        "FastMCP server configured with MCP tools",
        operation="server_ready",
        expected_tool_count=expected_tool_count,
        tool_module_count=len(tool_modules)
    )
    
    return mcp
