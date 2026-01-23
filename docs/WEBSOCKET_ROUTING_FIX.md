# WebSocket Routing Fix

**Date:** January 23, 2026  
**Issue:** WebSocket connection to `/api/runtime/agent` failing with 502/403  
**Status:** In Progress

---

## Problem

WebSocket connection attempts to `ws://35.215.64.103/api/runtime/agent` are failing with:
- 502 Bad Gateway
- 403 Forbidden

---

## Root Cause

The WebSocket endpoint `/api/runtime/agent` is in the **Experience service** (port 8001), not the Runtime service. However, Traefik was routing `/api/runtime/*` to the Runtime service, which doesn't have this endpoint.

---

## Solution Applied

### 1. Added `/api/runtime/agent` to Experience Service Routing

Updated Traefik routing rules to include the WebSocket endpoint:

```yaml
- traefik.http.routers.experience.rule=PathPrefix(`/api/sessions`) || PathPrefix(`/api/intent`) || PathPrefix(`/api/ws`)
  || PathPrefix(`/api/admin`) || PathPrefix(`/api/auth`) || PathPrefix(`/api/runtime/agent`)
```

### 2. Added WebSocket Timeout Configuration

Added Traefik entrypoint configuration for WebSocket support:

```yaml
- --entrypoints.web.transport.respondingTimeouts.readTimeout=0s
- --entrypoints.web.transport.respondingTimeouts.writeTimeout=0s
- --entrypoints.web.transport.respondingTimeouts.idleTimeout=3600s
```

---

## Architecture Note

**Important:** The endpoint `/api/runtime/agent` is in the Experience service, not Runtime service. This is by design:
- Experience Plane = Intent + Context Boundary (user-facing)
- Runtime = Execution Engine (stateless)

The endpoint name is a contract, not a locator.

---

## Verification Steps

1. Check Traefik routing:
```bash
curl http://localhost:8080/api/http/routers | grep experience
```

2. Test WebSocket endpoint (direct):
```bash
curl -I --header "Connection: Upgrade" --header "Upgrade: websocket" \
  http://localhost:8001/api/runtime/agent?session_token=test
```

3. Test via Traefik:
```bash
curl -I --header "Connection: Upgrade" --header "Upgrade: websocket" \
  http://localhost:80/api/runtime/agent?session_token=test
```

---

## Next Steps

If still failing:
1. Verify the WebSocket endpoint is registered in Experience service
2. Check Experience service logs for WebSocket connection attempts
3. Verify session token validation
4. Check CORS configuration for WebSocket

---

**Last Updated:** January 23, 2026
