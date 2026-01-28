"""
3D Test Suite - Shared Fixtures and Configuration

Provides fixtures for:
- Solution instances
- Journey orchestrators
- Intent services
- MCP servers
- Execution contexts
- Mock infrastructure
"""

import sys
from pathlib import Path

# Add project roots to path
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pytest
import asyncio
from typing import Dict, Any, Optional
from unittest.mock import Mock, AsyncMock, MagicMock
from datetime import datetime, timezone

# ============================================
# Mock Infrastructure Fixtures
# ============================================

@pytest.fixture
def mock_public_works():
    """Mock PublicWorksFoundationService."""
    pw = Mock()
    
    # State abstraction
    pw.state_abstraction = Mock()
    pw.state_abstraction.get = AsyncMock(return_value=None)
    pw.state_abstraction.set = AsyncMock(return_value=True)
    pw.state_abstraction.delete = AsyncMock(return_value=True)
    
    # File storage abstraction
    pw.file_storage_abstraction = Mock()
    pw.file_storage_abstraction.upload_file = AsyncMock(return_value={"file_id": "test_file_123"})
    pw.file_storage_abstraction.download_file = AsyncMock(return_value=b"test content")
    pw.file_storage_abstraction.delete_file = AsyncMock(return_value=True)
    
    # Artifact storage abstraction
    pw.artifact_storage_abstraction = Mock()
    pw.artifact_storage_abstraction.store_artifact = AsyncMock(return_value={"artifact_id": "test_artifact_123"})
    pw.artifact_storage_abstraction.get_artifact = AsyncMock(return_value={"artifact_id": "test_artifact_123", "status": "READY"})
    
    # Registry abstraction
    pw.registry_abstraction = Mock()
    pw.registry_abstraction.register = AsyncMock(return_value=True)
    pw.registry_abstraction.get = AsyncMock(return_value={})
    pw.registry_abstraction.list = AsyncMock(return_value=[])
    
    # Auth abstraction
    pw.auth_abstraction = Mock()
    pw.auth_abstraction.validate_token = AsyncMock(return_value={"valid": True, "user_id": "test_user"})
    pw.auth_abstraction.create_session = AsyncMock(return_value={"session_id": "test_session_123"})
    
    # Tenant abstraction
    pw.tenant_abstraction = Mock()
    pw.tenant_abstraction.get_tenant = AsyncMock(return_value={"tenant_id": "test_tenant", "name": "Test Tenant"})
    pw.tenant_abstraction.validate_tenant = AsyncMock(return_value=True)
    
    # Telemetry
    pw.get_telemetry_service = Mock(return_value=Mock(record=AsyncMock()))
    
    # Redis adapter
    pw.redis_adapter = Mock()
    pw.redis_adapter.get = AsyncMock(return_value=None)
    pw.redis_adapter.set = AsyncMock(return_value=True)
    
    # Get abstraction methods
    pw.get_state_abstraction = Mock(return_value=pw.state_abstraction)
    pw.get_auth_abstraction = Mock(return_value=pw.auth_abstraction)
    pw.get_tenant_abstraction = Mock(return_value=pw.tenant_abstraction)
    
    return pw


@pytest.fixture
def mock_state_surface():
    """Mock StateSurface."""
    ss = Mock()
    
    # Session state
    ss.get_session_state = AsyncMock(return_value=None)
    ss.set_session_state = AsyncMock(return_value=True)
    
    # Execution state
    ss.get_execution_state = AsyncMock(return_value=None)
    ss.set_execution_state = AsyncMock(return_value=True)
    
    # Artifact management
    ss.register_artifact = AsyncMock(return_value={"artifact_id": "test_artifact_123", "status": "PENDING"})
    ss.get_artifact = AsyncMock(return_value={"artifact_id": "test_artifact_123", "status": "READY"})
    ss.mark_artifact_ready = AsyncMock(return_value=True)
    
    return ss


@pytest.fixture
def mock_solution_registry():
    """Mock SolutionRegistry."""
    from symphainy_platform.civic_systems.platform_sdk.solution_registry import SolutionRegistry
    registry = SolutionRegistry()
    return registry


@pytest.fixture
def mock_intent_registry():
    """Mock IntentRegistry."""
    from symphainy_platform.runtime.intent_registry import IntentRegistry
    registry = IntentRegistry()
    return registry


