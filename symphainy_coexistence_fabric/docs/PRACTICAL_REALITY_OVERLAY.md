# Practical Reality Overlay

**Status:** Canonical Reference (January 2026)  
**Purpose:** Keep all teams aligned on what we're actually building and why, without losing the thread or our minds.  
**Audience:** C-Suite, Sales, Product, Engineering Teams A/B/C

---

## The One-Sentence Reality

**We are building Platform OS v1.0 that runs four demo tenants (Base, AAR, PSO, VLP) to prove the architecture while delivering real value.**

---

## Part 1: What the C-Suite Needs to Know

### The MVP = Platform OS v1.0

The MVP is not "a bunch of features." It is the **first version of a semantic operating system** that proves:

| Proof Point | What It Demonstrates |
|-------------|---------------------|
| **Data Mash** | Reality → Semantics → Action works |
| **Journey Builder** | Humans can "program" in intent language |
| **Secure Login** | Smart City governance is real |
| **Control Tower** | We can see inside the kernel |
| **Coexistence Agents** | Human-AI semantic bridge works |

### The Four Demo Tenants

Each demo is **the same platform** with different configurations:

| Tenant | Industry | Primary Showcase |
|--------|----------|-----------------|
| **Base** | Internal | All features (testing) |
| **AAR** | Defense/Military | After Action Report analysis |
| **PSO** | Energy/Utilities | Permit & Service Order processing |
| **VLP** | Insurance | Variable Life Policy migration |

**Key Message for Sales:** *"Watch me switch tenants. Same platform, completely different application. This is exactly how YOUR tenant would work."*

### What Users Will Actually See

1. **Login** → Select demo environment → Enter platform
2. **Content Pillar** → Upload files → AI parses and understands
3. **Insights Pillar** → See quality, patterns, relationships
4. **Operations Pillar** → Generate SOPs, analyze workflows
5. **Outcomes Pillar** → Get roadmaps, POC proposals, blueprints
6. **Chat** → Talk to AI agents that actually understand context

---

## Part 2: The Three Teams and What They Own

### Team A: Takeoff (Infrastructure)

**Mission:** Build everything UP TO the Platform SDK boundary.

| Deliverable | Status | Notes |
|-------------|--------|-------|
| Public Works (protocols) | ✅ Done | Protocol layer complete |
| Genesis Protocol (boot) | ✅ Done | Platform can start |
| Adapter implementations | 🟡 Partial | Some adapters need wiring |
| Civic System refactor | 🟡 In Progress | Curator, Smart City cleanup |
| Experience SDK backend | ⚠️ Critical | Must verify endpoints exist |
| WebSocket gateway | ⚠️ Critical | For chat and execution streaming |
| Runtime → Platform SDK wiring | ⚠️ Critical | The final intercept |

**Team A's North Star:** When Team B's capability services receive `ctx`, all the protocols and adapters must work.

**Practical Reality Check for Team A:**
- [ ] `/api/intent/submit` routes to Team B's capability services
- [ ] `/api/session/*` endpoints exist and work
- [ ] `/api/execution/{id}/status` returns real status
- [ ] WebSocket `/ws/chat` and `/ws/execution` exist
- [ ] Tenant isolation enforced in StateSurface and ArtifactRegistry

---

### Team B: Landing (Platform SDK + Capabilities)

**Mission:** Build the Platform SDK and everything FORWARD from it.

| Deliverable | Status | Notes |
|-------------|--------|-------|
| Platform SDK (`ctx`) | ✅ Done | 4 services + factory + base class |
| PlatformIntentService | ✅ Done | New intent service pattern |
| Content services (10) | ✅ Done | Ingest, parse, embeddings, etc. |
| Security services (7) | ✅ Done | Auth, sessions, tokens |
| Coexistence services (7) | ✅ Done | Guide agent, liaisons |
| Insights services (7) | ✅ Done | Quality, analysis, lineage |
| Operations services (6) | ✅ Done | SOP, workflows, coexistence |
| Outcomes services (6) | ✅ Done | Roadmap, POC, blueprint |
| Control Tower services (9) | ✅ Done | Health, stats, docs |
| AI agents (real LLM) | ✅ Done | 15+ agents with LLM reasoning |
| Architecture docs | ✅ Done | Three-Layer Model, Sovereignty, etc. |

