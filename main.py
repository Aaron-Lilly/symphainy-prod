#!/usr/bin/env python3
"""
Symphainy Platform - Main Entry Point

Clean implementation following architecture guide.
Should be < 100 lines.

Version: 2.0 (Breaking Changes - No Backwards Compatibility)
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import FastAPI
import uvicorn

from utilities import get_logger, get_clock
from symphainy_platform.config import get_env_contract

# Initialize
env = get_env_contract()
logger = get_logger("platform")
clock = get_clock()

# Initialize OpenTelemetry SDK
try:
    from symphainy_platform.foundations.public_works.adapters.telemetry_adapter import TelemetryAdapter
    
    telemetry_adapter = TelemetryAdapter(
        service_name="symphainy-platform",
        otlp_endpoint=getattr(env, "OTEL_EXPORTER_OTLP_ENDPOINT", None),
        insecure=True
    )
    if telemetry_adapter.initialize():
        telemetry_adapter.instrument_logging()
        logger.info("✅ OpenTelemetry SDK initialized")
    else:
        logger.warning("⚠️ OpenTelemetry SDK initialization failed")
except ImportError:
    logger.warning("⚠️ OpenTelemetry SDK not available (optional)")
except Exception as e:
    logger.warning(f"⚠️ OpenTelemetry SDK initialization error: {e}")

# Create FastAPI app
app = FastAPI(
    title="Symphainy Platform",
    description="Governed Execution Platform",
    version="2.0.0"
)

# Instrument FastAPI
try:
    if 'telemetry_adapter' in locals():
        telemetry_adapter.instrument_fastapi(app)
except Exception as e:
    logger.warning(f"⚠️ FastAPI instrumentation error: {e}")

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "version": "2.0.0"}

def main():
    """Main entry point."""
    host = "0.0.0.0"
    port = env.RUNTIME_PORT
    
    logger.info(f"Starting Symphainy Platform v2.0.0 on {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=env.LOG_LEVEL.lower()
    )

if __name__ == "__main__":
    main()
