# Platform Version Evaluation: Three Folders, One Source of Truth

**Date:** 2026-01-29  
**Context:** Possible version-control confusion from multiple Cursor web agents merging to main. Need to confirm which folder is source of truth and whether anything must be "brought forward" from the others.

**Conclusion:** **symphainy_coexistence_fabric/symphainy_platform** is the only real platform directory and is the correct source of truth. Nothing needs to be brought forward from the other folders. Details below.

---

## 1. What the Three Paths Actually Are

| Path | What it is | Python file count |
|------|------------|--------------------|
| **symphainy_source_code/symphainy_coexistence_fabric/symphainy_platform** | **Real directory.** The v2 "Coexistence Fabric" platform (solution→journey→intent). **SOURCE OF TRUTH.** | 437 |
| **symphainy_source_code/symphainy_platform** | **Symlink** → `symphainy_coexistence_fabric/symphainy_platform`. Same content as above. Not a separate copy. | (same) |
| **symphainy_source_code/symphainy_platform_old** | **Real directory.** Pre-refactor "Clean Rebuild v1" (realm-centric, orchestrators, no bases). **Reference only.** | 383 |

So there are only **two** actual codebases: **coexistence_fabric/symphainy_platform** (source of truth) and **symphainy_platform_old** (old architecture).

---

## 2. Why This Isn’t Partial Implementations in Each

- **symphainy_platform** (the symlink): It is not a separate implementation. `ls -la` shows `symphainy_platform -> symphainy_coexistence_fabric/symphainy_platform`. Any change under one is the other. No merge or “bring forward” between them.
- **symphainy_platform_old**: This is the **pre–Coexistence Fabric** layout:
  - **No** `bases/` (no BaseOrchestrator, BaseIntentService).
  - **Realms** are realm-centric: `content_realm.py`, `insights_realm.py`, `*_orchestrator.py`, `orchestrators/handlers/`, `enabling_services/` inside each realm, realm-level `mcp_server/`.
  - **Foundations** are flatter (no `foundations/libraries/` with chunking, coexistence, embeddings, etc.).
- **coexistence_fabric/symphainy_platform**: This is the **v2** layout:
  - **Has** `bases/` (intent_service_base, orchestrator_base).
  - **Realms** are intent-service–centric: `realms/*/intent_services/` (no `content_realm.py`, no realm orchestrators/handlers).
  - **Foundations** include `foundations/libraries/` (chunking, coexistence, embeddings, export, etc.) and `foundations/curator/` (with soa_api_registry, etc.).
  - **Solutions** use the solution→journey→intent pattern and SOLUTION_PATTERN.md.

So we have one **old** architecture (_old) and one **new** architecture (fabric). The difference is intentional refactor, not “partial implementations spread across folders.”

---

## 3. File Comparison: Do We Need to Bring Anything Forward?

### 3.1 Files only in _old (64 files)

These are **old-structure** files that the v2 design deliberately replaced:

- **Realms:** `content_realm.py`, `insights_realm.py`, `operations_realm.py`, `outcomes_realm.py`, realm `orchestrators/` (e.g. `content_orchestrator.py`), `orchestrators/handlers/`, `enabling_services/` inside realms, realm-level `mcp_server/` (e.g. `content_mcp_server.py`).
- **Agents:** Old realm-level agents (e.g. under `realms/insights/agents/`).

In v2, the equivalent behavior lives in:

- **Realms:** `realms/*/intent_services/` (no realm orchestrators).
- **Foundations:** `foundations/libraries/` (chunking, coexistence, embeddings, etc.) instead of realm `enabling_services/`.
- **Solutions:** Solution classes and journeys in `solutions/`.
- **Agentic:** Agents under `civic_systems/agentic/`.

**Recommendation:** Do **not** bring these 64 _old files “forward” into coexistence_fabric. They belong to the old architecture. If a specific capability is missing in v2, re-implement it in the v2 structure (intent services, solutions, foundations/libraries) rather than copying old realm/orchestrator code.

### 3.2 Files only in coexistence_fabric (118 files)

These are the **new** pieces: bases, foundations/libraries, realm intent_services, and extra agentic agents. They are the intended v2 implementation. No action needed except to keep treating fabric as source of truth.

### 3.3 Files that exist in both (shared paths)

For a few critical files we compared:

| File | Result |
|------|--------|
| **runtime/runtime_services.py** | **Identical** (diff empty). |
| **config/env_contract.py** | **Identical** (diff empty). |
| **solutions/solution_initializer.py** | **Fabric is more complete:** fabric builds `SolutionContext` and passes `solution_context` into `Solution`; _old does not. Fabric = intended version. |
| **runtime/service_factory.py** | **Fabric is the new architecture:** fabric registers **intent services** per realm; _old registers **realm orchestrators** (ContentOrchestrator, InsightsOrchestrator, etc.). Fabric = intended version. |

So: no critical logic lives only in _old. Where they differ, fabric is either identical or the evolved, intended version.

---

## 4. Recommendations

1. **Treat symphainy_coexistence_fabric/symphainy_platform as the single source of truth.** All edits and merges should happen there (or via the symlink, which points to it).
2. **Do not bring forward** any of the 64 “only in _old” files into fabric. They are old-structure; v2 uses intent_services, solutions, and foundations/libraries instead.
3. **Document the symlink** so the team knows:
   - `symphainy_source_code/symphainy_platform` is an alias for `symphainy_coexistence_fabric/symphainy_platform`.
   - Imports like `symphainy_platform.runtime.*` resolve to the fabric copy when the repo root (or coexistence_fabric) is on the path.
4. **symphainy_platform_old:** Keep as **reference only** (or archive). Do not merge from it into fabric. If something is missing in v2, re-implement in v2 structure rather than copying from _old.
5. **CI / run scripts:** Prefer running from **symphainy_coexistence_fabric** (or repo root with path set so `symphainy_platform` resolves via the symlink) so there is no ambiguity about which platform code is used.

---

## 5. Summary

- **symphainy_platform** = symlink → **coexistence_fabric/symphainy_platform** (one implementation).
- **symphainy_platform_old** = old architecture (realm-centric, orchestrators); superseded by fabric.
- **Nothing from _old needs to be “brought forward”** into coexistence_fabric; fabric is the intended final version and is more complete where they differ.
- **Source of truth:** `symphainy_coexistence_fabric/symphainy_platform` (and thus the symlink). No version-control “merge” required between the three paths; only fabric is the live codebase.
