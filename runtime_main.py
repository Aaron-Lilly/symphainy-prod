#!/usr/bin/env python3
"""
Runtime Service - Main Entry Point

Initializes Runtime with Public Works, registers realms, and exposes API.

Version: 2.0 (New Architecture)
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from utilities import get_logger
from symphainy_platform.config import get_env_contract
from symphainy_platform.config.service_config import get_redis_url, get_arango_url, get_consul_host, get_consul_port

# Runtime Components
from symphainy_platform.runtime.intent_registry import IntentRegistry
from symphainy_platform.runtime.realm_registry import RealmRegistry
from symphainy_platform.runtime.state_surface import StateSurface
from symphainy_platform.runtime.wal import WriteAheadLog
from symphainy_platform.runtime.transactional_outbox import TransactionalOutbox
from symphainy_platform.runtime.execution_lifecycle_manager import ExecutionLifecycleManager

# Public Works
from symphainy_platform.foundations.public_works.foundation_service import PublicWorksFoundationService

# Realms
from symphainy_platform.realms.content import ContentRealm
from symphainy_platform.realms.insights import InsightsRealm
from symphainy_platform.realms.journey import JourneyRealm
from symphainy_platform.realms.outcomes import OutcomesRealm

# Initialize
env = get_env_contract()
logger = get_logger("runtime")

# Global state
runtime_components = {}


async def initialize_runtime():
    """
    Initialize Runtime components.
    
    Returns:
        Dict with initialized components
    """
    logger.info("🚀 Initializing Runtime Service...")
    
    try:
        # Step 1: Initialize Public Works Foundation
        logger.info("📦 Step 1: Initializing Public Works Foundation...")
        
        # Get Redis URL from service_config
        from urllib.parse import urlparse
        redis_url = get_redis_url()
        parsed = urlparse(redis_url)
        redis_host = parsed.hostname or "redis"
        redis_port = parsed.port or 6379
        
        public_works = PublicWorksFoundationService(
            config={
                "redis": {
                    "host": redis_host,
                    "port": redis_port,
                },
                "consul": {
                    "host": get_consul_host(),
                    "port": get_consul_port(),
                },
                "arango_url": get_arango_url(),
                "arango_username": "root",
                "arango_password": getattr(env, "ARANGO_ROOT_PASSWORD", "changeme"),
                "arango_database": "symphainy_platform",
            }
        )
        
        if not await public_works.initialize():
            raise RuntimeError("Failed to initialize Public Works Foundation")
        
        logger.info("✅ Public Works Foundation initialized")
        
        # Step 2: Initialize Runtime Components
        logger.info("⚙️ Step 2: Initializing Runtime Components...")
        
        # Intent Registry
        intent_registry = IntentRegistry()
        logger.info("✅ Intent Registry initialized")
        
        # Realm Registry
        realm_registry = RealmRegistry(intent_registry)
        logger.info("✅ Realm Registry initialized")
        
        # State Surface (with FileStorageAbstraction for file retrieval)
        state_surface = StateSurface(
            state_abstraction=public_works.get_state_abstraction(),
            file_storage=public_works.get_file_storage_abstraction()
        )
        logger.info("✅ State Surface initialized")
        
        # Set State Surface on Public Works (for parsing abstractions)
        public_works.set_state_surface(state_surface)
        
        # WAL
        wal = WriteAheadLog(
            redis_adapter=public_works.redis_adapter
        )
        logger.info("✅ Write-Ahead Log initialized")
        
        # Transactional Outbox
        transactional_outbox = TransactionalOutbox(
            redis_adapter=public_works.redis_adapter
        )
        logger.info("✅ Transactional Outbox initialized")
        
        # Materialization Policy & Artifact Storage
        from symphainy_platform.runtime.policies.materialization_policy_abstraction import (
            MaterializationPolicyAbstraction,
            MVP_POLICY_OVERRIDE
        )
        
        # Get Artifact Storage Abstraction from Public Works
        artifact_storage = public_works.get_artifact_storage_abstraction() if public_works else None
        if artifact_storage:
            logger.info("✅ Artifact Storage Abstraction available")
        else:
            logger.warning("⚠️ Artifact Storage Abstraction not available")
        
        # Try to load materialization policy from config file, fallback to MVP override
        import yaml
        import os
        solution_config = None
        # Use absolute path based on project root for container reliability
        config_path = project_root / "config" / "mvp_materialization_policy.yaml"
        
        if config_path.exists():
            try:
                with open(str(config_path), 'r') as f:
                    solution_config = yaml.safe_load(f)
                logger.info(f"✅ Loaded materialization policy from {config_path}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to load materialization policy from {config_path}: {e}, using defaults")
                solution_config = {"materialization_policy": MVP_POLICY_OVERRIDE}
        else:
            logger.info(f"ℹ️ Materialization policy config not found at {config_path}, using hardcoded MVP override")
            solution_config = {"materialization_policy": MVP_POLICY_OVERRIDE}
        
        # Create Materialization Policy Abstraction
        materialization_policy = MaterializationPolicyAbstraction(
            default_policy=None,  # Use default
            solution_config=solution_config
        )
        logger.info("✅ Materialization Policy Abstraction initialized")
        
        # Execution Lifecycle Manager
        execution_lifecycle_manager = ExecutionLifecycleManager(
            intent_registry=intent_registry,
            state_surface=state_surface,
            wal=wal,
            transactional_outbox=transactional_outbox,
            materialization_policy=materialization_policy,
            artifact_storage=public_works.get_artifact_storage_abstraction(),
            solution_config=solution_config
        )
        logger.info("✅ Execution Lifecycle Manager initialized")
        
        # Step 3: Register Realms
        logger.info("📋 Step 3: Registering Realms...")
        
        # Register Content Realm with Public Works
        content_realm = ContentRealm("content", public_works=public_works)
        if realm_registry.register_realm(content_realm):
            logger.info("✅ Content Realm registered")
        else:
            logger.error("❌ Failed to register Content Realm")
            raise RuntimeError("Failed to register Content Realm")
        
        # Register Insights Realm with Public Works
        insights_realm = InsightsRealm("insights", public_works=public_works)
        if realm_registry.register_realm(insights_realm):
            logger.info("✅ Insights Realm registered")
        else:
            logger.error("❌ Failed to register Insights Realm")
            raise RuntimeError("Failed to register Insights Realm")
        
        # Register Journey Realm with Public Works
        journey_realm = JourneyRealm("journey", public_works=public_works)
        if realm_registry.register_realm(journey_realm):
            logger.info("✅ Journey Realm registered")
        else:
            logger.error("❌ Failed to register Journey Realm")
            raise RuntimeError("Failed to register Journey Realm")
        
        # Register Outcomes Realm with Public Works
        outcomes_realm = OutcomesRealm("outcomes", public_works=public_works)
        if realm_registry.register_realm(outcomes_realm):
            logger.info("✅ Outcomes Realm registered")
        else:
            logger.error("❌ Failed to register Outcomes Realm")
            raise RuntimeError("Failed to register Outcomes Realm")
        
        logger.info(f"✅ Registered {len(realm_registry.list_realms())} realm(s)")
        
        # Store components
        runtime_components.update({
            "public_works": public_works,
            "intent_registry": intent_registry,
            "realm_registry": realm_registry,
            "state_surface": state_surface,
            "wal": wal,
            "transactional_outbox": transactional_outbox,
            "execution_lifecycle_manager": execution_lifecycle_manager,
        })
        
        logger.info("✅ Runtime Service initialized successfully")
        return runtime_components
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Runtime Service: {e}", exc_info=True)
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown.
    """
    # Startup
    logger.info("🚀 Starting Runtime Service...")
    
    try:
        # Initialize Runtime
        components = await initialize_runtime()
        
        # Store runtime API instance in app state
        from symphainy_platform.runtime.runtime_api import RuntimeAPI
        
        runtime_api = RuntimeAPI(
            execution_lifecycle_manager=components["execution_lifecycle_manager"],
            state_surface=components["state_surface"],
            artifact_storage=components["public_works"].get_artifact_storage_abstraction()
        )
        
        app.state.runtime_api = runtime_api
        app.state.realm_registry = components["realm_registry"]
        
        logger.info("✅ Runtime Service started successfully")
        yield
        
    except Exception as e:
        logger.error(f"❌ Runtime Service startup failed: {e}", exc_info=True)
        raise
    
    finally:
        # Shutdown
        logger.info("🛑 Shutting down Runtime Service...")
        
        if "public_works" in runtime_components:
            await runtime_components["public_works"].shutdown()
        
        logger.info("✅ Runtime Service shut down")