**Team B's North Star:** When frontend calls `invoke_intent("ingest_file")`, our service executes with full AI capabilities.

**Practical Reality Check for Team B:**
- [x] 52 capability services built and registered
- [x] All services use `PlatformIntentService` pattern
- [x] AI agents use real LLM (not keyword matching)
- [x] Services are registered in `service_factory.py`
- [ ] Verify services execute when Runtime routes to them

---

### Team C: Frontend (Multi-Tenant UI)

**Mission:** Transform single-tenant UI into multi-tenant demo platform.

| Deliverable | Status | Notes |
|-------------|--------|-------|
| Tenant config system | ❌ Not Started | 4 tenant JSON configs |
| TenantContext provider | ❌ Not Started | React context for tenant |
| Login tenant selector | ❌ Not Started | Dropdown on login page |
| Conditional demo sections | ❌ Not Started | AAR/PSO/VLP visibility |
| Tenant-aware welcome | ❌ Not Started | Different messages per tenant |
| Control Tower tenant filter | ❌ Not Started | Show current tenant |
| VLPExtractionSection | ❌ Not Started | New component for VLP |

**Team C's North Star:** Each demo tenant sees only their relevant features; demos prove the platform.

**Practical Reality Check for Team C:**
- [ ] Login page has tenant selector
- [ ] AAR tenant sees only AAR features
- [ ] PSO tenant sees only PSO features
- [ ] VLP tenant sees only VLP features
- [ ] Base tenant sees everything (for internal testing)

**Specification:** `docs/frontend/FRONTEND_MULTI_TENANT_SPEC.md`

---

## Part 3: How It All Fits Together

### The Complete Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER EXPERIENCE                                    │
│                                                                             │
│  1. User visits login page                                                  │
│  2. User selects demo tenant (AAR/PSO/VLP/Base)    ← TEAM C                │
│  3. User logs in                                                            │
│  4. Platform loads tenant-specific UI              ← TEAM C                │
│  5. User uploads a file                                                     │
│  6. Frontend calls Experience SDK                  ← TEAM C (existing)     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        EXPERIENCE SDK LAYER                                  │
│                                                                             │
│  ExperiencePlaneClient.submitIntent({              ← TEAM C (existing)     │
│    intent_type: "ingest_file",                                              │
│    tenant_id: "vlp",                                                        │
│    session_id: "...",                                                       │
│    parameters: { file_data, metadata }                                      │
│  })                                                                         │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           BACKEND API                                        │
│                                                                             │
│  POST /api/intent/submit                           ← TEAM A                │
│  ├── Validates session                                                      │
│  ├── Creates execution record                                               │
│  └── Routes to Runtime                                                      │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                             RUNTIME                                          │
│                                                                             │
│  ExecutionLifecycleManager.execute(intent)         ← TEAM A                │
│  ├── Looks up handler for "ingest_file"                                     │
│  ├── Detects uses_platform_context = True                                   │
│  ├── Creates PlatformContext (ctx) via factory                              │
│  └── Calls handler(ctx)                                                     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      PLATFORM SDK (ctx)                                      │
│                                                                             │
│  PlatformContext                                   ← TEAM B (built)        │
│  ├── ctx.platform    → Parse, ingest, visualize                             │
│  ├── ctx.governance  → Smart City SDKs                                      │
│  ├── ctx.reasoning   → LLM, AI agents                                       │
│  ├── ctx.state_surface → State (Runtime)                                    │
│  ├── ctx.artifacts   → Artifact registry (Runtime)                          │
│  └── ctx.wal         → Write-ahead log (Runtime)                            │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     CAPABILITY SERVICE                                       │
│                                                                             │
│  IngestFileService.execute(ctx)                    ← TEAM B (built)        │
│  ├── Validates parameters via ctx.intent                                    │
│  ├── Ingests file via ctx.platform.ingest_file()                            │
│  ├── Registers artifact via ctx.artifacts                                   │
│  └── Returns { artifacts, events, status }                                  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      PUBLIC WORKS                                            │
│                                                                             │
│  Protocol-typed abstractions                       ← TEAM A (built)        │
│  ├── IngestionAbstraction                                                   │
│  ├── FileStorageAbstraction                                                 │
│  ├── ArtifactStorageAbstraction                                             │
│  └── (etc.)                                                                 │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ADAPTERS                                              │
│                                                                             │
│  Actual infrastructure                             ← TEAM A (built)        │
│  ├── GCS (file storage)                                                     │
│  ├── Supabase (auth, registry)                                              │
│  ├── Redis (state)                                                          │
│  ├── OpenAI (LLM)                                                           │
│  └── (etc.)                                                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

