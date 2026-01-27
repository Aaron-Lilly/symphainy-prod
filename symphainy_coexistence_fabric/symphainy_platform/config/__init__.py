"""
Configuration Module

Phase 0: Environment contract and configuration management.
"""

from .env_contract import EnvContract, get_env_contract, get_env_value

__all__ = [
    "EnvContract",
    "get_env_contract",
    "get_env_value",
]
