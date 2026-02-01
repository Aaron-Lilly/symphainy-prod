# Getting On Track: Honest Assessment and Plan

**Purpose:** Step back, name what’s going wrong, and lock in a single path so we build the operating system with minimum functionality for MVP—methodically, explainably, with safe boundaries at every seam.

**Audience:** Anyone struggling with “we keep reintroducing anti-patterns.” This doc is the reset.

---

## Part 1: Honest Assessment — What’s Going Wrong

### 1.1 You’re Not Doing “It” Wrong; the Process Is

You’re trying to do the right thing: build layer by layer, audit → fix → probe → document, with safe boundaries. The problem isn’t your intent; it’s that we never **locked** the contract and then **enforced** it in one pass. So every time we touch a layer we:

- **Fix in context** — We find a gap (e.g. “Curator has no backing”) and we fix that one place. We don’t first write down “what Public Works must guarantee” and then make the whole layer conform. So we get a mix of strict and lenient: some getters fail fast, others return None and callers are supposed to handle it, others return empty and log. The boundary is underspecified.
- **Add fallbacks “so nothing breaks”** — We add “if table missing return []”, “if curator_service is None then no-op”, “if adapter missing log and return None”. That keeps the demo running but erodes the guarantee. For a true v1.0 system, **required** capabilities must not have silent fallbacks. Either the capability is there or we fail at boot.
- **Reference infrastructure directly where we shouldn’t** — Adapters leak (or we build services that take adapters in tests), getters return Optional and callers don’t consistently fail fast, and “protocol-only at the boundary” is stated but not enforced everywhere. So we keep “fixing” one caller at a time instead of making the boundary the only way in.
- **Spread “what we need” across many docs** — INTERCEPT_ALIGNMENT_CONTRACT, PLATFORM_SDK_REQUIREMENT_SPEC, PLATFORM_CONTRACT, FOUNDATION_CONTRACT_PASS_STRATEGY, CURATOR_*, MEET_IN_THE_MIDDLE_PLAN, etc. There is no **single** “Platform V1.0 / Public Works Contract” that says: “Public Works SHALL provide exactly these getters; each SHALL return a protocol implementation or the process SHALL NOT start; no adapter leak; no fallback for required capabilities.” So when we implement, we’re reconciling on the fly and fallbacks creep in.

### 1.2 Why It Keeps Happening

- **No single source of truth** — The contract is distributed. We don’t have one checklist that says “required getters: A, B, C; each must return protocol or raise; no Optional for required.”
- **No “done” gate** — We don’t say “Public Works is NOT done until: (1) contract doc exists and is agreed, (2) code conforms (audit passes), (3) probes pass, (4) no required capability has a silent fallback.” So we ship partial compliance and fix later.
- **Curator (and others) built before the foundation was solid** — We built Curator on top of Public Works without first nailing Public Works’ contract. So Curator inherited the same looseness (optional this, fallback that). Your instinct to **fix Public Works first, then Curator with schema and migrations from the start** is correct.

### 1.3 What You’re Doing Right

- **Genesis protocol** — Supabase (and required infra) is already required there; boot is gated. That’s the right shape.
- **Wanting one pattern** — Contract → Protocol → Abstraction → Adapter (CTA), no fallbacks, no half measures. That *is* what the platform needs to operate as a true v1.0 system.
- **Wanting to audit and fix, then test** — Audit what we have vs what we need, fix the gaps, then use the testing methodology to ensure Public Works actually provides and guarantees the foundation. That’s the right sequence.
- **Curator after foundation, with schema first** — Start Curator with Supabase schema and migration scripts, then build adapter → abstraction → protocol on top. No in-memory-only as the final answer. Right.

---

## Part 2: The Corrected Approach — One Contract, One Pass, No Fallbacks

### 2.1 Order of Operations

1. **Review** the new platform vision and MVP required elements (already in PRACTICAL_REALITY_OVERLAY, PLATFORM_CONTRACT, INTERCEPT_ALIGNMENT_CONTRACT).
2. **Document** the CTA pattern as **REQUIRED** for the platform — in one place, with “no fallbacks for required capabilities” and “adapters never cross the boundary.”
3. **Write** a single **Public Works Contract** (or extend PLATFORM_CONTRACT §Public Works): list every boundary getter, its return type (protocol), and whether it’s **required** or **optional**. Required = boot fails if missing. Optional = may return None; callers must handle.
4. **Audit** Public Works code against that contract: every getter, every fallback, every adapter reference. Produce a gap list.
5. **Fix** all gaps in one pass: remove or tighten fallbacks for required capabilities; ensure no adapter leak; make required getters fail fast when dependency is missing.
6. **Probe** using the existing testing methodology: boot with required config succeeds; boot without required config fails with clear error; boundary getters return protocol types; no silent degradation.
7. **Document** “Public Works contract satisfied as of &lt;date&gt;” and “how Public Works fails and when.” Then **lock**: changes to Public Works require contract update or explicit exception.
8. **Then** start Curator: schema and migration scripts for Supabase first; then adapter → abstraction → protocol; then wire to boundary. No Curator without Supabase; no in-memory-only as production path.