### The Intercept Point

The critical handoff is between Team A and Team B:

```
TEAM A DELIVERS                       TEAM B CONSUMES
───────────────────────────────────────────────────────
PlatformContextFactory receives:      PlatformContext provides:
├── public_works (protocols)    →     ctx.platform (capabilities)
├── state_surface               →     ctx.state_surface
├── wal                         →     ctx.wal
├── artifact_registry           →     ctx.artifacts
├── Smart City SDKs             →     ctx.governance
└── Agentic (LLM, agents)       →     ctx.reasoning
```

**If Team A delivers these correctly, Team B's 52 services light up.**

---

## Part 4: What We Have on the Other Side

### Demo Day Reality

When all teams complete their work:

| Demo | What Happens |
|------|--------------|
| **Login** | Select "VLP Demo" → Platform configures for insurance |
| **Upload** | Drop mainframe file → AI parses COBOL layout |
| **Insights** | See policy fields extracted, quality assessed |
| **Chat** | "What's the migration readiness?" → Real AI response |
| **Operations** | Generate coexistence SOP for legacy/modern operation |
| **Outcomes** | Receive transformation roadmap document |

**Switch to AAR Demo:**
- Same platform, different configuration
- Upload PDF → AI extracts lessons learned
- Chat understands military context
- Generate incident response SOP

**The Proof:** *Same kernel, different applications.*

### What Each Stakeholder Gets

| Stakeholder | They Get | Proof Point |
|-------------|----------|-------------|
| **CEO** | "Platform OS v1.0 is real" | 4 demos on one platform |
| **Sales** | "Switch tenants live in demo" | Tenant selector in login |
| **Product** | "We can add new tenants" | Just add a JSON config |
| **Engineering** | "Clean architecture" | Teams don't step on each other |
| **Investors** | "This is an OS, not an app" | Same code serves all industries |

---

## Part 5: Risk Mitigation

### What Could Go Wrong

| Risk | Mitigation | Owner |
|------|------------|-------|
| Team A's wiring doesn't reach Team B | Daily sync on intercept status | Team A |
| WebSocket gateway doesn't exist | Verify early, escalate if missing | Team A |
| Frontend changes break existing UI | Use feature flags, test each tenant | Team C |
| Demo-specific features leak across tenants | Tenant config checks in every component | Team C |
| Services don't execute when called | Integration test after wiring | Team A + B |

### The Three Questions Every Day

1. **Team A:** "Can Team B's services receive `ctx` yet?"
2. **Team B:** "Are our services registered and callable?"
3. **Team C:** "Does each tenant see only their features?"

---

## Part 6: Definition of Done

### MVP is Done When:

