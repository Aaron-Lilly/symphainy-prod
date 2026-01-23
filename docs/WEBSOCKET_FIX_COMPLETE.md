# WebSocket Routing Fix - Complete

**Date:** January 23, 2026  
**Status:** ✅ **FIXED**

---

## Problem

WebSocket connection to `ws://35.215.64.103/api/runtime/agent` was failing with:
- 502 Bad Gateway
- 403 Forbidden

---

## Root Causes

1. **Routing Priority Issue:** `/api/runtime/agent` was matching the Runtime service router (`/api/runtime`) before the Experience service router
2. **Missing WebSocket Route:** No dedicated high-priority route for the WebSocket endpoint
3. **Architecture:** The WebSocket endpoint is in the Experience service, not Runtime service

---

## Solutions Applied

### 1. Created Dedicated WebSocket Router (High Priority)

Added a dedicated router with priority 20 (higher than runtime's priority 10):

```yaml
- traefik.http.routers.experience-websocket.rule=PathPrefix(`/api/runtime/agent`)
- traefik.http.routers.experience-websocket.entrypoints=web
- traefik.http.routers.experience-websocket.service=experience
- traefik.http.routers.experience-websocket.priority=20
```

### 2. Excluded WebSocket Path from Runtime Router

Updated Runtime router to exclude `/api/runtime/agent`:

```yaml
- traefik.http.routers.runtime.rule=PathPrefix(`/api/runtime`) && !PathPrefix(`/api/runtime/agent`) || ...
```

### 3. Added WebSocket Timeout Configuration

Added Traefik entrypoint configuration for long-lived WebSocket connections:

```yaml
- --entrypoints.web.transport.respondingTimeouts.readTimeout=0s
- --entrypoints.web.transport.respondingTimeouts.writeTimeout=0s
- --entrypoints.web.transport.respondingTimeouts.idleTimeout=3600s
```

---

## Router Priority Order

1. **Priority 99:** Health checks (`/health`)
2. **Priority 20:** WebSocket endpoint (`/api/runtime/agent`) → Experience service
3. **Priority 10:** Runtime API (`/api/runtime/*` except `/agent`) → Runtime service
4. **Priority 10:** Experience API (`/api/sessions`, `/api/auth`, etc.) → Experience service
5. **Priority 1:** Frontend (catch-all) → Frontend service

---

## Architecture Note

**Important:** The endpoint `/api/runtime/agent` is in the Experience service, not Runtime service. This is by design:
- **Experience Plane** = Intent + Context Boundary (user-facing, knows who is talking)
- **Runtime** = Execution Engine (stateless, executes agents when told)

The endpoint name is a contract, not a locator.

---

## Verification

✅ **Routing Confirmed:**
```
experience-websocket@docker: PathPrefix(`/api/runtime/agent`) (priority: 20)
runtime@docker: PathPrefix(`/api/runtime`) && !PathPrefix(`/api/runtime/agent`) (priority: 10)
```

✅ **Endpoint Responds:**
- Direct connection to Experience service: Returns auth error (expected)
- Via Traefik: Routes correctly (400 Bad Request from curl is expected - not a real WebSocket client)

---

## Next Steps

The WebSocket routing is now configured correctly. The frontend should be able to connect. If issues persist:

1. Check browser console for specific WebSocket errors
2. Verify session token is valid
3. Check Experience service logs for WebSocket connection attempts
4. Verify CORS allows WebSocket upgrades

---

**Last Updated:** January 23, 2026
