"""
EDA Analysis Agent Base - Pandas-based EDA and Business Insights
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

from typing import Dict, Any, List, Optional
from ..agent_base import AgentBase
from ..models.agent_runtime_context import AgentRuntimeContext
from symphainy_platform.runtime.execution_context import ExecutionContext


class EDAAnalysisAgentBase(AgentBase):
    """
    Base for EDA analysis agents (pandas-based).
    
    Purpose: Pandas-based EDA, business insights.
    """
    
    def __init__(
        self,
        agent_id: str,
        capabilities: List[str],
        collaboration_router=None,
        **kwargs
    ):
        """Initialize EDA analysis agent."""
        super().__init__(
            agent_id=agent_id,
            agent_type="eda_analysis",
            capabilities=capabilities,
            collaboration_router=collaboration_router,
            **kwargs
        )
    
    async def _process_with_assembled_prompt(
        self,
        system_message: str,
        user_message: str,
        runtime_context: AgentRuntimeContext,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Process request with assembled prompt (4-layer model).
        
        This method is called by AgentBase.process_request() after assembling
        the system and user messages from the 4-layer model.
        
        Args:
            system_message: Assembled system message (from layers 1-3)
            user_message: Assembled user message
            runtime_context: Runtime context with business_context
            context: Execution context
        
        Returns:
            Dict with EDA analysis results
        """
        # Extract request from user_message or runtime_context
        request_data = {}
        try:
            import json
            if user_message.strip().startswith("{"):
                request_data = json.loads(user_message)
            else:
                # Try to extract from runtime_context.business_context
                if hasattr(runtime_context, 'business_context') and runtime_context.business_context:
                    request_data = runtime_context.business_context.get("request", {})
                # If still empty, use user_message as data description
                if not request_data:
                    request_data = {"data_description": user_message.strip()}
        except (json.JSONDecodeError, ValueError):
            request_data = {"data_description": user_message.strip()}
        
        # Use business context from runtime_context if available
        if runtime_context.business_context:
            request_data.setdefault("business_context", runtime_context.business_context)
        
        # Execute EDA analysis logic directly (avoid circular call)
        # Get data
        data = await context.get_state("data") if hasattr(context, 'get_state') else request_data.get("data", {})
        
        # Load into pandas DataFrame
        try:
            import pandas as pd
            df = pd.DataFrame(data) if isinstance(data, (list, dict)) else pd.DataFrame([data])
        except ImportError:
            self.logger.warning("Pandas not available, using basic analysis")
            df = None
        
        # Perform EDA
        eda_results = await self.perform_eda(df, context) if df is not None else {}
        
        # Generate insights
        insights = await self.generate_insights(eda_results, context)
        
        # Return structured output
        return {
            "artifact_type": "proposal",
            "artifact": {
                "eda_results": eda_results,
                "business_insights": insights
            },
            "confidence": 0.85
        }
    
    async def process_request(
        self,
        request: Dict[str, Any],
        context: ExecutionContext,
        runtime_context: Optional[AgentRuntimeContext] = None
    ) -> Dict[str, Any]:
        """
        Perform EDA analysis and generate business insights.
        
        ARCHITECTURAL PRINCIPLE: This method can be called directly, but for
        4-layer model support, it should be called via AgentBase.process_request().
        """
        # 1. Get data (via Runtime State Surface)
        data = await context.get_state("data") if hasattr(context, 'get_state') else request.get("data", {})
        
        # 2. Load into pandas DataFrame (if data is available)
        try:
            import pandas as pd
            df = pd.DataFrame(data) if isinstance(data, (list, dict)) else pd.DataFrame([data])
        except ImportError:
            self.logger.warning("Pandas not available, using basic analysis")
            df = None
        
        # 3. Perform EDA
        eda_results = await self.perform_eda(df, context) if df is not None else {}
        
        # 4. Generate business insights
        insights = await self.generate_insights(eda_results, context)
        
        # 5. Return structured output (non-executing)
        return {
            "artifact_type": "proposal",
            "artifact": {
                "eda_results": eda_results,
                "business_insights": insights
            },
            "confidence": 0.85
        }
    
    async def get_agent_description(self) -> str:
        """Get agent description."""
        return f"EDA Analysis agent ({self.agent_id}) - Pandas-based EDA and business insights"
    
    async def perform_eda(
        self,
        df: Any,  # pandas.DataFrame
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Perform EDA analysis (abstract method).
        
        Subclasses should implement this.
        
        Args:
            df: Pandas DataFrame
            context: Execution context
        
        Returns:
            EDA results dictionary
        """
        # Default implementation: Basic statistics
        if df is None:
            return {}
        
        try:
            return {
                "shape": df.shape if hasattr(df, 'shape') else None,
                "columns": list(df.columns) if hasattr(df, 'columns') else [],
                "dtypes": str(df.dtypes) if hasattr(df, 'dtypes') else None
            }
        except Exception as e:
            self.logger.warning(f"EDA analysis failed: {e}")
            return {}
    
    async def generate_insights(
        self,
        eda_results: Dict[str, Any],
        context: ExecutionContext
    ) -> List[str]:
        """
        Generate business insights from EDA results (abstract method).
        
        Subclasses should implement this.
        
        Args:
            eda_results: EDA results dictionary
            context: Execution context
        
        Returns:
            List of insight strings
        """
        # Default implementation: Empty insights
        return []
