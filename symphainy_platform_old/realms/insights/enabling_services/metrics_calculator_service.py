"""
Metrics Calculator Service - Pure Data Processing for Metrics Calculation

Enabling service for metrics calculation operations.

WHAT (Enabling Service Role): I execute metrics calculation
HOW (Enabling Service Implementation): I use Public Works abstractions for metrics

Key Principle: Pure data processing - no LLM, no business logic, no orchestration.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional

from utilities import get_logger
from symphainy_platform.runtime.execution_context import ExecutionContext


class MetricsCalculatorService:
    """
    Metrics Calculator Service - Pure data processing for metrics calculation.
    
    Uses Public Works abstractions to calculate metrics.
    Returns raw data only - no business logic.
    """
    
    def __init__(self, public_works: Optional[Any] = None):
        """
        Initialize Metrics Calculator Service.
        
        Args:
            public_works: Public Works Foundation Service (for accessing abstractions)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.public_works = public_works
    
    async def calculate_metrics(
        self,
        parsed_file_id: str,
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Calculate data quality metrics.
        
        ARCHITECTURAL PRINCIPLE: Uses Public Works abstractions for data access.
        
        Args:
            parsed_file_id: Parsed file identifier
            tenant_id: Tenant identifier
            context: Execution context
        
        Returns:
            Dict with metrics results
        """
        self.logger.info(f"Calculating metrics: {parsed_file_id} for tenant: {tenant_id}")
        
        try:
            # Get parsed file content via Content Realm service
            from symphainy_platform.realms.content.enabling_services.file_parser_service import FileParserService
            file_parser_service = FileParserService(public_works=self.public_works)
            parsed_content = await file_parser_service.get_parsed_file(
                parsed_file_id=parsed_file_id,
                tenant_id=tenant_id,
                context=context
            )
            
            if not parsed_content:
                return {
                    "parsed_file_id": parsed_file_id,
                    "metrics": {
                        "data_quality": {},
                        "completeness": {},
                        "accuracy": {}
                    },
                    "error": "Parsed file not found"
                }
            
            # Calculate basic metrics
            data = parsed_content.get("data", [])
            metadata = parsed_content.get("metadata", {})
            columns = metadata.get("columns", [])
            
            # Data quality metrics
            total_rows = len(data) if isinstance(data, list) else 0
            total_columns = len(columns)
            
            # Completeness metrics
            completeness_scores = {}
            for col in columns:
                col_name = col.get("name", "")
                null_count = sum(1 for row in data if isinstance(row, dict) and (row.get(col_name) is None or row.get(col_name) == ""))
                completeness = 1.0 - (null_count / total_rows) if total_rows > 0 else 0.0
                completeness_scores[col_name] = {
                    "completeness": completeness,
                    "null_count": null_count,
                    "total_count": total_rows
                }
            
            # Accuracy metrics (basic - would be enhanced with validation rules)
            accuracy_scores = {}
            for col in columns:
                col_name = col.get("name", "")
                col_type = col.get("type", "unknown")
                # Basic type accuracy check
                type_matches = 0
                type_total = 0
                for row in data:
                    if isinstance(row, dict) and col_name in row:
                        value = row[col_name]
                        if value is not None:
                            type_total += 1
                            # Basic type checking
                            if col_type == "integer" and isinstance(value, int):
                                type_matches += 1
                            elif col_type == "float" and isinstance(value, (int, float)):
                                type_matches += 1
                            elif col_type == "string" and isinstance(value, str):
                                type_matches += 1
                            elif col_type == "boolean" and isinstance(value, bool):
                                type_matches += 1
                
                accuracy = type_matches / type_total if type_total > 0 else 0.0
                accuracy_scores[col_name] = {
                    "accuracy": accuracy,
                    "type_matches": type_matches,
                    "type_total": type_total
                }
            
            # Overall data quality score
            overall_completeness = sum(s["completeness"] for s in completeness_scores.values()) / len(completeness_scores) if completeness_scores else 0.0
            overall_accuracy = sum(s["accuracy"] for s in accuracy_scores.values()) / len(accuracy_scores) if accuracy_scores else 0.0
            overall_quality = (overall_completeness + overall_accuracy) / 2.0
            
            return {
                "parsed_file_id": parsed_file_id,
                "metrics": {
                    "data_quality": {
                        "overall_quality": overall_quality,
                        "total_rows": total_rows,
                        "total_columns": total_columns
                    },
                    "completeness": {
                        "overall_completeness": overall_completeness,
                        "column_scores": completeness_scores
                    },
                    "accuracy": {
                        "overall_accuracy": overall_accuracy,
                        "column_scores": accuracy_scores
                    }
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to calculate metrics: {e}", exc_info=True)
            return {
                "parsed_file_id": parsed_file_id,
                "metrics": {
                    "data_quality": {},
                    "completeness": {},
                    "accuracy": {}
                },
                "error": str(e)
            }
