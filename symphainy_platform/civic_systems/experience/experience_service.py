"""
Experience Service - FastAPI Service for User Interaction

Experience translates external interaction into intent.

WHAT (Experience Role): I translate user actions into intents
HOW (Experience Implementation): I expose REST, WebSockets, and coordinate with Runtime
"""

import sys
from pathlib import Path

# Add project root to path
# Find project root by looking for common markers (pyproject.toml, requirements.txt, etc.)
current = Path(__file__).resolve()
project_root = current
for _ in range(10):  # Max 10 levels up
    if (project_root / "pyproject.toml").exists() or (project_root / "requirements.txt").exists():
        break
    project_root = project_root.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from utilities import get_logger
from .middleware.auth_middleware import AuthenticationMiddleware
from .api.sessions import router as sessions_router
from .api.intents import router as intents_router
from .api.websocket import router as websocket_router
from .api.guide_agent import router as guide_agent_router
from .api.auth import router as auth_router
from .api.runtime_agent_websocket import router as runtime_agent_websocket_router


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
    
    # Authentication middleware (must be added before CORS)
    app.add_middleware(AuthenticationMiddleware)
    
    # CORS for frontend
    # Get allowed origins from environment variable, default to localhost for development
    allowed_origins_str = os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:3001,http://localhost:8000"
    )
    allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,  # Specific origins only (not wildcard)
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    )
    
    # Include routers
    app.include_router(auth_router)
    app.include_router(sessions_router)
    app.include_router(intents_router)
    app.include_router(websocket_router)
    app.include_router(guide_agent_router)
    app.include_router(runtime_agent_websocket_router)  # Experience Plane owns /api/runtime/agent
    
    # Include Admin Dashboard routers
    from symphainy_platform.civic_systems.experience.admin_dashboard.api import (
        control_room_router,
        developer_view_router,
        business_user_view_router
    )
    app.include_router(control_room_router)
    app.include_router(developer_view_router)
    app.include_router(business_user_view_router)
    
    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy", "service": "experience", "version": "2.0.0"}
    
    logger.info("Experience Service application created")
    return app


# Create app instance
app = create_app()
