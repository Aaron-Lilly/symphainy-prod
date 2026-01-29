# Merge Strategy: Combining Work from Three Parallel Teams

**Purpose:** Get the best of (1) **Foundation/backend** (config, pre-boot, experience service, auth path), (2) **Team A** (content intent services, Content Orchestrator), and (3) **Team B** (frontend types/tests, CI, SecuritySolution, testing infra) without losing work or creating a long-lived conflict mess.

**Repo:** `Aaron-Lilly/symphainy-prod`  
**Branches analyzed:** All remote branches after `git fetch --all`.

---

## 1. Branch Summary (vs origin/main)

| Branch | Commits ahead | Focus | Key files |
|--------|----------------|--------|------------|
| **main (local)** | Your unpushed work | Foundation: bootstrap, pre-boot, experience_main, docker-compose healthchecks, auth path, config override=False | bootstrap/, experience_main.py, docker-compose.yml, platform_config.py, docs/architecture/*, PATH_TO_WORKING_PLATFORM |
| **origin/cursor/content-intent-services** | 3 | Content Realm intent services + Content Orchestrator; remove backward-compat | service_factory.py, runtime_api.py, execution_lifecycle_manager.py, content/orchestrators, realms/content/intent_services/*, bases/intent_service_base.py |
| **origin/cursor/infrastructure-testing-setup** | 29 | Frontend: remove `any` types (content, insights, adapters, APIService, core); tests; docker-compose.fullstack; PLATFORM_TYPE_ALIGNMENT_PLAN | symphainy-frontend/* (types, tests, GeneratedArtifactsDisplay), .github/workflows, traefik |
| **origin/cursor/infrastructure-testing-setup-800e** | 41 | Extends above: SecuritySolution/auth fixes, CI (Arango/Redis wait), backend (realm_registry, solution_base, security_solution journeys, control_room_service) | All of infrastructure-testing-setup + symphainy_coexistence_fabric (bases, security_solution, realm_registry), docker-compose.fullstack |
| **origin/cursor/parameter-assertion-tests-829c** | 20 | Testing vision, integration tests, Phase 4 (any removal), Phase 5 (hook consolidation), archive deprecated | Frontend tests + archive, docker-compose.test.yml, scripts/wait-for-services.sh, tests/integration/*, tests/expected/* |
| **origin/cursor/intent-services-pilot-6262** | 1 | ingest_file + save_materialization intent services only | content/intent_services/ingest_file_service.py, save_materialization_service.py, bases/intent_service_base.py |
| **origin/feature/intent-services-pilot** | 2 | Same as 6262 + README for content intent services | Same 5–6 files + docs |
| **origin/cursor/insights-realm-intent-contracts-5b32** | 0 | — | — |
| **origin/cursor/intent-services-pilot-d31b** | 0 | — | — |
| **origin/cursor/infrastructure-frontend-only** | 0 | — | — |

---

## 2. Overlap and Conflict Risk

### High risk (same file, different edits by multiple branches)

- **symphainy_platform/runtime/service_factory.py**  
  - **Foundation (you):** Pre-boot failure → raise RuntimeError; init order.  
  - **content-intent-services:** Content intent registration, orchestrator wiring.  
  - **infrastructure-testing-setup-800e:** Possibly solution/realm registration.  
  - **Strategy:** Merge in order: Foundation first (so service_factory has your strict init), then content-intent-services (add Content intent registration), then infra-800e. Resolve conflicts by keeping Foundation semantics and adding the other teams’ registrations.

- **symphainy_platform/bases/__init__.py**  
  - **content-intent-services:** Exports intent_service_base.  
  - **infrastructure-testing-setup-800e:** Exports solution_base.  
  - **Strategy:** Single merge: ensure both intent_service_base and solution_base (and any new bases) are exported.

- **docker-compose.yml**  
  - **Foundation (you):** experience service (experience_main.py), healthchecks, env for experience (REDIS_URL=redis://redis:6379, etc.).  
  - **infrastructure-testing-setup-800e:** May add fullstack/test variants.  
  - **Strategy:** Keep your docker-compose.yml as the main one; merge in any new services or env from 800e (e.g. docker-compose.fullstack as a separate file if not already).

### Medium risk (frontend – multiple teams)

- **symphainy-frontend/** (types, APIService, core, GeneratedArtifactsDisplay, tests)  
  - **infrastructure-testing-setup** and **infrastructure-testing-setup-800e:** Type cleanup, tests.  
  - **parameter-assertion-tests-829c:** Tests, any removal, archive.  
  - **Strategy:** Treat one branch as the “frontend type/test” source (recommend **infrastructure-testing-setup-800e** as it has SecuritySolution fixes and CI), then bring in parameter-assertion-tests-829c’s testing docs and integration test scripts. Resolve GeneratedArtifactsDisplay (e.g. add `status` to Artifact type or fix usage) once and keep that fix in the chosen frontend branch.

### Lower risk (mostly additive)

- **content-intent-services** vs **intent-services-pilot-6262** / **feature/intent-services-pilot:**  
  - content-intent-services is the larger set (all Content intent services + orchestrator).  
  - 6262/feature are subsets (ingest_file, save_materialization).  
  - **Strategy:** Use **content-intent-services** for Content Realm; ignore or merge 6262/feature only if you need just those two intents and not the full Content refactor.

---

## 3. Recommended Merge Order and Flow

Goal: **Foundation (your work) is the base**, then add **backend intent/services** from content-intent-services, then **frontend + CI + SecuritySolution** from infrastructure-testing-setup-800e, then **testing docs and integration scripts** from parameter-assertion-tests-829c.

### Step 1: Push and consolidate Foundation (your work)

1. Commit all local changes on `main` (bootstrap, experience_main, docker-compose, docs, probe script, CONFIG_ACQUISITION_SPEC).
2. Push `main` to `origin` (or push to a branch like `foundation/experience-auth-health` and open a PR into `main`).
3. Ensure `main` is the single source of truth for: config acquisition (override=False), pre-boot, experience_main, docker-compose service definitions and healthchecks.

### Step 2: Merge Content Realm (content-intent-services)

1. Create a merge branch: `git checkout -b merge/content-intent main` (after main has your Foundation work).
2. Merge: `git merge origin/cursor/content-intent-services`.
3. Resolve conflicts:
   - **service_factory.py:** Keep your RuntimeError-on–Public-Works-failure and init order; add Content intent registration and Content Orchestrator wiring from content-intent-services.
   - **bases/__init__.py:** Export both intent_service_base and any existing bases.
4. Run backend tests; fix any regressions.
5. Merge this branch into `main` (or open PR: merge/content-intent → main).

### Step 3: Merge Frontend + CI + SecuritySolution (infrastructure-testing-setup-800e)

1. Branch: `git checkout -b merge/infra-800e main` (or from updated main after Step 2).
2. Merge: `git merge origin/cursor/infrastructure-testing-setup-800e`.
3. Resolve conflicts:
   - **docker-compose.yml:** Keep your experience service and healthchecks; add any new services/compose files from 800e (or keep docker-compose.fullstack as a separate file).
   - **service_factory.py:** Keep Foundation + Content; add any solution/realm registration from 800e.
   - **symphainy-frontend:** Prefer 800e’s type fixes and SecuritySolution/auth fixes; ensure GeneratedArtifactsDisplay has a consistent Artifact type (e.g. add `status` or fix usage so the build passes).
4. Run frontend build and backend tests; fix the TypeScript error in GeneratedArtifactsDisplay if still present.
5. Merge into `main`.

### Step 4: Add testing docs and integration scripts (parameter-assertion-tests-829c)

1. Branch: `git checkout -b merge/parameter-tests main`.
2. Merge: `git merge origin/cursor/parameter-assertion-tests-829c`.
3. Resolve conflicts:
   - Prefer keeping the testing vision and integration test scripts (e.g. docker-compose.test.yml, wait-for-services.sh, tests/integration/*).
   - If frontend files conflict, prefer the version already merged from infrastructure-testing-setup-800e (Step 3).
4. Run tests; then merge into `main`.

### Step 5: Optional – intent-services-pilot-6262 / feature/intent-services-pilot

Only if you did **not** merge content-intent-services (which already includes more Content intents). If you did merge content-intent-services, these branches are redundant. If you want only ingest_file + save_materialization on top of current main, cherry-pick those commits onto main instead of merging the whole branch.

---

## 4. Who Does What (suggested)

- **Foundation owner (you):** Push Foundation to main; own service_factory conflict resolution (init order + Public Works failure semantics); own docker-compose.yml (experience + healthchecks).
- **Team A (content intent services):** Own content-intent-services merge and conflict resolution for content orchestrator + intent_services; confirm service_factory Content registration is correct after merge.
- **Team B (frontend + CI):** Own infrastructure-testing-setup-800e merge; fix GeneratedArtifactsDisplay / Artifact type so frontend build passes; own SecuritySolution and CI (Arango/Redis wait) semantics.
- **Testing / parameter-assertion owner:** Own parameter-assertion-tests-829c merge; keep testing docs and integration scripts; resolve any remaining frontend conflicts by deferring to the 800e version.

---

## 5. Quick Reference: Files Touched by More Than One Branch

- **service_factory.py:** Foundation, content-intent-services, infrastructure-testing-setup-800e  
- **docker-compose.yml:** Foundation, infrastructure-testing-setup-800e  
- **symphainy_platform/bases/__init__.py:** content-intent-services, infrastructure-testing-setup-800e  
- **GeneratedArtifactsDisplay.tsx:** infrastructure-testing-setup, infrastructure-testing-setup-800e, parameter-assertion-tests-829c  
- **Frontend types (content, insights, adapters, core, APIService, etc.):** infrastructure-testing-setup, infrastructure-testing-setup-800e, parameter-assertion-tests-829c  

---

## 6. Summary

1. **Yes:** Branch and file visibility is possible from the repo (remotes fetched). This doc is based on that.
2. **Strategy:** Foundation → main first; then merge content-intent-services (Content Realm); then infrastructure-testing-setup-800e (frontend + CI + SecuritySolution); then parameter-assertion-tests-829c (testing docs + integration). Resolve the high-risk files (service_factory, docker-compose, bases, frontend types) in that order with clear ownership.
3. **Best of all three:** Keep your config/pre-boot/experience/auth and healthchecks; add Content intent services and orchestrator from content-intent-services; add type cleanup, tests, CI, and SecuritySolution fixes from infrastructure-testing-setup-800e; add testing vision and integration scripts from parameter-assertion-tests-829c.
