"""
Platform lifecycle hooks (MVP: no-ops).

Per PLATFORM_VISION_RECONCILIATION §2.3: five hooks must exist in the boot/lifecycle
path so Enterprise can add behavior without refactoring control flow. In MVP all are no-ops.

Hook locations (runtime_main):
- startup_begin: before load_platform_config (before Φ1/G2)
- startup_complete: after create_fastapi_app(services), before uvicorn.run (after Φ3/Φ4 equivalent)
- shutdown_begin: on SIGTERM (graceful shutdown request)
- shutdown_complete: after uvicorn.run() returns or in atexit (after infrastructure released)
- crash_detected: in main() except block (unhandled exception / unclean exit path)
"""

from typing import Any, Dict


def startup_begin(config: None = None) -> None:
    """Before Φ1 / substrate init. MVP: no-op. Enterprise: telemetry, pre-flight."""
    pass


def startup_complete(config: None = None, app: Any = None) -> None:
    """After Φ4 / experience attachment. MVP: no-op. Enterprise: readiness declaration, health registration."""
    pass


def shutdown_begin(reason: str = "graceful") -> None:
    """On graceful shutdown request. MVP: no-op. Enterprise: drain active execution, persist WAL, checkpoint state."""
    pass


def shutdown_complete() -> None:
    """After infrastructure released. MVP: no-op. Enterprise: finalize WAL, release resources."""
    pass


def crash_detected(exc: BaseException, context: Dict[str, Any] | None = None) -> None:
    """On unhandled exception / unclean exit path. MVP: no-op. Enterprise: mark state for recovery, trigger recovery path."""
    pass
