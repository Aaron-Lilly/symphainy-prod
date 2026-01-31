"""
Seam probe: §8A upstream behavior — callers get explicit failure when a required dependency is missing.

Validates that platform components (non-adapter) raise RuntimeError with "Platform contract §8A"
when a required dependency is not wired, instead of returning defaults or falling back silently.
Callers (runtime, intent services) must see the failure at the seam.

Seam: Caller → Platform (StateSurface, ArtifactRegistry, etc.).
Success: dependency wired → operation proceeds.
Failure: dependency missing (use_memory=False) → RuntimeError with §8A message.

See docs/testing/PLATFORM_SEAMS.md and PLATFORM_CONTRACT.md §8A.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

SECTION_8A_MARKER = "Platform contract §8A"


class TestSeamSection8AStateSurface:
    """Probe: StateSurface raises RuntimeError (§8A) when state_abstraction is missing."""

    @pytest.mark.asyncio
    async def test_get_session_state_raises_when_state_abstraction_missing(self):
        """StateSurface.get_session_state raises RuntimeError with §8A when state_abstraction is None."""
        from symphainy_platform.runtime.state_surface import StateSurface

        surface = StateSurface(state_abstraction=None, file_storage=None, use_memory=False)
        with pytest.raises(RuntimeError) as exc_info:
            await surface.get_session_state(session_id="s1", tenant_id="t1")
        assert SECTION_8A_MARKER in str(exc_info.value)
        assert "State abstraction not wired" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_set_session_state_raises_when_state_abstraction_missing(self):
        """StateSurface.set_session_state raises RuntimeError with §8A when state_abstraction is None."""
        from symphainy_platform.runtime.state_surface import StateSurface

        surface = StateSurface(state_abstraction=None, file_storage=None, use_memory=False)
        with pytest.raises(RuntimeError) as exc_info:
            await surface.set_session_state(
                session_id="s1", tenant_id="t1", state={"key": "value"}
            )
        assert SECTION_8A_MARKER in str(exc_info.value)
        assert "State abstraction not wired" in str(exc_info.value)


class TestSeamSection8AArtifactRegistry:
    """Probe: ArtifactRegistry raises RuntimeError (§8A) when state_abstraction is missing."""

    @pytest.mark.asyncio
    async def test_resolve_artifact_raises_when_state_abstraction_missing(self):
        """ArtifactRegistry.resolve_artifact raises RuntimeError with §8A when state_abstraction is None."""
        from symphainy_platform.runtime.artifact_registry import ArtifactRegistry

        registry = ArtifactRegistry(state_abstraction=None, use_memory=False)
        with pytest.raises(RuntimeError) as exc_info:
            await registry.resolve_artifact(
                artifact_id="a1", artifact_type="file", tenant_id="t1"
            )
        assert SECTION_8A_MARKER in str(exc_info.value)
        assert "State abstraction not wired" in str(exc_info.value)
