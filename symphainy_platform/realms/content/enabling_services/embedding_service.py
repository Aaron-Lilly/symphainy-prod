"""
Embedding Service - Semantic Embeddings from Deterministic Embeddings

Enabling service for creating semantic embeddings from deterministic embeddings.

WHAT (Enabling Service Role): I create semantic embeddings (3 per column: metadata, meaning, samples)
HOW (Enabling Service Implementation): I use StatelessEmbeddingAgent for governed embedding generation

Key Principle: Requires deterministic_embedding_id as input (sequential dependency).
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from utilities import get_logger, generate_event_id
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.civic_systems.agentic.agents.stateless_embedding_agent import StatelessEmbeddingAgent
from symphainy_platform.civic_systems.agentic.agent_base import AgentBase


class EmbeddingService:
    """
    Embedding Service - Creates semantic embeddings from deterministic embeddings.
    
    Creates 3 embeddings per column:
    1. metadata_embedding: Column name + data type + structure
    2. meaning_embedding: Semantic meaning (inferred via LLM)
    3. samples_embedding: Representative sample values
    """
    
    def __init__(self, public_works: Optional[Any] = None):
        """
        Initialize Embedding Service.
        
        Args:
            public_works: Public Works Foundation Service (for accessing abstractions)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.public_works = public_works
        
        # Get abstractions from Public Works
        self.semantic_data_abstraction = None
        if public_works:
            self.semantic_data_abstraction = public_works.get_semantic_data_abstraction()
        
        # Create StatelessEmbeddingAgent for embedding generation (governed access)
        self.embedding_agent = None
        if public_works:
            self.embedding_agent = StatelessEmbeddingAgent(
                agent_id="embedding_service_agent",
                public_works=public_works
            )
        
        # Create agent for semantic meaning inference (governed LLM access)
        self.semantic_meaning_agent = None
        if public_works:
            self.semantic_meaning_agent = self._create_semantic_meaning_agent(public_works)
    
    def _create_semantic_meaning_agent(self, public_works: Any) -> AgentBase:
        """Create agent for semantic meaning inference."""
        from symphainy_platform.civic_systems.agentic.agent_base import AgentBase
        
        class SemanticMeaningAgent(AgentBase):
            async def process_request(self, request, context):
                return {}
            
            async def get_agent_description(self):
                return "Semantic meaning inference agent"
        
        return SemanticMeaningAgent(
            agent_id="semantic_meaning_agent",
            agent_type="semantic_analysis",
            capabilities=["llm_access"],
            public_works=public_works
        )
    
    async def create_semantic_embeddings(
        self,
        deterministic_embedding_id: str,
        parsed_file_id: str,
        context: ExecutionContext,
        sampling_strategy: str = "every_nth",
        n: int = 10
    ) -> Dict[str, Any]:
        """
        Create semantic embeddings from deterministic embeddings.
        
        CRITICAL: Requires deterministic_embedding_id as input (not parsed_file_id).
        Users must create deterministic embeddings first.
        
        Args:
            deterministic_embedding_id: Deterministic embedding identifier (REQUIRED)
            parsed_file_id: Parsed file identifier (for retrieving parsed content)
            context: Execution context
            sampling_strategy: Sampling strategy ("every_nth")
            n: Sample every nth row (default: 10)
        
        Returns:
            Dict with embedding_id, embeddings_count, and metadata
        """
        self.logger.info(f"Creating semantic embeddings from deterministic_embedding_id: {deterministic_embedding_id}")
        
        # 1. Get deterministic embedding from ArangoDB
        from ..enabling_services.deterministic_embedding_service import DeterministicEmbeddingService
        deterministic_service = DeterministicEmbeddingService(public_works=self.public_works)
        
        deterministic_embedding = await deterministic_service.get_deterministic_embedding(
            deterministic_embedding_id=deterministic_embedding_id,
            context=context
        )
        
        if not deterministic_embedding:
            raise ValueError(f"Deterministic embedding not found: {deterministic_embedding_id}")
        
        # 2. Extract schema and pattern signature
        schema = deterministic_embedding.get("schema", [])
        pattern_signature = deterministic_embedding.get("pattern_signature", {})
        
        # 3. Get parsed content (for sampling)
        from ..enabling_services.file_parser_service import FileParserService
        file_parser_service = FileParserService(public_works=self.public_works)
        
        parsed_content = await file_parser_service.get_parsed_file(
            parsed_file_id=parsed_file_id,
            tenant_id=context.tenant_id,
            context=context
        )
        
        # 4. Sample representative rows (every nth row)
        sampled_data = self._sample_representative(parsed_content, n=n)
        
        # 5. Create embeddings for each column
        embeddings = []
        content_id = generate_event_id()
        
        for col in schema:
            col_name = col.get("name")
            col_type = col.get("type", "unknown")
            
            # Get sample values from pattern signature
            col_signature = pattern_signature.get(col_name, {})
            sample_values = col_signature.get("sample_values", [])
            
            # If no samples in signature, extract from sampled data
            if not sample_values and sampled_data:
                sample_values = [
                    str(row.get(col_name, ""))
                    for row in sampled_data[:5]
                    if col_name in row and row[col_name] is not None
                ]
            
            # Create 3 embeddings per column
            column_embeddings = await self._create_column_embeddings(
                column_name=col_name,
                column_type=col_type,
                sample_values=sample_values,
                context=context
            )
            
            # Create embedding document
            embedding_doc = {
                "_key": generate_event_id(),
                "content_id": content_id,
                "parsed_file_id": parsed_file_id,
                "deterministic_embedding_id": deterministic_embedding_id,
                "column_name": col_name,
                "column_type": col_type,
                "column_position": col.get("position", 0),
                "metadata_embedding": column_embeddings["metadata_embedding"],
                "meaning_embedding": column_embeddings["meaning_embedding"],
                "samples_embedding": column_embeddings["samples_embedding"],
                "semantic_meaning": column_embeddings["semantic_meaning"],
                "sample_values": sample_values[:10],  # Store first 10 samples
                "tenant_id": context.tenant_id,
                "session_id": context.session_id,
                "created_at": datetime.utcnow().isoformat()
            }
            
            embeddings.append(embedding_doc)
        
        # 6. Store via SemanticDataAbstraction
        if self.semantic_data_abstraction:
            storage_result = await self.semantic_data_abstraction.store_semantic_embeddings(
                embedding_documents=embeddings
            )
            self.logger.info(f"✅ Stored {storage_result.get('stored_count', 0)} semantic embeddings")
        else:
            self.logger.warning("SemanticDataAbstraction not available - embeddings not stored")
        
        return {
            "embedding_id": content_id,
            "embeddings_count": len(embeddings),
            "deterministic_embedding_id": deterministic_embedding_id,
            "parsed_file_id": parsed_file_id,
            "columns_processed": len(schema)
        }
    
    async def _create_column_embeddings(
        self,
        column_name: str,
        column_type: str,
        sample_values: List[str],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Create 3 embeddings for a column (metadata, meaning, samples).
        
        Args:
            column_name: Column name
            column_type: Column data type
            sample_values: Sample values
            context: Execution context
        
        Returns:
            Dict with metadata_embedding, meaning_embedding, samples_embedding, semantic_meaning
        """
        if not self.embedding_agent:
            raise ValueError("StatelessEmbeddingAgent not available")
        
        # 1. Metadata embedding (column name + type)
        metadata_text = f"Column: {column_name}, Type: {column_type}"
        metadata_result = await self.embedding_agent.generate_embedding(
            text=metadata_text,
            context=context
        )
        metadata_embedding = metadata_result.get("embedding", [])
        
        # 2. Semantic meaning (inferred via LLM via agent)
        semantic_meaning = await self._infer_semantic_meaning(
            column_name=column_name,
            column_type=column_type,
            sample_values=sample_values,
            context=context
        )
        
        # 3. Meaning embedding (from semantic meaning text)
        meaning_result = await self.embedding_agent.generate_embedding(
            text=semantic_meaning,
            context=context
        )
        meaning_embedding = meaning_result.get("embedding", [])
        
        # 4. Samples embedding (representative sample values)
        samples_text = f"Sample values: {', '.join(sample_values[:5])}" if sample_values else "No samples"
        samples_result = await self.embedding_agent.generate_embedding(
            text=samples_text,
            context=context
        )
        samples_embedding = samples_result.get("embedding", [])
        
        return {
            "metadata_embedding": metadata_embedding,
            "meaning_embedding": meaning_embedding,
            "samples_embedding": samples_embedding,
            "semantic_meaning": semantic_meaning
        }
    
    async def _infer_semantic_meaning(
        self,
        column_name: str,
        column_type: str,
        sample_values: List[str],
        context: ExecutionContext
    ) -> str:
        """
        Infer semantic meaning of a column using agent-based LLM reasoning.
        
        Uses agent._call_llm() for governed LLM access.
        
        Args:
            column_name: Column name
            column_type: Column data type
            sample_values: Sample values
            context: Execution context
        
        Returns:
            Semantic meaning text
        """
        if not self.semantic_meaning_agent:
            # Fallback to column name if agent not available
            return f"Column: {column_name}"
        
        try:
            system_message = """You are a data analyst inferring the semantic meaning of database columns.

Analyze the column name, data type, and sample values to determine what the column represents.

Return ONLY a concise description (1-5 words) of what the column represents.
Examples:
- "email" -> "Customer email address"
- "created_at" -> "Record creation timestamp"
- "amount" -> "Transaction amount"
- "status" -> "Order status code"

Be specific and descriptive."""
            
            samples_str = ', '.join(sample_values[:5]) if sample_values else "no samples"
            user_prompt = f"""Column name: {column_name}
Data type: {column_type}
Sample values: {samples_str}

What does this column represent? Return ONLY a concise description (1-5 words)."""
            
            # Use agent._call_llm() for governed LLM access
            response_text = await self.semantic_meaning_agent._call_llm(
                prompt=user_prompt,
                system_message=system_message,
                model="gpt-4o-mini",
                max_tokens=30,
                temperature=0.3
            )
            
            # Clean up response
            meaning = response_text.strip() if isinstance(response_text, str) else str(response_text).strip()
            if not meaning or len(meaning) < 2:
                # Fallback to column name if response is too short
                meaning = f"Column: {column_name}"
            
            return meaning
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to infer semantic meaning via agent for {column_name}: {e}, using column name")
            return f"Column: {column_name}"
    
    def _sample_representative(self, parsed_content: Dict[str, Any], n: int = 10) -> List[Dict[str, Any]]:
        """
        Sample representative rows (every nth row).
        
        Args:
            parsed_content: Parsed file content
            n: Sample every nth row (default: 10)
        
        Returns:
            List of sampled rows
        """
        data = parsed_content.get("data", [])
        
        if not isinstance(data, list) or len(data) == 0:
            return []
        
        # Sample every nth row
        sampled = [data[i] for i in range(0, len(data), n)]
        
        self.logger.info(f"Sampled {len(sampled)} rows from {len(data)} total rows (every {n}th row)")
        
        return sampled
