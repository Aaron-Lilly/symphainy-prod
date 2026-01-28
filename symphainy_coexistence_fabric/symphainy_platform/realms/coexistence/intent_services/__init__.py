"""
Coexistence Intent Services

Intent services for platform entry and navigation:
- Introduction: Platform welcome, catalog, explanation
- Navigation: Solution routing, context management
- Guide Agent: AI assistance intents
- Liaison Agent: Specialist handoff intents
- Chat Session: Conversation management
- Context Sharing: Cross-agent context
- MCP Tool Orchestration: Tool discovery and execution
"""

# Placeholder imports - services to be implemented
# These will be created as individual files following the Security realm pattern

# Introduction
class IntroducePlatformService:
    """Introduce the platform to new users."""
    pass

class ShowSolutionCatalogService:
    """Show available solutions."""
    pass

class ExplainCoexistenceService:
    """Explain the coexistence philosophy."""
    pass

# Navigation
class NavigateToSolutionService:
    """Navigate user to a specific solution."""
    pass

class GetSolutionContextService:
    """Get context for a solution."""
    pass

class EstablishSolutionContextService:
    """Establish working context within a solution."""
    pass

# Guide Agent
class InitiateGuideAgentService:
    """Initiate a Guide Agent session."""
    pass

class ProcessGuideAgentMessageService:
    """Process a message through Guide Agent."""
    pass

class RouteToLiaisonAgentService:
    """Route conversation to a Liaison Agent."""
    pass

# Liaison Agent
class InitiateLiaisonAgentService:
    """Initiate a Liaison Agent session for a pillar."""
    pass

class ProcessLiaisonAgentMessageService:
    """Process a message through Liaison Agent."""
    pass

class GetPillarContextService:
    """Get context for a specific pillar."""
    pass

class ExecutePillarActionService:
    """Execute an action within a pillar."""
    pass

# Chat Session
class GetChatSessionService:
    """Get or create a chat session."""
    pass

class UpdateChatContextService:
    """Update chat session context."""
    pass

# Context Sharing
class ShareContextToAgentService:
    """Share context from one agent to another."""
    pass

class GetSharedContextService:
    """Get shared context between agents."""
    pass

class MergeAgentContextsService:
    """Merge contexts from multiple agents."""
    pass

# MCP Tool Orchestration
class ListAvailableMCPToolsService:
    """List all available MCP tools from all solutions."""
    pass

class CallOrchestratorMCPToolService:
    """Call an MCP tool with governance."""
    pass

class ValidateMCPToolCallService:
    """Validate an MCP tool call before execution."""
    pass

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
