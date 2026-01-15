#!/usr/bin/env python3
"""
Experience Service - Main Entry Point

Initializes Experience Plane and exposes API.

Version: 2.0 (New Architecture)
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import FastAPI
import uvicorn

from utilities import get_logger
from config import get_env_contract

from symphainy_platform.civic_systems.experience.experience_service import create_app

# Initialize
env = get_env_contract()
logger = get_logger("experience")


def main():
    """Main entry point."""
    host = "0.0.0.0"
    port = int(env.EXPERIENCE_PORT) if hasattr(env, "EXPERIENCE_PORT") else 8001
    
    logger.info(f"Starting Symphainy Experience Service v2.0.0 on {host}:{port}")
    
    app = create_app()
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=env.LOG_LEVEL.lower() if hasattr(env, "LOG_LEVEL") else "info"
    )


if __name__ == "__main__":
    main()
