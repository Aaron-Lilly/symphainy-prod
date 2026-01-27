# 10 Key Architectural Principles - CTO Validated

**Date:** January 24, 2026  
**Status:** ✅ **VALIDATED WITH CLARIFICATIONS**  
**Purpose:** Canonical architectural principles for all platform development

---

## Executive Summary

These 10 principles represent the **non-negotiable architectural foundation** of the Symphainy platform. They have been validated by the CTO with important clarifications to prevent misinterpretation under pressure.

**What These Principles Protect Us From:**
- Demo-ware architectures
- Agent frameworks that can't be audited
- UX-driven execution bugs
- Tool lock-in
- Non-replayable outcomes
- "Magic" behavior no one can explain later

They are not academic. They are defensive.

---

## The 10 Principles (Refined)

### 1. Runtime as Single Execution Authority ⚠️ **REFINED**

> Runtime is the sole authority for **committed execution and durable system state**.
> Other components may hold ephemeral, local, or speculative state, but only Runtime can make reality true.

**What This Means:**
- Runtime owns **authoritative execution and durable state transitions**, not *all* state
- Frontend CAN have ephemeral UI state
- Agents CAN reason internally (speculative state)
- Session state CAN exist independently
- But only Runtime can make **committed, durable changes**

**What This Prevents:**
- ❌ "Frontend can't have state" (misinterpretation)
- ❌ "Agents can't reason internally" (misinterpretation)
- ❌ "Session state is invalid unless Runtime mutates it" (misinterpretation)

**Validation Question:** "If an agent produces a great answer but Runtime never recorded an execution, what happened?"
**Expected Answer:** "It didn't happen. The answer is advisory or speculative, not real."

---

### 2. Only Realms Touch Data (Through Abstractions) 🧭 **REFINED**

> Only Realm domain services perform data access and mutation, always via Public Works abstractions. Runtime orchestrates; Realms execute.

**What This Means:**
- **Only Realm logic may perform domain data mutations or reads**
- **Through Public Works abstractions**
- Runtime *coordinates* data access; Realms *perform* it

**What This Prevents:**
- ❌ Putting data logic in Runtime
- ❌ Sneaking queries into orchestration code
- ❌ Direct database calls outside Realms

**Validation Question:** "Can a Realm call Supabase directly if it's faster?"
**Expected Answer:** "No. All access goes through Public Works, even if it's slower or annoying."

---

### 3. Public Works Abstractions for All Infrastructure ✅ **STRONG**

> All infrastructure access must go through Public Works abstractions.

