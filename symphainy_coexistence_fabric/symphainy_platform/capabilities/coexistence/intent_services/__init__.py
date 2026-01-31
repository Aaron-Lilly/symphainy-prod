"""
Coexistence Capability Intent Services (Platform SDK Architecture)

These intent services use the PlatformIntentService base class
and receive PlatformContext (ctx) for execution.

KEY ARCHITECTURAL CHANGE:
Agent services now wire to REAL agents via ctx.reasoning.agents.invoke()
instead of using keyword matching and canned responses.

Introduction:
    - IntroducePlatformService: Platform welcome and overview
    - ShowSolutionCatalogService: Available solutions catalog

Navigation:
    - NavigateToSolutionService: Route to specific solution

Guide Agent (REAL AI Chat):
    - InitiateGuideAgentService: Start Guide Agent session
    - ProcessGuideAgentMessageService: Process chat via REAL GuideAgent LLM

Liaison Agent:
    - RouteToLiaisonAgentService: Handoff to specialized liaison agents

MCP Tool Orchestration:
    - ListAvailableMCPToolsService: Discover available MCP tools
    - CallOrchestratorMCPToolService: Execute MCP tools
"""

from .initiate_guide_agent_service import InitiateGuideAgentService
from .introduce_platform_service import IntroducePlatformService
from .list_available_mcp_tools_service import ListAvailableMCPToolsService
from .navigate_to_solution_service import NavigateToSolutionService
from .process_guide_agent_message_service import ProcessGuideAgentMessageService
from .route_to_liaison_agent_service import RouteToLiaisonAgentService
from .show_solution_catalog_service import ShowSolutionCatalogService

__all__ = [
    # Introduction
    "IntroducePlatformService",
    "ShowSolutionCatalogService",
    # Navigation
    "NavigateToSolutionService",
    # Guide Agent (REAL AI)
    "InitiateGuideAgentService",
    "ProcessGuideAgentMessageService",
    # Liaison Agent
    "RouteToLiaisonAgentService",
    # MCP Tool Orchestration
    "ListAvailableMCPToolsService",
]
