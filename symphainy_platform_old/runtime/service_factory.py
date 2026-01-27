"""
Service Factory - Build Runtime Object Graph

CTO Guidance: "Who wires the world together?"

This module builds the runtime object graph:
- Adapters → Foundation abstractions → StateSurface → ExecutionLifecycleManager → FastAPI routes

Key Principles:
1. Services are created once (in create_runtime_services)
2. FastAPI receives services (in create_fastapi_app)
3. No side effects on import
4. Explicit initialization order
5. Testable without FastAPI

Red Flags to Avoid:
- Importing causes side effects ❌
- Routes create services ❌
- Unclear startup order ❌
- "Docker fixes it" ❌
"""

from typing import Dict, Any, Optional
from utilities import get_logger

from .runtime_services import RuntimeServices
from .state_surface import StateSurface
from .execution_lifecycle_manager import ExecutionLifecycleManager
from .intent_registry import IntentRegistry
from .wal import WriteAheadLog

# Foundation service
from ..foundations.public_works.foundation_service import PublicWorksFoundationService

logger = get_logger(__name__)


async def create_runtime_services(config: Dict[str, Any]) -> RuntimeServices:
    """
    Build the runtime object graph.
    
    Initialization Order (CRITICAL - must be explicit):
    1. PublicWorksFoundationService (infrastructure layer - adapters & abstractions)
    2. StateSurface (with ArtifactRegistry)
    3. WriteAheadLog (for audit trail)
    4. IntentRegistry (for intent handlers)
    5. ExecutionLifecycleManager (orchestrates execution)
    
    Args:
        config: Configuration dictionary (from get_env_contract())
    
    Returns:
        RuntimeServices object with all long-lived services
    
    Raises:
        ValueError: If required services cannot be initialized
    """
    logger.info("🔧 Building runtime object graph...")
    
    # Step 1: Initialize Public Works Foundation Service
    # This provides all infrastructure adapters and abstractions
    logger.info("  → Initializing PublicWorksFoundationService...")
    public_works = PublicWorksFoundationService(config=config)
    
    # Initialize adapters and abstractions (async method)
    logger.info("  → Initializing adapters and abstractions...")
    initialized = await public_works.initialize()
    if not initialized:
        logger.warning("  ⚠️ PublicWorksFoundationService initialization had issues, continuing anyway...")
    logger.info("  ✅ PublicWorksFoundationService initialized")
    
    # Step 2: Create StateSurface (with ArtifactRegistry)
    logger.info("  → Creating StateSurface...")
    state_surface = StateSurface(
        state_abstraction=public_works.state_abstraction,
        file_storage=public_works.file_storage_abstraction,
        # ArtifactRegistry is created inside StateSurface.__init__
    )
    logger.info("  ✅ StateSurface created")
    
    # Step 3: Create WriteAheadLog (for audit trail)
    logger.info("  → Creating WriteAheadLog...")
    wal = WriteAheadLog(
        redis_adapter=public_works.redis_adapter
    )
    logger.info("  ✅ WriteAheadLog created")
    
    # Step 4: Create IntentRegistry (for intent handlers)
    logger.info("  → Creating IntentRegistry...")
    intent_registry = IntentRegistry()
    
    # Register intent handlers from realms (explicit registration, no magic imports)
    logger.info("  → Registering intent handlers...")
    
    # Content Realm handlers
    from ..realms.content.orchestrators.content_orchestrator import ContentOrchestrator
    content_orchestrator = ContentOrchestrator(public_works=public_works)
    
    # Register content realm intents
    content_intents = [
        "ingest_file",
        "bulk_ingest_files",
        "parse_content",
        "bulk_parse_files",
        "create_deterministic_embeddings",  # Required before extract_embeddings
        "extract_embeddings",
        "bulk_extract_embeddings",
        "save_materialization",
        "get_parsed_file",
        "get_semantic_interpretation",
        "register_artifact",  # Artifact-centric (register_file is legacy alias)
        "register_file",  # Legacy alias for register_artifact
        "retrieve_artifact_metadata",  # Artifact-centric (retrieve_file_metadata is legacy alias)
        "retrieve_file_metadata",  # Legacy alias for retrieve_artifact_metadata
        "retrieve_artifact",  # Artifact-centric (retrieve_file is legacy alias)
        "retrieve_file",  # Legacy alias for retrieve_artifact
        "list_files",
        "bulk_interpret_data",
        "get_operation_status",
        "archive_artifact",  # Artifact-centric (archive_file is legacy alias)
        "archive_file",  # Legacy alias for archive_artifact
        "delete_artifact",  # Artifact-centric (purge_file is legacy alias)
        "purge_file"  # Legacy alias for delete_artifact
    ]
    
    for intent_type in content_intents:
        intent_registry.register_intent(
            intent_type=intent_type,
            handler_name="content_orchestrator",
            handler_function=content_orchestrator.handle_intent,
            metadata={"realm": "content", "orchestrator": "ContentOrchestrator"}
        )
        logger.info(f"    ✅ Registered: {intent_type} → content_orchestrator")
    
    # Register insights realm handlers
    logger.info("  → Registering insights realm handlers...")
    from ..realms.insights.orchestrators.insights_orchestrator import InsightsOrchestrator
    insights_orchestrator = InsightsOrchestrator(public_works=public_works)
    
    insights_intents = [
        "analyze_content",
        "interpret_data",
        "map_relationships",
        "query_data",
        "calculate_metrics",
        "assess_data_quality",
        "interpret_data_self_discovery",
        "interpret_data_guided",
        "analyze_structured_data",
        "analyze_unstructured_data",
        "visualize_lineage",
        "extract_structured_data",
        "discover_extraction_pattern",
        "create_extraction_config",
        "match_source_to_target"
    ]
    
    for intent_type in insights_intents:
        intent_registry.register_intent(
            intent_type=intent_type,
            handler_name="insights_orchestrator",
            handler_function=insights_orchestrator.handle_intent,
            metadata={"realm": "insights", "orchestrator": "InsightsOrchestrator"}
        )
        logger.info(f"    ✅ Registered: {intent_type} → insights_orchestrator")
    
    # Register outcomes realm handlers
    logger.info("  → Registering outcomes realm handlers...")
    from ..realms.outcomes.orchestrators.outcomes_orchestrator import OutcomesOrchestrator
    outcomes_orchestrator = OutcomesOrchestrator(public_works=public_works)
    
    outcomes_intents = [
        "synthesize_outcome",
        "generate_roadmap",
        "create_poc",
        "create_blueprint",
        "create_solution",
        "export_to_migration_engine",
        "export_artifact"
    ]
    
    for intent_type in outcomes_intents:
        intent_registry.register_intent(
            intent_type=intent_type,
            handler_name="outcomes_orchestrator",
            handler_function=outcomes_orchestrator.handle_intent,
            metadata={"realm": "outcomes", "orchestrator": "OutcomesOrchestrator"}
        )
        logger.info(f"    ✅ Registered: {intent_type} → outcomes_orchestrator")
    
    # Register operations realm handlers
    # NOTE: Operations Realm consolidates all SOP, workflow, and coexistence capabilities
    # The old "journey realm" has been merged into Operations Realm.
    # "Journey" is now reserved for platform journeys (intent sequences in solutions)
    logger.info("  → Registering operations realm handlers...")
    from ..realms.operations.orchestrators.operations_orchestrator import OperationsOrchestrator
    operations_orchestrator = OperationsOrchestrator(public_works=public_works)
    
    operations_intents = [
        "optimize_process",
        "generate_sop",
        "create_workflow",
        "analyze_coexistence",
        "create_blueprint",
        "generate_sop_from_chat",
        "sop_chat_message"
    ]
    
    for intent_type in operations_intents:
        intent_registry.register_intent(
            intent_type=intent_type,
            handler_name="operations_orchestrator",
            handler_function=operations_orchestrator.handle_intent,
            metadata={"realm": "operations", "orchestrator": "OperationsOrchestrator"}
        )
        logger.info(f"    ✅ Registered: {intent_type} → operations_orchestrator")
    
    total_handlers = len(content_intents) + len(insights_intents) + len(outcomes_intents) + len(operations_intents)
    logger.info(f"  ✅ IntentRegistry created with {total_handlers} intent handlers across all realms")
    
    # Step 4.5: Initialize Platform Solutions
    logger.info("  → Initializing Platform Solutions...")
    from ..solutions import initialize_solutions
    from ..civic_systems.platform_sdk.solution_registry import SolutionRegistry
    
    solution_registry = SolutionRegistry()
    solution_services = await initialize_solutions(
        public_works=public_works,
        state_surface=state_surface,
        solution_registry=solution_registry,
        intent_registry=intent_registry,
        initialize_mcp_servers=True
    )
    logger.info("  ✅ Platform Solutions initialized")
    
    # Step 5: Create ExecutionLifecycleManager
    logger.info("  → Creating ExecutionLifecycleManager...")
    execution_lifecycle_manager = ExecutionLifecycleManager(
        intent_registry=intent_registry,
        state_surface=state_surface,
        wal=wal,
        artifact_storage=public_works.artifact_storage_abstraction,
        # ... other dependencies
    )
    logger.info("  ✅ ExecutionLifecycleManager created")
    
    # Get abstractions from PublicWorksFoundationService
    registry_abstraction = public_works.registry_abstraction
    artifact_storage = public_works.artifact_storage_abstraction
    file_storage = public_works.file_storage_abstraction
    
    # Build RuntimeServices container
    services = RuntimeServices(
        public_works=public_works,
        state_surface=state_surface,
        execution_lifecycle_manager=execution_lifecycle_manager,
        registry_abstraction=registry_abstraction,
        artifact_storage=artifact_storage,
        file_storage=file_storage,
        wal=wal,
        intent_registry=intent_registry,
        solution_registry=solution_registry,
        solution_services=solution_services
    )
    
    logger.info("✅ Runtime object graph built successfully")
    
    return services


def create_fastapi_app(services: RuntimeServices) -> Any:
    """
    Create FastAPI app with routes (receives services, doesn't create them).
    
    Key Principle: FastAPI should not create services. Routes should not create services.
    They should only *receive* them.
    
    Args:
        services: RuntimeServices object with all dependencies
    
    Returns:
        Configured FastAPI app with all routes registered
    
    Raises:
        ValueError: If required services are missing
    """
    from .runtime_api import create_runtime_app
    
    logger.info("🔧 Creating FastAPI app...")
    
    # Create FastAPI app (receives services, doesn't create them)
    app = create_runtime_app(
        execution_lifecycle_manager=services.execution_lifecycle_manager,
        state_surface=services.state_surface,
        registry_abstraction=services.registry_abstraction,
        artifact_storage=services.artifact_storage,
        file_storage=services.file_storage
    )
    
    logger.info("✅ FastAPI app created with all routes registered")
    
    return app
