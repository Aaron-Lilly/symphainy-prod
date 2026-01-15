# Abstraction Validation Strategy

**Date:** January 2026  
**Status:** 📋 **VALIDATION STRATEGY**  
**Purpose:** Validate refactored abstractions work correctly and are swappable

---

## Executive Summary

**Goal:** Ensure refactored abstractions:
- ✅ Still work with their adapters
- ✅ Are swappable (can swap adapters)
- ✅ Business logic was properly removed
- ✅ Integration works (Runtime, Smart City can use them)

**Strategy:** Multi-layer validation (unit → integration → contract → E2E)

---

## Validation Layers

### Layer 1: Unit Tests (Abstraction + Adapter)

**Purpose:** Test each abstraction with its adapter in isolation

**Pattern:**
```python
# tests/foundations/public_works/test_auth_abstraction.py
import pytest
from symphainy_platform.foundations.public_works.abstractions.auth_abstraction import AuthAbstraction
from symphainy_platform.foundations.public_works.adapters.supabase_adapter import SupabaseAdapter

@pytest.fixture
async def supabase_adapter():
    """Create Supabase adapter for testing."""
    return SupabaseAdapter(
        url=os.getenv("SUPABASE_URL"),
        anon_key=os.getenv("SUPABASE_ANON_KEY"),
        service_key=os.getenv("SUPABASE_SERVICE_KEY")
    )

@pytest.fixture
async def auth_abstraction(supabase_adapter):
    """Create Auth abstraction with Supabase adapter."""
    return AuthAbstraction(supabase_adapter=supabase_adapter)

@pytest.mark.asyncio
async def test_auth_abstraction_authenticate_returns_raw_data(auth_abstraction):
    """Test that authenticate returns raw data (no business logic)."""
    result = await auth_abstraction.authenticate({
        "email": "test@example.com",
        "password": "test_password"
    })
    
    # Should return raw data structure
    assert result is not None
    assert "user_id" in result or "id" in result
    assert "email" in result
    # Should NOT contain SecurityContext (business logic)
    assert not isinstance(result, SecurityContext)
    
@pytest.mark.asyncio
async def test_auth_abstraction_validate_token_returns_raw_data(auth_abstraction):
    """Test that validate_token returns raw data."""
    # Use a valid test token
    result = await auth_abstraction.validate_token("valid_token")
    
    # Should return raw data
    assert result is not None
    assert "user_id" in result or "id" in result
    # Should NOT contain tenant creation logic
    # (test would fail if abstraction creates tenant)
```

**Coverage:**
- ✅ Each abstraction method returns raw data
- ✅ No business logic in abstraction
- ✅ Adapter integration works

---

### Layer 2: Swappability Tests (Adapter Swapping)

**Purpose:** Test that abstractions can swap adapters

**Pattern:**
```python
# tests/foundations/public_works/test_auth_abstraction_swappability.py
import pytest
from symphainy_platform.foundations.public_works.abstractions.auth_abstraction import AuthAbstraction
from symphainy_platform.foundations.public_works.adapters.supabase_adapter import SupabaseAdapter
from symphainy_platform.foundations.public_works.adapters.auth0_adapter import Auth0Adapter  # Mock

@pytest.fixture
async def supabase_adapter():
    """Create Supabase adapter."""
    return SupabaseAdapter(...)

@pytest.fixture
async def auth0_adapter():
    """Create Auth0 adapter (mock for testing)."""
    return Auth0Adapter(...)

@pytest.mark.asyncio
async def test_auth_abstraction_swappable(supabase_adapter, auth0_adapter):
    """Test that Auth abstraction works with different adapters."""
    # Test with Supabase
    auth_supabase = AuthAbstraction(supabase_adapter=supabase_adapter)
    result_supabase = await auth_supabase.authenticate({"email": "...", "password": "..."})
    
    # Test with Auth0
    auth_auth0 = AuthAbstraction(supabase_adapter=auth0_adapter)  # Same interface
    result_auth0 = await auth_auth0.authenticate({"email": "...", "password": "..."})
    
    # Both should return same structure (raw data)
    assert "user_id" in result_supabase or "id" in result_supabase
    assert "user_id" in result_auth0 or "id" in result_auth0
    # Structure should be similar (adapter-agnostic)
```

**Coverage:**
- ✅ Abstractions work with different adapters
- ✅ Return structures are adapter-agnostic
- ✅ No adapter-specific business logic

---

### Layer 3: Contract Tests (Protocol Compliance)

**Purpose:** Test that abstractions comply with protocols

