#!/usr/bin/env python3
"""
Runtime Service Entry Point

CTO Guidance: "Where does execution begin?"

This is non-negotiable and must be boring:
- One Python file
- One function call
- Zero logic

Rule of thumb: If I can't explain the entry point in one sentence, it's wrong.

This entry point:
1. Loads config
2. Creates runtime services (object graph)
3. Creates FastAPI app (receives services)
4. Starts uvicorn server
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from symphainy_platform.config import get_env_contract
from symphainy_platform.runtime.service_factory import (
    create_runtime_services,
    create_fastapi_app
)
import uvicorn
from utilities import get_logger

logger = get_logger("runtime_main")


async def _initialize_services(config):
    """Async helper to initialize services."""
    return await create_runtime_services(config.__dict__)


def main():
    """
    Entry point: load config → create services → create app → start server.
    
    This is the only place where the object graph is built.
    """
    import asyncio
    
    try:
        # Load configuration
        logger.info("🚀 Starting Symphainy Runtime Service...")
        config = get_env_contract()
        
        # Build object graph (creates all services) - async initialization
        logger.info("Building runtime object graph...")
        services = asyncio.run(_initialize_services(config))
        
        # Create FastAPI app (receives services, doesn't create them)
        app = create_fastapi_app(services)
        
        # Start server
        host = "0.0.0.0"
        port = config.RUNTIME_PORT
        
        logger.info(f"✅ Runtime service ready on {host}:{port}")
        logger.info("Starting uvicorn server...")
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level=config.LOG_LEVEL.lower()
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start runtime service: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
