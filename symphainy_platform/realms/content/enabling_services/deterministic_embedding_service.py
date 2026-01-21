"""
Deterministic Embedding Service - Schema Fingerprints + Pattern Signatures

Enabling service for creating deterministic embeddings from parsed files.

WHAT (Enabling Service Role): I create deterministic embeddings (schema fingerprints + pattern signatures)
HOW (Enabling Service Implementation): I extract schema structure and data patterns from parsed content

Key Principle: Deterministic = reproducible, hash-based, exact matching capable.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List
from datetime import datetime
import hashlib
import json
import re
from collections import Counter

from utilities import get_logger, generate_event_id
from symphainy_platform.runtime.execution_context import ExecutionContext


class DeterministicEmbeddingService:
    """
    Deterministic Embedding Service - Creates schema fingerprints and pattern signatures.
    
    Deterministic Embeddings = Schema Fingerprints + Pattern Signatures:
    - Schema Fingerprint: Hash of column structure (names, types, positions, constraints)
    - Pattern Signature: Statistical signature of data patterns (distributions, formats, ranges)
    """
    
    def __init__(self, public_works: Optional[Any] = None):
        """
        Initialize Deterministic Embedding Service.
        
        Args:
            public_works: Public Works Foundation Service (for accessing abstractions)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.public_works = public_works
        
        # Get ArangoDB adapter for storage
        self.arango_adapter = None
        if public_works:
            self.arango_adapter = public_works.get_arango_adapter()
    
    async def create_deterministic_embeddings(
        self,
        parsed_file_id: str,
        parsed_content: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Create deterministic embeddings (schema fingerprints + pattern signatures).
        
        Args:
            parsed_file_id: Parsed file identifier
            parsed_content: Parsed file content (from FileParserService)
            context: Execution context
        
        Returns:
            Dict with deterministic_embedding_id, schema_fingerprint, and pattern_signature
        """
        self.logger.info(f"Creating deterministic embeddings for parsed_file_id: {parsed_file_id}")
        
        # Extract schema from parsed content
        schema = self._extract_schema(parsed_content)
        
        # Create schema fingerprint
        schema_fingerprint = self._create_schema_fingerprint(schema)
        
        # Create pattern signature
        pattern_signature = await self._create_pattern_signature(parsed_content, schema)
        
        # Store in ArangoDB
        embedding_doc = {
            "_key": generate_event_id(),
            "parsed_file_id": parsed_file_id,
            "tenant_id": context.tenant_id,
            "session_id": context.session_id,
            "schema_fingerprint": schema_fingerprint,
            "pattern_signature": pattern_signature,
            "schema": schema,  # Store full schema for reference
            "created_at": datetime.utcnow().isoformat()
        }
        
        embedding_id = await self._store_deterministic_embedding(embedding_doc, context)
        
        self.logger.info(f"✅ Deterministic embeddings created: {embedding_id}")
        
        return {
            "deterministic_embedding_id": embedding_id,
            "schema_fingerprint": schema_fingerprint,
            "pattern_signature": pattern_signature,
            "schema": schema
        }
    
    def _extract_schema(self, parsed_content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract schema from parsed content.
        
        Args:
            parsed_content: Parsed file content
        
        Returns:
            List of column definitions with name, type, position
        """
        schema = []
        
        # Try to get schema from metadata
        metadata = parsed_content.get("metadata", {})
        columns = metadata.get("columns", [])
        
        if columns:
            # Schema already extracted
            for idx, col in enumerate(columns):
                schema.append({
                    "name": col.get("name", f"column_{idx}"),
                    "type": col.get("type", "unknown"),
                    "position": idx,
                    "nullable": col.get("nullable", True),
                    "constraints": col.get("constraints", [])
                })
        else:
            # Try to infer schema from data
            data = parsed_content.get("data", [])
            if isinstance(data, list) and len(data) > 0:
                first_row = data[0]
                if isinstance(first_row, dict):
                    for idx, (key, value) in enumerate(first_row.items()):
                        inferred_type = self._infer_type(value)
                        schema.append({
                            "name": key,
                            "type": inferred_type,
                            "position": idx,
                            "nullable": True,
                            "constraints": []
                        })
        
        return schema
    
    def _infer_type(self, value: Any) -> str:
        """Infer data type from value."""
        if value is None:
            return "null"
        elif isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "integer"
        elif isinstance(value, float):
            return "float"
        elif isinstance(value, str):
            # Try to detect more specific types
            if re.match(r'^\d{4}-\d{2}-\d{2}', value):
                return "date"
            elif re.match(r'^\d{4}-\d{2}-\d{2}T', value):
                return "datetime"
            elif re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', value):
                return "email"
            elif re.match(r'^\+?[\d\s\-\(\)]+$', value):
                return "phone"
            else:
                return "string"
        elif isinstance(value, list):
            return "array"
        elif isinstance(value, dict):
            return "object"
        else:
            return "unknown"
    
    def _create_schema_fingerprint(self, schema: List[Dict[str, Any]]) -> str:
        """
        Create schema fingerprint (hash of column structure).
        
        Args:
            schema: List of column definitions
        
        Returns:
            SHA256 hash of schema structure
        """
        # Normalize schema for hashing
        normalized_schema = []
        for col in sorted(schema, key=lambda x: x.get("position", 0)):
            normalized_col = {
                "name": col.get("name", "").lower().strip(),
                "type": col.get("type", "unknown").lower(),
                "position": col.get("position", 0),
                "nullable": col.get("nullable", True),
                "constraints": sorted(col.get("constraints", []))
            }
            normalized_schema.append(normalized_col)
        
        # Create hash
        schema_json = json.dumps(normalized_schema, sort_keys=True)
        fingerprint = hashlib.sha256(schema_json.encode('utf-8')).hexdigest()
        
        return fingerprint
    
    async def _create_pattern_signature(
        self,
        parsed_content: Dict[str, Any],
        schema: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create pattern signature (statistical signature of data patterns).
        
        Args:
            parsed_content: Parsed file content
            schema: Schema definition
        
        Returns:
            Pattern signature dictionary
        """
        signature = {}
        data = parsed_content.get("data", [])
        
        if not isinstance(data, list) or len(data) == 0:
            return {"empty": True}
        
        # Analyze each column
        for col in schema:
            col_name = col.get("name")
            col_type = col.get("type", "unknown")
            
            # Extract column values
            values = []
            for row in data:
                if isinstance(row, dict) and col_name in row:
                    values.append(row[col_name])
            
            if not values:
                continue
            
            # Calculate statistics
            col_signature = {
                "type": col_type,
                "total_count": len(values),
                "null_count": sum(1 for v in values if v is None),
                "unique_count": len(set(v for v in values if v is not None))
            }
            
            # Type-specific analysis
            if col_type in ["integer", "float"]:
                numeric_values = [v for v in values if v is not None and isinstance(v, (int, float))]
                if numeric_values:
                    col_signature["min"] = min(numeric_values)
                    col_signature["max"] = max(numeric_values)
                    col_signature["mean"] = sum(numeric_values) / len(numeric_values)
            
            elif col_type == "string":
                string_values = [str(v) for v in values if v is not None]
                if string_values:
                    # Length statistics
                    lengths = [len(s) for s in string_values]
                    col_signature["min_length"] = min(lengths)
                    col_signature["max_length"] = max(lengths)
                    col_signature["mean_length"] = sum(lengths) / len(lengths)
                    
                    # Format patterns (sample)
                    sample_values = string_values[:10]
                    col_signature["sample_values"] = sample_values
                    
                    # Pattern detection
                    patterns = self._detect_patterns(string_values)
                    if patterns:
                        col_signature["patterns"] = patterns
            
            elif col_type in ["date", "datetime"]:
                date_values = [v for v in values if v is not None]
                if date_values:
                    col_signature["date_range"] = {
                        "earliest": min(date_values),
                        "latest": max(date_values)
                    }
            
            signature[col_name] = col_signature
        
        return signature
    
    def _detect_patterns(self, values: List[str]) -> Dict[str, Any]:
        """Detect common patterns in string values."""
        patterns = {}
        
        # Email pattern
        email_count = sum(1 for v in values if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', v))
        if email_count > len(values) * 0.5:
            patterns["email"] = True
        
        # Phone pattern
        phone_count = sum(1 for v in values if re.match(r'^\+?[\d\s\-\(\)]+$', v))
        if phone_count > len(values) * 0.5:
            patterns["phone"] = True
        
        # UUID pattern
        uuid_count = sum(1 for v in values if re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', v, re.I))
        if uuid_count > len(values) * 0.5:
            patterns["uuid"] = True
        
        # Numeric string pattern
        numeric_count = sum(1 for v in values if re.match(r'^\d+$', v))
        if numeric_count > len(values) * 0.5:
            patterns["numeric_string"] = True
        
        return patterns
    
    async def _store_deterministic_embedding(
        self,
        embedding_doc: Dict[str, Any],
        context: ExecutionContext
    ) -> str:
        """
        Store deterministic embedding in ArangoDB.
        
        Args:
            embedding_doc: Embedding document
            context: Execution context
        
        Returns:
            Embedding ID (_key)
        """
        if not self.arango_adapter:
            self.logger.warning("ArangoDB adapter not available - skipping storage")
            return embedding_doc["_key"]
        
        collection_name = "deterministic_embeddings"
        database = context.tenant_id or "symphainy_platform"
        
        try:
            # Ensure collection exists
            if not await self.arango_adapter.collection_exists(collection_name):
                await self.arango_adapter.create_collection(collection_name)
            
            # Store document
            result = await self.arango_adapter.create_document(
                collection=collection_name,
                document=embedding_doc,
                database=database
            )
            
            embedding_id = result.get("_key") or embedding_doc["_key"]
            self.logger.info(f"Stored deterministic embedding: {embedding_id}")
            
            return embedding_id
            
        except Exception as e:
            self.logger.error(f"Failed to store deterministic embedding: {e}")
            # Return ID even if storage fails (graceful degradation)
            return embedding_doc["_key"]
    
    async def get_deterministic_embedding(
        self,
        deterministic_embedding_id: str,
        context: ExecutionContext
    ) -> Optional[Dict[str, Any]]:
        """
        Get deterministic embedding by ID.
        
        Args:
            deterministic_embedding_id: Embedding identifier
            context: Execution context
        
        Returns:
            Embedding document or None
        """
        if not self.arango_adapter:
            return None
        
        collection_name = "deterministic_embeddings"
        database = context.tenant_id or "symphainy_platform"
        
        try:
            document = await self.arango_adapter.get_document(
                collection=collection_name,
                key=deterministic_embedding_id,
                database=database
            )
            return document
        except Exception as e:
            self.logger.error(f"Failed to get deterministic embedding: {e}")
            return None
    
    async def match_schemas(
        self,
        source_embedding_id: str,
        target_embedding_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Match schemas using deterministic embeddings.
        
        Args:
            source_embedding_id: Source deterministic embedding ID
            target_embedding_id: Target deterministic embedding ID
            context: Execution context
        
        Returns:
            Matching result with confidence scores
        """
        source_embedding = await self.get_deterministic_embedding(source_embedding_id, context)
        target_embedding = await self.get_deterministic_embedding(target_embedding_id, context)
        
        if not source_embedding or not target_embedding:
            return {
                "match": False,
                "confidence": 0.0,
                "error": "Embedding not found"
            }
        
        # Exact match via fingerprints
        source_fingerprint = source_embedding.get("schema_fingerprint")
        target_fingerprint = target_embedding.get("schema_fingerprint")
        
        exact_match = source_fingerprint == target_fingerprint
        
        # Similarity match via pattern signatures
        source_signature = source_embedding.get("pattern_signature", {})
        target_signature = target_embedding.get("pattern_signature", {})
        
        similarity_score = self._calculate_similarity(source_signature, target_signature)
        
        return {
            "match": exact_match,
            "exact_match": exact_match,
            "similarity_score": similarity_score,
            "confidence": 1.0 if exact_match else similarity_score,
            "source_fingerprint": source_fingerprint,
            "target_fingerprint": target_fingerprint
        }
    
    def _calculate_similarity(
        self,
        source_signature: Dict[str, Any],
        target_signature: Dict[str, Any]
    ) -> float:
        """Calculate similarity score between pattern signatures."""
        if not source_signature or not target_signature:
            return 0.0
        
        # Compare column types and patterns
        source_cols = set(source_signature.keys())
        target_cols = set(target_signature.keys())
        
        common_cols = source_cols & target_cols
        total_cols = source_cols | target_cols
        
        if not total_cols:
            return 0.0
        
        # Base score from column overlap
        column_overlap = len(common_cols) / len(total_cols) if total_cols else 0.0
        
        # Type matching score
        type_matches = 0
        for col in common_cols:
            source_type = source_signature[col].get("type")
            target_type = target_signature[col].get("type")
            if source_type == target_type:
                type_matches += 1
        
        type_score = type_matches / len(common_cols) if common_cols else 0.0
        
        # Combined score
        similarity = (column_overlap * 0.6) + (type_score * 0.4)
        
        return similarity