**Pattern:**
```python
# tests/foundations/public_works/test_auth_protocol_compliance.py
import pytest
from symphainy_platform.foundations.public_works.protocols.auth_protocol import AuthenticationProtocol
from symphainy_platform.foundations.public_works.abstractions.auth_abstraction import AuthAbstraction

def test_auth_abstraction_implements_protocol():
    """Test that Auth abstraction implements AuthenticationProtocol."""
    # Check that AuthAbstraction implements the protocol
    assert issubclass(AuthAbstraction, AuthenticationProtocol)
    
    # Check that all protocol methods exist
    assert hasattr(AuthAbstraction, 'authenticate')
    assert hasattr(AuthAbstraction, 'validate_token')
    assert hasattr(AuthAbstraction, 'refresh_token')
    
    # Check method signatures match protocol
    import inspect
    protocol_methods = inspect.signature(AuthenticationProtocol.authenticate)
    impl_methods = inspect.signature(AuthAbstraction.authenticate)
    assert protocol_methods == impl_methods
```

**Coverage:**
- ✅ Abstractions implement protocols correctly
- ✅ Method signatures match protocols
- ✅ Return types match protocols

---

### Layer 4: Integration Tests (Smart City Roles)

**Purpose:** Test that Smart City roles can use abstractions correctly

**Pattern:**
```python
# tests/smart_city/test_security_guard_with_auth_abstraction.py
import pytest
from symphainy_platform.smart_city.services.security_guard import SecurityGuard
from symphainy_platform.foundations.public_works.abstractions.auth_abstraction import AuthAbstraction
from symphainy_platform.foundations.public_works.abstractions.tenant_abstraction import TenantAbstraction

@pytest.fixture
async def security_guard(auth_abstraction, tenant_abstraction):
    """Create Security Guard with abstractions."""
    return SecurityGuard(
        auth_abstraction=auth_abstraction,
        tenant_abstraction=tenant_abstraction
    )

@pytest.mark.asyncio
async def test_security_guard_uses_auth_abstraction(security_guard):
    """Test that Security Guard uses Auth abstraction correctly."""
    # Security Guard should use abstraction for infrastructure
    result = await security_guard.authenticate_user({
        "email": "test@example.com",
        "password": "test_password"
    })
    
    # Security Guard should add business logic (SecurityContext creation)
    assert isinstance(result, SecurityContext)
    assert result.user_id is not None
    assert result.tenant_id is not None
    assert result.roles is not None
    assert result.permissions is not None
```

**Coverage:**
- ✅ Smart City roles can use abstractions
- ✅ Business logic is in Smart City roles (not abstractions)
- ✅ Integration works end-to-end

---

### Layer 5: End-to-End Tests (Container-Based)

**Purpose:** Test abstractions in real environment (containers running)

**Pattern:**
```python
# tests/integration/test_abstractions_e2e.py
import pytest
import httpx
from symphainy_platform.foundations.public_works.foundation_service import PublicWorksFoundationService

@pytest.fixture(scope="session")
def docker_compose():
    """Start Docker containers for E2E testing."""
    import subprocess
    subprocess.run(["docker-compose", "up", "-d"], check=True)
    yield
    subprocess.run(["docker-compose", "down"], check=True)

@pytest.fixture
async def public_works_foundation(docker_compose):
    """Create Public Works Foundation with real adapters."""
    foundation = PublicWorksFoundationService()
    await foundation.initialize()
    return foundation

@pytest.mark.asyncio
@pytest.mark.integration
async def test_auth_abstraction_e2e(public_works_foundation):
    """Test Auth abstraction end-to-end with real Supabase."""
    auth_abstraction = public_works_foundation.get_auth_abstraction()
    
    # Test authentication
    result = await auth_abstraction.authenticate({
        "email": "test@example.com",
        "password": "test_password"
    })
    
    # Should return raw data
    assert result is not None
    assert "user_id" in result or "id" in result
    
@pytest.mark.asyncio
@pytest.mark.integration
async def test_telemetry_abstraction_e2e(public_works_foundation):
    """Test Telemetry abstraction end-to-end with real OpenTelemetry."""
    telemetry_abstraction = public_works_foundation.get_telemetry_abstraction()
    
    # Test metric collection
    from symphainy_platform.foundations.public_works.protocols.telemetry_protocol import TelemetryData, TelemetryType
    telemetry_data = TelemetryData(
        name="test_metric",
        type=TelemetryType.METRIC,
        value=1.0
    )
    
    result = await telemetry_abstraction.collect_metric(telemetry_data)
    assert result is True
```

**Coverage:**
- ✅ Abstractions work with real adapters (Supabase, Redis, etc.)
- ✅ Containers are running and accessible
- ✅ End-to-end integration works

