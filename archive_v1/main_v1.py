#!/usr/bin/env python3
"""
Symphainy Platform - Main Entry Point

Phase 0-4: Complete Platform Stack
- Phase 0: Containers, Infra, Guardrails
- Phase 1: Runtime Plane
- Phase 2: Foundations (Public Works + Curator)
- Phase 3: Agent Foundation
- Phase 4: Smart City Plane

All foundations initialized and wired together.
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

from fastapi import FastAPI
import uvicorn

from utilities import get_logger, LogLevel, LogCategory, get_clock
from config import get_env_contract

# Phase 2 Foundations
from symphainy_platform.foundations.public_works.foundation_service import PublicWorksFoundationService
from symphainy_platform.foundations.curator.foundation_service import CuratorFoundationService

# Phase 3 Agent Foundation
from symphainy_platform.agentic.foundation_service import AgentFoundationService

# Phase 4 Smart City
from symphainy_platform.smart_city.foundation_service import SmartCityFoundationService

# Phase 1 Runtime Plane
from symphainy_platform.runtime import (
    StateSurface,
    WriteAheadLog,
    SagaCoordinator,
    create_runtime_app
)
from symphainy_platform.runtime.runtime_service import RuntimeService

# Initialize Phase 0 utilities
env = get_env_contract()
clock = get_clock()
logger = get_logger("platform", LogLevel.INFO, LogCategory.PLATFORM)

# Global shutdown event for graceful shutdown
shutdown_event = asyncio.Event()

# Global references for graceful shutdown
_foundations = {}
_runtime_components = {}


def signal_handler(signum, frame):
    """Handle shutdown signals (SIGTERM, SIGINT)."""
    logger.info(
        "Received shutdown signal, initiating graceful shutdown",
        metadata={"signal": signum}
    )
    shutdown_event.set()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for graceful shutdown.
    
    Handles:
    - Startup: Initialize all foundations and Runtime components
    - Shutdown: Gracefully close connections and finish in-flight requests
    """
    # Startup
    logger.info("Starting Symphainy Platform", metadata={"version": "0.4.0"})
    
    try:
        # ========================================================================
        # Phase 2: Initialize Foundations
        # ========================================================================
        
        # 1. Public Works Foundation (infrastructure)
        logger.info("Initializing Public Works Foundation...")
        # Parse Redis URL for Public Works config
        redis_url = env.REDIS_URL
        redis_host = "localhost"
        redis_port = 6379
        redis_password = None
        
        if redis_url and "://" in redis_url:
            # Parse redis://host:port or redis://:password@host:port
            parts = redis_url.replace("redis://", "").split("@")
            if len(parts) == 2:
                redis_password = parts[0].replace(":", "")
                host_port = parts[1]
            else:
                host_port = parts[0]
            
            if ":" in host_port:
                redis_host, port_str = host_port.split(":")
                redis_port = int(port_str)
            else:
                redis_host = host_port
        
        public_works_config = {
            "redis": {
                "host": redis_host,
                "port": redis_port,
                "db": 0,
                "password": redis_password
            },
            "consul": {
                "host": env.CONSUL_HOST,
                "port": env.CONSUL_PORT,
                "token": env.CONSUL_TOKEN
            }
        }
        
        public_works = PublicWorksFoundationService(config=public_works_config)
        await public_works.initialize()
        _foundations["public_works"] = public_works
        logger.info("✅ Public Works Foundation initialized")
        
        # 2. Curator Foundation (registry)
        logger.info("Initializing Curator Foundation...")
        curator = CuratorFoundationService(public_works_foundation=public_works)
        await curator.initialize()
        _foundations["curator"] = curator
        logger.info("✅ Curator Foundation initialized")
        
        # ========================================================================
        # Phase 1: Initialize Runtime Components (using Foundations)
        # ========================================================================
        
        # Get state abstraction from Public Works
        state_abstraction = public_works.get_state_abstraction()
        use_memory = state_abstraction is None
        
        # Get file storage abstraction from Public Works
        file_storage = public_works.get_file_storage_abstraction()
        
        # Initialize Runtime components
        # State Surface stores file metadata/references, FileStorageAbstraction stores actual file data
        state_surface = StateSurface(
            state_abstraction=state_abstraction,
            file_storage=file_storage,
            use_memory=use_memory
        )
        
        # WAL uses Redis directly (for list operations) or in-memory fallback
        # Get Redis adapter from Public Works
        redis_adapter = public_works.redis_adapter
        wal_redis_client = None
        if redis_adapter and hasattr(redis_adapter, '_client') and redis_adapter._client:
            wal_redis_client = redis_adapter._client
        elif not use_memory:
            # Fallback: create Redis client for WAL
            import redis.asyncio as redis
            try:
                wal_redis_client = await redis.from_url(env.REDIS_URL, decode_responses=True)
                await wal_redis_client.ping()
            except Exception as e:
                logger.warning(f"WAL Redis not available: {e}, using in-memory for WAL")
                wal_redis_client = None
        
        wal = WriteAheadLog(redis_client=wal_redis_client, use_memory=(wal_redis_client is None))
        saga_coordinator = SagaCoordinator(state_surface=state_surface)
        
        # Create Runtime Service with Curator
        runtime_service = RuntimeService(
            state_surface=state_surface,
            wal=wal,
            saga_coordinator=saga_coordinator,
            curator=curator
        )
        
        # Store references
        _runtime_components["state_surface"] = state_surface
        _runtime_components["wal"] = wal
        _runtime_components["saga_coordinator"] = saga_coordinator
        _runtime_components["runtime_service"] = runtime_service
        
        logger.info(
            "✅ Runtime Plane components initialized",
            metadata={
                "state_surface": "Public Works abstraction" if not use_memory else "in-memory",
                "wal": "Redis-backed" if wal_redis_client else "in-memory"
            }
        )
        
        # ========================================================================
        # Phase 3: Initialize Agent Foundation
        # ========================================================================
        
        logger.info("Initializing Agent Foundation...")
        agent_foundation = AgentFoundationService(
            curator_foundation=curator,
            runtime_service=runtime_service,
            state_surface=state_surface
        )
        await agent_foundation.initialize()
        _foundations["agent"] = agent_foundation
        logger.info("✅ Agent Foundation initialized")
        
        # ========================================================================
        # Phase 4: Initialize Smart City Foundation
        # ========================================================================
        
        logger.info("Initializing Smart City Foundation...")
        smart_city = SmartCityFoundationService(
            public_works_foundation=public_works,
            curator_foundation=curator,
            runtime_service=runtime_service,
            agent_foundation=agent_foundation
        )
        await smart_city.initialize()
        _foundations["smart_city"] = smart_city
        logger.info("✅ Smart City Foundation initialized")
        
        # ========================================================================
        # Initialize Content Realm (Parsing Services)
        # ========================================================================
        
        logger.info("Initializing Content Realm Foundation...")
        
        # Create Platform Gateway
        from symphainy_platform.runtime.platform_gateway import PlatformGateway
        platform_gateway = PlatformGateway(
            public_works_foundation=public_works,
            curator=curator
        )
        
        # Set State Surface for parsing abstractions (they need it for file retrieval)
        public_works.set_state_surface(state_surface)
        
        # Initialize Content Realm Foundation
        from symphainy_platform.realms.content.foundation_service import ContentRealmFoundationService
        content_realm = ContentRealmFoundationService(
            state_surface=state_surface,
            platform_gateway=platform_gateway,
            curator=curator
        )
        await content_realm.initialize()
        _foundations["content_realm"] = content_realm
        logger.info("✅ Content Realm Foundation initialized")
        
        # Initialize Content Realm Manager
        from symphainy_platform.realms.content.manager import ContentRealmManager
        content_manager = ContentRealmManager(
            curator=curator,
            content_orchestrator=content_realm.get_content_orchestrator()
        )
        await content_manager.initialize()
        _foundations["content_manager"] = content_manager
        logger.info("✅ Content Realm Manager initialized")
        
        # ========================================================================
        # Initialize Insights Realm (Data Mash)
        # ========================================================================
        
        logger.info("Initializing Insights Realm Foundation...")
        
        from symphainy_platform.realms.insights.services.data_quality_service import DataQualityService
        from symphainy_platform.realms.insights.services.semantic_interpretation_service import SemanticInterpretationService
        from symphainy_platform.realms.insights.services.semantic_mapping_service import SemanticMappingService
        from symphainy_platform.realms.insights.orchestrators.data_mash_orchestrator import DataMashOrchestrator
        from symphainy_platform.realms.insights.manager import InsightsRealmManager
        
        # Initialize Insights Realm services
        data_quality_service = DataQualityService()
        semantic_interpretation_service = SemanticInterpretationService(
            agent_foundation=agent_foundation,
            content_realm=content_realm
        )
        semantic_mapping_service = SemanticMappingService()
        
        # Initialize Data Mash Orchestrator
        data_mash_orchestrator = DataMashOrchestrator(
            data_quality_service=data_quality_service,
            semantic_interpretation_service=semantic_interpretation_service,
            semantic_mapping_service=semantic_mapping_service,
            state_surface=state_surface,
            saga_coordinator=saga_coordinator
        )
        
        # Initialize Insights Realm Manager
        insights_manager = InsightsRealmManager(
            curator=curator,
            data_mash_orchestrator=data_mash_orchestrator
        )
        await insights_manager.initialize()
        _foundations["insights_manager"] = insights_manager
        _foundations["data_mash_orchestrator"] = data_mash_orchestrator
        logger.info("✅ Insights Realm Foundation initialized")
        
        # ========================================================================
        # Create FastAPI App
        # ========================================================================
        
        # ========================================================================
        # Initialize Intent Executor
        # ========================================================================
        
        logger.info("Initializing Intent Executor...")
        from symphainy_platform.runtime.intent_executor import IntentExecutor
        intent_executor = IntentExecutor(curator=curator)
        
        # Register realm handlers
        intent_executor.register_realm_handler(
            realm_name="content",
            orchestrator=content_realm.get_content_orchestrator()
        )
        intent_executor.register_realm_handler(
            realm_name="insights",
            orchestrator=data_mash_orchestrator
        )
        
        _runtime_components["intent_executor"] = intent_executor
        logger.info("✅ Intent Executor initialized")
        
        # Update Runtime Service with Intent Executor
        runtime_service.intent_executor = intent_executor
        
        # ========================================================================
        # Create FastAPI App
        # ========================================================================
        
        # Create FastAPI app
        runtime_app = create_runtime_app(
            state_surface=state_surface,
            wal=wal,
            saga_coordinator=saga_coordinator,
            curator=curator,
            intent_executor=intent_executor
        )
        
        # Merge routes into main app
        app.mount("/api", runtime_app)
        
        # ========================================================================
        # Experience Plane Note
        # ========================================================================
        # Experience Plane should be a SEPARATE service that:
        # - Submits intents to Runtime via HTTP POST /api/intent/submit
        # - Subscribes to execution events via WebSocket or polling
        # - Does NOT mount routers on Runtime Plane (anti-pattern)
        # 
        # For testing, use Runtime's /api/intent/submit directly.
        # For production, create separate Experience service.
        logger.info("✅ Runtime Plane ready - Experience Plane should be separate service")
        
        logger.info("✅ Symphainy Platform ready", metadata={"port": env.RUNTIME_PORT})
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize platform: {e}", exc_info=e)
        raise
    
    finally:
        # Shutdown
        logger.info("Shutting down Symphainy Platform")
        
        try:
            # Shutdown Smart City
            if "smart_city" in _foundations:
                await _foundations["smart_city"].shutdown()
                logger.info("✅ Smart City Foundation shut down")
            
            # Shutdown Agent Foundation
            if "agent" in _foundations:
                await _foundations["agent"].shutdown()
                logger.info("✅ Agent Foundation shut down")
            
            # Shutdown foundations
            if "curator" in _foundations:
                # Curator doesn't have explicit shutdown, but log it
                logger.info("✅ Curator Foundation shut down")
            
            if "public_works" in _foundations:
                await _foundations["public_works"].shutdown()
                logger.info("✅ Public Works Foundation shut down")
            
            # Close WAL Redis connection if exists
            if "wal" in _runtime_components:
                wal = _runtime_components.get("wal")
                if wal and wal.redis_client:
                    await wal.redis_client.aclose()
                    logger.info("✅ WAL Redis connection closed")
            
            logger.info("✅ Graceful shutdown complete")
        except Exception as e:
            logger.error(
                "Error during shutdown",
                metadata={"error": str(e)},
                exc_info=e
            )


async def setup_platform() -> FastAPI:
    """
    Set up platform components.
    
    Returns:
        FastAPI application with lifespan context
    """
    # Create FastAPI app with lifespan
    app = FastAPI(
        title="Symphainy Platform",
        description="Agentic Integrated Development Platform",
        version="0.4.0",
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
        "Starting Symphainy Platform",
        metadata={
            "host": host,
            "port": port,
            "version": "0.4.0",
            "container_aware": True
        }
    )
    
    # Create app (async setup)
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(setup_platform())
    
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
