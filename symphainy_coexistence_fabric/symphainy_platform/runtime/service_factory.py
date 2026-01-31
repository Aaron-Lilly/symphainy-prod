"""
Service Factory - Build Runtime Object Graph

CTO Guidance: "Who wires the world together?"

This module builds the runtime object graph:
- Adapters → Foundation abstractions → StateSurface → ExecutionLifecycleManager → FastAPI routes
- PlatformContextFactory → Intent Services (new architecture)

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

# Platform SDK - The front door for building on Symphainy
from ..civic_systems.platform_sdk import PlatformContextFactory

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
    
    # Initialize adapters and abstractions (async method). Pre-boot passed, so init must succeed.
    logger.info("  → Initializing adapters and abstractions...")
    initialized = await public_works.initialize()
    if not initialized:
        raise RuntimeError(
            "PublicWorksFoundationService initialization failed. "
            "Pre-boot (G3) passed, so required backing services are reachable; init must not fail. "
            "Check logs for adapter/abstraction errors."
        )
    logger.info("  ✅ PublicWorksFoundationService initialized")
    
    # Step 2: Create StateSurface (with ArtifactRegistry)
    logger.info("  → Creating StateSurface...")
    state_surface = StateSurface(
        state_abstraction=public_works.state_abstraction,
        file_storage=public_works.file_storage_abstraction,
        # ArtifactRegistry is created inside StateSurface.__init__
    )
    logger.info("  ✅ StateSurface created")
    
    # Step 3: Create WriteAheadLog (for audit trail) — uses EventLogProtocol, not adapter
    logger.info("  → Creating WriteAheadLog...")
    wal = WriteAheadLog(
        event_log=public_works.get_wal_backend()
    )
    logger.info("  ✅ WriteAheadLog created")
    
    # Step 3.5: Create PlatformContextFactory (Platform SDK)
    # This is the front door for building on Symphainy - intent services
    # receive PlatformContext (ctx) for accessing platform capabilities
    logger.info("  → Creating PlatformContextFactory...")
    platform_context_factory = PlatformContextFactory(
        public_works=public_works,
        state_surface=state_surface,
        wal=wal
    )
    logger.info("  ✅ PlatformContextFactory created")
    
    # Step 4: Create IntentRegistry (for intent handlers)
    logger.info("  → Creating IntentRegistry...")
    intent_registry = IntentRegistry()
    
    # Register intent handlers from realm intent services
    # PATTERN: Each intent maps to an IntentService.execute() method
    # No orchestrators - Runtime handles orchestration via Sagas
    logger.info("  → Registering intent handlers from intent services...")
    
    # Import PlatformIntentService for type checking
    from ..civic_systems.platform_sdk import PlatformIntentService
    
    # Helper function to register intent service
    def register_intent_service(intent_type: str, service_class, realm: str):
        """Register an intent service with the registry."""
        try:
            # Detect if this is a new-style PlatformIntentService
            # PlatformIntentService is initialized with optional service_id
            # Old-style BaseIntentService is initialized with public_works and state_surface
            uses_platform_context = issubclass(service_class, PlatformIntentService)
            
            if uses_platform_context:
                # New architecture: PlatformIntentService doesn't need public_works/state_surface
                # It receives PlatformContext (ctx) at execution time
                service = service_class(service_id=f"{realm}_{intent_type}_service")
                logger.info(f"    📦 New architecture: {service_class.__name__} uses PlatformContext")
            else:
                # Legacy architecture: BaseIntentService receives public_works and state_surface
                service = service_class(public_works=public_works, state_surface=state_surface)
            
            intent_registry.register_intent(
                intent_type=intent_type,
                handler_name=f"{realm}_{intent_type}_service",
                handler_function=service.execute,
                metadata={
                    "realm": realm,
                    "service": service_class.__name__,
                    "uses_platform_context": uses_platform_context
                }
            )
            logger.info(f"    ✅ Registered: {intent_type} → {service_class.__name__}")
            return True
        except Exception as e:
            logger.warning(f"    ⚠️ Failed to register {intent_type}: {e}")
            return False
    
    # Content Capability intent services (Platform SDK Architecture)
    # All Content services rebuilt to use PlatformContext (ctx)
    logger.info("  → Registering Content Capability intent services...")
    content_count = 0
    try:
        from ..capabilities.content.intent_services import (
            ArchiveFileService,
            CreateDeterministicEmbeddingsService,
            DeleteFileService,
            EchoService,
            GetParsedFileService,
            IngestFileService,
            ListArtifactsService,
            ParseContentService,
            RetrieveArtifactMetadataService,
            SaveMaterializationService
        )
        
        # All content services using Platform SDK pattern
        content_services = [
            # Test service
            ("echo", EchoService),
            # Core content flow: ingest → save → parse → embeddings
            ("ingest_file", IngestFileService),
            ("save_materialization", SaveMaterializationService),
            ("parse_content", ParseContentService),
            ("create_deterministic_embeddings", CreateDeterministicEmbeddingsService),
            # File management
            ("get_parsed_file", GetParsedFileService),
            ("retrieve_artifact_metadata", RetrieveArtifactMetadataService),
            ("list_artifacts", ListArtifactsService),
            ("archive_file", ArchiveFileService),
            ("delete_file", DeleteFileService),
        ]
        
        content_count = sum(1 for intent, svc in content_services if register_intent_service(intent, svc, "content"))
        logger.info(f"  ✅ Content Capability: {content_count} intent services registered")
    except ImportError as e:
        logger.warning(f"  ⚠️ Content Capability import error: {e}")
        content_count = 0
    
    # Legacy extract_embeddings (not yet rebuilt - uses semantic embeddings)
    legacy_content_count = 0
    try:
        from ..realms.content.intent_services import ExtractEmbeddingsService
        
        legacy_content_services = [
            ("extract_embeddings", ExtractEmbeddingsService),
        ]
        
        legacy_content_count = sum(1 for intent, svc in legacy_content_services if register_intent_service(intent, svc, "content"))
        if legacy_content_count > 0:
            logger.info(f"  ✅ Content (legacy): {legacy_content_count} intent services registered")
    except ImportError as e:
        logger.debug(f"  Legacy Content import skipped: {e}")
    
    # Insights Capability intent services (Platform SDK Architecture)
    # AI-powered analysis services use ctx.reasoning.agents for real LLM analysis
    logger.info("  → Registering Insights Capability intent services...")
    insights_count = 0
    try:
        from ..capabilities.insights.intent_services import (
            AssessDataQualityService,
            InterpretDataSelfDiscoveryService,
            InterpretDataGuidedService,
            AnalyzeStructuredDataService,
            AnalyzeUnstructuredDataService,
            VisualizeLineageService,
            MapRelationshipsService
        )
        
        insights_services = [
            # Data Quality
            ("assess_data_quality", AssessDataQualityService),
            # AI-powered Interpretation (uses real agents)
            ("interpret_data_self_discovery", InterpretDataSelfDiscoveryService),
            ("interpret_data_guided", InterpretDataGuidedService),
            # Analysis
            ("analyze_structured_data", AnalyzeStructuredDataService),
            ("analyze_unstructured_data", AnalyzeUnstructuredDataService),
            # Visualization
            ("visualize_lineage", VisualizeLineageService),
            ("map_relationships", MapRelationshipsService),
        ]
        
        insights_count = sum(1 for intent, svc in insights_services if register_intent_service(intent, svc, "insights"))
        logger.info(f"  ✅ Insights Capability: {insights_count} intent services registered")
    except ImportError as e:
        logger.warning(f"  ⚠️ Insights Capability import error: {e}")
        insights_count = 0
    
    # Operations Capability intent services (Platform SDK Architecture)
    # SOP and workflow services use real agents for AI generation
    logger.info("  → Registering Operations Capability intent services...")
    operations_count = 0
    try:
        from ..capabilities.operations.intent_services import (
            GenerateSOPService,
            GenerateSOPFromChatService,
            SOPChatMessageService,
            CreateWorkflowService,
            OptimizeProcessService,
            AnalyzeCoexistenceService
        )
        
        operations_services = [
            # SOP Generation (AI via SOPGenerationAgent)
            ("generate_sop", GenerateSOPService),
            ("generate_sop_from_chat", GenerateSOPFromChatService),
            ("sop_chat_message", SOPChatMessageService),
            # Workflow Management (AI via WorkflowOptimizationAgent)
            ("create_workflow", CreateWorkflowService),
            ("optimize_process", OptimizeProcessService),
            # Coexistence Analysis (AI via CoexistenceAnalysisAgent)
            ("analyze_coexistence", AnalyzeCoexistenceService),
        ]
        
        operations_count = sum(1 for intent, svc in operations_services if register_intent_service(intent, svc, "operations"))
        logger.info(f"  ✅ Operations Capability: {operations_count} intent services registered")
    except ImportError as e:
        logger.warning(f"  ⚠️ Operations Capability import error: {e}")
        operations_count = 0
    
    # Outcomes Capability intent services (Platform SDK Architecture)
    # Strategic synthesis services use real agents for AI generation
    logger.info("  → Registering Outcomes Capability intent services...")
    outcomes_count = 0
    try:
        from ..capabilities.outcomes.intent_services import (
            SynthesizeOutcomeService,
            GenerateRoadmapService,
            CreatePOCService,
            CreateBlueprintService,
            ExportArtifactService,
            CreateSolutionService
        )
        
        outcomes_services = [
            # Synthesis (AI via respective agents)
            ("synthesize_outcome", SynthesizeOutcomeService),
            ("generate_roadmap", GenerateRoadmapService),
            ("create_poc", CreatePOCService),
            ("create_blueprint", CreateBlueprintService),
            # Export & Solution Creation
            ("export_artifact", ExportArtifactService),
            ("create_solution", CreateSolutionService),
        ]
        
        outcomes_count = sum(1 for intent, svc in outcomes_services if register_intent_service(intent, svc, "outcomes"))
        logger.info(f"  ✅ Outcomes Capability: {outcomes_count} intent services registered")
    except ImportError as e:
        logger.warning(f"  ⚠️ Outcomes Capability import error: {e}")
        outcomes_count = 0
    
    # Security Capability intent services (Platform SDK Architecture)
    logger.info("  → Registering Security Capability intent services...")
    security_count = 0
    try:
        from ..capabilities.security.intent_services import (
            AuthenticateUserService,
            CheckEmailAvailabilityService,
            CreateSessionService,
            CreateUserAccountService,
            TerminateSessionService,
            ValidateAuthorizationService,
            ValidateTokenService
        )
        
        security_services = [
            # Authentication
            ("authenticate_user", AuthenticateUserService),
            ("validate_token", ValidateTokenService),
            # Registration
            ("create_user_account", CreateUserAccountService),
            ("check_email_availability", CheckEmailAvailabilityService),
            # Session Management
            ("create_session", CreateSessionService),
            ("validate_authorization", ValidateAuthorizationService),
            ("terminate_session", TerminateSessionService),
        ]
        
        security_count = sum(1 for intent, svc in security_services if register_intent_service(intent, svc, "security"))
        logger.info(f"  ✅ Security Capability: {security_count} intent services registered")
    except ImportError as e:
        logger.warning(f"  ⚠️ Security Capability import error: {e}")
        security_count = 0
    
    # Control Tower Capability intent services (Platform SDK Architecture)
    logger.info("  → Registering Control Tower Capability intent services...")
    control_tower_count = 0
    try:
        from ..capabilities.control_tower.intent_services import (
            GetPlatformStatisticsService,
            GetSystemHealthService,
            GetRealmHealthService,
            ListSolutionsService,
            GetSolutionStatusService,
            ValidateSolutionService,
            GetPatternsService,
            GetCodeExamplesService,
            GetDocumentationService
        )
        
        control_tower_services = [
            # Platform Monitoring
            ("get_platform_statistics", GetPlatformStatisticsService),
            ("get_system_health", GetSystemHealthService),
            ("get_realm_health", GetRealmHealthService),
            # Solution Management
            ("list_solutions", ListSolutionsService),
            ("get_solution_status", GetSolutionStatusService),
            ("validate_solution", ValidateSolutionService),
            # Developer Documentation
            ("get_patterns", GetPatternsService),
            ("get_code_examples", GetCodeExamplesService),
            ("get_documentation", GetDocumentationService),
        ]
        
        control_tower_count = sum(1 for intent, svc in control_tower_services if register_intent_service(intent, svc, "control_tower"))
        logger.info(f"  ✅ Control Tower Capability: {control_tower_count} intent services registered")
    except ImportError as e:
        logger.warning(f"  ⚠️ Control Tower Capability import error: {e}")
        control_tower_count = 0
    
    # Coexistence Capability intent services (Platform SDK Architecture)
    # KEY: Agent services now use REAL agents via ctx.reasoning.agents.invoke()
    logger.info("  → Registering Coexistence Capability intent services...")
    coexistence_count = 0
    try:
        from ..capabilities.coexistence.intent_services import (
            InitiateGuideAgentService,
            IntroducePlatformService,
            ListAvailableMCPToolsService,
            NavigateToSolutionService,
            ProcessGuideAgentMessageService,
            RouteToLiaisonAgentService,
            ShowSolutionCatalogService
        )
        
        coexistence_services = [
            # Introduction
            ("introduce_platform", IntroducePlatformService),
            ("show_solution_catalog", ShowSolutionCatalogService),
            # Navigation
            ("navigate_to_solution", NavigateToSolutionService),
            # Guide Agent (REAL AI via ctx.reasoning)
            ("initiate_guide_agent", InitiateGuideAgentService),
            ("process_guide_agent_message", ProcessGuideAgentMessageService),
            # Liaison Agent
            ("route_to_liaison_agent", RouteToLiaisonAgentService),
            # MCP Tool Orchestration
            ("list_available_mcp_tools", ListAvailableMCPToolsService),
        ]
        
        coexistence_count = sum(1 for intent, svc in coexistence_services if register_intent_service(intent, svc, "coexistence"))
        logger.info(f"  ✅ Coexistence Capability: {coexistence_count} intent services registered (using REAL agents)")
    except ImportError as e:
        logger.warning(f"  ⚠️ Coexistence Capability import error: {e}")
        coexistence_count = 0
    
    # Legacy: call_orchestrator_mcp_tool (not yet rebuilt)
    try:
        from ..realms.coexistence.intent_services import CallOrchestratorMCPToolService
        if register_intent_service("call_orchestrator_mcp_tool", CallOrchestratorMCPToolService, "coexistence"):
            coexistence_count += 1
    except ImportError:
        pass
    
    total_handlers = content_count + legacy_content_count + insights_count + operations_count + outcomes_count + security_count + control_tower_count + coexistence_count
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
    
    # Step 5: Create Data Steward (boundary contract store from Public Works; no adapter)
    boundary_contract_store = public_works.get_boundary_contract_store()
    data_steward_primitives = None
    data_steward_sdk = None
    if boundary_contract_store:
        from symphainy_platform.civic_systems.smart_city.primitives.data_steward_primitives import DataStewardPrimitives
        from symphainy_platform.civic_systems.smart_city.sdk.data_steward_sdk import DataStewardSDK
        data_steward_primitives = DataStewardPrimitives(boundary_contract_store=boundary_contract_store)
        data_steward_sdk = DataStewardSDK(data_steward_primitives=data_steward_primitives)
        logger.info("  ✅ Data Steward SDK created (boundary contract store from Public Works)")
    else:
        logger.info("  ⚠️ Boundary contract store not available; Data Steward SDK not created")

    # Step 6: Create ExecutionLifecycleManager
    logger.info("  → Creating ExecutionLifecycleManager...")
    execution_lifecycle_manager = ExecutionLifecycleManager(
        intent_registry=intent_registry,
        state_surface=state_surface,
        wal=wal,
        artifact_storage=public_works.get_artifact_storage_abstraction(),
        platform_context_factory=platform_context_factory,
        data_steward_sdk=data_steward_sdk,
    )
    logger.info("  ✅ ExecutionLifecycleManager created")

    # Get abstractions via get_* (protocol-typed surface; no direct attr access)
    registry_abstraction = public_works.get_registry_abstraction()
    artifact_storage = public_works.get_artifact_storage_abstraction()
    file_storage = public_works.get_file_storage_abstraction()
    
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
        solution_services=solution_services,
        platform_context_factory=platform_context_factory
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
    # Attach full services to app for tests and admin tooling (e.g. genesis_services fixture)
    app.state.runtime_services = services

    logger.info("✅ FastAPI app created with all routes registered")

    return app
