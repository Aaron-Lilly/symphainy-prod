"""
Integration tests for Operations Realm Blueprint capabilities (formerly Journey Realm).

Tests:
1. create_blueprint - Creates comprehensive blueprint with all components
2. create_solution_from_blueprint - Converts blueprint to implementation-ready solution

NOTE: These tests were written for JourneyOrchestrator which has been replaced
by OperationsOrchestrator. Tests are skipped until refactored.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pytest
from symphainy_platform.runtime.intent_model import Intent
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.realms.operations.orchestrators.operations_orchestrator import OperationsOrchestrator
from symphainy_platform.runtime.state_surface import StateSurface
from tests.infrastructure.test_fixtures import test_public_works


@pytest.fixture
def operations_orchestrator(test_public_works):
    """Create Operations Orchestrator with test dependencies."""
    return OperationsOrchestrator(public_works=test_public_works)


@pytest.fixture
def test_state_surface(test_public_works, test_redis, test_arango):
    """Create test state surface."""
    from symphainy_platform.foundations.public_works.abstractions.state_abstraction import StateManagementAbstraction
    
    state_abstraction = StateManagementAbstraction(
        redis_adapter=test_redis,
        arango_adapter=test_arango
    )
    
    file_storage = test_public_works.get_file_storage_abstraction() if test_public_works else None
    
    return StateSurface(
        state_abstraction=state_abstraction,
        file_storage=file_storage
    )


@pytest.fixture
def test_context(test_state_surface):
    """Create test execution context."""
    return ExecutionContext(
        session_id="test_session_blueprint",
        tenant_id="test_tenant",
        user_id="test_user",
        state_surface=test_state_surface
    )


@pytest.fixture
async def mock_workflow_state(test_state_surface):
    """Create mock workflow in state surface."""
    workflow_data = {
        "workflow_id": "test_workflow_123",
        "description": "Test insurance policy processing workflow",
        "steps": [
            {
                "step": 1,
                "name": "Receive Policy File",
                "actor": "human",
                "description": "Manual file upload"
            },
            {
                "step": 2,
                "name": "Validate Policy",
                "actor": "legacy_system",
                "description": "Legacy validation system"
            },
            {
                "step": 3,
                "name": "Process Policy",
                "actor": "human",
                "description": "Manual policy processing"
            }
        ],
        "decision_points": 1,
        "actors": ["human", "legacy_system"]
    }
    
    await test_state_surface.set_execution_state(
        "workflow_test_workflow_123",
        "test_tenant",
        {
            "artifacts": {
                "workflow": workflow_data
            }
        }
    )
    
    return workflow_data


@pytest.fixture
async def mock_coexistence_analysis(test_state_surface):
    """Create mock coexistence analysis in state surface."""
    analysis_data = {
        "workflow_id": "test_workflow_123",
        "existing_processes": [
            {
                "process_id": "legacy_process_456",
                "name": "Legacy Policy Processing",
                "interaction_type": "dependency",
                "severity": "medium",
                "description": "Workflow depends on legacy process"
            }
        ],
        "integration_points": [
            {
                "point": "policy_status_update",
                "type": "external_system",
                "system_name": "Legacy Policy System",
                "conflicts": 0,
                "dependencies": 1
            }
        ],
        "conflicts": [],
        "dependencies": [
            {
                "from": "test_workflow_123",
                "to": "legacy_process_456",
                "type": "depends_on"
            }
        ]
    }
    
    await test_state_surface.set_execution_state(
        "coexistence_analysis_test_workflow_123",
        "test_tenant",
        {
            "artifacts": {
                "coexistence_analysis": analysis_data
            }
        }
    )
    
    return analysis_data


@pytest.mark.asyncio
@pytest.mark.skip(reason="Tests need to be refactored for Operations Realm - uses old JourneyOrchestrator")
async def test_create_blueprint(journey_orchestrator, test_context, mock_workflow_state, mock_coexistence_analysis):
    """Test create_blueprint generates comprehensive blueprint with all components."""
    intent = Intent(
        intent_type="create_blueprint",
        parameters={
            "workflow_id": "test_workflow_123"
        }
    )
    
    result = await journey_orchestrator.handle_intent(intent, test_context)
    
    # Verify result structure
    assert "artifacts" in result
    assert "events" in result
    
    blueprint = result["artifacts"]["blueprint"]
    
    # Verify blueprint has all required components
    assert "blueprint_id" in blueprint
    assert "workflow_id" in blueprint
    
    # 1. Current State
    assert "current_state" in blueprint
    assert "description" in blueprint["current_state"]
    assert "workflow_chart" in blueprint["current_state"]
    assert "workflow_definition" in blueprint["current_state"]
    
    # 2. Coexistence State
    assert "coexistence_state" in blueprint
    assert "description" in blueprint["coexistence_state"]
    assert "workflow_chart" in blueprint["coexistence_state"]
    assert "workflow_definition" in blueprint["coexistence_state"]
    
    # 3. Roadmap
    assert "roadmap" in blueprint
    assert "description" in blueprint["roadmap"]
    assert "phases" in blueprint["roadmap"]
    assert len(blueprint["roadmap"]["phases"]) == 3  # Foundation Setup, Parallel Operation, Full Migration
    assert "timeline" in blueprint["roadmap"]
    
    # 4. Responsibility Matrix
    assert "responsibility_matrix" in blueprint
    assert "description" in blueprint["responsibility_matrix"]
    assert "note" in blueprint["responsibility_matrix"]
    assert "responsibilities" in blueprint["responsibility_matrix"]
    
    # Verify responsibility matrix structure
    for responsibility in blueprint["responsibility_matrix"]["responsibilities"]:
        assert "step" in responsibility
        assert "human" in responsibility
        assert "ai_symphainy" in responsibility
        assert "external_systems" in responsibility
    
    # 5. Sections
    assert "sections" in blueprint
    assert len(blueprint["sections"]) > 0
    
    # Verify events
    assert len(result["events"]) > 0
    assert result["events"][0]["type"] == "blueprint_created"
    
    print(f"✅ Blueprint created: {blueprint['blueprint_id']}")
    print(f"   - Current state steps: {len(blueprint['current_state']['workflow_definition'].get('steps', []))}")
    print(f"   - Coexistence state steps: {len(blueprint['coexistence_state']['workflow_definition'].get('steps', []))}")
    print(f"   - Roadmap phases: {len(blueprint['roadmap']['phases'])}")
    print(f"   - Responsibility matrix entries: {len(blueprint['responsibility_matrix']['responsibilities'])}")


@pytest.mark.asyncio
@pytest.mark.skip(reason="Tests need to be refactored for Operations Realm - uses old JourneyOrchestrator")
async def test_create_solution_from_blueprint(
    journey_orchestrator,
    test_context,
    mock_workflow_state,
    mock_coexistence_analysis
):
    """Test create_solution_from_blueprint converts blueprint to implementation-ready solution."""
    # First create a blueprint
    create_intent = Intent(
        intent_type="create_blueprint",
        parameters={
            "workflow_id": "test_workflow_123"
        }
    )
    
    blueprint_result = await journey_orchestrator.handle_intent(create_intent, test_context)
    blueprint = blueprint_result["artifacts"]["blueprint"]
    blueprint_id = blueprint["blueprint_id"]
    
    # Store blueprint in execution state for solution creation
    await test_context.state_surface.set_execution_state(
        f"blueprint_{blueprint_id}",
        test_context.tenant_id,
        {
            "artifacts": {
                "blueprint": blueprint
            }
        }
    )
    
    # Now create solution from blueprint
    solution_intent = Intent(
        intent_type="create_solution_from_blueprint",
        parameters={
            "blueprint_id": blueprint_id
        }
    )
    
    solution_result = await journey_orchestrator.handle_intent(solution_intent, test_context)
    
    # Verify result structure
    assert "artifacts" in solution_result
    assert "events" in solution_result
    
    solution = solution_result["artifacts"]["solution"]
    
    # Verify solution structure
    assert "solution_id" in solution
    assert "solution" in solution
    assert "source" in solution
    assert solution["source"] == "blueprint"
    assert solution["source_id"] == blueprint_id
    
    # Verify solution has required fields
    solution_data = solution["solution"]
    assert "solution_id" in solution_data
    assert "context" in solution_data
    assert "domain_service_bindings" in solution_data
    assert "supported_intents" in solution_data
    
    # Verify solution includes journey intents
    supported_intents = solution_data["supported_intents"]
    assert "analyze_coexistence" in supported_intents
    assert "create_blueprint" in supported_intents
    assert "create_workflow" in supported_intents
    assert "create_solution_from_blueprint" in supported_intents
    
    # Verify events
    assert len(solution_result["events"]) > 0
    assert solution_result["events"][0]["type"] == "solution_created_from_blueprint"
    assert solution_result["events"][0]["solution_id"] == solution["solution_id"]
    assert solution_result["events"][0]["blueprint_id"] == blueprint_id
    
    print(f"✅ Solution created from blueprint: {solution['solution_id']}")
    print(f"   - Source: {solution['source']}")
    print(f"   - Supported intents: {len(supported_intents)}")


@pytest.mark.asyncio
@pytest.mark.skip(reason="Tests need to be refactored for Operations Realm - uses old JourneyOrchestrator")
async def test_blueprint_to_solution_end_to_end(
    journey_orchestrator,
    test_context,
    mock_workflow_state,
    mock_coexistence_analysis
):
    """Test end-to-end flow: analyze coexistence → create blueprint → create solution."""
    # Step 1: Analyze coexistence (if not already done)
    analyze_intent = Intent(
        intent_type="analyze_coexistence",
        parameters={
            "workflow_id": "test_workflow_123"
        }
    )
    
    analyze_result = await journey_orchestrator.handle_intent(analyze_intent, test_context)
    assert "artifacts" in analyze_result
    
    # Step 2: Create blueprint
    blueprint_intent = Intent(
        intent_type="create_blueprint",
        parameters={
            "workflow_id": "test_workflow_123"
        }
    )
    
    blueprint_result = await journey_orchestrator.handle_intent(blueprint_intent, test_context)
    blueprint = blueprint_result["artifacts"]["blueprint"]
    blueprint_id = blueprint["blueprint_id"]
    
    # Store blueprint for solution creation
    await test_context.state_surface.set_execution_state(
        f"blueprint_{blueprint_id}",
        test_context.tenant_id,
        {
            "artifacts": {
                "blueprint": blueprint
            }
        }
    )
    
    # Step 3: Create solution from blueprint
    solution_intent = Intent(
        intent_type="create_solution_from_blueprint",
        parameters={
            "blueprint_id": blueprint_id
        }
    )
    
    solution_result = await journey_orchestrator.handle_intent(solution_intent, test_context)
    solution = solution_result["artifacts"]["solution"]
    
    # Verify end-to-end flow
    assert blueprint_id is not None
    assert solution["solution_id"] is not None
    assert solution["source"] == "blueprint"
    assert solution["source_id"] == blueprint_id
    
    print(f"✅ End-to-end flow complete:")
    print(f"   1. Coexistence analyzed")
    print(f"   2. Blueprint created: {blueprint_id}")
    print(f"   3. Solution created: {solution['solution_id']}")
