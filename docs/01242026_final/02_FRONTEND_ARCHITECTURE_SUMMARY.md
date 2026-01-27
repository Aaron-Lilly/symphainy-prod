# Frontend Architecture Summary (symphainy-frontend)

**Date:** January 24, 2026  
**Status:** ✅ **COMPREHENSIVE REFERENCE**  
**Purpose:** Complete guide to frontend architecture, patterns, state management, and how to work with them

---

## Executive Summary

The Symphainy frontend (`symphainy-frontend/`) is **not a traditional web application**. It is a **platform runtime** that renders state, hosts experience logic, and compiles user interaction into intent.

**Key Principle:** The frontend renders platform state, hosts experience logic, and compiles user interaction into intent. It does not decide outcomes.

---

## Core Architecture Principles

### 1. Frontend as Platform Runtime (Not Web App)

> The frontend renders platform state, hosts experience logic, and compiles user interaction into intent.
> It does not decide outcomes.

**What This Means:**
- Frontend renders state from backend
- Frontend submits intents, not capability calls
- Frontend manages session state, not business state
- Frontend follows Session Boundary pattern
- Frontend does NOT orchestrate, own workflows, or decide outcomes

**What This Prevents:**
- ❌ "Frontend does orchestration" (misinterpretation)
- ❌ "Frontend owns workflows" (misinterpretation)
- ❌ "Frontend replaces Runtime" (misinterpretation)
- ❌ Business logic in frontend
- ❌ Direct database access from frontend

### 2. Session-First, Auth-Second

> Sessions exist independently of authentication. Authentication upgrades sessions.
> Authentication *upgrades* trust and capability; it does not create existence.

**What This Means:**
- Sessions can be created anonymously (no auth required)
- Authentication adds user_id/tenant_id to existing session
- Session ID remains the same (upgrade, not replacement)
- Frontend creates session first, then authenticates
- Anonymous exploration is a feature, not a loophole

### 3. State Drives Actions, Not Components

> UI components may **express intent**, but never **cause execution**.
> Execution happens only as a result of backend state transitions.
> Intent ≠ execution. Events ≠ side effects.

**What This Means:**
- Components subscribe to state, not trigger actions
- State changes drive UI updates
- Backend state is source of truth
- Frontend state syncs with backend state
- UI can express intent, but execution is backend-driven

---

## Frontend Structure

```
symphainy-frontend/
├── app/                        ← Next.js App Router
│   ├── (protected)/           ← Protected routes (require session)
│   │   ├── pillars/
│   │   │   ├── content/       ← Content Pillar
│   │   │   ├── insights/      ← Insights Pillar
│   │   │   ├── journey/       ← Journey Pillar
│   │   │   └── business-outcomes/  ← Outcomes Pillar
│   │   └── admin/             ← Admin Dashboard
│   └── login/                 ← Authentication
│
├── components/                 ← UI Components
│   ├── content/               ← Content pillar components
│   ├── insights/              ← Insights pillar components
│   ├── operations/             ← Journey/Operations components
│   └── auth/                   ← Authentication components
│
└── shared/                     ← Shared infrastructure
    ├── state/                  ← State management
    │   ├── SessionBoundaryProvider.tsx  ← Session lifecycle
    │   ├── PlatformStateProvider.tsx    ← Platform state
    │   └── AppProviders.tsx             ← Provider composition
    │
    ├── services/               ← Service layer
    │   ├── ExperiencePlaneClient.ts     ← Experience Plane API client
    │   ├── RuntimeClient.ts             ← Runtime WebSocket client
    │   └── ServiceLayerAPI.ts           ← Unified service layer
    │
    ├── hooks/                  ← React hooks
    │   ├── useFileAPI.ts       ← File operations
    │   ├── useContentAPI.ts    ← Content operations
    │   ├── useInsightsAPI.ts    ← Insights operations
    │   └── useOperationsAPI.ts ← Operations/Journey operations
    │
    ├── components/             ← Shared UI components
    │   ├── chatbot/            ← Chat components
    │   └── MainLayout.tsx      ← Main layout
    │
    └── config/                 ← Configuration
        └── api-config.ts       ← API endpoint configuration
```

---

## State Management Architecture

### Three-Layer State Model

1. **Session Boundary Layer** - Session lifecycle (SessionBoundaryProvider)
2. **Platform State Layer** - Platform state (PlatformStateProvider)
3. **UI State Layer** - Component-local state (React useState)

### SessionBoundaryProvider

**Purpose:** Single source of truth for session lifecycle management.

**Location:** `shared/state/SessionBoundaryProvider.tsx`

**Responsibilities:**
- Session creation (anonymous and authenticated)
- Session upgrade (add auth to existing session)
- Session invalidation (404/401 = state transition, not error)
- Session recovery (automatic after invalidation)

**Session Status States:**
- `Initializing` - Checking existing session
- `Anonymous` - Valid anonymous session
- `Authenticating` - Login in progress
- `Active` - Valid authenticated session
- `Invalid` - 404/401 received - session doesn't exist
- `Recovering` - Creating new session after invalidation

