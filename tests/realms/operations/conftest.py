"""
Pytest fixtures for Operations Realm tests.

NOTE: Migrated from Journey Realm tests. The Operations Realm uses
enabling_services pattern instead of the old service pattern.
"""

import pytest
from typing import Dict, Any

from symphainy_platform.runtime.state_surface import StateSurface
from symphainy_platform.runtime.in_memory_file_storage import InMemoryFileStorage
from symphainy_platform.realms.operations.enabling_services.workflow_conversion_service import WorkflowConversionService
from symphainy_platform.realms.operations.enabling_services.coexistence_analysis_service import CoexistenceAnalysisService
from symphainy_platform.realms.operations.orchestrators.operations_orchestrator import OperationsOrchestrator


@pytest.fixture
def in_memory_file_storage():
    """Create in-memory file storage for testing."""
    return InMemoryFileStorage()


@pytest.fixture
def state_surface(in_memory_file_storage):
    """Create State Surface with in-memory file storage for testing."""
    return StateSurface(
        state_abstraction=None,
        file_storage=in_memory_file_storage,
        use_memory=True
    )


@pytest.fixture
def workflow_conversion_service():
    """Create Workflow Conversion Service for testing."""
    return WorkflowConversionService()


@pytest.fixture
def coexistence_analysis_service():
    """Create Coexistence Analysis Service for testing."""
    return CoexistenceAnalysisService()


@pytest.fixture
def operations_orchestrator():
    """Create Operations Orchestrator for testing."""
    return OperationsOrchestrator()


@pytest.fixture
def sample_session_id():
    """Sample session ID for testing."""
    return "test_session_123"


@pytest.fixture
def sample_tenant_id():
    """Sample tenant ID for testing."""
    return "test_tenant_456"


@pytest.fixture
def sample_sop_data():
    """Sample SOP data for testing."""
    return {
        "template_type": "standard",
        "title": "Test SOP",
        "purpose": "This is a test SOP",
        "sections": {
            "procedures": [
                {"step": 1, "description": "Step 1: Do something"},
                {"step": 2, "description": "Step 2: Do something else"}
            ]
        }
    }


@pytest.fixture
def sample_workflow_data():
    """Sample workflow data for testing."""
    return {
        "workflow_id": "test_workflow_123",
        "workflow_name": "Test Workflow",
        "workflow_type": "sequential",
        "description": "This is a test workflow",
        "nodes": [
            {
                "node_id": "node_1",
                "node_type": "task",
                "label": "Task 1",
                "position": {"x": 100, "y": 100}
            },
            {
                "node_id": "node_2",
                "node_type": "task",
                "label": "Task 2",
                "position": {"x": 100, "y": 200}
            }
        ],
        "edges": [
            {
                "edge_id": "edge_1",
                "source": "node_1",
                "target": "node_2",
                "type": "sequential"
            }
        ]
    }
