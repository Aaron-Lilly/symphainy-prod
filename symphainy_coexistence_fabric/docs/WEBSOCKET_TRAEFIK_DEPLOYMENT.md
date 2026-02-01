# WebSocket + Traefik Deployment (Production-Grade)

**Status:** Canonical (January 2026)  
**Purpose:** Document how API and WebSocket traffic are routed through Traefik so that the frontend uses one host and both REST and WebSocket work. This setup avoids the v16 failure mode where WebSocket connections were routed to the wrong service or dropped by timeouts.

**Related:** [HOW_WE_RUN_THE_PLATFORM.md](HOW_WE_RUN_THE_PLATFORM.md), [PRACTICAL_REALITY_OVERLAY.md](PRACTICAL_REALITY_OVERLAY.md), [docs/architecture/MVP_FRONTEND_BACKEND_CONNECTIVITY.md](architecture/MVP_FRONTEND_BACKEND_CONNECTIVITY.md).

---

## 1. Design: One Frontend URL, Experience as Gateway

- **Frontend** uses a single base URL (e.g. Traefik on port 80). All `/api/*` calls go to that host.
- **Traefik** path-routes to **Experience** for every path the frontend needs (auth, session, intent, **execution**, ws). Experience then **proxies** execution status (and other Runtime-only paths) to Runtime internally.
- **WebSocket** endpoints live on **Experience** only:
  - **Chat (guide agent):** `WebSocket /api/runtime/agent`
  - **Execution stream:** `WebSocket /api/execution/{execution_id}/stream`
- **REST** execution: `GET /api/execution/{id}/status` is served by **Experience** and **proxied** to Runtime. This way `/api/execution/*` is routed to Experience by Traefik, so both status (REST) and stream (WebSocket) hit the same backend and CORS/upgrade behave correctly.

**Why this fixes v16:** Previously, Traefik sent `/api/execution` to Runtime. The execution **stream** is implemented only on Experience. So `ws://host/api/execution/123/stream` went to Runtime → 404 or failed upgrade. By routing `/api/execution` to Experience, the stream WebSocket hits Experience (which has the route), and the status REST call is proxied by Experience to Runtime.

---

## 2. Traefik Configuration (docker-compose)

### Entrypoint: WebSocket-Safe Timeouts

- **readTimeout=0s, writeTimeout=0s:** Do not close connections after a fixed time; long-lived WebSocket and streaming stay up.
- **idleTimeout=3600s:** Allow idle connections (e.g. agent chat) for 1 hour before closing.
- **HTTP/1.1 Upgrade:** Traefik passes `Upgrade: websocket` through by default; no extra middleware required for standard WebSocket.

### Routing Rules

| Path | Routed to | Purpose |
|------|------------|---------|
| `/api/execution` | **Experience** | GET .../status (proxied to Runtime) + WebSocket .../stream (Experience) |
| `/api/runtime/agent` | **Experience** | WebSocket guide-agent chat (priority 20) |
| `/api/session`, `/api/intent`, `/api/auth`, `/api/ws`, `/api/admin` | **Experience** | REST + any WS under /api/ws |
| `/api/runtime` (except agent), `/api/realms` | **Runtime** | Internal or direct Runtime use; frontend uses Experience so these are mostly Experience→Runtime |

Experience proxies to Runtime for: intent submit, session create/get/upgrade, **execution status**, artifact resolve/list, intent pending (when implemented). So the frontend never talks to Runtime directly; it always talks to Experience (single origin, no CORS issues, WebSocket on same host).

---

## 3. Experience: Execution Proxy

- **GET /api/execution/{execution_id}/status** is implemented on Experience and **proxied** to Runtime via `RuntimeClient.get_execution_status(...)`. Query params: `tenant_id` (required), `include_artifacts`, `include_visuals`.
- **WebSocket /api/execution/{execution_id}/stream** is implemented on Experience (no proxy); it uses Experience SDK subscribe (polling or stream) and does not call Runtime’s nonexistent stream URL.

---

## 4. Checklist (Production-Grade WebSocket)

- [x] Traefik routes `/api/execution` to Experience (not Runtime)
- [x] Experience exposes GET `/api/execution/{id}/status` (proxy to Runtime)
- [x] Experience exposes WebSocket `/api/execution/{id}/stream`
- [x] Traefik entrypoint has readTimeout=0, writeTimeout=0, idleTimeout=3600 for WebSocket/long-lived
- [x] Frontend uses single base URL (Traefik); no direct Runtime URL for browser
- [ ] (Optional) Add Traefik middleware for WebSocket-specific headers if any client requires them; default Upgrade passthrough is sufficient for standard clients
- [x] Keepalive: application-level heartbeat (ping) in WebSocket handlers so long-idle connections (e.g. user leaves tab open) are not dropped by Traefik or client

**Ping/keepalive behaviour:** Experience sends JSON messages `{"type": "ping", "ts": <unix_ts>}` every 30 seconds while the execution stream is open. This keeps long-idle connections (e.g. user leaves tab open) from being closed by Traefik, proxies, or the client. Clients may ignore these messages or respond with `{"type": "pong"}` if they implement application-level pong; the server does not require a response. The heartbeat task is cancelled when the stream ends or the client disconnects.

---

## 5. References

- **docker-compose.yml:** Traefik command and service labels (runtime, experience).
- **Experience api/websocket.py:** Execution status proxy and stream WebSocket.
- **Experience sdk/runtime_client.py:** `get_execution_status`, `stream_execution` (polling fallback).

---

**Last updated:** January 2026
