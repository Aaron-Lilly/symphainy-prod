"""
Phase 1 Validation - Lightweight Smoke Tests

Quick smoke tests to validate Phase 1 functionality:
- Unified ingestion (upload, EDI, API)
- File management intents (register, retrieve, list, get_by_id)

WHAT (Test Role): I verify Phase 1 functionality works
HOW (Test Implementation): I use existing fixtures and test happy paths only
"""

import pytest
from symphainy_platform.runtime.intent_model import IntentFactory
from symphainy_platform.runtime.execution_context import ExecutionContextFactory
from symphainy_platform.foundations.public_works.abstractions.state_abstraction import StateManagementAbstraction
from symphainy_platform.runtime.state_surface import StateSurface
from symphainy_platform.runtime.wal import WriteAheadLog
from tests.infrastructure.test_fixtures import test_redis, test_arango, test_public_works
from tests.infrastructure.test_data_fixtures import test_data_seeder


@pytest.mark.integration
@pytest.mark.infrastructure
@pytest.mark.realms
class TestPhase1Validation:
    """Lightweight smoke tests for Phase 1 functionality."""
    
    @pytest.fixture
    def phase1_setup(self, test_redis, test_arango, test_public_works):
        """Set up minimal infrastructure for Phase 1 tests."""
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
        
        return {
            "state_surface": state_surface,
            "wal": wal,
            "public_works": test_public_works
        }
    
    @pytest.mark.asyncio
    async def test_unified_ingestion_upload(
        self,
        phase1_setup,
        test_data_seeder
    ):
        """Smoke test: Verify ingest_file with ingestion_type='upload' works."""
        try:
            from symphainy_platform.realms.content.content_realm import ContentRealm
            
            realm = ContentRealm(public_works=phase1_setup["public_works"])
            state_surface = phase1_setup["state_surface"]
            wal = phase1_setup["wal"]
            
            # Create a small test file
            test_content = b"test file content for unified ingestion"
            file_content_hex = test_content.hex()
            
            # Create ingest_file intent with ingestion_type="upload"
            intent = IntentFactory.create_intent(
                intent_type="ingest_file",
                tenant_id="phase1_test_tenant",
                session_id="phase1_test_session",
                solution_id="solution_phase1",
                parameters={
                    "ingestion_type": "upload",
                    "file_content": file_content_hex,
                    "ui_name": "test_upload.txt",
                    "file_type": "text/plain",
                    "mime_type": "text/plain"
                }
            )
            
            context = ExecutionContextFactory.create_context(
                intent=intent,
                state_surface=state_surface,
                wal=wal
            )
            
            # Execute intent
            result = await realm.handle_intent(intent, context)
            
            # Verify result structure
            assert result is not None, "Should return result"
            assert isinstance(result, dict), "Result should be a dictionary"
            assert "artifacts" in result, "Should contain artifacts"
            
            artifacts = result["artifacts"]
            assert "file_id" in artifacts, "Should return file_id"
            assert "file_reference" in artifacts, "Should return file_reference"
            assert artifacts.get("ingestion_type") == "upload", "Should indicate upload ingestion"
            
            # Cleanup
            await test_data_seeder.cleanup_test_records(
                tenant_id="phase1_test_tenant",
                session_id="phase1_test_session"
            )
            
        except ImportError as e:
            pytest.skip(f"Content Realm not available: {e}")
        except Exception as e:
            pytest.fail(f"Unified ingestion upload failed: {e}")
    
    @pytest.mark.asyncio
    async def test_register_file(
        self,
        phase1_setup,
        test_data_seeder
    ):
        """Smoke test: Verify register_file intent works."""
        try:
            from symphainy_platform.realms.content.content_realm import ContentRealm
            
            realm = ContentRealm(public_works=phase1_setup["public_works"])
            state_surface = phase1_setup["state_surface"]
            wal = phase1_setup["wal"]
            
            # Upload a test file first (use existing sample.txt)
            blob_path = await test_data_seeder.upload_test_file(
                "sample.txt",
                test_id="phase1_register_test"
            )
            
            if not blob_path:
                pytest.skip("Failed to upload test file")
            
            # Seed source file record
            file_id = await test_data_seeder.seed_source_file(
                file_id="phase1_register_001",
                gcs_blob_path=blob_path,
                tenant_id="phase1_register_tenant",
                session_id="phase1_register_session",
                file_name="sample.txt",
                file_type="text/plain"
            )
            
            # Create register_file intent
            intent = IntentFactory.create_intent(
                intent_type="register_file",
                tenant_id="phase1_register_tenant",
                session_id="phase1_register_session",
                solution_id="solution_register",
                parameters={
                    "file_id": file_id,
                    "ui_name": "test_register.txt",
                    "file_type": "text/plain",
                    "mime_type": "text/plain"
                }
            )
            
            context = ExecutionContextFactory.create_context(
                intent=intent,
                state_surface=state_surface,
                wal=wal
            )
            
            # Execute intent
            result = await realm.handle_intent(intent, context)
            
            # Verify result
            assert result is not None, "Should return result"
            assert "artifacts" in result, "Should contain artifacts"
            assert "file_id" in result["artifacts"], "Should return file_id"
            assert "file_reference" in result["artifacts"], "Should return file_reference"
            
            # Cleanup
            await test_data_seeder.cleanup_test_files("phase1_register_test")
            await test_data_seeder.cleanup_test_records(
                tenant_id="phase1_register_tenant",
                session_id="phase1_register_session"
            )
            
        except ImportError as e:
            pytest.skip(f"Content Realm not available: {e}")
        except Exception as e:
            pytest.fail(f"Register file failed: {e}")
    
    @pytest.mark.asyncio
    async def test_retrieve_file_metadata(
        self,
        phase1_setup,
        test_data_seeder
    ):
        """Smoke test: Verify retrieve_file_metadata intent works."""
        try:
            from symphainy_platform.realms.content.content_realm import ContentRealm
            
            realm = ContentRealm(public_works=phase1_setup["public_works"])
            state_surface = phase1_setup["state_surface"]
            wal = phase1_setup["wal"]
            
            # Upload and seed a test file
            blob_path = await test_data_seeder.upload_test_file(
                "sample.txt",
                test_id="phase1_metadata_test"
            )
            
            if not blob_path:
                pytest.skip("Failed to upload test file")
            
            file_id = await test_data_seeder.seed_source_file(
                file_id="phase1_metadata_001",
                gcs_blob_path=blob_path,
                tenant_id="phase1_metadata_tenant",
                session_id="phase1_metadata_session",
                file_name="sample.txt",
                file_type="text/plain"
            )
            
            # Create retrieve_file_metadata intent
            intent = IntentFactory.create_intent(
                intent_type="retrieve_file_metadata",
                tenant_id="phase1_metadata_tenant",
                session_id="phase1_metadata_session",
                solution_id="solution_metadata",
                parameters={
                    "file_id": file_id
                }
            )
            
            context = ExecutionContextFactory.create_context(
                intent=intent,
                state_surface=state_surface,
                wal=wal
            )
            
            # Execute intent
            result = await realm.handle_intent(intent, context)
            
            # Verify result
            assert result is not None, "Should return result"
            assert "artifacts" in result, "Should contain artifacts"
            assert "file_metadata" in result["artifacts"], "Should return file_metadata"
            
            # Cleanup
            await test_data_seeder.cleanup_test_files("phase1_metadata_test")
            await test_data_seeder.cleanup_test_records(
                tenant_id="phase1_metadata_tenant",
                session_id="phase1_metadata_session"
            )
            
        except ImportError as e:
            pytest.skip(f"Content Realm not available: {e}")
        except Exception as e:
            pytest.fail(f"Retrieve file metadata failed: {e}")
    
    @pytest.mark.asyncio
    async def test_list_files(
        self,
        phase1_setup,
        test_data_seeder
    ):
        """Smoke test: Verify list_files intent works."""
        try:
            from symphainy_platform.realms.content.content_realm import ContentRealm
            
            realm = ContentRealm(public_works=phase1_setup["public_works"])
            state_surface = phase1_setup["state_surface"]
            wal = phase1_setup["wal"]
            
            # Upload and seed a test file
            blob_path = await test_data_seeder.upload_test_file(
                "sample.txt",
                test_id="phase1_list_test"
            )
            
            if not blob_path:
                pytest.skip("Failed to upload test file")
            
            file_id = await test_data_seeder.seed_source_file(
                file_id="phase1_list_001",
                gcs_blob_path=blob_path,
                tenant_id="phase1_list_tenant",
                session_id="phase1_list_session",
                file_name="sample.txt",
                file_type="text/plain"
            )
            
            # Create list_files intent
            intent = IntentFactory.create_intent(
                intent_type="list_files",
                tenant_id="phase1_list_tenant",
                session_id="phase1_list_session",
                solution_id="solution_list",
                parameters={}
            )
            
            context = ExecutionContextFactory.create_context(
                intent=intent,
                state_surface=state_surface,
                wal=wal
            )
            
            # Execute intent
            result = await realm.handle_intent(intent, context)
            
            # Verify result
            assert result is not None, "Should return result"
            assert "artifacts" in result, "Should contain artifacts"
            assert "files" in result["artifacts"], "Should return files list"
            assert isinstance(result["artifacts"]["files"], list), "Files should be a list"
            
            # Cleanup
            await test_data_seeder.cleanup_test_files("phase1_list_test")
            await test_data_seeder.cleanup_test_records(
                tenant_id="phase1_list_tenant",
                session_id="phase1_list_session"
            )
            
        except ImportError as e:
            pytest.skip(f"Content Realm not available: {e}")
        except Exception as e:
            pytest.fail(f"List files failed: {e}")
    
    @pytest.mark.asyncio
    async def test_file_management_flow(
        self,
        phase1_setup,
        test_data_seeder
    ):
        """Smoke test: Quick end-to-end flow (ingest → register → retrieve → list)."""
        try:
            from symphainy_platform.realms.content.content_realm import ContentRealm
            
            realm = ContentRealm(public_works=phase1_setup["public_works"])
            state_surface = phase1_setup["state_surface"]
            wal = phase1_setup["wal"]
            
            tenant_id = "phase1_flow_tenant"
            session_id = "phase1_flow_session"
            
            # Step 1: Ingest file via unified ingestion
            test_content = b"test file content for flow"
            file_content_hex = test_content.hex()
            
            ingest_intent = IntentFactory.create_intent(
                intent_type="ingest_file",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_flow",
                parameters={
                    "ingestion_type": "upload",
                    "file_content": file_content_hex,
                    "ui_name": "flow_test.txt",
                    "file_type": "text/plain",
                    "mime_type": "text/plain"
                }
            )
            
            ingest_context = ExecutionContextFactory.create_context(
                intent=ingest_intent,
                state_surface=state_surface,
                wal=wal
            )
            
            ingest_result = await realm.handle_intent(ingest_intent, ingest_context)
            assert ingest_result is not None, "Ingest should succeed"
            file_id = ingest_result["artifacts"]["file_id"]
            
            # Step 2: Retrieve metadata
            metadata_intent = IntentFactory.create_intent(
                intent_type="retrieve_file_metadata",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_flow",
                parameters={"file_id": file_id}
            )
            
            metadata_context = ExecutionContextFactory.create_context(
                intent=metadata_intent,
                state_surface=state_surface,
                wal=wal
            )
            
            metadata_result = await realm.handle_intent(metadata_intent, metadata_context)
            assert metadata_result is not None, "Retrieve metadata should succeed"
            
            # Step 3: List files
            list_intent = IntentFactory.create_intent(
                intent_type="list_files",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_flow",
                parameters={}
            )
            
            list_context = ExecutionContextFactory.create_context(
                intent=list_intent,
                state_surface=state_surface,
                wal=wal
            )
            
            list_result = await realm.handle_intent(list_intent, list_context)
            assert list_result is not None, "List files should succeed"
            assert len(list_result["artifacts"]["files"]) > 0, "Should find at least one file"
            
            # Cleanup
            await test_data_seeder.cleanup_test_records(
                tenant_id=tenant_id,
                session_id=session_id
            )
            
        except ImportError as e:
            pytest.skip(f"Content Realm not available: {e}")
        except Exception as e:
            pytest.fail(f"File management flow failed: {e}")
    
    @pytest.mark.asyncio
    async def test_bulk_ingest_files(
        self,
        phase1_setup,
        test_data_seeder
    ):
        """Smoke test: Verify bulk_ingest_files works with multiple files."""
        try:
            from symphainy_platform.realms.content.content_realm import ContentRealm
            
            realm = ContentRealm(public_works=phase1_setup["public_works"])
            state_surface = phase1_setup["state_surface"]
            wal = phase1_setup["wal"]
            
            # Create multiple test files
            files = [
                {
                    "ingestion_type": "upload",
                    "file_content": b"test file 1 content".hex(),
                    "ui_name": "bulk_test_1.txt",
                    "file_type": "text/plain",
                    "mime_type": "text/plain"
                },
                {
                    "ingestion_type": "upload",
                    "file_content": b"test file 2 content".hex(),
                    "ui_name": "bulk_test_2.txt",
                    "file_type": "text/plain",
                    "mime_type": "text/plain"
                }
            ]
            
            # Create bulk_ingest_files intent
            intent = IntentFactory.create_intent(
                intent_type="bulk_ingest_files",
                tenant_id="phase1_bulk_tenant",
                session_id="phase1_bulk_session",
                solution_id="solution_bulk",
                parameters={
                    "files": files,
                    "batch_size": 2,
                    "max_parallel": 2
                }
            )
            
            context = ExecutionContextFactory.create_context(
                intent=intent,
                state_surface=state_surface,
                wal=wal
            )
            
            # Execute intent
            result = await realm.handle_intent(intent, context)
            
            # Verify result
            assert result is not None, "Should return result"
            assert "artifacts" in result, "Should contain artifacts"
            assert result["artifacts"]["total_files"] == 2, "Should process 2 files"
            assert result["artifacts"]["success_count"] == 2, "Should succeed for both files"
            assert len(result["artifacts"]["results"]) == 2, "Should have 2 results"
            
            # Cleanup
            await test_data_seeder.cleanup_test_records(
                tenant_id="phase1_bulk_tenant",
                session_id="phase1_bulk_session"
            )
            
        except ImportError as e:
            pytest.skip(f"Content Realm not available: {e}")
        except Exception as e:
            pytest.fail(f"Bulk ingest files failed: {e}")
    
    @pytest.mark.asyncio
    async def test_phase2_bulk_operations_smoke(
        self,
        phase1_setup,
        test_data_seeder
    ):
        """Smoke test: Quick validation of Phase 2 bulk operations."""
        try:
            from symphainy_platform.realms.content.content_realm import ContentRealm
            
            realm = ContentRealm(public_works=phase1_setup["public_works"])
            state_surface = phase1_setup["state_surface"]
            wal = phase1_setup["wal"]
            
            tenant_id = "phase2_bulk_tenant"
            session_id = "phase2_bulk_session"
            
            # Step 1: Bulk ingest 3 files
            files = [
                {
                    "ingestion_type": "upload",
                    "file_content": b"bulk test file 1".hex(),
                    "ui_name": "bulk_1.txt",
                    "file_type": "text/plain",
                    "mime_type": "text/plain"
                },
                {
                    "ingestion_type": "upload",
                    "file_content": b"bulk test file 2".hex(),
                    "ui_name": "bulk_2.txt",
                    "file_type": "text/plain",
                    "mime_type": "text/plain"
                },
                {
                    "ingestion_type": "upload",
                    "file_content": b"bulk test file 3".hex(),
                    "ui_name": "bulk_3.txt",
                    "file_type": "text/plain",
                    "mime_type": "text/plain"
                }
            ]
            
            bulk_ingest_intent = IntentFactory.create_intent(
                intent_type="bulk_ingest_files",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_bulk_smoke",
                parameters={
                    "files": files,
                    "batch_size": 2,
                    "max_parallel": 2
                }
            )
            
            bulk_ingest_context = ExecutionContextFactory.create_context(
                intent=bulk_ingest_intent,
                state_surface=state_surface,
                wal=wal
            )
            
            bulk_ingest_result = await realm.handle_intent(bulk_ingest_intent, bulk_ingest_context)
            
            # Verify bulk ingestion succeeded
            assert bulk_ingest_result is not None, "Bulk ingest should return result"
            assert bulk_ingest_result["artifacts"]["total_files"] == 3, "Should process 3 files"
            assert bulk_ingest_result["artifacts"]["success_count"] == 3, "All 3 files should succeed"
            
            # Extract file IDs for next step
            file_ids = [r["file_id"] for r in bulk_ingest_result["artifacts"]["results"]]
            assert len(file_ids) == 3, "Should have 3 file IDs"
            
            # Step 2: Verify bulk_parse_files intent exists (don't actually parse - would need real files)
            # Just verify the intent is declared
            declared_intents = realm.declare_intents()
            assert "bulk_parse_files" in declared_intents, "bulk_parse_files should be declared"
            assert "bulk_extract_embeddings" in declared_intents, "bulk_extract_embeddings should be declared"
            assert "bulk_interpret_data" in declared_intents, "bulk_interpret_data should be declared"
            
            # Cleanup
            await test_data_seeder.cleanup_test_records(
                tenant_id=tenant_id,
                session_id=session_id
            )
            
        except ImportError as e:
            pytest.skip(f"Content Realm not available: {e}")
        except Exception as e:
            pytest.fail(f"Phase 2 bulk operations smoke test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_phase3_idempotency_and_progress(
        self,
        phase1_setup,
        test_data_seeder
    ):
        """Smoke test: Verify Phase 3 idempotency and progress tracking."""
        try:
            from symphainy_platform.realms.content.content_realm import ContentRealm
            
            realm = ContentRealm(public_works=phase1_setup["public_works"])
            state_surface = phase1_setup["state_surface"]
            wal = phase1_setup["wal"]
            
            tenant_id = "phase3_test_tenant"
            session_id = "phase3_test_session"
            
            # Create a test file for bulk ingestion
            files = [
                {
                    "ingestion_type": "upload",
                    "file_content": b"phase3 test file".hex(),
                    "ui_name": "phase3_test.txt",
                    "file_type": "text/plain",
                    "mime_type": "text/plain"
                }
            ]
            
            # Create bulk_ingest_files intent with idempotency key
            idempotency_key = "phase3_test_key_001"
            bulk_intent = IntentFactory.create_intent(
                intent_type="bulk_ingest_files",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_phase3",
                parameters={
                    "files": files,
                    "batch_size": 1,
                    "max_parallel": 1
                }
            )
            bulk_intent.idempotency_key = idempotency_key
            
            bulk_context = ExecutionContextFactory.create_context(
                intent=bulk_intent,
                state_surface=state_surface,
                wal=wal
            )
            
            # Execute first time
            result1 = await realm.handle_intent(bulk_intent, bulk_context)
            assert result1 is not None, "First execution should succeed"
            operation_id = result1["artifacts"].get("operation_id")
            assert operation_id is not None, "Should return operation_id"
            
            # Execute again with same idempotency key (should return previous result)
            result2 = await realm.handle_intent(bulk_intent, bulk_context)
            assert result2 is not None, "Second execution should return result"
            # Should have same operation_id (idempotent)
            assert result2["artifacts"].get("operation_id") == operation_id, "Should return same operation_id"
            
            # Check operation status
            status_intent = IntentFactory.create_intent(
                intent_type="get_operation_status",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_phase3",
                parameters={
                    "operation_id": operation_id
                }
            )
            
            status_context = ExecutionContextFactory.create_context(
                intent=status_intent,
                state_surface=state_surface,
                wal=wal
            )
            
            status_result = await realm.handle_intent(status_intent, status_context)
            assert status_result is not None, "Status query should succeed"
            assert status_result["artifacts"]["status"] == "completed", "Operation should be completed"
            assert status_result["artifacts"]["total"] == 1, "Should have processed 1 file"
            assert status_result["artifacts"]["succeeded"] == 1, "Should have succeeded for 1 file"
            
            # Cleanup
            await test_data_seeder.cleanup_test_records(
                tenant_id=tenant_id,
                session_id=session_id
            )
            
        except ImportError as e:
            pytest.skip(f"Content Realm not available: {e}")
        except Exception as e:
            pytest.fail(f"Phase 3 idempotency and progress test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_phase4_file_lifecycle_smoke(
        self,
        phase1_setup,
        test_data_seeder
    ):
        """Smoke test: Verify Phase 4 file lifecycle operations."""
        try:
            from symphainy_platform.realms.content.content_realm import ContentRealm
            
            realm = ContentRealm(public_works=phase1_setup["public_works"])
            state_surface = phase1_setup["state_surface"]
            wal = phase1_setup["wal"]
            
            tenant_id = "phase4_test_tenant"
            session_id = "phase4_test_session"
            
            # Step 1: Ingest a file first
            test_content = b"phase4 lifecycle test file"
            file_content_hex = test_content.hex()
            
            ingest_intent = IntentFactory.create_intent(
                intent_type="ingest_file",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_phase4",
                parameters={
                    "ingestion_type": "upload",
                    "file_content": file_content_hex,
                    "ui_name": "phase4_lifecycle.txt",
                    "file_type": "text/plain",
                    "mime_type": "text/plain"
                }
            )
            
            ingest_context = ExecutionContextFactory.create_context(
                intent=ingest_intent,
                state_surface=state_surface,
                wal=wal
            )
            
            ingest_result = await realm.handle_intent(ingest_intent, ingest_context)
            assert ingest_result is not None, "Ingest should succeed"
            file_id = ingest_result["artifacts"]["file_id"]
            file_reference = ingest_result["artifacts"]["file_reference"]
            
            # Step 2: Validate file
            validate_intent = IntentFactory.create_intent(
                intent_type="validate_file",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_phase4",
                parameters={
                    "file_id": file_id,
                    "validation_rules": {
                        "max_size": 1000000,  # 1MB
                        "allowed_types": ["text/plain", "text"]
                    }
                }
            )
            
            validate_context = ExecutionContextFactory.create_context(
                intent=validate_intent,
                state_surface=state_surface,
                wal=wal
            )
            
            validate_result = await realm.handle_intent(validate_intent, validate_context)
            assert validate_result is not None, "Validate should succeed"
            assert validate_result["artifacts"]["validation_results"]["valid"], "File should be valid"
            
            # Step 3: Update metadata
            update_intent = IntentFactory.create_intent(
                intent_type="update_file_metadata",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_phase4",
                parameters={
                    "file_id": file_id,
                    "metadata_updates": {
                        "description": "Phase 4 test file",
                        "tags": ["test", "phase4"]
                    }
                }
            )
            
            update_context = ExecutionContextFactory.create_context(
                intent=update_intent,
                state_surface=state_surface,
                wal=wal
            )
            
            update_result = await realm.handle_intent(update_intent, update_context)
            assert update_result is not None, "Update metadata should succeed"
            
            # Step 4: Archive file
            archive_intent = IntentFactory.create_intent(
                intent_type="archive_file",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_phase4",
                parameters={
                    "file_id": file_id,
                    "reason": "Test archive"
                }
            )
            
            archive_context = ExecutionContextFactory.create_context(
                intent=archive_intent,
                state_surface=state_surface,
                wal=wal
            )
            
            archive_result = await realm.handle_intent(archive_intent, archive_context)
            assert archive_result is not None, "Archive should succeed"
            assert archive_result["artifacts"]["status"] == "archived", "File should be archived"
            
            # Step 5: Restore file
            restore_intent = IntentFactory.create_intent(
                intent_type="restore_file",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_phase4",
                parameters={
                    "file_id": file_id
                }
            )
            
            restore_context = ExecutionContextFactory.create_context(
                intent=restore_intent,
                state_surface=state_surface,
                wal=wal
            )
            
            restore_result = await realm.handle_intent(restore_intent, restore_context)
            assert restore_result is not None, "Restore should succeed"
            assert restore_result["artifacts"]["status"] == "active", "File should be active"
            
            # Step 6: Search files
            search_intent = IntentFactory.create_intent(
                intent_type="search_files",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_phase4",
                parameters={
                    "query": "phase4",
                    "search_type": "name"
                }
            )
            
            search_context = ExecutionContextFactory.create_context(
                intent=search_intent,
                state_surface=state_surface,
                wal=wal
            )
            
            search_result = await realm.handle_intent(search_intent, search_context)
            assert search_result is not None, "Search should succeed"
            assert "files" in search_result["artifacts"], "Should return files list"
            
            # Cleanup
            await test_data_seeder.cleanup_test_records(
                tenant_id=tenant_id,
                session_id=session_id
            )
            
        except ImportError as e:
            pytest.skip(f"Content Realm not available: {e}")
        except Exception as e:
            pytest.fail(f"Phase 4 file lifecycle test failed: {e}")
    
    # ============================================================================
    # HIGH PRIORITY TESTS - Expanded Scenarios
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_register_file_expanded(
        self,
        phase1_setup,
        test_data_seeder
    ):
        """High Priority: Expanded register_file test with edge cases."""
        try:
            from symphainy_platform.realms.content.content_realm import ContentRealm
            
            realm = ContentRealm(public_works=phase1_setup["public_works"])
            state_surface = phase1_setup["state_surface"]
            wal = phase1_setup["wal"]
            
            tenant_id = "register_test_tenant"
            session_id = "register_test_session"
            
            # First, ingest a file to create it in GCS/Supabase
            test_content = b"file to register later"
            file_content_hex = test_content.hex()
            
            ingest_intent = IntentFactory.create_intent(
                intent_type="ingest_file",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_register",
                parameters={
                    "ingestion_type": "upload",
                    "file_content": file_content_hex,
                    "ui_name": "file_to_register.txt",
                    "file_type": "text/plain",
                    "mime_type": "text/plain"
                }
            )
            
            ingest_context = ExecutionContextFactory.create_context(
                intent=ingest_intent,
                state_surface=state_surface,
                wal=wal
            )
            
            ingest_result = await realm.handle_intent(ingest_intent, ingest_context)
            assert ingest_result is not None, "Ingest should succeed"
            file_id = ingest_result["artifacts"]["file_id"]
            
            # Now register the file (simulating it being in GCS but not in State Surface)
            register_intent = IntentFactory.create_intent(
                intent_type="register_file",
                tenant_id=tenant_id,
                session_id=session_id + "_new",  # Different session
                solution_id="solution_register",
                parameters={
                    "file_id": file_id,
                    "ui_name": "registered_file.txt",
                    "file_type": "text/plain",
                    "mime_type": "text/plain"
                }
            )
            
            register_context = ExecutionContextFactory.create_context(
                intent=register_intent,
                state_surface=state_surface,
                wal=wal
            )
            
            register_result = await realm.handle_intent(register_intent, register_context)
            assert register_result is not None, "Register should succeed"
            assert register_result["artifacts"]["file_id"] == file_id, "Should return same file_id"
            assert register_result["artifacts"]["ui_name"] == "registered_file.txt", "Should preserve ui_name"
            
            # Cleanup
            await test_data_seeder.cleanup_test_records(
                tenant_id=tenant_id,
                session_id=session_id
            )
            
        except ImportError as e:
            pytest.skip(f"Content Realm not available: {e}")
        except Exception as e:
            pytest.fail(f"Register file expanded test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_retrieve_file_metadata_expanded(
        self,
        phase1_setup,
        test_data_seeder
    ):
        """High Priority: Expanded retrieve_file_metadata test."""
        try:
            from symphainy_platform.realms.content.content_realm import ContentRealm
            
            realm = ContentRealm(public_works=phase1_setup["public_works"])
            state_surface = phase1_setup["state_surface"]
            wal = phase1_setup["wal"]
            
            tenant_id = "retrieve_meta_test_tenant"
            session_id = "retrieve_meta_test_session"
            
            # First, ingest a file
            test_content = b"file for metadata retrieval"
            file_content_hex = test_content.hex()
            
            ingest_intent = IntentFactory.create_intent(
                intent_type="ingest_file",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_retrieve",
                parameters={
                    "ingestion_type": "upload",
                    "file_content": file_content_hex,
                    "ui_name": "metadata_test.txt",
                    "file_type": "text/plain",
                    "mime_type": "text/plain"
                }
            )
            
            ingest_context = ExecutionContextFactory.create_context(
                intent=ingest_intent,
                state_surface=state_surface,
                wal=wal
            )
            
            ingest_result = await realm.handle_intent(ingest_intent, ingest_context)
            assert ingest_result is not None, "Ingest should succeed"
            file_id = ingest_result["artifacts"]["file_id"]
            
            # Retrieve metadata
            retrieve_intent = IntentFactory.create_intent(
                intent_type="retrieve_file_metadata",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_retrieve",
                parameters={
                    "file_id": file_id
                }
            )
            
            retrieve_context = ExecutionContextFactory.create_context(
                intent=retrieve_intent,
                state_surface=state_surface,
                wal=wal
            )
            
            retrieve_result = await realm.handle_intent(retrieve_intent, retrieve_context)
            assert retrieve_result is not None, "Retrieve should succeed"
            assert "file_metadata" in retrieve_result["artifacts"], "Should return file_metadata"
            
            metadata = retrieve_result["artifacts"]["file_metadata"]
            assert metadata is not None, "Metadata should not be None"
            
            # Cleanup
            await test_data_seeder.cleanup_test_records(
                tenant_id=tenant_id,
                session_id=session_id
            )
            
        except ImportError as e:
            pytest.skip(f"Content Realm not available: {e}")
        except Exception as e:
            pytest.fail(f"Retrieve file metadata expanded test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_retrieve_file_expanded(
        self,
        phase1_setup,
        test_data_seeder
    ):
        """High Priority: Expanded retrieve_file test with contents."""
        try:
            from symphainy_platform.realms.content.content_realm import ContentRealm
            
            realm = ContentRealm(public_works=phase1_setup["public_works"])
            state_surface = phase1_setup["state_surface"]
            wal = phase1_setup["wal"]
            
            tenant_id = "retrieve_file_test_tenant"
            session_id = "retrieve_file_test_session"
            
            # First, ingest a file
            original_content = b"original file content for retrieval"
            file_content_hex = original_content.hex()
            
            ingest_intent = IntentFactory.create_intent(
                intent_type="ingest_file",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_retrieve",
                parameters={
                    "ingestion_type": "upload",
                    "file_content": file_content_hex,
                    "ui_name": "retrieve_test.txt",
                    "file_type": "text/plain",
                    "mime_type": "text/plain"
                }
            )
            
            ingest_context = ExecutionContextFactory.create_context(
                intent=ingest_intent,
                state_surface=state_surface,
                wal=wal
            )
            
            ingest_result = await realm.handle_intent(ingest_intent, ingest_context)
            assert ingest_result is not None, "Ingest should succeed"
            file_id = ingest_result["artifacts"]["file_id"]
            file_reference = ingest_result["artifacts"]["file_reference"]
            
            # Retrieve file with contents
            retrieve_intent = IntentFactory.create_intent(
                intent_type="retrieve_file",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_retrieve",
                parameters={
                    "file_id": file_id,
                    "include_contents": True
                }
            )
            
            retrieve_context = ExecutionContextFactory.create_context(
                intent=retrieve_intent,
                state_surface=state_surface,
                wal=wal
            )
            
            retrieve_result = await realm.handle_intent(retrieve_intent, retrieve_context)
            assert retrieve_result is not None, "Retrieve should succeed"
            assert "file_contents" in retrieve_result["artifacts"], "Should return file_contents"
            
            # Verify contents match
            retrieved_contents = retrieve_result["artifacts"]["file_contents"]
            assert retrieved_contents == original_content, "Contents should match original"
            
            # Cleanup
            await test_data_seeder.cleanup_test_records(
                tenant_id=tenant_id,
                session_id=session_id
            )
            
        except ImportError as e:
            pytest.skip(f"Content Realm not available: {e}")
        except Exception as e:
            pytest.fail(f"Retrieve file expanded test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_bulk_ingest_files_expanded(
        self,
        phase1_setup,
        test_data_seeder
    ):
        """High Priority: Expanded bulk_ingest_files test with larger batch."""
        try:
            from symphainy_platform.realms.content.content_realm import ContentRealm
            
            realm = ContentRealm(public_works=phase1_setup["public_works"])
            state_surface = phase1_setup["state_surface"]
            wal = phase1_setup["wal"]
            
            tenant_id = "bulk_ingest_test_tenant"
            session_id = "bulk_ingest_test_session"
            
            # Prepare 10 files for bulk ingestion
            files = []
            for i in range(10):
                file_content = f"bulk test file {i}".encode()
                files.append({
                    "ingestion_type": "upload",
                    "file_content": file_content.hex(),
                    "ui_name": f"bulk_file_{i}.txt",
                    "file_type": "text/plain",
                    "mime_type": "text/plain"
                })
            
            bulk_intent = IntentFactory.create_intent(
                intent_type="bulk_ingest_files",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_bulk",
                parameters={
                    "files": files,
                    "batch_size": 5,
                    "max_parallel": 3
                }
            )
            
            bulk_context = ExecutionContextFactory.create_context(
                intent=bulk_intent,
                state_surface=state_surface,
                wal=wal
            )
            
            bulk_result = await realm.handle_intent(bulk_intent, bulk_context)
            assert bulk_result is not None, "Bulk ingest should succeed"
            assert bulk_result["artifacts"]["total_files"] == 10, "Should process 10 files"
            assert bulk_result["artifacts"]["success_count"] == 10, "All files should succeed"
            assert len(bulk_result["artifacts"]["results"]) == 10, "Should return 10 results"
            
            # Verify each file has file_id
            for result in bulk_result["artifacts"]["results"]:
                assert "file_id" in result, "Each result should have file_id"
                assert result.get("success") == True, "Each file should succeed"
            
            # Cleanup
            await test_data_seeder.cleanup_test_records(
                tenant_id=tenant_id,
                session_id=session_id
            )
            
        except ImportError as e:
            pytest.skip(f"Content Realm not available: {e}")
        except Exception as e:
            pytest.fail(f"Bulk ingest files expanded test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_idempotency_expanded(
        self,
        phase1_setup,
        test_data_seeder
    ):
        """High Priority: Expanded idempotency test with multiple operations."""
        try:
            from symphainy_platform.realms.content.content_realm import ContentRealm
            
            realm = ContentRealm(public_works=phase1_setup["public_works"])
            state_surface = phase1_setup["state_surface"]
            wal = phase1_setup["wal"]
            
            tenant_id = "idempotency_test_tenant"
            session_id = "idempotency_test_session"
            
            # Create bulk_ingest_files intent with idempotency key
            files = [
                {
                    "ingestion_type": "upload",
                    "file_content": b"idempotency test".hex(),
                    "ui_name": "idempotency_test.txt",
                    "file_type": "text/plain",
                    "mime_type": "text/plain"
                }
            ]
            
            idempotency_key = "test_idempotency_key_001"
            bulk_intent = IntentFactory.create_intent(
                intent_type="bulk_ingest_files",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_idempotency",
                parameters={
                    "files": files,
                    "batch_size": 1,
                    "max_parallel": 1
                }
            )
            bulk_intent.idempotency_key = idempotency_key
            
            bulk_context = ExecutionContextFactory.create_context(
                intent=bulk_intent,
                state_surface=state_surface,
                wal=wal
            )
            
            # Execute first time
            result1 = await realm.handle_intent(bulk_intent, bulk_context)
            assert result1 is not None, "First execution should succeed"
            operation_id_1 = result1["artifacts"].get("operation_id")
            
            # Execute second time (should return previous result)
            result2 = await realm.handle_intent(bulk_intent, bulk_context)
            assert result2 is not None, "Second execution should return result"
            operation_id_2 = result2["artifacts"].get("operation_id")
            
            # Verify same operation_id (idempotent)
            assert operation_id_1 == operation_id_2, "Should return same operation_id"
            assert result1["artifacts"]["success_count"] == result2["artifacts"]["success_count"], "Results should match"
            
            # Execute third time (should still return previous result)
            result3 = await realm.handle_intent(bulk_intent, bulk_context)
            assert result3 is not None, "Third execution should return result"
            assert result3["artifacts"].get("operation_id") == operation_id_1, "Should return same operation_id"
            
            # Cleanup
            await test_data_seeder.cleanup_test_records(
                tenant_id=tenant_id,
                session_id=session_id
            )
            
        except ImportError as e:
            pytest.skip(f"Content Realm not available: {e}")
        except Exception as e:
            pytest.fail(f"Idempotency expanded test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_progress_tracking_expanded(
        self,
        phase1_setup,
        test_data_seeder
    ):
        """High Priority: Expanded progress tracking test."""
        try:
            from symphainy_platform.realms.content.content_realm import ContentRealm
            
            realm = ContentRealm(public_works=phase1_setup["public_works"])
            state_surface = phase1_setup["state_surface"]
            wal = phase1_setup["wal"]
            
            tenant_id = "progress_test_tenant"
            session_id = "progress_test_session"
            
            # Create bulk_ingest_files intent with multiple files
            files = []
            for i in range(20):
                file_content = f"progress test file {i}".encode()
                files.append({
                    "ingestion_type": "upload",
                    "file_content": file_content.hex(),
                    "ui_name": f"progress_file_{i}.txt",
                    "file_type": "text/plain",
                    "mime_type": "text/plain"
                })
            
            bulk_intent = IntentFactory.create_intent(
                intent_type="bulk_ingest_files",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_progress",
                parameters={
                    "files": files,
                    "batch_size": 5,
                    "max_parallel": 2
                }
            )
            
            bulk_context = ExecutionContextFactory.create_context(
                intent=bulk_intent,
                state_surface=state_surface,
                wal=wal
            )
            
            # Execute bulk operation
            bulk_result = await realm.handle_intent(bulk_intent, bulk_context)
            assert bulk_result is not None, "Bulk ingest should succeed"
            operation_id = bulk_result["artifacts"].get("operation_id")
            assert operation_id is not None, "Should return operation_id"
            
            # Query progress
            status_intent = IntentFactory.create_intent(
                intent_type="get_operation_status",
                tenant_id=tenant_id,
                session_id=session_id,
                solution_id="solution_progress",
                parameters={
                    "operation_id": operation_id
                }
            )
            
            status_context = ExecutionContextFactory.create_context(
                intent=status_intent,
                state_surface=state_surface,
                wal=wal
            )
            
            status_result = await realm.handle_intent(status_intent, status_context)
            assert status_result is not None, "Status query should succeed"
            assert status_result["artifacts"]["status"] == "completed", "Operation should be completed"
            assert status_result["artifacts"]["total"] == 20, "Should have processed 20 files"
            assert status_result["artifacts"]["succeeded"] == 20, "Should have succeeded for 20 files"
            assert status_result["artifacts"]["progress_percentage"] == 100.0, "Should be 100% complete"
            
            # Cleanup
            await test_data_seeder.cleanup_test_records(
                tenant_id=tenant_id,
                session_id=session_id
            )
            
        except ImportError as e:
            pytest.skip(f"Content Realm not available: {e}")
        except Exception as e:
            pytest.fail(f"Progress tracking expanded test failed: {e}")
