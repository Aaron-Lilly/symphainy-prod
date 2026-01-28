"""
Extract Structured Data Intent Service

Implements the extract_structured_data intent for the Insights Realm.

Contract: docs/intent_contracts/journey_insights_data_analysis/intent_extract_structured_data.md

Purpose: Extract structured data from unstructured sources using configurable patterns.
Supports pre-configured patterns (variable_life_policy_rules, aar, pso) and custom configs.

WHAT (Intent Service Role): I extract structured data from unstructured sources
HOW (Intent Service Implementation): I use StructuredExtractionService library
    to perform pattern-based extraction via agentic reasoning

Naming Convention:
- Realm: Insights Realm
- Artifacts: insights_structured_extraction
- Solution = platform construct (InsightsSolution)
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.foundations.libraries.extraction.structured_extraction_service import StructuredExtractionService
from utilities import generate_event_id


class ExtractStructuredDataService(BaseIntentService):
    """
    Intent service for structured data extraction.
    
    Extracts structured data from unstructured sources using:
    - Pre-configured patterns (variable_life_policy_rules, aar, pso)
    - Custom extraction configurations
    - Pattern discovery from data
    
    Uses StructuredExtractionService library for core extraction capabilities.
    """
    
    def __init__(self, public_works, state_surface):
        """Initialize ExtractStructuredDataService."""
        super().__init__(
            service_id="extract_structured_data_service",
            intent_type="extract_structured_data",
            public_works=public_works,
            state_surface=state_surface
        )
        
        # Initialize the extraction library
        self._extraction_service = StructuredExtractionService(public_works=public_works)
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the extract_structured_data intent."""
        await self.record_telemetry(
            telemetry_data={"action": "execute", "status": "started", "intent_type": self.intent_type},
            tenant_id=context.tenant_id
        )
        
        try:
            intent_params = context.intent.parameters or {} if context.intent else {}
            if params:
                intent_params = {**intent_params, **params}
            
            # Validate required parameters
            parsed_file_id = intent_params.get("parsed_file_id")
            if not parsed_file_id:
                raise ValueError("parsed_file_id is required for structured extraction")
            
            pattern = intent_params.get("pattern", "custom")
            extraction_config_id = intent_params.get("extraction_config_id")
            
            # Build data source from parsed file
            data_source = await self._build_data_source(parsed_file_id, intent_params, context)
            
            # Perform extraction using the library
            extraction_result = await self._extraction_service.extract_structured_data(
                pattern=pattern,
                data_source=data_source,
                extraction_config_id=extraction_config_id,
                tenant_id=context.tenant_id,
                context=context
            )
            
            # Check for extraction error
            if extraction_result.get("error"):
                self.logger.warning(f"Extraction warning: {extraction_result.get('error')}")
            
            extraction_id = extraction_result.get("extraction_id") or f"extraction_{generate_event_id()}"
            
            # Build result artifact
            extraction_artifact = {
                "extraction_id": extraction_id,
                "parsed_file_id": parsed_file_id,
                "pattern": pattern,
                "extracted_data": extraction_result.get("extracted_data", {}),
                "categories": extraction_result.get("categories", []),
                "confidence_scores": extraction_result.get("confidence_scores", {}),
                "metadata": extraction_result.get("metadata", {}),
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Store in Artifact Plane
            artifact_id = await self._store_extraction(extraction_artifact, context)
            
            self.logger.info(f"Structured extraction completed: {extraction_id}")
            
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute", "status": "completed", "intent_type": self.intent_type,
                    "extraction_id": extraction_id,
                    "pattern": pattern,
                    "categories_count": len(extraction_artifact.get("categories", []))
                },
                tenant_id=context.tenant_id
            )
            
            return {
                "artifacts": {
                    "extraction": extraction_artifact,
                    "artifact_id": artifact_id
                },
                "events": [
                    {
                        "type": "structured_data_extracted",
                        "extraction_id": extraction_id,
                        "pattern": pattern,
                        "categories_count": len(extraction_artifact.get("categories", []))
                    }
                ]
            }
            
        except Exception as e:
            await self.record_telemetry(
                telemetry_data={"action": "execute", "status": "failed", "error": str(e)},
                tenant_id=context.tenant_id
            )
            raise
    
    async def discover_pattern(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Discover extraction pattern from data.
        
        Sub-intent for freeform pattern discovery from unstructured sources.
        """
        await self.record_telemetry(
            telemetry_data={"action": "discover_pattern", "status": "started"},
            tenant_id=context.tenant_id
        )
        
        try:
            intent_params = context.intent.parameters or {} if context.intent else {}
            if params:
                intent_params = {**intent_params, **params}
            
            parsed_file_id = intent_params.get("parsed_file_id")
            if not parsed_file_id:
                raise ValueError("parsed_file_id is required for pattern discovery")
            
            data_source = await self._build_data_source(parsed_file_id, intent_params, context)
            
            # Use library for pattern discovery
            discovery_result = await self._extraction_service.discover_extraction_pattern(
                data_source=data_source,
                tenant_id=context.tenant_id,
                context=context
            )
            
            discovery_id = f"discovery_{generate_event_id()}"
            
            await self.record_telemetry(
                telemetry_data={
                    "action": "discover_pattern", "status": "completed",
                    "discovery_id": discovery_id,
                    "confidence": discovery_result.get("confidence", 0)
                },
                tenant_id=context.tenant_id
            )
            
            return {
                "artifacts": {
                    "discovery_id": discovery_id,
                    "discovered_config": discovery_result.get("discovered_config"),
                    "confidence": discovery_result.get("confidence", 0),
                    "analysis": discovery_result.get("analysis", {}),
                    "suggested_categories": discovery_result.get("suggested_categories", [])
                },
                "events": [
                    {
                        "type": "extraction_pattern_discovered",
                        "discovery_id": discovery_id,
                        "confidence": discovery_result.get("confidence", 0)
                    }
                ]
            }
            
        except Exception as e:
            await self.record_telemetry(
                telemetry_data={"action": "discover_pattern", "status": "failed", "error": str(e)},
                tenant_id=context.tenant_id
            )
            raise
    
    async def create_config_from_target(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create extraction config from target data model.
        
        Sub-intent for generating extraction configs from target schemas.
        """
        await self.record_telemetry(
            telemetry_data={"action": "create_config_from_target", "status": "started"},
            tenant_id=context.tenant_id
        )
        
        try:
            intent_params = context.intent.parameters or {} if context.intent else {}
            if params:
                intent_params = {**intent_params, **params}
            
            target_model_file_id = intent_params.get("target_model_file_id")
            if not target_model_file_id:
                raise ValueError("target_model_file_id is required for config creation")
            
            # Use library to create config from target model
            config_result = await self._extraction_service.create_extraction_config_from_target_model(
                target_model_file_id=target_model_file_id,
                tenant_id=context.tenant_id,
                context=context
            )
            
            await self.record_telemetry(
                telemetry_data={
                    "action": "create_config_from_target", "status": "completed",
                    "config_id": config_result.get("config_id"),
                    "registered": config_result.get("registered", False)
                },
                tenant_id=context.tenant_id
            )
            
            return {
                "artifacts": {
                    "config": config_result.get("config"),
                    "config_id": config_result.get("config_id"),
                    "registered": config_result.get("registered", False)
                },
                "events": [
                    {
                        "type": "extraction_config_created",
                        "config_id": config_result.get("config_id"),
                        "registered": config_result.get("registered", False)
                    }
                ]
            }
            
        except Exception as e:
            await self.record_telemetry(
                telemetry_data={"action": "create_config_from_target", "status": "failed", "error": str(e)},
                tenant_id=context.tenant_id
            )
            raise
    
    async def _build_data_source(
        self,
        parsed_file_id: str,
        params: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Build data source dictionary for extraction."""
        data_source = {
            "parsed_file_id": parsed_file_id,
            "session_id": params.get("session_id") or context.session_id
        }
        
        # Add embeddings if available
        if params.get("embeddings_id"):
            data_source["embeddings_id"] = params["embeddings_id"]
        
        # Try to get parsed data from state surface
        if context.state_surface:
            try:
                parsed_data = await context.state_surface.get_execution_state(
                    key=f"parsed_file_{parsed_file_id}",
                    tenant_id=context.tenant_id
                )
                if parsed_data:
                    data_source["parsed_data"] = parsed_data
            except Exception:
                pass
        
        return data_source
    
    async def _store_extraction(
        self,
        extraction: Dict[str, Any],
        context: ExecutionContext
    ) -> Optional[str]:
        """Store extraction result in Artifact Plane."""
        if self.public_works:
            try:
                artifact_plane = self.public_works.get_artifact_plane()
                if artifact_plane:
                    result = await artifact_plane.create_artifact(
                        artifact_type="structured_extraction",
                        content=extraction,
                        metadata={
                            "extraction_id": extraction.get("extraction_id"),
                            "pattern": extraction.get("pattern")
                        },
                        tenant_id=context.tenant_id,
                        include_payload=True
                    )
                    return result.get("artifact_id")
            except Exception as e:
                self.logger.warning(f"Could not store extraction: {e}")
        return None