**What This Means:**
- Public Works is **not a convenience layer**
- Public Works is **a governance boundary**
- Enables swappability (Redis → ArangoDB, GCS → S3, etc.)
- Adapters can call infrastructure directly (that's their job)

**What This Prevents:**
- ❌ "It's just a wrapper" thinking (red flag)
- ❌ Direct infrastructure calls in business logic
- ❌ Tool lock-in

**Validation Question:** "Can a Realm call Supabase directly if it's faster?"
**Expected Answer:** "No. All access goes through Public Works, even if it's slower or annoying."

---

### 4. Session-First, Auth-Second ✅ **STRATEGICALLY IMPORTANT**

> Sessions exist independently of authentication. Authentication upgrades sessions.
> Authentication *upgrades* trust and capability; it does not create existence.

**What This Means:**
- Sessions can be created anonymously (no auth required)
- Authentication adds user_id/tenant_id to existing session
- Session ID remains the same (upgrade, not replacement)
- Frontend creates session first, then authenticates
- You are an **adoption/runtime layer**, not a consumer app
- Anonymous exploration is a feature, not a loophole

**What This Prevents:**
- ❌ Auth-first thinking (blocks anonymous exploration)
- ❌ Session invalidation on auth changes
- ❌ Consumer app patterns

---

### 5. State Drives Actions, Not Components ⚠️ **REFINED**

> UI components may **express intent**, but never **cause execution**.
> Execution happens only as a result of backend state transitions.
> Intent ≠ execution. Events ≠ side effects.

**What This Means:**
- Components subscribe to state, not trigger actions
- State changes drive UI updates
- Backend state is source of truth
- Frontend state syncs with backend state
- UI can express intent, but execution is backend-driven

**What This Prevents:**
- ❌ Weird indirection (overcorrection)
- ❌ Fear of user intent (overcorrection)
- ❌ Over-passive UI (overcorrection)
- ❌ Direct capability calls from components

**Validation Question:** "If a frontend developer wants to 'just call a service' to speed things up, what do we say?"
**Expected Answer:** "They must express intent. Direct calls violate governance and determinism."

---

### 6. Working Code Only (No Stubs/Placeholders/Cheats) 🧭 **REFINED**

> No code may simulate success, bypass governance, or hide missing implementation.
> Incomplete functionality must fail loudly and truthfully.

**What This Means:**
- Ban: Fake success paths, hard-coded returns, mocked reality pretending to be production
- Allow: Feature flags, "Not yet implemented" surfaced honestly, explicit `Unsupported` responses
- Tests must fail if code has cheats
- Placeholders only if explicitly documented and resolved in same sprint

**What This Prevents:**
- ❌ Fake success paths
- ❌ Hard-coded returns
- ❌ Mocked reality pretending to be production
- ❌ Absolutism during final push (blocks velocity)

**What This Allows:**
- ✅ Feature flags
- ✅ Honest "Not yet implemented" responses
- ✅ Explicit `Unsupported` responses

---

### 7. Architecture Guide Wins (Canonical) ✅ **WITH PROCESS HOOK**

> If code conflicts with architecture guide, the architecture guide is correct.
> Changes require architectural review. Drift is not allowed silently.

**What This Means:**
- Architecture guide (`docs/architecture/north_star.md`) is source of truth
- Code must follow architecture guide
- If code doesn't match, fix the code
- Architecture guide updated only through ADRs
- **Process:** Changes require architectural review

**What This Prevents:**
- ❌ "Pragmatic" deviations from architecture
- ❌ "Temporary" architectural violations
- ❌ Silent drift (people quietly fork reality)

---

### 8. Intent-Based Execution (Not Capability Calls) ✅ **VERY STRONG**

> Frontend submits intents. Runtime orchestrates execution. Domain services handle intents.
> Intents are **commitment requests**, not function calls.

**What This Means:**
- Frontend does NOT call capabilities directly
- Frontend submits intents via Runtime
- Runtime routes intents to appropriate domain services
- Domain services return artifacts, not side effects
- Intents are commitment requests, not RPC calls

**What This Prevents:**
- ❌ Direct capability calls from frontend
- ❌ RPC thinking (intents ≠ function calls)
- ❌ Non-deterministic execution

**Validation Question:** "Where does AGUI end and Intent begin?"
**Expected Answer:** "AGUI expresses experience and interaction; Intent is the execution contract Runtime understands."

---

### 9. Policy-Governed Sagas (Not ACID) ⚠️ **NEEDS GROUNDING**

> Execution is governed by policy. Sagas replace ACID transactions.
> Intent-bounded execution with explicit promotion workflows.

**What This Means:**
- No traditional ACID transactions
- Policy-governed sagas for multi-step operations
- Intent-bounded execution
- Explicit promotion workflows
- Compensatable failure patterns

**What This Prevents:**
- ❌ ACID transaction thinking
- ❌ Commits in agents
- ❌ Commits in domain services

**Validation Question:** "What happens if a saga partially completes and then policy changes?"
**Expected Answer:** "The saga reflects the policy at execution time; remediation or promotion is explicit and auditable."

**Team Must Understand:**
- Where policies live
- How failures are recorded
- What "promotion" actually means

---

### 10. Frontend as Platform Runtime (Not Web App) ⚠️ **HIGH RISK OF MISINTERPRETATION**

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

**Validation Question:** "What is the frontend *not* allowed to decide?"
**Expected Answer:** "Outcomes, execution paths, data mutation, policy enforcement."

---

## 7 Alignment Questions (For Team Validation)

### 1. "If an agent produces a great answer but Runtime never recorded an execution, what happened?"

**Expected Answer:**
> It didn't happen. The answer is advisory or speculative, not real.

🚨 **Red flag if they say:**
- "The agent executed it"
- "The UI handled it"

---

### 2. "Where does AGUI end and Intent begin?"

**Expected Answer:**
> AGUI expresses experience and interaction; Intent is the execution contract Runtime understands.

🚨 **Red flag if they blur the two or say "they're basically the same."**

---

### 3. "Can a Realm call Supabase directly if it's faster?"

**Expected Answer:**
> No. All access goes through Public Works, even if it's slower or annoying.

🚨 **Any "just this once" answer is a fail.**

---

### 4. "What kinds of state are allowed outside Runtime?"

**Expected Answer:**
> Ephemeral UI state, speculative agent reasoning, session-local context — but nothing authoritative or durable.

This tells you whether they truly understand Principle #1.

---

### 5. "What happens if a saga partially completes and then policy changes?"

**Expected Answer:**
> The saga reflects the policy at execution time; remediation or promotion is explicit and auditable.

🚨 **Red flag if they assume rollback "just happens."**

---

### 6. "If a frontend developer wants to 'just call a service' to speed things up, what do we say?"

**Expected Answer:**
> They must express intent. Direct calls violate governance and determinism.

This tests cultural alignment, not just technical understanding.

---

### 7. "What is the frontend *not* allowed to decide?"

**Expected Answer:**
> Outcomes, execution paths, data mutation, policy enforcement.

If they answer this crisply, you're aligned.

---

## Final Assessment

**You're not "almost aligned."**
**You're architecturally aligned and now refining precision.**

That's exactly where you want to be before the final push.

---

**Last Updated:** January 24, 2026  
**Status:** ✅ **CTO VALIDATED WITH CLARIFICATIONS**
