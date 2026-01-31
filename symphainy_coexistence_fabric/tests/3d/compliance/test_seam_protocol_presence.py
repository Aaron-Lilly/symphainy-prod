"""
Seam probe: Required protocol getters return non-None after successful boot.

Validates Layer B of PLATFORM_PROBE_APPROACH: when Genesis succeeds (full required
infra), Public Works exists and required protocol getters return a working
implementation (non-None). "Protocols only exist when infrastructure is there."

Run with genesis_services fixture (requires full infra / genesis_app). If
genesis_services is None (pre_boot skipped), tests are skipped.

See docs/testing/PLATFORM_PROBE_APPROACH.md Layer B.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Required protocol getters that must be non-None when boot succeeded (per PLATFORM_CONTRACT §3).
# Minimal set: state, file_storage, registry, artifact_storage (core runtime).
REQUIRED_GETTERS = [
    "get_state_abstraction",
    "get_file_storage_abstraction",
    "get_registry_abstraction",
    "get_artifact_storage_abstraction",
]


class TestSeamProtocolPresence:
    """When Genesis succeeds, required protocol getters return non-None."""

    @pytest.mark.requires_infra
    def test_required_protocol_getters_non_none_after_boot(self, genesis_services):
        """
        After successful boot, public_works required getters return non-None.

        genesis_services is None when pre_boot failed (missing infra); then skipped.
        """
        if genesis_services is None:
            pytest.skip("genesis_services not available (pre_boot skipped or failed)")
        pw = getattr(genesis_services, "public_works", None)
        if pw is None:
            pytest.skip("public_works not available on runtime_services")
        for getter_name in REQUIRED_GETTERS:
            getter = getattr(pw, getter_name, None)
            assert getter is not None, f"Public Works missing {getter_name}"
            value = getter()
            assert value is not None, (
                f"{getter_name}() returned None after successful boot; "
                "required protocol must be wired when infra is present."
            )
