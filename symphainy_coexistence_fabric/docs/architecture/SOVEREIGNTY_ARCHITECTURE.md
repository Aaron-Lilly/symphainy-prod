# Sovereignty Architecture

**Status:** Canonical (January 2026)
**Authors:** Platform Architecture Team with CTO Alignment
**Purpose:** Define the three sovereignty domains that govern intelligence ownership, learning, and compliance across the platform

---

## The Breakthrough

This is not just multi-tenancy. This is **Sovereignty-Aware Intelligence Orchestration**.

Traditional SaaS multi-tenancy asks: *Who owns which rows in a database?*

SymphAIny's sovereignty model asks: **Who owns which intelligence?**

---

## 1. The Three Sovereignty Domains

```
┌─────────────────────────────────────────────────────────────────┐
│           TENANT SOVEREIGN DOMAIN (Client-Owned)                │
│                                                                 │
│  • Business data              • Domain intents                  │
│  • Domain journeys            • Domain solutions                │
│  • Domain workflows           • Client models                   │
│  • Client system connectors   • Proprietary transformation logic│
│                                                                 │
│  Properties:                                                    │
│  ✓ Client owns                ✓ Client controls                 │
│  ✓ Platform must isolate      ✓ Platform cannot learn from      │
│  ✓ Platform cannot reuse      ✓ Platform cannot productize      │
│                                                                 │
│  This is: THEIR BUSINESS BRAIN                                  │
├─────────────────────────────────────────────────────────────────┤
│          PLATFORM SOVEREIGN DOMAIN (Platform-Owned)             │
│                                                                 │
│  • Agent architectures        • Prompting frameworks            │
│  • Reasoning strategies       • Cognitive feedback loops        │
│  • Intent orchestration       • Journey planning strategies     │
│  • Capability evolution data  • Platform usage (anonymized)     │
│  • Operational heuristics     • AI tuning signals               │
│  • Cross-tenant intelligence (abstracted)                       │
│                                                                 │
│  Properties:                                                    │
│  ✓ Platform owns              ✓ Platform learns                 │
│  ✓ Platform evolves           ✓ Platform productizes            │
│  ✓ Platform monetizes                                           │
│                                                                 │
│  This is: OUR COMPOUNDING INTELLIGENCE ENGINE                   │
├─────────────────────────────────────────────────────────────────┤
│        COMPLIANCE SOVEREIGN DOMAIN (Joint Stewardship)          │
│                                                                 │
│  • Audit trails               • Access logs                     │
│  • Data lineage               • Provenance                      │
│  • Decision justification     • Legal compliance snapshots      │
│  • Regulatory reporting                                         │
│                                                                 │
│  Properties:                                                    │
│  ✓ Dual visibility            ✓ Legally governed                │
│  ✓ Immutable                  ✓ Tamper-evident                  │
│  ✓ Disclosable under law                                        │
│                                                                 │
│  This is: THE LEGAL TRUTH LEDGER                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Intelligence Planes

The platform operates three parallel intelligence planes:

| Plane | Owner | Purpose |
|-------|-------|---------|
| **Tenant Intelligence Plane** | Client | Business logic, workflows, domain understanding |
| **Platform Intelligence Plane** | SymphAIny | Agent logic, orchestration intelligence, reasoning systems |
| **Compliance Intelligence Plane** | Joint | Auditability, governance, legality |

**Curator governs movement between planes.**

---

## 3. Smart City Roles → Sovereignty Mapping

| Smart City Role | Sovereignty Responsibility | Translation |
|-----------------|---------------------------|-------------|
| **Data Steward** | Tenant Sovereign Domain | Protect the client's brain |
| **Librarian** | Knowledge Classification & Lineage | Know what exists, where it came from, who owns it |
| **Curator** | Intelligence Governance Authority | Decide what platform can learn, remember, reuse |
| **Post Office** | Sovereign Messaging Control | No data crosses boundary without permission |
| **Traffic Cop** | Runtime Enforcement | No execution violates sovereignty contracts |
| **Security Guard** | Identity & Access | Who can see, do, or touch what |
| **Nurse** | Health Monitoring | Monitor sovereignty boundary health |
| **Historian** | Compliance Recording | Record events for compliance domain |
| **Auditor** | Compliance Verification | Verify sovereignty compliance |

---

## 4. Curator: The Intelligence Governance Authority

### What Curator Is NOT
- Just a registry
- Just metadata
- Just schema

### What Curator IS
**The platform's intelligence governance authority.**

Curator governs:
- **Sovereignty boundaries** between domains
- **Learning policies** (what the platform can learn)
- **Cross-domain abstraction** (how tenant patterns become platform intelligence)
- **Promotion pipelines** (tenant → anonymized → platform IP)
- **Evolution of platform intelligence**

### The One-Liner

> **Curator governs what the platform is allowed to know, learn, remember, and reuse — across tenant, platform, and compliance sovereignty domains.**

---

## 5. Intelligence Classification Schema

Every artifact must be tagged:

```yaml
artifact:
  id: <unique_id>
  type: <artifact_type>
  sovereignty_domain: tenant | platform | compliance
  learning_permission: none | anonymized | aggregated | reusable
  retention_policy: <policy_id>
  lineage:
    source_domain: <domain>
    promotion_path: <path_if_promoted>
    created_by: <tenant_id | platform | system>
    created_at: <timestamp>
