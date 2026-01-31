"""
Test Genesis Protocol - Config and Boot

Confirms:
1. USE_SUPABASE_TEST=1 causes config to use SUPABASE_TEST_* (test project).
2. genesis_app builds via full Genesis (G2 → G3 → Φ3) and /health responds when backing services are available.
"""

import os
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestGenesisConfigWithTestSupabase:
    """Config uses TEST Supabase vars when USE_SUPABASE_TEST=1."""

    def test_use_supabase_test_uses_test_url(self):
        """With USE_SUPABASE_TEST=1, build_canonical_config uses SUPABASE_TEST_URL."""
        os.environ["USE_SUPABASE_TEST"] = "1"
        test_url = "https://test-project.supabase.co"
        os.environ["SUPABASE_TEST_URL"] = test_url
        os.environ["SUPABASE_TEST_PUBLISHABLE_KEY"] = "test_anon"
        os.environ["SUPABASE_TEST_SECRET_KEY"] = "test_secret"
        try:
            from symphainy_platform.bootstrap.platform_config import build_canonical_config
            from symphainy_platform.bootstrap.repo_root import get_repo_root
            # Ensure env is acquired so our setenv is used
            from symphainy_platform.bootstrap.platform_config import acquire_env
            acquire_env()
            config = build_canonical_config()
            assert config.get("supabase_url") == test_url
            assert config.get("supabase_anon_key") == "test_anon"
            assert config.get("supabase_service_key") == "test_secret"
        finally:
            os.environ.pop("USE_SUPABASE_TEST", None)
            os.environ.pop("SUPABASE_TEST_URL", None)
            os.environ.pop("SUPABASE_TEST_PUBLISHABLE_KEY", None)
            os.environ.pop("SUPABASE_TEST_SECRET_KEY", None)

    def test_no_use_supabase_test_uses_prod_vars(self):
        """With USE_SUPABASE_TEST=0, config uses SUPABASE_URL."""
        os.environ["USE_SUPABASE_TEST"] = "0"
        prod_url = "https://prod-project.supabase.co"
        os.environ["SUPABASE_URL"] = prod_url
        os.environ["SUPABASE_PUBLISHABLE_KEY"] = "prod_anon"
        os.environ["SUPABASE_SECRET_KEY"] = "prod_secret"
        try:
            from symphainy_platform.bootstrap.platform_config import build_canonical_config, acquire_env
            acquire_env()
            config = build_canonical_config()
            assert config.get("supabase_url") == prod_url
        finally:
            os.environ.pop("USE_SUPABASE_TEST", None)
            os.environ.pop("SUPABASE_URL", None)
            os.environ.pop("SUPABASE_PUBLISHABLE_KEY", None)
            os.environ.pop("SUPABASE_SECRET_KEY", None)


class TestGenesisAppBoot:
    """Genesis-built app responds when backing services are available."""

    def test_genesis_client_health(self, genesis_client):
        """genesis_client (TestClient on Genesis app) returns 200 on /health when pre-boot passed."""
        response = genesis_client.get("/health")
        assert response.status_code == 200
