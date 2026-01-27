# 3D Testing Quick Start Guide

## 🚀 For Cursor Web Agents

This guide helps agents generate 3D tests (Solution → Journey → Intent) from contracts.

## 📍 Location

**Working Directory:** `/home/founders/demoversion/symphainy_source_code/symphainy_coexistence_fabric/`

**Test Location:** `tests/3d/` (to be created)

## ✅ What to Generate

### 1. Intent Tests (Unit-Level)

**Location:** `tests/3d/intent/{realm}/{journey}/test_{intent_name}.py`

**What to Generate:**
- Parameter validation tests
- Return structure tests
- Artifact registration tests
- Event emission tests
- Error handling tests
- Idempotency tests

**Reference:** Intent contract at `docs/intent_contracts/{journey}/{intent_name}.md`

### 2. Journey Tests (Integration-Level)

**Location:** `tests/3d/journey/{solution}/test_{journey_name}.py`

**What to Generate:**
- Intent sequence tests
- Artifact flow tests
- State transition tests
- Error propagation tests

**Reference:** Journey contract at `docs/journey_contracts/{solution}/{journey_name}.md`

### 3. Solution Tests (End-to-End)

**Location:** `tests/3d/solution/test_{solution_name}.py`

**What to Generate:**
- Journey composition tests
- Cross-journey integration tests
- MCP tool interaction tests

**Reference:** Solution contract at `docs/solution_contracts/{solution_path}/{solution_name}.md`

### 4. Test Infrastructure

**Location:** `tests/`

**What to Generate:**
- `docker-compose.test.yml` - Test environment
- `setup_test_db.sh` - Database setup
- `wait_for_services.sh` - Health checks
- `.env.test` - Test configuration

### 5. CI/CD Pipeline

**Location:** `.github/workflows/`

**What to Generate:**
- `3d-tests.yml` - Test execution workflow
- `contract-validation.yml` - Contract validation workflow

## 🎯 Agent Prompt Template

```
Generate 3D test suite for: {level} - {name}

Context:
- Contract: {contract_path}
- Implementation: {implementation_path}
- Level: {intent/journey/solution}

Requirements:
1. Read contract completely
2. Read implementation (if exists)
3. Generate pytest test class
4. Generate tests for all contract sections
5. Include SRE-style tests (resilience, performance)
6. Save to: {test_path}

Test Structure:
- Use pytest fixtures
- Use contract examples for test data
- Validate contract compliance
- Include happy path and failure scenarios
```

## 📋 Checklist Per Test File

- [ ] Read contract completely
- [ ] Read implementation (if exists)
- [ ] Generate test class
- [ ] Generate parameter validation tests
- [ ] Generate return structure tests
- [ ] Generate artifact registration tests
- [ ] Generate event emission tests
- [ ] Generate error handling tests
- [ ] Generate SRE-style tests
- [ ] Use contract examples for test data
- [ ] Validate against implementation
- [ ] Save to correct location

## ⚠️ Important Notes

1. **Tests Don't Run Yet:** Agents generate test code, CI/CD runs it
2. **Test Against Running Services:** Tests will call real services (via Docker)
3. **Use Contract Examples:** Contract JSON examples = test data
4. **Validate Compliance:** Tests validate implementation matches contract
5. **SRE-Style:** Include resilience, performance, error recovery tests

## 🔗 Related Documents

- **Full Strategy:** `3D_TESTING_STRATEGY.md`
- **Examples:** `3D_TESTING_EXAMPLES.md`
- **Contracts:** `docs/intent_contracts/`, `docs/journey_contracts/`, `docs/solution_contracts/`
- **Implementations:** `symphainy_platform/realms/`, `symphainy_platform/solutions/`

---

**Ready to generate tests!** 🎯
