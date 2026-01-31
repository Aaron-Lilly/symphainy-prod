"""
Seam probe: No adapter escape — adapter getters raise; protocols are the only surface.

Validates Layer D of PLATFORM_PROBE_APPROACH: get_arango_adapter(),
get_supabase_adapter(), get_redis_adapter() must not expose adapters to callers
outside Public Works. They must raise RuntimeError so no code path can obtain
an adapter; protocols are the only surface.

See docs/testing/PLATFORM_PROBE_APPROACH.md Layer D.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class TestSeamNoAdapterLeak:
    """Adapter getters must raise RuntimeError; no adapter escape."""

    def test_get_arango_adapter_raises(self):
        """get_arango_adapter() raises RuntimeError (adapters must not escape Public Works)."""
        from symphainy_platform.foundations.public_works.foundation_service import (
            PublicWorksFoundationService,
        )

        pw = PublicWorksFoundationService(config={})
        with pytest.raises(RuntimeError) as exc_info:
            pw.get_arango_adapter()
        assert "not part of the public API" in str(exc_info.value) or "must not escape" in str(exc_info.value)

    def test_get_supabase_adapter_raises(self):
        """get_supabase_adapter() raises RuntimeError (adapters must not escape Public Works)."""
        from symphainy_platform.foundations.public_works.foundation_service import (
            PublicWorksFoundationService,
        )

        pw = PublicWorksFoundationService(config={})
        with pytest.raises(RuntimeError) as exc_info:
            pw.get_supabase_adapter()
        assert "not part of the public API" in str(exc_info.value) or "must not escape" in str(exc_info.value)
