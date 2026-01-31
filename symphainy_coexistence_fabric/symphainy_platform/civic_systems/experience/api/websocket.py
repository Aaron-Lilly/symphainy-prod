"""
WebSocket API Endpoints - Real-time Execution Streaming
"""

import sys
from pathlib import Path

# Add project root to path
# Find project root by looking for common markers (pyproject.toml, requirements.txt, etc.)
current = Path(__file__).resolve()
project_root = current
for _ in range(10):  # Max 10 levels up
    if (project_root / "pyproject.toml").exists() or (project_root / "requirements.txt").exists():
        break
    project_root = project_root.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import asyncio
import time
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from typing import Dict, Any, Optional

from utilities import get_logger
from ..sdk.runtime_client import RuntimeClient
from ..sdk.experience_sdk import ExperienceSDK

# Keepalive: send ping so long-idle connections (user leaves tab open) are not dropped by Traefik/client
WEBSOCKET_PING_INTERVAL_SEC = 30


router = APIRouter(prefix="/api/execution", tags=["execution", "websocket"])
logger = get_logger("ExperienceAPI.WebSocket")


def get_runtime_client() -> RuntimeClient:
    """Dependency to get Runtime client."""
    return RuntimeClient(runtime_url="http://runtime:8000")


def get_experience_sdk(runtime_client: RuntimeClient = Depends(get_runtime_client)) -> ExperienceSDK:
    """Dependency to get Experience SDK."""
    return ExperienceSDK(runtime_client)


@router.get("/{execution_id}/status")
async def get_execution_status_proxy(
    execution_id: str,
    tenant_id: str = Query(..., description="Tenant ID"),
    include_artifacts: bool = False,
    include_visuals: bool = False,
    runtime_client: RuntimeClient = Depends(get_runtime_client),
) -> Dict[str, Any]:
    """
    Proxy GET /api/execution/{id}/status to Runtime.
    Required when Traefik routes all /api/execution to Experience so that
    execution status (REST) and execution stream (WebSocket) are on one host.
    """
    return await runtime_client.get_execution_status(
        execution_id=execution_id,
        tenant_id=tenant_id,
        include_artifacts=include_artifacts,
        include_visuals=include_visuals,
    )


@router.websocket("/{execution_id}/stream")
async def stream_execution(
    websocket: WebSocket,
    execution_id: str,
    runtime_client: RuntimeClient = Depends(get_runtime_client),
    experience_sdk: ExperienceSDK = Depends(get_experience_sdk)
):
    """
    Stream execution updates via WebSocket.
    Uses Experience SDK subscribe when tenant_id in query string (enables polling fallback);
    otherwise RuntimeClient.stream_execution for backward compat.
    """
    await websocket.accept()
    tenant_id: Optional[str] = websocket.query_params.get("tenant_id") if websocket.query_params else None
    logger.info(f"WebSocket connection established for execution: {execution_id}")

    stop_heartbeat = asyncio.Event()
    heartbeat_task: Optional[asyncio.Task] = None
    try:
        heartbeat_task = asyncio.create_task(
            _heartbeat_loop(
                websocket,
                WEBSOCKET_PING_INTERVAL_SEC,
                stop_heartbeat,
                execution_id,
            )
        )
        if tenant_id:
            async for event in experience_sdk.subscribe(execution_id, tenant_id):
                await websocket.send_json(event)
        else:
            async for event in runtime_client.stream_execution(execution_id):
                await websocket.send_json(event)
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for execution: {execution_id}")
    except Exception as e:
        logger.error(f"WebSocket error for execution {execution_id}: {e}", exc_info=True)
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except Exception:
            logger.debug("WebSocket already closed, ignoring close error")
    finally:
        stop_heartbeat.set()
        if heartbeat_task and not heartbeat_task.done():
            heartbeat_task.cancel()
            try:
                await heartbeat_task
            except asyncio.CancelledError:
                pass