### 2.2 Why This Gets You On Track

- **Single source of truth** — The Public Works Contract (and the CTA doc) are the only place we look to decide “is this allowed?”
- **Clear done criterion** — Public Works is “done” when the contract is written, the audit passes, the fixes are in, and the probes pass. We don’t move to Curator until that’s true.
- **No more “fix in context” for foundations** — When we find a foundation gap while working on Runtime or Civic or Curator, we document the gap, fix the foundation (and update the contract if needed), re-run the foundation probes, then continue. We don’t work around it in the upper layer.
- **Curator starts clean** — Schema and migrations first; then one backing (Supabase); then protocol at the boundary. No optional Curator, no in-memory-only for production.

---

## Part 3: CTA Pattern — REQUIRED for the Platform (No Fallbacks, No Half Measures)

The platform **shall** use this pattern for every capability that crosses the foundation boundary. No exceptions for “quick fix” or “demo.”

### 3.1 Contract (What the Platform Guarantees)

- **At the boundary** (what Team B / Runtime / Civic see): only **protocol-typed** getters. No adapter types, no “optional adapter,” no raw client references.
- **Required capability:** If the contract says a getter is **required**, then when the dependency (adapter, config) is missing, **boot fails** with a clear, actionable error. No “return None and let the caller handle it.” No “log and return empty.”
- **Optional capability:** Only if the contract explicitly marks a getter as **optional** may it return None. Callers must check and fail fast (e.g. RuntimeError with “Platform contract §8A”) when they need it and it’s missing.
- **MVP use cases** drive what’s required. If an MVP flow needs X, then X is required and there is no fallback.

### 3.2 Protocol (The Type at the Boundary)

- Every boundary getter returns a **protocol type** (e.g. `StateManagementProtocol`, `FileStorageProtocol`, `CuratorProtocol`). The type is defined in a single place (e.g. `foundations/public_works/protocols/`). Callers type against the protocol only.
- The protocol has the **minimum** methods needed for the platform and MVP. No “we might need this later” in the protocol unless it’s in the contract.

### 3.3 Abstraction (The Implementation Behind the Boundary)

- The **abstraction** implements the protocol. It is the only layer that talks to the adapter. It translates protocol calls into adapter calls (or multiple adapters). It does **not** expose the adapter to callers.
- One abstraction per capability (or per cohesive group). The foundation service **holds** the abstraction and exposes it only via the getter that returns the **protocol** type.

### 3.4 Adapter (The Raw Technology, Never Exposed)

- The **adapter** is the raw client (Supabase, Redis, Arango, GCS, etc.). It lives **inside** Public Works (or inside the abstraction’s package). It is **never** returned from a boundary getter. `get_supabase_adapter()` and the like **raise** or are not part of the boundary.
- Required infra (per PLATFORM_CONTRACT / Genesis): if the adapter can’t be created (config missing, unreachable), **boot fails**. No “create Public Works with half the adapters and hope for the best.”

### 3.5 Rules (No Fallbacks, No Half Measures)

1. **No fallback for required capabilities.** If the contract says “get_X() is required,” then get_X() either returns a protocol implementation or the process fails at boot. No “return None and log.”
2. **No adapter at the boundary.** No getter returns an adapter. No caller receives an adapter from the foundation.
3. **No “optional” for MVP-critical path.** For everything the MVP needs (state, file storage, registry, auth, Curator, etc.), the contract must list it as required and the code must fail fast if it’s missing.
4. **One contract document.** The Public Works Contract (see Part 4) is the single source of truth for “what getters exist, what they return, and whether they’re required or optional.”

---

## Part 4: Public Works Contract — Single Source of Truth (To Be Filled and Audited Against)

This section is the **template** for the single Public Works contract. It should be filled once, agreed, then the code audited and fixed against it.

### 4.1 Scope

- **Public Works** = the foundation service that owns adapters and abstractions and exposes **only** protocol-typed getters.
- **Boundary** = the set of getters that Runtime, Civic, and Platform SDK use. Nothing else is the “official” way to get capability from Public Works.

### 4.2 Required Getters (Boot Fails If Missing)

| Getter | Protocol Type | Backing (Adapter) | Notes |
|--------|----------------|-------------------|--------|
| (To be filled from INTERCEPT_ALIGNMENT_CONTRACT + PLATFORM_CONTRACT) | | | |

Example rows (to be completed in the actual contract pass):

- `get_state_abstraction()` → StateManagementProtocol (Redis + Arango)
- `get_file_storage_abstraction()` → FileStorageProtocol (GCS + Supabase file)
- `get_artifact_storage_abstraction()` → ArtifactStorageProtocol
- `get_registry_abstraction()` → Registry contract (Supabase)
- `get_auth_abstraction()` → AuthenticationProtocol (Supabase)
- `get_tenant_abstraction()` → TenancyProtocol (Supabase)
- `get_wal_backend()` → EventLogProtocol (Redis)
- `get_curator_service()` → CuratorProtocol (Supabase + artifact plane) — Curator required, Supabase-only

All of the above: if the backing adapter or dependency is missing, **Public Works initialize() fails** (raises). No partial init.

