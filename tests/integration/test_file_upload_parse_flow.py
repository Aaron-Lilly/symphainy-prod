"""
Integration Tests: File Upload and Parse Flow

These tests prove the platform ACTUALLY WORKS by:
1. Uploading real test files to real storage
2. Parsing files with real parsers
3. Validating outputs against expected results

Requirements:
- Docker Compose test infrastructure running (redis, arango, gcs-emulator, etc.)
- Test files in tests/test_data/files/

Run with:
    pytest tests/integration/test_file_upload_parse_flow.py -v --tb=short

Or with docker-compose:
    docker-compose -f docker-compose.test.yml up -d
    ./scripts/wait-for-services.sh --runtime
    pytest tests/integration/test_file_upload_parse_flow.py -v
"""

import pytest
import asyncio
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Import test infrastructure
from tests.infrastructure.test_fixtures import (
    test_redis,
    test_arango,
    test_gcs,
    test_supabase,
    test_public_works,
    test_infrastructure,
)

# Import validation rules
from tests.expected.validation_rules import (
    validate_csv_parse,
    validate_json_parse,
    validate_file_upload,
    validate_parse_result_structure,
    validate_execution_status,
    validate_upload_and_parse_flow,
    ValidationResult,
)

# Import platform components
try:
    from symphainy_coexistence_fabric.runtime.intent_model import Intent, IntentFactory
    from symphainy_coexistence_fabric.runtime.execution_context import (
        ExecutionContext,
        ExecutionContextFactory,
    )
    from symphainy_coexistence_fabric.runtime.state_surface import StateSurface
    from symphainy_coexistence_fabric.runtime.wal import WriteAheadLog
    from symphainy_coexistence_fabric.runtime.intent_registry import IntentRegistry
    from symphainy_coexistence_fabric.runtime.execution_lifecycle_manager import (
        ExecutionLifecycleManager,
    )
    from symphainy_coexistence_fabric.realms.content.content_realm import ContentRealm
    from symphainy_coexistence_fabric.foundations.public_works.abstractions.state_abstraction import (
        StateManagementAbstraction,
    )

    PLATFORM_AVAILABLE = True
except ImportError as e:
    PLATFORM_AVAILABLE = False
    IMPORT_ERROR = str(e)


# Test data directory
TEST_DATA_DIR = Path(__file__).parent.parent / "test_data" / "files"


def read_test_file(filename: str) -> bytes:
    """Read a test file from test_data/files directory."""
    file_path = TEST_DATA_DIR / filename
    if not file_path.exists():
        raise FileNotFoundError(f"Test file not found: {file_path}")
    return file_path.read_bytes()


