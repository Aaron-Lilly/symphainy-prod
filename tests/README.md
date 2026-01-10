# Symphainy Platform Test Suite

**Status:** 🚧 **IN PROGRESS** - Week 0 Scaffolding  
**Purpose:** Comprehensive testing infrastructure for platform validation

---

## 🎯 Overview

This test suite provides:

1. **Comprehensive Test Coverage** - Unit, Integration, E2E tests
2. **Platform Validation** - Runtime Plane, Agents, Realms, Experience
3. **CI/CD Integration** - Fast feedback loops
4. **Real Infrastructure Testing** - Redis, ArangoDB support

---

## 📁 Test Structure

```
tests/
├── conftest.py                    # Global fixtures
├── pytest.ini                     # Pytest configuration
├── README.md                      # This file
│
├── unit/                          # Unit tests (fast, isolated)
│   ├── runtime/                   # Runtime Plane tests
│   ├── agentic/                   # Agent Foundation tests
│   ├── realms/                    # Realm tests
│   └── experience/                # Experience Plane tests
│
├── integration/                   # Integration tests
│   ├── runtime/                   # Runtime integration tests
│   ├── cross_realm/               # Cross-realm communication
│   └── saga/                      # Saga integration tests
│
├── e2e/                          # E2E tests (full platform)
│   └── platform/                  # Full platform E2E tests
│
├── fixtures/                      # Test fixtures
├── utils/                         # Test utilities
└── config/                        # Test configuration
```

---

## 🚀 Quick Start

### Prerequisites

```bash
# Install test dependencies
cd /home/founders/demoversion/symphainy_source_code
pip3 install -r tests/requirements.txt
```

### Environment Setup

```bash
# Set up test environment
export TEST_USE_REAL_INFRASTRUCTURE=false  # Use mocks for fast tests
export TEST_REDIS_URL=redis://localhost:6379
export TEST_ARANGODB_URL=http://localhost:8529
```

---

## 📋 Running Tests

### Run All Tests

```bash
cd /home/founders/demoversion/symphainy_source_code
pytest tests/ -v
```

### Run by Category

```bash
# Unit tests (fast)
pytest tests/unit/ -v -m unit

# Integration tests
pytest tests/integration/ -v -m integration

# E2E tests
pytest tests/e2e/ -v -m e2e
```

### Run with Markers

```bash
# Critical tests only
pytest tests/ -v -m critical

# Runtime Plane tests
pytest tests/ -v -m runtime

# Fast tests only
pytest tests/ -v -m fast
```

---

## 📝 Adding Tests

### Test File Structure

```python
import pytest
from typing import Dict, Any

@pytest.mark.unit
@pytest.mark.runtime
class TestRuntimeFeature:
    @pytest.mark.asyncio
    async def test_feature(self, mock_session, mock_intent):
        # Test implementation
        assert True
```

### Test Markers

- `@pytest.mark.unit` - Unit test
- `@pytest.mark.integration` - Integration test
- `@pytest.mark.e2e` - E2E test
- `@pytest.mark.runtime` - Runtime Plane test
- `@pytest.mark.critical` - Critical test

---

## 🔧 Test Configuration

### Using Mocks (Default)

```bash
export TEST_USE_REAL_INFRASTRUCTURE=false
pytest tests/ -v
```

### Using Real Infrastructure

```bash
export TEST_USE_REAL_INFRASTRUCTURE=true
export TEST_REDIS_URL=redis://localhost:6379
export TEST_ARANGODB_URL=http://localhost:8529
pytest tests/ -v
```

---

## 📚 Test Fixtures

Available fixtures (see `conftest.py`):

- `project_root_path` - Project root Path object
- `test_config` - Test configuration dictionary
- `mock_redis` - Mock Redis client
- `mock_arangodb` - Mock ArangoDB client
- `mock_session` - Mock session dictionary
- `mock_intent` - Mock intent dictionary

---

## 🐛 Troubleshooting

### Import Errors

```bash
# Ensure pytest.ini pythonpath is correct
# Run from project root
cd /home/founders/demoversion/symphainy_source_code
pytest tests/ -v
```

### Infrastructure Not Available

Tests will skip gracefully if infrastructure unavailable when using mocks.

---

**Last Updated:** January 2026
