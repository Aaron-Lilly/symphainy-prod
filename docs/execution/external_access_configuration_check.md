# External Access Configuration Check

**Date:** January 2026  
**Status:** 🔍 **CONFIGURATION AUDIT**  
**Public IP:** 35.215.64.103  
**Purpose:** Verify configuration for external access via public IP

---

## 🎯 Configuration Requirements

For external access via `http://35.215.64.103`, we need:

1. ✅ **Traefik** - Exposed on port 80 (public)
2. ✅ **CORS** - Configured to allow frontend origin
3. ✅ **Frontend API Config** - Points to public IP
4. ✅ **WebSocket** - Configured for external access
5. ✅ **Service Routing** - Traefik labels for service discovery

---

## 📋 Current Configuration Status

### 1. Traefik Configuration

**Status:** ⚠️ **NEEDS VERIFICATION**

**Current Setup:**
- Traefik exposed on port 80 (HTTP) and 443 (HTTPS)
- Listens on `0.0.0.0` (all interfaces) ✅
- Entrypoints: `web` (port 80), `websecure` (port 443) ✅

**Missing:**
- ❓ Traefik labels for Runtime service
- ❓ Traefik labels for Experience service
- ❓ Routing rules for `/api/*` paths

**Action Required:**
- Add Traefik labels to `runtime` and `experience` services in `docker-compose.yml`
- Configure routing rules for API endpoints

---

### 2. CORS Configuration

**Status:** ⚠️ **NEEDS UPDATE**

**Experience Service:**
```python
allow_origins=["*"]  # Currently allows all (OK for testing, needs restriction for production)
```

**Runtime API:**
- ❓ Need to check if CORS is configured

**Action Required:**
- Verify Runtime API has CORS middleware
- Update CORS to allow `http://35.215.64.103` (or use environment variable)

---

### 3. Frontend API Configuration

**Status:** ⚠️ **NEEDS ENVIRONMENT VARIABLE**

**Current Config:**
- `api-config.ts` uses `NEXT_PUBLIC_API_URL` environment variable
- Falls back to `localhost:8000` in development
- Hardcoded fallback in `lib/config.ts`: `http://35.215.64.103` ✅

**Action Required:**
- Set `NEXT_PUBLIC_API_URL=http://35.215.64.103` in frontend environment
- Verify WebSocket URL generation uses public IP

---

### 4. WebSocket Configuration

**Status:** ⚠️ **NEEDS VERIFICATION**

**Current Setup:**
- `getRuntimeWebSocketUrl()` converts `http://` to `ws://`
- Uses `getApiUrl()` as base

**Action Required:**
- Verify WebSocket endpoint is accessible via public IP
- Check Traefik WebSocket routing configuration

---

### 5. Service Routing (Traefik Labels)

**Status:** ❌ **MISSING**

**Current Issue:**
- `docker-compose.yml` doesn't have Traefik labels for `runtime` and `experience` services
- Services won't be discoverable by Traefik

**Action Required:**
- Add Traefik labels to `runtime` service
- Add Traefik labels to `experience` service
- Configure routing rules

---

## 🔧 Required Configuration Changes

### 1. Add Traefik Labels to Runtime Service

**File:** `docker-compose.yml`

```yaml
runtime:
  # ... existing config ...
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.runtime.rule=PathPrefix(`/api/runtime`) || PathPrefix(`/api/intent`) || PathPrefix(`/api/session`) || PathPrefix(`/api/execution`) || PathPrefix(`/api/realms`)"
    - "traefik.http.routers.runtime.entrypoints=web"
    - "traefik.http.routers.runtime.service=runtime"
    - "traefik.http.services.runtime.loadbalancer.server.port=8000"
    - "traefik.http.routers.runtime.priority=10"
```

### 2. Add Traefik Labels to Experience Service

**File:** `docker-compose.yml`

```yaml
experience:
  # ... existing config ...
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.experience.rule=PathPrefix(`/api/sessions`) || PathPrefix(`/api/intent`) || PathPrefix(`/api/ws`) || PathPrefix(`/api/admin`)"
    - "traefik.http.routers.experience.entrypoints=web"
    - "traefik.http.routers.experience.service=experience"
    - "traefik.http.services.experience.loadbalancer.server.port=8001"
    - "traefik.http.routers.experience.priority=10"
    - "traefik.http.routers.experience.middlewares=cors@file"  # If CORS middleware exists
```

### 3. Add CORS to Runtime API

**File:** `runtime_main.py`

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specific: ["http://35.215.64.103", "http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4. Set Frontend Environment Variable

**File:** `.env.local` or `.env.production` in `symphainy-frontend/`

```bash
NEXT_PUBLIC_API_URL=http://35.215.64.103
NEXT_PUBLIC_FRONTEND_URL=http://35.215.64.103
```

---

## ✅ Verification Checklist

Before testing, verify:

- [ ] Traefik is running and accessible on port 80
- [ ] Runtime service has Traefik labels
- [ ] Experience service has Traefik labels
- [ ] Runtime API has CORS middleware
- [ ] Experience API has CORS middleware (already has `allow_origins=["*"]`)
- [ ] Frontend `NEXT_PUBLIC_API_URL` is set to `http://35.215.64.103`
- [ ] WebSocket URL generation uses public IP
- [ ] Services are on `symphainy_net` network
- [ ] Traefik can discover services (check Traefik dashboard: `http://35.215.64.103:8080`)

---

## 🧪 Test External Access

### Test 1: Traefik Dashboard
```bash
curl http://35.215.64.103:8080/api/overview
```

### Test 2: Runtime Health
```bash
curl http://35.215.64.103/api/runtime/health
# Or via Traefik routing
curl http://35.215.64.103/api/health
```

### Test 3: Experience Health
```bash
curl http://35.215.64.103/api/health
```

### Test 4: Frontend Access
```bash
curl http://35.215.64.103
# Should return frontend HTML
```

### Test 5: CORS Headers
```bash
curl -H "Origin: http://35.215.64.103" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     http://35.215.64.103/api/sessions
```

---

## 🚀 Next Steps

1. ✅ Add Traefik labels to services
2. ✅ Add CORS to Runtime API
3. ✅ Set frontend environment variables
4. ✅ Verify Traefik routing
5. ✅ Test external access

---

**This configuration ensures the platform is accessible via the public IP!** 🎯