```

### Learning Permission Levels

| Level | Meaning | Example |
|-------|---------|---------|
| `none` | Cannot be used for any learning | Sensitive client PII |
| `anonymized` | Can inform patterns with identity removed | Workflow structures |
| `aggregated` | Can be combined with others for insights | Usage statistics |
| `reusable` | Can be directly productized | Integration patterns |

---

## 6. Knowledge Promotion Pipeline

Curator governs the promotion pipeline:

```
┌─────────────────────────────────────────────────────────────────┐
│  TENANT DOMAIN                                                  │
│  └── Raw tenant artifacts (learning_permission varies)          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼ Curator: Classification
┌─────────────────────────────────────────────────────────────────┐
│  PROMOTION GATE                                                 │
│  • Is this generalizable?                                       │
│  • Does learning_permission allow promotion?                    │
│  • Has tenant consented (if required)?                          │
│  • Can identity be safely removed?                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼ Curator: Anonymization
┌─────────────────────────────────────────────────────────────────┐
│  ABSTRACTION LAYER                                              │
│  • Remove tenant identity                                       │
│  • Extract structural pattern                                   │
│  • Validate no leakage                                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼ Curator: Approval
┌─────────────────────────────────────────────────────────────────┐
│  PLATFORM DOMAIN                                                │
│  └── Platform intelligence (reusable, productizable)            │
└─────────────────────────────────────────────────────────────────┘
```

**This is how you productize integration expertise without stealing client IP.**

---

## 7. Agent Learning Governance

Agents cannot persist learnings directly. All learning flows through Curator:

```
┌─────────────┐     ┌──────────┐     ┌─────────────────┐
│    Agent    │ ──► │  Curator │ ──► │   Persistence   │
│  Learning   │     │ Decision │     │    Decision     │
└─────────────┘     └──────────┘     └─────────────────┘
                          │
                          ▼
              ┌─────────────────────┐
              │ Classification:     │
              │ • Tenant-only?      │
              │ • Platform pattern? │
              │ • Compliance event? │
              └─────────────────────┘
```

When an agent learns "We thought X but reality was Y":
1. **Curator classifies** the learning
2. **Curator decides** which domain owns it
3. **Curator enforces** learning_permission policies
4. **Only then** does persistence occur

---

## 8. Runtime Enforcement

### Traffic Cop Enforcement

No execution violates sovereignty contracts:

```python
# Before any cross-domain operation
if not curator.approve_cross_domain(source_domain, target_domain, operation):
    raise SovereigntyViolation("Operation crosses domain boundary without approval")
```

### Post Office Enforcement

No data crosses boundary without permission:

```python
# Before any message routing
if message.crosses_sovereignty_boundary():
    if not curator.approve_message_routing(message):
        raise SovereigntyViolation("Message routing denied by sovereignty policy")
