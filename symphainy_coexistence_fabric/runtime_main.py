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
1. Loads platform config (Layer 1: single canonical config from env)
2. Pre-boot validates required backing services (Layer 2: fail fast)
3. Creates runtime services (object graph) with that config
4. Creates FastAPI app (receives services)
5. Starts uvicorn server
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from symphainy_platform.bootstrap import load_platform_config, pre_boot_validate
from symphainy_platform.runtime.service_factory import (
    create_runtime_services,
    create_fastapi_app
)
import uvicorn
from utilities import get_logger

logger = get_logger("runtime_main")


async def _initialize_services(config):
    """Async helper to initialize services. Config is the canonical dict from Layer 1."""
    return await create_runtime_services(config)


def main():
    """
    Entry point: load config → pre-boot validate → create services → create app → start server.
    
    Config is loaded once (Layer 1); pre-boot validates all required infra (Layer 2);
    then the object graph is built with that config. No env reads inside Public Works.
    """
    import asyncio

    try:
        # Layer 1: Load canonical platform config from environment
        logger.info("🚀 Starting Symphainy Runtime Service...")
        config = load_platform_config()

        # Layer 2: Pre-boot validation (exits on first failure)
        pre_boot_validate(config)

        # Build object graph (creates all services) with canonical config
        logger.info("Building runtime object graph...")
        services = asyncio.run(_initialize_services(config))

        # Create FastAPI app (receives services, doesn't create them)
        app = create_fastapi_app(services)

        # Start server
        host = "0.0.0.0"
        port = config.get("runtime_port", 8000)
        log_level = (config.get("log_level") or "INFO").lower()

        logger.info(f"✅ Runtime service ready on {host}:{port}")
        logger.info("Starting uvicorn server...")

        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level=log_level
        )

    except SystemExit:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to start runtime service: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
