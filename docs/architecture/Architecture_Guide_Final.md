What follows is the **3-part guide** designed to hand to a new senior engineer and say: *“If you understand this, you understand the platform.”*

---

# PART I — ARCHITECTURE GUIDE (THE NORTH STAR)

## 1. What This Platform *Is* (and Is Not)

**SymphAIny is not:**

* A CRUD application
* A traditional data platform
* A workflow engine
* An agent framework

**SymphAIny *is*:**

> A **policy-governed execution fabric** for turning messy, opt-in client data into durable meaning, outcomes, and platform DNA — without assuming automation, permanence, or completeness.

Everything else flows from this.

---

## 2. The Core Architectural Law

> **Only Realms touch data.
> Everything else governs, observes, or intends.**

This is the law that replaces CRUD.

Violations of this law *will* reintroduce hidden coupling, security holes, and irreversibility.

---

## 3. The Artifact Lifecycle (Canonical)

Everything begins as an **Artifact**.

Artifacts are not files.
Artifacts are **units of intent-bound work**.

### Artifact Lifecycle States

1. **Ephemeral Artifact**

   * Client opt-in
   * Exists “in the moment”
   * May or may not include bytes
   * Governed by TTL + policy

2. **Working Material**

   * Parsed content
   * Deterministic embeddings
   * Validation outputs
   * Replayable, reproducible

3. **Record of Fact**

   * Explicitly promoted
   * Policy-approved
   * Permanent
   * May reference content without storing it

4. **Purpose-Bound Outcome**

   * Reports
   * SOPs
   * Blueprints
   * Roadmaps
   * Proposals
   * Exists *for a reason*, not forever

5. **Platform DNA**

   * Intents
   * Journeys
   * Realms
   * Capabilities
   * Solutions
   * Explicitly curated and promoted

> **Promotion is always explicit.
> Nothing becomes permanent by accident.**

---

## 4. Planes vs Realms vs Services

### Planes (Horizontal)

Planes are **governance and truth layers**.

* **Artifact Plane**

  * Lifecycle
  * Lineage
  * Versioning
  * Dependencies
  * State machine

* **Policy Plane (Smart City)**

  * Materialization rules
  * Access control
  * TTL
  * Promotion rights
  * Tenant governance

* **Runtime Plane**

  * Records reality
  * Execution context
  * Observability
  * Telemetry hooks

Planes never touch data.

---

### Realms (Vertical)

Realms are **bounded execution environments**.

* **Content Realm**

  * File ingestion
  * Parsing
  * Deterministic embeddings
  * Content abstractions

* **Insight Realm**

  * Validation
  * Analysis
  * Interpretation
  * Transformation

* **Journey Realm**

  * Orchestration
  * SOP execution
  * Human-in-the-loop flows

* **Solution Realm**

  * Deployment
  * Monitoring
  * Long-lived outcomes

Realms may touch data — **only through abstractions**.

---

### Services

Services are **implementation details** behind realm boundaries.

Examples:

* FileManagementAbstraction
* FileStorageAbstraction
* ParserService
* EmbeddingService
* ValidationService

Agents never call services directly.

---

## 5. Storage & Compute Canon

| Abstraction                     | Technology (Adapter)       | Why                    |
| ------------------------------- | -------------------------- | ---------------------- |
| Lineage, meaning, relationships | **ArangoDB**               | Graph-native, semantic |
| Deterministic compute           | **DuckDB**                 | Embedded, replayable   |
| Vector semantics                | **ArangoDB (or external)** | Meaningful similarity  |
| Ephemeral coordination          | Redis                      | Fast, volatile         |
| Blob storage                    | GCS / S3                   | Dumb storage           |
| Search (non-vector)             | Meilisearch                | Fast lexical discovery |

> Storage never defines truth.
> **Policy + lineage do.**

---

## 6. Transactions: Your ACID Replacement

You use **Policy-Governed Sagas**.

Guarantees:

* Intent-bounded execution
* Explicit promotion
* Compensatable failure
* Durable lineage

Failures are outcomes.
Incomplete work is allowed.
Humans are first-class participants.

---

# PART II — HOW TO BUILD ON THE PLATFORM (DEVELOPER GUIDE)

## 1. How You Should Think Before Writing Code

Before building anything, answer:

1. What artifact does this create or transform?
2. What realm owns this action?
3. What policy governs promotion?
4. What lineage must be preserved?
5. Can this fail safely?

If you can’t answer these, stop.

---

## 2. How Agents Work (Canonical)

Agents:

* **Express intent**
* **Reason**
* **Select tools**
* **Request realm actions**

Agents do **not**:

* Fetch files
* Read storage
* Bypass policy
* Manage lifecycle

### Agent Configuration Layers

1. **Journey Context (User-Set)**

   * What the agent should help with
   * Business domain
   * Desired capabilities

2. **Tenant Defaults (Admin)**

   * Allowed realms
   * Tool budgets
   * Cost limits
   * Safety rails

3. **Developer Canon**

   * System instructions
   * Tool contracts
   * Promotion rules
   * Failure semantics

Prompt engineering lives **below** these layers, not above them.

---

## 3. The Correct Retrieval Pattern

❌ Agent → File
❌ Agent → Storage
❌ Runtime → Bytes

✅ Agent → Intent
✅ Runtime → Metadata
✅ Policy → Authorization
✅ Realm → Data

If you feel tempted to “just fetch the thing,” you’re breaking the model.

---

## 4. Deterministic vs Semantic Embeddings

### Deterministic

* Produced in Content Realm
* DuckDB-backed
* Reproducible
* Policy-bound
* Used for workflows, SOPs, validation

### Semantic

* Produced in Insight Realm
* Vector-backed
* Interpretive
* Meaning-based
* Used for reasoning, search, similarity

Deterministic embeddings **persist by default**.
Semantic embeddings **persist by intent**.

---

## 5. How to Add a New Capability

1. Define the **intent**
2. Identify the **realm**
3. Define input/output artifacts
4. Define promotion rules
5. Register capability
6. Add curator hooks (if DNA-worthy)

If step 4 is missing, the capability is incomplete.

---

# PART III — PLATFORM VOCABULARY (GLOSSARY)

### Artifact

A unit of intent-bound work with lifecycle, lineage, and policy.

### Working Material

Intermediate outputs used to produce outcomes.

### Record of Fact

An explicitly promoted, permanent truth.

### Purpose-Bound Outcome

A deliverable that exists for a reason, not forever.

### Platform DNA

Curated, reusable intelligence embedded into the platform.

### Realm

A bounded execution environment that may touch data.

### Plane

A horizontal governance or truth layer.

### Smart City

The policy and stewardship system governing materialization.

### Promotion

An explicit act that changes lifecycle state.

### Lineage

The durable history of how something came to be.

### Deterministic

Replayable, reproducible, invariant.

### Semantic

Interpretive, contextual, meaning-driven.

---

## The Epiphany

We didn’t build a modern data platform.

We built something *past* that:

> **A system where data is allowed to be incomplete, human, governed, and still operational.**

Most platforms choose:

* Automation **or** governance
* Flexibility **or** durability
* Agents **or** systems

We chose **intent** as the primitive.

That’s why everything suddenly fits.