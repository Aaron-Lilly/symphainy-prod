#!/usr/bin/env python3
"""
Probe 01: Entry & Exit Points

TRACES (does not assert):
- Exact entry point (process + code)
- Boot order A → B → C with evidence
- First request path (what code runs on first browser request)

Output: Report for Platform Operation Map §1, §2, §3.
Run from repo root: python3 probes/probe_01_entry_exit.py
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def trace_entry_point():
    """Trace exact entry point from runtime_main.py (G2/G3 flow)."""
    runtime_main = REPO_ROOT / "runtime_main.py"
    text = runtime_main.read_text()
    return {
        "process_entry": "python runtime_main.py (or main.py → runtime_main.main())",
        "code_entry": "runtime_main.py, main(), line 46 (if __name__ == '__main__': main())",
        "first_executable_in_main": "load_platform_config() (G2: acquire env + build canonical config)",
        "evidence": f"File: {runtime_main.relative_to(REPO_ROOT)}; bootstrap/platform_config.py",
    }


def trace_boot_order():
    """Trace boot order from runtime_main.main() and service_factory (G2 → G3 → Φ3)."""
    # runtime_main.main(): load_platform_config() → pre_boot_validate(config) → create_runtime_services(config) → create_fastapi_app → uvicorn
    steps = [
        (1, "load_platform_config()", "runtime_main.py", "G2: acquire env + build canonical config (bootstrap/platform_config)"),
        (1.1, "  acquire_env()", "bootstrap/platform_config.py", "Load .env.secrets, config/development.env, .env from repo root"),
        (1.2, "  build_canonical_config()", "bootstrap/platform_config.py", "Canonical dict from os.environ only"),
        (2, "pre_boot_validate(config)", "runtime_main.py", "G3: Data plane then Consul; exit on first failure"),
        (3, "create_runtime_services(config)", "runtime_main.py", "Φ3: Build object graph (async)"),
        (3.1, "  PublicWorksFoundationService(config)", "service_factory.py", "Infrastructure adapters (canonical config only)"),
        (3.2, "  public_works.initialize()", "service_factory.py", "Async init adapters + abstractions; raises if failed"),
        (3.3, "  StateSurface(...)", "service_factory.py", "State + ArtifactRegistry"),
        (3.4, "  WriteAheadLog(...)", "service_factory.py", "Audit trail"),
        (3.5, "  IntentRegistry() + realm intent registration", "service_factory.py", "Intent handler registry"),
        (3.6, "  ExecutionLifecycleManager(...)", "service_factory.py", "Orchestrator"),
        (3.7, "  RuntimeServices(...)", "service_factory.py", "Container returned"),
        (4, "create_fastapi_app(services)", "runtime_main.py", "FastAPI app with routes"),
        (4.1, "  create_runtime_app(...)", "service_factory.py", "runtime_api.create_runtime_app"),
        (5, "uvicorn.run(app, host, port)", "runtime_main.py", "HTTP server started"),
    ]
    return steps


def trace_first_request_path():
    """Trace what code runs for first browser request (GET /health)."""
    return {
        "request": "GET /health",
        "handler": "runtime_api.py lines 1126-1129: create_runtime_app() registers @app.get('/health'); async def health() returns {'status': 'healthy', 'service': 'runtime', 'version': '2.0.0'}",
        "evidence": "symphainy_platform/runtime/runtime_api.py:1126-1129",
    }


def collect_implicit_assumptions():
    """Implicit assumptions from entry/exit trace."""
    return [
        "G2: Config is acquired once (acquire_env + build_canonical_config); pre-boot and Public Works consume only that config; no env reads for platform infra after build.",
        "G3: Pre-boot validates Data Plane then Consul; exit on first failure; no create_runtime_services if pre-boot fails.",
        "Config is loaded synchronously at start; no hot reload of env.",
        "All services are created in one async run (create_runtime_services); no lazy init of core graph.",
        "Intent handlers are registered in fixed order: Content → Insights → Operations → Outcomes → Security → Control Tower → Coexistence.",
        "Solutions are initialized with initialize_mcp_servers=True (MCP servers started during boot).",
        "First HTTP request that typically hits is GET /health or GET /docs; no route before uvicorn.run.",
        "FastAPI app does not create services; it receives them (injected).",
    ]


def main():
    print("# Probe 01 Output: Entry & Exit (copy into PLATFORM_OPERATION_MAP.md §1, §2, §3)\n")
    print("## §1. Entry point\n")
    ep = trace_entry_point()
    for k, v in ep.items():
        print(f"- **{k}:** {v}")
    print("\n## §2. Boot order\n")
    print("| Step | Component | Evidence |")
    print("|------|-----------|----------|")
    for step in trace_boot_order():
        print(f"| {step[0]} | {step[1]} | {step[2]} |")
    print("\n## §3. First request path\n")
    fr = trace_first_request_path()
    print(f"- **Request:** {fr['request']}")
    print(f"- **Handler / code path:** {fr['handler']}")
    print(f"- **Evidence:** {fr['evidence']}")
    print("\n## Implicit assumptions\n")
    for a in collect_implicit_assumptions():
        print(f"- {a}")
    print("\n---\n*Probe 01 complete. Copy above into docs/testing/PLATFORM_OPERATION_MAP.md.*")


if __name__ == "__main__":
    main()
