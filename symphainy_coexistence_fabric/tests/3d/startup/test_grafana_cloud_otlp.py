"""
Test Grafana Cloud OTLP (Option C).

Verifies that OTEL_EXPORTER_OTLP_ENDPOINT (from .env.secrets) is set and reachable
(same pre-boot check as Genesis G3). When the full stack runs, runtime sends traces
to Grafana Cloud; this test confirms the endpoint is valid.
"""

import os
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestGrafanaCloudOtlpReachability:
    """Grafana Cloud OTLP endpoint is reachable (Genesis G3 telemetry check)."""

    def test_otel_endpoint_reachable(self):
        """Pre-boot telemetry check passes when OTEL_EXPORTER_OTLP_ENDPOINT is set and reachable."""
        from symphainy_platform.bootstrap.platform_config import load_platform_config
        from symphainy_platform.bootstrap.pre_boot import _check_telemetry

        config = load_platform_config()
        endpoint = config.get("otel_exporter_otlp_endpoint")
        if not endpoint:
            pytest.skip(
                "OTEL_EXPORTER_OTLP_ENDPOINT not set. "
                "Add to .env.secrets (Grafana Cloud OTLP) to run this test."
            )
        # Should not raise; _check_telemetry exits process on failure
        result = _check_telemetry(config)
        assert result == "checked"
