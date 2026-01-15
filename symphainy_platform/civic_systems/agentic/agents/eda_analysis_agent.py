"""
EDA Analysis Agent Base - Pandas-based EDA and Business Insights
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[6]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, List
from ..agent_base import AgentBase
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
            collaboration_router=collaboration_router
        )
    
    async def process_request(
        self,
        request: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Perform EDA analysis and generate business insights.
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