### 4.3 Optional Getters (May Return None; Callers Must Check)

(Only capabilities that are explicitly not required for MVP. List them; everything else is required.)

| Getter | Protocol Type | When None |
|--------|----------------|-----------|
| (List only if truly optional) | | |

### 4.4 What Must NOT Exist

- No getter that returns an adapter (e.g. get_supabase_adapter). Those raise or are removed from the boundary.
- No “if adapter missing, return None and log” for a **required** getter.
- No caller that receives an adapter from Public Works. Audit: GovernanceService, Runtime, Civic — they use only the boundary getters and protocol types.

---

## Part 5: Audit Checklist (Public Works)

Use this **after** the contract (§4) is filled. For each item, pass = “yes,” fail = “gap to fix.”

1. **Contract doc exists** — One document (this one or PUBLIC_WORKS_CONTRACT.md) lists every boundary getter, its protocol type, and required vs optional.
2. **Required getters fail when dependency missing** — For each required getter, if the backing adapter or abstraction can’t be built, Public Works `initialize()` raises (no silent None).
3. **No adapter leak** — No boundary getter returns an adapter. No public method `get_*_adapter()` that returns an adapter; they raise or don’t exist.
4. **No fallback for required** — No “if table missing return []”, “if client missing return None” for a required capability. Either the capability is there or we fail.
5. **Protocol types only** — Every boundary getter’s return type is a protocol (or a type that implements a protocol). No raw abstraction class in the type signature if we have a protocol for it.
6. **Probes pass** — Boot with full required config succeeds; boot without required config fails with clear error; boundary getters return expected types.
7. **Documentation** — “Public Works contract satisfied as of &lt;date&gt;” and “how Public Works fails and when” are written and linked from MEET_IN_THE_MIDDLE_PLAN.

---

## Part 6: Then Curator — Schema First, No Half Measures

After Public Works passes the audit and probes:

1. **Schema and migrations** — Define Supabase tables for Curator: solution_registry, intent_registry, realm_registry, registry_entries, and (for capability/agent) capability_registry, agent_registry (or equivalent). Write migration scripts. No Curator without these tables (or explicit migration path).
2. **Adapter** — Supabase adapter (already exists). Curator uses it only inside the abstraction; it never crosses the boundary.
3. **Abstraction** — One Curator abstraction that implements CuratorProtocol: register_capability, discover_agents, get_domain_registry, promote_to_platform_dna (and sovereignty methods when we add policy). All backed by Supabase (and artifact plane where needed). No in-memory-only path for production.
4. **Protocol** — CuratorProtocol is the boundary type. get_curator_service() returns it. Required: no Optional; if Curator can’t be built (Supabase missing), boot fails.
5. **No fallbacks** — Curator doesn’t “degrade” to in-memory. It’s Supabase-backed or we don’t run.

---

## Part 7: Summary — What To Do Next

1. **Adopt this doc** as the “get on track” plan. Use Part 3 (CTA) as the **required** pattern. Use Part 4 as the template for the single Public Works contract.
2. **Fill** the Public Works contract (Part 4.2, 4.3) from INTERCEPT_ALIGNMENT_CONTRACT and PLATFORM_CONTRACT — one list of getters, required vs optional.
3. **Audit** Public Works code against Part 5 (and the filled contract). Produce a gap list.
4. **Fix** all gaps: required getters fail when dependency missing; no adapter leak; no fallback for required capabilities.
5. **Probe** with existing methodology; document “contract satisfied” and “how it fails.”
6. **Lock** Public Works: changes require contract update or explicit exception.
7. **Start Curator** with schema and migrations, then adapter → abstraction → protocol, then wire to boundary.

You’re not doing the wrong thing. The process wasn’t locked to one contract and one pass. Lock it now; then build Curator clean on top.

---

## Part 8: Alternative (Stronger) Approach — Top-Down Derivation

Instead of uncovering rules as we move up the stack, we can **start with the CTA contracts and work our way down** from what Team B has already built:

1. **What Platform SDK expects** — Derive from ctx and the four services (platform, governance, reasoning, experience) and from actual intent-service usage. That is the **contract at the top**.
2. **What Experience, Agentic, Smart City, and Runtime need to do** to enable that.
3. **What protocols** they need (so we only consume via protocols).
4. **What abstractions** those protocols need.
5. **What adapters** those abstractions need.
6. **What infrastructure** is behind that.
7. **Genesis gaps** — Is anything missing in our Genesis protocol?

Then **build back up** from the bottom. That gives a **layered pattern in one place** that defines everything we need to build. It is a larger undertaking (Smart City alone has 9 roles, each with SDKs and primitives), but done with rigor it yields the right answer.

See **[CTA_TOP_DOWN_DERIVATION.md](CTA_TOP_DOWN_DERIVATION.md)** for the living document: Layer 1 = What Platform SDK expects (seeded from code); Layer 2–7 = What must enable it, protocols, abstractions, adapters, infrastructure, Genesis gaps. Use it to fill PUBLIC_WORKS_CONTRACT and to drive the audit and fix pass.
