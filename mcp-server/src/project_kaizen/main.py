"""Entry point and configuration for Project Kaizen MCP server."""

import asyncio
import signal
import sys
from typing import Any

from .config import settings
from .database import db_manager
from .server import setup_server
from .utils.logging import configure_logging, get_logger


async def initialize_services() -> None:
    """Initialize all required services for the MCP server."""
    logger = get_logger("main")
    
    try:
        # Configure structured logging first
        configure_logging()
        logger.info("Logging configured", operation="logging_setup")
        
        # Initialize database connection pool
        await db_manager.initialize()
        logger.info("Database initialized", operation="database_setup")
        
    except Exception as e:
        logger.error(
            "Failed to initialize services",
            operation="service_initialization_failed",
            error_type=type(e).__name__,
            error_message=str(e)
        )
        raise


async def shutdown_services() -> None:
    """Gracefully shutdown all services."""
    logger = get_logger("main")
    
    try:
        # Close database connections
        await db_manager.close()
        logger.info("Services shutdown completed", operation="shutdown_complete")
        
    except Exception as e:
        logger.error(
            "Error during shutdown",
            operation="shutdown_failed",
            error_type=type(e).__name__,
            error_message=str(e)
        )




def run() -> None:
    """Entry point for the MCP server."""
    logger = get_logger("main")
    
    try:
        # Initialize services synchronously before starting FastMCP
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Initialize all services
            loop.run_until_complete(initialize_services())
            
            # Setup FastMCP server
            mcp_server = setup_server()
            logger.info(
                "Project Kaizen MCP server started",
                operation="server_started",
                debug_mode=settings.debug,
                log_level=settings.log_level
            )
            
            # Setup signal handlers for graceful shutdown
            def signal_handler(signum: int, frame: Any) -> None:
                logger.info(
                    "Received shutdown signal",
                    operation="signal_received",
                    signal=signum
                )
                loop.run_until_complete(shutdown_services())
                sys.exit(0)
            
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
            
            # Run the MCP server (this will create its own event loop)
            mcp_server.run()
            
        finally:
            # Cleanup
            loop.run_until_complete(shutdown_services())
            loop.close()
            
    except KeyboardInterrupt:
        logger.info("Server interrupted by user", operation="user_interrupt")
    except Exception as e:
        logger.error(
            "Server startup failed",
            operation="startup_failed",
            error_type=type(e).__name__,
            error_message=str(e)
        )
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run()