@pytest.fixture
def mock_curator():
    """Mock Curator for MCP tool discovery."""
    curator = Mock()
    
    # Return all platform MCP tools
    curator.get_all_mcp_tools = AsyncMock(return_value=[
        {"tool_name": "coexist_introduce", "description": "Introduce platform", "solution": "coexistence"},
        {"tool_name": "coexist_navigate", "description": "Navigate to solution", "solution": "coexistence"},
        {"tool_name": "content_upload", "description": "Upload file", "solution": "content_solution"},
        {"tool_name": "content_parse", "description": "Parse content", "solution": "content_solution"},
        {"tool_name": "insights_analyze", "description": "Analyze data", "solution": "insights_solution"},
        {"tool_name": "insights_quality", "description": "Assess quality", "solution": "insights_solution"},
        {"tool_name": "ops_workflow", "description": "Manage workflow", "solution": "operations_solution"},
        {"tool_name": "ops_sop", "description": "Generate SOP", "solution": "operations_solution"},
        {"tool_name": "outcomes_poc", "description": "Create POC", "solution": "outcomes_solution"},
        {"tool_name": "outcomes_roadmap", "description": "Generate roadmap", "solution": "outcomes_solution"},
        {"tool_name": "security_auth", "description": "Authenticate", "solution": "security_solution"},
        {"tool_name": "tower_monitor", "description": "Monitor platform", "solution": "control_tower"},
    ])
    
    return curator


# ============================================
# Execution Context Fixtures
# ============================================

@pytest.fixture
def execution_context(mock_state_surface):
    """Create ExecutionContext for tests."""
    from symphainy_platform.runtime.execution_context import ExecutionContext
    from utilities import generate_event_id
    
    return ExecutionContext(
        execution_id=generate_event_id(),
        tenant_id="test_tenant",
        session_id="test_session_123",
        intent=None,
        solution_id="test_solution",
        state_surface=mock_state_surface
    )


@pytest.fixture
def tenant_a_context(mock_state_surface):
    """ExecutionContext for tenant A (isolation tests)."""
    from symphainy_platform.runtime.execution_context import ExecutionContext
    from utilities import generate_event_id
    
    return ExecutionContext(
        execution_id=generate_event_id(),
        tenant_id="tenant_a",
        session_id="session_tenant_a",
        intent=None,
        solution_id="test_solution",
        state_surface=mock_state_surface
    )


@pytest.fixture
def tenant_b_context(mock_state_surface):
    """ExecutionContext for tenant B (isolation tests)."""
    from symphainy_platform.runtime.execution_context import ExecutionContext
    from utilities import generate_event_id
    
    return ExecutionContext(
        execution_id=generate_event_id(),
        tenant_id="tenant_b",
        session_id="session_tenant_b",
        intent=None,
        solution_id="test_solution",
        state_surface=mock_state_surface
    )


# ============================================
# Solution Fixtures
# ============================================

@pytest.fixture
def coexistence_solution(mock_public_works, mock_state_surface, mock_solution_registry, mock_curator):
    """CoexistenceSolution instance."""
    from symphainy_platform.solutions.coexistence import CoexistenceSolution
    return CoexistenceSolution(
        public_works=mock_public_works,
        state_surface=mock_state_surface,
        solution_registry=mock_solution_registry,
        curator=mock_curator
    )


@pytest.fixture
def content_solution(mock_public_works, mock_state_surface):
    """ContentSolution instance."""
    from symphainy_platform.solutions.content_solution import ContentSolution
    return ContentSolution(
        public_works=mock_public_works,
        state_surface=mock_state_surface
    )


@pytest.fixture
def insights_solution(mock_public_works, mock_state_surface):
    """InsightsSolution instance."""
    from symphainy_platform.solutions.insights_solution import InsightsSolution
    return InsightsSolution(
        public_works=mock_public_works,
        state_surface=mock_state_surface
    )


@pytest.fixture
def operations_solution(mock_public_works, mock_state_surface):
    """OperationsSolution instance."""
    from symphainy_platform.solutions.operations_solution import OperationsSolution
    return OperationsSolution(
        public_works=mock_public_works,
        state_surface=mock_state_surface
    )