---

## Validation Checklist

### ✅ Phase 1: Unit Tests (Week 1)

**For Each Refactored Abstraction:**

- [ ] **Test returns raw data** (not business objects)
- [ ] **Test no business logic** (no tenant creation, no role extraction)
- [ ] **Test adapter integration** (works with adapter)
- [ ] **Test error handling** (proper error propagation)

**Example Test Structure:**
```python
# tests/foundations/public_works/test_auth_abstraction.py
class TestAuthAbstraction:
    async def test_authenticate_returns_raw_data(self):
        """Test authenticate returns raw data."""
        pass
    
    async def test_authenticate_no_tenant_creation(self):
        """Test authenticate does NOT create tenant."""
        pass
    
    async def test_validate_token_returns_raw_data(self):
        """Test validate_token returns raw data."""
        pass
    
    async def test_validate_token_no_role_extraction(self):
        """Test validate_token does NOT extract roles."""
        pass
```

---

### ✅ Phase 2: Swappability Tests (Week 1)

**For Each Abstraction:**

- [ ] **Test with primary adapter** (Supabase, Redis, etc.)
- [ ] **Test with alternative adapter** (Auth0, Memcached, etc. - mock)
- [ ] **Test return structure consistency** (same structure regardless of adapter)

**Example Test Structure:**
```python
# tests/foundations/public_works/test_auth_abstraction_swappability.py
class TestAuthAbstractionSwappability:
    async def test_works_with_supabase(self):
        """Test works with Supabase adapter."""
        pass
    
    async def test_works_with_auth0(self):
        """Test works with Auth0 adapter (mock)."""
        pass
    
    async def test_return_structure_consistent(self):
        """Test return structure is consistent across adapters."""
        pass
```

---

### ✅ Phase 3: Contract Tests (Week 1)

**For Each Abstraction:**

- [ ] **Test implements protocol** (implements correct protocol)
- [ ] **Test method signatures** (match protocol)
- [ ] **Test return types** (match protocol)

**Example Test Structure:**
```python
# tests/foundations/public_works/test_auth_protocol_compliance.py
class TestAuthProtocolCompliance:
    def test_implements_authentication_protocol(self):
        """Test Auth abstraction implements AuthenticationProtocol."""
        pass
    
    def test_method_signatures_match(self):
        """Test method signatures match protocol."""
        pass
```

---

### ✅ Phase 4: Integration Tests (Week 2)

**For Each Smart City Role:**

- [ ] **Test uses abstraction** (role uses abstraction correctly)
- [ ] **Test adds business logic** (role adds business logic)
- [ ] **Test end-to-end flow** (abstraction → role → result)

**Example Test Structure:**
```python
# tests/smart_city/test_security_guard_integration.py
class TestSecurityGuardIntegration:
    async def test_uses_auth_abstraction(self):
        """Test Security Guard uses Auth abstraction."""
        pass
    
    async def test_adds_business_logic(self):
        """Test Security Guard adds business logic (SecurityContext)."""
        pass
    
    async def test_end_to_end_authentication(self):
        """Test end-to-end authentication flow."""
        pass
```

---

### ✅ Phase 5: End-to-End Tests (Week 3)

**For Each Abstraction:**

- [ ] **Test with real containers** (Docker Compose running)
- [ ] **Test with real adapters** (Supabase, Redis, etc.)
- [ ] **Test integration with Runtime** (Runtime can use abstractions)
- [ ] **Test integration with Smart City** (Smart City roles can use abstractions)

**Example Test Structure:**
```python
# tests/integration/test_abstractions_e2e.py
@pytest.mark.integration
class TestAbstractionsE2E:
    async def test_auth_abstraction_e2e(self):
        """Test Auth abstraction end-to-end."""
        pass
    
    async def test_telemetry_abstraction_e2e(self):
        """Test Telemetry abstraction end-to-end."""
        pass
    
    async def test_runtime_uses_abstractions(self):
        """Test Runtime can use abstractions via Smart City."""
        pass
```

---

## Validation Scripts

### Script 1: Run All Validation Tests

