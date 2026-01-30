"""
Layer 2: Pre-boot validation.

Consumes only the canonical config from Layer 1. For each required backing
service (Redis, Arango, Consul, Supabase, GCS, Meilisearch, DuckDB), runs
a minimal connectivity/readiness check. When configured, Telemetry (OTLP)
is validated. No Public Works or adapters.
On first failure: exit with a clear, actionable message.

Aligned with PLATFORM_CONTRACT §5 (pre-boot validation).
"""

import json
import os
import socket
import sys
from typing import Any, Dict
from urllib.parse import urlparse

# Optional: use get_logger from utilities if available
try:
    from utilities import get_logger
except ImportError:
    def get_logger(name: str):
        import logging
        return logging.getLogger(name)

logger = get_logger("bootstrap.pre_boot")

# Last pre-boot result (set after pre_boot_validate succeeds). Used by Control Room for infrastructure health.
_last_pre_boot_result: Dict[str, Any] = {}


def get_pre_boot_status() -> Dict[str, Any]:
    """
    Return the last pre-boot validation result for use by Control Room / genesis status.
    Keys: status ("passed" | "not_run"), services_validated (list), telemetry ("checked" | "skipped").
    """
    return dict(_last_pre_boot_result)


def _fail(service: str, reason: str, hint: str) -> None:
    """Exit immediately with a clear message."""
    msg = (
        f"Platform contract violation: {service} failed: {reason}. "
        f"{hint}"
    )
    logger.error(msg)
    sys.exit(1)


def _check_redis(config: Dict[str, Any]) -> None:
    """Redis: connect and ping."""
    redis_cfg = config.get("redis") or {}
    host = redis_cfg.get("host", "localhost")
    port = int(redis_cfg.get("port", 6379))
    password = redis_cfg.get("password")
    db = int(redis_cfg.get("db", 0))
    try:
        import redis
        client = redis.Redis(
            host=host,
            port=port,
            password=password,
            db=db,
            socket_connect_timeout=5,
            decode_responses=True,
        )
        client.ping()
        client.close()
    except ImportError as e:
        _fail("Redis", f"redis client not available: {e}", "Install: pip install redis")
    except Exception as e:
        _fail(
            "Redis",
            str(e),
            "Check REDIS_URL (or redis host/port/password) and that Redis is reachable.",
        )


def _check_arango(config: Dict[str, Any]) -> None:
    """ArangoDB: connect and authorize (no 401)."""
    url = config.get("arango_url") or "http://localhost:8529"
    username = config.get("arango_username") or "root"
    password = config.get("arango_password") or ""
    database = config.get("arango_database") or "symphainy_platform"
    try:
        from arango import ArangoClient
        client = ArangoClient(hosts=url)
        db = client.db(name=database, username=username, password=password)
        # Trigger auth and connectivity
        db.version()
    except ImportError as e:
        _fail("ArangoDB", f"python-arango not available: {e}", "Install: pip install python-arango")
    except Exception as e:
        hint = (
            "Check ARANGO_URL, ARANGO_USER (or ARANGO_USERNAME), ARANGO_DB (or ARANGO_DATABASE), "
            "ARANGO_PASS or ARANGO_ROOT_PASSWORD (blank password is valid)."
        )
        if "401" in str(e) or "Unauthorized" in str(e):
            hint = "Check ARANGO_PASS or ARANGO_ROOT_PASSWORD (blank is valid); ensure user is authorized."
        _fail("ArangoDB", str(e), hint)


def _check_consul(config: Dict[str, Any]) -> None:
    """Consul: reachable (e.g. agent.self())."""
    consul_cfg = config.get("consul") or {}
    host = consul_cfg.get("host", "localhost")
    port = int(consul_cfg.get("port", 8500))
    token = consul_cfg.get("token")
    try:
        from consul import Consul
        c = Consul(host=host, port=port, token=token)
        c.agent.self()
    except ImportError as e:
        _fail("Consul", f"python-consul not available: {e}", "Install: pip install python-consul")
    except Exception as e:
        _fail(
            "Consul",
            str(e),
            "Check CONSUL_HOST, CONSUL_PORT and that Consul is reachable.",
        )