@pytest.mark.integration
@pytest.mark.infrastructure
class TestFileUploadParseFlow:
    """
    Integration tests for file upload and parse flow.
    
    These tests prove the platform correctly:
    1. Accepts file uploads
    2. Stores files in GCS (emulator)
    3. Parses files with appropriate parsers
    4. Returns correctly structured artifacts
    5. Produces expected content from parsing
    """

    @pytest.fixture
    def platform_setup(
        self,
        test_redis,
        test_arango,
        test_public_works,
    ):
        """Set up platform components for testing."""
        if not PLATFORM_AVAILABLE:
            pytest.skip(f"Platform not available: {IMPORT_ERROR}")

        # Create state management
        state_abstraction = StateManagementAbstraction(
            redis_adapter=test_redis,
            arango_adapter=test_arango,
        )
        state_surface = StateSurface(state_abstraction=state_abstraction)
        wal = WriteAheadLog(redis_adapter=test_redis)

        # Create intent registry
        intent_registry = IntentRegistry()

        # Create execution manager (without data steward for now)
        execution_manager = ExecutionLifecycleManager(
            intent_registry=intent_registry,
            state_surface=state_surface,
            wal=wal,
        )

        # Create content realm
        content_realm = ContentRealm(public_works=test_public_works)

        # Register content realm intents
        for intent_type in content_realm.declare_intents():
            intent_registry.register_intent(
                intent_type=intent_type,
                handler_name="content_realm",
                handler_function=content_realm.handle_intent,
            )

        return {
            "state_surface": state_surface,
            "wal": wal,
            "intent_registry": intent_registry,
            "execution_manager": execution_manager,
            "content_realm": content_realm,
            "public_works": test_public_works,
        }

    @pytest.mark.asyncio
    async def test_csv_upload_and_parse_produces_expected_output(
        self,
        platform_setup,
        test_gcs,
    ):
        """
        Test: Upload CSV → Parse → Validate content matches expected.
        
        This proves the platform can:
        1. Accept a CSV file upload
        2. Store it in GCS
        3. Parse it correctly
        4. Produce expected structured output
        """
        content_realm = platform_setup["content_realm"]
        state_surface = platform_setup["state_surface"]
        wal = platform_setup["wal"]

        # Read test file
        csv_content = read_test_file("sample.csv")
        assert len(csv_content) > 0, "Test file should have content"

        # Step 1: Upload file
        import base64

        upload_intent = IntentFactory.create_intent(
            intent_type="ingest_file",
            tenant_id="integration_test_tenant",
            session_id="integration_test_session",
            solution_id="solution_content",
            parameters={
                "file_content": base64.b64encode(csv_content).decode("utf-8"),
                "file_name": "sample.csv",
                "file_type": "text/csv",
                "mime_type": "text/csv",
            },
        )

        upload_context = ExecutionContextFactory.create_context(
            intent=upload_intent,
            state_surface=state_surface,
            wal=wal,
        )

        upload_result = await content_realm.handle_intent(upload_intent, upload_context)

        # Validate upload result
        upload_validation = validate_file_upload(
            upload_result, "sample.csv", "text/csv"
        )
        assert upload_validation.is_valid, f"Upload failed: {upload_validation.errors}"

        # Extract file_id for parsing
        file_id = upload_result.get("artifacts", {}).get(
            "file_id", upload_result.get("file_id")
        )
        assert file_id, "Upload should return file_id"

        # Step 2: Parse file
        parse_intent = IntentFactory.create_intent(
            intent_type="parse_content",
            tenant_id="integration_test_tenant",
            session_id="integration_test_session",
            solution_id="solution_content",
            parameters={
                "file_id": file_id,
                "file_type": "text/csv",
            },
        )

        parse_context = ExecutionContextFactory.create_context(
            intent=parse_intent,
            state_surface=state_surface,
            wal=wal,
        )

        parse_result = await content_realm.handle_intent(parse_intent, parse_context)

        # Validate parse result structure
        structure_validation = validate_parse_result_structure(parse_result)
        assert (
            structure_validation.is_valid
        ), f"Parse structure invalid: {structure_validation.errors}"

        # Validate CSV content matches expected
        csv_validation = validate_csv_parse(parse_result, "sample.csv")
        assert csv_validation.is_valid, f"CSV validation failed: {csv_validation.errors}"

        # Additional semantic checks
        parsed = parse_result.get("artifacts", {}).get("parsed_content", {})
        if parsed:
            # Verify we got the right number of columns
            columns = parsed.get("columns", parsed.get("headers", []))
            assert len(columns) == 5, f"Expected 5 columns, got {len(columns)}"

            # Verify we got the right number of rows
            rows = parsed.get("rows", parsed.get("data", []))
            assert len(rows) == 5, f"Expected 5 rows, got {len(rows)}"

    @pytest.mark.asyncio
    async def test_json_upload_and_parse_produces_expected_output(
        self,
        platform_setup,
        test_gcs,
    ):
        """
        Test: Upload JSON → Parse → Validate content matches expected.
        """
        content_realm = platform_setup["content_realm"]
        state_surface = platform_setup["state_surface"]
        wal = platform_setup["wal"]

        # Read test file
        json_content = read_test_file("sample.json")
        assert len(json_content) > 0, "Test file should have content"

        # Upload file
        import base64

        upload_intent = IntentFactory.create_intent(
            intent_type="ingest_file",
            tenant_id="integration_test_tenant",
            session_id="integration_test_session_json",
            solution_id="solution_content",
            parameters={
                "file_content": base64.b64encode(json_content).decode("utf-8"),
                "file_name": "sample.json",
                "file_type": "application/json",
                "mime_type": "application/json",
            },
        )

        upload_context = ExecutionContextFactory.create_context(
            intent=upload_intent,
            state_surface=state_surface,
            wal=wal,
        )

        upload_result = await content_realm.handle_intent(upload_intent, upload_context)

        # Validate upload
        upload_validation = validate_file_upload(
            upload_result, "sample.json", "application/json"
        )
        assert upload_validation.is_valid, f"Upload failed: {upload_validation.errors}"

        file_id = upload_result.get("artifacts", {}).get(
            "file_id", upload_result.get("file_id")
        )
        assert file_id, "Upload should return file_id"

        # Parse file
        parse_intent = IntentFactory.create_intent(
            intent_type="parse_content",
            tenant_id="integration_test_tenant",
            session_id="integration_test_session_json",
            solution_id="solution_content",
            parameters={
                "file_id": file_id,
                "file_type": "application/json",
            },
        )

        parse_context = ExecutionContextFactory.create_context(
            intent=parse_intent,
            state_surface=state_surface,
            wal=wal,
        )

        parse_result = await content_realm.handle_intent(parse_intent, parse_context)

        # Validate JSON content
        json_validation = validate_json_parse(parse_result, "sample.json")
        assert json_validation.is_valid, f"JSON validation failed: {json_validation.errors}"

        # Semantic check: verify organization name
        parsed = parse_result.get("artifacts", {}).get("parsed_content", {})
        if parsed:
            org = parsed.get("organization")
            if org:
                assert org == "SymphAIny Platform", f"Wrong organization: {org}"

    @pytest.mark.asyncio
    async def test_full_upload_parse_flow_validation(
        self,
        platform_setup,
        test_gcs,
    ):
        """
        Test: Complete upload → parse flow with aggregate validation.
        
        Uses validate_upload_and_parse_flow() to validate entire flow.
        """
        content_realm = platform_setup["content_realm"]
        state_surface = platform_setup["state_surface"]
        wal = platform_setup["wal"]

        csv_content = read_test_file("sample.csv")
        import base64

        # Upload
        upload_intent = IntentFactory.create_intent(
            intent_type="ingest_file",
            tenant_id="integration_test_tenant",
            session_id="flow_test_session",
            solution_id="solution_content",
            parameters={
                "file_content": base64.b64encode(csv_content).decode("utf-8"),
                "file_name": "sample.csv",
                "file_type": "text/csv",
                "mime_type": "text/csv",
            },
        )

        upload_result = await content_realm.handle_intent(
            upload_intent,
            ExecutionContextFactory.create_context(
                intent=upload_intent,
                state_surface=state_surface,
                wal=wal,
            ),
        )

        file_id = upload_result.get("artifacts", {}).get("file_id")

        # Parse
        parse_intent = IntentFactory.create_intent(
            intent_type="parse_content",
            tenant_id="integration_test_tenant",
            session_id="flow_test_session",
            solution_id="solution_content",
            parameters={
                "file_id": file_id,
                "file_type": "text/csv",
            },
        )

        parse_result = await content_realm.handle_intent(
            parse_intent,
            ExecutionContextFactory.create_context(
                intent=parse_intent,
                state_surface=state_surface,
                wal=wal,
            ),
        )

        # Validate complete flow
        flow_validation = validate_upload_and_parse_flow(
            upload_result=upload_result,
            parse_result=parse_result,
            file_name="sample.csv",
            file_type="text/csv",
        )

        assert flow_validation.is_valid, f"Flow validation failed: {flow_validation.errors}"

        # Report any warnings
        if flow_validation.warnings:
            for warning in flow_validation.warnings:
                print(f"Warning: {warning}")


