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

from fastapi import FastAPI, Header
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
        
        # Materialization Policy Store & Artifact Storage
        from symphainy_platform.civic_systems.smart_city.primitives.materialization_policy_primitives import (
            MaterializationPolicyStore
        )
        
        # Get Artifact Storage Abstraction from Public Works
        artifact_storage = public_works.get_artifact_storage_abstraction() if public_works else None
        if artifact_storage:
            logger.info("✅ Artifact Storage Abstraction available")
        else:
            logger.warning("⚠️ Artifact Storage Abstraction not available")
        
        # Initialize Materialization Policy Store (loads from config file)
        import yaml
        import os
        config_path = str(project_root / "config" / "mvp_materialization_policy.yaml")
        materialization_policy_store = MaterializationPolicyStore(config_path=config_path)
        logger.info(f"✅ Materialization Policy Store initialized (config: {config_path})")
        
        # Initialize Data Steward (Smart City) - Boundary Contract Management
        data_steward_sdk = None
        data_steward_primitives = None
        boundary_contract_store = None
        
        try:
            logger.info("🔍 Attempting to initialize Data Steward SDK...")
            from symphainy_platform.civic_systems.smart_city.primitives.data_steward_primitives import (
                DataStewardPrimitives,
                BoundaryContractStore
            )
            from symphainy_platform.civic_systems.smart_city.sdk.data_steward_sdk import DataStewardSDK
            logger.info("✅ Data Steward imports successful")
            
            # Create Boundary Contract Store (uses Supabase adapter)
            if public_works and public_works.supabase_adapter:
                boundary_contract_store = BoundaryContractStore(
                    supabase_adapter=public_works.supabase_adapter
                )
                logger.info("✅ Boundary Contract Store initialized")
            else:
                logger.warning("⚠️ Boundary Contract Store not available (Supabase adapter missing)")
            
            # Initialize Data Steward Primitives
            data_steward_primitives = DataStewardPrimitives(
                policy_store=None,  # Future: Add policy store
                boundary_contract_store=boundary_contract_store
            )
            logger.info("✅ Data Steward Primitives initialized")
            
            # Initialize Data Steward SDK
            data_steward_sdk = DataStewardSDK(
                data_governance_abstraction=None,  # Future: Add data governance abstraction
                policy_resolver=None,  # Future: Add policy resolver
                data_steward_primitives=data_steward_primitives,
                materialization_policy=materialization_policy_store
            )
            logger.info(f"✅ Data Steward SDK initialized (type: {type(data_steward_sdk)}, is None: {data_steward_sdk is None})")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Data Steward SDK: {e}", exc_info=True)
            logger.warning("⚠️ Continuing without Data Steward SDK (boundary contracts will not be enforced)")
            data_steward_sdk = None  # Explicitly set to None on failure
        
        # Log final state of data_steward_sdk before passing to ExecutionLifecycleManager
        logger.info(f"🔍 DEBUG: data_steward_sdk before ExecutionLifecycleManager: type={type(data_steward_sdk)}, is None={data_steward_sdk is None}")
        
        # Load solution config for execution contracts
        solution_config = None
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    solution_config = yaml.safe_load(f)
                logger.info(f"✅ Loaded solution config from {config_path}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to load solution config from {config_path}: {e}")
                solution_config = {}
        else:
            logger.info(f"ℹ️ Solution config not found at {config_path}, using defaults")
            solution_config = {}
        
        # Execution Lifecycle Manager
        logger.info(f"🔍 DEBUG: Creating ExecutionLifecycleManager with data_steward_sdk: type={type(data_steward_sdk)}, is None={data_steward_sdk is None}")
        execution_lifecycle_manager = ExecutionLifecycleManager(
            intent_registry=intent_registry,
            state_surface=state_surface,
            wal=wal,
            transactional_outbox=transactional_outbox,
            materialization_policy_store=materialization_policy_store,
            artifact_storage=artifact_storage,
            solution_config=solution_config,
            data_steward_sdk=data_steward_sdk
        )
        logger.info(f"✅ Execution Lifecycle Manager initialized (data_steward_sdk: {execution_lifecycle_manager.data_steward_sdk is not None})")
        
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
            "data_steward_sdk": data_steward_sdk,
            "data_steward_primitives": data_steward_primitives,
            "boundary_contract_store": boundary_contract_store,
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
        
        # Get file storage abstraction for unified artifact retrieval
        file_storage = components["public_works"].get_file_storage_abstraction()
        
        runtime_api = RuntimeAPI(
            execution_lifecycle_manager=components["execution_lifecycle_manager"],
            state_surface=components["state_surface"],
            artifact_storage=components["public_works"].get_artifact_storage_abstraction(),
            file_storage=file_storage
        )
        
        app.state.runtime_api = runtime_api
        app.state.realm_registry = components["realm_registry"]
        app.state.execution_lifecycle_manager = components["execution_lifecycle_manager"]
        
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
    
    # Add request logging middleware to debug tenant_id issue
    @app.middleware("http")
    async def log_request_body(request, call_next):
        """Log raw request body for /api/intent/submit to debug tenant_id."""
        if request.url.path == "/api/intent/submit":
            body = await request.body()
            from utilities import get_logger
            logger = get_logger("RequestMiddleware")
            try:
                import json
                body_json = json.loads(body.decode()) if body else {}
                logger.info(f"🔵 RAW REQUEST BODY: {json.dumps(body_json, indent=2)}")
                logger.info(f"🔵 tenant_id in body: {body_json.get('tenant_id', 'MISSING')}")
            except Exception as e:
                logger.warning(f"Could not parse request body: {e}")
            
            # Recreate request with body (FastAPI needs it)
            from starlette.requests import Request
            async def receive():
                return {"type": "http.request", "body": body}
            request._receive = receive
        
        response = await call_next(request)
        return response
    
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
        # Log raw request for debugging
        from utilities import get_logger
        logger = get_logger("FastAPI")
        logger.info(f"🔵 FASTAPI RECEIVED: tenant_id={request.tenant_id}, intent_type={request.intent_type}")
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
        """
        Get artifact by ID (unified retrieval).
        
        Supports:
        - Structured artifacts (workflow, sop, solution, etc.)
        - File artifacts (files ingested via Content Realm)
        - Composite artifacts with visuals
        """
        from fastapi import HTTPException
        artifact = await app.state.runtime_api.get_artifact(
            artifact_id=artifact_id,
            tenant_id=tenant_id,
            include_visuals=include_visuals,
            materialization_policy=None  # MVP: all persisted
        )
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
    
    @app.post("/api/content/save_materialization")
    async def save_materialization(
        boundary_contract_id: str,
        file_id: str,
        tenant_id: str,
        user_id: str = Header(..., alias="x-user-id"),
        session_id: str = Header(..., alias="x-session-id")
    ):
        """
        Explicitly save (materialize) a file that was uploaded.
        
        This is the second step after upload:
        1. Upload → creates boundary contract (pending materialization)
        2. Save → authorizes materialization (active) and registers in materialization index
        
        Files must be saved before they are available for parsing (MVP requirement).
        """
        from fastapi import HTTPException
        from symphainy_platform.runtime.intent_model import Intent
        
        try:
            # Create save_materialization intent
            from utilities import generate_event_id
            intent = Intent(
                intent_id=generate_event_id(),
                intent_type="save_materialization",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="default",  # MVP default
                parameters={
                    "boundary_contract_id": boundary_contract_id,
                    "file_id": file_id
                },
                metadata={"user_id": user_id}  # Pass user_id in metadata
            )
            
            # Execute via ExecutionLifecycleManager (it creates the context internally)
            if not hasattr(app.state, "execution_lifecycle_manager"):
                raise HTTPException(status_code=500, detail="ExecutionLifecycleManager not available")
            execution_lifecycle_manager = app.state.execution_lifecycle_manager
            result = await execution_lifecycle_manager.execute(intent)
            
            if not result.success:
                raise HTTPException(status_code=400, detail=result.error or "Failed to save materialization")
            
            return {
                "success": True,
                "file_id": file_id,
                "boundary_contract_id": boundary_contract_id,
                "execution_id": result.execution_id,
                "artifacts": result.artifacts,
                "message": "File saved and available for parsing"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to save materialization: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
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
