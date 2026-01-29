#!/usr/bin/env python3
"""
Probe container health checks from the host.

Run after `docker-compose up -d`. Verifies that each service is reachable
and responds the way the compose healthchecks expect—so we know "healthy"
means actually usable, not just "port open" or "TCP up".

Usage:
  python scripts/probe_health_checks.py
  # Or from repo root with env loaded:
  set -a && source .env.secrets 2>/dev/null; source config/development.env 2>/dev/null; set +a
  python scripts/probe_health_checks.py

Exits 0 if all probes pass, 1 otherwise. Reads host/ports from env
(REDIS_URL, ARANGO_URL, ARANGO_ROOT_PASSWORD, CONSUL_HOST, CONSUL_PORT,
MEILISEARCH_HOST, MEILISEARCH_PORT, RUNTIME_PORT, EXPERIENCE_PORT).
"""

from __future__ import annotations

import os
import sys
import urllib.error
import urllib.request
from typing import Callable

# Optional: load .env.secrets and config/development.env if python-dotenv present
try:
    from dotenv import load_dotenv
    load_dotenv(".env.secrets")
    load_dotenv("config/development.env")
    load_dotenv(".env")
except ImportError:
    pass


def _redis_ping() -> tuple[bool, str]:
    try:
        import redis
    except ImportError:
        return False, "redis package not installed"
    url = os.environ.get("REDIS_URL", "redis://localhost:6379")
    try:
        r = redis.from_url(url, socket_connect_timeout=3)
        r.ping()
        return True, "PONG"
    except Exception as e:
        return False, str(e)


def _http_get(
    url: str,
    timeout: int = 5,
    user: str | None = None,
    password: str | None = None,
) -> tuple[bool, str]:
    req = urllib.request.Request(url)
    if user and password:
        import base64
        creds = base64.b64encode(f"{user}:{password}".encode()).decode()
        req.add_header("Authorization", f"Basic {creds}")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            code = resp.getcode()
            return code == 200, f"HTTP {code}"
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code} {e.reason}"
    except Exception as e:
        return False, str(e)


def _arango_version() -> tuple[bool, str]:
    base = os.environ.get("ARANGO_URL", "http://localhost:8529").rstrip("/")
    url = f"{base}/_api/version"
    password = os.environ.get("ARANGO_ROOT_PASSWORD") or os.environ.get("ARANGO_PASS") or "test_password"
    ok, msg = _http_get(url, user="root", password=password)
    return ok, msg


def _consul_leader() -> tuple[bool, str]:
    host = os.environ.get("CONSUL_HOST", "localhost")
    port = os.environ.get("CONSUL_PORT", "8500")
    url = f"http://{host}:{port}/v1/status/leader"
    return _http_get(url)


def _meilisearch_health() -> tuple[bool, str]:
    host = os.environ.get("MEILISEARCH_HOST", "localhost")
    port = os.environ.get("MEILISEARCH_PORT", "7700")
    url = f"http://{host}:{port}/health"
    return _http_get(url)


def _runtime_health() -> tuple[bool, str]:
    port = os.environ.get("RUNTIME_PORT", "8000")
    url = f"http://localhost:{port}/health"
    try:
        with urllib.request.urlopen(urllib.request.Request(url), timeout=5) as resp:
            if resp.getcode() != 200:
                return False, f"HTTP {resp.getcode()}"
            body = resp.read().decode()
            if "healthy" not in body.lower():
                return False, f"body missing 'healthy': {body[:80]}"
            return True, "HTTP 200 + healthy"
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code} {e.reason}"
    except Exception as e:
        return False, str(e)


def _experience_health() -> tuple[bool, str]:
    port = os.environ.get("EXPERIENCE_PORT", "8001")
    url = f"http://localhost:{port}/health"
    return _http_get(url)


def main() -> int:
    probes: list[tuple[str, Callable[[], tuple[bool, str]]]] = [
        ("Redis", _redis_ping),
        ("Arango (HTTP + auth)", _arango_version),
        ("Consul", _consul_leader),
        ("Meilisearch", _meilisearch_health),
        ("Runtime /health", _runtime_health),
        ("Experience /health", _experience_health),
    ]
    failed = []
    for name, fn in probes:
        ok, msg = fn()
        status = "OK" if ok else "FAIL"
        print(f"  {status}  {name}: {msg}")
        if not ok:
            failed.append(name)
    if failed:
        print("\nProbe failed:", ", ".join(failed))
        return 1
    print("\nAll health-check probes passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
