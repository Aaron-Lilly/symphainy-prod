# Probes (Discovery, Not Tests)

**Probes** trace and document how the platform actually operates. They do not assert pass/fail. Their output fills the [Platform Operation Map](docs/testing/PLATFORM_OPERATION_MAP.md) and the [Reality Maps](docs/testing/reality_maps/README.md) so we can state **with 100% certainty** exactly how each part of the platform works.

See [docs/testing/PROBE_DESIGN.md](docs/testing/PROBE_DESIGN.md) for philosophy and probe vs test.  
**Full layer map (Foundations → Civic → Realms → Runtime → Solutions → Utilities):** [docs/testing/PROBE_LAYER_MAP.md](docs/testing/PROBE_LAYER_MAP.md).

---

## Run order (dependency order)

| Order | Probe | Layer | Artifact |
|-------|-------|--------|----------|
| 0 | probe_01_entry_exit | Lock platform | Platform Operation Map §1–§3 |
| 0 | probe_02_config_behavior | Lock platform | Platform Operation Map §4 |
| 0 | probe_03_order_restart | Lock platform | Platform Operation Map §5 + Stability/Gravity |
| 1 | probe_04_public_works | Foundations | Public Works Reality Map |
| 2 | probe_05_curator_foundation | Foundations | Curator (Foundation) Reality Map |
| 3 | probe_06_smart_city | Civic | Smart City Reality Map |
| 4 | probe_07_agentic | Civic | Agentic Reality Map |
| 5 | probe_08_experience | Civic | Experience Reality Map |
| 6 | probe_09_artifact_plane | Civic | Artifact Plane Reality Map |
| 7 | probe_10_orchestrator_health | Civic | Orchestrator Health Reality Map |
| 8 | probe_11_platform_sdk | Civic | Platform SDK Reality Map |
| 9 | probe_12_realms | Realms | Realms Reality Map |
| 10 | probe_13_runtime | Runtime | Runtime Reality Map |
| 11 | probe_14_solutions | Solutions | Solutions Reality Map |
| 12 | probe_15_utilities | Utilities | Utilities Reality Map |

---

## How to run

From repo root:

```bash
# Layer 0: Lock platform behavior
python3 probes/probe_01_entry_exit.py
python3 probes/probe_02_config_behavior.py
# probe_03: see probes/probe_03_order_restart.md (manual procedure)

# Layer 1: Foundations – Public Works
python3 probes/probe_04_public_works.py
# probe_05–15: designs in PROBE_LAYER_MAP.md; implement or run manually per layer.
```

After each probe, copy its output into the corresponding Reality Map or Platform Operation Map section.
