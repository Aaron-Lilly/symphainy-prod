You’re **not wrong** — you caught exactly the right thing, and this is an important line to hold.

Short answer up front:

> **The state surface is NOT a master data store and should NOT contain files or large payloads.**
> It stores **execution state, facts, references, and lineage**, not the data itself.

Your correction to the team was **100% correct**.

Let me anchor this cleanly so you can say it with confidence.

---

## What the State Surface *Is*

Think of the **State Surface** as the platform’s **authoritative memory of what happened and what is true right now**, not where the world’s data lives.

It stores:

* **Identifiers**

  * session_id
  * tenant_id
  * workflow_id
  * saga_id
  * mash_id

* **Execution state**

  * current phase
  * step status
  * retries
  * failure markers

* **Facts**

  * “Field X maps to Policy Number with 0.93 confidence”
  * “Data quality check Y failed”
  * “Embedding version Z was used”

* **References**

  * GCS object URIs
  * Supabase row IDs
  * Parser output version hashes

* **Lineage**

  * raw → parsed → quality → interpretation → model
  * which agent / tool produced what

* **Policy-relevant metadata**

  * access scope
  * tenancy
  * retention class
  * audit flags

👉 It is **small, structured, queryable, and durable**.

---

## What the State Surface Is *Not*

It is **explicitly not**:

* ❌ A file store
* ❌ A blob store
* ❌ A document database
* ❌ A data lake
* ❌ A master data management (MDM) system

If someone says “we’ll just store the file in state,” that’s a design bug, not a convenience.

---

## Where Files Actually Live (Correct Model)

| Thing                        | Where it lives    |
| ---------------------------- | ----------------- |
| Raw uploads                  | GCS               |
| Parsed artifacts (JSON)      | GCS               |
| Client-visible metadata      | Supabase          |
| Large intermediate results   | Object storage    |
| Execution facts & references | **State Surface** |

The **state surface points to data**, it does not *contain* it.

---

## Why This Matters (Practically)

You avoided three major problems by correcting this:

### 1. Performance & Cost

State surfaces need to be:

* fast
* transactional
* frequently updated

Files break all three.

---

### 2. Determinism & Auditability

Execution state must be:

* comparable
* replayable
* inspectable

Blobs inside state make replay and diffing impossible.

---

### 3. Platform Longevity

If state becomes a data lake:

* WAL explodes
* Saga recovery becomes unreliable
* Multi-tenancy isolation breaks
* Every future feature gets harder

This is exactly how platforms become brittle.

---

## Correct Mental Model (You can share this verbatim)

> **State Surface = “What do we know, what’s happening, and where is everything?”**
> **Storage = “Where the actual data lives.”**

Or even simpler:

> *State contains facts and pointers, not payloads.*

---

## Is State a “Master Database”?

No — but it *is* the **system of record for execution truth**.

A helpful distinction:

* **MDM** answers: “What is the canonical customer record?”
* **State Surface** answers: “What is true about this execution right now?”

Those are very different jobs.

---

## One-Line Guidance for the Team

If you want a crisp rule to give them:

> “If it’s bigger than a few KB or could be re-derived, it does not belong in state — store a reference instead.”
