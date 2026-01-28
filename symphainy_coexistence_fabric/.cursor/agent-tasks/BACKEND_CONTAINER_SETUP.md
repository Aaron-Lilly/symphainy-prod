# Backend Container Setup - Quick Start

**Date:** January 28, 2026  
**Status:** ✅ **READY** - Backend container and startup script created

---

## 🎯 What Was Created

### 1. Dockerfile.runtime ✅
- Python 3.10-slim base image
- Installs dependencies from `requirements.txt`
- Runs `runtime_main.py` as entry point
- Health check on `/health` endpoint

### 2. docker-compose.yml ✅
- **Infrastructure Services:**
  - Redis (port 6379)
  - ArangoDB (port 8529)
  - Consul (port 8500)
- **Application Services:**
  - Runtime service (port 8000)
  - Experience service (port 8001)
- Proper health checks and dependencies
- Network configuration

### 3. startup.sh ✅
- Phased startup (infrastructure → application)
- Health check verification
- Service status reporting

---

## 🚀 Quick Start

### Step 1: Start Services
```bash
cd /home/founders/demoversion/symphainy_source_code/symphainy_coexistence_fabric
./startup.sh
```

This will:
1. Start infrastructure (Redis, ArangoDB, Consul)
2. Wait for infrastructure to be healthy
3. Start runtime service
4. Start experience service
5. Verify all services

### Step 2: Verify Services
```bash
# Check service status
docker-compose ps

# Check health endpoints
curl http://localhost:8000/health  # Runtime
curl http://localhost:8001/health  # Experience
```

### Step 3: Run Real Infrastructure Tests
```bash
# All real infrastructure tests
pytest tests/3d/real_infrastructure/ -v -m real_infrastructure

# Just critical demo paths
pytest tests/3d/real_infrastructure/ -v -m critical

# Just SRE tests
pytest tests/3d/real_infrastructure/ -v -m sre
```

---

## 📋 Environment Variables

### Required
- `REDIS_URL` (default: `redis://redis:6379`)
- `ARANGO_URL` (default: `http://arango:8529`)
- `ARANGO_ROOT_PASSWORD` (default: `test_password`)

### Optional
- `RUNTIME_PORT` (default: `8000`)
- `EXPERIENCE_PORT` (default: `8001`)
- `LOG_LEVEL` (default: `INFO`)

### Secrets (`.env.secrets`)
- `LLM_OPENAI_API_KEY` (for LLM tests)
- `LLM_ANTHROPIC_API_KEY` (for LLM tests)
- Other API keys as needed

---

## 🔧 Troubleshooting

### Services Won't Start
```bash
# Check logs
docker-compose logs runtime
docker-compose logs experience

# Restart services
docker-compose restart runtime experience
```

### Health Checks Failing
```bash
# Check if services are running
docker-compose ps

# Check infrastructure health
docker-compose ps redis arango consul

# Check service logs
docker-compose logs runtime | tail -50
```

### Port Conflicts
```bash
# Check what's using ports
sudo lsof -i :8000
sudo lsof -i :8001

# Stop conflicting services or change ports in docker-compose.yml
```

---

## 🎯 What This Enables

### Real Infrastructure Testing ✅
- Tests against actual Redis
- Tests against actual ArangoDB
- Tests against actual services
- Catches real integration issues

### Demo Readiness ✅
- Validates authentication flow
- Validates file upload
- Validates parsing quality
- Validates chat agents
- Validates navigation

---

## 📝 Next Steps

1. ✅ **Backend container created** - DONE
2. ✅ **Startup script created** - DONE
3. ⏳ **Start services** - Run `./startup.sh`
4. ⏳ **Run tests** - Run `pytest tests/3d/real_infrastructure/ -v`
5. ⏳ **Fix any issues** - Address test failures
6. ⏳ **Validate demo paths** - Ensure all critical paths work

---

**Status:** ✅ **Backend container ready. Run `./startup.sh` to start services and then run real infrastructure tests.**
