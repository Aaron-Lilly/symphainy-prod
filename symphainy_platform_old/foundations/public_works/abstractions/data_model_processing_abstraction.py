"""
Data Model Processing Abstraction - Layer 1

Lightweight coordination layer for data model processing operations (JSON Schema, YAML schemas).
Used for target data model schemas (AAR, PSO, variable_life_policies) in Insights pillar.

WHAT (Infrastructure): I coordinate data model processing operations
HOW (Abstraction): I provide lightweight coordination for JSON/YAML processing
"""

import logging
import json
import yaml
from typing import Dict, Any, Optional
from datetime import datetime

from ..protocols.file_parsing_protocol import FileParsingRequest, FileParsingResult

logger = logging.getLogger(__name__)


class DataModelProcessingAbstraction:
    """
    Data Model Processing Infrastructure Abstraction.
    
    Lightweight coordination layer for data model processing operations.
    Processes JSON Schema, YAML schemas, OpenAPI specs, etc.
    Used for target data model schemas in Insights pillar (AAR, PSO, variable_life_policies).
    """
    
    def __init__(
        self,
        json_adapter: Optional[Any] = None,  # For JSON Schema files
        yaml_adapter: Optional[Any] = None,  # For YAML schema files
        state_surface: Optional[Any] = None
    ):
        """
        Initialize Data Model Processing Abstraction.
        
        Args:
            json_adapter: JSON adapter (Layer 0) - for JSON Schema files
            yaml_adapter: YAML adapter (Layer 0) - for YAML schema files
            state_surface: State Surface instance for file retrieval
        """
        self.json_adapter = json_adapter
        self.yaml_adapter = yaml_adapter
        self.state_surface = state_surface
        self.logger = logger
        
        self.logger.info("✅ Data Model Processing Abstraction initialized")
    
    async def parse_file(self, request: FileParsingRequest) -> FileParsingResult:
        """
        Parse data model file (JSON Schema, YAML schema) using State Surface reference.
        
        Args:
            request: FileParsingRequest with file_reference
        
        Returns:
            FileParsingResult with schema structure and metadata
        """
        try:
            # Get State Surface from request if not provided in __init__
            state_surface = request.state_surface or self.state_surface
            
            if not state_surface:
                return FileParsingResult(
                    success=False,
                    error="State Surface not available for file retrieval",
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Retrieve file from State Surface
            file_data = await state_surface.get_file(request.file_reference)
            
            if not file_data:
                return FileParsingResult(
                    success=False,
                    error=f"File not found: {request.file_reference}",
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Determine file type from filename
            filename = request.filename.lower()
            is_yaml = filename.endswith(('.yaml', '.yml'))
            is_json = filename.endswith('.json')
            
            # Parse based on file type
            schema_data = None
            schema_type = None
            
            if is_yaml:
                # Parse YAML
                if isinstance(file_data, bytes):
                    file_data = file_data.decode('utf-8')
                schema_data = yaml.safe_load(file_data)
                schema_type = "yaml_schema"
            elif is_json:
                # Parse JSON
                if isinstance(file_data, bytes):
                    file_data = file_data.decode('utf-8')
                schema_data = json.loads(file_data)
                schema_type = "json_schema"
            else:
                # Try JSON first, then YAML
                try:
                    if isinstance(file_data, bytes):
                        file_data = file_data.decode('utf-8')
                    schema_data = json.loads(file_data)
                    schema_type = "json_schema"
                except json.JSONDecodeError:
                    try:
                        schema_data = yaml.safe_load(file_data)
                        schema_type = "yaml_schema"
                    except yaml.YAMLError:
                        return FileParsingResult(
                            success=False,
                            error="File is not valid JSON or YAML",
                            timestamp=datetime.utcnow().isoformat()
                        )
            
            if not schema_data:
                return FileParsingResult(
                    success=False,
                    error="Failed to parse schema data",
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Extract target model name if present (AAR, PSO, variable_life_policies)
            target_model_name = None
            if isinstance(schema_data, dict):
                # Check for common patterns
                if "target_model" in schema_data:
                    target_model_name = schema_data.get("target_model")
                elif "title" in schema_data:
                    title = schema_data.get("title", "").lower()
                    if "aar" in title:
                        target_model_name = "aar"
                    elif "pso" in title:
                        target_model_name = "pso"
                    elif "variable_life" in title or "variable_life_policy" in title:
                        target_model_name = "variable_life_policies"
            
            # Build structure metadata for chunking service (schema structure)
            structure = {
                "schema": {
                    "type": schema_data.get("type") if isinstance(schema_data, dict) else None,
                    "properties": schema_data.get("properties", {}) if isinstance(schema_data, dict) else {},
                    "required": schema_data.get("required", []) if isinstance(schema_data, dict) else [],
                    "definitions": schema_data.get("definitions", {}) if isinstance(schema_data, dict) else {}
                }
            }
            
            # Build metadata (include structure, parsing_type, target_model_name)
            metadata = {
                "parsing_type": "data_model",
                "structure": structure,
                "file_type": "json" if is_json else "yaml",
                "schema_type": schema_type,
                "target_model_name": target_model_name
            }
            
            # Build structured_data (standardized format, no nested metadata)
            structured_data = {
                "format": "data_model",
                "schema": schema_data,
                "schema_type": schema_type,
                "target_model_name": target_model_name
            }
            
            # Convert to FileParsingResult (standardized format)
            return FileParsingResult(
                success=True,
                text_content=None,  # Data models have no text content
                structured_data=structured_data,
                metadata=metadata,
                parsing_type="data_model",  # Explicit parsing type
                timestamp=datetime.utcnow().isoformat()
            )
        
        except Exception as e:
            self.logger.error(f"❌ Data model parsing failed: {e}", exc_info=True)
            return FileParsingResult(
                success=False,
                error=f"Data model parsing failed: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )
