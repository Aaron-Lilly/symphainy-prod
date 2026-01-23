"""
Data Analyzer Service - Pure Data Processing for Data Analysis

Enabling service for data analysis operations.

WHAT (Enabling Service Role): I execute data analysis
HOW (Enabling Service Implementation): I use Public Works abstractions for analysis

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

# Note: Import path for FileParserService (cross-realm access)
# ARCHITECTURAL PRINCIPLE: Realms can access other realm services via Public Works


class DataAnalyzerService:
    """
    Data Analyzer Service - Pure data processing for data analysis.
    
    Uses Public Works abstractions to analyze data.
    Returns raw data only - no business logic.
    """
    
    def __init__(self, public_works: Optional[Any] = None):
        """
        Initialize Data Analyzer Service.
        
        Args:
            public_works: Public Works Foundation Service (for accessing abstractions)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.public_works = public_works
        
        # Get abstractions from Public Works
        self.semantic_data_abstraction = None
        if public_works:
            self.semantic_data_abstraction = public_works.get_semantic_data_abstraction()
    
    async def analyze_content(
        self,
        parsed_file_id: str,
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Analyze content for insights.
        
        ARCHITECTURAL PRINCIPLE: Uses Public Works abstractions for data access.
        
        Args:
            parsed_file_id: Parsed file identifier
            tenant_id: Tenant identifier
            context: Execution context
        
        Returns:
            Dict with analysis results
        """
        self.logger.info(f"Analyzing content: {parsed_file_id} for tenant: {tenant_id}")
        
        try:
            # Get parsed file content
            from ..content.enabling_services.file_parser_service import FileParserService
            file_parser_service = FileParserService(public_works=self.public_works)
            parsed_content = await file_parser_service.get_parsed_file(
                parsed_file_id=parsed_file_id,
                tenant_id=tenant_id,
                context=context
            )
            
            if not parsed_content:
                return {
                    "parsed_file_id": parsed_file_id,
                    "analysis_status": "error",
                    "insights": {},
                    "patterns": [],
                    "error": "Parsed file not found"
                }
            
            # Basic content analysis
            data = parsed_content.get("data", [])
            metadata = parsed_content.get("metadata", {})
            
            insights = {
                "total_records": len(data) if isinstance(data, list) else 0,
                "file_type": metadata.get("file_type", "unknown"),
                "columns": metadata.get("columns", []),
                "structure": "structured" if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict) else "unstructured"
            }
            
            # Identify basic patterns
            patterns = []
            if isinstance(data, list) and len(data) > 0:
                first_row = data[0]
                if isinstance(first_row, dict):
                    # Pattern: Key-value structure
                    patterns.append({
                        "type": "key_value_structure",
                        "description": "Data organized as key-value pairs",
                        "confidence": 1.0
                    })
                    
                    # Pattern: Column count
                    column_count = len(first_row.keys())
                    patterns.append({
                        "type": "column_count",
                        "description": f"Data contains {column_count} columns",
                        "confidence": 1.0,
                        "value": column_count
                    })
            
            return {
                "parsed_file_id": parsed_file_id,
                "analysis_status": "completed",
                "insights": insights,
                "patterns": patterns
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze content: {e}", exc_info=True)
            return {
                "parsed_file_id": parsed_file_id,
                "analysis_status": "error",
                "insights": {},
                "patterns": [],
                "error": str(e)
            }
    
    async def interpret_data(
        self,
        parsed_file_id: str,
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Interpret structured/unstructured data.
        
        ARCHITECTURAL PRINCIPLE: Uses SemanticDataAbstraction for semantic interpretation.
        
        Args:
            parsed_file_id: Parsed file identifier
            tenant_id: Tenant identifier
            context: Execution context
        
        Returns:
            Dict with interpretation results
        """
        self.logger.info(f"Interpreting data: {parsed_file_id} for tenant: {tenant_id}")
        
        try:
            # Get semantic embeddings if available
            semantic_mapping = {}
            if self.semantic_data_abstraction:
                try:
                    embeddings = await self.semantic_data_abstraction.get_semantic_embeddings(
                        filter_conditions={"parsed_file_id": parsed_file_id},
                        limit=None,
                        tenant_id=tenant_id
                    )
                    
                    # Build semantic mapping from embeddings
                    for emb in embeddings or []:
                        col_name = emb.get("column_name")
                        if col_name:
                            semantic_mapping[col_name] = {
                                "semantic_meaning": emb.get("semantic_meaning", ""),
                                "column_type": emb.get("column_type", ""),
                                "sample_values": emb.get("sample_values", [])
                            }
                except Exception as e:
                    self.logger.debug(f"Could not get semantic embeddings: {e}")
            
            # Basic interpretation
            from symphainy_platform.realms.content.enabling_services.file_parser_service import FileParserService
            file_parser_service = FileParserService(public_works=self.public_works)
            parsed_content = await file_parser_service.get_parsed_file(
                parsed_file_id=parsed_file_id,
                tenant_id=tenant_id,
                context=context
            )
            
            interpretation = {
                "data_type": "structured" if parsed_content and isinstance(parsed_content.get("data"), list) else "unstructured",
                "columns_interpreted": len(semantic_mapping),
                "semantic_mapping_available": len(semantic_mapping) > 0
            }
            
            return {
                "parsed_file_id": parsed_file_id,
                "interpretation": interpretation,
                "semantic_mapping": semantic_mapping
            }
            
        except Exception as e:
            self.logger.error(f"Failed to interpret data: {e}", exc_info=True)
            return {
                "parsed_file_id": parsed_file_id,
                "interpretation": {},
                "semantic_mapping": {},
                "error": str(e)
            }
    
    async def map_relationships(
        self,
        parsed_file_id: str,
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Map semantic relationships.
        
        ARCHITECTURAL PRINCIPLE: Uses SemanticDataAbstraction for relationship discovery.
        
        Args:
            parsed_file_id: Parsed file identifier
            tenant_id: Tenant identifier
            context: Execution context
        
        Returns:
            Dict with relationship mapping results
        """
        self.logger.info(f"Mapping relationships: {parsed_file_id} for tenant: {tenant_id}")
        
        try:
            # Get parsed file to understand structure
            from symphainy_platform.realms.content.enabling_services.file_parser_service import FileParserService
            file_parser_service = FileParserService(public_works=self.public_works)
            parsed_content = await file_parser_service.get_parsed_file(
                parsed_file_id=parsed_file_id,
                tenant_id=tenant_id,
                context=context
            )
            
            relationships = []
            nodes = []
            edges = []
            
            if parsed_content:
                metadata = parsed_content.get("metadata", {})
                columns = metadata.get("columns", [])
                
                # Create nodes for each column
                for col in columns:
                    col_name = col.get("name", "")
                    nodes.append({
                        "id": col_name,
                        "label": col_name,
                        "type": "column",
                        "data_type": col.get("type", "unknown")
                    })
                
                # Identify basic relationships (foreign key patterns)
                data = parsed_content.get("data", [])
                if isinstance(data, list) and len(data) > 0:
                    first_row = data[0] if isinstance(data[0], dict) else {}
                    
                    # Look for ID/reference patterns
                    id_columns = [col for col in columns if "id" in col.get("name", "").lower() or "key" in col.get("name", "").lower()]
                    reference_columns = [col for col in columns if any(ref in col.get("name", "").lower() for ref in ["ref", "foreign", "link"])]
                    
                    # Create relationships
                    for ref_col in reference_columns:
                        ref_name = ref_col.get("name", "")
                        # Try to find matching ID column
                        for id_col in id_columns:
                            id_name = id_col.get("name", "")
                            # Simple heuristic: if reference column name contains part of ID column name
                            if any(part in ref_name.lower() for part in id_name.lower().split("_") if len(part) > 2):
                                relationships.append({
                                    "from": ref_name,
                                    "to": id_name,
                                    "type": "references",
                                    "confidence": 0.7
                                })
                                edges.append({
                                    "source": ref_name,
                                    "target": id_name,
                                    "type": "references"
                                })
            
            return {
                "parsed_file_id": parsed_file_id,
                "relationships": relationships,
                "graph": {
                    "nodes": nodes,
                    "edges": edges
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to map relationships: {e}", exc_info=True)
            return {
                "parsed_file_id": parsed_file_id,
                "relationships": [],
                "graph": {"nodes": [], "edges": []},
                "error": str(e)
            }
    
    async def query_data(
        self,
        query: str,
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Query semantic data.
        
        Args:
            query: Query string
            tenant_id: Tenant identifier
            context: Execution context
        
        Returns:
            Dict with query results
        """
        self.logger.info(f"Querying data: {query} for tenant: {tenant_id}")
        
        # For MVP: Return placeholder
        # In full implementation: Use SemanticDataAbstraction for querying
        
        return {
            "query": query,
            "results": [],
            "count": 0
        }