**Key Principle:** Sessions are lease-based, not guaranteed. 404/401 = state transition, not error.

**Usage:**
```typescript
const { state, createAnonymousSession, upgradeSession } = useSessionBoundary();
const sessionId = state.sessionId;
const status = state.status; // SessionStatus enum
```

### PlatformStateProvider

**Purpose:** Unified state management for platform state.

**Location:** `shared/state/PlatformStateProvider.tsx`

**Responsibilities:**
- Session state (synced with Runtime)
- Execution state (from Runtime)
- Realm state (from State Surface)
- UI state (local)

**State Structure:**
```typescript
interface PlatformState {
  session: SessionState;      // Session info
  execution: ExecutionState;    // Execution status
  realm: RealmState;           // Realm state (content, insights, journey, outcomes)
  ui: UIState;                // UI state (current pillar, sidebar, etc.)
}
```

**Key Methods:**
- `getRealmState(realm, key)` - Get realm state
- `setRealmState(realm, key, value)` - Set realm state
- `syncWithRuntime()` - Sync with backend Runtime

**Usage:**
```typescript
const { state, getRealmState, setRealmState } = usePlatformState();
const contentState = getRealmState('content', 'files');
await setRealmState('content', 'files', updatedFiles);
```

**Key Principle:** PlatformStateProvider syncs with Runtime every 30 seconds automatically.

---

## Service Layer Architecture

### Service Layer Pattern

**Purpose:** All API calls go through service layer hooks.

**Key Principle:** Components never call APIs directly. Components use hooks.

### Service Layer Hooks

**File Operations:**
- `useFileAPI()` - File upload, list, parse, delete

**Content Operations:**
- `useContentAPI()` - Content pillar operations

**Insights Operations:**
- `useInsightsAPI()` - Insights pillar operations

**Operations/Journey:**
- `useOperationsAPI()` - Journey/Operations operations

**Service Layer API:**
- `useServiceLayerAPI()` - Generic service layer access

### ExperiencePlaneClient

**Purpose:** Unified client for Experience Plane API interactions.

**Location:** `shared/services/ExperiencePlaneClient.ts`

**Responsibilities:**
- Session management → Traffic Cop SDK → Runtime
- Intent submission → Runtime Client → Runtime
- Execution status → Runtime Client → Runtime

**Key Methods:**
- `createSession(request)` - Create session
- `createAnonymousSession()` - Create anonymous session
- `submitIntent(intent)` - Submit intent
- `getExecutionStatus(executionId)` - Get execution status

**Usage:**
```typescript
const client = new ExperiencePlaneClient();
const session = await client.createAnonymousSession();
const result = await client.submitIntent({
  intent_type: "parse_file",
  file_id: "...",
  session_id: session.session_id
});
```

### RuntimeClient

**Purpose:** WebSocket client for agent communication.

**Location:** `shared/services/RuntimeClient.ts`

**Responsibilities:**
- WebSocket connection to `/api/runtime/agent`
- Agent message streaming
- Authentication token handling

**Key Principle:** WebSocket connects when `SessionStatus === Active` (not when authenticated).

---

## Component Architecture

### Layering Model

```
UI Layer (Components)
    ↓
View Models (Hooks)
    ↓
Providers (State Management)
    ↓
Services (API Clients)
    ↓
Transport (HTTP/WebSocket)
```

**Key Principle:** No direct component-to-transport coupling.

### Component Patterns

#### Pattern 1: State Subscription

```typescript
// ✅ CORRECT: Component subscribes to state
const { state } = usePlatformState();
const files = getRealmState('content', 'files');

// UI renders based on state
return <FileList files={files} />;
```

#### Pattern 2: Intent Expression

```typescript
// ✅ CORRECT: Component expresses intent
const { submitIntent } = useServiceLayerAPI();

const handleUpload = async (file: File) => {
  // Express intent, don't execute
  await submitIntent({
    intent_type: "upload_file",
    file: file,
    session_id: sessionId
  });
};
```

#### Pattern 3: Service Layer Usage

```typescript
// ✅ CORRECT: Use service layer hook
const { uploadAndProcessFile } = useFileAPI();

const handleUpload = async (file: File) => {
  const result = await uploadAndProcessFile(file, sessionId, fileType);
  // Handle result
};
```

---

## API Integration Patterns

### Pattern 1: Service Layer Hook

**All API calls must go through service layer hooks.**

**Before (Breaking):**
```typescript
// ❌ WRONG: Direct API call
import { listFiles } from "@/lib/api/fms";
const files = await listFiles(token);
```

**After (Required):**
```typescript
// ✅ CORRECT: Use service layer hook
import { useFileAPI } from "@/shared/hooks/useFileAPI";
const { listFiles } = useFileAPI();
const files = await listFiles(); // Token automatic
```

### Pattern 2: Session Boundary Integration

**Service layer hooks automatically get tokens from SessionBoundaryProvider.**

