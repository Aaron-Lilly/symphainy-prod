"""
End-to-End Integration Tests for Librarian

Tests the complete Librarian flow:
1. Store embeddings (with domain logic in service)
2. Get embeddings (with tenant filtering via Platform SDK)
3. Search knowledge (with coordination logic in service)
4. Access control (via Platform SDK + Librarian Primitive)

This validates that the new implementation works with equivalent or better
functionality than the old Librarian service.

NOTE: Uses mocked adapters for now (can be extended to use real ArangoDB, Meilisearch, Redis Graph).
"""

import pytest
import uuid
from typing import Dict, Any, List, Optional
from unittest.mock import AsyncMock, MagicMock

from symphainy_platform.foundations.public_works.protocols.semantic_data_protocol import SemanticDataProtocol
from symphainy_platform.foundations.public_works.protocols.knowledge_discovery_protocol import KnowledgeDiscoveryProtocol
from symphainy_platform.foundations.public_works.protocols.content_metadata_protocol import ContentMetadataProtocol
from symphainy_platform.foundations.public_works.protocols.auth_protocol import SecurityContext
from civic_systems.platform_sdk.platform_sdk import PlatformSDK
from civic_systems.smart_city.primitives.librarian.librarian_primitive import LibrarianPrimitive
from civic_systems.smart_city.registries.policy_registry import PolicyRegistry
from symphainy_platform.smart_city.services.librarian.librarian_service import LibrarianService


# ============================================================================
# Mock Adapters
# ============================================================================

