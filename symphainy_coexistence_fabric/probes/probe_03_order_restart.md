# Probe 03: Order / Restart (Fault Amplifiers)

**Step 3 from new_testing_mindset:** Run probes with different startup orders and restarts. Record Stability/Gravity reports.

Probes are **instruments that trace and document**. This probe is a **procedure** plus optional script. You run the procedure, observe, and fill the Stability/Gravity template. Output feeds **Platform Operation Map §5** and `docs/testing/stability_gravity_reports/`.

---

## Procedure

### 1. Baseline

- Start platform: `python3 runtime_main.py` (or `main.py`).
- Wait for log: "Runtime service ready on 0.0.0.0:PORT".
- Send first request: `GET http://localhost:PORT/health` → 200 and `{"status":"healthy",...}`.
- Record: **Baseline boot order** (from Probe 01) and **baseline first response** (status code, body).

### 2. Config variation (amplifies config-as-behavior)

- Unset or change one config at a time; restart process; observe.
  - Examples: unset `REDIS_URL`; set `RUNTIME_PORT=99999`; set `LOG_LEVEL=INVALID`.
- For each variation, record:
  - **Trigger:** What you changed.
  - **Observed behavior:** What broke (message, where it failed—startup vs first request).
  - **Time to failure:** Immediate (at get_env_contract / boot) vs delayed (first request).
- Fill **Stability/Gravity report** (copy `docs/testing/stability_gravity_reports/_TEMPLATE.md`); scope = `config`.
- Add row to **Platform Operation Map §5** (order/restart failure modes).

### 3. Order variation (if applicable)

- If the platform had multiple processes or services, start them in different orders and record what breaks.
- For single-process runtime (runtime_main only): order variation = **internal boot order** (e.g. if we could skip PublicWorks and start StateSurface—we cannot without code change; so this step may be "N/A – single process, fixed order in code").
- If you have docker-compose or multiple containers: start in different order; record which combination fails and where.
- Fill Stability/Gravity report; scope = `startup_order`.
- Add row to Map §5.

### 4. Restart behavior

- Start platform; send GET /health (success). Stop platform. Start again; send GET /health again.
- Observe: Does second start behave identically? Any "restart fixes it" or "restart breaks it"?
- If you have state (e.g. Redis): start, create some state, stop, start again—does state persist? Does restart "fix" a broken state (suggesting state leak or stale assumption)?
- Record in Stability/Gravity report; add row to Map §5.

---

## Output

- **Stability/Gravity reports:** One per trigger (config change, order change, restart). Save under `docs/testing/stability_gravity_reports/YYYYMMDD_config_*.md`, `YYYYMMDD_startup_order_*.md`, `YYYYMMDD_restart_*.md`.
- **Platform Operation Map §5:** Rows filled with trigger, observed behavior, hypothesis (do not resolve).

---

## Template row for Map §5

| Trigger | Observed behavior | Hypothesis (do not resolve) |
|---------|-------------------|-----------------------------|
| *(e.g. REDIS_URL unset)* | *(e.g. PublicWorks.initialize() fails; process exits)* | *(e.g. Redis is required for WAL/state; no graceful degradation)* |

---

*Probe 03 is manual: run procedure, observe, record. No fix; only hypotheses.*
