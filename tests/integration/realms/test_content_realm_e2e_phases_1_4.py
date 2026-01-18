"""
Content Realm E2E Tests - Phases 1-4 Critical Paths

End-to-end tests for critical user journeys covering Phases 1-4 features.

WHAT (Test Role): I verify complete user journeys work end-to-end
HOW (Test Implementation): I test full workflows from ingestion to lifecycle management
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
@pytest.mark.e2e
@pytest.mark.realms
class TestContentRealmE2EPhases1_4:
    """E2E tests for critical paths covering Phases 1-4."""
    
    @pytest.fixture
    def e2e_setup(
        self,
        test_redis,
        test_arango,
        test_public_works
    ):
        """Set up infrastructure for E2E tests."""
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
    async def test_e2e_file_upload_to_archive_workflow(
        self,
        e2e_setup,
        test_data_seeder
    ):
        """E2E: Complete workflow from file upload to archive."""
        try:
            from symphainy_platform.realms.content.content_realm import ContentRealm
            
            realm = ContentRealm(public_works=e2e_setup["public_works"])
            execution_manager = e2e_setup["execution_manager"]
            state_surface = e2e_setup["state_surface"]
            
            tenant_id = "e2e_workflow_tenant"
            session_id = "e2e_workflow_session"
            
            # Step 1: Upload file
            test_content = b"E2E workflow test file content"
            file_content_hex = test_content.hex()
            
            ingest_intent = IntentFactory.create_intent(
                intent_type="ingest_file",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_e2e",
                parameters={
                    "ingestion_type": "upload",
                    "file_content": file_content_hex,
                    "ui_name": "e2e_workflow.txt",
                    "file_type": "text/plain",
                    "mime_type": "text/plain"
                }
            )
            
            ingest_result = await execution_manager.execute(ingest_intent)
            assert ingest_result is not None, "Ingest should succeed"
            assert ingest_result.success, f"Ingest should succeed: {ingest_result.error}"
            file_id = ingest_result.artifacts["file_id"]
            file_reference = ingest_result.artifacts["file_reference"]
            
            # Step 2: Retrieve metadata
            retrieve_meta_intent = IntentFactory.create_intent(
                intent_type="retrieve_file_metadata",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_e2e",
                parameters={
                    "file_id": file_id
                }
            )
            
            retrieve_meta_result = await execution_manager.execute(retrieve_meta_intent)
            assert retrieve_meta_result is not None, "Retrieve metadata should succeed"
            assert retrieve_meta_result.success, f"Retrieve metadata should succeed: {retrieve_meta_result.error}"
            assert "file_metadata" in retrieve_meta_result.artifacts, "Should return metadata"
            
            # Step 3: Update metadata
            update_intent = IntentFactory.create_intent(
                intent_type="update_file_metadata",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_e2e",
                parameters={
                    "file_id": file_id,
                    "metadata_updates": {
                        "description": "E2E workflow test file",
                        "tags": ["e2e", "test"]
                    }
                }
            )
            
            update_result = await execution_manager.execute(update_intent)
            assert update_result is not None, "Update metadata should succeed"
            
            # Step 4: Archive file
            archive_intent = IntentFactory.create_intent(
                intent_type="archive_file",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_e2e",
                parameters={
                    "file_id": file_id,
                    "reason": "E2E workflow test archive"
                }
            )
            
            archive_result = await execution_manager.execute(archive_intent)
            assert archive_result is not None, "Archive should succeed"
            assert archive_result.success, f"Archive should succeed: {archive_result.error}"
            assert archive_result.artifacts["status"] == "archived", "File should be archived"
            
            # Verify archived status
            metadata = await state_surface.get_file_metadata(file_reference)
            assert metadata is not None, "File should exist in State Surface"
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
    async def test_e2e_bulk_ingestion_with_progress_tracking(
        self,
        e2e_setup,
        test_data_seeder
    ):
        """E2E: Bulk ingestion with progress tracking and status queries."""
        try:
            from symphainy_platform.realms.content.content_realm import ContentRealm
            
            realm = ContentRealm(public_works=e2e_setup["public_works"])
            execution_manager = e2e_setup["execution_manager"]
            
            tenant_id = "e2e_bulk_tenant"
            session_id = "e2e_bulk_session"
            
            # Step 1: Prepare bulk ingestion
            files = []
            for i in range(30):
                file_content = f"E2E bulk test file {i}".encode()
                files.append({
                    "ingestion_type": "upload",
                    "file_content": file_content.hex(),
                    "ui_name": f"e2e_bulk_{i}.txt",
                    "file_type": "text/plain",
                    "mime_type": "text/plain"
                })
            
            # Step 2: Execute bulk ingestion with idempotency
            idempotency_key = "e2e_bulk_key_001"
            bulk_intent = IntentFactory.create_intent(
                intent_type="bulk_ingest_files",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_e2e",
                parameters={
                    "files": files,
                    "batch_size": 10,
                    "max_parallel": 3
                }
            )
            bulk_intent.idempotency_key = idempotency_key
            
            bulk_result = await execution_manager.execute(bulk_intent)
            assert bulk_result is not None, "Bulk ingest should succeed"
            assert bulk_result.success, f"Bulk ingest should succeed: {bulk_result.error}"
            assert bulk_result.artifacts["total_files"] == 30, "Should process 30 files"
            assert bulk_result.artifacts["success_count"] == 30, "All files should succeed"
            
            operation_id = bulk_result.artifacts.get("operation_id")
            assert operation_id is not None, "Should return operation_id"
            
            # Step 3: Query operation status
            status_intent = IntentFactory.create_intent(
                intent_type="get_operation_status",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_e2e",
                parameters={
                    "operation_id": operation_id
                }
            )
            
            status_result = await execution_manager.execute(status_intent)
            assert status_result is not None, "Status query should succeed"
            assert status_result.success, f"Status query should succeed: {status_result.error}"
            assert status_result.artifacts["status"] == "completed", "Operation should be completed"
            assert status_result.artifacts["total"] == 30, "Should have processed 30 files"
            assert status_result.artifacts["succeeded"] == 30, "Should have succeeded for 30 files"
            assert status_result.artifacts["progress_percentage"] == 100.0, "Should be 100% complete"
            
            # Step 4: Verify idempotency (execute again)
            bulk_result_2 = await execution_manager.execute(bulk_intent)
            assert bulk_result_2 is not None, "Second execution should return result"
            assert bulk_result_2.success, f"Second execution should succeed: {bulk_result_2.error}"
            assert bulk_result_2.artifacts.get("operation_id") == operation_id, "Should return same operation_id"
            
            # Cleanup
            await test_data_seeder.cleanup_test_records(
                tenant_id=tenant_id,
                session_id=session_id
            )
            
        except ImportError as e:
            pytest.skip(f"Content Realm not available: {e}")
    
    @pytest.mark.asyncio
    async def test_e2e_file_lifecycle_complete_workflow(
        self,
        e2e_setup,
        test_data_seeder
    ):
        """E2E: Complete file lifecycle workflow (upload -> validate -> archive -> restore)."""
        try:
            from symphainy_platform.realms.content.content_realm import ContentRealm
            
            realm = ContentRealm(public_works=e2e_setup["public_works"])
            execution_manager = e2e_setup["execution_manager"]
            state_surface = e2e_setup["state_surface"]
            
            tenant_id = "e2e_lifecycle_tenant"
            session_id = "e2e_lifecycle_session"
            
            # Step 1: Upload file
            test_content = b"E2E lifecycle test file content"
            file_content_hex = test_content.hex()
            
            ingest_intent = IntentFactory.create_intent(
                intent_type="ingest_file",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_e2e",
                parameters={
                    "ingestion_type": "upload",
                    "file_content": file_content_hex,
                    "ui_name": "e2e_lifecycle.txt",
                    "file_type": "text/plain",
                    "mime_type": "text/plain"
                }
            )
            
            ingest_result = await execution_manager.execute(ingest_intent)
            assert ingest_result is not None, "Ingest should succeed"
            assert ingest_result.success, f"Ingest should succeed: {ingest_result.error}"
            file_id = ingest_result.artifacts["file_id"]
            file_reference = ingest_result.artifacts["file_reference"]
            
            # Step 2: Validate file
            validate_intent = IntentFactory.create_intent(
                intent_type="validate_file",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_e2e",
                parameters={
                    "file_id": file_id,
                    "validation_rules": {
                        "max_size": 1000000,
                        "allowed_types": ["text/plain", "text"]
                    }
                }
            )
            
            validate_result = await execution_manager.execute(validate_intent)
            assert validate_result is not None, "Validate should succeed"
            assert validate_result.success, f"Validate should succeed: {validate_result.error}"
            assert validate_result.artifacts["validation_results"]["valid"], "File should be valid"
            
            # Step 3: Archive file
            archive_intent = IntentFactory.create_intent(
                intent_type="archive_file",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_e2e",
                parameters={
                    "file_id": file_id,
                    "reason": "E2E lifecycle test archive"
                }
            )
            
            archive_result = await execution_manager.execute(archive_intent)
            assert archive_result is not None, "Archive should succeed"
            assert archive_result.success, f"Archive should succeed: {archive_result.error}"
            assert archive_result.artifacts["status"] == "archived", "File should be archived"
            
            # Verify archived
            metadata = await state_surface.get_file_metadata(file_reference)
            status = metadata.get("status") or metadata.get("metadata", {}).get("status")
            assert status == "archived", "Status should be archived"
            
            # Step 4: Restore file
            restore_intent = IntentFactory.create_intent(
                intent_type="restore_file",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_e2e",
                parameters={
                    "file_id": file_id
                }
            )
            
            restore_result = await execution_manager.execute(restore_intent)
            assert restore_result is not None, "Restore should succeed"
            assert restore_result.success, f"Restore should succeed: {restore_result.error}"
            assert restore_result.artifacts["status"] == "active", "File should be active"
            
            # Verify restored
            metadata = await state_surface.get_file_metadata(file_reference)
            status = metadata.get("status") or metadata.get("metadata", {}).get("status")
            assert status == "active", "Status should be active"
            
            # Cleanup
            await test_data_seeder.cleanup_test_records(
                tenant_id=tenant_id,
                session_id=session_id
            )
            
        except ImportError as e:
            pytest.skip(f"Content Realm not available: {e}")
