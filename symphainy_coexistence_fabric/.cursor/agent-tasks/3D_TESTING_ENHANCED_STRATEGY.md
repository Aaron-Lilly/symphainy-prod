# 3D Testing Enhanced Strategy: Demo-Ready Test Suite

**Status:** 📋 **ENHANCEMENT** - Based on Platform Audit (January 27, 2026)

## Executive Summary

This document enhances the original 3D testing strategy based on a comprehensive audit of the rebuilt platform. The goal is to achieve **"demo ready"** status when all tests pass.

### Key Findings from Platform Audit

| Component | Count | Notes |
|-----------|-------|-------|
| Solutions | 8 | CoexistenceSolution, ContentSolution, InsightsSolution, etc. |
| Journeys | 33 | Across all solutions |
| MCP Servers | 8 | One per solution |
| Intent Services | 50+ | New services in symphainy_coexistence_fabric |

---

## 1. Missing Test Dimensions

The original 3D strategy covers Solution → Journey → Intent but misses several critical dimensions:

### 1.1 MCP Server Testing (NEW DIMENSION)

**Why Critical:** MCP Servers expose SOA APIs as tools for agents. If MCP registration fails, agents can't use platform capabilities.

```python
# tests/3d/mcp/test_{solution}_mcp_server.py

class TestContentSolutionMCPServer:
    """Test MCP Server tool registration and invocation."""
    
    def test_all_soa_apis_registered_as_tools(self):
        """Every journey's SOA API should be registered as an MCP tool."""
        solution = ContentSolution()
        mcp_server = ContentSolutionMCPServer(solution)
        
        # Verify tool count matches SOA API count
        total_soa_apis = sum(
            len(journey.get_soa_apis()) 
            for journey in solution.get_journeys().values()
        )
        assert len(mcp_server.tools) >= total_soa_apis
    
    def test_tool_naming_convention(self):
        """Tools should follow {prefix}_{action} naming."""
        # content_upload, content_parse, etc.
        for tool in mcp_server.tools:
            assert tool.name.startswith("content_")
    
    def test_tool_invocation_routes_to_journey(self):
        """Tool invocation should route to correct journey."""
        result = await mcp_server.call_tool("content_upload", {...})
        assert result["success"]
```

### 1.2 Solution Initializer Testing (NEW DIMENSION)

**Why Critical:** `solution_initializer.py` is the startup procedure. If this fails, no solutions are available.

```python
# tests/3d/startup/test_solution_initializer.py

class TestSolutionInitializer:
    """Test platform startup and solution registration."""
    
    async def test_all_8_solutions_initialized(self):
        """All 8 platform solutions should be initialized."""
        services = await initialize_solutions(
            public_works=mock_public_works,
            state_surface=mock_state_surface,
            solution_registry=SolutionRegistry()
        )
        
        assert services.coexistence is not None
        assert services.content is not None
        assert services.insights is not None
        assert services.operations is not None
        assert services.outcomes is not None
        assert services.security is not None
        assert services.journey is not None
        assert services.control_tower is not None
    
    async def test_solutions_registered_in_registry(self, solution_registry):
        """All solutions should be registered and active."""
        for solution_id in ["coexistence", "content_solution", ...]:
            assert solution_registry.get_solution(solution_id) is not None
            assert solution_registry.is_solution_active(solution_id)
    
    async def test_compose_journey_intents_registered(self, intent_registry):
        """compose_journey intent should be registered for all solutions."""
        for solution_id in ["coexistence", "content_solution", ...]:
            handler = intent_registry.get_handler("compose_journey")
            assert handler is not None
```

### 1.3 GuideAgent Testing (NEW DIMENSION)

**Why Critical:** GuideAgent is the primary user-facing AI. If it can't discover or call MCP tools, the platform appears broken.

