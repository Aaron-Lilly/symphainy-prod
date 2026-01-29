#!/usr/bin/env python3
"""
Probe 02: Configuration as Behavior

TRACES (does not assert):
- Which env vars, ports, or names change behavior or stability
- What breaks when config is missing or wrong (implicit contracts)

Output: Report for Platform Operation Map §4.
Run from repo root: python3 probes/probe_02_config_behavior.py
"""

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def trace_config_contracts():
    """Extract config contract from env_contract and get_env_contract()."""
    from symphainy_platform.config.env_contract import EnvContract, get_env_contract

    # Required = no default or default that assumes local services; changing breaks boot or runtime
    contracts = []
    for name, field in EnvContract.model_fields.items():
        default = field.default
        if default is None and "Optional" in str(field.annotation):
            contracts.append((name, "Optional", "None", "Feature may be disabled or use fallback"))
        elif name in ("REDIS_URL", "ARANGO_URL"):
            contracts.append((name, "Has default", str(default), "Wrong URL → PublicWorks.initialize() / adapters fail at boot"))
        elif name == "RUNTIME_PORT":
            contracts.append((name, "Has default", str(default), "Wrong port → uvicorn binds elsewhere; client must use same port"))
        elif name == "LOG_LEVEL":
            contracts.append((name, "Has default", str(default), "Invalid value → Pydantic ValidationError at get_env_contract()"))
        elif "PORT" in name:
            contracts.append((name, "Has default", str(default), "Out of range 1-65535 → ValidationError at get_env_contract()"))
        elif name.startswith("SUPABASE") or name.startswith("GCS") or name.startswith("MEILI"):
            contracts.append((name, "Optional", "None", "Optional integration; missing → feature disabled"))
        else:
            contracts.append((name, "Has default", str(default), "Change may affect adapters or ports"))
    return contracts


def main():
    print("# Probe 02 Output: Config as Behavior (copy into PLATFORM_OPERATION_MAP.md §4)\n")
    print("## §4. Config contracts\n")
    print("| Config element | Required? | Default / note | Effect if missing/wrong |")
    print("|----------------|-----------|----------------|--------------------------|")
    for name, req, default, effect in trace_config_contracts():
        print(f"| {name} | {req} | {default} | {effect} |")
    print("\n**Evidence (legacy):** symphainy_platform/config/env_contract.py + get_env_contract().")
    print("\n**Canonical config (G2):** Bootstrap builds the single config source: symphainy_platform/bootstrap/platform_config.py (acquire_env → build_canonical_config). See CONFIG_ACQUISITION_SPEC and CONFIG_CONTRACT_SPEC. runtime_main uses load_platform_config(); pre-boot and Public Works consume only that config.")
    print("\n**Implicit contracts:**")
    print("- All ports validated 1–65535 at load; invalid → process exits before boot.")
    print("- LOG_LEVEL must be one of DEBUG, INFO, WARNING, ERROR, CRITICAL.")
    print("- Pre-boot (G3) validates reachability of Redis, Arango, Consul, Supabase, GCS, Meilisearch, DuckDB before create_runtime_services().")
    print("\n---\n*Probe 02 complete. Copy above into docs/testing/PLATFORM_OPERATION_MAP.md §4.*")


if __name__ == "__main__":
    main()
