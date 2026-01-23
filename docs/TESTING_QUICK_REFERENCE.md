# Testing Quick Reference Guide

**Purpose:** Quick reference for running pre-browser tests

---

## Quick Start

### Run All Tests
```bash
./scripts/run_pre_browser_tests.sh
```

### Run Specific Phase
```bash
# Phase 1: Infrastructure
./scripts/run_pre_browser_tests.sh --phase 1

# Phase 2: Core Flows
./scripts/run_pre_browser_tests.sh --phase 2

# Phase 3: Data & Resilience
./scripts/run_pre_browser_tests.sh --phase 3

# Phase 4: Performance
./scripts/run_pre_browser_tests.sh --phase 4

# Phase 5: Security
./scripts/run_pre_browser_tests.sh --phase 5
```

### Skip Service Startup
```bash
# If services are already running
./scripts/run_pre_browser_tests.sh --skip-startup
```

### Verbose Output
```bash
./scripts/run_pre_browser_tests.sh --verbose
```

---

## Manual Test Execution

### Phase 1: Foundation
```bash
# Start services
./scripts/startup.sh

# Run tests
pytest tests/smoke/test_service_startup.py -v
pytest tests/integration/infrastructure/ -v -m infrastructure
pytest tests/integration/test_basic_integration.py -v
```

### Phase 2: Core Flows
```bash
pytest tests/integration/test_basic_integration.py -v
pytest tests/integration/experience/ -v
pytest tests/integration/realms/ -v
pytest tests/integration/test_architecture_integration.py -v
```

### Phase 3: Data & Resilience
```bash
pytest tests/integration/infrastructure/test_state_abstraction.py -v
pytest tests/integration/test_artifact_storage_smoke.py -v
pytest tests/integration/runtime/test_wal.py -v
pytest tests/integration/test_error_handling_edge_cases.py -v
```

### Phase 4: Performance
```bash
pytest tests/integration/test_performance_load.py -v
```

### Phase 5: Security
```bash
pytest tests/integration/test_auth_security_comprehensive.py -v
pytest tests/integration/test_auth_and_websocket_inline.py -v
```

---

## Test Markers

### Run by Marker
```bash
# Unit tests
pytest tests/ -v -m unit

# Integration tests
pytest tests/ -v -m integration

# Critical tests
pytest tests/ -v -m critical

# Runtime tests
pytest tests/ -v -m runtime

# Realm tests
pytest tests/ -v -m realms
```

---

## Service Health Checks

### Check Service Status
```bash
# All services
docker-compose ps

# Specific service
docker-compose ps runtime experience realms
```

### Manual Health Checks
```bash
# Runtime
curl http://localhost:8000/health

# Experience
curl http://localhost:8001/health
```

### Service Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f runtime
docker-compose logs -f experience
```

---

## Test Results

### View Results
```bash
# Results are saved to:
ls -la docs/test_results/
```

### Latest Results
```bash
ls -t docs/test_results/ | head -1
```

---

## Troubleshooting

### Services Won't Start
```bash
# Check infrastructure
docker-compose ps redis arango consul

# Restart services
docker-compose restart

# View logs
docker-compose logs runtime
```

### Tests Fail to Connect
```bash
# Verify services are running
docker-compose ps

# Check ports
netstat -tuln | grep -E "8000|8001|8002"

# Test connectivity
curl http://localhost:8000/health
curl http://localhost:8001/health
```

### Import Errors
```bash
# Ensure you're in project root
cd /home/founders/demoversion/symphainy_source_code

# Install dependencies
pip install -r requirements.txt
pip install -r tests/requirements.txt
```

---

## Test File Locations

### Smoke Tests
- `tests/smoke/test_service_startup.py`
- `tests/smoke/test_realm_smoke.py`
- `tests/smoke/test_platform_parsing_smoke.py`

### Integration Tests
- `tests/integration/test_basic_integration.py`
- `tests/integration/realms/` - Realm-specific tests
- `tests/integration/infrastructure/` - Infrastructure tests
- `tests/integration/runtime/` - Runtime tests
- `tests/integration/experience/` - Experience tests

### Performance Tests
- `tests/integration/test_performance_load.py`

### Security Tests
- `tests/integration/test_auth_security_comprehensive.py`
- `tests/integration/test_auth_and_websocket_inline.py`

---

## Success Criteria

Before proceeding to browser testing, verify:

- ✅ All services healthy
- ✅ Phase 1 tests pass
- ✅ Phase 2 tests pass (at least one flow per realm)
- ✅ Phase 3 critical tests pass
- ✅ No critical security issues

---

**Last Updated:** January 2026