```python
# tests/3d/agents/test_guide_agent.py

class TestGuideAgent:
    """Test GuideAgent capabilities."""
    
    async def test_query_curator_for_mcp_tools(self):
        """GuideAgent should discover all MCP tools via Curator."""
        guide_journey = GuideAgentJourney(curator=mock_curator)
        tools = await guide_journey._query_curator_for_mcp_tools()
        
        # Should find tools from all solutions
        tool_prefixes = {t["tool_name"].split("_")[0] for t in tools}
        expected_prefixes = {"coexist", "content", "insights", "ops", "outcomes", "security", "tower"}
        assert expected_prefixes.issubset(tool_prefixes)
    
    async def test_call_orchestrator_mcp_tool(self):
        """GuideAgent should be able to call any MCP tool."""
        result = await guide_journey._call_orchestrator_mcp_tool(
            tool_name="content_upload",
            params={"file_path": "/tmp/test.txt"},
            context=mock_context
        )
        assert "result" in result or "error" in result
    
    async def test_liaison_agent_handoff(self):
        """GuideAgent should be able to hand off to Liaison Agents."""
        result = await guide_journey._route_to_liaison_agent(
            context=mock_context,
            params={
                "pillar_type": "content",
                "conversation_history": [...],
                "user_query": "Help me upload a file"
            },
            journey_execution_id="test_123"
        )
        assert result["success"]
        assert "liaison_agent_id" in result
```

### 1.4 Tenant Isolation Testing (NEW DIMENSION)

**Why Critical:** Multi-tenancy is built-in. Cross-tenant data leakage would be catastrophic.

```python
# tests/3d/security/test_tenant_isolation.py

class TestTenantIsolation:
    """Test multi-tenant isolation."""
    
    async def test_artifacts_isolated_by_tenant(self):
        """Tenant A cannot access Tenant B's artifacts."""
        # Create artifact for tenant_a
        await content_solution.handle_intent(
            intent=upload_intent,
            context=ExecutionContext(tenant_id="tenant_a", ...)
        )
        
        # Try to retrieve with tenant_b
        result = await content_solution.handle_intent(
            intent=retrieve_intent,
            context=ExecutionContext(tenant_id="tenant_b", ...)
        )
        assert result["success"] is False or result["artifacts"] == {}
    
    async def test_state_surface_isolated_by_tenant(self):
        """State Surface enforces tenant isolation."""
        # Set state for tenant_a
        await state_surface.set_session_state(
            key="test_key",
            value={"secret": "tenant_a_data"},
            tenant_id="tenant_a"
        )
        
        # Try to get with tenant_b
        result = await state_surface.get_session_state(
            key="test_key",
            tenant_id="tenant_b"
        )
        assert result is None
```

### 1.5 Structured Artifact Testing (NEW DIMENSION)

**Why Critical:** All outputs use the structured artifact pattern. If artifacts are malformed, frontend can't render them.

```python
# tests/3d/artifacts/test_structured_artifacts.py

class TestStructuredArtifacts:
    """Test structured artifact creation and validation."""
    
    def test_artifact_has_required_fields(self):
        """All artifacts must have result_type, semantic_payload, renderings."""
        artifact = create_structured_artifact(
            result_type="file_upload_result",
            semantic_payload={"file_id": "123"},
            renderings={"summary": "File uploaded"}
        )
        
        assert "result_type" in artifact
        assert "semantic_payload" in artifact
        assert "renderings" in artifact
    
    def test_artifact_lifecycle_states(self):
        """Artifacts should transition: PENDING → READY."""
        artifact = await state_surface.register_artifact(...)
        assert artifact["status"] == "PENDING"
        
        await state_surface.mark_artifact_ready(artifact["artifact_id"])
        updated = await state_surface.get_artifact(artifact["artifact_id"])
        assert updated["status"] == "READY"
```

---

## 2. Enhanced Test Structure

### Recommended Directory Structure

