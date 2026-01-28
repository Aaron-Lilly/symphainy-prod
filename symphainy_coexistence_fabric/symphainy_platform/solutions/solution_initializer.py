"""
Solution Initializer - Register and Initialize All Platform Solutions

This module provides the startup procedure for initializing all platform solutions.
Called from runtime_main.py and experience_main.py.

WHAT (Initializer Role): I register and initialize all platform solutions
HOW (Initializer Implementation): I create solution instances and register intents

Initialization Order:
1. Create PublicWorks and StateSurface
2. Create Solution instances
3. Register solutions with SolutionRegistry
4. Register compose_journey and solution intents with IntentRegistry
5. Initialize MCP Servers (optional)

Usage:
    services = await initialize_solutions(
        public_works=public_works,
        state_surface=state_surface,
        solution_registry=solution_registry,
        intent_registry=intent_registry
    )
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional
from utilities import get_logger

from .coexistence import CoexistenceSolution
from .content_solution import ContentSolution
from .insights_solution import InsightsSolution
from .journey_solution import JourneySolution
from .operations_solution import OperationsSolution
from .outcomes_solution import OutcomesSolution
from .security_solution import SecuritySolution
from .control_tower import ControlTower

logger = get_logger(__name__)


class SolutionServices:
    """Container for all initialized solutions."""
    
    def __init__(self):
        self.coexistence: Optional[CoexistenceSolution] = None
        self.content: Optional[ContentSolution] = None
        self.insights: Optional[InsightsSolution] = None
        self.journey: Optional[JourneySolution] = None
        self.operations: Optional[OperationsSolution] = None
        self.outcomes: Optional[OutcomesSolution] = None
        self.security: Optional[SecuritySolution] = None
        self.control_tower: Optional[ControlTower] = None
        
        self._solutions: Dict[str, Any] = {}
        self._mcp_servers: Dict[str, Any] = {}
    
    def get_solution(self, solution_id: str) -> Optional[Any]:
        """Get solution by ID."""
        return self._solutions.get(solution_id)
    
    def list_solutions(self) -> Dict[str, Any]:
        """List all solutions."""
        return self._solutions.copy()
    
    def get_mcp_server(self, solution_id: str) -> Optional[Any]:
        """Get MCP server for solution."""
        return self._mcp_servers.get(solution_id)


async def initialize_solutions(
    public_works: Optional[Any] = None,
    state_surface: Optional[Any] = None,
    solution_registry: Optional[Any] = None,
    intent_registry: Optional[Any] = None,
    curator: Optional[Any] = None,
    initialize_mcp_servers: bool = True
) -> SolutionServices:
    """
    Initialize all platform solutions.
    
    Args:
        public_works: Public Works Foundation Service
        state_surface: State Surface for artifact management
        solution_registry: Solution Registry for registration
        intent_registry: Intent Registry for compose_journey intents
        curator: Curator for MCP tool discovery (for GuideAgent)
        initialize_mcp_servers: Whether to initialize MCP servers
    
    Returns:
        SolutionServices container with all initialized solutions
    """
    logger.info("🚀 Initializing Platform Solutions...")
    
    services = SolutionServices()
    
    # 1. Initialize Coexistence Solution (Platform Front Door)
    logger.info("  → Initializing CoexistenceSolution...")
    services.coexistence = CoexistenceSolution(
        public_works=public_works,
        state_surface=state_surface,
        solution_registry=solution_registry,
        curator=curator
    )
    services._solutions["coexistence"] = services.coexistence
    logger.info("  ✅ CoexistenceSolution initialized")
    
    # 2. Initialize Content Solution
    logger.info("  → Initializing ContentSolution...")
    services.content = ContentSolution(
        public_works=public_works,
        state_surface=state_surface
    )
    services._solutions["content_solution"] = services.content
    logger.info("  ✅ ContentSolution initialized")
    
    # 3. Initialize Insights Solution
    logger.info("  → Initializing InsightsSolution...")
    services.insights = InsightsSolution(
        public_works=public_works,
        state_surface=state_surface
    )
    services._solutions["insights_solution"] = services.insights
    logger.info("  ✅ InsightsSolution initialized")
    
    # 4. Initialize Journey Solution
    logger.info("  → Initializing JourneySolution...")
    services.journey = JourneySolution(
        public_works=public_works,
        state_surface=state_surface
    )
    services._solutions["journey_solution"] = services.journey
    logger.info("  ✅ JourneySolution initialized")
    
    # 5. Initialize Operations Solution
    logger.info("  → Initializing OperationsSolution...")
    services.operations = OperationsSolution(
        public_works=public_works,
        state_surface=state_surface
    )
    services._solutions["operations_solution"] = services.operations
    logger.info("  ✅ OperationsSolution initialized")
    
    # 6. Initialize Outcomes Solution
    logger.info("  → Initializing OutcomesSolution...")
    services.outcomes = OutcomesSolution(
        public_works=public_works,
        state_surface=state_surface
    )
    services._solutions["outcomes_solution"] = services.outcomes
    logger.info("  ✅ OutcomesSolution initialized")
    
    # 7. Initialize Security Solution (FOUNDATIONAL)
    logger.info("  → Initializing SecuritySolution...")
    services.security = SecuritySolution(
        public_works=public_works,
        state_surface=state_surface
    )
    services._solutions["security_solution"] = services.security
    logger.info("  ✅ SecuritySolution initialized")
    
    # 8. Initialize Control Tower
    logger.info("  → Initializing ControlTower...")
    services.control_tower = ControlTower(
        public_works=public_works,
        state_surface=state_surface,
        solution_registry=solution_registry
    )
    services._solutions["control_tower"] = services.control_tower
    logger.info("  ✅ ControlTower initialized")
    
    # Register solutions with SolutionRegistry if provided
    if solution_registry:
        logger.info("  → Registering solutions with SolutionRegistry...")
        for solution_id, solution in services._solutions.items():
            try:
                # Create Solution model for registry
                from symphainy_platform.civic_systems.platform_sdk.solution_model import (
                    Solution, SolutionContext, DomainServiceBinding
                )
                
                # Get journeys from solution
                journeys = []
                if hasattr(solution, 'get_journeys'):
                    journeys = list(solution.get_journeys().keys())
                
                # Get supported intents
                supported_intents = getattr(solution, 'SUPPORTED_INTENTS', [])
                
                # Create solution context
                solution_name = getattr(solution, 'SOLUTION_NAME', solution_id)
                solution_context = SolutionContext(
                    goals=[f"Provide {solution_name} capabilities"],
                    constraints=[],
                    risk="Low",
                    metadata={
                        "name": solution_name,
                        "description": f"Platform solution: {solution_id}",
                        "version": "1.0.0",
                        "owner": "platform"
                    }
                )
                
                solution_model = Solution(
                    solution_id=solution_id,
                    solution_context=solution_context,
                    domain_service_bindings=[],
                    supported_intents=supported_intents,
                    metadata={
                        "journeys": journeys,
                        "mcp_prefix": f"{solution_id.replace('_solution', '').replace('_', '')}_"
                    }
                )
                
                solution_registry.register_solution(solution_model)
                solution_registry.activate_solution(solution_id)
                logger.info(f"    ✅ Registered: {solution_id}")
                
            except Exception as e:
                logger.warning(f"    ⚠️ Failed to register {solution_id}: {e}")
    
    # Register compose_journey intents with IntentRegistry if provided
    if intent_registry:
        logger.info("  → Registering compose_journey intents...")
        for solution_id, solution in services._solutions.items():
            if hasattr(solution, 'handle_intent'):
                try:
                    # Register compose_journey for this solution
                    intent_registry.register_intent(
                        intent_type="compose_journey",
                        handler_name=f"{solution_id}_compose_journey",
                        handler_function=solution.handle_intent,
                        metadata={
                            "solution": solution_id,
                            "handler": "compose_journey"
                        }
                    )
                    logger.info(f"    ✅ Registered compose_journey for {solution_id}")
                    
                    # Also register solution-specific intents
                    supported_intents = getattr(solution, 'SUPPORTED_INTENTS', [])
                    for intent_type in supported_intents:
                        if intent_type != "compose_journey":
                            intent_registry.register_intent(
                                intent_type=intent_type,
                                handler_name=f"{solution_id}_{intent_type}",
                                handler_function=solution.handle_intent,
                                metadata={
                                    "solution": solution_id,
                                    "intent": intent_type
                                }
                            )
                    
                except Exception as e:
                    logger.warning(f"    ⚠️ Failed to register intents for {solution_id}: {e}")
    
    # Initialize MCP Servers if requested
    if initialize_mcp_servers:
        logger.info("  → Initializing MCP Servers...")
        for solution_id, solution in services._solutions.items():
            if hasattr(solution, 'initialize_mcp_server'):
                try:
                    mcp_server = await solution.initialize_mcp_server()
                    services._mcp_servers[solution_id] = mcp_server
                    logger.info(f"    ✅ MCP Server initialized for {solution_id}")
                except Exception as e:
                    logger.warning(f"    ⚠️ Failed to initialize MCP Server for {solution_id}: {e}")
    
    total_solutions = len(services._solutions)
    total_mcp_servers = len(services._mcp_servers)
    
    logger.info(f"✅ Platform Solutions initialized: {total_solutions} solutions, {total_mcp_servers} MCP servers")
    
    return services


def get_solution_summary() -> Dict[str, Any]:
    """
    Get a summary of all platform solutions and their journeys.
    
    Returns:
        Dictionary with solution information for documentation
    """
    return {
        "coexistence": {
            "name": "Coexistence Solution",
            "description": "Platform entry point (introduction, navigation, guide agent)",
            "mcp_prefix": "coexist_",
            "journeys": ["introduction", "navigation", "guide_agent"],
            "status": "implemented"
        },
        "content_solution": {
            "name": "Content Solution",
            "description": "File upload, parsing, embedding, management",
            "mcp_prefix": "content_",
            "journeys": ["file_upload_materialization", "file_parsing", "deterministic_embedding", "file_management"],
            "status": "implemented"
        },
        "insights_solution": {
            "name": "Insights Solution",
            "description": "Business analysis, data quality, interpretation, lineage",
            "mcp_prefix": "insights_",
            "journeys": ["business_analysis", "data_quality", "data_analysis", "data_interpretation", "lineage_visualization", "relationship_mapping"],
            "status": "implemented"
        },
        "journey_solution": {
            "name": "Journey Solution",
            "description": "Workflow/SOP management, coexistence analysis",
            "mcp_prefix": "journey_",
            "journeys": ["workflow_sop", "coexistence_analysis"],
            "status": "implemented"
        },
        "operations_solution": {
            "name": "Operations Solution",
            "description": "Workflows, SOPs, process optimization, coexistence",
            "mcp_prefix": "ops_",
            "journeys": ["workflow_management", "sop_management", "process_optimization", "coexistence_analysis"],
            "status": "implemented"
        },
        "outcomes_solution": {
            "name": "Outcomes Solution",
            "description": "POC creation, roadmap generation, solution synthesis, blueprints",
            "mcp_prefix": "outcomes_",
            "journeys": ["poc_creation", "poc_proposal", "roadmap_generation", "outcome_synthesis", "blueprint_creation", "solution_creation", "artifact_export"],
            "status": "implemented"
        },
        "security_solution": {
            "name": "Security Solution",
            "description": "Authentication, registration, session management (FOUNDATIONAL)",
            "mcp_prefix": "security_",
            "journeys": ["authentication", "registration", "session_management"],
            "status": "implemented",
            "is_foundational": True
        },
        "control_tower": {
            "name": "Control Tower",
            "description": "Platform command center (monitoring, management, composition)",
            "mcp_prefix": "tower_",
            "journeys": ["platform_monitoring", "solution_management", "developer_docs", "solution_composition"],
            "status": "implemented"
        }
    }