```bash
#!/bin/bash
# scripts/validate_abstractions.sh

echo "🔍 Validating Public Works Abstractions..."

# Start containers
echo "📦 Starting containers..."
docker-compose up -d

# Wait for containers to be ready
echo "⏳ Waiting for containers..."
sleep 10

# Run unit tests
echo "🧪 Running unit tests..."
pytest tests/foundations/public_works/ -v

# Run swappability tests
echo "🔄 Running swappability tests..."
pytest tests/foundations/public_works/test_*_swappability.py -v

# Run contract tests
echo "📋 Running contract tests..."
pytest tests/foundations/public_works/test_*_protocol_compliance.py -v

# Run integration tests
echo "🔗 Running integration tests..."
pytest tests/smart_city/test_*_integration.py -v

# Run E2E tests
echo "🌐 Running E2E tests..."
pytest tests/integration/test_abstractions_e2e.py -v --integration

# Stop containers
echo "🛑 Stopping containers..."
docker-compose down

echo "✅ Validation complete!"
```

---

### Script 2: Validate Single Abstraction

```bash
#!/bin/bash
# scripts/validate_abstraction.sh <abstraction_name>

ABSTRACTION=$1

echo "🔍 Validating ${ABSTRACTION}..."

# Run unit tests
pytest tests/foundations/public_works/test_${ABSTRACTION}_abstraction.py -v

# Run swappability tests
pytest tests/foundations/public_works/test_${ABSTRACTION}_abstraction_swappability.py -v

# Run contract tests
pytest tests/foundations/public_works/test_${ABSTRACTION}_protocol_compliance.py -v

echo "✅ Validation complete for ${ABSTRACTION}!"
```

---

### Script 3: Validate Swappability

```bash
#!/bin/bash
# scripts/validate_swappability.sh

echo "🔄 Validating abstraction swappability..."

# Test Auth: Supabase → Auth0 (mock)
pytest tests/foundations/public_works/test_auth_abstraction_swappability.py -v

# Test File Storage: GCS → S3 (mock)
pytest tests/foundations/public_works/test_file_storage_abstraction_swappability.py -v

# Test State: Redis → Memcached (mock)
pytest tests/foundations/public_works/test_state_abstraction_swappability.py -v

echo "✅ Swappability validation complete!"
```

---

## Validation Test Structure

### Test Directory Structure

```
tests/
├── foundations/
│   └── public_works/
│       ├── test_auth_abstraction.py              # Unit tests
│       ├── test_auth_abstraction_swappability.py  # Swappability tests
│       ├── test_auth_protocol_compliance.py       # Contract tests
│       ├── test_telemetry_abstraction.py
│       ├── test_telemetry_abstraction_swappability.py
│       ├── test_telemetry_protocol_compliance.py
│       └── ... (one set per abstraction)
│
├── smart_city/
│   ├── test_security_guard_integration.py        # Integration tests
│   ├── test_city_manager_integration.py
│   ├── test_librarian_integration.py
│   └── ... (one per Smart City role)
│
└── integration/
    ├── test_abstractions_e2e.py                  # E2E tests
    ├── conftest.py                                # E2E fixtures
    └── docker_compose_fixtures.py                 # Container fixtures
```

---

## Validation Criteria

### ✅ Abstraction Validation Criteria

**For Each Abstraction:**

1. **Returns Raw Data**
   - ✅ Returns `Dict[str, Any]` or raw data structure
   - ✅ Does NOT return business objects (SecurityContext, etc.)
   - ✅ Does NOT contain business logic

2. **No Business Logic**
   - ✅ Does NOT create tenants
   - ✅ Does NOT extract roles/permissions
   - ✅ Does NOT validate access
   - ✅ Does NOT make business decisions

3. **Swappable**
   - ✅ Works with primary adapter (Supabase, Redis, etc.)
   - ✅ Works with alternative adapter (Auth0, Memcached, etc. - mock)
   - ✅ Return structure is adapter-agnostic

4. **Protocol Compliant**
   - ✅ Implements correct protocol
   - ✅ Method signatures match protocol
   - ✅ Return types match protocol

---

### ✅ Integration Validation Criteria

**For Each Smart City Role:**

1. **Uses Abstractions**
   - ✅ Role uses abstraction for infrastructure
   - ✅ Role does NOT call adapters directly

2. **Adds Business Logic**
   - ✅ Role adds business logic (SecurityContext, policy validation, etc.)
   - ✅ Business logic is NOT in abstraction

3. **End-to-End Works**
   - ✅ Abstraction → Role → Result flow works
   - ✅ Runtime can use role → role uses abstraction

---

## Validation Workflow

### Step 1: After Each Abstraction Refactoring

1. **Write Unit Tests**
   - Test returns raw data
   - Test no business logic
   - Test adapter integration

2. **Write Swappability Tests**
   - Test with primary adapter
   - Test with alternative adapter (mock)
   - Test return structure consistency

3. **Write Contract Tests**
   - Test protocol compliance
   - Test method signatures