```
tests/
├── 3d/
│   ├── intent/                           # Level 1: Intent Tests
│   │   ├── content/
│   │   │   ├── test_ingest_file_service.py
│   │   │   ├── test_parse_content_service.py
│   │   │   └── ...
│   │   ├── insights/
│   │   │   ├── test_assess_data_quality_service.py
│   │   │   ├── test_map_relationships_service.py
│   │   │   └── ...
│   │   ├── operations/
│   │   │   ├── test_generate_sop_service.py
│   │   │   ├── test_analyze_coexistence_service.py
│   │   │   └── ...
│   │   ├── outcomes/
│   │   │   ├── test_synthesize_outcome_service.py
│   │   │   ├── test_create_poc_service.py
│   │   │   └── ...
│   │   └── security/
│   │       ├── test_authenticate_user_service.py
│   │       ├── test_create_session_service.py
│   │       └── ...
│   │
│   ├── journey/                          # Level 2: Journey Tests
│   │   ├── coexistence/
│   │   │   ├── test_introduction_journey.py
│   │   │   ├── test_navigation_journey.py
│   │   │   └── test_guide_agent_journey.py
│   │   ├── content_solution/
│   │   │   ├── test_file_upload_journey.py
│   │   │   ├── test_file_parsing_journey.py
│   │   │   └── ...
│   │   └── .../
│   │
│   ├── solution/                         # Level 3: Solution Tests
│   │   ├── test_coexistence_solution.py
│   │   ├── test_content_solution.py
│   │   ├── test_insights_solution.py
│   │   ├── test_operations_solution.py
│   │   ├── test_outcomes_solution.py
│   │   ├── test_security_solution.py
│   │   ├── test_journey_solution.py
│   │   └── test_control_tower.py
│   │
│   ├── mcp/                              # NEW: MCP Server Tests
│   │   ├── test_coexistence_mcp_server.py
│   │   ├── test_content_mcp_server.py
│   │   └── ...
│   │
│   ├── agents/                           # NEW: Agent Tests
│   │   ├── test_guide_agent.py
│   │   ├── test_liaison_agents.py
│   │   └── test_agent_handoffs.py
│   │
│   ├── startup/                          # NEW: Startup/Initialization Tests
│   │   ├── test_solution_initializer.py
│   │   ├── test_service_factory.py
│   │   └── test_experience_startup.py
│   │
│   ├── security/                         # NEW: Security Tests
│   │   ├── test_tenant_isolation.py
│   │   ├── test_auth_flow.py
│   │   └── test_authorization.py
│   │
│   └── artifacts/                        # NEW: Artifact Tests
│       ├── test_structured_artifacts.py
│       └── test_artifact_lifecycle.py
│
├── infrastructure/
│   ├── docker-compose.3d-test.yml       # Full test environment
│   ├── wait_for_services.py             # Health check script
│   └── test_data_seeder.py              # Test data setup
│
└── e2e/
    ├── test_file_to_insight_flow.py     # Upload → Parse → Analyze
    ├── test_poc_to_roadmap_flow.py      # POC → Blueprint → Roadmap
    └── test_guide_to_liaison_flow.py    # Guide → Liaison → Specialist
```

---

## 3. Test Coverage Requirements

### For "Demo Ready" Status

| Test Category | Required Coverage | Current | Gap |
|---------------|-------------------|---------|-----|
| Intent Services | 100% (50+ services) | 0% | 50+ tests |
| Journey Orchestrators | 100% (33 journeys) | 0% | 33 tests |
| Solution Handlers | 100% (8 solutions) | 0% | 8 tests |
| MCP Servers | 100% (8 servers) | 0% | 8 tests |
| compose_journey Flow | 100% | 0% | 8 tests |
| Agent Capabilities | 100% | 0% | 3 tests |
| Tenant Isolation | 100% | 0% | 5 tests |
| Artifact Lifecycle | 100% | 0% | 5 tests |
| Startup/Init | 100% | 0% | 3 tests |

**Total Estimated Tests Needed: ~120+ test files**

---

## 4. Demo-Ready Checklist

### Critical Path Tests (Must Pass for Demo)

- [ ] **Startup:** All 8 solutions initialize successfully
- [ ] **MCP Tools:** All MCP tools are registered and callable
- [ ] **GuideAgent:** Can discover tools, call tools, hand off to Liaison
- [ ] **File Upload Flow:** Upload → Parse → Embed → Store works end-to-end
- [ ] **Insights Flow:** Quality assessment → Analysis → Report works
- [ ] **POC Flow:** POC creation → Blueprint → Roadmap works
- [ ] **Control Tower:** Platform stats visible, solution management works
- [ ] **Security:** Auth flow works, tenant isolation enforced

### Visual Demo Path Tests

For demos, users typically:
1. Land on Coexistence (introduction)
2. Chat with GuideAgent
3. Upload a file
4. Get insights/analysis
5. Generate a POC/roadmap
6. View in Control Tower

Each of these should have dedicated E2E tests.

---

## 5. Test Data Requirements

### Seed Data for Tests

