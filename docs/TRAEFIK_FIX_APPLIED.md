# Traefik Fix Applied

**Date:** January 23, 2026  
**Issue:** ERR_CONNECTION_REFUSED from external IP  
**Status:** ✅ **FIXED** (Local access working, external access needs firewall check)

---

## Problem

- External access to `35.215.64.103` was returning `ERR_CONNECTION_REFUSED`
- Traefik logs showed "Router defined multiple times" errors
- Local access (`localhost:80`) was working

---

## Root Cause

**Duplicate Traefik Labels:**
- Traefik labels were incorrectly placed on the `traefik` service itself (lines 310-321 in docker-compose.yml)
- These labels should ONLY be on the `runtime` service (which they already were at lines 127-137)
- This caused Traefik to try to route to itself, creating duplicate router definitions

---

## Fix Applied

**Removed duplicate labels from `traefik` service:**
- Removed all `traefik.http.routers.runtime.*` labels from the `traefik` service
- These labels belong only on the `runtime` service (already correctly placed)

**File Changed:**
- `docker-compose.yml` (removed lines 310-321)

---

## Current Status

### ✅ Local Access
- `http://localhost:80` → ✅ Working (frontend loads)
- `http://localhost:80/health` → ✅ Working (returns experience service health)
- `http://localhost:80/api/auth/login` → ✅ Working (routes correctly)

### ⚠️ External Access
- `http://35.215.64.103` → Needs firewall check
- Traefik is listening on port 80
- Services are healthy

---

## Next Steps

1. **Check Firewall Rules:**
   ```bash
   # Verify firewall allows port 80
   gcloud compute firewall-rules list --filter="name~allow-http"
   ```

2. **Verify Network Tags:**
   ```bash
   # Check if VM has http-server tag
   gcloud compute instances describe <instance-name> --zone=<zone> | grep tags
   ```

3. **Test External Access:**
   - After firewall verification, test from external browser
   - Should be able to access `http://35.215.64.103`

---

## Verification

**Local Tests:**
```bash
# Frontend
curl http://localhost:80
# Returns: HTML (frontend loads)

# Health check
curl http://localhost:80/health
# Returns: {"status":"healthy","service":"experience","version":"2.0.0"}

# API routing
curl http://localhost:80/api/auth/login -X POST -H "Content-Type: application/json" -d '{"email":"test@test.com","password":"test12345"}'
# Returns: Proper API response
```

---

**Last Updated:** January 23, 2026
