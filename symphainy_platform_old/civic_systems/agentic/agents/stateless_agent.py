"""
Stateless Agent Base - Deterministic/Semantic Data Generation
"""

import sys
from pathlib import Path

# Add project root to path
# Find project root by looking for common markers (pyproject.toml, requirements.txt, etc.)
current = Path(__file__).resolve()
project_root = current
for _ in range(10):  # Max 10 levels up
    if (project_root / "pyproject.toml").exists() or (project_root / "requirements.txt").exists():
        break
    project_root = project_root.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, List
from ..agent_base import AgentBase
from symphainy_platform.runtime.execution_context import ExecutionContext


class StatelessAgentBase(AgentBase):
    """
    Base for stateless agents (no session state).
    
    Purpose: Generate deterministic/semantic meaning of client data.
    """
    
    def __init__(
        self,
        agent_id: str,
        capabilities: List[str],
        collaboration_router=None,
        **kwargs
    ):
        """Initialize stateless agent."""
        super().__init__(
            agent_id=agent_id,
            agent_type="stateless",
            capabilities=capabilities,
            collaboration_router=collaboration_router
        )
    
    async def _process_with_assembled_prompt(
        self,
        system_message: str,
        user_message: str,
        runtime_context: Any,  # AgentRuntimeContext
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Process request with assembled prompt (4-layer model).
        
        Returns deterministic/semantic meaning of client data.
        """
        # 1. Extract data from request (from runtime_context or user_message)
        data = runtime_context.business_context.get("data", {}) if hasattr(runtime_context, 'business_context') else {}
        
        # 2. Generate semantic meaning (deterministic)
        semantic_meaning = await self.generate_semantic_meaning(data, context)
        
        # 3. Return structured output (non-executing)
        return {
            "artifact_type": "proposal",
            "artifact": {
                "semantic_meaning": semantic_meaning,
                "deterministic": True
            },
            "confidence": 1.0
        }
    
    async def process_request(
        self,
        request: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Process request (delegates to 4-layer model).
        
        Maintains backward compatibility.
        """
        return await super().process_request(request, context)
    
    async def get_agent_description(self) -> str:
        """Get agent description."""
        return f"Stateless agent ({self.agent_id}) - Generates deterministic/semantic meaning of client data"
    
    async def generate_semantic_meaning(
        self,
        data: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Generate semantic meaning from data (abstract method).
        
        Subclasses should implement this.
        
        Args:
            data: Input data
            context: Execution context
        
        Returns:
            Semantic meaning dictionary
        """
        # Default implementation: Return data structure
        return {
            "data_structure": type(data).__name__,
            "keys": list(data.keys()) if isinstance(data, dict) else [],
            "semantic_type": "unknown"
        }
