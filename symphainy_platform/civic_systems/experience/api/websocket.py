"""
WebSocket API Endpoints - Real-time Execution Streaming
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[6]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Any

from utilities import get_logger
from ..sdk.runtime_client import RuntimeClient


router = APIRouter(prefix="/api/execution", tags=["websocket"])
logger = get_logger("ExperienceAPI.WebSocket")


def get_runtime_client() -> RuntimeClient:
    """Dependency to get Runtime client."""
    return RuntimeClient(runtime_url="http://runtime:8000")


@router.websocket("/{execution_id}/stream")
async def stream_execution(
    websocket: WebSocket,
    execution_id: str,
    runtime_client: RuntimeClient = Depends(get_runtime_client)
):
    """
    Stream execution updates via WebSocket.
    
    Flow:
    1. Accept WebSocket connection
    2. Subscribe to execution events from Runtime
    3. Stream events to client
    4. Handle disconnection
    """
    await websocket.accept()
    logger.info(f"WebSocket connection established for execution: {execution_id}")
    
    try:
        # Subscribe to execution events (via Runtime WebSocket)
        async for event in runtime_client.stream_execution(execution_id):
            await websocket.send_json(event)
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for execution: {execution_id}")
    except Exception as e:
        logger.error(f"WebSocket error for execution {execution_id}: {e}", exc_info=True)
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass
