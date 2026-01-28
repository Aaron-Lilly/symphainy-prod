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
            
            async def _process_with_assembled_prompt(
                self,
                system_message: str,
                user_message: str,
                runtime_context: Any,  # AgentRuntimeContext
                context: Any  # ExecutionContext
            ) -> Dict[str, Any]:
                """
                Process request with assembled prompt (4-layer model).
                
                This is a placeholder implementation for semantic meaning inference.
                The actual semantic meaning generation is handled elsewhere.
                
                Args:
                    system_message: Assembled system message (from layers 1-3)
                    user_message: Assembled user message
                    runtime_context: Runtime context
                    context: Execution context
                
                Returns:
                    Dict with empty result (semantic meaning handled elsewhere)
                """
                return {
                    "artifact_type": "semantic_meaning",
                    "artifact": {},
                    "confidence": 0.0
                }
            
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
        from symphainy_platform.foundations.libraries.embeddings.deterministic_embedding_service import DeterministicEmbeddingService
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
        from symphainy_platform.foundations.libraries.parsing.file_parser_service import FileParserService
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
    
    # ============================================================================
    # CHUNK-BASED EMBEDDING METHODS (Phase 2 - CTO + CIO Aligned)
    # ============================================================================
    
    async def create_chunk_embeddings(
        self,
        chunks: List[Any],  # List[DeterministicChunk]
        semantic_profile: str = "default",
        model_name: str = "text-embedding-ada-002",
        semantic_version: str = "1.0.0",
        tenant_id: str = None,
        context: Optional[ExecutionContext] = None
    ) -> Dict[str, Any]:
        """
        Create semantic embeddings for chunks (idempotent, profile-aware).
        
        CTO Principle: Chunk-based, idempotent, profile-aware, stores by reference
        CIO Requirement: Per-chunk embeddings, stable chunk IDs, explicit failures
        
        Args:
            chunks: List of DeterministicChunk objects
            semantic_profile: Semantic profile name (default: "default")
            model_name: Embedding model name (default: "text-embedding-ada-002")
            semantic_version: Semantic version (platform-controlled, default: "1.0.0")
            tenant_id: Tenant identifier
            context: Execution context (for tenant_id if not provided)
        
        Returns:
            {
                "status": "success" | "partial" | "failed",
                "embedded_chunk_ids": List[str],
                "failed_chunks": List[Dict[str, Any]],
                "semantic_profile": str,
                "model_name": str,
                "semantic_version": str
            }
        """
        if not chunks:
            return {
                "status": "failed",
                "embedded_chunk_ids": [],
                "failed_chunks": [],
                "semantic_profile": semantic_profile,
                "model_name": model_name,
                "semantic_version": semantic_version,
                "error": "No chunks provided"
            }
        
        # Get tenant_id from context if not provided
        if not tenant_id and context:
            tenant_id = context.tenant_id
        
        if not tenant_id:
            raise ValueError("tenant_id is required (provide directly or via context)")
        
        self.logger.info(
            f"Creating chunk embeddings: {len(chunks)} chunks, "
            f"profile={semantic_profile}, model={model_name}"
        )
        
        results = {
            "status": "success",
            "embedded_chunk_ids": [],
            "failed_chunks": [],
            "semantic_profile": semantic_profile,
            "model_name": model_name,
            "semantic_version": semantic_version
        }
        
        # Get LLM adapter for embedding generation
        llm_adapter = None
        if self.public_works:
            llm_adapter = getattr(self.public_works, 'openai_adapter', None)
            if not llm_adapter:
                # Try to get from LLM adapter registry
                llm_adapter_registry = getattr(self.public_works, 'llm_adapter_registry', None)
                if llm_adapter_registry:
                    llm_adapter = llm_adapter_registry.get_adapter("openai")
        
        if not llm_adapter:
            raise ValueError("LLM adapter not available for embedding generation")
        
        # Process each chunk
        embedding_documents = []
        
        for chunk in chunks:
            try:
                # Import DeterministicChunk to check type
                from .deterministic_chunking_service import DeterministicChunk
                
                # Validate chunk type
                if not isinstance(chunk, DeterministicChunk):
                    raise ValueError(f"Invalid chunk type: {type(chunk)}")
                
                # Idempotency check (CTO principle)
                if await self._chunk_embedding_exists(
                    chunk_id=chunk.chunk_id,
                    semantic_profile=semantic_profile,
                    model_name=model_name,
                    semantic_version=semantic_version
                ):
                    self.logger.debug(
                        f"Chunk {chunk.chunk_id} already embedded "
                        f"(profile={semantic_profile}, model={model_name})"
                    )
                    results["embedded_chunk_ids"].append(chunk.chunk_id)
                    continue  # Skip if already embedded
                
                # Create embedding via LLM adapter
                embedding_vector = await self._create_embedding_vector(
                    text=chunk.text,
                    model_name=model_name,
                    llm_adapter=llm_adapter,
                    context=context
                )
                
                # Create embedding document (stores by reference, not blob - CTO principle)
                embedding_doc = {
                    "_key": generate_event_id(),  # Unique document key
                    "chunk_id": chunk.chunk_id,  # Reference to deterministic chunk
                    "chunk_index": chunk.chunk_index,
                    "source_path": chunk.source_path,
                    "text_hash": chunk.text_hash,
                    "structural_type": chunk.structural_type,
                    "embedding": embedding_vector,  # Vector embedding
                    "semantic_profile": semantic_profile,
                    "model_name": model_name,
                    "semantic_version": semantic_version,  # Platform-controlled (CTO principle)
                    "schema_fingerprint": chunk.schema_fingerprint,  # Link to schema-level
                    "pattern_hints": chunk.pattern_hints,
                    "tenant_id": tenant_id,
                    "session_id": context.session_id if context else None,
                    "metadata": {
                        "chunk_index": chunk.chunk_index,
                        "source_path": chunk.source_path,
                        "text_hash": chunk.text_hash,
                        "structural_type": chunk.structural_type,
                        "schema_fingerprint": chunk.schema_fingerprint,
                        "file_id": chunk.metadata.get("file_id") if chunk.metadata else None,
                        "parsed_file_id": chunk.metadata.get("parsed_file_id") if chunk.metadata else None,
                        "created_at": datetime.utcnow().isoformat()
                    }
                }
                
                embedding_documents.append(embedding_doc)
                results["embedded_chunk_ids"].append(chunk.chunk_id)
                
            except Exception as e:
                # Explicit failure handling (CIO Gap 3)
                error_info = {
                    "chunk_id": chunk.chunk_id if hasattr(chunk, 'chunk_id') else "unknown",
                    "chunk_index": chunk.chunk_index if hasattr(chunk, 'chunk_index') else "unknown",
                    "error": str(e),
                    "error_type": type(e).__name__
                }
                results["failed_chunks"].append(error_info)
                results["status"] = "partial" if results["embedded_chunk_ids"] else "failed"
                self.logger.error(
                    f"Failed to create embedding for chunk {error_info['chunk_id']}: {e}",
                    exc_info=True
                )
        
        # Store embeddings via SemanticDataAbstraction (if any succeeded)
        if embedding_documents and self.semantic_data_abstraction:
            try:
                storage_result = await self.semantic_data_abstraction.store_semantic_embeddings(
                    embedding_documents=embedding_documents
                )
                self.logger.info(
                    f"✅ Stored {storage_result.get('stored_count', 0)} chunk embeddings "
                    f"(profile={semantic_profile}, model={model_name})"
                )
            except Exception as e:
                self.logger.error(f"Failed to store chunk embeddings: {e}", exc_info=True)
                # Mark all as failed if storage fails
                for doc in embedding_documents:
                    results["failed_chunks"].append({
                        "chunk_id": doc.get("chunk_id"),
                        "chunk_index": doc.get("chunk_index"),
                        "error": f"Storage failed: {str(e)}",
                        "error_type": "StorageError"
                    })
                    if doc.get("chunk_id") in results["embedded_chunk_ids"]:
                        results["embedded_chunk_ids"].remove(doc.get("chunk_id"))
                results["status"] = "failed"
        elif embedding_documents and not self.semantic_data_abstraction:
            self.logger.warning("SemanticDataAbstraction not available - embeddings not stored")
            # Mark as failed if storage abstraction not available
            for doc in embedding_documents:
                results["failed_chunks"].append({
                    "chunk_id": doc.get("chunk_id"),
                    "chunk_index": doc.get("chunk_index"),
                    "error": "SemanticDataAbstraction not available",
                    "error_type": "ConfigurationError"
                })
                if doc.get("chunk_id") in results["embedded_chunk_ids"]:
                    results["embedded_chunk_ids"].remove(doc.get("chunk_id"))
            results["status"] = "failed"
        
        # Log final status
        success_count = len(results["embedded_chunk_ids"])
        failed_count = len(results["failed_chunks"])
        self.logger.info(
            f"Chunk embedding creation complete: "
            f"{success_count} succeeded, {failed_count} failed "
            f"(status={results['status']})"
        )
        
        return results
    
    async def _chunk_embedding_exists(
        self,
        chunk_id: str,
        semantic_profile: str,
        model_name: str,
        semantic_version: str
    ) -> bool:
        """
        Check if chunk embedding already exists (idempotency check).
        
        CTO Principle: Idempotent - won't re-embed existing chunks
        """
        if not self.semantic_data_abstraction:
            return False
        
        try:
            # Query for existing embedding with matching criteria
            existing_embeddings = await self.semantic_data_abstraction.get_semantic_embeddings(
                filter_conditions={
                    "chunk_id": chunk_id,
                    "semantic_profile": semantic_profile,
                    "model_name": model_name,
                    "semantic_version": semantic_version
                },
                limit=1
            )
            
            return len(existing_embeddings) > 0
            
        except Exception as e:
            self.logger.debug(f"Error checking for existing embedding: {e}")
            return False  # If check fails, proceed with creation
    
    async def _create_embedding_vector(
        self,
        text: str,
        model_name: str,
        llm_adapter: Any,
        context: Optional[ExecutionContext] = None
    ) -> List[float]:
        """
        Create embedding vector from text using LLM adapter.
        
        Args:
            text: Text to embed
            model_name: Embedding model name
            llm_adapter: LLM adapter instance
            context: Execution context
        
        Returns:
            List of floats (embedding vector)
        """
        # Try to use adapter's embedding method
        if hasattr(llm_adapter, 'create_embeddings'):
            result = await llm_adapter.create_embeddings(
                text=text,
                model=model_name
            )
            # Handle different response formats
            if isinstance(result, dict):
                return result.get("embedding", result.get("data", [result])[0] if isinstance(result.get("data"), list) else [])
            elif isinstance(result, list):
                return result
            else:
                raise ValueError(f"Unexpected embedding response format: {type(result)}")
        elif hasattr(llm_adapter, 'generate_embedding'):
            # Alternative method name
            result = await llm_adapter.generate_embedding(
                text=text,
                model=model_name
            )
            if isinstance(result, dict):
                return result.get("embedding", [])
            elif isinstance(result, list):
                return result
            else:
                raise ValueError(f"Unexpected embedding response format: {type(result)}")
        elif self.embedding_agent:
            # Fallback to StatelessEmbeddingAgent
            result = await self.embedding_agent.generate_embedding(
                text=text,
                context=context
            )
            if isinstance(result, dict):
                return result.get("embedding", [])
            elif isinstance(result, list):
                return result
            else:
                raise ValueError(f"Unexpected embedding response format: {type(result)}")
        else:
            raise ValueError("No embedding generation method available")