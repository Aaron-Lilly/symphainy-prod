"""
Content Realm Phases 1-4 Integration Tests

High-priority integration tests for Phases 1-4 features using real infrastructure.

WHAT (Test Role): I verify Phases 1-4 functionality works with real infrastructure
HOW (Test Implementation): I use docker-compose infrastructure and test realm operations
"""

import pytest
from symphainy_platform.runtime.intent_model import IntentFactory
from symphainy_platform.runtime.execution_context import ExecutionContextFactory
from symphainy_platform.foundations.public_works.abstractions.state_abstraction import StateManagementAbstraction
from symphainy_platform.runtime.state_surface import StateSurface
from symphainy_platform.runtime.wal import WriteAheadLog
from symphainy_platform.runtime.intent_registry import IntentRegistry
from symphainy_platform.runtime.execution_lifecycle_manager import ExecutionLifecycleManager
from tests.infrastructure.test_fixtures import test_redis, test_arango, test_public_works
from tests.infrastructure.test_data_fixtures import test_data_seeder


@pytest.mark.integration
@pytest.mark.infrastructure
@pytest.mark.realms
class TestContentRealmPhases1_4Integration:
    """High-priority integration tests for Phases 1-4 features."""
    
    @pytest.fixture
    def integration_setup(
        self,
        test_redis,
        test_arango,
        test_public_works
    ):
        """Set up infrastructure for integration tests."""
        state_abstraction = StateManagementAbstraction(
            redis_adapter=test_redis,
            arango_adapter=test_arango
        )
        
        # Get FileStorageAbstraction from Public Works for StateSurface
        file_storage = test_public_works.get_file_storage_abstraction() if test_public_works else None
        
        state_surface = StateSurface(
            state_abstraction=state_abstraction,
            file_storage=file_storage
        )
        wal = WriteAheadLog(redis_adapter=test_redis)
        
        intent_registry = IntentRegistry()
        
        # Register Content Realm intents
        try:
            from symphainy_platform.realms.content.content_realm import ContentRealm
            realm = ContentRealm(public_works=test_public_works)
            realm.register_intents(intent_registry)
        except ImportError:
            pass  # Will be handled in tests
        
        execution_manager = ExecutionLifecycleManager(
            intent_registry=intent_registry,
            state_surface=state_surface,
            wal=wal
        )
        
        return {
            "state_surface": state_surface,
            "wal": wal,
            "intent_registry": intent_registry,
            "execution_manager": execution_manager,
            "public_works": test_public_works
        }
    
    @pytest.mark.asyncio
    async def test_register_file_integration(
        self,
        integration_setup,
        test_data_seeder
    ):
        """High Priority: Integration test for register_file intent."""
        try:
            from symphainy_platform.realms.content.content_realm import ContentRealm
            
            realm = ContentRealm(public_works=integration_setup["public_works"])
            execution_manager = integration_setup["execution_manager"]
            state_surface = integration_setup["state_surface"]
            
            tenant_id = "integration_register_tenant"
            session_id = "integration_register_session"
            
            # First ingest a file
            test_content = b"file for registration integration test"
            file_content_hex = test_content.hex()
            
            ingest_intent = IntentFactory.create_intent(
                intent_type="ingest_file",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_integration",
                parameters={
                    "ingestion_type": "upload",
                    "file_content": file_content_hex,
                    "ui_name": "register_integration.txt",
                    "file_type": "text/plain",
                    "mime_type": "text/plain"
                }
            )
            
            ingest_result = await execution_manager.execute(ingest_intent)
            assert ingest_result is not None, "Ingest should succeed"
            assert ingest_result.success, f"Ingest should succeed: {ingest_result.error}"
            file_id = ingest_result.artifacts["file_id"]
            
            # Register file in new session
            register_intent = IntentFactory.create_intent(
                intent_type="register_file",
                tenant_id=tenant_id,
                session_id=session_id + "_new",
                solution_id="solution_integration",
                parameters={
                    "file_id": file_id,
                    "ui_name": "registered_integration.txt",
                    "file_type": "text/plain",
                    "mime_type": "text/plain"
                }
            )
            
            register_result = await execution_manager.execute(register_intent)
            assert register_result is not None, "Register should succeed"
            assert register_result.success, f"Register should succeed: {register_result.error}"
            assert register_result.artifacts["file_id"] == file_id, "Should return same file_id"
            
            # Verify file reference in State Surface
            file_reference = register_result.artifacts["file_reference"]
            metadata = await state_surface.get_file_metadata(file_reference)
            assert metadata is not None, "File should be registered in State Surface"
            
            # Cleanup
            await test_data_seeder.cleanup_test_records(
                tenant_id=tenant_id,
                session_id=session_id
            )
            
        except ImportError as e:
            pytest.skip(f"Content Realm not available: {e}")
    
    @pytest.mark.asyncio
    async def test_retrieve_file_metadata_integration(
        self,
        integration_setup,
        test_data_seeder
    ):
        """High Priority: Integration test for retrieve_file_metadata intent."""
        try:
            from symphainy_platform.realms.content.content_realm import ContentRealm
            
            realm = ContentRealm(public_works=integration_setup["public_works"])
            execution_manager = integration_setup["execution_manager"]
            
            tenant_id = "integration_retrieve_meta_tenant"
            session_id = "integration_retrieve_meta_session"
            
            # First ingest a file
            test_content = b"file for metadata retrieval integration test"
            file_content_hex = test_content.hex()
            
            ingest_intent = IntentFactory.create_intent(
                intent_type="ingest_file",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_integration",
                parameters={
                    "ingestion_type": "upload",
                    "file_content": file_content_hex,
                    "ui_name": "retrieve_meta_integration.txt",
                    "file_type": "text/plain",
                    "mime_type": "text/plain"
                }
            )
            
            ingest_result = await execution_manager.execute(ingest_intent)
            assert ingest_result is not None, "Ingest should succeed"
            assert ingest_result.success, f"Ingest should succeed: {ingest_result.error}"
            file_id = ingest_result.artifacts["file_id"]
            
            # Retrieve metadata
            retrieve_intent = IntentFactory.create_intent(
                intent_type="retrieve_file_metadata",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_integration",
                parameters={
                    "file_id": file_id
                }
            )
            
            retrieve_result = await execution_manager.execute(retrieve_intent)
            assert retrieve_result is not None, "Retrieve should succeed"
            assert retrieve_result.success, f"Retrieve should succeed: {retrieve_result.error}"
            assert "file_metadata" in retrieve_result.artifacts, "Should return file_metadata"
            assert retrieve_result.artifacts["file_metadata"] is not None, "Metadata should not be None"
            
            # Cleanup
            await test_data_seeder.cleanup_test_records(
                tenant_id=tenant_id,
                session_id=session_id
            )
            
        except ImportError as e:
            pytest.skip(f"Content Realm not available: {e}")
    
    @pytest.mark.asyncio
    async def test_retrieve_file_integration(
        self,
        integration_setup,
        test_data_seeder
    ):
        """High Priority: Integration test for retrieve_file intent."""
        try:
            from symphainy_platform.realms.content.content_realm import ContentRealm
            
            realm = ContentRealm(public_works=integration_setup["public_works"])
            execution_manager = integration_setup["execution_manager"]
            
            tenant_id = "integration_retrieve_file_tenant"
            session_id = "integration_retrieve_file_session"
            
            # First ingest a file
            original_content = b"file content for retrieval integration test"
            file_content_hex = original_content.hex()
            
            ingest_intent = IntentFactory.create_intent(
                intent_type="ingest_file",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_integration",
                parameters={
                    "ingestion_type": "upload",
                    "file_content": file_content_hex,
                    "ui_name": "retrieve_file_integration.txt",
                    "file_type": "text/plain",
                    "mime_type": "text/plain"
                }
            )
            
            ingest_result = await execution_manager.execute(ingest_intent)
            assert ingest_result is not None, "Ingest should succeed"
            assert ingest_result.success, f"Ingest should succeed: {ingest_result.error}"
            file_id = ingest_result.artifacts["file_id"]
            
            # Retrieve file with contents
            retrieve_intent = IntentFactory.create_intent(
                intent_type="retrieve_file",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_integration",
                parameters={
                    "file_id": file_id,
                    "include_contents": True
                }
            )
            
            retrieve_result = await execution_manager.execute(retrieve_intent)
            assert retrieve_result is not None, "Retrieve should succeed"
            assert retrieve_result.success, f"Retrieve should succeed: {retrieve_result.error}"
            assert "file_contents" in retrieve_result.artifacts, "Should return file_contents"
            assert retrieve_result.artifacts["file_contents"] == original_content, "Contents should match"
            
            # Cleanup
            await test_data_seeder.cleanup_test_records(
                tenant_id=tenant_id,
                session_id=session_id
            )
            
        except ImportError as e:
            pytest.skip(f"Content Realm not available: {e}")
    
    @pytest.mark.asyncio
    async def test_bulk_ingest_files_integration(
        self,
        integration_setup,
        test_data_seeder
    ):
        """High Priority: Integration test for bulk_ingest_files intent."""
        try:
            from symphainy_platform.realms.content.content_realm import ContentRealm
            
            realm = ContentRealm(public_works=integration_setup["public_works"])
            execution_manager = integration_setup["execution_manager"]
            
            tenant_id = "integration_bulk_tenant"
            session_id = "integration_bulk_session"
            
            # Prepare 15 files for bulk ingestion
            files = []
            for i in range(15):
                file_content = f"bulk integration test file {i}".encode()
                files.append({
                    "ingestion_type": "upload",
                    "file_content": file_content.hex(),
                    "ui_name": f"bulk_integration_{i}.txt",
                    "file_type": "text/plain",
                    "mime_type": "text/plain"
                })
            
            bulk_intent = IntentFactory.create_intent(
                intent_type="bulk_ingest_files",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_integration",
                parameters={
                    "files": files,
                    "batch_size": 5,
                    "max_parallel": 3
                }
            )
            
            bulk_result = await execution_manager.execute(bulk_intent)
            assert bulk_result is not None, "Bulk ingest should succeed"
            assert bulk_result.success, f"Bulk ingest should succeed: {bulk_result.error}"
            assert bulk_result.artifacts["total_files"] == 15, "Should process 15 files"
            assert bulk_result.artifacts["success_count"] == 15, "All files should succeed"
            assert len(bulk_result.artifacts["results"]) == 15, "Should return 15 results"
            
            # Verify operation_id for progress tracking
            operation_id = bulk_result.artifacts.get("operation_id")
            assert operation_id is not None, "Should return operation_id"
            
            # Cleanup
            await test_data_seeder.cleanup_test_records(
                tenant_id=tenant_id,
                session_id=session_id
            )
            
        except ImportError as e:
            pytest.skip(f"Content Realm not available: {e}")
    
    @pytest.mark.asyncio
    async def test_idempotency_integration(
        self,
        integration_setup,
        test_data_seeder
    ):
        """High Priority: Integration test for idempotency."""
        try:
            from symphainy_platform.realms.content.content_realm import ContentRealm
            
            realm = ContentRealm(public_works=integration_setup["public_works"])
            execution_manager = integration_setup["execution_manager"]
            
            tenant_id = "integration_idempotency_tenant"
            session_id = "integration_idempotency_session"
            
            # Create bulk_ingest_files intent with idempotency key
            files = [
                {
                    "ingestion_type": "upload",
                    "file_content": b"idempotency integration test".hex(),
                    "ui_name": "idempotency_integration.txt",
                    "file_type": "text/plain",
                    "mime_type": "text/plain"
                }
            ]
            
            idempotency_key = "integration_idempotency_key_001"
            bulk_intent = IntentFactory.create_intent(
                intent_type="bulk_ingest_files",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_integration",
                parameters={
                    "files": files,
                    "batch_size": 1,
                    "max_parallel": 1
                }
            )
            bulk_intent.idempotency_key = idempotency_key
            
            # Execute first time
            result1 = await execution_manager.execute(bulk_intent)
            assert result1 is not None, "First execution should succeed"
            assert result1.success, f"First execution should succeed: {result1.error}"
            operation_id_1 = result1.artifacts.get("operation_id")
            
            # Execute second time (should return previous result)
            result2 = await execution_manager.execute(bulk_intent)
            assert result2 is not None, "Second execution should return result"
            assert result2.success, f"Second execution should succeed: {result2.error}"
            operation_id_2 = result2.artifacts.get("operation_id")
            
            # Verify same operation_id (idempotent)
            assert operation_id_1 == operation_id_2, "Should return same operation_id"
            
            # Cleanup
            await test_data_seeder.cleanup_test_records(
                tenant_id=tenant_id,
                session_id=session_id
            )
            
        except ImportError as e:
            pytest.skip(f"Content Realm not available: {e}")
    
    @pytest.mark.asyncio
    async def test_progress_tracking_integration(
        self,
        integration_setup,
        test_data_seeder
    ):
        """High Priority: Integration test for progress tracking."""
        try:
            from symphainy_platform.realms.content.content_realm import ContentRealm
            
            realm = ContentRealm(public_works=integration_setup["public_works"])
            execution_manager = integration_setup["execution_manager"]
            
            tenant_id = "integration_progress_tenant"
            session_id = "integration_progress_session"
            
            # Create bulk_ingest_files intent with multiple files
            files = []
            for i in range(25):
                file_content = f"progress integration test file {i}".encode()
                files.append({
                    "ingestion_type": "upload",
                    "file_content": file_content.hex(),
                    "ui_name": f"progress_integration_{i}.txt",
                    "file_type": "text/plain",
                    "mime_type": "text/plain"
                })
            
            bulk_intent = IntentFactory.create_intent(
                intent_type="bulk_ingest_files",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_integration",
                parameters={
                    "files": files,
                    "batch_size": 5,
                    "max_parallel": 2
                }
            )
            
            # Execute bulk operation
            bulk_result = await execution_manager.execute(bulk_intent)
            assert bulk_result is not None, "Bulk ingest should succeed"
            assert bulk_result.success, f"Bulk ingest should succeed: {bulk_result.error}"
            operation_id = bulk_result.artifacts.get("operation_id")
            assert operation_id is not None, "Should return operation_id"
            
            # Query progress
            status_intent = IntentFactory.create_intent(
                intent_type="get_operation_status",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_integration",
                parameters={
                    "operation_id": operation_id
                }
            )
            
            status_result = await execution_manager.execute(status_intent)
            assert status_result is not None, "Status query should succeed"
            assert status_result.success, f"Status query should succeed: {status_result.error}"
            assert status_result.artifacts["status"] == "completed", "Operation should be completed"
            assert status_result.artifacts["total"] == 25, "Should have processed 25 files"
            assert status_result.artifacts["succeeded"] == 25, "Should have succeeded for 25 files"
            
            # Cleanup
            await test_data_seeder.cleanup_test_records(
                tenant_id=tenant_id,
                session_id=session_id
            )
            
        except ImportError as e:
            pytest.skip(f"Content Realm not available: {e}")
    
    @pytest.mark.asyncio
    async def test_archive_file_integration(
        self,
        integration_setup,
        test_data_seeder
    ):
        """High Priority: Integration test for archive_file intent."""
        try:
            from symphainy_platform.realms.content.content_realm import ContentRealm
            
            realm = ContentRealm(public_works=integration_setup["public_works"])
            execution_manager = integration_setup["execution_manager"]
            state_surface = integration_setup["state_surface"]
            
            tenant_id = "integration_archive_tenant"
            session_id = "integration_archive_session"
            
            # First ingest a file
            test_content = b"file for archive integration test"
            file_content_hex = test_content.hex()
            
            ingest_intent = IntentFactory.create_intent(
                intent_type="ingest_file",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_integration",
                parameters={
                    "ingestion_type": "upload",
                    "file_content": file_content_hex,
                    "ui_name": "archive_integration.txt",
                    "file_type": "text/plain",
                    "mime_type": "text/plain"
                }
            )
            
            ingest_result = await execution_manager.execute(ingest_intent)
            assert ingest_result is not None, "Ingest should succeed"
            assert ingest_result.success, f"Ingest should succeed: {ingest_result.error}"
            file_id = ingest_result.artifacts["file_id"]
            file_reference = ingest_result.artifacts["file_reference"]
            
            # Archive file
            archive_intent = IntentFactory.create_intent(
                intent_type="archive_file",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_integration",
                parameters={
                    "file_id": file_id,
                    "reason": "Integration test archive"
                }
            )
            
            archive_result = await execution_manager.execute(archive_intent)
            assert archive_result is not None, "Archive should succeed"
            assert archive_result.success, f"Archive should succeed: {archive_result.error}"
            assert archive_result.artifacts["status"] == "archived", "File should be archived"
            
            # Verify status in State Surface
            metadata = await state_surface.get_file_metadata(file_reference)
            assert metadata is not None, "File should still exist in State Surface"
            status = metadata.get("status") or metadata.get("metadata", {}).get("status")
            assert status == "archived", "Status should be archived"
            
            # Cleanup
            await test_data_seeder.cleanup_test_records(
                tenant_id=tenant_id,
                session_id=session_id
            )
            
        except ImportError as e:
            pytest.skip(f"Content Realm not available: {e}")
    
    @pytest.mark.asyncio
    async def test_restore_file_integration(
        self,
        integration_setup,
        test_data_seeder
    ):
        """High Priority: Integration test for restore_file intent."""
        try:
            from symphainy_platform.realms.content.content_realm import ContentRealm
            
            realm = ContentRealm(public_works=integration_setup["public_works"])
            execution_manager = integration_setup["execution_manager"]
            state_surface = integration_setup["state_surface"]
            
            tenant_id = "integration_restore_tenant"
            session_id = "integration_restore_session"
            
            # First ingest and archive a file
            test_content = b"file for restore integration test"
            file_content_hex = test_content.hex()
            
            ingest_intent = IntentFactory.create_intent(
                intent_type="ingest_file",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_integration",
                parameters={
                    "ingestion_type": "upload",
                    "file_content": file_content_hex,
                    "ui_name": "restore_integration.txt",
                    "file_type": "text/plain",
                    "mime_type": "text/plain"
                }
            )
            
            ingest_result = await execution_manager.execute(ingest_intent)
            assert ingest_result is not None, "Ingest should succeed"
            assert ingest_result.success, f"Ingest should succeed: {ingest_result.error}"
            file_id = ingest_result.artifacts["file_id"]
            file_reference = ingest_result.artifacts["file_reference"]
            
            # Archive file
            archive_intent = IntentFactory.create_intent(
                intent_type="archive_file",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_integration",
                parameters={
                    "file_id": file_id,
                    "reason": "Test archive before restore"
                }
            )
            
            archive_result = await execution_manager.execute(archive_intent)
            assert archive_result.success, f"Archive should succeed: {archive_result.error}"
            
            # Restore file
            restore_intent = IntentFactory.create_intent(
                intent_type="restore_file",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_integration",
                parameters={
                    "file_id": file_id
                }
            )
            
            restore_result = await execution_manager.execute(restore_intent)
            assert restore_result is not None, "Restore should succeed"
            assert restore_result.success, f"Restore should succeed: {restore_result.error}"
            assert restore_result.artifacts["status"] == "active", "File should be active"
            
            # Verify status in State Surface
            metadata = await state_surface.get_file_metadata(file_reference)
            assert metadata is not None, "File should exist in State Surface"
            status = metadata.get("status") or metadata.get("metadata", {}).get("status")
            assert status == "active", "Status should be active"
            
            # Cleanup
            await test_data_seeder.cleanup_test_records(
                tenant_id=tenant_id,
                session_id=session_id
            )
            
        except ImportError as e:
            pytest.skip(f"Content Realm not available: {e}")