@pytest.fixture
def outcomes_solution(mock_public_works, mock_state_surface):
    """OutcomesSolution instance."""
    from symphainy_platform.solutions.outcomes_solution import OutcomesSolution
    return OutcomesSolution(
        public_works=mock_public_works,
        state_surface=mock_state_surface
    )


@pytest.fixture
def security_solution(mock_public_works, mock_state_surface):
    """SecuritySolution instance."""
    from symphainy_platform.solutions.security_solution import SecuritySolution
    return SecuritySolution(
        public_works=mock_public_works,
        state_surface=mock_state_surface
    )




@pytest.fixture
def control_tower(mock_public_works, mock_state_surface, mock_solution_registry):
    """ControlTower instance."""
    from symphainy_platform.solutions.control_tower import ControlTower
    return ControlTower(
        public_works=mock_public_works,
        state_surface=mock_state_surface,
        solution_registry=mock_solution_registry
    )


# ============================================
# Intent Fixtures
# ============================================

@pytest.fixture
def compose_journey_intent():
    """Factory for compose_journey intents."""
    from symphainy_platform.runtime.intent_model import IntentFactory
    
    def _create(journey_id: str, journey_params: Dict = None, solution_id: str = "test_solution"):
        return IntentFactory.create_intent(
            intent_type="compose_journey",
            tenant_id="test_tenant",
            session_id="test_session_123",
            solution_id=solution_id,
            parameters={
                "journey_id": journey_id,
                "journey_params": journey_params or {}
            }
        )
    
    return _create


@pytest.fixture
def upload_file_intent():
    """Factory for ingest_file intents."""
    from symphainy_platform.runtime.intent_model import IntentFactory
    
    def _create(file_path: str = "/tmp/test.txt", file_name: str = "test.txt"):
        return IntentFactory.create_intent(
            intent_type="ingest_file",
            tenant_id="test_tenant",
            session_id="test_session_123",
            solution_id="content_solution",
            parameters={
                "file_path": file_path,
                "file_name": file_name
            }
        )
    
    return _create


# ============================================
# Test Data Fixtures
# ============================================

@pytest.fixture
def sample_file_content():
    """Sample file content for upload tests."""
    return b"This is test content for file upload testing."


@pytest.fixture
def sample_parsed_content():
    """Sample parsed content for analysis tests."""
    return {
        "parsed_file_id": "parsed_123",
        "source_file_id": "file_123",
        "content_type": "text/plain",
        "parsed_at": datetime.now(timezone.utc).isoformat(),
        "chunks": [
            {"chunk_id": "chunk_1", "text": "First paragraph"},
            {"chunk_id": "chunk_2", "text": "Second paragraph"}
        ]
    }


@pytest.fixture
def sample_quality_report():
    """Sample quality assessment report."""
    return {
        "quality_score": 0.85,
        "completeness": 0.90,
        "accuracy": 0.88,
        "consistency": 0.82,
        "issues": [],
        "recommendations": []
    }


@pytest.fixture
def sample_user_credentials():
    """Sample user credentials for auth tests."""
    return {
        "email": "test@example.com",
        "password": "SecureP@ssw0rd123"
    }


@pytest.fixture
def sample_auth_token():
    """Sample auth token."""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test_token_payload.signature"


# ============================================
# Helper Functions
# ============================================

def assert_artifact_structure(artifact: Dict[str, Any]):
    """Assert artifact has required structure."""
    assert "result_type" in artifact, "Artifact missing result_type"
    assert "semantic_payload" in artifact, "Artifact missing semantic_payload"
    assert "renderings" in artifact, "Artifact missing renderings"


def assert_journey_result(result: Dict[str, Any]):
    """Assert journey result has required structure."""
    assert "success" in result, "Result missing success flag"
    assert "journey_id" in result, "Result missing journey_id"
    assert "journey_execution_id" in result, "Result missing journey_execution_id"
    assert "artifacts" in result, "Result missing artifacts"
    assert "events" in result, "Result missing events"


def assert_soa_api_structure(api_def: Dict[str, Any]):
    """Assert SOA API definition has required structure."""
    assert "handler" in api_def, "SOA API missing handler"
    assert "input_schema" in api_def, "SOA API missing input_schema"
    assert "description" in api_def, "SOA API missing description"