```python
# tests/infrastructure/test_data_seeder.py

TEST_DATA = {
    "files": [
        {"name": "sample_policy.pdf", "type": "insurance_policy"},
        {"name": "claims_data.csv", "type": "structured_data"},
        {"name": "workflow.bpmn", "type": "workflow_definition"},
    ],
    "tenants": [
        {"id": "demo_tenant", "name": "Demo Corp"},
        {"id": "test_tenant", "name": "Test Corp"},
    ],
    "users": [
        {"id": "demo_user", "tenant": "demo_tenant", "role": "admin"},
    ]
}
```

---

## 6. CI/CD Enhancements

### Enhanced GitHub Actions Workflow

```yaml
# .github/workflows/3d-tests.yml

name: 3D Test Suite

on:
  pull_request:
    branches: [main, cursor/*]

jobs:
  startup-tests:
    name: Startup & Initialization
    runs-on: ubuntu-latest
    steps:
      - name: Run startup tests
        run: pytest tests/3d/startup/ -v --tb=short

  intent-tests:
    name: Intent Service Tests
    needs: startup-tests
    strategy:
      matrix:
        realm: [content, insights, operations, outcomes, security]
    steps:
      - name: Run ${{ matrix.realm }} intent tests
        run: pytest tests/3d/intent/${{ matrix.realm }}/ -v

  journey-tests:
    name: Journey Orchestrator Tests
    needs: intent-tests
    steps:
      - name: Run journey tests
        run: pytest tests/3d/journey/ -v

  solution-tests:
    name: Solution Tests
    needs: journey-tests
    steps:
      - name: Run solution tests
        run: pytest tests/3d/solution/ -v

  mcp-tests:
    name: MCP Server Tests
    needs: solution-tests
    steps:
      - name: Run MCP tests
        run: pytest tests/3d/mcp/ -v

  agent-tests:
    name: Agent Tests
    needs: mcp-tests
    steps:
      - name: Run agent tests
        run: pytest tests/3d/agents/ -v

  security-tests:
    name: Security Tests
    needs: agent-tests
    steps:
      - name: Run security tests
        run: pytest tests/3d/security/ -v

  e2e-tests:
    name: E2E Demo Path Tests
    needs: [security-tests]
    steps:
      - name: Spin up full environment
        run: docker-compose -f tests/infrastructure/docker-compose.3d-test.yml up -d
      - name: Wait for services
        run: python tests/infrastructure/wait_for_services.py
      - name: Seed test data
        run: python tests/infrastructure/test_data_seeder.py
      - name: Run E2E tests
        run: pytest tests/e2e/ -v
      - name: Teardown
        run: docker-compose -f tests/infrastructure/docker-compose.3d-test.yml down
```

---

## 7. Contract Compliance Validation

### Automated Contract-to-Implementation Check

```python
# tests/3d/compliance/test_contract_compliance.py

class TestContractCompliance:
    """Verify implementations match contracts."""
    
    @pytest.mark.parametrize("contract_path", glob("docs/intent_contracts/**/intent_*.md"))
    def test_intent_contract_has_implementation(self, contract_path):
        """Every intent contract should have an implementation."""
        intent_name = extract_intent_name(contract_path)
        
        # Check implementation exists
        impl_path = find_implementation(intent_name)
        assert impl_path is not None, f"No implementation for {intent_name}"
    
    @pytest.mark.parametrize("journey_contract", glob("docs/journey_contracts/**/*.md"))
    def test_journey_contract_has_implementation(self, journey_contract):
        """Every journey contract should have an implementation."""
        journey_name = extract_journey_name(journey_contract)
        
        # Check implementation exists
        impl_path = find_journey_implementation(journey_name)
        assert impl_path is not None, f"No implementation for {journey_name}"
```

---

## 8. Summary of Enhancements

| Enhancement | Priority | Rationale |
|-------------|----------|-----------|
| MCP Server Tests | **Critical** | Agents can't function without MCP tools |
| Solution Initializer Tests | **Critical** | Platform won't start without this |
| GuideAgent Tests | **Critical** | Primary user-facing AI |
| Tenant Isolation Tests | **Critical** | Security requirement |
| Structured Artifact Tests | High | Frontend rendering depends on this |
| Contract Compliance Tests | High | Ensures contracts match implementations |
| E2E Demo Path Tests | High | Validates actual demo flow |
| Security Flow Tests | Medium | Auth/authz validation |

---

**Last Updated:** January 27, 2026  
**Author:** Platform Audit Team  
**Status:** 📋 **ENHANCED PLAN** - Ready for implementation
