"""Entry point for Project Kaizen MCP server."""

from project_kaizen.server import mcp


def main() -> None:
    """Entry point that lets FastMCP control entire lifecycle."""
    mcp.run()


if __name__ == "__main__":
    main()
