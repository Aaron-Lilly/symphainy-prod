"""
Repo root: single definition for env file paths.

CONFIG_ACQUISITION_SPEC: "Repo root is the directory that contains the
symphainy_platform package." One helper, no alternate definitions.
"""

from pathlib import Path


def get_repo_root() -> Path:
    """Directory containing the symphainy_platform package (workspace root)."""
    # This file is symphainy_platform/bootstrap/repo_root.py -> parents[1] = symphainy_platform, parents[2] = repo root
    return Path(__file__).resolve().parents[2]
