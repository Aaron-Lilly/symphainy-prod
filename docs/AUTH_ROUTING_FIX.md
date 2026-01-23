# Auth API Routing Fix

**Date:** January 23, 2026  
**Issue:** `/api/auth/login` returning 404  
**Status:** ✅ **FIXED**

---

## Problem

The login endpoint `/api/auth/login` was returning 404 because Traefik was not routing `/api/auth` requests to the Experience service.

**Error:**
```
POST http://35.215.64.103/api/auth/login 404 (Not Found)
```

---

## Root Cause

Traefik routing rules for the Experience service only included:
- `/api/sessions`
- `/api/intent`
- `/api/ws`
- `/api/admin`

But **NOT** `/api/auth`

---

## Solution

Added `/api/auth` to the Traefik routing rules in `docker-compose.yml`:

**Before:**
```yaml
- traefik.http.routers.experience.rule=PathPrefix(`/api/sessions`) || PathPrefix(`/api/intent`) || PathPrefix(`/api/ws`)
  || PathPrefix(`/api/admin`)
```

**After:**
```yaml
- traefik.http.routers.experience.rule=PathPrefix(`/api/sessions`) || PathPrefix(`/api/intent`) || PathPrefix(`/api/ws`)
  || PathPrefix(`/api/admin`) || PathPrefix(`/api/auth`)
```

---

## Verification

1. ✅ Traefik routing rule updated
2. ✅ Services restarted
3. ✅ Routing confirmed via Traefik API

**Test:**
```bash
curl -X POST http://localhost:80/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test12345"}'
```

---

## Additional Notes

The auth endpoint is defined in:
- `symphainy_platform/civic_systems/experience/api/auth.py`
- Router prefix: `/api/auth`
- Endpoints: `/api/auth/login`, `/api/auth/register`, etc.

---

**Last Updated:** January 23, 2026
