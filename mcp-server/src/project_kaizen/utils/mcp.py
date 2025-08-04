"""Common utilities for MCP tools including error handling and response formatting."""

import json
from typing import Any, NoReturn

from fastmcp.tools.tool import ToolResult
from mcp.types import TextContent
from pydantic import BaseModel

from .logging import log_error_with_context


def create_tool_result(output: BaseModel | dict[str, Any] | str) -> ToolResult:
    """Create standardized ToolResult from different output types."""
    if isinstance(output, BaseModel):
        # Pydantic model output
        return ToolResult(
            content=[TextContent(type="text", text=output.model_dump_json(exclude_none=True))],
            structured_content=output.model_dump(exclude_none=True)
        )
    elif isinstance(output, dict):
        # Dict output - convert to JSON
        return ToolResult(
            content=[TextContent(type="text", text=json.dumps(output, indent=2))],
            structured_content=output
        )
    else:
        # String or other output
        return ToolResult(
            content=[TextContent(type="text", text=str(output))]
        )


def handle_tool_error(e: Exception, tool_name: str, **context: Any) -> NoReturn:
    """Standard error handling for MCP tools."""
    log_error_with_context(e, {"tool": tool_name, **context})
    raise