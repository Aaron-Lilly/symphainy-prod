# Config Acquisition Spec (Gate G2 — First Step of Φ2)

**Purpose:** Define how the process gets its configuration so “Config loads” (Gate G2) is unambiguous. This is the **first mechanical step of Φ2 (Runtime Consciousness)**. No other code may read platform config until acquisition has run.

**Status:** Canonical. Implementation (bootstrap / runtime_main) must conform to this spec.

**References:**
- [FOUNDATION_PLAN.md](../FOUNDATION_PLAN.md) Step 1
- [STEP0_FOUNDATION_OPEN_QUESTIONS.md](../STEP0_FOUNDATION_OPEN_QUESTIONS.md) — validated answers
- [genesis_protocol.md](../genesis_protocol.md) — G2, Φ2
- [PLATFORM_CONTRACT.md](PLATFORM_CONTRACT.md) — §4 (one config source)

---

## 1. Scope

**Config acquisition** means: **populating the environment** (or otherwise making config values available) so that the next step—building the **canonical config** (see Config Contract spec)—can read them. This spec covers:

- Which env files exist and their role
- Where they live and in what order they are loaded
- Precedence and rules (e.g. no secrets in `.env`)
- Who loads them (Φ1 vs Φ2) per deployment mode
- When acquisition runs (before any other platform config read)

This spec does **not** define the canonical config shape or key mapping; that is the [Config Contract spec](CONFIG_CONTRACT_SPEC.md) (Step 2).

---

## 2. Repo Root

**Definition:** **Repo root** is the directory that contains the `symphainy_platform` package (i.e. the workspace root of the coexistence fabric repo).

- All env file paths in this spec are relative to repo root.
- A single helper (e.g. “get repo root”) must be used everywhere so bootstrap, tests, and tooling share one definition. No alternate definitions (e.g. different `__file__.parents[n]` in different modules).
- When running in Docker, the process may not read env files from disk (Φ1 injects env); if it does, “repo root” is the app directory inside the container.

---

## 3. Env Files: Names, Paths, Role

Exactly three env files are part of the contract. All paths are relative to **repo root**.

| File | Path | Role | Required? |
|------|------|------|-----------|
| **.env.secrets** | `.env.secrets` | Sensitive secrets (passwords, API keys). Excluded from repo. | Required when process loads env (non-Docker); optional when Docker injects env (Φ1). |
| **config/development.env** | `config/development.env` | Non-secret config (URLs, hosts, DB names, user names). Developer overrides / dev infra. | Optional. If absent, we rely on other files or compose/env. |
| **.env** | `.env` | Defaults, documentation, non-secret fallback only. | Optional. |

**Rules:**

- **.env** = **defaults + documentation + non-secret fallback only.** Do **not** use `.env` for secrets or environment-specific overrides. Do not treat `.env` as “.env.secrets-lite.” (CTO tightening.)
- Secrets and environment-specific overrides belong in `.env.secrets` or `config/development.env`.
- If a file is optional and missing, it is skipped; no error. Acquisition proceeds with the next file in order.

---

## 4. Load Order and Precedence

When the **process** is responsible for loading (see §6):

1. **.env.secrets** (if present)
2. **config/development.env** (if present)
3. **.env** (if present)

**Precedence:** Later file **overrides** earlier for the same key (e.g. `load_dotenv(..., override=False)` for later files, or equivalent “later wins” semantics). So: `.env.secrets` base → `config/development.env` overrides → `.env` overrides. This allows dev overrides without touching secrets.

Process env (e.g. Docker) wins over file values; then first file to set a key wins.

---

## 5. Who Loads: Φ1 vs Φ2

Responsibility depends on **deployment mode**.

| Mode | Who loads env | When |
|------|----------------|------|
| **Docker (or any env-injected run)** | **Φ1.** Docker/orchestrator supplies env via `env_file` and/or `environment` block. The process does **not** read .env.secrets or other files from disk; it only sees `os.environ` already populated. | At container/process start (Φ1 Physical Viability). |
| **Local dev / non-Docker (process started without pre-injected env)** | **Φ2.** The **first step of Φ2** (config acquisition) loads env files in the order and paths above. In code: the designated “acquire env” step (e.g. first thing inside the function that builds canonical config, or a dedicated function called by main/runtime_main before building config). | Before building canonical config; before any other platform code reads config. |
| **CI** | Either CI injects env (Φ1 equivalent) or the process loads files in Φ2 (e.g. CI places a specific env file and the same Φ2 step loads it). Define per pipeline. | Same as above. |
| **Prod / Option C** | Same as local dev if the process is not given pre-injected env; if using GCP/K8s secrets or similar, env may be injected (Φ1 equivalent) and no file load. | Same as above. |

**Invariant:** By the time we **build canonical config**, env has been loaded by either Φ1 (injected) or the designated Φ2 step (process loads files). No other code path (e.g. import of `service_config`, or `config_helper` on first use) may be relied on for platform boot. Exactly one env acquisition point.

---

## 6. When Acquisition Runs

- **Relative to Φ2:** Acquisition is the **first** mechanical step of Φ2 (Runtime Consciousness). So: process starts → (if non-Docker) load env files in order from repo root → then build canonical config → then any other Φ2 steps (logging, DI, etc.).
- **Relative to canonical config:** Acquisition runs **before** the code that builds the canonical config object. That builder reads only from `os.environ` (or equivalent) after acquisition has run.
- **Relative to Public Works / pre-boot:** Acquisition and canonical config build run **before** pre-boot and **before** `create_runtime_services()`. So: acquire env → build config → pre-boot(config) → create_runtime_services(config).

---

## 7. Designated Loader (Code Contract)

- **Single designated place:** One function or one “step” in the entry path (e.g. runtime_main or main.py) is responsible for loading env files when the process is in “non-Docker” mode. That step must run before any call to build canonical config.
- **No scattered loading:** Platform boot must **not** depend on:
  - `service_config` being imported (and its import-time load of .env.secrets), or
  - `config_helper` loading .env.secrets on first use of a getter.
- **Contract:** “By the time we build canonical config, env has been loaded by the designated Φ2 step (or by Φ1 in Docker).” Implementations must guarantee this.

---

## 8. Summary: What “Config Loads” (G2) Means

Gate G2 (“Config loads”) is satisfied when:

1. **If Docker / env-injected:** Φ1 has supplied env; the process has not read env files. **Then** the process builds canonical config from `os.environ`.
2. **If non-Docker:** The designated Φ2 step has loaded env files in order (`.env.secrets`, `config/development.env`, `.env`) from repo root, each if present. **Then** the process builds canonical config from `os.environ`.

So: **“Config loads”** = env is populated (by Φ1 or by Φ2 acquisition) **and** canonical config has been built from that env. The Config Contract spec defines the shape and mapping of that canonical config.

---

## 9. References to This Spec

- **FOUNDATION_PLAN.md** Step 1 — output is this spec.
- **genesis_protocol.md** Gate G2 — “Config loads” is defined by this spec.
- **PLATFORM_CONTRACT.md** §4 — “one config source” assumes env is acquired per this spec, then canonical config is built per Config Contract spec.
