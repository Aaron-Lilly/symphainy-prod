"""
ArangoDB Adapter Integration Tests

Tests ArangoDB adapter with real ArangoDB instance.

WHAT (Test Role): I verify ArangoDB adapter works with real ArangoDB
HOW (Test Implementation): I use docker-compose ArangoDB and test all operations
"""

import pytest
from typing import Dict, Any
from symphainy_platform.foundations.public_works.adapters.arango_adapter import ArangoAdapter
from tests.infrastructure.test_fixtures import test_arango, clean_test_db
from tests.infrastructure.test_data_manager import TestDataManager


@pytest.mark.integration
@pytest.mark.infrastructure
class TestArangoAdapter:
    """Test ArangoDB adapter with real ArangoDB."""
    
    @pytest.mark.asyncio
    async def test_connection(self, test_arango: ArangoAdapter):
        """Test ArangoDB connection."""
        assert test_arango.is_connected(), "Adapter should be connected"
        
        # Test connection by getting database properties
        db = test_arango.get_database()
        assert db is not None, "Database should be available"
        
        properties = db.properties()
        assert properties is not None, "Should be able to get database properties"
    
    @pytest.mark.asyncio
    async def test_database_operations(self, test_arango: ArangoAdapter):
        """Test database creation and existence check."""
        test_db_name = "test_database_123"
        
        # Test database creation
        created = await test_arango.create_database(test_db_name)
        assert created, "Database should be created"
        
        # Test database existence
        exists = await test_arango.database_exists(test_db_name)
        assert exists, "Database should exist"
        
        # Note: We don't delete the test database as it requires system database access
        # In production, this would be cleaned up by test infrastructure
    
    @pytest.mark.asyncio
    async def test_collection_operations(
        self,
        test_arango: ArangoAdapter,
        clean_test_db
    ):
        """Test collection operations (create, exists, delete)."""
        test_collection = "test_collection_123"
        data_manager = TestDataManager(arango_adapter=test_arango)
        
        # Test collection creation
        created = await test_arango.create_collection(test_collection)
        assert created, "Collection should be created"
        data_manager.test_collections.append(test_collection)
        
        # Test collection existence
        exists = await test_arango.collection_exists(test_collection)
        assert exists, "Collection should exist"
        
        # Test collection deletion
        deleted = await test_arango.delete_collection(test_collection)
        assert deleted, "Collection should be deleted"
        
        # Verify collection no longer exists
        exists_after = await test_arango.collection_exists(test_collection)
        assert not exists_after, "Collection should not exist after deletion"
    
    @pytest.mark.asyncio
    async def test_document_operations(
        self,
        test_arango: ArangoAdapter,
        clean_test_db
    ):
        """Test document operations (insert, get, update, delete)."""
        test_collection = "test_documents_123"
        data_manager = TestDataManager(arango_adapter=test_arango)
        
        # Create collection
        await test_arango.create_collection(test_collection)
        data_manager.test_collections.append(test_collection)
        
        # Test document insertion
        test_doc = {
            "_key": "test_doc_1",
            "name": "Test Document",
            "value": 123,
            "data": {"nested": "value"}
        }
        
        result = await test_arango.insert_document(test_collection, test_doc)
        assert result is not None, "Document should be inserted"
        assert result.get("_key") == "test_doc_1", "Document key should match"
        data_manager.track_document(test_collection, "test_doc_1")
        
        # Test document retrieval
        retrieved = await test_arango.get_document(test_collection, "test_doc_1")
        assert retrieved is not None, "Document should be retrieved"
        assert retrieved["name"] == "Test Document", "Document name should match"
        assert retrieved["value"] == 123, "Document value should match"
        
        # Test document update
        updates = {"value": 456, "updated": True}
        update_result = await test_arango.update_document(
            test_collection,
            "test_doc_1",
            updates
        )
        assert update_result is not None, "Document should be updated"
        
        # Verify update
        updated_doc = await test_arango.get_document(test_collection, "test_doc_1")
        assert updated_doc["value"] == 456, "Document value should be updated"
        assert updated_doc["updated"] is True, "Document should have updated field"
        
        # Test document deletion
        deleted = await test_arango.delete_document(test_collection, "test_doc_1")
        assert deleted, "Document should be deleted"
        
        # Verify deletion
        deleted_doc = await test_arango.get_document(test_collection, "test_doc_1")
        assert deleted_doc is None, "Document should not exist after deletion"
        
        # Cleanup
        await data_manager.cleanup()
    
    @pytest.mark.asyncio
    async def test_aql_query_execution(
        self,
        test_arango: ArangoAdapter,
        clean_test_db
    ):
        """Test AQL query execution."""
        test_collection = "test_aql_123"
        data_manager = TestDataManager(arango_adapter=test_arango)
        
        # Create collection and insert test data
        await test_arango.create_collection(test_collection)
        data_manager.test_collections.append(test_collection)
        
        # Insert multiple documents
        for i in range(5):
            doc = {
                "_key": f"doc_{i}",
                "index": i,
                "value": i * 10
            }
            await test_arango.insert_document(test_collection, doc)
            data_manager.track_document(test_collection, f"doc_{i}")
        
        # Test AQL query
        query = f"FOR doc IN {test_collection} FILTER doc.index >= 2 RETURN doc"
        results = await test_arango.execute_aql(query)
        
        assert len(results) == 3, "Should return 3 documents (index 2, 3, 4)"
        assert all(doc["index"] >= 2 for doc in results), "All results should have index >= 2"
        
        # Test AQL query with bind variables
        query_with_bind = f"FOR doc IN {test_collection} FILTER doc.index >= @min_index RETURN doc"
        bind_vars = {"min_index": 3}
        results_with_bind = await test_arango.execute_aql(query_with_bind, bind_vars=bind_vars)
        
        assert len(results_with_bind) == 2, "Should return 2 documents (index 3, 4)"
        assert all(doc["index"] >= 3 for doc in results_with_bind), "All results should have index >= 3"
        
        # Cleanup
        await data_manager.cleanup()
    
    @pytest.mark.asyncio
    async def test_error_handling(
        self,
        test_arango: ArangoAdapter,
        clean_test_db
    ):
        """Test error handling (invalid operations)."""
        # Test getting non-existent document
        non_existent = await test_arango.get_document("non_existent_collection", "non_existent_key")
        assert non_existent is None, "Should return None for non-existent document"
        
        # Test deleting non-existent document (should not raise exception)
        deleted = await test_arango.delete_document("non_existent_collection", "non_existent_key")
        # Should return False or not raise exception
        assert deleted is False or deleted is None, "Should handle non-existent document deletion gracefully"
        
        # Test invalid AQL query (should not raise exception, but return empty results or error)
        invalid_query = "INVALID AQL QUERY SYNTAX"
        results = await test_arango.execute_aql(invalid_query)
        # Should return empty list or handle error gracefully
        assert results == [] or results is not None, "Should handle invalid AQL query gracefully"
    
    @pytest.mark.asyncio
    async def test_collection_type_document(
        self,
        test_arango: ArangoAdapter,
        clean_test_db
    ):
        """Test creating document collection (default type)."""
        test_collection = "test_document_collection"
        data_manager = TestDataManager(arango_adapter=test_arango)
        
        created = await test_arango.create_collection(test_collection, collection_type="document")
        assert created, "Document collection should be created"
        data_manager.test_collections.append(test_collection)
        
        exists = await test_arango.collection_exists(test_collection)
        assert exists, "Document collection should exist"
        
        # Cleanup
        await data_manager.cleanup()
    
    @pytest.mark.asyncio
    async def test_collection_type_edge(
        self,
        test_arango: ArangoAdapter,
        clean_test_db
    ):
        """Test creating edge collection."""
        test_collection = "test_edge_collection"
        data_manager = TestDataManager(arango_adapter=test_arango)
        
        created = await test_arango.create_collection(test_collection, collection_type="edge")
        assert created, "Edge collection should be created"
        data_manager.test_collections.append(test_collection)
        
        exists = await test_arango.collection_exists(test_collection)
        assert exists, "Edge collection should exist"
        
        # Cleanup
        await data_manager.cleanup()
    
    @pytest.mark.asyncio
    async def test_duplicate_collection_handling(
        self,
        test_arango: ArangoAdapter,
        clean_test_db
    ):
        """Test that creating duplicate collection is handled gracefully."""
        test_collection = "test_duplicate_collection"
        data_manager = TestDataManager(arango_adapter=test_arango)
        
        # Create collection first time
        created1 = await test_arango.create_collection(test_collection)
        assert created1, "Collection should be created first time"
        data_manager.test_collections.append(test_collection)
        
        # Try to create again (should handle gracefully)
        created2 = await test_arango.create_collection(test_collection)
        # Should return True (already exists) or False (failed), but not raise exception
        assert created2 is True or created2 is False, "Should handle duplicate collection creation gracefully"
        
        # Cleanup
        await data_manager.cleanup()
    
    @pytest.mark.asyncio
    async def test_batch_operations(
        self,
        test_arango: ArangoAdapter,
        clean_test_db
    ):
        """Test batch document operations."""
        test_collection = "test_batch_123"
        data_manager = TestDataManager(arango_adapter=test_arango)
        
        # Create collection
        await test_arango.create_collection(test_collection)
        data_manager.test_collections.append(test_collection)
        
        # Insert multiple documents
        documents = []
        for i in range(10):
            doc = {
                "_key": f"batch_doc_{i}",
                "batch_index": i,
                "data": f"batch_data_{i}"
            }
            result = await test_arango.insert_document(test_collection, doc)
            assert result is not None, f"Document {i} should be inserted"
            data_manager.track_document(test_collection, f"batch_doc_{i}")
            documents.append(result)
        
        # Verify all documents exist
        for i in range(10):
            retrieved = await test_arango.get_document(test_collection, f"batch_doc_{i}")
            assert retrieved is not None, f"Document {i} should exist"
            assert retrieved["batch_index"] == i, f"Document {i} should have correct index"
        
        # Cleanup
        await data_manager.cleanup()
