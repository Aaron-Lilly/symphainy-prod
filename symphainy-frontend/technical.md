# Testing Structure and Best Practices

## Playwright (E2E) Tests

- **Location:** All Playwright E2E tests must be placed in `frontend/tests/e2e`.
- **Configuration:**
  - Set in `frontend/playwright.config.ts` with `testDir: './tests/e2e'`.
  - Only files in this directory will be picked up by Playwright.
- **Do NOT place E2E tests in:**
  - `frontend/__tests__`
  - Any root-level `tests/` or `tests/e2e/` directory (these will not be run and may cause confusion).

## Jest (Unit) Tests

- **Location:** All Jest unit tests must be placed in `frontend/__tests__` or as `*.test.ts(x)` files in the codebase.
- **Configuration:**
  - Set in `frontend/jest.config.js` with `testMatch` and `testPathIgnorePatterns`.
  - Jest ignores `/tests/e2e/` to avoid running Playwright E2E tests.
- **Do NOT place Jest tests in:**
  - `frontend/tests/e2e` (these will be ignored by Jest and may be picked up by Playwright).

## Python/Other Tests

- **Location:** Root-level `tests/` directory is reserved for backend (Python) tests only.
- **Do NOT place JS/TS tests here.**

## Best Practices

- Keep E2E and unit tests in their respective directories.
- If you add new test files, double-check they are in the correct folder.
- If you see errors about `expect` or `describe` not being defined, check that the right runner is being used for the test type.
- If you see Playwright errors about `test.describe()` in the wrong context, check for misplaced or duplicate test files.

## Client Components: Global 'use client' Directive Approach

- We use the global 'use client' directive at the top of top-level app/page components (e.g., `/app/insights_pillar/page.tsx`, `/app/content_pillar/page.tsx`).
- This ensures that all child components (including deeply nested ones) are treated as client components by Next.js.
- **Do not** manually add 'use client' to every subcomponent unless a component is intended to be used in both server and client contexts.
- This approach avoids duplication and reduces the risk of missing the directive in new or refactored components.
- If you need a component to be client-only but used in both server and client trees, add 'use client' at the component level.

**Summary:**

- Prefer global 'use client' at the page level for all client-side pages and flows.
- Only use manual 'use client' in lower-level components if absolutely necessary.

# Session/Event Storage: Best Practices and Migration Strategy

## In-Memory Storage (MVP/Fast Iteration)

- Abstract your storage layer (e.g., `SessionStore`, `EventStore` interfaces).
- Implement with an in-memory backend (Python dict) for now.
- Centralize all access to session/event data through the store/service layer.
- Keep session/event models decoupled from storage (use Pydantic models or dataclasses).
- Ensure models are serialization-ready (JSON serializable).
- Implement expiry/cleanup logic for in-memory stores.
- Add TODOs or feature flags for future migration to persistent storage.

## Migration/Easy Button Analysis

- **Supabase/Postgres** is the "easy button" for identity, metadata, sessions, and events for most SaaS/AI apps.
- Use Supabase for:
  - Auth/identity
  - Metadata
  - Long-lived or resumable sessions
  - Event logs (chat, agent events, audit trails)
- Use Redis for fast, ephemeral session/event access (optional, can sync to Postgres for durability).
- For high-volume or real-time event streaming, consider managed Kafka, Kinesis, or Google Pub/Sub.
- For analytics, ClickHouse or TimescaleDB are popular for time-series/event data.

### Summary Table

| Use Case      | MVP/Easy Button   | Scale/Best Practice      |
| ------------- | ----------------- | ------------------------ |
| Auth/Identity | Supabase Auth     | Supabase Auth            |
| Metadata      | Supabase/Postgres | Supabase/Postgres        |
| Sessions      | Supabase/Postgres | Supabase + Redis (cache) |
| Events/Logs   | Supabase/Postgres | Kafka/Kinesis + Postgres |
| Realtime      | Supabase Realtime | Kafka/NATS + Websockets  |
| Analytics     | Supabase/Postgres | ClickHouse/TimescaleDB   |

## Best Practices for Future-Proofing

- Abstract storage logic from day one, even if only using in-memory for MVP.
- Centralize all access to session/event data.
- Keep models and business logic backend-agnostic.
- Document migration plans and add feature flags for easy backend swaps.

**Bottom line:**

- Supabase/Postgres is the "easy button" for most needs.
- If you outgrow it, you have a clear migration path to more specialized tools.
- Start simple, but architect for change.

---

**Last updated: [automated update]**