def _check_supabase(config: Dict[str, Any]) -> None:
    """Supabase: reachable (minimal REST call)."""
    url = (config.get("supabase_url") or "").rstrip("/")
    service_key = config.get("supabase_service_key")
    if not url:
        _fail("Supabase", "supabase_url is missing", "Set SUPABASE_URL.")
    if not service_key:
        _fail("Supabase", "supabase_service_key is missing", "Set SUPABASE_SERVICE_KEY (or SUPABASE_SECRET_KEY).")
    try:
        import httpx
        # Health / REST availability: GET rest/v1/ with apikey
        resp = httpx.get(
            f"{url}/rest/v1/",
            headers={"apikey": service_key, "Authorization": f"Bearer {service_key}"},
            timeout=10.0,
        )
        # 200 or 404 on root is fine; 401/403 means bad key
        if resp.status_code in (401, 403):
            _fail("Supabase", f"auth failed (status {resp.status_code})", "Check SUPABASE_SERVICE_KEY.")
        if resp.status_code >= 500:
            _fail("Supabase", f"server error (status {resp.status_code})", "Check Supabase project health.")
    except ImportError:
        _fail("Supabase", "httpx not available", "Install: pip install httpx")
    except Exception as e:
        _fail("Supabase", str(e), "Check SUPABASE_URL and network reachability.")


def _check_gcs(config: Dict[str, Any]) -> None:
    """GCS: bucket exists and credentials valid."""
    project_id = config.get("gcs_project_id")
    bucket_name = config.get("gcs_bucket_name")
    credentials_json = config.get("gcs_credentials_json")
    if not project_id:
        _fail("GCS", "gcs_project_id is missing", "Set GCS_PROJECT_ID.")
    if not bucket_name:
        _fail("GCS", "gcs_bucket_name is missing", "Set GCS_BUCKET_NAME.")
    try:
        from google.cloud import storage
        from google.oauth2 import service_account
        if credentials_json:
            creds = service_account.Credentials.from_service_account_info(
                json.loads(credentials_json)
            )
            client = storage.Client(project=project_id, credentials=creds)
        else:
            client = storage.Client(project=project_id)
        bucket = client.bucket(bucket_name)
        # Trigger auth and bucket access (head or list with max_results=1)
        bucket.reload()
    except ImportError as e:
        _fail("GCS", f"google-cloud-storage not available: {e}", "Install: pip install google-cloud-storage google-auth")
    except Exception as e:
        _fail(
            "GCS",
            str(e),
            "Check GCS_PROJECT_ID, GCS_BUCKET_NAME, GCS_CREDENTIALS_JSON and network.",
        )


def _check_meilisearch(config: Dict[str, Any]) -> None:
    """Meilisearch: reachable (health endpoint)."""
    host = config.get("meilisearch_host") or "meilisearch"
    port = int(config.get("meilisearch_port", 7700))
    key = config.get("meilisearch_key")
    url = f"http://{host}:{port}/health"
    try:
        import httpx
        headers = {}
        if key:
            headers["Authorization"] = f"Bearer {key}"
        resp = httpx.get(url, headers=headers, timeout=5.0)
        if resp.status_code == 401:
            _fail("Meilisearch", "unauthorized (check MEILI_MASTER_KEY)", "Set MEILI_MASTER_KEY if required.")
        if resp.status_code >= 500:
            _fail("Meilisearch", f"server error (status {resp.status_code})", "Check Meilisearch is running.")
    except ImportError:
        _fail("Meilisearch", "httpx not available", "Install: pip install httpx")
    except Exception as e:
        _fail("Meilisearch", str(e), "Check MEILISEARCH_HOST, MEILISEARCH_PORT and that Meilisearch is reachable.")


