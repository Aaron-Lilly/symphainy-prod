# Test Suite Quick Reference

## 🚀 Quick Start

### Run All Tests (Recommended)
```bash
cd /home/founders/demoversion/symphainy_source_code
python3 tests/integration/test_comprehensive_suite.py
```

### Run Individual Test Suites

**Priority 1: Security (Critical)**
```bash
python3 tests/integration/test_auth_security_comprehensive.py
```
- 13 tests covering authentication, tokens, rate limiting, input validation

**Priority 2: WebSocket (High Priority)**
```bash
python3 tests/integration/test_websocket_robustness.py
```
- 8 tests covering WebSocket authentication, message validation, error handling

**Priority 3: Error Handling (Medium)**
```bash
python3 tests/integration/test_error_handling_edge_cases.py
```
- 5 tests covering error format consistency, HTTP methods, request validation

**Priority 4: Performance (Medium)**
```bash
python3 tests/integration/test_performance_load.py
```
- 4 tests covering concurrent users, high message volume, connection scalability

---

## 📊 Test Coverage

| Category | Tests | Priority | Status |
|----------|-------|----------|--------|
| Security & Authentication | 13 | 🔴 Critical | ✅ Ready |
| WebSocket Robustness | 8 | 🟠 High | ✅ Ready |
| Error Handling | 5 | 🟡 Medium | ✅ Ready |
| Performance & Load | 4 | 🟡 Medium | ✅ Ready |
| **Total** | **30** | - | ✅ **Ready** |

---

## ⚙️ Prerequisites

1. **Experience Service Running**
   ```bash
   docker-compose up experience
   ```

2. **Service Health Check**
   ```bash
   curl http://localhost:8001/health
   ```

3. **Dependencies Installed**
   - `httpx` (HTTP client)
   - `websockets` (WebSocket client)
   - `asyncio` (built-in)

---

## 🎯 Test Execution Order

The comprehensive suite runs tests in priority order:

1. **Security & Authentication** (Critical) - Must pass
2. **WebSocket Robustness** (High) - Should pass
3. **Error Handling** (Medium) - Nice to pass
4. **Performance & Load** (Medium) - Nice to pass

---

## 📝 Expected Output

### Success
```
✅ All test suites passed! Platform is ready for executive demo.
```

### Partial Success
```
⚠️  X test suite(s) had failures. Review before demo.
```

### Critical Failure
```
❌ Critical security tests failed. Do not proceed with demo.
```

---

## 🔍 Troubleshooting

### Tests Fail to Connect
- Verify service is running: `docker-compose ps experience`
- Check service logs: `docker-compose logs experience`
- Verify port: `curl http://localhost:8001/health`

### Rate Limiting Tests Fail
- Wait 60 seconds between runs
- Or adjust rate limits in `middleware/rate_limiter.py`

### WebSocket Tests Fail
- Check WebSocket endpoint: `ws://localhost:8001/api/runtime/agent`
- Verify authentication is working
- Check connection manager limits

---

## 📚 Documentation

- **Full Implementation Details:** `docs/execution/comprehensive_test_suite_implementation.md`
- **Test Suite Assessment:** `docs/execution/test_suite_assessment.md`
- **Architectural Review:** `docs/execution/architectural_review_pre_testing.md`

---

## ✅ Pre-Demo Checklist

- [ ] All test suites pass
- [ ] Experience service running
- [ ] Docker containers healthy
- [ ] No critical errors in logs
- [ ] Rate limiting configured
- [ ] Authentication working
- [ ] WebSocket connections stable

---

**Last Updated:** January 17, 2026
**Status:** ✅ Ready for Execution
