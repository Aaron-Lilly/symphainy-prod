"""
Seam probe: Genesis gate (G3) does not progress to Public Works when infrastructure is missing.

Validates the design decision that adapters are excluded from §8A silent-degradation
scan because Genesis pre_boot_validate (G3) is the single gate: if required infra is
missing or unreachable, the process exits and create_runtime_services (hence Public Works)
is never invoked.

Seam: Genesis (pre_boot_validate) → Public Works (create_runtime_services).
Success: all G3 checks pass → create_runtime_services runs → Public Works available.
Failure: any G3 check fails → sys.exit(1) → no Public Works.

See docs/testing/PLATFORM_SEAMS.md.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Repo root
REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _fail_raises(service: str, reason: str, hint: str) -> None:
    """Raise SystemExit(1) instead of sys.exit(1) so tests can catch it."""
    raise SystemExit(1)


class TestSeamGenesisGate:
    """Probe: when required infra is missing, Genesis (G3) aborts and does not proceed to Public Works."""

    def test_pre_boot_exits_when_required_infra_missing(self):
        """
        pre_boot_validate(config) raises SystemExit(1) when a required service is missing.

        We patch _fail to raise SystemExit(1) so the test process does not exit.
        Config with supabase_url="" causes _check_supabase to call _fail.
        """
        from symphainy_platform.bootstrap import pre_boot_validate

        # Config that will trigger _check_supabase to fail (no network needed)
        config_missing_supabase = {"supabase_url": ""}

        with patch(
            "symphainy_platform.bootstrap.pre_boot._fail",
            side_effect=_fail_raises,
        ):
            with pytest.raises(SystemExit) as exc_info:
                pre_boot_validate(config_missing_supabase)
            assert exc_info.value.code == 1

