# MVP Frontend–Backend Connectivity: Will It Work on the Other Side?

**Purpose:** Answer: if we complete Phase 1–2 of the Experience Civic refactor and kick off the landing (web) agents, then resume takeoff work — **will the system actually work** for users “playing around” on the website? What **additional work** is required so the frontend and symphainy_coexistence_fabric connect and provide the necessary functionality?

**Short answer:** Phase 1–2 + landing agents deliver the **contract and structure** (SDK, capabilities/experience layout). They do **not** by themselves make the existing frontend and backend work end-to-end. You need a small set of **connectivity and one-critical-path** steps so the MVP works on the “other side.”

---

## 1. How the Frontend Connects Today

- The frontend uses **one base URL** for all API calls: `getApiUrl()` / `getApiEndpointUrl()` from `shared/config/api-config.ts`.
- **Default in development:** `http://localhost:8000` (Runtime), with a warning if no env is set.
- **Production:** `NEXT_PUBLIC_API_URL` or `NEXT_PUBLIC_BACKEND_URL` must be set.

**Frontend calls (examples):**

| Frontend need | Endpoint | Where it lives today |
|---------------|----------|----------------------|
| Auth | `/api/auth/login`, `/api/auth/register`, etc. | **Experience only** (Runtime has no `/api/auth`) |
| Session | `/api/session/create`, `/api/session/create-anonymous`, `/api/session/{id}`, `/api/session/{id}/upgrade` | **Experience** (proxies to Runtime via RuntimeClient) |
| Intent | `/api/intent/submit` | **Experience** (proxies to Runtime) |
| Execution status | `GET /api/execution/{id}/status` | **Runtime only** — Experience does **not** expose this |
| Artifacts | `POST /api/artifact/resolve`, `POST /api/artifact/list`, `GET /api/artifacts/{id}` | **Runtime only** — Experience does **not** expose these |
| Pending intents | `POST /api/intent/pending/list`, `POST /api/intent/pending/create` | **Runtime only** — Experience does **not** expose these |
| Execution stream | WebSocket `/api/execution/{id}/stream` | **Experience** has a WebSocket route that uses RuntimeClient; Runtime may not have HTTP `/stream` (see audit) |

So: **auth, session, intent** work if the frontend points at **Experience (8001)**. **Execution status, artifact, intent/pending** are only on Runtime (8000). If the frontend points at **Experience (8001)** only, those calls currently **404** because Experience does not proxy them.

---

## 2. Will It Work After Phase 1–2 + Landing Agents?

- **Phase 1–2:** Experience SDK contract (doc), RuntimeClient aligned with Runtime, SDK facade, Experience routes wired through facade. Backend/civic side only.
- **Landing agents:** Canonical doc, capabilities/ and experience/ layout, migration map, optional validation job. Mostly **additive structure and docs**; they do **not** implement the existing frontend app or the HTTP glue between frontend and backend.

So after Phase 1–2 + landing agents:

- **Backend:** Experience exposes the SDK surface (session, intent, auth) and is the right place to attach “experience” clients. Runtime still has execution status, artifact, intent/pending.
- **Frontend:** Unchanged: still one base URL; still calls `/api/execution/.../status`, `/api/artifact/*`, `/api/intent/pending/*` to that same base URL.
- **Gap:** If the frontend base URL is **Experience (8001)** (required for auth), then **execution status, artifact, and intent/pending** do **not** work yet because Experience does not proxy them. So the system will **not** fully work on the other side until that gap is closed.

---

## 3. What Additional Work Is Required for the MVP to Work “on the Other Side”

To have the website and symphainy_coexistence_fabric actually connect so users can “play around” (e.g. log in or get a session, do one thing like upload/parse or run a journey, see result), you need the following **in addition to** Phase 1–2 and landing tasks.

### 3.1 Single Backend URL: Experience as the Gateway

- **Decision:** The frontend should use **one** base URL and that URL should be **Experience** (so auth, session, intent all work).
- **Implication:** Experience must **proxy** every path the frontend needs that today lives only on Runtime:
  - `GET /api/execution/{execution_id}/status`
  - `POST /api/artifact/resolve`
  - `POST /api/artifact/list`
  - `GET /api/artifacts/{artifact_id}` (if used)
  - `POST /api/intent/pending/list`
  - `POST /api/intent/pending/create`
- **Work:** Add proxy routes on the Experience app (or a single catch-all proxy) that forward these to Runtime (using RuntimeClient or a small HTTP forwarder). This can be part of Phase 2 (SDK facade) or a small “Phase 2b: Experience proxy for execution/artifact/pending.”
- **Outcome:** Frontend sets `NEXT_PUBLIC_API_URL` (or `NEXT_PUBLIC_BACKEND_URL`) to Experience (e.g. `http://localhost:8001` in dev, or the Traefik/public URL that routes to Experience). All frontend calls then succeed against one host.

