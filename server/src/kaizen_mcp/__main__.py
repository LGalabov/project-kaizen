"""Entry point for KaizenMCP Server."""

import asyncio
import sys
from pathlib import Path

# Enable running as a script (python src/kaizen_mcp/__main__.py) for development.
sys.path.insert(0, str(Path(__file__).parent.parent))

from kaizen_mcp import database
from kaizen_mcp.config import Config, create_parser
from kaizen_mcp.server import mcp


async def run_server(config: Config) -> None:
    """Initialize the database and run the MCP server."""
    await database.initialize(config)
    
    # Run MCP server based on transport
    if config.transport == "http":
        print(f"Starting HTTP server on {config.http_host}:{config.http_port}{config.http_path}", file=sys.stderr)
        await mcp.run_http_async(
            host=config.http_host,
            port=config.http_port,
            path=config.http_path,
            stateless_http=True
        )
    else:
        print("Starting STDIO server", file=sys.stderr)
        await mcp.run_stdio_async()


def main() -> None:
    """Run the MCP server."""
    parser = create_parser()
    args = parser.parse_args()
    config = Config.from_args(args)
    
    # Show startup info
    print("KaizenMCP Server", file=sys.stderr)
    print(f"Transport: {config.transport}", file=sys.stderr)
    if config.transport == "http":
        # noinspection HttpUrlsUsage
        print(f"HTTP endpoint: http://{config.http_host}:{config.http_port}{config.http_path}", file=sys.stderr)
    print(f"Database: {config.database_url.split('@')[-1] if '@' in config.database_url else 'local'}", file=sys.stderr)
    print("", file=sys.stderr)

    asyncio.run(run_server(config))


if __name__ == "__main__":
    main()