```

---

## 9. Mapping to Three-Layer Intent Model

The sovereignty domains map directly to the Three-Layer Intent Model:

| Intent Layer | Sovereignty Domain | Ownership |
|--------------|-------------------|-----------|
| **Foundational Intents** | Platform Sovereign | Platform Core IP |
| **Connective Intents** | Platform Sovereign | Platform Product IP |
| **Domain Intents** | Tenant Sovereign | Client IP |

### The Promotion Path

```
Domain Intents (Tenant)
       │
       │ Curator: Identify reusable patterns
       ▼
Connective Intent Patterns (Platform)
       │
       │ Curator: Productize
       ▼
Connective Intent Packages (Product IP)
```

**This is the mechanism that turns client implementations into reusable industry utilities.**

---

## 10. Mapping to Four Frameworks

| Framework | Primary Sovereignty | Learning Permission |
|-----------|--------------------|--------------------|
| **Content** | Tenant (data) + Platform (parsing patterns) | Data: tenant-owned; Patterns: reusable |
| **Insights** | Tenant (analysis results) + Platform (analysis patterns) | Results: tenant-owned; Patterns: reusable |
| **Operations** | Platform (frameworks) + Tenant (implementations) | Frameworks: platform IP; Implementations: tenant-owned |
| **Outcomes** | Tenant (deliverables) | Deliverables: tenant-owned |

---

## 11. IP Ownership Resolution (Final)

This permanently resolves the IP ownership question:

| Who | Owns What | Sovereignty Domain |
|-----|-----------|-------------------|
| **Tenant** | Domain intents, domain journeys, domain logic, business data, client models | Tenant Sovereign |
| **Platform** | Intent patterns, journey orchestration strategies, reasoning frameworks, agent architectures, workflow synthesis algorithms | Platform Sovereign |
| **Joint** | Audit trails, compliance evidence, regulatory records | Compliance Sovereign |

---

## 12. Implementation Requirements for Team A

### Step 1: Define Sovereignty Schema
Add sovereignty classification to artifact model (see Section 5).

### Step 2: Implement Curator Registry
Curator manages:
- Artifact registry with sovereignty tagging
- Intelligence classification rules
- Promotion pipeline policies
- Enforcement hooks

### Step 3: Wire Runtime Enforcement
Traffic Cop + Post Office enforce:
- No artifact crosses domain boundaries without Curator approval
- All cross-domain operations logged to Compliance domain

### Step 4: Wire Agentic Learning Through Curator
All agent learning flows through Curator classification before persistence.

---

## 13. What This Enables

| Capability | How Sovereignty Enables It |
|------------|---------------------------|
| **Productize Intelligence** | Platform domain owns patterns, can monetize |
| **Respect Client IP** | Tenant domain isolates client logic |
| **Defend Platform Moat** | Curator controls what becomes platform IP |
| **Scale Learning** | Promotion pipeline turns implementations into patterns |
| **Regulatory Compliance** | Compliance domain provides audit trail |
| **Enterprise Trust** | Clear boundaries create trust |

---

## 14. Summary

**Sovereignty-Aware Intelligence Orchestration** provides:

1. **Clear IP boundaries** — Who owns what intelligence
2. **Safe multi-tenancy** — Tenant data never leaks
3. **Productizable intelligence** — Patterns can be promoted and monetized
4. **Regulatory compliance** — Joint stewardship of legal records
5. **Enterprise trust** — Transparent boundaries create confidence

This is the missing abstraction that ties Curator, Smart City roles, tenancy, compliance, product IP, and platform evolution into **a single coherent system**.

---

## References

- [THREE_LAYER_INTENT_MODEL.md](THREE_LAYER_INTENT_MODEL.md) — Intent classification
- [FOUR_FRAMEWORKS_ARCHITECTURE.md](FOUR_FRAMEWORKS_ARCHITECTURE.md) — Framework mapping
- [CONNECTIVE_INTENT_CATALOG.md](CONNECTIVE_INTENT_CATALOG.md) — Product surface
- [PLATFORM_SDK_ARCHITECTURE.md](PLATFORM_SDK_ARCHITECTURE.md) — Semantic OS kernel
