#!/usr/bin/env python3
"""
Experience Service Entry Point

Runs the Experience API (auth, session, intents, etc.) on EXPERIENCE_PORT.
Uses the same config and object graph as Runtime so auth/session have
SecurityGuardSDK and TrafficCopSDK backed by Public Works abstractions.

Flow:
1. Load platform config (Gate G2)
2. Pre-boot validate (Gate G3)
3. Build runtime object graph (Public Works + state + intents)
4. Create Experience FastAPI app and attach security_guard_sdk, traffic_cop_sdk
5. Run uvicorn on EXPERIENCE_PORT (default 8001)
"""

import os
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import asyncio
import uvicorn

from symphainy_platform.bootstrap import load_platform_config, pre_boot_validate
from symphainy_platform.runtime.service_factory import create_runtime_services
from symphainy_platform.civic_systems.experience import create_app
from symphainy_platform.civic_systems.smart_city.sdk.security_guard_sdk import SecurityGuardSDK
from symphainy_platform.civic_systems.smart_city.sdk.traffic_cop_sdk import TrafficCopSDK
from utilities import get_logger

logger = get_logger("experience_main")


def main() -> None:
    logger.info("Starting Symphainy Experience Service...")

    # Gate G2: Load canonical config
    config = load_platform_config()

    # Gate G3: Pre-boot validate (same as Runtime)
    pre_boot_validate(config)

    # Build runtime object graph (same as Runtime) so we get Public Works
    logger.info("Building runtime object graph for Experience...")
    services = asyncio.run(create_runtime_services(config))

    public_works = services.public_works
    auth_abstraction = public_works.get_auth_abstraction()
    tenant_abstraction = public_works.get_tenant_abstraction()
    state_abstraction = public_works.get_state_abstraction()

    if not auth_abstraction or not state_abstraction:
        raise RuntimeError(
            "Experience requires auth and state abstractions. "
            "Public Works did not create them (check Supabase and Redis config)."
        )
    if not tenant_abstraction:
        raise RuntimeError(
            "Experience requires tenant abstraction. "
            "Public Works did not create it (check Supabase config)."
        )

    security_guard_sdk = SecurityGuardSDK(
        auth_abstraction=auth_abstraction,
        tenant_abstraction=tenant_abstraction,
    )
    traffic_cop_sdk = TrafficCopSDK(state_abstraction=state_abstraction)

    app = create_app()
    app.state.security_guard_sdk = security_guard_sdk
    app.state.traffic_cop_sdk = traffic_cop_sdk

    port = int(os.environ.get("EXPERIENCE_PORT", "8001"))
    host = "0.0.0.0"
    log_level = (config.get("log_level") or "INFO").lower()

    logger.info("Experience service ready on %s:%s", host, port)
    uvicorn.run(app, host=host, port=port, log_level=log_level)


if __name__ == "__main__":
    main()
