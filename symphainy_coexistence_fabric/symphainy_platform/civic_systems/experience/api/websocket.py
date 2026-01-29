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

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Any, Optional

from utilities import get_logger
from ..sdk.runtime_client import RuntimeClient
from ..sdk.experience_sdk import ExperienceSDK


router = APIRouter(prefix="/api/execution", tags=["websocket"])
logger = get_logger("ExperienceAPI.WebSocket")


def get_runtime_client() -> RuntimeClient:
    """Dependency to get Runtime client."""
    return RuntimeClient(runtime_url="http://runtime:8000")


def get_experience_sdk(runtime_client: RuntimeClient = Depends(get_runtime_client)) -> ExperienceSDK:
    """Dependency to get Experience SDK."""
    return ExperienceSDK(runtime_client)


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

    try:
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
