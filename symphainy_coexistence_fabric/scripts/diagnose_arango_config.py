#!/usr/bin/env python3
"""
Arango/env diagnostic: what the platform sees after G2 (config acquisition + contract).

Run from repo root: python3 scripts/diagnose_arango_config.py

Shows:
- Which ARANGO_* env vars are set (names only; no secret values).
- What canonical config resolves to for Arango (url, username, database; password length only).
- Whether config/development.env exists and is loaded.
- Optional: try Arango connection and report result (same as pre-boot).
"""

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def main():
    from symphainy_platform.bootstrap.platform_config import acquire_env, build_canonical_config
    from symphainy_platform.bootstrap.repo_root import get_repo_root

    root = get_repo_root()
    config_dev = root / "config" / "development.env"
    env_secrets = root / ".env.secrets"

    print("=== Arango/env diagnostic (G2 path) ===\n")
    print(f"Repo root: {root}")
    print(f"config/development.env exists: {config_dev.exists()}")
    print(f".env.secrets exists: {env_secrets.exists()}")

    # Which ARANGO_* are set (after acquisition)
    acquire_env()
    arango_vars = [k for k in os.environ if k.startswith("ARANGO")]
    print(f"\nARANGO_* env vars set (after acquire_env): {sorted(arango_vars) or '(none)'}")

    cfg = build_canonical_config()
    url = cfg.get("arango_url") or "(default)"
    username = cfg.get("arango_username") or "(default)"
    database = cfg.get("arango_database") or "(default)"
    pwd = cfg.get("arango_password") or ""
    pwd_status = "blank" if not pwd else f"set ({len(pwd)} chars)"

    print("\nCanonical config (Arango):")
    print(f"  arango_url:      {url}")
    print(f"  arango_username: {username}")
    print(f"  arango_database: {database}")
    print(f"  arango_password: {pwd_status}")

    # Try connection (same as pre-boot)
    print("\n--- Connection check (same as pre-boot) ---")
    try:
        from arango import ArangoClient
        client = ArangoClient(hosts=cfg.get("arango_url") or "http://localhost:8529")
        db = client.db(
            name=cfg.get("arango_database") or "symphainy_platform",
            username=cfg.get("arango_username") or "root",
            password=cfg.get("arango_password") or "",
        )
        db.version()
        print("OK: Connected and authorized.")
    except Exception as e:
        print(f"FAIL: {e}")
        if "401" in str(e) or "Unauthorized" in str(e):
            print("\n>>> 401 = wrong password or user not authorized.")
            print(">>> If using Docker Arango (default root password test_password), set in .env.secrets:")
            print(">>>   ARANGO_PASS=test_password   OR   ARANGO_ROOT_PASSWORD=test_password")
            print(">>> If config/development.env is missing, URL/user/database fall back to defaults (localhost:8529, root, symphainy_platform).")
            print(">>> Create config/development.env with ARANGO_URL, ARANGO_USER (or ARANGO_USERNAME), ARANGO_DB (or ARANGO_DATABASE) if you need different values.")


if __name__ == "__main__":
    main()
