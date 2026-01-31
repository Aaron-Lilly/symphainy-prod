"""
Structured Extraction Service - Core Extraction Capabilities

Enabling service for structured data extraction using configurable patterns.

WHAT (Enabling Service Role): I extract structured data from unstructured sources
HOW (Enabling Service Implementation): I use extraction configs and agents to perform extraction

Key Principle: Config-driven extraction - extraction patterns are defined in ExtractionConfig,
executed by StructuredExtractionAgent via governed LLM access.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List, TYPE_CHECKING
from utilities import get_logger
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.realms.insights.models.extraction_config import ExtractionConfig

# Avoid circular import - use TYPE_CHECKING for type hints, lazy import for runtime
if TYPE_CHECKING:
    from symphainy_platform.civic_systems.agentic.agents.structured_extraction_agent import StructuredExtractionAgent


class StructuredExtractionService:
    """
    Structured Extraction Service - Core extraction capabilities.
    
    Provides SOA API methods for:
    - Extracting structured data using pre-configured or custom patterns
    - Discovering extraction patterns from data
    - Creating extraction configs from target data models
    """
    
    def __init__(self, public_works: Optional[Any] = None):
        """
        Initialize Structured Extraction Service.
        
        Args:
            public_works: Public Works Foundation Service (for accessing abstractions)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.public_works = public_works
        
        # Use extraction config registry from Public Works (protocol; no adapter access)
        self.config_registry = public_works.get_extraction_config_registry() if public_works else None
        
        # Lazy initialization of StructuredExtractionAgent (avoid circular import)
        self._extraction_agent = None
        self._public_works = public_works
    
    @property
    def extraction_agent(self):
        """Lazy-load StructuredExtractionAgent to avoid circular import."""
        if self._extraction_agent is None:
            # Import here to avoid circular import
            from symphainy_platform.civic_systems.agentic.agents.structured_extraction_agent import StructuredExtractionAgent
            self._extraction_agent = StructuredExtractionAgent(
                agent_id="structured_extraction_agent",
                capabilities=["structured_extraction", "pattern_discovery"],
                public_works=self._public_works
            )
        return self._extraction_agent
    
    async def extract_structured_data(
        self,
        pattern: str,
        data_source: Dict[str, Any],
        extraction_config_id: Optional[str] = None,
        tenant_id: str = None,
        context: Optional[ExecutionContext] = None
    ) -> Dict[str, Any]:
        """
        Extract structured data using pattern or custom config.
        
        Args:
            pattern: Pattern name ("variable_life_policy_rules", "aar", "pso", "custom")
            data_source: Data source (parsed_file_id, embeddings, etc.)
            extraction_config_id: Optional custom config ID (for "custom" pattern)
            tenant_id: Tenant identifier
            context: Execution context
        
        Returns:
            Dict with extracted structured data:
            {
                "extraction_id": str,
                "pattern": str,
                "extracted_data": Dict[str, Any],
                "categories": List[Dict[str, Any]],
                "confidence_scores": Dict[str, float],
                "metadata": Dict[str, Any]
            }
        """
        self.logger.info(
            f"Extracting structured data: pattern={pattern}, "
            f"config_id={extraction_config_id}, tenant_id={tenant_id}"
        )
        
        try:
            # Get extraction config
            config = None
            if pattern == "custom" and extraction_config_id:
                config = await self.config_registry.get_config(extraction_config_id, tenant_id)
                if not config:
                    raise ValueError(f"Extraction config not found: {extraction_config_id}")
            elif pattern in ["variable_life_policy_rules", "aar", "pso"]:
                # Get pre-configured pattern
                configs = await self.config_registry.list_configs(tenant_id, domain=pattern)
                if not configs:
                    raise ValueError(f"Pre-configured pattern not found: {pattern}")
                config = configs[0]  # Use first matching config
            else:
                raise ValueError(f"Unknown pattern: {pattern}")
            
            if not config:
                raise ValueError("No extraction config available")
            
            # Execute extraction via agent
            extraction_result = await self.extraction_agent.extract_structured_data(
                config=config,
                data_source=data_source,
                context=context or ExecutionContext(
                    tenant_id=tenant_id,
                    session_id=data_source.get("session_id", "default"),
                    execution_id=f"extraction_{pattern}"
                )
            )
            
            return {
                "extraction_id": extraction_result.get("extraction_id", "unknown"),
                "pattern": pattern,
                "extracted_data": extraction_result.get("extracted_data", {}),
                "categories": extraction_result.get("categories", []),
                "confidence_scores": extraction_result.get("confidence_scores", {}),
                "metadata": {
                    "config_id": config.config_id,
                    "config_version": config.version,
                    "categories_extracted": len(extraction_result.get("categories", [])),
                    "extraction_method": "agentic"
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to extract structured data: {e}", exc_info=True)
            return {
                "extraction_id": None,
                "pattern": pattern,
                "extracted_data": {},
                "categories": [],
                "confidence_scores": {},
                "error": str(e),
                "metadata": {}
            }
    
    async def discover_extraction_pattern(
        self,
        data_source: Dict[str, Any],
        tenant_id: str = None,
        context: Optional[ExecutionContext] = None
    ) -> Dict[str, Any]:
        """
        Discover extraction pattern from data (freeform analysis).
        
        Args:
            data_source: Data source (parsed_file_id, embeddings, etc.)
            tenant_id: Tenant identifier
            context: Execution context
        
        Returns:
            Dict with discovered pattern:
            {
                "discovered_config": ExtractionConfig,
                "confidence": float,
                "analysis": Dict[str, Any],
                "suggested_categories": List[str]
            }
        """
        self.logger.info(f"Discovering extraction pattern for tenant_id={tenant_id}")
        
        try:
            # Use agent to discover pattern
            discovery_result = await self.extraction_agent.discover_pattern(
                data_source=data_source,
                context=context or ExecutionContext(
                    tenant_id=tenant_id,
                    session_id=data_source.get("session_id", "default"),
                    execution_id="pattern_discovery"
                )
            )
            
            return {
                "discovered_config": discovery_result.get("config"),
                "confidence": discovery_result.get("confidence", 0.0),
                "analysis": discovery_result.get("analysis", {}),
                "suggested_categories": discovery_result.get("suggested_categories", [])
            }
            
        except Exception as e:
            self.logger.error(f"Failed to discover extraction pattern: {e}", exc_info=True)
            return {
                "discovered_config": None,
                "confidence": 0.0,
                "analysis": {},
                "suggested_categories": [],
                "error": str(e)
            }
    
    async def create_extraction_config_from_target_model(
        self,
        target_model_file_id: str,
        tenant_id: str = None,
        context: Optional[ExecutionContext] = None
    ) -> Dict[str, Any]:
        """
        Generate extraction config from target data model.
        
        Args:
            target_model_file_id: Parsed file ID of target data model
            tenant_id: Tenant identifier
            context: Execution context
        
        Returns:
            Dict with generated config:
            {
                "config": ExtractionConfig,
                "config_id": str,
                "registered": bool
            }
        """
        self.logger.info(
            f"Creating extraction config from target model: "
            f"file_id={target_model_file_id}, tenant_id={tenant_id}"
        )
        
        try:
            # Use agent to analyze target model and generate config
            config_result = await self.extraction_agent.generate_config_from_target_model(
                target_model_file_id=target_model_file_id,
                tenant_id=tenant_id,
                context=context or ExecutionContext(
                    tenant_id=tenant_id,
                    session_id="config_generation",
                    execution_id="target_model_to_config"
                )
            )
            
            config = config_result.get("config")
            if not config:
                raise ValueError("Failed to generate extraction config from target model")
            
            # Register config
            registered = await self.config_registry.register_config(config, tenant_id)
            
            return {
                "config": config,
                "config_id": config.config_id,
                "registered": registered
            }
            
        except Exception as e:
            self.logger.error(
                f"Failed to create extraction config from target model: {e}",
                exc_info=True
            )
            return {
                "config": None,
                "config_id": None,
                "registered": False,
                "error": str(e)
            }
