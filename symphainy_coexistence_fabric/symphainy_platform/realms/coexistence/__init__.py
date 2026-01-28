"""
Coexistence Realm - Platform Entry and Navigation Domain

Provides intent services for:
- Platform Introduction: Welcome, catalog, explanation
- Navigation: Solution routing, context management
- Guide Agent: AI-powered assistance
- Liaison Agents: Specialist handoffs
- Chat Sessions: Conversation management
- Context Sharing: Cross-agent context

User-Facing Domain: Coexistence (Landing/Welcome)
Pattern: Only intent_services/ - no orchestrators, agents, or MCP servers

Note: GuideAgent and LiaisonAgents are in civic_systems/agentic/agents/
This realm provides the intent services they use.
"""

from .intent_services import (
    # Introduction
    IntroducePlatformService,
    ShowSolutionCatalogService,
    ExplainCoexistenceService,
    # Navigation
    NavigateToSolutionService,
    GetSolutionContextService,
    EstablishSolutionContextService,
    # Guide Agent
    InitiateGuideAgentService,
    ProcessGuideAgentMessageService,
    RouteToLiaisonAgentService,
    # Liaison Agent
    InitiateLiaisonAgentService,
    ProcessLiaisonAgentMessageService,
    GetPillarContextService,
    ExecutePillarActionService,
    # Chat Session
    GetChatSessionService,
    UpdateChatContextService,
    # Context Sharing
    ShareContextToAgentService,
    GetSharedContextService,
    MergeAgentContextsService,
    # MCP Tool Orchestration
    ListAvailableMCPToolsService,
    CallOrchestratorMCPToolService,
    ValidateMCPToolCallService,
)

__all__ = [
    # Introduction
    "IntroducePlatformService",
    "ShowSolutionCatalogService",
    "ExplainCoexistenceService",
    # Navigation
    "NavigateToSolutionService",
    "GetSolutionContextService",
    "EstablishSolutionContextService",
    # Guide Agent
    "InitiateGuideAgentService",
    "ProcessGuideAgentMessageService",
    "RouteToLiaisonAgentService",
    # Liaison Agent
    "InitiateLiaisonAgentService",
    "ProcessLiaisonAgentMessageService",
    "GetPillarContextService",
    "ExecutePillarActionService",
    # Chat Session
    "GetChatSessionService",
    "UpdateChatContextService",
    # Context Sharing
    "ShareContextToAgentService",
    "GetSharedContextService",
    "MergeAgentContextsService",
    # MCP Tool Orchestration
    "ListAvailableMCPToolsService",
    "CallOrchestratorMCPToolService",
    "ValidateMCPToolCallService",
]
