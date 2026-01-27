"""
Runtime Context Hydration Service

Service for assembling authoritative AgentRuntimeContext from committed sources.

ARCHITECTURAL PRINCIPLE: Only reads from committed_context (not discovery_context).
Discovery context is provisional until committed by user/platform.

WHAT (Service Role): I assemble authoritative runtime context
HOW (Service Implementation): I read from committed sources in priority order
"""

import sys
from pathlib import Path

# Add project root to path
current = Path(__file__).resolve()
project_root = current
for _ in range(10):
    if (project_root / "pyproject.toml").exists() or (project_root / "requirements.txt").exists():
        break
    project_root = project_root.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional
from utilities import get_logger
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.civic_systems.agentic.models.agent_runtime_context import AgentRuntimeContext


class RuntimeContextHydrationService:
    """
    Service for hydrating AgentRuntimeContext from committed sources.
    
    Priority Order:
    1. Request dict (explicit parameters) - highest priority
    2. ExecutionContext.metadata
    3. Session committed_context (NOT discovery_context!)
    4. Intent.parameters (fallback)
    
    ARCHITECTURAL PRINCIPLE: Only reads from committed_context.
    Discovery context is provisional and must be committed before use.
    """
    
    def __init__(self):
        """Initialize Runtime Context Hydration Service."""
        self.logger = get_logger(self.__class__.__name__)
    
    async def create_runtime_context(
        self,
        request: Dict[str, Any],
        context: ExecutionContext
    ) -> AgentRuntimeContext:
        """
        Create authoritative runtime context from committed sources.
        
        ARCHITECTURAL PRINCIPLE: Runtime context is optional.
        If no committed context exists (e.g., user bypassed landing page),
        returns empty defaults. Agents should handle empty context gracefully.
        
        Args:
            request: Request dictionary (may contain explicit context fields)
            context: Execution context
        
        Returns:
            AgentRuntimeContext (authoritative, read-only, may be empty)
        """
        self.logger.debug(f"Creating runtime context for session {context.session_id}")
        
        # Extract from session state (committed_context only)
        committed_context = {}
        if context and context.state_surface:
            try:
                session_state = await context.state_surface.get_session_state(
                    context.session_id,
                    context.tenant_id
                )
                
                if session_state:
                    # Only read from committed_context (not discovery_context)
                    committed_context = session_state.get("committed_context", {})
                    
                    # Log if discovery_context exists but committed_context doesn't
                    if session_state.get("discovery_context") and not committed_context:
                        self.logger.debug(
                            f"Discovery context exists but not yet committed for session {context.session_id}"
                        )
            except Exception as e:
                self.logger.debug(f"Could not retrieve session state: {e}")
        
        # Priority order: request > metadata > committed_context > intent.parameters
        business_context = (
            request.get("business_context") or
            context.metadata.get("business_context") or
            committed_context.get("business_context") or
            {}
        )
        
        journey_goal = (
            request.get("journey_goal") or
            context.metadata.get("journey_goal") or
            committed_context.get("journey_goal") or
            (context.intent.parameters.get("journey_goal") if context.intent else "") or
            ""
        )
        
        human_preferences = (
            request.get("human_preferences") or
            context.metadata.get("human_preferences") or
            committed_context.get("human_preferences") or
            (context.intent.parameters.get("human_preferences") if context.intent else {}) or
            {}
        )
        
        # Get available artifacts from session state
        available_artifacts = []
        if context and context.state_surface:
            try:
                session_state = await context.state_surface.get_session_state(
                    context.session_id,
                    context.tenant_id
                )
                if session_state:
                    available_artifacts = session_state.get("available_artifacts", [])
            except Exception as e:
                self.logger.debug(f"Could not retrieve available artifacts: {e}")
        
        # Create AgentRuntimeContext (authoritative, immutable)
        runtime_context = AgentRuntimeContext(
            business_context=business_context if isinstance(business_context, dict) else {},
            journey_goal=journey_goal if isinstance(journey_goal, str) else "",
            human_preferences=human_preferences if isinstance(human_preferences, dict) else {},
            available_artifacts=available_artifacts,
            session_state=committed_context  # Include committed context as session state
        )
        
        self.logger.debug(
            f"✅ Runtime context created: "
            f"industry={runtime_context.business_context.get('industry', 'none')}, "
            f"goal={runtime_context.journey_goal[:50] if runtime_context.journey_goal else 'none'}"
        )
        
        return runtime_context