- [ ] **Login works** with tenant selection (Base, AAR, PSO, VLP)
- [ ] **Content pillar** accepts files and parses them per tenant config
- [ ] **Insights pillar** shows tenant-specific analysis (AAR/PSO/VLP sections)
- [ ] **Operations pillar** generates tenant-specific SOPs and workflows
- [ ] **Outcomes pillar** generates roadmaps, POCs, blueprints
- [ ] **Chat works** with real AI responses (not keyword matching)
- [ ] **Control Tower** shows platform health with tenant context
- [ ] **Tenant switching** works live (for sales demos)
- [ ] **No cross-tenant data leakage** (tenant isolation verified)

### The Handoff Chain

```
Team A completes wiring    →    Team B verifies services execute    →    Team C verifies UI works
         │                               │                                      │
         ▼                               ▼                                      ▼
   "ctx is available"           "52 services respond"             "4 tenants render correctly"
```

---

## Part 7: Timeline Reality

### What's Actually Left

| Team | Work Remaining | Estimate |
|------|----------------|----------|
| **Team A** | Verify endpoints, WebSocket, complete wiring | 1-3 days |
| **Team B** | Verify services execute (integration test) | 0.5 day |
| **Team C** | Implement multi-tenant UI | 5-7 days |

### Critical Path

```
Day 1-2: Team A completes wiring
Day 2:   Team B verifies integration
Day 2-7: Team C implements multi-tenant
Day 7+:  Full integration testing
```

**The honest answer:** We're days away from demo-ready once Team A completes the wiring.

---

## Summary: The Practical Reality

### What We're Building

**Platform OS v1.0** — A semantic operating system that:
- Runs multiple demo tenants on one codebase
- Proves the "same kernel, different applications" thesis
- Delivers real AI capabilities (not parlor tricks)
- Shows C-suite exactly what clients will experience

### How We Get There

| Team | Focus | Deliverable |
|------|-------|-------------|
| **Team A** | Wire the intercept | `ctx` reaches services |
| **Team B** | Verify services work | 52 services respond |
| **Team C** | Tenant-aware UI | 4 demos look different |

### What We Don't Do

- ❌ Don't refactor architecture (it's locked)
- ❌ Don't add new features (scope is fixed)
- ❌ Don't mix demo code (tenants stay separate)
- ❌ Don't break existing functionality (additive only)

### The Finish Line

**When a user can:**
1. Login and select "VLP Demo"
2. Upload a mainframe file
3. See AI extract policy fields
4. Chat with an agent that understands insurance
5. Generate a migration roadmap

**...and then switch to "AAR Demo" and have an equally compelling but completely different experience...**

**...we're done.**

---

## Reference Documents

| Document | Purpose | Location |
|----------|---------|----------|
| Intercept Alignment Contract | Team A/B contract | `docs/INTERCEPT_ALIGNMENT_CONTRACT.md` |
| Platform SDK Requirement Spec | Team B build spec | `docs/PLATFORM_SDK_REQUIREMENT_SPEC.md` |
| Frontend Multi-Tenant Spec | Team C build spec | `docs/frontend/FRONTEND_MULTI_TENANT_SPEC.md` |
| Three-Layer Intent Model | Architecture reference | `docs/architecture/THREE_LAYER_INTENT_MODEL.md` |
| Sovereignty Architecture | Data ownership | `docs/architecture/SOVEREIGNTY_ARCHITECTURE.md` |
| Four Frameworks Architecture | Product strategy | `docs/architecture/FOUR_FRAMEWORKS_ARCHITECTURE.md` |
| Unified Testing Strategy | Testing approach | `docs/testing/UNIFIED_TESTING_STRATEGY.md` |
| Comprehensive Architecture Package | Full architecture | `docs/architecture/COMPREHENSIVE_ARCHITECTURE_PACKAGE.md` |

---

*"The demos prove the platform. The platform doesn't exist to run demos."*