def _check_duckdb(config: Dict[str, Any]) -> None:
    """DuckDB: database path writable/readable (or parent writable for create)."""
    duck_cfg = config.get("duckdb") or {}
    path = duck_cfg.get("database_path", "/app/data/duckdb/main.duckdb")
    read_only = duck_cfg.get("read_only", False)
    try:
        import duckdb
        if read_only:
            if not os.path.isfile(path):
                _fail("DuckDB", f"read_only but database file does not exist: {path}", "Create DB or set DUCKDB_READ_ONLY=0.")
            conn = duckdb.connect(path, read_only=True)
        else:
            parent = os.path.dirname(path)
            if parent and not os.path.exists(parent):
                try:
                    os.makedirs(parent, exist_ok=True)
                except OSError as e:
                    _fail("DuckDB", f"cannot create directory for DB: {e}", f"Ensure parent of {path} is writable.")
            conn = duckdb.connect(path)
        conn.execute("SELECT 1").fetchone()
        conn.close()
    except ImportError as e:
        _fail("DuckDB", f"duckdb not available: {e}", "Install: pip install duckdb")
    except Exception as e:
        _fail("DuckDB", str(e), "Check DUCKDB_DATABASE_PATH and filesystem permissions.")


def _check_telemetry(config: Dict[str, Any]) -> str:
    """
    Telemetry (OpenTelemetry OTLP): required; validate endpoint reachability.
    Minimal check: TCP connect to OTLP endpoint host:port (default 4317 for gRPC).
    Boot fails if endpoint is missing or unreachable.
    """
    endpoint = config.get("otel_exporter_otlp_endpoint") or (config.get("telemetry") or {}).get("otlp_endpoint")
    if not endpoint:
        _fail(
            "Telemetry",
            "otel_exporter_otlp_endpoint is missing",
            "Set OTEL_EXPORTER_OTLP_ENDPOINT (e.g. http://localhost:4317) or add telemetry.otlp_endpoint to config.",
        )
    try:
        parsed = urlparse(endpoint)
        host = parsed.hostname or "localhost"
        port = parsed.port
        if port is None:
            port = 4317 if parsed.scheme in ("http", "https") else 4317
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((host, port))
        sock.close()
    except socket.gaierror as e:
        _fail(
            "Telemetry",
            f"OTLP endpoint host unreachable: {e}",
            f"Check OTEL_EXPORTER_OTLP_ENDPOINT ({endpoint}) and that the OTLP collector is running.",
        )
    except (OSError, socket.error) as e:
        _fail(
            "Telemetry",
            str(e),
            f"Check OTEL_EXPORTER_OTLP_ENDPOINT ({endpoint}) and that the OTLP collector is reachable on port {port}.",
        )
    return "checked"


def pre_boot_validate(config: Dict[str, Any]) -> None:
    """
    Run pre-boot validation for all required backing services (Gate G3).

    Uses only the canonical config. Order: Data Plane (Redis, Arango, Supabase,
    GCS, Meilisearch, DuckDB) then Control Plane (Consul). On first failure,
    exits the process with a clear message.
    """
    logger.info("Pre-boot validation: checking required backing services...")
    # Data plane first (per PRE_BOOT_SPEC / HYBRID_CLOUD_VISION)
    _check_redis(config)
    _check_arango(config)
    _check_supabase(config)
    _check_gcs(config)
    _check_meilisearch(config)
    _check_duckdb(config)
    # Control plane
    _check_consul(config)
    # Telemetry (required)
    _check_telemetry(config)
    # Store result for Control Room / genesis status
    global _last_pre_boot_result
    _last_pre_boot_result = {
        "status": "passed",
        "services_validated": ["redis", "arango", "supabase", "gcs", "meilisearch", "duckdb", "consul", "telemetry"],
        "telemetry": "checked",
    }
    logger.info("Pre-boot validation: all required services passed.")