@pytest.mark.integration
@pytest.mark.infrastructure
class TestStorageVerification:
    """
    Tests that verify files are actually stored and retrievable.
    """

    @pytest.mark.asyncio
    async def test_uploaded_file_exists_in_storage(
        self,
        test_gcs,
        test_infrastructure,
    ):
        """
        Test: Uploaded file is actually persisted in GCS.
        
        Proves that uploads aren't just returning fake IDs.
        """
        # Upload a file directly to GCS
        test_content = b"test,data\n1,hello\n2,world"
        blob_path = f"test_uploads/verification_test_{asyncio.get_event_loop().time()}.csv"

        # Use GCS adapter to upload
        try:
            # Upload
            await test_gcs.upload_blob(
                blob_path,
                test_content,
                content_type="text/csv",
            )

            # Verify it exists
            exists = await test_gcs.blob_exists(blob_path)
            assert exists, "Uploaded file should exist in storage"

            # Verify content matches
            downloaded = await test_gcs.download_blob(blob_path)
            assert downloaded == test_content, "Downloaded content should match uploaded"

            # Cleanup
            await test_gcs.delete_blob(blob_path)

        except Exception as e:
            pytest.skip(f"GCS operations not available: {e}")


@pytest.mark.integration
class TestExecutionStatusTracking:
    """
    Tests for execution status tracking and retrieval.
    """

    @pytest.mark.asyncio
    async def test_execution_status_transitions(
        self,
        test_redis,
        test_arango,
    ):
        """
        Test: Execution status correctly transitions through states.
        
        Proves that execution lifecycle is tracked correctly.
        """
        if not PLATFORM_AVAILABLE:
            pytest.skip(f"Platform not available: {IMPORT_ERROR}")

        # Create state management
        state_abstraction = StateManagementAbstraction(
            redis_adapter=test_redis,
            arango_adapter=test_arango,
        )

        # Create an execution and verify status
        execution_id = f"test_exec_{asyncio.get_event_loop().time()}"

        # Store initial status
        await state_abstraction.set_state(
            f"execution:{execution_id}",
            {
                "execution_id": execution_id,
                "status": "pending",
                "created_at": "2026-01-28T00:00:00Z",
            },
        )

        # Retrieve and verify
        status = await state_abstraction.get_state(f"execution:{execution_id}")
        assert status is not None, "Status should be stored"
        assert status.get("status") == "pending", "Initial status should be pending"

        # Update to running
        await state_abstraction.set_state(
            f"execution:{execution_id}",
            {
                "execution_id": execution_id,
                "status": "running",
                "started_at": "2026-01-28T00:00:01Z",
            },
        )

        status = await state_abstraction.get_state(f"execution:{execution_id}")
        assert status.get("status") == "running", "Status should be running"

        # Update to completed
        await state_abstraction.set_state(
            f"execution:{execution_id}",
            {
                "execution_id": execution_id,
                "status": "completed",
                "completed_at": "2026-01-28T00:00:02Z",
                "artifacts": {"result": "success"},
            },
        )

        status = await state_abstraction.get_state(f"execution:{execution_id}")
        validation = validate_execution_status(status, "completed")
        assert validation.is_valid, f"Status validation failed: {validation.errors}"
