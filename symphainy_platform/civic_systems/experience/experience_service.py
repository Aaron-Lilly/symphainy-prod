"""
Experience Service - FastAPI Service for User Interaction

Experience translates external interaction into intent.

WHAT (Experience Role): I translate user actions into intents
HOW (Experience Implementation): I expose REST, WebSockets, and coordinate with Runtime
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from utilities import get_logger
from .api.sessions import router as sessions_router
from .api.intents import router as intents_router
from .api.websocket import router as websocket_router


logger = get_logger("ExperienceService")


def create_app() -> FastAPI:
    """
    Create FastAPI application for Experience service.
    
    Returns:
        FastAPI application instance
    """
    app = FastAPI(
        title="Symphainy Experience Service",
        description="User interaction layer - translates user actions into intents",
        version="2.0.0"
    )
    
    # CORS for frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(sessions_router)
    app.include_router(intents_router)
    app.include_router(websocket_router)
    
    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy", "service": "experience", "version": "2.0.0"}
    
    logger.info("Experience Service application created")
    return app


# Create app instance
app = create_app()
