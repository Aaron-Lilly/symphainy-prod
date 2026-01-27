"""
Structured Extraction Agent - Agentic Extraction Reasoning

Base agent for structured data extraction using extraction configs.
Uses governed LLM access via _call_llm() for extraction operations.

WHAT (Agent Role): I perform structured data extraction using configurable patterns
HOW (Agent Implementation): I use extraction configs and governed LLM access to extract structured data

Key Principle: Agents use MCP tools (not direct service calls) - but for MVP, we'll use direct service
access with governance via _call_llm() until MCP infrastructure is complete.
"""

import sys
from pathlib import Path

# Add project root to path
current = Path(__file__).resolve()
project_root = current
for _ in range(10):  # Max 10 levels up
    if (project_root / "pyproject.toml").exists() or (project_root / "requirements.txt").exists():
        break
    project_root = project_root.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List
import uuid
import json

from ..agent_base import AgentBase
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.realms.insights.models.extraction_config import (
    ExtractionConfig,
    ExtractionCategory
)


class StructuredExtractionAgent(AgentBase):
    """
    Structured Extraction Agent - Agentic extraction reasoning.
    
    Performs structured data extraction using extraction configs.
    Uses governed LLM access for extraction operations.
    """
    
    def __init__(
        self,
        agent_id: str = "structured_extraction_agent",
        capabilities: List[str] = None,
        collaboration_router=None,
        public_works: Optional[Any] = None,
        agent_definition_id: Optional[str] = None,
        agent_posture_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        solution_id: Optional[str] = None,
        mcp_client_manager: Optional[Any] = None,
        telemetry_service: Optional[Any] = None,
        **kwargs
    ):
        """
        Initialize Structured Extraction Agent (4-layer model).
        
        Args:
            agent_id: Agent identifier
            capabilities: List of capabilities (default: ["structured_extraction"])
            collaboration_router: Optional collaboration router
            public_works: Public Works Foundation Service (REQUIRED for LLM access)
            agent_definition_id: Optional agent definition ID (loads from registry)
            agent_posture_id: Optional agent posture ID (loads from registry)
            tenant_id: Optional tenant ID (for posture lookup)
            solution_id: Optional solution ID (for posture lookup)
            mcp_client_manager: Optional MCP client manager
            telemetry_service: Optional telemetry service
        """
        if capabilities is None:
            capabilities = ["structured_extraction", "pattern_discovery"]
        
        super().__init__(
            agent_id=agent_id,
            agent_type="structured_extraction",
            capabilities=capabilities,
            collaboration_router=collaboration_router,
            public_works=public_works,
            agent_definition_id=agent_definition_id or agent_id,
            agent_posture_id=agent_posture_id,
            tenant_id=tenant_id,
            solution_id=solution_id,
            mcp_client_manager=mcp_client_manager,
            telemetry_service=telemetry_service
        )
        
        if not public_works:
            self.logger.warning("Public Works not provided - LLM access will fail")
    
    async def _process_with_assembled_prompt(
        self,
        system_message: str,
        user_message: str,
        runtime_context: Any,  # AgentRuntimeContext
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Process request with assembled prompt (4-layer model).
        
        Args:
            system_message: Assembled system message (from layers 1-3)
            user_message: Assembled user message
            runtime_context: Runtime context
            context: Execution context
        
        Returns:
            Dict with extraction result
        """
        # Extract extraction parameters from runtime context or user message
        extraction_type = runtime_context.business_context.get("extraction_type", "structured_data") if hasattr(runtime_context, 'business_context') else "structured_data"
        config = runtime_context.business_context.get("config") if hasattr(runtime_context, 'business_context') else None
        data_source = runtime_context.business_context.get("data_source", {}) if hasattr(runtime_context, 'business_context') else {}
        
        # Fallback to user_message parsing if needed
        if not config and not data_source:
            # Try to extract from user_message
            if "extract" in user_message.lower() or "pattern" in user_message.lower():
                extraction_type = "structured_data"
        
        if extraction_type == "structured_data":
            return await self.extract_structured_data(
                config=config,
                data_source=data_source,
                context=context
            )
        elif extraction_type == "pattern_discovery":
            return await self.discover_pattern(
                data_source=data_source,
                context=context
            )
        elif extraction_type == "config_generation":
            target_model_file_id = runtime_context.business_context.get("target_model_file_id") if hasattr(runtime_context, 'business_context') else None
            return await self.generate_config_from_target_model(
                target_model_file_id=target_model_file_id,
                tenant_id=context.tenant_id,
                context=context
            )
        else:
            return {
                "error": f"Unknown extraction type: {extraction_type}",
                "extraction_type": extraction_type
            }
    
    async def process_request(
        self,
        request: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Process extraction request (backward compatibility).
        
        Args:
            request: Request dictionary
            context: Execution context
        
        Returns:
            Dict with extraction result
        """
        # Delegate to 4-layer model via super()
        return await super().process_request(request, context)
    
    async def get_agent_description(self) -> str:
        """Get agent description."""
        return f"Structured Extraction Agent ({self.agent_id}) - Config-driven structured data extraction"
    
    async def extract_structured_data(
        self,
        config: ExtractionConfig,
        data_source: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Extract structured data using extraction config.
        
        Args:
            config: ExtractionConfig instance
            data_source: Data source (parsed_file_id, embeddings, etc.)
            context: Execution context
        
        Returns:
            Dict with extraction result:
            {
                "extraction_id": str,
                "extracted_data": Dict[str, Any],
                "categories": List[Dict[str, Any]],
                "confidence_scores": Dict[str, float]
            }
        """
        extraction_id = str(uuid.uuid4())
        self.logger.info(
            f"Extracting structured data: config_id={config.config_id}, "
            f"categories={len(config.categories)}, extraction_id={extraction_id}"
        )
        
        extracted_data = {}
        categories = []
        confidence_scores = {}
        
        # Determine extraction order
        extraction_order = config.extraction_order if config.extraction_order else [
            cat.name for cat in config.categories
        ]
        
        # Extract each category in order
        for category_name in extraction_order:
            category = next((c for c in config.categories if c.name == category_name), None)
            if not category:
                self.logger.warning(f"Category not found in config: {category_name}")
                continue
            
            # Check dependencies
            dependencies = config.dependencies.get(category_name, [])
            if dependencies:
                # Ensure dependencies are extracted first
                for dep_name in dependencies:
                    if dep_name not in extracted_data:
                        self.logger.warning(
                            f"Dependency {dep_name} not extracted before {category_name}"
                        )
            
            # Extract category
            try:
                category_result = await self._extract_category(
                    category=category,
                    data_source=data_source,
                    config=config,
                    context=context
                )
                
                extracted_data[category_name] = category_result.get("data", {})
                confidence_scores[category_name] = category_result.get("confidence", 0.0)
                
                categories.append({
                    "name": category_name,
                    "extraction_type": category.extraction_type,
                    "data": category_result.get("data", {}),
                    "confidence": category_result.get("confidence", 0.0),
                    "metadata": category_result.get("metadata", {})
                })
                
            except Exception as e:
                self.logger.error(f"Failed to extract category {category_name}: {e}", exc_info=True)
                extracted_data[category_name] = {}
                confidence_scores[category_name] = 0.0
                categories.append({
                    "name": category_name,
                    "extraction_type": category.extraction_type,
                    "data": {},
                    "confidence": 0.0,
                    "error": str(e)
                })
        
        return {
            "extraction_id": extraction_id,
            "extracted_data": extracted_data,
            "categories": categories,
            "confidence_scores": confidence_scores
        }
    
    async def _extract_category(
        self,
        category: ExtractionCategory,
        data_source: Dict[str, Any],
        config: ExtractionConfig,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Extract a single category using the configured extraction type.
        
        Args:
            category: ExtractionCategory to extract
            data_source: Data source
            config: Full ExtractionConfig (for context)
            context: Execution context
        
        Returns:
            Dict with extracted data and confidence
        """
        extraction_type = category.extraction_type
        
        if extraction_type == "llm":
            return await self._extract_via_llm(category, data_source, config, context)
        elif extraction_type == "pattern":
            return await self._extract_via_pattern(category, data_source, config, context)
        elif extraction_type == "embedding":
            return await self._extract_via_embedding(category, data_source, config, context)
        elif extraction_type == "hybrid":
            return await self._extract_via_hybrid(category, data_source, config, context)
        else:
            raise ValueError(f"Unknown extraction type: {extraction_type}")
    
    async def _extract_via_llm(
        self,
        category: ExtractionCategory,
        data_source: Dict[str, Any],
        config: ExtractionConfig,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Extract category using LLM."""
        # Build prompt from template
        prompt_template = category.prompt_template or f"""
Extract {category.name} information from the provided data source.
Return structured JSON data matching the expected schema.

Category: {category.name}
Description: {category.description}
Domain: {config.domain}
"""
        
        # Prepare data context for prompt (retrieve actual parsed file content)
        data_context = await self._prepare_data_context(data_source, context)
        
        prompt = f"{prompt_template}\n\nData Source:\n{json.dumps(data_context, indent=2)}"
        
        system_message = f"""
You are a structured data extraction expert specializing in {config.domain}.
Extract {category.name} information accurately and return valid JSON.
"""
        
        # Call LLM via governed access
        try:
            response_text = await self._call_llm(
                prompt=prompt,
                system_message=system_message,
                model="gpt-4o-mini",
                max_tokens=2000,
                temperature=0.3,
                user_context={"category": category.name, "domain": config.domain},
                metadata={"extraction_type": "llm", "category": category.name}
            )
            
            # Parse JSON response
            try:
                extracted_data = json.loads(response_text)
            except json.JSONDecodeError:
                # Try to extract JSON from markdown code blocks
                import re
                json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
                if json_match:
                    extracted_data = json.loads(json_match.group(1))
                else:
                    # Try to find JSON object in response
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        extracted_data = json.loads(json_match.group(0))
                    else:
                        raise ValueError("No valid JSON found in LLM response")
            
            # Validate extracted data
            confidence = self._calculate_confidence(extracted_data, category)
            
            return {
                "data": extracted_data,
                "confidence": confidence,
                "metadata": {
                    "extraction_method": "llm",
                    "model": "gpt-4o-mini"
                }
            }
            
        except Exception as e:
            self.logger.error(f"LLM extraction failed for {category.name}: {e}", exc_info=True)
            return {
                "data": {},
                "confidence": 0.0,
                "error": str(e),
                "metadata": {"extraction_method": "llm", "failed": True}
            }
    
    async def _extract_via_pattern(
        self,
        category: ExtractionCategory,
        data_source: Dict[str, Any],
        config: ExtractionConfig,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Extract category using pattern matching."""
        # Pattern-based extraction (for future implementation)
        # For MVP, fall back to LLM
        self.logger.info(f"Pattern extraction not yet implemented, falling back to LLM for {category.name}")
        return await self._extract_via_llm(category, data_source, config, context)
    
    async def _extract_via_embedding(
        self,
        category: ExtractionCategory,
        data_source: Dict[str, Any],
        config: ExtractionConfig,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Extract category using embedding similarity."""
        # Embedding-based extraction (for future implementation)
        # For MVP, fall back to LLM
        self.logger.info(f"Embedding extraction not yet implemented, falling back to LLM for {category.name}")
        return await self._extract_via_llm(category, data_source, config, context)
    
    async def _extract_via_hybrid(
        self,
        category: ExtractionCategory,
        data_source: Dict[str, Any],
        config: ExtractionConfig,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Extract category using hybrid approach (embeddings + LLM)."""
        # Hybrid extraction (for future implementation)
        # For MVP, use LLM
        self.logger.info(f"Hybrid extraction not yet implemented, using LLM for {category.name}")
        return await self._extract_via_llm(category, data_source, config, context)
    
    async def _prepare_data_context(
        self, 
        data_source: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Prepare data context for extraction.
        
        Retrieves actual parsed file content from state_surface.
        
        Args:
            data_source: Data source dictionary (may contain parsed_file_id)
            context: Execution context (required for state_surface access)
        
        Returns:
            Dict with parsed content and metadata
        """
        parsed_file_id = data_source.get("parsed_file_id")
        
        # If no parsed_file_id, return data_source as-is (for other data sources)
        if not parsed_file_id:
            return data_source
        
        # Retrieve actual parsed file content via Content Realm (governed access)
        # ARCHITECTURAL PRINCIPLE: Agents never retrieve files directly.
        # Use Content Realm service which goes through proper governance.
        try:
            if not self.public_works:
                self.logger.warning(
                    "Public Works not available - cannot retrieve parsed file via Content Realm. "
                    "Falling back to data_source as-is."
                )
                return {
                    "parsed_file_id": parsed_file_id,
                    "data_preview": "Data retrieval unavailable (Public Works not available)",
                    "metadata": data_source.get("metadata", {})
                }
            
            # Use Content Realm service (governed access)
            from symphainy_platform.realms.content.enabling_services.file_parser_service import FileParserService
            file_parser_service = FileParserService(public_works=self.public_works)
            
            parsed_file = await file_parser_service.get_parsed_file(
                parsed_file_id=parsed_file_id,
                tenant_id=context.tenant_id,
                context=context
            )
            
            parsed_content = parsed_file.get("parsed_content")
            
            # Create data preview (truncate for prompt efficiency)
            if isinstance(parsed_content, (dict, list)):
                data_preview = json.dumps(parsed_content, indent=2)[:2000]  # Limit to 2000 chars
            else:
                data_preview = str(parsed_content)[:2000]
            
            self.logger.info(
                f"Retrieved parsed file content via Content Realm: {parsed_file_id} "
                f"(type: {type(parsed_content).__name__}, size: {len(str(parsed_content))} chars)"
            )
            
            return {
                "parsed_file_id": parsed_file_id,
                "parsed_content": parsed_content,
                "data_preview": data_preview,
                "metadata": parsed_file.get("metadata", data_source.get("metadata", {}))
            }
        except Exception as e:
            self.logger.error(
                f"Failed to retrieve parsed file content via Content Realm for {parsed_file_id}: {e}",
                exc_info=True
            )
            return {
                "parsed_file_id": parsed_file_id,
                "data_preview": f"Error retrieving data via Content Realm: {str(e)}",
                "metadata": data_source.get("metadata", {}),
                "error": str(e)
            }
    
    def _calculate_confidence(
        self,
        extracted_data: Dict[str, Any],
        category: ExtractionCategory
    ) -> float:
        """Calculate confidence score for extracted data."""
        # Basic confidence calculation
        # For MVP: 0.8 if data exists, 0.0 if empty
        if not extracted_data:
            return 0.0
        
        # Check validation rules if provided
        validation_rules = category.validation_rules
        if validation_rules:
            # Simple validation: check if required fields exist
            # (Full implementation would validate against rules)
            return 0.7
        
        return 0.8  # Default confidence for non-empty data
    
    async def discover_pattern(
        self,
        data_source: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Discover extraction pattern from data.
        
        Args:
            data_source: Data source
            context: Execution context
        
        Returns:
            Dict with discovered pattern
        """
        self.logger.info("Discovering extraction pattern from data")
        
        # Use LLM to analyze data structure and propose categories
        data_context = await self._prepare_data_context(data_source, context)
        
        prompt = f"""
Analyze the following data source and propose an extraction pattern.
Suggest categories that should be extracted and their extraction types.

Data Source:
{json.dumps(data_context, indent=2)}

Return a JSON structure with:
- suggested_categories: List of category names
- extraction_types: Suggested extraction type for each category
- confidence: Confidence score (0.0-1.0)
"""
        
        system_message = """
You are a data analysis expert. Analyze data sources and propose extraction patterns.
Return valid JSON with suggested categories and extraction methods.
"""
        
        try:
            response_text = await self._call_llm(
                prompt=prompt,
                system_message=system_message,
                model="gpt-4o-mini",
                max_tokens=1500,
                temperature=0.5,
                metadata={"extraction_type": "pattern_discovery"}
            )
            
            # Parse response
            try:
                discovery_result = json.loads(response_text)
            except json.JSONDecodeError:
                import re
                json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
                if json_match:
                    discovery_result = json.loads(json_match.group(1))
                else:
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        discovery_result = json.loads(json_match.group(0))
                    else:
                        raise ValueError("No valid JSON found in discovery response")
            
            # Create ExtractionConfig from discovery result
            suggested_categories = discovery_result.get("suggested_categories", [])
            
            categories = []
            for cat_name in suggested_categories:
                categories.append(ExtractionCategory(
                    name=cat_name,
                    extraction_type=discovery_result.get("extraction_types", {}).get(cat_name, "llm"),
                    description=f"Discovered category: {cat_name}",
                    prompt_template=f"Extract {cat_name} information from the data source."
                ))
            
            config = ExtractionConfig(
                config_id=f"discovered_{str(uuid.uuid4())[:8]}",
                name="Discovered Extraction Pattern",
                description="Auto-discovered extraction pattern",
                domain="custom",
                categories=categories
            )
            
            return {
                "config": config,
                "confidence": discovery_result.get("confidence", 0.7),
                "analysis": discovery_result,
                "suggested_categories": suggested_categories
            }
            
        except Exception as e:
            self.logger.error(f"Pattern discovery failed: {e}", exc_info=True)
            return {
                "config": None,
                "confidence": 0.0,
                "analysis": {},
                "suggested_categories": [],
                "error": str(e)
            }
    
    async def generate_config_from_target_model(
        self,
        target_model_file_id: str,
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Generate extraction config from target data model.
        
        Retrieves actual target model content and analyzes it to generate extraction config.
        
        Args:
            target_model_file_id: Parsed file ID of target data model
            tenant_id: Tenant identifier
            context: Execution context
        
        Returns:
            Dict with generated config
        """
        self.logger.info(f"Generating extraction config from target model: {target_model_file_id}")
        
        # Retrieve actual target model content via Content Realm (governed access)
        # ARCHITECTURAL PRINCIPLE: Agents never retrieve files directly.
        # Use Content Realm service which goes through proper governance.
        target_model_content = None
        try:
            if not self.public_works:
                self.logger.warning(
                    "Public Works not available - cannot retrieve target model via Content Realm. "
                    "LLM will only receive file_id."
                )
            else:
                # Use Content Realm service (governed access)
                from symphainy_platform.realms.content.enabling_services.file_parser_service import FileParserService
                file_parser_service = FileParserService(public_works=self.public_works)
                
                target_model_file = await file_parser_service.get_parsed_file(
                    parsed_file_id=target_model_file_id,
                    tenant_id=tenant_id,
                    context=context
                )
                
                target_model_content = target_model_file.get("parsed_content")
                
                self.logger.info(
                    f"Retrieved target model content via Content Realm: {target_model_file_id} "
                    f"(type: {type(target_model_content).__name__})"
                )
        except Exception as e:
            self.logger.error(
                f"Failed to retrieve target model content via Content Realm for {target_model_file_id}: {e}",
                exc_info=True
            )
            # Continue with file_id only (will be less effective but won't fail completely)
        
        # Build prompt with actual target model content
        if target_model_content:
            # Format target model content for prompt
            if isinstance(target_model_content, (dict, list)):
                model_structure = json.dumps(target_model_content, indent=2)
            else:
                model_structure = str(target_model_content)
            
            # Truncate if too large (keep first 4000 chars for prompt efficiency)
            if len(model_structure) > 4000:
                model_structure = model_structure[:4000] + "\n... (truncated)"
            
            prompt = f"""
Analyze the following target data model structure and generate an extraction configuration.
The extraction config should extract data that matches the target model structure.

Target Model Structure:
{model_structure}

Return a JSON structure with:
- config_id: Unique identifier
- name: Config name
- description: Config description
- categories: List of extraction categories matching target model fields
- extraction_order: Suggested extraction order
- output_schema: JSON Schema matching the target model structure
"""
        else:
            # Fallback: use file_id only (less effective)
            prompt = f"""
Analyze the target data model (file_id: {target_model_file_id}) and generate an extraction configuration.
The extraction config should extract data that matches the target model structure.

Note: Target model content not available. Generate a generic extraction config structure.

Return a JSON structure with:
- config_id: Unique identifier
- name: Config name
- description: Config description
- categories: List of extraction categories matching target model fields
- extraction_order: Suggested extraction order
"""
        
        system_message = """
You are a data modeling expert. Analyze target data models and generate extraction configurations.
Return valid JSON with extraction config structure matching the target model.
"""
        
        try:
            response_text = await self._call_llm(
                prompt=prompt,
                system_message=system_message,
                model="gpt-4o-mini",
                max_tokens=2000,
                temperature=0.3,
                metadata={"extraction_type": "config_generation", "target_model": target_model_file_id}
            )
            
            # Parse and create config
            try:
                config_data = json.loads(response_text)
            except json.JSONDecodeError:
                import re
                json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
                if json_match:
                    config_data = json.loads(json_match.group(1))
                else:
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        config_data = json.loads(json_match.group(0))
                    else:
                        raise ValueError("No valid JSON found in config generation response")
            
            # Create ExtractionConfig from generated data
            categories = []
            for cat_data in config_data.get("categories", []):
                categories.append(ExtractionCategory.from_dict(cat_data))
            
            config = ExtractionConfig(
                config_id=config_data.get("config_id", f"generated_{str(uuid.uuid4())[:8]}"),
                name=config_data.get("name", "Generated Extraction Config"),
                description=config_data.get("description", "Generated from target model"),
                domain="custom",
                categories=categories,
                extraction_order=config_data.get("extraction_order", [])
            )
            
            return {"config": config}
            
        except Exception as e:
            self.logger.error(f"Config generation failed: {e}", exc_info=True)
            return {"config": None, "error": str(e)}
