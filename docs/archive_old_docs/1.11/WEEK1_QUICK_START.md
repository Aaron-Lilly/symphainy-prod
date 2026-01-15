# Week 1 Quick Start Guide

**Status:** ✅ **READY TO TEST**

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd /home/founders/demoversion/symphainy_source_code
pip install -r requirements.txt
pip install -r tests/requirements.txt
```

### 2. Start Infrastructure (Optional)

If you have Redis available:

```bash
# Start Redis (if using Docker)
docker run -d -p 6379:6379 redis:7-alpine

# Or use existing Redis
export REDIS_URL=redis://localhost:6379
```

### 3. Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run unit tests
pytest tests/unit/runtime/ -v -m unit

# Run integration tests
pytest tests/integration/runtime/ -v -m integration
```

### 4. Start Runtime Service

```bash
# With Redis
export REDIS_URL=redis://localhost:6379
python3 main.py

# Without Redis (in-memory mode)
python3 main.py
```

The service will start on `http://localhost:8000`

---

## 📋 API Endpoints

### Create Session

```bash
curl -X POST http://localhost:8000/session/create \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "test_tenant",
    "user_id": "test_user",
    "context": {"key": "value"}
  }'
```

**Response:**
```json
{
  "success": true,
  "session": {
    "session_id": "...",
    "tenant_id": "test_tenant",
    "user_id": "test_user",
    "created_at": "...",
    "context": {"key": "value"},
    "active_sagas": []
  }
}
```

### Get Session

```bash
curl "http://localhost:8000/session/SESSION_ID?tenant_id=test_tenant"
```

### Submit Intent

```bash
curl -X POST http://localhost:8000/intent/submit \
  -H "Content-Type: application/json" \
  -d '{
    "intent_type": "content.upload",
    "realm": "content",
    "session_id": "SESSION_ID",
    "tenant_id": "test_tenant",
    "payload": {"file_path": "/tmp/test.txt"}
  }'
```

**Response:**
```json
{
  "success": true,
  "execution_id": "exec_..."
}
```

### Get Execution Status

```bash
curl "http://localhost:8000/execution/EXECUTION_ID/status?tenant_id=test_tenant"
```

### Health Check

```bash
curl http://localhost:8000/health
```

---

## ✅ Verification

**Expected Behavior:**
1. ✅ Session creation returns session with tenant_id
2. ✅ Intent submission requires valid session
3. ✅ WAL entries created for all operations
4. ✅ Saga created for each intent
5. ✅ Execution state stored in State Surface
6. ✅ Multi-tenant isolation enforced

---

**Last Updated:** January 2026
