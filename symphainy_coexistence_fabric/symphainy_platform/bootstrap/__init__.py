"""
Bootstrap: contract-first platform config and pre-boot validation (G2 + G3).

Layer 1: load_platform_config() — acquire env then build canonical config (Gate G2).
Layer 2: pre_boot_validate(config) — connectivity/readiness checks; exit on failure (Gate G3).

The runtime entry point uses these before building the object graph.
Downstream (e.g. Public Works) consumes only the config produced by Layer 1.
"""

from .platform_config import load_platform_config, acquire_env, build_canonical_config
from .pre_boot import pre_boot_validate
from .repo_root import get_repo_root

__all__ = [
    "load_platform_config",
    "acquire_env",
    "build_canonical_config",
    "pre_boot_validate",
    "get_repo_root",
]
