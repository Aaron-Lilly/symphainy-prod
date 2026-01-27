# Phase 1: Provider Consolidation Audit

## Provider Inventory

### ✅ KEEP (Single Source of Truth)

1. **`shared/state/AppProviders.tsx`** - Main provider composition (NEW ARCHITECTURE)
   - Uses SessionBoundaryProvider pattern
   - Correct provider hierarchy
   - **Status:** KEEP - This is the canonical AppProviders

2. **`shared/state/SessionBoundaryProvider.tsx`** - Session authority
   - Single source of truth for session lifecycle
   - Manages session state machine
   - **Status:** KEEP - Core architecture component

3. **`shared/auth/AuthProvider.tsx`** - Authentication
   - Uses SessionBoundaryProvider
   - Handles login/register/logout
   - **Status:** KEEP - Single auth provider

4. **`shared/state/PlatformStateProvider.tsx`** - Platform state
   - Execution, realm, UI state
   - Subscribes to SessionBoundaryProvider
   - **Status:** KEEP - Core state provider

5. **`shared/agui/GuideAgentProvider.tsx`** - Agent chat
   - WebSocket connection for Guide Agent
   - Follows session state
   - **Status:** KEEP - Agent-specific provider

6. **`shared/agui/AppProvider.tsx`** - App state (file management)
   - File metadata, pillar state, chat state
   - Local app state (not session-related)
   - **Status:** KEEP - Different concern from PlatformStateProvider

7. **`shared/testing/EnhancedTestingProvider.tsx`** - Testing utilities
   - Testing-specific provider
   - **Status:** KEEP - Testing infrastructure

### 🔴 ARCHIVE (Duplicates)

1. **`shared/agui/AuthProvider.tsx`** - DUPLICATE
   - Old auth provider using GlobalSessionProvider
   - **Replacement:** `shared/auth/AuthProvider.tsx`
   - **Status:** ARCHIVE

2. **`shared/agui/AppProviders.tsx`** - DUPLICATE
   - Old provider composition using GlobalSessionProvider
   - **Replacement:** `shared/state/AppProviders.tsx`
   - **Status:** ARCHIVE

3. **`shared/agui/SessionProvider.tsx`** - OLD SESSION PROVIDER
   - Old session management (pre-SessionBoundaryProvider)
   - **Replacement:** `shared/state/SessionBoundaryProvider.tsx`
   - **Status:** ARCHIVE

4. **`shared/agui/GlobalSessionProvider.tsx`** - OLD SESSION PROVIDER
   - Old session management (pre-SessionBoundaryProvider)
   - **Replacement:** `shared/state/SessionBoundaryProvider.tsx`
   - **Status:** ARCHIVE

5. **`shared/session/GlobalSessionProvider.tsx`** - OLD SESSION PROVIDER
   - Old session management (pre-SessionBoundaryProvider)
   - **Replacement:** `shared/state/SessionBoundaryProvider.tsx`
   - **Status:** ARCHIVE

6. **`shared/components/SessionProvider.tsx`** - OLD SESSION PROVIDER
   - Old session management (pre-SessionBoundaryProvider)
   - **Replacement:** `shared/state/SessionBoundaryProvider.tsx`
   - **Status:** ARCHIVE

### ⚠️ REVIEW (Need to Check Usage)

1. **`shared/agui/AGUIEventProvider.tsx`** - Event handling
   - Need to check if still used
   - **Status:** REVIEW

2. **`shared/agui/WebSocketProvider.tsx`** - WebSocket provider
   - Need to check if still used (might be replaced by GuideAgentProvider)
   - **Status:** REVIEW

3. **`shared/agui/ProviderComposer.tsx`** - Provider composition utility
   - Need to check if still used
   - **Status:** REVIEW

4. **`shared/state/EnhancedStateProvider.tsx`** - Enhanced state
   - Need to check if still used
   - **Status:** REVIEW

## Import Audit

### Files Importing Archived Providers

Need to update imports in:
- Components using `shared/agui/AuthProvider` → use `shared/auth/AuthProvider`
- Components using `shared/agui/AppProviders` → use `shared/state/AppProviders`
- Components using any old session providers → use `shared/state/SessionBoundaryProvider`

## Action Plan

1. ✅ Create audit document (this file)
2. ⏳ Check usage of REVIEW providers
3. ⏳ Create archive directory structure
4. ⏳ Move archived providers to archive
5. ⏳ Update all imports
6. ⏳ Test build
7. ⏳ Verify no regressions
