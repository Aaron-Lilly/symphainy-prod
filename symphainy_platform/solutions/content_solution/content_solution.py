"""
Content Solution - Content Realm Solution

The top-level solution that composes content journeys, exposes SOA APIs,
and wires up with the frontend via Experience SDK.

WHAT (Solution Role): I provide content capabilities for the platform
HOW (Solution Implementation): I compose content journeys and expose SOA APIs

Key Principle: The platform runs Solutions; Solutions run systems.
Solutions bind domain services to external systems.

Architecture:
- ContentSolution composes journey orchestrators
- Each journey orchestrator provides SOA APIs
- ContentSolutionMCPServer aggregates and exposes all SOA APIs as MCP tools
- compose_journey intent allows invoking journeys programmatically
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List
from utilities import get_logger, generate_event_id, get_clock
from symphainy_platform.runtime.intent_model import Intent, IntentFactory
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.civic_systems.platform_sdk.solution_model import (
    Solution,
    SolutionContext,
    DomainServiceBinding
)
from symphainy_platform.civic_systems.platform_sdk.solution_builder import SolutionBuilder
from symphainy_platform.realms.utils.structured_artifacts import create_structured_artifact

# Import journey orchestrators
from .journeys.file_upload_materialization_journey import FileUploadMaterializationJourney


class ContentSolution:
    """
    Content Solution - Content Realm Solution.
    
    Composes content journeys:
    - FileUploadMaterializationJourney
    - FileParsingJourney (future)
    - DeterministicEmbeddingJourney (future)
    - FileManagementJourney (future)
    
    Exposes SOA APIs:
    - compose_journey: Invoke a journey by ID
    - get_journeys: List available journeys
    - get_journey_status: Get journey execution status
    
    Supports compose_journey intent pattern for programmatic journey invocation.
    """
    
    SOLUTION_ID = "content_solution"
    SOLUTION_NAME = "Content Solution"
    
    # Supported intent types for this solution
    SUPPORTED_INTENTS = [
        "compose_journey",
        "ingest_file",
        "save_materialization",
        "parse_content",
        "create_deterministic_embeddings",
        "extract_embeddings",
        "list_artifacts",
        "retrieve_artifact_metadata",
        "archive_file"
    ]
    
    def __init__(
        self,
        public_works: Optional[Any] = None,
        state_surface: Optional[Any] = None
    ):
        """
        Initialize Content Solution.
        
        Args:
            public_works: Public Works Foundation Service
            state_surface: State Surface for artifact management
        """
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        self.public_works = public_works
        self.state_surface = state_surface
        
        # Solution configuration
        self.solution_id = self.SOLUTION_ID
        self.solution_name = self.SOLUTION_NAME
        
        # Initialize journey orchestrators
        self._journeys: Dict[str, Any] = {}
        self._initialize_journeys()
        
        # Build solution model
        self._solution_model = self._build_solution_model()
        
        # MCP Server (lazy initialization)
        self._mcp_server = None
        
        # Telemetry
        self.telemetry_service = None
    
    def _initialize_journeys(self):
        """Initialize all journey orchestrators."""
        # File Upload & Materialization Journey
        self._journeys["file_upload_materialization"] = FileUploadMaterializationJourney(
            public_works=self.public_works,
            state_surface=self.state_surface
        )
        
        # Future journeys will be added here:
        # self._journeys["file_parsing"] = FileParsingJourney(...)
        # self._journeys["deterministic_embedding"] = DeterministicEmbeddingJourney(...)
        # self._journeys["file_management"] = FileManagementJourney(...)
        
        self.logger.info(f"Initialized {len(self._journeys)} journey orchestrators")
    
    def _build_solution_model(self) -> Solution:
        """Build formal Solution model."""
        builder = SolutionBuilder(solution_id=self.solution_id)
        
        builder.with_context(
            goals=[
                "Provide content ingestion capabilities",
                "Manage content lifecycle (PENDING → READY → ARCHIVED)",
                "Enable semantic content analysis"
            ],
            constraints=[
                "All operations via intents (no direct API calls)",
                "All artifacts registered in State Surface",
                "No backward compatibility - follow current patterns only"
            ],
            risk="Low"
        )
        
        builder.add_domain_binding(
            domain="content",
            system_name="file_storage",
            adapter_type="gcs_adapter",
            adapter_config={
                "bucket_prefix": "content_"
            }
        )
        
        builder.register_intents(self.SUPPORTED_INTENTS)
        
        builder.with_metadata({
            "solution_name": self.SOLUTION_NAME,
            "version": "1.0.0",
            "journeys": list(self._journeys.keys())
        })
        
        return builder.build()
    
    def get_journeys(self) -> Dict[str, Any]:
        """
        Get all journey orchestrators.
        
        Used by ContentSolutionMCPServer to register tools.
        
        Returns:
            Dict of journey_id -> journey orchestrator
        """
        return self._journeys.copy()
    
    def get_journey(self, journey_id: str) -> Optional[Any]:
        """Get a specific journey orchestrator."""
        return self._journeys.get(journey_id)
    
    async def initialize_mcp_server(self):
        """
        Initialize MCP server.
        
        Should be called after solution initialization.
        
        Returns:
            ContentSolutionMCPServer instance
        """
        if not self._mcp_server:
            from .mcp_server.content_solution_mcp_server import ContentSolutionMCPServer
            
            self._mcp_server = ContentSolutionMCPServer(
                solution=self,
                public_works=self.public_works,
                state_surface=self.state_surface
            )
            await self._mcp_server.initialize()
        
        return self._mcp_server
    
    def get_mcp_server(self):
        """Get MCP server instance (may be None if not initialized)."""
        return self._mcp_server
    
    async def handle_intent(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle intent by routing to appropriate journey or handler.
        
        This is the main entry point for intent handling at the solution level.
        
        Args:
            intent: The intent to handle
            context: Execution context
        
        Returns:
            Dict with "artifacts" and "events" keys
        """
        intent_type = intent.intent_type
        
        self.logger.info(f"Handling intent: {intent_type}")
        
        # Initialize telemetry if needed
        await self._ensure_telemetry()
        
        # Handle compose_journey intent
        if intent_type == "compose_journey":
            return await self._handle_compose_journey(intent, context)
        
        # Route to appropriate journey based on intent type
        journey = self._find_journey_for_intent(intent_type)
        if journey:
            # For journey-level intents, use compose_journey
            return await journey.compose_journey(context, intent.parameters)
        
        # Fallback to unknown intent
        raise ValueError(f"Unknown intent type: {intent_type} (Solution: {self.solution_id})")
    
    def _find_journey_for_intent(self, intent_type: str) -> Optional[Any]:
        """Find the journey that handles a given intent type."""
        # Map intent types to journeys
        intent_to_journey = {
            "ingest_file": "file_upload_materialization",
            "save_materialization": "file_upload_materialization",
            # Future mappings:
            # "parse_content": "file_parsing",
            # "create_deterministic_embeddings": "deterministic_embedding",
            # "extract_embeddings": "deterministic_embedding",
            # "list_artifacts": "file_management",
            # "archive_file": "file_management",
        }
        
        journey_id = intent_to_journey.get(intent_type)
        if journey_id:
            return self._journeys.get(journey_id)
        
        return None
    
    async def _handle_compose_journey(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle compose_journey intent.
        
        This is the special intent for invoking journeys programmatically.
        
        Parameters:
            - journey_id: Journey identifier
            - journey_params: Parameters for the journey
        
        Returns:
            Journey execution result
        """
        journey_id = intent.parameters.get("journey_id")
        journey_params = intent.parameters.get("journey_params", {})
        
        if not journey_id:
            raise ValueError("journey_id is required for compose_journey intent")
        
        journey = self._journeys.get(journey_id)
        if not journey:
            available = list(self._journeys.keys())
            raise ValueError(f"Unknown journey: {journey_id}. Available: {available}")
        
        self.logger.info(f"Composing journey: {journey_id}")
        
        # Execute journey
        result = await journey.compose_journey(context, journey_params)
        
        return result
    
    # ========================================
    # SOA API Handlers (solution-level)
    # ========================================
    
    def get_soa_apis(self) -> Dict[str, Dict[str, Any]]:
        """
        Get solution-level SOA API definitions.
        
        These are solution-level APIs (not journey-specific).
        
        Returns:
            Dict of SOA API definitions
        """
        return {
            "compose_journey": {
                "handler": self._handle_compose_journey_soa,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "journey_id": {
                            "type": "string",
                            "description": "Journey identifier"
                        },
                        "journey_params": {
                            "type": "object",
                            "description": "Journey-specific parameters"
                        },
                        "user_context": {
                            "type": "object",
                            "description": "User context (tenant_id, session_id)"
                        }
                    },
                    "required": ["journey_id"]
                },
                "description": "Compose and execute a content journey"
            },
            "list_journeys": {
                "handler": self._handle_list_journeys_soa,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "user_context": {
                            "type": "object",
                            "description": "User context"
                        }
                    },
                    "required": []
                },
                "description": "List available content journeys"
            },
            "get_solution_info": {
                "handler": self._handle_get_solution_info_soa,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "user_context": {
                            "type": "object",
                            "description": "User context"
                        }
                    },
                    "required": []
                },
                "description": "Get Content Solution information"
            }
        }
    
    async def _handle_compose_journey_soa(self, **kwargs) -> Dict[str, Any]:
        """SOA API handler for compose_journey."""
        journey_id = kwargs.get("journey_id")
        journey_params = kwargs.get("journey_params", {})
        user_context = kwargs.get("user_context", {})
        
        # Create execution context
        context = ExecutionContext(
            execution_id=generate_event_id(),
            tenant_id=user_context.get("tenant_id", "default"),
            session_id=user_context.get("session_id", generate_event_id()),
            solution_id=self.solution_id
        )
        context.state_surface = self.state_surface
        
        # Create intent
        intent = IntentFactory.create_intent(
            intent_type="compose_journey",
            tenant_id=context.tenant_id,
            session_id=context.session_id,
            solution_id=self.solution_id,
            parameters={
                "journey_id": journey_id,
                "journey_params": journey_params
            }
        )
        
        return await self._handle_compose_journey(intent, context)
    
    async def _handle_list_journeys_soa(self, **kwargs) -> Dict[str, Any]:
        """SOA API handler for list_journeys."""
        journeys = []
        
        for journey_id, journey in self._journeys.items():
            journey_info = {
                "journey_id": journey_id,
                "journey_name": getattr(journey, 'JOURNEY_NAME', journey_id),
                "description": getattr(journey, '__doc__', '').strip().split('\n')[0] if hasattr(journey, '__doc__') else ''
            }
            
            # Get SOA APIs if available
            if hasattr(journey, 'get_soa_apis'):
                journey_info["available_actions"] = list(journey.get_soa_apis().keys())
            
            journeys.append(journey_info)
        
        return {
            "success": True,
            "solution_id": self.solution_id,
            "journeys": journeys,
            "journey_count": len(journeys)
        }
    
    async def _handle_get_solution_info_soa(self, **kwargs) -> Dict[str, Any]:
        """SOA API handler for get_solution_info."""
        return {
            "success": True,
            "solution_id": self.solution_id,
            "solution_name": self.solution_name,
            "supported_intents": self.SUPPORTED_INTENTS,
            "journeys": list(self._journeys.keys()),
            "solution_model": self._solution_model.to_dict() if self._solution_model else None
        }
    
    async def _ensure_telemetry(self):
        """Ensure telemetry service is initialized."""
        if not self.telemetry_service and self.public_works:
            try:
                from symphainy_platform.civic_systems.agentic.telemetry.agentic_telemetry_service import AgenticTelemetryService
                self.telemetry_service = AgenticTelemetryService()
            except Exception as e:
                self.logger.debug(f"Telemetry service not available: {e}")
    
    # ========================================
    # Experience SDK Integration
    # ========================================
    
    def get_experience_sdk_config(self) -> Dict[str, Any]:
        """
        Get configuration for Experience SDK integration.
        
        This configuration tells the frontend how to interact with this solution.
        
        Returns:
            Dict with Experience SDK configuration
        """
        # Collect all SOA APIs from journeys and solution
        all_apis = {}
        
        # Solution-level APIs
        all_apis.update(self.get_soa_apis())
        
        # Journey-level APIs
        for journey_id, journey in self._journeys.items():
            if hasattr(journey, 'get_soa_apis'):
                journey_apis = journey.get_soa_apis()
                for api_name, api_def in journey_apis.items():
                    # Prefix with journey ID to avoid conflicts
                    all_apis[f"{journey_id}_{api_name}"] = api_def
        
        return {
            "solution_id": self.solution_id,
            "solution_name": self.solution_name,
            "supported_intents": self.SUPPORTED_INTENTS,
            "journeys": [
                {
                    "journey_id": jid,
                    "journey_name": getattr(j, 'JOURNEY_NAME', jid)
                }
                for jid, j in self._journeys.items()
            ],
            "soa_apis": {
                name: {
                    "input_schema": api_def.get("input_schema", {}),
                    "description": api_def.get("description", "")
                }
                for name, api_def in all_apis.items()
            },
            "integration_patterns": {
                "intent_submission": {
                    "description": "Submit intents via Experience SDK submitIntent()",
                    "example": {
                        "intent_type": "compose_journey",
                        "parameters": {
                            "journey_id": "file_upload_materialization",
                            "journey_params": {
                                "file_content": "<base64>",
                                "file_name": "example.pdf"
                            }
                        }
                    }
                },
                "journey_invocation": {
                    "description": "Invoke journeys directly via compose_journey intent",
                    "available_journeys": list(self._journeys.keys())
                }
            }
        }
