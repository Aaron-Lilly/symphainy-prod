#!/usr/bin/env python3
"""
Symphainy Platform - Main Entry Point

Week 1: Runtime Plane v0
- Runtime Service (FastAPI)
- Session Lifecycle
- State Surface (Redis-backed)
- WAL (Write-Ahead Log)
- Saga Skeleton

No business logic. No realms imported.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import asyncio
import signal
from contextlib import asynccontextmanager
from typing import Optional

import redis.asyncio as redis
from fastapi import FastAPI
import uvicorn

from utilities import get_logger, LogLevel, LogCategory, get_clock
from config import get_env_contract
from symphainy_platform.runtime import (
    StateSurface,
    WriteAheadLog,
    SagaCoordinator,
    create_runtime_app
)

# Initialize Phase 0 utilities
env = get_env_contract()
clock = get_clock()
logger = get_logger("runtime_plane", LogLevel.INFO, LogCategory.PLATFORM)

# Global shutdown event for graceful shutdown
shutdown_event = asyncio.Event()


def signal_handler(signum, frame):
    """Handle shutdown signals (SIGTERM, SIGINT)."""
    logger.info(
        "Received shutdown signal, initiating graceful shutdown",
        metadata={"signal": signum}
    )
    shutdown_event.set()


async def create_redis_client() -> Optional[redis.Redis]:
    """
    Create Redis client if available.
    
    Returns:
        Redis client or None if not available
    """
    redis_url = env.REDIS_URL
    
    try:
        client = await redis.from_url(redis_url, decode_responses=True)
        # Test connection
        await client.ping()
        logger.info(
            "Connected to Redis",
            metadata={"redis_url": redis_url}
        )
        return client
    except Exception as e:
        logger.warning(
            "Redis not available, using in-memory storage",
            metadata={"error": str(e), "redis_url": redis_url}
        )
        return None


# Global references for graceful shutdown
_runtime_components = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for graceful shutdown.
    
    Handles:
    - Startup: Initialize components
    - Shutdown: Gracefully close connections and finish in-flight requests
    """
    # Startup
    logger.info("Starting Runtime Plane", metadata={"version": "0.1.0"})
    
    # Create Redis client (or None for in-memory)
    redis_client = await create_redis_client()
    use_memory = redis_client is None
    
    # Initialize components
    state_surface = StateSurface(redis_client=redis_client, use_memory=use_memory)
    wal = WriteAheadLog(redis_client=redis_client, use_memory=use_memory)
    saga_coordinator = SagaCoordinator(state_surface=state_surface)
    
    # Store references for shutdown
    _runtime_components["state_surface"] = state_surface
    _runtime_components["wal"] = wal
    _runtime_components["saga_coordinator"] = saga_coordinator
    _runtime_components["redis_client"] = redis_client
    
    storage_type = "in-memory" if use_memory else "Redis-backed"
    logger.info(
        "Runtime Plane components initialized",
        metadata={
            "state_surface": storage_type,
            "wal": storage_type,
            "saga_coordinator": "initialized"
        }
    )
    
    # Create FastAPI app
    runtime_app = create_runtime_app(
        state_surface=state_surface,
        wal=wal,
        saga_coordinator=saga_coordinator
    )
    
    # Merge routes into main app
    app.mount("/api", runtime_app)
    
    logger.info("Runtime Plane ready", metadata={"port": env.RUNTIME_PORT})
    
    yield
    
    # Shutdown
    logger.info("Shutting down Runtime Plane")
    
    try:
        # Close Redis connection
        if redis_client:
            await redis_client.aclose()
            logger.info("Redis connection closed")
        
        # Flush any pending WAL entries (if needed)
        # Note: WAL is append-only, so we just ensure Redis connection is closed
        
        logger.info("Graceful shutdown complete")
    except Exception as e:
        logger.error(
            "Error during shutdown",
            metadata={"error": str(e)},
            exc_info=e
        )


async def setup_runtime_plane() -> FastAPI:
    """
    Set up Runtime Plane components.
    
    Returns:
        FastAPI application with lifespan context
    """
    # Create FastAPI app with lifespan
    app = FastAPI(
        title="Symphainy Runtime Plane",
        description="Runtime execution kernel for Symphainy Platform",
        version="0.1.0",
        lifespan=lifespan
    )
    
    return app


def main():
    """Main entry point."""
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Get configuration from env contract
    host = "0.0.0.0"
    port = env.RUNTIME_PORT
    
    logger.info(
        "Starting Symphainy Runtime Plane",
        metadata={
            "host": host,
            "port": port,
            "version": "0.1.0",
            "container_aware": True
        }
    )
    
    # Create app (async setup)
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(setup_runtime_plane())
    
    # Run server
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=env.LOG_LEVEL.lower(),
        timeout_keep_alive=300,  # 5 minutes for long-running requests
        timeout_graceful_shutdown=30  # 30 seconds for graceful shutdown
    )


if __name__ == "__main__":
    main()
