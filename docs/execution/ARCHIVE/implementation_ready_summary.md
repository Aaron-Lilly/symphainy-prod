# Implementation Ready Summary - Architecture Aligned

**Date:** January 2026  
**Status:** ✅ **READY FOR IMPLEMENTATION** (with backend team clarification)

---

## 🎯 Executive Summary

After reviewing the platform architecture, "rules of the road", and backend SDK patterns, I've identified the correct approach to address both gaps. We'll follow the backend team's established patterns and have prepared questions for clarification.

---

## ✅ What We've Learned

### 1. Authentication Architecture ✅

**Backend Pattern:**
- ✅ Security Guard SDK initialized in `experience_main.py`
- ✅ Stored in `app.state.security_guard_sdk` for dependency injection
- ✅ SDK uses `auth_abstraction` from Public Works (follows abstraction pattern)
- ✅ SDK has `authenticate()` method (returns `AuthenticationResult`)
- ⚠️ `AuthenticationProtocol` only defines: `authenticate()`, `validate_token()`, `refresh_token()`
- ⚠️ No `register_user()` in protocol (need to check adapter)

**Implementation Path:**
- ✅ Add auth router to Experience Plane
- ✅ Use Security Guard SDK from `app.state.security_guard_sdk`
- ✅ Follow `sessions.py` pattern
- ⚠️ Need to check if `supabase_adapter` has `sign_up_with_password()` method

---

### 2. WebSocket Architecture ⚠️

**Frontend Expectation:**
- ✅ Endpoint: `/api/runtime/agent`
- ✅ Uses `RuntimeClient` connecting to `/api/runtime/agent`
- ✅ Message format: `{ type: "intent", intent: "...", session_id: "...", agent_type: "guide" | "liaison", pillar: "..." }`

**Backend State:**
- ❌ Runtime service has no WebSocket router
- ✅ Experience Plane has Guide Agent Service
- ✅ Experience Plane has WebSocket router (for execution streaming)
- ⚠️ Architecture docs show `/api/ws/agent` in some places, `/api/runtime/agent` in others

**Architecture Question:**
- Which service should own `/api/runtime/agent`?
- How should agent routing work?

---

## 📋 Questions for Backend Team

### Question 1: User Registration

**Does `supabase_adapter` have a `sign_up_with_password()` method?**

**If Yes:**
- We'll add `register_user()` to `AuthenticationProtocol` and `AuthAbstraction`
- Then use it via Security Guard SDK

**If No:**
- Should we add it to the adapter?
- Or use a different approach for registration?

---

### Question 2: WebSocket Endpoint Ownership

**Which service should own `/api/runtime/agent` WebSocket endpoint?**

**Options:**
- **Runtime Service:** Matches endpoint path, Runtime handles execution
- **Experience Plane:** User-facing APIs, already has Guide Agent Service
- **Hybrid:** Experience Plane endpoint that proxies to Runtime

**Follow-up:**
- How should agent messages be routed (guide vs liaison)?
- Should routing happen in Runtime or Experience Plane?
- How do agents get invoked from WebSocket messages?

---

## 🔧 Implementation Plan

### Phase 1: Authentication (Ready to Implement) ✅

**Steps:**
1. Check `supabase_adapter` for `sign_up_with_password()` method
2. If exists: Add `register_user()` to `AuthenticationProtocol` and `AuthAbstraction`
3. Create `auth.py` router in Experience Plane
4. Use Security Guard SDK pattern
5. Register router in `experience_service.py`

**Files to Create/Modify:**
- `symphainy_platform/civic_systems/experience/api/auth.py` (NEW)
- `symphainy_platform/civic_systems/experience/experience_service.py` (UPDATE)
- `symphainy_platform/foundations/public_works/protocols/auth_protocol.py` (UPDATE - if needed)
- `symphainy_platform/foundations/public_works/abstractions/auth_abstraction.py` (UPDATE - if needed)

---

### Phase 2: WebSocket (Awaiting Clarification) ⚠️

**Steps:**
1. Get backend team clarification on endpoint ownership
2. Implement WebSocket router in appropriate service
3. Implement agent routing logic
4. Update frontend if needed to match backend design

**Files to Create/Modify:**
- TBD based on backend team's guidance

---

## 📝 Summary

**Authentication:** ✅ **READY** - Clear pattern, just need to check registration method

**WebSocket:** ⚠️ **AWAITING CLARIFICATION** - Need backend team input on endpoint ownership

**Recommendation:**
- Check `supabase_adapter` for registration method
- Implement authentication endpoints (following clear pattern)
- Ask backend team about WebSocket before implementing
- Update frontend if needed to match backend design

---

**Last Updated:** January 2026
