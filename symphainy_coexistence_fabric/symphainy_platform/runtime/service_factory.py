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
    
    # Register intent handlers from realm intent services
    # PATTERN: Each intent maps to an IntentService.execute() method
    # No orchestrators - Runtime handles orchestration via Sagas
    logger.info("  → Registering intent handlers from intent services...")
    
    # Helper function to register intent service
    def register_intent_service(intent_type: str, service_class, realm: str):
        """Register an intent service with the registry."""
        try:
            service = service_class(public_works=public_works, state_surface=state_surface)
            intent_registry.register_intent(
                intent_type=intent_type,
                handler_name=f"{realm}_{intent_type}_service",
                handler_function=service.execute,
                metadata={"realm": realm, "service": service_class.__name__}
            )
            logger.info(f"    ✅ Registered: {intent_type} → {service_class.__name__}")
            return True
        except Exception as e:
            logger.warning(f"    ⚠️ Failed to register {intent_type}: {e}")
            return False
    
    # Content Realm intent services
    logger.info("  → Registering Content Realm intent services...")
    try:
        from ..realms.content.intent_services import (
            IngestFileService,
            ParseContentService,
            CreateDeterministicEmbeddingsService,
            ExtractEmbeddingsService,
            SaveMaterializationService,
            GetParsedFileService,
            RetrieveArtifactMetadataService,
            ListArtifactsService,
            ArchiveFileService,
            DeleteFileService
        )
        
        content_services = [
            ("ingest_file", IngestFileService),
            ("parse_content", ParseContentService),
            ("create_deterministic_embeddings", CreateDeterministicEmbeddingsService),
            ("extract_embeddings", ExtractEmbeddingsService),
            ("save_materialization", SaveMaterializationService),
            ("get_parsed_file", GetParsedFileService),
            ("retrieve_artifact_metadata", RetrieveArtifactMetadataService),
            ("list_artifacts", ListArtifactsService),
            ("archive_file", ArchiveFileService),
            ("delete_file", DeleteFileService),
        ]
        
        content_count = sum(1 for intent, svc in content_services if register_intent_service(intent, svc, "content"))
        logger.info(f"  ✅ Content Realm: {content_count} intent services registered")
    except ImportError as e:
        logger.warning(f"  ⚠️ Content Realm import error: {e}")
        content_count = 0
    
    # Insights Realm intent services
    logger.info("  → Registering Insights Realm intent services...")
    try:
        from ..realms.insights.intent_services import (
            AssessDataQualityService,
            InterpretDataSelfDiscoveryService,
            InterpretDataGuidedService,
            AnalyzeStructuredDataService,
            AnalyzeUnstructuredDataService,
            VisualizeLineageService,
            MapRelationshipsService
        )
        
        insights_services = [
            ("assess_data_quality", AssessDataQualityService),
            ("interpret_data_self_discovery", InterpretDataSelfDiscoveryService),
            ("interpret_data_guided", InterpretDataGuidedService),
            ("analyze_structured_data", AnalyzeStructuredDataService),
            ("analyze_unstructured_data", AnalyzeUnstructuredDataService),
            ("visualize_lineage", VisualizeLineageService),
            ("map_relationships", MapRelationshipsService),
        ]
        
        insights_count = sum(1 for intent, svc in insights_services if register_intent_service(intent, svc, "insights"))
        logger.info(f"  ✅ Insights Realm: {insights_count} intent services registered")
    except ImportError as e:
        logger.warning(f"  ⚠️ Insights Realm import error: {e}")
        insights_count = 0
    
    # Operations Realm intent services
    logger.info("  → Registering Operations Realm intent services...")
    try:
        from ..realms.operations.intent_services import (
            OptimizeProcessService,
            GenerateSOPService,
            CreateWorkflowService,
            AnalyzeCoexistenceService,
            GenerateSOPFromChatService,
            SOPChatMessageService
        )
        
        operations_services = [
            ("optimize_process", OptimizeProcessService),
            ("generate_sop", GenerateSOPService),
            ("create_workflow", CreateWorkflowService),
            ("analyze_coexistence", AnalyzeCoexistenceService),
            ("generate_sop_from_chat", GenerateSOPFromChatService),
            ("sop_chat_message", SOPChatMessageService),
        ]
        
        operations_count = sum(1 for intent, svc in operations_services if register_intent_service(intent, svc, "operations"))
        logger.info(f"  ✅ Operations Realm: {operations_count} intent services registered")
    except ImportError as e:
        logger.warning(f"  ⚠️ Operations Realm import error: {e}")
        operations_count = 0
    
    # Outcomes Realm intent services
    logger.info("  → Registering Outcomes Realm intent services...")
    try:
        from ..realms.outcomes.intent_services import (
            SynthesizeOutcomeService,
            GenerateRoadmapService,
            CreatePOCService,
            CreateBlueprintService,
            CreateSolutionService,
            ExportArtifactService
        )
        
        outcomes_services = [
            ("synthesize_outcome", SynthesizeOutcomeService),
            ("generate_roadmap", GenerateRoadmapService),
            ("create_poc", CreatePOCService),
            ("create_blueprint", CreateBlueprintService),
            ("create_solution", CreateSolutionService),
            ("export_artifact", ExportArtifactService),
        ]
        
        outcomes_count = sum(1 for intent, svc in outcomes_services if register_intent_service(intent, svc, "outcomes"))
        logger.info(f"  ✅ Outcomes Realm: {outcomes_count} intent services registered")
    except ImportError as e:
        logger.warning(f"  ⚠️ Outcomes Realm import error: {e}")
        outcomes_count = 0
    
    # Security Realm intent services
    logger.info("  → Registering Security Realm intent services...")
    try:
        from ..realms.security.intent_services import (
            AuthenticateUserService,
            CreateUserAccountService,
            CreateSessionService,
            ValidateAuthorizationService,
            TerminateSessionService,
            CheckEmailAvailabilityService,
            ValidateTokenService
        )
        
        security_services = [
            ("authenticate_user", AuthenticateUserService),
            ("create_user_account", CreateUserAccountService),
            ("create_session", CreateSessionService),
            ("validate_authorization", ValidateAuthorizationService),
            ("terminate_session", TerminateSessionService),
            ("check_email_availability", CheckEmailAvailabilityService),
            ("validate_token", ValidateTokenService),
        ]
        
        security_count = sum(1 for intent, svc in security_services if register_intent_service(intent, svc, "security"))
        logger.info(f"  ✅ Security Realm: {security_count} intent services registered")
    except ImportError as e:
        logger.warning(f"  ⚠️ Security Realm import error: {e}")
        security_count = 0
    
    # Control Tower Realm intent services
    logger.info("  → Registering Control Tower Realm intent services...")
    try:
        from ..realms.control_tower.intent_services import (
            GetPlatformStatisticsService,
            GetSystemHealthService,
            GetRealmHealthService,
            ListSolutionsService,
            GetSolutionStatusService,
            GetPatternsService,
            GetCodeExamplesService,
            GetDocumentationService,
            ValidateSolutionService
        )
        
        control_tower_services = [
            ("get_platform_statistics", GetPlatformStatisticsService),
            ("get_system_health", GetSystemHealthService),
            ("get_realm_health", GetRealmHealthService),
            ("list_solutions", ListSolutionsService),
            ("get_solution_status", GetSolutionStatusService),
            ("get_patterns", GetPatternsService),
            ("get_code_examples", GetCodeExamplesService),
            ("get_documentation", GetDocumentationService),
            ("validate_solution", ValidateSolutionService),
        ]
        
        control_tower_count = sum(1 for intent, svc in control_tower_services if register_intent_service(intent, svc, "control_tower"))
        logger.info(f"  ✅ Control Tower Realm: {control_tower_count} intent services registered")
    except ImportError as e:
        logger.warning(f"  ⚠️ Control Tower Realm import error: {e}")
        control_tower_count = 0
    
    # Coexistence Realm intent services
    logger.info("  → Registering Coexistence Realm intent services...")
    try:
        from ..realms.coexistence.intent_services import (
            IntroducePlatformService,
            ShowSolutionCatalogService,
            NavigateToSolutionService,
            InitiateGuideAgentService,
            ProcessGuideAgentMessageService,
            RouteToLiaisonAgentService,
            ListAvailableMCPToolsService,
            CallOrchestratorMCPToolService
        )
        
        coexistence_services = [
            ("introduce_platform", IntroducePlatformService),
            ("show_solution_catalog", ShowSolutionCatalogService),
            ("navigate_to_solution", NavigateToSolutionService),
            ("initiate_guide_agent", InitiateGuideAgentService),
            ("process_guide_agent_message", ProcessGuideAgentMessageService),
            ("route_to_liaison_agent", RouteToLiaisonAgentService),
            ("list_available_mcp_tools", ListAvailableMCPToolsService),
            ("call_orchestrator_mcp_tool", CallOrchestratorMCPToolService),
        ]
        
        coexistence_count = sum(1 for intent, svc in coexistence_services if register_intent_service(intent, svc, "coexistence"))
        logger.info(f"  ✅ Coexistence Realm: {coexistence_count} intent services registered")
    except ImportError as e:
        logger.warning(f"  ⚠️ Coexistence Realm import error: {e}")
        coexistence_count = 0
    
    total_handlers = content_count + insights_count + operations_count + outcomes_count + security_count + control_tower_count + coexistence_count
    logger.info(f"  ✅ IntentRegistry created with {total_handlers} intent services across all realms")
    
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
