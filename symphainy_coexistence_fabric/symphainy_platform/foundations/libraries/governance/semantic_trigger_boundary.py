"""
Semantic Trigger Boundary - Enforce Pull-Based Semantic Computation

Enabling service for enforcing CTO's principle: No semantic computation without explicit trigger.

WHAT (Enabling Service Role): I enforce pull-based semantic computation
HOW (Enabling Service Implementation): I validate triggers before allowing semantic computation

CTO Principle: No semantic computation without explicit trigger
Platform Enhancement: Use intent system for triggers
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List
from utilities import get_logger
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.runtime.intent_model import Intent


class SemanticTriggerBoundary:
    """
    Enforces pull-based semantic computation.
    
    CTO Principle: No semantic computation without explicit trigger
    Platform Enhancement: Uses intent system for trigger detection
    """
    
    TRIGGER_TYPES = [
        "explicit_user_intent",
        "downstream_agent_request",
        "missing_semantic_signal"
    ]
    
    def __init__(self, public_works: Optional[Any] = None):
        """
        Initialize Semantic Trigger Boundary.
        
        Args:
            public_works: Public Works Foundation Service (for accessing abstractions)
        """
        self.public_works = public_works
        self.logger = get_logger(self.__class__.__name__)
    
    def should_compute_semantics(
        self,
        trigger_type: str,
        intent: Optional[Intent] = None,
        context: Optional[ExecutionContext] = None
    ) -> bool:
        """
        Determine if semantic computation should proceed.
        
        Platform Enhancement: Uses intent system for trigger detection
        
        Args:
            trigger_type: Type of trigger (must be in TRIGGER_TYPES)
            intent: Optional intent (for explicit_user_intent)
            context: Optional execution context
        
        Returns:
            True if semantic computation should proceed, False otherwise
        """
        # ANTI-CORRUPTION: Fail fast on invalid trigger types
        if trigger_type not in self.TRIGGER_TYPES:
            raise ValueError(
                f"❌ ANTI-PATTERN: Invalid trigger type '{trigger_type}'.\n"
                f"Must be one of: {self.TRIGGER_TYPES}\n"
                "\n"
                "This ensures semantic computation only happens on explicit triggers:\n"
                "  - explicit_user_intent: User explicitly requested semantic computation\n"
                "  - downstream_agent_request: Agent requested semantic signal\n"
                "  - missing_semantic_signal: Semantic signal required but missing\n"
                "\n"
                "CTO Principle: No semantic computation without explicit trigger."
            )
        
        # Platform Enhancement: Intent-driven trigger detection
        if trigger_type == "explicit_user_intent":
            if intent is None:
                return False
            # Check if intent is for semantic hydration
            return intent.intent_type in [
                "hydrate_semantic_profile",
                "extract_semantic_signals",
                "get_semantic_interpretation"
            ]
        
        if trigger_type == "downstream_agent_request":
            # Check if agent requested semantic signal via intent
            if context:
                return context.get("requested_semantic_signal") is not None
            return False
        
        if trigger_type == "missing_semantic_signal":
            # Check if semantic signal is required but missing
            if context:
                return context.get("required_semantic_signal") is not None
            return False
        
        return False
    
    async def log_semantic_computation(
        self,
        chunk_ids: List[str],
        semantic_profile: str,
        model_name: str,
        trigger_type: str,
        context: ExecutionContext
    ):
        """
        Log semantic computation for cost tracking.
        
        Platform Enhancement: Uses Runtime WAL for cost tracking
        
        Args:
            chunk_ids: List of chunk IDs that were embedded
            semantic_profile: Semantic profile name
            model_name: Embedding model name
            trigger_type: Type of trigger that caused computation
            context: Execution context
        """
        self.logger.info(
            f"Semantic computation logged: "
            f"profile={semantic_profile}, model={model_name}, "
            f"trigger={trigger_type}, chunks={len(chunk_ids)}, "
            f"tenant={context.tenant_id}"
        )
        
        # TODO: Log to Runtime WAL for cost tracking (Platform enhancement)
        # This would integrate with Runtime WAL when available
        # await self.runtime_wal.log_semantic_computation(...)
