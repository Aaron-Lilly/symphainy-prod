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

from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

from utilities import get_logger
from symphainy_platform.config import get_env_contract
from symphainy_platform.config.service_config import get_redis_url, get_arango_url, get_consul_host, get_consul_port

from symphainy_platform.civic_systems.experience.experience_service import create_app
from symphainy_platform.foundations.public_works.foundation_service import PublicWorksFoundationService
from symphainy_platform.civic_systems.smart_city.sdk.traffic_cop_sdk import TrafficCopSDK
from symphainy_platform.civic_systems.smart_city.sdk.security_guard_sdk import SecurityGuardSDK
from symphainy_platform.civic_systems.experience.admin_dashboard import AdminDashboardService
from symphainy_platform.civic_systems.experience.sdk.runtime_client import RuntimeClient
from symphainy_platform.civic_systems.platform_sdk.solution_registry import SolutionRegistry

# Initialize
env = get_env_contract()
logger = get_logger("experience")
experience_components = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for Experience service."""
    logger.info("🚀 Starting Experience Service...")
    
    try:
        # Initialize Public Works Foundation
        logger.info("📦 Step 1: Initializing Public Works Foundation...")
        # Parse Redis URL if provided, otherwise use defaults
        # Get Redis URL from service_config
        from urllib.parse import urlparse
        redis_url = get_redis_url()
        parsed = urlparse(redis_url)
        redis_host = parsed.hostname or "redis"
        redis_port = parsed.port or 6379
        
        public_works = PublicWorksFoundationService(
            config={
                "redis": {"host": redis_host, "port": redis_port},
                "consul": {"host": get_consul_host(), "port": get_consul_port()},
                "arango_url": get_arango_url(),
                "arango_username": "root",
                "arango_password": env.ARANGO_ROOT_PASSWORD,
                "arango_database": "symphainy_platform",
                "supabase_url": getattr(env, "SUPABASE_URL", None),
                "supabase_anon_key": getattr(env, "SUPABASE_ANON_KEY", None),
                "supabase_service_key": getattr(env, "SUPABASE_SERVICE_KEY", None),
                "supabase_jwks_url": getattr(env, "SUPABASE_JWKS_URL", None),
                "supabase_jwt_issuer": getattr(env, "SUPABASE_JWT_ISSUER", None),
                "gcs_project_id": getattr(env, "GCS_PROJECT_ID", None),
                "gcs_bucket_name": getattr(env, "GCS_BUCKET_NAME", None),
                "gcs_credentials_json": getattr(env, "GCS_CREDENTIALS_JSON", None),
            }
        )
        
        if not await public_works.initialize():
            raise RuntimeError("Failed to initialize Public Works Foundation")
        logger.info("✅ Public Works Foundation initialized")
        
        # Initialize Smart City SDKs
        logger.info("📦 Step 2: Initializing Smart City SDKs...")
        
        # Traffic Cop SDK (for session coordination)
        traffic_cop_sdk = TrafficCopSDK(
            state_abstraction=public_works.get_state_abstraction()
        )
        logger.info("✅ Traffic Cop SDK initialized")
        
        # Security Guard SDK (for authentication)
        security_guard_sdk = SecurityGuardSDK(
            auth_abstraction=public_works.get_auth_abstraction(),
            tenant_abstraction=public_works.get_tenant_abstraction()
        )
        logger.info("✅ Security Guard SDK initialized")
        
        # Initialize Runtime Client (for Admin Dashboard)
        logger.info("📦 Step 3: Initializing Runtime Client...")
        runtime_url = getattr(env, "RUNTIME_URL", "http://runtime:8000")
        runtime_client = RuntimeClient(runtime_url=runtime_url)
        logger.info("✅ Runtime Client initialized")
        
        # Initialize Solution Registry (for Admin Dashboard)
        logger.info("📦 Step 4: Initializing Solution Registry...")
        solution_registry = SolutionRegistry()
        logger.info("✅ Solution Registry initialized")
        
        # Initialize Admin Dashboard Service
        logger.info("📦 Step 5: Initializing Admin Dashboard Service...")
        admin_dashboard_service = AdminDashboardService(
            runtime_client=runtime_client,
            realm_registry=None,  # Will be accessed via Runtime client when needed
            solution_registry=solution_registry,
            security_guard_sdk=security_guard_sdk,
            public_works=public_works
        )
        logger.info("✅ Admin Dashboard Service initialized")
        
        # Initialize Guide Agent Service
        logger.info("📦 Step 6: Initializing Guide Agent Service...")
        from symphainy_platform.civic_systems.experience.services.guide_agent_service import GuideAgentService
        guide_agent_service = GuideAgentService(public_works=public_works)
        logger.info("✅ Guide Agent Service initialized")
        
        # Store components in app state
        app.state.public_works = public_works
        app.state.traffic_cop_sdk = traffic_cop_sdk
        app.state.security_guard_sdk = security_guard_sdk
        app.state.runtime_client = runtime_client
        app.state.solution_registry = solution_registry
        app.state.admin_dashboard_service = admin_dashboard_service
        app.state.guide_agent_service = guide_agent_service
        
        experience_components["public_works"] = public_works
        experience_components["traffic_cop_sdk"] = traffic_cop_sdk
        experience_components["security_guard_sdk"] = security_guard_sdk
        experience_components["runtime_client"] = runtime_client
        experience_components["solution_registry"] = solution_registry
        experience_components["admin_dashboard_service"] = admin_dashboard_service
        
        logger.info("✅ Experience Service started successfully")
        yield
        
    except Exception as e:
        logger.error(f"❌ Experience Service startup failed: {e}", exc_info=True)
        raise
    
    finally:
        logger.info("🛑 Shutting down Experience Service...")
        if "public_works" in experience_components:
            await experience_components["public_works"].shutdown()
        logger.info("✅ Experience Service shut down")


def main():
    """Main entry point."""
    host = "0.0.0.0"
    port = int(env.EXPERIENCE_PORT) if hasattr(env, "EXPERIENCE_PORT") else 8001
    
    logger.info(f"Starting Symphainy Experience Service v2.0.0 on {host}:{port}")
    
    app = create_app()
    app.router.lifespan_context = lifespan
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=env.LOG_LEVEL.lower() if hasattr(env, "LOG_LEVEL") else "info",
        lifespan="on"
    )


if __name__ == "__main__":
    main()
