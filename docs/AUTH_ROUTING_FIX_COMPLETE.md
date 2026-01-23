# Auth API Routing Fix - Complete

**Date:** January 23, 2026  
**Status:** ✅ **FIXED**

---

## Problem

1. `/api/auth/login` returning 404
2. `pillars/operation?_rsc=...` returning 404

---

## Root Causes

### Issue 1: Missing `/api/auth` in Traefik Routing
Traefik routing rules didn't include `/api/auth` path prefix.

### Issue 2: Traefik Labels on Wrong Container
Traefik labels were on the **Traefik container** instead of the **service containers**. Traefik's Docker provider discovers services by reading labels from the service containers themselves.

---

## Solutions Applied

### 1. Added `/api/auth` to Experience Service Routing
```yaml
- traefik.http.routers.experience.rule=PathPrefix(`/api/sessions`) || PathPrefix(`/api/intent`) || PathPrefix(`/api/ws`)
  || PathPrefix(`/api/admin`) || PathPrefix(`/api/auth`)
```

### 2. Moved Traefik Labels to Service Containers

**Before:** Labels were on `traefik` service  
**After:** Labels are on `runtime` and `experience` services

**Runtime Service:**
```yaml
runtime:
  # ... other config ...
  labels:
    - traefik.enable=true
    - traefik.http.routers.runtime.rule=PathPrefix(`/api/runtime`) || ...
    # ... other labels ...
```

**Experience Service:**
```yaml
experience:
  # ... other config ...
  labels:
    - traefik.enable=true
    - traefik.http.routers.experience.rule=PathPrefix(`/api/sessions`) || ... || PathPrefix(`/api/auth`)
    # ... other labels ...
```

---

## Verification

✅ **Login Endpoint Working:**
```bash
curl -X POST http://localhost:80/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test12345"}'
# Returns: HTTP 401 (expected for invalid credentials)
```

✅ **Traefik Routing Confirmed:**
```
experience@docker: PathPrefix(`/api/sessions`) || PathPrefix(`/api/intent`) || 
  PathPrefix(`/api/ws`) || PathPrefix(`/api/admin`) || PathPrefix(`/api/auth`) -> experience
```

---

## Remaining Issue

**`pillars/operation?_rsc=...` 404 Error:**
- This is a Next.js RSC (React Server Component) route issue
- The route may not exist or may need to be created
- This is a frontend routing issue, not a backend/API issue

---

## Key Learnings

1. **Traefik Docker Provider:** Labels must be on the **service containers**, not the Traefik container
2. **Service Discovery:** Traefik automatically discovers services via Docker labels
3. **Routing Rules:** All API path prefixes must be explicitly included in routing rules

---

**Last Updated:** January 23, 2026
