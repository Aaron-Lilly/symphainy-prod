# Security Experience Surface

**What it is:** Login, registration, and account management interface.

**What it provides:**
- Login page
- Registration workflow
- Account settings management
- Session management UI
- Password reset flows

**Capability lens:** `capabilities/security`

**Current implementation:** `solutions/security_solution/`

**SDK operations used:**
- `invoke_intent("authenticate_user", ...)` — User login
- `invoke_intent("register_user", ...)` — Registration
- `invoke_intent("create_session", ...)` — Session creation
- `invoke_intent("terminate_session", ...)` — Logout
- `query_state(...)` — Session/auth status

**Layer:** Solutions Plane (above SDK boundary) — must use Experience SDK only.