class MockSemanticDataAbstraction(SemanticDataProtocol):
    """Mock Semantic Data Abstraction for testing."""
    
    def __init__(self):
        self.stored_embeddings = []
        self.stored_graphs = []
    
    async def store_semantic_embeddings(self, embedding_documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        self.stored_embeddings.extend(embedding_documents)
        return {"success": True, "stored_count": len(embedding_documents)}
    
    async def get_semantic_embeddings(self, filter_conditions: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        results = self.stored_embeddings
        if filter_conditions:
            for key, value in filter_conditions.items():
                results = [r for r in results if r.get(key) == value]
        if limit:
            results = results[:limit]
        return results
    
    async def query_by_semantic_id(self, semantic_id: str, filter_conditions: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        return [e for e in self.stored_embeddings if e.get("semantic_id") == semantic_id]
    
    async def vector_search(self, query_embedding: List[float], filter_conditions: Optional[Dict[str, Any]] = None, limit: int = 10) -> List[Dict[str, Any]]:
        results = await self.get_semantic_embeddings(filter_conditions, limit)
        return results
    
    async def store_semantic_graph(self, node_documents: List[Dict[str, Any]], edge_documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        self.stored_graphs.append({"nodes": node_documents, "edges": edge_documents})
        return {"success": True, "stored_nodes": len(node_documents), "stored_edges": len(edge_documents)}
    
    async def get_semantic_graph(self, filter_conditions: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if self.stored_graphs:
            return self.stored_graphs[0]
        return {"nodes": [], "edges": []}
    
    async def store_correlation_map(self, correlation_document: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True, "correlation_map_id": correlation_document.get("_key")}
    
    async def get_correlation_map(self, filter_conditions: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        return None
    
    async def health_check(self) -> Dict[str, Any]:
        return {"status": "healthy"}


class MockKnowledgeDiscoveryAbstraction(KnowledgeDiscoveryProtocol):
    """Mock Knowledge Discovery Abstraction for testing."""
    
    def __init__(self):
        self.search_results = []
    
    async def search_meilisearch(self, index: str, query: str, filters: Optional[Dict[str, Any]] = None, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        results = self.search_results
        if filters:
            for key, value in filters.items():
                results = [r for r in results if r.get(key) == value]
        return {
            "hits": results[:limit],
            "totalHits": len(results),
            "estimatedTotalHits": len(results)
        }
    
    async def search_meilisearch_with_facets(self, index: str, query: str, facets: List[str], limit: int = 10) -> Dict[str, Any]:
        return await self.search_meilisearch(index, query, None, limit, 0)
    
    async def get_meilisearch_analytics(self, index: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        return {"analytics": {}}
    
    async def track_meilisearch_event(self, index: str, query: str, results_count: int, user_id: Optional[str] = None) -> bool:
        return True
    
    async def search_redis_graph(self, graph: str, query: str, similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        return [{"id": "redis_1", "similarity": 0.8, "content": query}]
    
    async def get_redis_graph_neighbors(self, graph: str, node_id: str, max_depth: int = 2) -> List[Dict[str, Any]]:
        return []
    
    async def find_redis_graph_path(self, graph: str, start_id: str, end_id: str, max_paths: int = 5) -> List[List[str]]:
        return []
    
    async def get_redis_graph_stats(self, graph: str) -> Dict[str, Any]:
        return {"stats": {}}
    
    async def search_arango_semantic(self, query: str, similarity_threshold: float = 0.7, max_results: int = 10) -> List[Dict[str, Any]]:
        return [{"id": "arango_1", "similarity": 0.75, "content": query}]
    
    async def get_arango_related_documents(self, asset_id: str, relationship_types: Optional[List[str]] = None, max_depth: int = 2) -> List[Dict[str, Any]]:
        return []
    
    async def get_arango_database_statistics(self) -> Dict[str, Any]:
        return {"stats": {}}
    
    async def health_check(self) -> Dict[str, Any]:
        return {"status": "healthy"}


class MockContentMetadataAbstraction(ContentMetadataProtocol):
    """Mock Content Metadata Abstraction for testing."""
    
    def __init__(self):
        self.metadata = {}
    
    async def create_content_metadata(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        content_id = content_data.get("content_id") or content_data.get("_key")
        self.metadata[content_id] = content_data
        return content_data
    
    async def get_content_metadata(self, content_id: str) -> Optional[Dict[str, Any]]:
        return self.metadata.get(content_id)
    
    async def update_content_metadata(self, content_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        if content_id in self.metadata:
            self.metadata[content_id].update(updates)
            return self.metadata[content_id]
        return {}
    
    async def delete_content_metadata(self, content_id: str) -> bool:
        if content_id in self.metadata:
            del self.metadata[content_id]
            return True
        return False
    
    async def search_content_metadata(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        return list(self.metadata.values())


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_semantic_data_abstraction():
    """Create mock Semantic Data Abstraction."""
    return MockSemanticDataAbstraction()


@pytest.fixture
def mock_knowledge_discovery_abstraction():
    """Create mock Knowledge Discovery Abstraction."""
    return MockKnowledgeDiscoveryAbstraction()


@pytest.fixture
def mock_content_metadata_abstraction():
    """Create mock Content Metadata Abstraction."""
    return MockContentMetadataAbstraction()


@pytest.fixture
def mock_policy_registry():
    """Create mock Policy Registry."""
    registry = MagicMock(spec=PolicyRegistry)
    registry.get_policy_rules = AsyncMock(return_value={
        "required_roles": ["user"],
        "required_permissions": [],
        "restricted_queries": []
    })
    return registry


@pytest.fixture
def platform_sdk(mock_policy_registry):
    """Create Platform SDK with mocked dependencies."""
    from symphainy_platform.foundations.public_works.abstractions.auth_abstraction import AuthAbstraction
    from symphainy_platform.foundations.public_works.abstractions.tenant_abstraction import TenantAbstraction
    from symphainy_platform.foundations.public_works.abstractions.authorization_abstraction import AuthorizationAbstraction
    
    # Create minimal mocks for Platform SDK
    mock_auth = MagicMock(spec=AuthAbstraction)
    mock_tenant = MagicMock(spec=TenantAbstraction)
    mock_authz = MagicMock(spec=AuthorizationAbstraction)
    
    return PlatformSDK(
        auth_abstraction=mock_auth,
        tenant_abstraction=mock_tenant,
        authorization_abstraction=mock_authz,
        file_management_abstraction=None,
        policy_registry=mock_policy_registry
    )


@pytest.fixture
def librarian_primitive():
    """Create Librarian Primitive."""
    return LibrarianPrimitive()


@pytest.fixture
def librarian_service(
    mock_semantic_data_abstraction,
    mock_knowledge_discovery_abstraction,
    mock_content_metadata_abstraction,
    platform_sdk,
    librarian_primitive
):
    """Create Librarian Service with mocked dependencies."""
    return LibrarianService(
        semantic_data_abstraction=mock_semantic_data_abstraction,
        knowledge_discovery_abstraction=mock_knowledge_discovery_abstraction,
        content_metadata_abstraction=mock_content_metadata_abstraction,
        platform_sdk=platform_sdk,
        librarian_primitive=librarian_primitive
    )


@pytest.fixture
def test_security_context():
    """Create test security context."""
    return SecurityContext(
        user_id="test_user_123",
        tenant_id="test_tenant_456",
        email="test@example.com",
        roles=["user"],
        permissions=["knowledge_management:read", "knowledge_management:write"],
        origin="test"
    )


# ============================================================================
# Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.librarian
async def test_store_embeddings_success(
    librarian_service,
    mock_semantic_data_abstraction,
    mock_content_metadata_abstraction,
    test_security_context
):
    """Test storing embeddings successfully."""
    content_id = str(uuid.uuid4())
    file_id = str(uuid.uuid4())
    
    # Create content metadata first (so it can be updated)
    await mock_content_metadata_abstraction.create_content_metadata({
        "content_id": content_id,
        "file_uuid": file_id,
        "has_embeddings": False,
        "embedding_count": 0
    })
    
    embeddings = [
        {
            "column_name": "customer_id",
            "metadata_embedding": [0.1, 0.2, 0.3],
            "meaning_embedding": [0.4, 0.5, 0.6],
            "data_type": "string",
            "semantic_meaning": "Customer identifier"
        },
        {
            "column_name": "order_date",
            "metadata_embedding": [0.7, 0.8, 0.9],
            "meaning_embedding": [0.1, 0.2, 0.3],
            "data_type": "date",
            "semantic_meaning": "Order date"
        }
    ]
    
    result = await librarian_service.store_embeddings(
        content_id=content_id,
        file_id=file_id,
        embeddings=embeddings,
        security_context=test_security_context
    )
    
    assert result["success"] is True
    assert result["content_id"] == content_id
    assert result["file_id"] == file_id
    assert result["stored_count"] == 2
    
    # Verify embeddings were stored
    assert len(mock_semantic_data_abstraction.stored_embeddings) == 2
    
    # Verify content metadata was updated
    metadata = await mock_content_metadata_abstraction.get_content_metadata(content_id)
    assert metadata is not None
    assert metadata.get("has_embeddings") is True
    assert metadata.get("embedding_count") == 2


@pytest.mark.asyncio
@pytest.mark.librarian
async def test_get_embeddings_with_tenant_filtering(
    librarian_service,
    mock_semantic_data_abstraction,
    test_security_context
):
    """Test getting embeddings with tenant filtering."""
    content_id = str(uuid.uuid4())
    file_id = str(uuid.uuid4())
    
    # Store embeddings for tenant_1
    embeddings = [
        {
            "column_name": "test_column",
            "metadata_embedding": [0.1, 0.2, 0.3],
            "tenant_id": "test_tenant_456"  # Same tenant as test_security_context
        }
    ]
    
    await librarian_service.store_embeddings(
        content_id=content_id,
        file_id=file_id,
        embeddings=embeddings,
        security_context=test_security_context
    )
    
    # Get embeddings (should only return tenant's embeddings)
    results = await librarian_service.get_embeddings(
        security_context=test_security_context,
        content_id=content_id
    )
    
    assert len(results) == 1
    assert results[0]["tenant_id"] == "test_tenant_456"


@pytest.mark.asyncio
@pytest.mark.librarian
async def test_search_knowledge_hybrid(
    librarian_service,
    mock_knowledge_discovery_abstraction,
    test_security_context
):
    """Test hybrid search coordination."""
    # Setup mock search results
    mock_knowledge_discovery_abstraction.search_results = [
        {"id": "result_1", "title": "Test Document 1"},
        {"id": "result_2", "title": "Test Document 2"}
    ]
    
    result = await librarian_service.search_knowledge(
        query="test query",
        security_context=test_security_context,
        search_mode="hybrid",
        limit=10
    )
    
    assert result["status"] == "success"
    assert "results" in result
    assert len(result["results"]) > 0  # Should have merged results from multiple backends


@pytest.mark.asyncio
@pytest.mark.librarian
async def test_search_access_denied(
    librarian_service,
    test_security_context
):
    """Test search access denied by policy."""
    # Create security context without required permissions
    restricted_context = SecurityContext(
        user_id="restricted_user",
        tenant_id="test_tenant_456",
        email="restricted@example.com",
        roles=[],  # No roles
        permissions=[],  # No permissions
        origin="test"
    )
    
    # Mock policy registry to deny access
    librarian_service.platform_sdk.policy_registry.get_policy_rules = AsyncMock(return_value={
        "required_roles": ["admin"],  # User doesn't have admin role
        "required_permissions": [],
        "restricted_queries": []
    })
    
    with pytest.raises(PermissionError, match="Access denied"):
        await librarian_service.search_knowledge(
            query="test query",
            security_context=restricted_context
        )


@pytest.mark.asyncio
@pytest.mark.librarian
async def test_knowledge_access_denied(
    librarian_service,
    test_security_context
):
    """Test knowledge access denied by policy."""
    # Create security context without required permissions
    restricted_context = SecurityContext(
        user_id="restricted_user",
        tenant_id="test_tenant_456",
        email="restricted@example.com",
        roles=[],  # No roles
        permissions=[],  # No permissions
        origin="test"
    )
    
    # Mock policy registry to deny access
    librarian_service.platform_sdk.policy_registry.get_policy_rules = AsyncMock(return_value={
        "required_roles": ["admin"],  # User doesn't have admin role
        "required_permissions": [],
        "restricted_resources": []
    })
    
    with pytest.raises(PermissionError, match="Access denied"):
        await librarian_service.get_embeddings(
            content_id="test_content",
            security_context=restricted_context
        )


@pytest.mark.asyncio
@pytest.mark.librarian
async def test_store_embeddings_validation(
    librarian_service,
    test_security_context
):
    """Test embedding validation (domain logic)."""
    content_id = str(uuid.uuid4())
    file_id = str(uuid.uuid4())
    
    # Invalid embedding (missing required fields)
    invalid_embeddings = [
        {
            "column_name": "test_column"
            # Missing embedding vectors
        }
    ]
    
    with pytest.raises(ValueError, match="must have at least one embedding vector"):
        await librarian_service.store_embeddings(
            content_id=content_id,
            file_id=file_id,
            embeddings=invalid_embeddings,
            security_context=test_security_context
        )


@pytest.mark.asyncio
@pytest.mark.librarian
async def test_search_result_merging(
    librarian_service,
    mock_knowledge_discovery_abstraction,
    test_security_context
):
    """Test search result merging (domain logic)."""
    # Setup mock results from different backends
    mock_knowledge_discovery_abstraction.search_results = [
        {"id": "meilisearch_1", "title": "Meilisearch Result"}
    ]
    
    # Mock Redis Graph and ArangoDB results
    original_redis_search = mock_knowledge_discovery_abstraction.search_redis_graph
    original_arango_search = mock_knowledge_discovery_abstraction.search_arango_semantic
    
    async def mock_redis_search(*args, **kwargs):
        return [{"id": "redis_1", "similarity": 0.8, "title": "Redis Result"}]
    
    async def mock_arango_search(*args, **kwargs):
        return [{"id": "arango_1", "similarity": 0.75, "title": "Arango Result"}]
    
    mock_knowledge_discovery_abstraction.search_redis_graph = mock_redis_search
    mock_knowledge_discovery_abstraction.search_arango_semantic = mock_arango_search
    
    result = await librarian_service.search_knowledge(
        query="test query",
        security_context=test_security_context,
        search_mode="hybrid"
    )
    
    # Should have merged results from all backends
    assert result["status"] == "success"
    assert len(result["results"]) >= 1  # At least one result from merging
    
    # Restore original methods
    mock_knowledge_discovery_abstraction.search_redis_graph = original_redis_search
    mock_knowledge_discovery_abstraction.search_arango_semantic = original_arango_search
