"""
Pytest fixtures for Journey Realm tests.
"""

import pytest
from typing import Dict, Any

from symphainy_platform.runtime.state_surface import StateSurface
from symphainy_platform.runtime.in_memory_file_storage import InMemoryFileStorage
from symphainy_platform.realms.journey.services.sop_builder_service.sop_builder_service import SOPBuilderService
from symphainy_platform.realms.journey.services.workflow_conversion_service.workflow_conversion_service import WorkflowConversionService
from symphainy_platform.realms.journey.services.coexistence_analysis_service.coexistence_analysis_service import CoexistenceAnalysisService
from symphainy_platform.realms.journey.orchestrators.journey_orchestrator import JourneyOrchestrator


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
def sop_builder_service(state_surface, in_memory_file_storage):
    """Create SOP Builder Service for testing."""
    return SOPBuilderService(
        state_surface=state_surface,
        file_storage_abstraction=in_memory_file_storage,
        platform_gateway=None
    )


@pytest.fixture
def workflow_conversion_service(state_surface, in_memory_file_storage):
    """Create Workflow Conversion Service for testing."""
    return WorkflowConversionService(
        state_surface=state_surface,
        file_storage_abstraction=in_memory_file_storage,
        platform_gateway=None
    )


@pytest.fixture
def coexistence_analysis_service(state_surface, in_memory_file_storage):
    """Create Coexistence Analysis Service for testing."""
    return CoexistenceAnalysisService(
        state_surface=state_surface,
        file_storage_abstraction=in_memory_file_storage,
        platform_gateway=None
    )


@pytest.fixture
def journey_orchestrator(
    sop_builder_service,
    workflow_conversion_service,
    coexistence_analysis_service,
    state_surface,
    in_memory_file_storage
):
    """Create Journey Orchestrator for testing."""
    return JourneyOrchestrator(
        sop_builder_service=sop_builder_service,
        workflow_conversion_service=workflow_conversion_service,
        coexistence_analysis_service=coexistence_analysis_service,
        state_surface=state_surface,
        file_storage_abstraction=in_memory_file_storage,
        agent_foundation=None
    )


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
