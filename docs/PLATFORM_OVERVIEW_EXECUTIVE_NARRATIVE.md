# Symphainy Coexistence Fabric - Executive Narrative

**Last Updated:** January 2026  
**Version:** 2.0  
**Status:** Executive Overview

---

## One-Page Architecture Narrative
"How the Symphainy Coexistence Fabric Works"

This narrative is designed to be read while looking at a single architecture diagram, providing an executive-friendly explanation of how the platform works.

---

## Symphainy Coexistence Fabric
**Where work gets done**

Harnessing AI to remove friction between people, processes, and systems.

---

## The Core Idea

Enterprises don't fail because they lack systems.

They fail because work has to cross boundaries — between people, legacy platforms, modern tools, and incomplete automation.

**The Symphainy Coexistence Fabric exists to govern and coordinate that boundary-crossing** so work can move without forcing replacement, rewrites, or premature automation.

---

## The Architecture, End-to-End

**Work enters the fabric as intent.**

An intent can come from:
- **a human** (via UI, chat, upload, approval)
- **an agent** (reasoned suggestion)
- **or an external system** (API, batch, event)

---

## 1. Experience Systems — Where intent is expressed

Experience systems capture **what someone is trying to accomplish**, not how to do it.

**Capabilities:**
- UI, APIs, chat, streaming, external integrations
- Humans are first-class actors
- No execution, no policy, no orchestration

**Output:** "Here is the work we want to happen."

---

## 2. Civic Systems — How work is coordinated safely

Civic Systems are the **behavioral backbone of the platform**.

They define:
- how work is composed
- how governance is applied
- how humans, agents, and systems participate together

**Key Civic Systems:**

1. **Platform SDK** – defines end-to-end flows and compositions (Solution Builder, Realm SDK, Civic Composition)
2. **Smart City** – applies governance, policy, coordination patterns (includes Curator role for capability registry)
3. **Agentic System** – enables reasoning, collaboration, and assistance
4. **Experience** – translates interactions into intents, streams execution updates

**Note:** Experience is both Layer 1 (where intent is expressed) and a Civic System (how intent expression works). Curator is a Smart City Role, not a separate Civic System.

**This is where:**
- humans are routed into flows
- agents collaborate without executing
- legacy and modern systems are coordinated without being rewritten

**Output:** "This is the governed plan for how the work will proceed."

---

## 3. Runtime Execution Engine — Where work actually happens

Runtime is the **single execution authority**.

It:
- validates execution contracts
- applies final governance checks
- records state, lineage, and outcomes
- executes both automated steps and human handoffs

**Runtime does not decide what to do** — it ensures that whatever happens is auditable, replayable, and safe.

**Output:** "This work happened — here is the evidence."

---

## 4. Realm Services — Where domain work is performed

Realm Services do the actual domain-specific work:

- **Content** – File management, parsing, data extraction
- **Insights** – Data quality, interpretation, analysis
- **Journey** – Workflow creation, SOP generation, process optimization
- **Outcomes** – Solution synthesis, roadmap generation, POC creation

**They:**
- execute deterministically
- rely on Civic Systems for coordination
- never bypass governance or Runtime

---

## The Result

The platform does not eliminate humans or legacy systems.

**It integrates them into a governed, observable system of work.**

Work moves forward even when:
- automation is incomplete
- humans must intervene
- systems cannot be modernized yet

**That is the Coexistence Fabric.**

---

## How This Relates to Technical Architecture

This narrative describes the **same architecture** as the technical documentation, but from a **business perspective**:

- **Experience Systems** = Experience Plane (Civic System)
- **Civic Systems** = Smart City, Experience, Agentic, Platform SDK
- **Runtime Execution Engine** = Runtime Plane
- **Realm Services** = Realm Plane (Domain Services)

The technical architecture document ([Architecture Guide](architecture/north_star.md)) provides detailed technical specifications. This narrative provides the executive-friendly explanation.

---

## Key Differentiators

1. **Coexistence, Not Replacement** – Works with existing systems
2. **Governed, Not Autonomous** – Every operation is tracked and auditable
3. **Intent-Based, Not Command-Based** – Declares what should happen, not how
4. **Human-First, Not Automation-First** – Humans are first-class actors

---

**For Technical Details:** See [Architecture Guide](architecture/north_star.md)  
**For Capabilities:** See [Capabilities Index](capabilities/00_CAPABILITIES_INDEX.md)  
**For Platform Overview:** See [Platform Overview](PLATFORM_OVERVIEW.md)
