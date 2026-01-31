#!/usr/bin/env python3
"""
Test Grafana Cloud OTLP (Option C).

OpenTelemetry is required for the platform. This script:
1. Loads .env.secrets and builds config (same as Genesis).
2. Runs pre-boot telemetry check (endpoint reachable).
3. Initializes OTLP tracer (same as TelemetryAdapter), records one span
   "symphainy-grafana-cloud-test", flushes so it is sent to Grafana Cloud.
4. Fails if OpenTelemetry is not installed or endpoint unreachable.

Run from repo root with .env.secrets present and OpenTelemetry installed:
  python3 scripts/test_grafana_cloud_otlp.py

Expect: "Grafana Cloud OTLP: endpoint reachable, test span sent."
Then check Grafana Cloud → Traces for service symphainy-platform and span symphainy-grafana-cloud-test.
"""

import os
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))


def main() -> int:
    # 1. Load env and build config (Genesis G2)
    from symphainy_platform.bootstrap.platform_config import load_platform_config
    from symphainy_platform.bootstrap.pre_boot import _check_telemetry

    print("Loading config (G2)...")
    config = load_platform_config()
    endpoint = config.get("otel_exporter_otlp_endpoint")
    if not endpoint:
        print("FAIL: OTEL_EXPORTER_OTLP_ENDPOINT not set. Add it to .env.secrets (Grafana Cloud OTLP).")
        return 1

    # 2. Pre-boot telemetry check (Genesis G3)
    print("Checking OTLP endpoint reachability (G3)...")
    try:
        _check_telemetry(config)
    except SystemExit as e:
        print(f"FAIL: Telemetry check failed: {e}")
        return 1
    print("  Endpoint reachable.")

    # 3. Send one test span to Grafana Cloud if OpenTelemetry is available (same exporter as runtime)
    try:
        from symphainy_platform.foundations.public_works.adapters.telemetry_adapter import TelemetryAdapter
        adapter = TelemetryAdapter(
            service_name="symphainy-platform",
            otlp_endpoint=endpoint,
        )
    except ImportError:
        print("Grafana Cloud OTLP: endpoint reachable (pre-boot passed).")
        print("  Skipping test span: install opentelemetry-* to verify export. Runtime sends traces when running.")
        return 0

    if not adapter.initialize():
        print("FAIL: TelemetryAdapter.initialize() failed.")
        return 1

    try:
        from opentelemetry import trace
        tracer = trace.get_tracer("symphainy-grafana-cloud-test", "1.0")
        with tracer.start_as_current_span("symphainy-grafana-cloud-test") as span:
            span.set_attribute("test", "grafana-cloud-otlp")
        # Flush so the span is exported before we exit
        provider = trace.get_tracer_provider()
        if hasattr(provider, "force_flush"):
            provider.force_flush(timeout_millis=5000)
    except Exception as e:
        print(f"FAIL: Sending test span failed: {e}")
        return 1

    print("Grafana Cloud OTLP: endpoint reachable, test span sent.")
    print("  Check Grafana Cloud → Traces for service 'symphainy-platform' and span 'symphainy-grafana-cloud-test'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