### 3.2 Frontend Env and CORS

- **Env:** In dev and in deployment, set `NEXT_PUBLIC_API_URL` (or `NEXT_PUBLIC_BACKEND_URL`) to the Experience base URL (e.g. `http://localhost:8001` for local, or the URL that reaches Experience behind Traefik).
- **CORS:** Experience already has CORS middleware (e.g. `CORS_ALLOWED_ORIGINS`). Ensure the frontend origin (e.g. `http://localhost:3000`, or your deployed frontend origin) is in the allowed list so browser requests succeed.
- **Outcome:** No CORS errors; frontend can call Experience from the browser.

### 3.3 One Critical Path E2E

- **Goal:** One user-visible path works end-to-end: e.g. “open site → create anonymous session (or log in) → submit one intent (e.g. compose_journey or content parse) → get execution status → show result (or artifact).”
- **Work:** (1) Manually or via E2E test: drive the frontend through that path with backend (Runtime + Experience) running. (2) Fix any broken links: missing proxy routes, wrong query params (e.g. `tenant_id` on execution status), or frontend assumptions about response shape. (3) Document the path (e.g. in PATH_TO_WORKING_PLATFORM or a short “MVP critical path” doc).
- **Outcome:** “MVP works on the other side” is demonstrable and regression-testable.

### 3.4 Deployment / Routing (Docker + Traefik)

- **Today:** docker-compose runs Runtime (8000) and Experience (8001); Traefik can route by path. For “one URL” for the frontend, Traefik should route **all** `/api/*` (or the subset the frontend uses) to **Experience**, and Experience proxies to Runtime for execution/artifact/pending (see 3.1). Alternatively, Traefik routes `/api/auth`, `/api/session`, `/api/intent` to Experience and `/api/execution`, `/api/artifact`, `/api/intent/pending` to Runtime — then the frontend **must** use the same host for all (e.g. Traefik on port 80) and Traefik does path-based routing; no frontend change. Either way, routing must be consistent with the single base URL the frontend uses.
- **Work:** Confirm Traefik (or your deployment) routes so that the single `NEXT_PUBLIC_API_URL` used by the frontend reaches either (a) Experience only, with Experience proxying to Runtime, or (b) a single entry point that path-routes to Experience and Runtime so that all frontend paths resolve. Document the chosen setup.
- **Outcome:** In the deployed environment, “play around” works the same as in dev.

---

## 4. Summary: Will It Work, and What To Do

| Question | Answer |
|----------|--------|
| After Phase 1–2 + landing agents, does the system “just work” for users on the website? | **No.** The contract and structure are in place, but the existing frontend will 404 on execution status, artifact, and intent/pending if it points at Experience, because Experience does not yet proxy those. |
| What additional work is required? | (1) **Experience proxies** for execution status, artifact, and intent/pending (so one backend URL = Experience). (2) **Frontend env** set to Experience URL; **CORS** allows frontend origin. (3) **One critical path** E2E (session → intent → execution status → result) working and documented. (4) **Deployment/routing** (e.g. Traefik) consistent with single-URL or path-routing so the same flow works in prod. |
| Who does it? | **Takeoff:** proxy routes (or “Phase 2b”) and CORS/env docs; critical path E2E can be takeoff or joint. **Landing agents** do not implement the existing frontend or these proxies; they build capabilities/experience layout against the SDK. |
| When? | **After Phase 2** (or as part of Phase 2): add proxy routes and env/CORS; then run one critical path and fix until it passes. After that, “MVP works on the other side” is true; you can then continue takeoff work and let landing agents build on the same contract. |

---

## 5. Suggested “Phase 2b” Checklist (Takeoff)

- [ ] Experience exposes proxy (or passthrough) routes: `GET /api/execution/{id}/status`, `POST /api/artifact/resolve`, `POST /api/artifact/list`, `GET /api/artifacts/{id}` (if needed), `POST /api/intent/pending/list`, `POST /api/intent/pending/create`. Each forwards to Runtime (e.g. via RuntimeClient extended with these methods, or a small generic proxy).
- [ ] Frontend env: document and set `NEXT_PUBLIC_API_URL` (or `NEXT_PUBLIC_BACKEND_URL`) to Experience base URL in dev and prod.
- [ ] CORS: frontend origin(s) in Experience `CORS_ALLOWED_ORIGINS`.
- [ ] One critical path: create session (anonymous or login) → submit intent → get execution status (and optionally artifact) → show result; manual or E2E; documented.
- [ ] Deployment: Traefik (or equivalent) routes so that the frontend’s single base URL reaches the right backend(s); document.

Once this is done, Phase 1–2 + landing agents + “Phase 2b” give you a working MVP on the other side: frontend and symphainy_coexistence_fabric connect, and users can play around with the platform via the website.
