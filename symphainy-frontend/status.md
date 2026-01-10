# Operations Pillar: Status Review and Recommendations

## 1. Agent Instantiation & API Endpoints

- **Current State:**
  - The frontend (e.g., `AGUIEventProvider.tsx`, `AGUIInsightsPanel.tsx`, and `lib/api/insights.ts`) still makes API calls to `/insights/agent`.
  - There is no evidence of `/global/agent` or a unified global agent endpoint being used in the frontend for agent orchestration.
  - The backend has .json definitions for all Operations agents, but **no corresponding .py implementations** (unlike the Insights agents, which have both .json and .py files).
  - The Insights agents have Python implementations, but Operations agents do not. This means Operations agent logic is not yet operational in Python.

- **Recommendations:**
  - Refactor the frontend to use a single `/global/agent` (or equivalent) endpoint for all agent interactions, retiring `/insights/agent` and any pillar-specific endpoints.
  - Implement Python classes for each Operations agent, mirroring the structure of the Insights agents.
  - Ensure the backend exposes a `/global/agent` endpoint that routes requests to the correct Operations agent logic.

## 2. Session Management

- **Current State:**
  - `GlobalSessionProvider` is the only source of truth for session tokens and state in the frontend. No exceptions found.
  - All session state is managed and propagated through this provider as intended.

- **Recommendations:**
  - Continue to enforce this pattern. If new session logic is added, ensure it is centralized in `GlobalSessionProvider`.

## 3. Supabase Integration

- **Current State:**
  - The backend (`fms_service.py`) is set up to use the Supabase Python client for file and metadata operations.
  - However, many Supabase-related methods are marked as TODO or raise `NotImplementedError`.
  - There is no evidence of Supabase integration in the frontend (no direct calls or client usage).

- **Recommendations:**
  - Complete the Supabase integration in the backend, especially for file upload, metadata registration, and linking.
  - Ensure all file operations in the Operations pillar (save, link, register) are routed through these backend services.

## 4. Data Dashboard Integration

- **Current State:**
  - Documentation states that all files and metadata must be registered in Supabase and the Data dashboard.
  - There is no direct evidence in the code of Data dashboard API usage, but this may be handled via the backend Supabase logic.

- **Recommendations:**
  - Confirm that the Data dashboard is updated via backend Supabase operations.
  - If a separate API is required for the Data dashboard, document and implement the integration.

## 5. Agent Implementation Files

- **Current State:**
  - Operations agents only have .json files (definitions/config), but **no .py files** (logic/implementation).
  - Insights agents have both .json and .py files, and are thus operational.

- **Recommendations:**
  - Create Python implementation files for each Operations agent, following the pattern used for Insights agents.
  - Register these agents in the backend so they can be invoked by the orchestrator/global endpoint.

## 6. Legacy Code

- **Current State:**
  - Multiple frontend files still reference `/insights/agent`.
  - No evidence of `/global/agent` usage in the frontend.

- **Recommendations:**
  - Remove or refactor all legacy endpoint usage in the frontend.
  - Ensure all agent interactions use the new global session/agent architecture.

---

## Summary Table

| Area                 | Status/Findings                                 | Recommendations                       |
| -------------------- | ----------------------------------------------- | ------------------------------------- |
| Agent Endpoints      | Still using legacy `/insights/agent`            | Refactor to `/global/agent`           |
| Operations Agents    | Only .json files, no .py implementations        | Implement .py files for all agents    |
| Session Management   | Centralized in `GlobalSessionProvider`          | Maintain this pattern                 |
| Supabase Integration | Backend setup, but many methods not implemented | Complete backend Supabase integration |
| Data Dashboard       | No direct code evidence, assumed via backend    | Confirm/update integration as needed  |
| Legacy Code          | Multiple files reference old endpoints          | Remove/refactor to new architecture   |

---

**Next Steps:**

1. Refactor frontend to use `/global/agent` for all agent interactions.
2. Implement Python logic for all Operations agents.
3. Complete Supabase integration in backend services.
4. Confirm Data dashboard integration is robust and automatic.
5. Remove all legacy endpoint usage from the codebase.
