"""
Semantic Signal Extractor - Structured Semantic Outputs

Enabling service for extracting structured semantic signals from deterministic chunks.

WHAT (Enabling Service Role): I extract structured semantic signals (not prose-first)
HOW (Enabling Service Implementation): I use LLM with structured output format to extract signals

CTO Principle: Semantic normalizer, not a philosopher
CIO Requirement: Produces structured meaning other agents can depend on
Platform Enhancement: Uses 4-layer agent model for structure
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
from datetime import datetime
import json

from utilities import get_logger
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.civic_systems.agentic.agent_base import AgentBase


class SemanticSignalExtractor(AgentBase):
    """
    Semantic Signal Extractor - Semantic normalizer, not a philosopher.
    
    CTO Principle: Extracts structured semantic signals, normalizes language
    CIO Requirement: Produces structured meaning other agents can depend on
    Platform Enhancement: Uses 4-layer agent model for structure
    """
    
    def __init__(
        self,
        agent_id: str = "semantic_signal_extractor",
        agent_type: str = "semantic_analysis",
        capabilities: Optional[List[str]] = None,
        public_works: Optional[Any] = None
    ):
        """
        Initialize Semantic Signal Extractor.
        
        Args:
            agent_id: Agent identifier
            agent_type: Agent type
            capabilities: Agent capabilities
            public_works: Public Works Foundation Service
        """
        super().__init__(
            agent_id=agent_id,
            agent_type=agent_type,
            capabilities=capabilities or ["llm_access", "semantic_analysis"],
            public_works=public_works
        )
        self.logger = get_logger(self.__class__.__name__)
    
    async def process_request(
        self,
        request: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Process request to extract semantic signals.
        
        Args:
            request: Request dictionary (should contain chunks)
            context: Execution context
        
        Returns:
            Structured semantic signals artifact
        """
        # Extract chunks from request
        chunks = request.get("chunks", [])
        
        if not chunks:
            return {
                "artifact_type": "semantic_signals",
                "artifact": {
                    "error": "No chunks provided"
                },
                "confidence": 0.0,
                "source_artifact_id": None,
                "producing_agent": self.get_agent_description().get("name"),
                "timestamp": datetime.utcnow().isoformat(),
                "tenant_id": context.tenant_id,
                "derived_from": []
            }
        
        # Create runtime context for agent processing (dict-like)
        runtime_context: Dict[str, Any] = {
            "chunks": chunks,
            "context": context
        }
        
        # Build system message (Layer 1 - AgentDefinition)
        system_message = self._build_system_message()
        
        # Build user message with chunks
        user_message = self._build_user_message(chunks)
        
        # Process with assembled prompt (4-layer model)
        return await self._process_with_assembled_prompt(
            system_message=system_message,
            user_message=user_message,
            runtime_context=runtime_context,
            context=context
        )
    
    async def _process_with_assembled_prompt(
        self,
        system_message: str,
        user_message: str,
        runtime_context: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Extract structured semantic signals from chunks.
        
        CIO Requirement: Structured output, not prose-only
        CTO Principle: Reference chunk IDs, not raw text
        
        Args:
            system_message: Assembled system message (from layers 1-3)
            user_message: Assembled user message
            runtime_context: Runtime context (contains chunks)
            context: Execution context
        
        Returns:
            Structured semantic signals artifact
        """
        # Extract chunks from runtime_context
        chunks = runtime_context.get("chunks", [])
        
        if not chunks:
            return {
                "artifact_type": "semantic_signals",
                "artifact": {
                    "error": "No chunks provided"
                },
                "confidence": 0.0,
                "source_artifact_id": None,
                "producing_agent": self.get_agent_description().get("name"),
                "timestamp": datetime.utcnow().isoformat(),
                "tenant_id": context.tenant_id,
                "derived_from": []
            }
        
        # Extract structured signals (not prose)
        signals = await self._extract_structured_signals(
            chunks=chunks,
            system_message=system_message,
            context=context
        )
        
        # CIO Requirement: Self-describing artifact
        return {
            "artifact_type": "semantic_signals",
            "artifact": {
                "key_concepts": signals.get("key_concepts", []),
                "inferred_intents": signals.get("inferred_intents", []),
                "domain_hints": signals.get("domain_hints", []),
                "entities": {
                    "dates": signals.get("dates", []),
                    "documents": signals.get("documents", []),
                    "people": signals.get("people", []),
                    "organizations": signals.get("organizations", [])
                },
                "ambiguities": signals.get("ambiguities", []),
                "interpretation": signals.get("interpretation", "")  # Optional prose
            },
            "confidence": signals.get("confidence", 0.7),
            # CIO Requirement: Self-describing metadata
            "source_artifact_id": chunks[0].chunk_id if chunks else None,
            "producing_agent": self.get_agent_description().get("name"),
            "timestamp": datetime.utcnow().isoformat(),
            "tenant_id": context.tenant_id,
            # CTO Principle: Reference deterministic IDs
            "derived_from": [chunk.chunk_id for chunk in chunks]
        }
    
    async def _extract_structured_signals(
        self,
        chunks: List[Any],  # List[DeterministicChunk]
        system_message: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Extract structured signals using LLM with JSON response format.
        
        CIO Requirement: Deterministic and replayable (modulo model variance)
        """
        # Build structured extraction prompt
        prompt = self._build_structured_extraction_prompt(chunks)
        
        # Get LLM via boundary getter only (CTA: no adapter at boundary; no silent failure)
        llm = None
        if self.public_works and hasattr(self.public_works, "get_llm_abstraction"):
            llm = self.public_works.get_llm_abstraction()
        if not llm:
            raise RuntimeError(
                "LLM not available for semantic signal extraction. "
                "Ensure Public Works provides get_llm_abstraction() and LLM is configured."
            )
        
        # Use LLM protocol complete() with system_message
        try:
            result = await llm.complete(
                prompt=prompt,
                model="gpt-4o-mini",
                max_tokens=1000,
                temperature=0.3,
                system_message=system_message,
            )
            content = result.get("content", "") if isinstance(result, dict) else str(result)
            
            # Parse JSON response
            if isinstance(content, str):
                signals = json.loads(content) if content.strip() else {}
            elif isinstance(content, dict):
                signals = content
            else:
                signals = {}
            
            # Ensure all required fields exist
            return {
                "key_concepts": signals.get("key_concepts", []),
                "inferred_intents": signals.get("inferred_intents", []),
                "domain_hints": signals.get("domain_hints", []),
                "dates": signals.get("dates", []),
                "documents": signals.get("documents", []),
                "people": signals.get("people", []),
                "organizations": signals.get("organizations", []),
                "ambiguities": signals.get("ambiguities", []),
                "interpretation": signals.get("interpretation", ""),
                "confidence": signals.get("confidence", 0.7)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to extract structured signals: {e}", exc_info=True)
            # Return empty signals on error
            return {
                "key_concepts": [],
                "inferred_intents": [],
                "domain_hints": [],
                "dates": [],
                "documents": [],
                "people": [],
                "organizations": [],
                "ambiguities": [],
                "interpretation": f"Error: {str(e)}",
                "confidence": 0.0
            }
    
    def _build_system_message(self) -> str:
        """Build system message for semantic signal extraction."""
        return """You are a semantic signal extractor. Your role is to extract structured semantic signals from text chunks, not to write prose.

Extract the following structured signals:
1. key_concepts: List of key concepts or topics
2. inferred_intents: List of inferred user intents or purposes
3. domain_hints: List of domain or industry hints
4. entities: Extract dates, documents, people, organizations
5. ambiguities: List of ambiguous terms or concepts
6. interpretation: Optional brief prose interpretation (keep concise)

Return your response as JSON with these exact field names."""
    
    def _build_user_message(self, chunks: List[Any]) -> str:
        """Build user message with chunk text."""
        # Combine chunk texts
        chunk_texts = []
        for chunk in chunks:
            chunk_text = chunk.text if hasattr(chunk, 'text') else str(chunk)
            chunk_texts.append(chunk_text)
        
        combined_text = "\n\n".join(chunk_texts)
        
        return f"""Extract structured semantic signals from the following text chunks:

{combined_text}

Return a JSON object with the following structure:
{{
    "key_concepts": ["concept1", "concept2"],
    "inferred_intents": ["intent1", "intent2"],
    "domain_hints": ["domain1", "domain2"],
    "dates": ["date1", "date2"],
    "documents": ["doc1", "doc2"],
    "people": ["person1", "person2"],
    "organizations": ["org1", "org2"],
    "ambiguities": ["ambiguity1", "ambiguity2"],
    "interpretation": "Brief interpretation",
    "confidence": 0.8
}}"""
    
    def _build_structured_extraction_prompt(self, chunks: List[Any]) -> str:
        """Build prompt for structured extraction."""
        return self._build_user_message(chunks)
    
    async def get_agent_description(self) -> Dict[str, Any]:
        """Get agent description."""
        return {
            "name": "SemanticSignalExtractor",
            "type": "semantic_analysis",
            "description": "Extracts structured semantic signals from deterministic chunks",
            "capabilities": ["llm_access", "semantic_analysis"]
        }
