"""
Insights EDA Agent - EDA Analysis Agent for Insights Realm

Pandas-based EDA analysis agent that provides business insights.
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

from .eda_analysis_agent import EDAAnalysisAgentBase
from symphainy_platform.runtime.execution_context import ExecutionContext


class InsightsEDAAgent(EDAAnalysisAgentBase):
    """
    Insights EDA Agent - EDA analysis agent for Insights realm.
    
    Performs exploratory data analysis and generates business insights.
    """
    
    def __init__(
        self,
        agent_id: str,
        capabilities: List[str],
        collaboration_router=None
    ):
        super().__init__(
            agent_id=agent_id,
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
        # Get data from request or context
        data = request.get("data", {})
        
        # Perform EDA
        eda_results = await self.perform_eda(data, context)
        
        # Generate business insights
        insights = await self.generate_insights(eda_results, context)
        
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
        return f"Insights EDA Agent ({self.agent_id}) - Pandas-based EDA and business insights"
    
    async def perform_eda(
        self,
        df: Any,  # pandas.DataFrame
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Perform EDA analysis.
        """
        try:
            import pandas as pd
            
            if df is None or not isinstance(df, pd.DataFrame):
                return {"error": "No data provided or invalid DataFrame"}
            
            # Basic EDA statistics
            eda_results = {
                "shape": df.shape,
                "columns": list(df.columns),
                "dtypes": df.dtypes.to_dict(),
                "null_counts": df.isnull().sum().to_dict(),
                "numeric_summary": df.describe().to_dict() if len(df.select_dtypes(include=['number']).columns) > 0 else {}
            }
            
            return eda_results
            
        except ImportError:
            self.logger.warning("Pandas not available, using basic analysis")
            return {
                "shape": None,
                "columns": list(df.keys()) if isinstance(df, dict) else [],
                "dtypes": None
            }
        except Exception as e:
            self.logger.error(f"EDA analysis failed: {e}", exc_info=True)
            return {"error": str(e)}
    
    async def generate_insights(
        self,
        eda_results: Dict[str, Any],
        context: ExecutionContext
    ) -> List[str]:
        """
        Generate business insights from EDA results.
        """
        insights = []
        
        # Check for null values
        null_counts = eda_results.get("null_counts", {})
        if null_counts:
            null_columns = [col for col, count in null_counts.items() if count > 0]
            if null_columns:
                insights.append(f"Found missing values in {len(null_columns)} columns: {', '.join(null_columns)}")
        
        # Check data shape
        shape = eda_results.get("shape")
        if shape:
            rows, cols = shape
            insights.append(f"Dataset contains {rows} rows and {cols} columns")
        
        # Check numeric columns
        numeric_summary = eda_results.get("numeric_summary", {})
        if numeric_summary:
            insights.append(f"Found {len(numeric_summary)} numeric columns for analysis")
        
        return insights if insights else ["No specific insights generated from the data"]