4. **Run Tests**
   ```bash
   pytest tests/foundations/public_works/test_<abstraction>_abstraction.py -v
   ```

---

### Step 2: After All Abstractions Refactored

1. **Write Integration Tests**
   - Test Smart City roles use abstractions
   - Test business logic is in roles

2. **Write E2E Tests**
   - Test with real containers
   - Test with real adapters

3. **Run All Tests**
   ```bash
   ./scripts/validate_abstractions.sh
   ```

---

### Step 3: Validate Swappability

1. **Create Mock Adapters**
   - Mock Auth0 adapter (for Auth abstraction)
   - Mock S3 adapter (for File Storage abstraction)
   - Mock Memcached adapter (for State abstraction)

2. **Run Swappability Tests**
   ```bash
   ./scripts/validate_swappability.sh
   ```

---

## Container-Based Validation

### Docker Compose Test Environment

```yaml
# docker-compose.test.yml
services:
  # Infrastructure services (same as main docker-compose.yml)
  redis:
    image: redis:7-alpine
    # ... same config
  
  supabase:
    image: supabase/postgres:latest
    # ... test Supabase instance
  
  # Test services
  test-runner:
    build:
      context: .
      dockerfile: Dockerfile.test
    depends_on:
      - redis
      - supabase
    environment:
      - REDIS_URL=redis://redis:6379
      - SUPABASE_URL=http://supabase:5432
    command: pytest tests/integration/ -v
```

**Usage:**
```bash
# Run E2E tests with containers
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

---

## Validation Report

### Generate Validation Report

```python
# scripts/generate_validation_report.py
import pytest
import json
from datetime import datetime

def generate_validation_report():
    """Generate validation report for abstractions."""
    report = {
        "timestamp": datetime.now().isoformat(),
        "abstractions": {}
    }
    
    # Run tests and collect results
    # ... test execution logic ...
    
    # Generate report
    with open("validation_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("✅ Validation report generated: validation_report.json")
```

**Report Format:**
```json
{
  "timestamp": "2026-01-XX...",
  "abstractions": {
    "auth_abstraction": {
      "unit_tests": "✅ PASS",
      "swappability_tests": "✅ PASS",
      "contract_tests": "✅ PASS",
      "integration_tests": "✅ PASS",
      "e2e_tests": "✅ PASS"
    },
    "telemetry_abstraction": {
      "unit_tests": "✅ PASS",
      "swappability_tests": "✅ PASS",
      "contract_tests": "✅ PASS",
      "integration_tests": "✅ PASS",
      "e2e_tests": "✅ PASS"
    }
  }
}
```

---

## Quick Validation Commands

### Validate All Abstractions

```bash
# Run all validation tests
./scripts/validate_abstractions.sh

# Or manually
docker-compose up -d
pytest tests/foundations/public_works/ -v
pytest tests/smart_city/ -v
pytest tests/integration/ -v --integration
docker-compose down
```

### Validate Single Abstraction

```bash
# Validate Auth abstraction
./scripts/validate_abstraction.sh auth

# Or manually
pytest tests/foundations/public_works/test_auth_abstraction*.py -v
```

### Validate Swappability

```bash
# Validate all abstractions are swappable
./scripts/validate_swappability.sh

# Or manually
pytest tests/foundations/public_works/test_*_swappability.py -v
```

---

## Success Criteria

### ✅ Validation Passes When:

1. **Unit Tests Pass**
   - ✅ All abstraction unit tests pass
   - ✅ Abstractions return raw data
   - ✅ No business logic in abstractions

2. **Swappability Tests Pass**
   - ✅ Abstractions work with different adapters
   - ✅ Return structures are adapter-agnostic

3. **Contract Tests Pass**
   - ✅ Abstractions implement protocols correctly
   - ✅ Method signatures match protocols

4. **Integration Tests Pass**
   - ✅ Smart City roles can use abstractions
   - ✅ Business logic is in roles (not abstractions)

5. **E2E Tests Pass**
   - ✅ Abstractions work with real containers
   - ✅ Runtime can use abstractions via Smart City
   - ✅ End-to-end flows work

---

## Conclusion

**This validation strategy ensures:**
- ✅ Abstractions work correctly after refactoring
- ✅ Abstractions are swappable
- ✅ Business logic was properly removed
- ✅ Integration works end-to-end

**Timeline:**
- **Week 1:** Write unit, swappability, contract tests (as we refactor)
- **Week 2:** Write integration tests (as we build Smart City roles)
- **Week 3:** Write E2E tests (as we integrate with Runtime)
- **Week 4:** Run full validation suite

**This gives us confidence that refactoring didn't break anything!**