def create_app() -> FastAPI:
    """
    Create FastAPI application for Runtime Service.
    
    Returns:
        FastAPI application
    """
    # Create app with lifespan
    app = FastAPI(
        title="Symphainy Runtime Service",
        description="Runtime Execution Engine - Intent submission and execution management",
        version="2.0.0",
        lifespan=lifespan
    )
    
    # Add CORS middleware for external access
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure for production - allow specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize OpenTelemetry SDK
    try:
        from symphainy_platform.foundations.public_works.adapters.telemetry_adapter import TelemetryAdapter
        
        telemetry_adapter = TelemetryAdapter(
            service_name="symphainy-runtime",
            otlp_endpoint=getattr(env, "OTEL_EXPORTER_OTLP_ENDPOINT", None),
            insecure=True
        )
        if telemetry_adapter.initialize():
            telemetry_adapter.instrument_logging()
            telemetry_adapter.instrument_fastapi(app)
            logger.info("✅ OpenTelemetry SDK initialized")
    except Exception as e:
        logger.warning(f"⚠️ OpenTelemetry SDK initialization error: {e}")
    
    # Health check
    @app.get("/health")
    async def health():
        """Health check endpoint."""
        realm_count = 0
        if hasattr(app.state, "realm_registry"):
            realm_count = len(app.state.realm_registry.list_realms())
        
        return {
            "status": "healthy",
            "service": "runtime",
            "version": "2.0.0",
            "realms": realm_count
        }
    
    # Runtime API endpoints (added after initialization via app.state)
    from symphainy_platform.runtime.runtime_api import (
        SessionCreateRequest,
        SessionCreateResponse,
        IntentSubmitRequest,
        IntentSubmitResponse,
        ExecutionStatusResponse
    )
    
    @app.post("/api/session/create", response_model=SessionCreateResponse)
    async def create_session(request: SessionCreateRequest):
        """Create a new session."""
        return await app.state.runtime_api.create_session(request)
    
    @app.post("/api/intent/submit", response_model=IntentSubmitResponse)
    async def submit_intent(request: IntentSubmitRequest):
        """Submit intent for execution."""
        return await app.state.runtime_api.submit_intent(request)
    
    @app.get("/api/execution/{execution_id}/status", response_model=ExecutionStatusResponse)
    async def get_execution_status(
        execution_id: str,
        tenant_id: str
    ):
        """Get execution status."""
        return await app.state.runtime_api.get_execution_status(execution_id, tenant_id)

    @app.get("/api/artifacts/{artifact_id}")
    async def get_artifact(
        artifact_id: str,
        tenant_id: str,
        include_visuals: bool = False
    ):
        """Get artifact by ID."""
        from fastapi import HTTPException
        artifact = await app.state.runtime_api.get_artifact(artifact_id, tenant_id, include_visuals)
        if not artifact:
            raise HTTPException(status_code=404, detail="Artifact not found")
        return artifact

    @app.get("/api/artifacts/visual/{visual_path:path}")
    async def get_visual(
        visual_path: str,
        tenant_id: str
    ):
        """Get visual image by storage path."""
        from fastapi import HTTPException, Response
        visual_bytes = await app.state.runtime_api.get_visual(visual_path, tenant_id)
        if not visual_bytes:
            raise HTTPException(status_code=404, detail="Visual not found")
        return Response(content=visual_bytes, media_type="image/png")
    
    @app.get("/api/realms")
    async def get_realms():
        """Get list of registered realms (for Admin Dashboard)."""
        try:
            if not hasattr(app.state, "realm_registry"):
                return {
                    "realms": [],
                    "total": 0,
                    "message": "Realm registry not available"
                }
            
            realm_registry = app.state.realm_registry
            realm_names = realm_registry.list_realms()
            
            realms = []
            for realm_name in realm_names:
                realm = realm_registry.get_realm(realm_name)
                if realm:
                    realms.append({
                        "name": realm_name,
                        "intents_supported": len(realm.declare_intents()) if hasattr(realm, 'declare_intents') else 0,
                        "intents": realm.declare_intents() if hasattr(realm, 'declare_intents') else []
                    })
            
            return {
                "realms": realms,
                "total": len(realms),
                "realm_names": realm_names
            }
        except Exception as e:
            logger.error(f"Failed to get realms: {e}", exc_info=True)
            return {
                "realms": [],
                "total": 0,
                "error": str(e)
            }
    
    return app


def main():
    """Main entry point."""
    host = "0.0.0.0"
    port = int(env.RUNTIME_PORT) if hasattr(env, "RUNTIME_PORT") else 8000
    
    logger.info(f"Starting Symphainy Runtime Service v2.0.0 on {host}:{port}")
    
    app = create_app()
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=env.LOG_LEVEL.lower() if hasattr(env, "LOG_LEVEL") else "info"
    )


if __name__ == "__main__":
    main()
