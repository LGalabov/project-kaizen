"""Entry point for Project Kaizen MCP Server."""

from project_kaizen.server import mcp


def main() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
