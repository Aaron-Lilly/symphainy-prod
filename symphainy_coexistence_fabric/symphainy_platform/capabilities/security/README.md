# Security Capability

**What it does:** Authentication, authorization, identity, and session management.

**Core functions:**
- User authentication (login, logout)
- User registration
- Session management (create, validate, terminate)
- Authorization and permission checks
- Identity verification

**MVP exposure:** `experience/security`

**Current implementation:**
- `realms/security/intent_services/`
- `solutions/security_solution/`

**Intent types:**
- `authenticate_user` — User login
- `register_user` — New user registration
- `create_session` — Establish session
- `validate_session` — Session validation
- `terminate_session` — Logout/session end
- `validate_authorization` — Permission check

**Layer:** Execution Plane (below SDK boundary) — may access Public Works and State Surface directly.
