"""
Coexistence Realm - Platform Entry and Navigation Domain

Provides intent services for:
- Platform Introduction: Welcome, catalog, explanation
- Navigation: Solution routing, context management
- Guide Agent: AI-powered assistance
- Liaison Agents: Specialist handoffs
- MCP Tool Orchestration: Tool discovery and execution

User-Facing Domain: Coexistence (Landing/Welcome)
Pattern: Only intent_services/ - no orchestrators, agents, or MCP servers

Note: GuideAgent and LiaisonAgents are in civic_systems/agentic/agents/
This realm provides the intent services they use.
"""

from .intent_services import (
    # Introduction
    IntroducePlatformService,
    ShowSolutionCatalogService,
    # Navigation
    NavigateToSolutionService,
    # Guide Agent
    InitiateGuideAgentService,
    ProcessGuideAgentMessageService,
    # Liaison Agent
    RouteToLiaisonAgentService,
    # MCP Tool Orchestration
    ListAvailableMCPToolsService,
    CallOrchestratorMCPToolService,
)

__all__ = [
    # Introduction
    "IntroducePlatformService",
    "ShowSolutionCatalogService",
    # Navigation
    "NavigateToSolutionService",
    # Guide Agent
    "InitiateGuideAgentService",
    "ProcessGuideAgentMessageService",
    # Liaison Agent
    "RouteToLiaisonAgentService",
    # MCP Tool Orchestration
    "ListAvailableMCPToolsService",
    "CallOrchestratorMCPToolService",
]