**Pattern:**
```typescript
// Service layer hook implementation
export function useFileAPI() {
  const { state: sessionState } = useSessionBoundary();
  const token = sessionState.accessToken; // Automatic
  
  const listFiles = async () => {
    // Use token automatically
    return await fileAPI.listFiles(token);
  };
  
  return { listFiles };
}
```

### Pattern 3: Error Handling

**Errors are signals, not exceptions.**

**Pattern:**
```typescript
const { data, error } = await uploadAndProcessFile(file, sessionId, fileType);

if (error) {
  // Error is a signal - handle it
  setError(error.message);
  return;
}

// Success - update state
await setRealmState('content', 'files', [...files, data.file]);
```

---

## WebSocket Architecture

### WebSocket Follows Session

**Key Principle:** WebSocket connects when `SessionStatus === Active`, not when authenticated.

**Pattern:**
```typescript
// ✅ CORRECT: WebSocket follows session
useEffect(() => {
  if (sessionStatus === SessionStatus.Active) {
    wsClient.connect(sessionId, accessToken);
  } else {
    wsClient.disconnect();
  }
}, [sessionStatus, sessionId]);
```

**What This Prevents:**
- ❌ WebSocket created on component mount
- ❌ Retries on 403/401 (we fixed this)
- ❌ Connections before session is Active

---

## Authentication Flow

### Session-First Pattern

1. **Create Anonymous Session** (no auth required)
   ```typescript
   const { createAnonymousSession } = useSessionBoundary();
   await createAnonymousSession();
   ```

2. **Authenticate User** (upgrades session)
   ```typescript
   const { upgradeSession } = useSessionBoundary();
   await upgradeSession({
     user_id: user.id,
     tenant_id: user.tenant_id,
     access_token: token
   });
   ```

3. **Session ID Remains Same** (upgrade, not replacement)

**Key Principle:** Authentication upgrades trust and capability; it does not create existence.

---

## What to Do / What Not to Do

### ✅ DO

- Use `useSessionBoundary()` for session management
- Use `usePlatformState()` for platform state
- Use service layer hooks for all API calls
- Subscribe to state changes in components
- Express intent, don't execute
- Handle errors as signals
- Connect WebSocket when `SessionStatus === Active`

### ❌ DON'T

- Call APIs directly from components
- Use `localStorage` for session storage
- Create WebSocket on component mount
- Check `isAuthenticated` instead of `SessionStatus`
- Put business logic in frontend
- Access database directly from frontend
- Bypass service layer hooks

---

## Common Issues & Fixes

### Issue: "getPillarState/setPillarState are placeholders"

**Fix:** Use `usePlatformState()` instead.

**Pattern:**
```typescript
// ❌ WRONG: Placeholder
const getPillarState = (pillar: string) => null;
const setPillarState = async (pillar: string, state: any) => {};

// ✅ CORRECT: Use PlatformStateProvider
const { getRealmState, setRealmState } = usePlatformState();
const contentState = getRealmState('content', 'files');
await setRealmState('content', 'files', updatedFiles);
```

### Issue: "Mock user_id in file upload"

**Fix:** Use actual user ID from session.

**Pattern:**
```typescript
// ❌ WRONG: Mock user_id
user_id: "mock-user"

// ✅ CORRECT: Use session user_id
const { state } = useSessionBoundary();
user_id: state.userId || sessionState.user_id
```

### Issue: "File upload mock fallback"

**Fix:** Remove mock fallback, fail gracefully.

**Pattern:**
```typescript
// ❌ WRONG: Create mock file when session fails
if (sessionId === null) {
  const mockFile = { ... }; // Don't do this
}

// ✅ CORRECT: Fail gracefully
if (!sessionId) {
  throw new Error("Session not available. Please ensure you're logged in.");
}
```

### Issue: "Direct API calls in components"

**Fix:** Use service layer hooks.

**Pattern:**
```typescript
// ❌ WRONG: Direct fetch
const response = await fetch('/api/files', {
  headers: { Authorization: `Bearer ${token}` }
});

// ✅ CORRECT: Service layer hook
const { listFiles } = useFileAPI();
const files = await listFiles();
```

---

## Migration Status

### ✅ Completed

- Provider consolidation (Phase 1)
- Service layer standardization (Phase 2 - partial)
- SessionBoundaryProvider implementation
- PlatformStateProvider implementation

### ⏳ In Progress

- Complete service layer migration (52 components still need migration)
- Remove GlobalSessionProvider (legacy)
- Complete state management migration

### 📋 Planned

- AGUI foundation (Phase 2.5)
- AGUI state layer
- Journey step enforcement

---

## Testing Patterns

### Unit Tests

Test components in isolation with mocked hooks.

### Integration Tests

Test component-service layer integration.

### E2E Tests

Test full user journeys with real backend.

**Key Principle:** Tests must fail if code has cheats. No tests that pass with stubs.

---

## Next Steps

1. Complete PlatformStateProvider migration (52 components)
2. Remove GlobalSessionProvider (legacy)
3. Implement Business Outcomes handlers
4. Remove all mock/placeholder code
5. Complete service layer migration

---

**Last Updated:** January 24, 2026  
**Status:** ✅ **COMPREHENSIVE REFERENCE**
