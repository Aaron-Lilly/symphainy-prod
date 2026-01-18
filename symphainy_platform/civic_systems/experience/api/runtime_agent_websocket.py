"""
Runtime Agent WebSocket - Experience Plane Endpoint

Experience Plane owns /api/runtime/agent WebSocket endpoint.
Runtime owns agent execution, state, and orchestration.

The endpoint name is a contract, not a locator.

Architecture:
- Experience Plane = Intent + Context Boundary
  * User-facing
  * Knows who is talking, why, and in what mode
  * Decides which agent should respond
  * Owns conversation semantics

- Runtime = Execution Engine
  * Stateless or minimally stateful
  * Does not know "users"
  * Does not route based on UX intent
  * Executes agents when told, returns results/events
"""
import sys
from pathlib import Path

# Add project root to path
current = Path(__file__).resolve()
project_root = current
for _ in range(10):
    if (project_root / "pyproject.toml").exists() or (project_root / "requirements.txt").exists():
        break
    project_root = project_root.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import json
import uuid
from typing import Dict, Any, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Request
from utilities import get_logger
from ..sdk.runtime_client import RuntimeClient
from ..services.guide_agent_service import GuideAgentService
from ..services.websocket_connection_manager import WebSocketConnectionManager
from symphainy_platform.civic_systems.smart_city.sdk.security_guard_sdk import SecurityGuardSDK
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.runtime.state_surface import StateSurface


router = APIRouter(prefix="/api/runtime", tags=["runtime", "websocket", "agents"])
logger = get_logger("ExperienceAPI.RuntimeAgentWebSocket")


def get_runtime_client(request: Request) -> RuntimeClient:
    """Dependency to get Runtime client."""
    if hasattr(request.app.state, "runtime_client"):
        return request.app.state.runtime_client
    return RuntimeClient(runtime_url="http://runtime:8000")


def get_security_guard_sdk(request: Request) -> SecurityGuardSDK:
    """Dependency to get Security Guard SDK."""
    if not hasattr(request.app.state, "security_guard_sdk"):
        raise RuntimeError("Security Guard SDK not initialized.")
    return request.app.state.security_guard_sdk


def get_guide_agent_service(request: Request) -> GuideAgentService:
    """Dependency to get Guide Agent Service."""
    if not hasattr(request.app.state, "guide_agent_service"):
        raise RuntimeError("Guide Agent Service not initialized.")
    return request.app.state.guide_agent_service


@router.websocket("/agent")
async def runtime_agent_websocket(
    websocket: WebSocket,
    session_token: Optional[str] = Query(None, description="Session token for authentication")
):
    """
    Runtime Agent WebSocket endpoint - owned by Experience Plane.
    
    This endpoint is owned by Experience Plane, even though the path says "runtime".
    The path is a contract (invoke runtime on my behalf), not a locator.
    
    Flow:
    1. Authenticate WebSocket connection
    2. Accept connection
    3. Receive agent messages
    4. Experience Plane routes to appropriate agent (guide vs liaison)
    5. Experience Plane invokes Runtime for agent execution
    6. Runtime executes agent and emits events
    7. Experience Plane streams events back to client
    
    Message Format (Client → Experience Plane):
    {
        "type": "agent.message",
        "payload": {
            "text": "user message",
            "context": {
                "surface": "content_pillar" | "insights_pillar" | "journey_pillar" | "outcomes_pillar",
                "project_id": "optional",
                "conversation_id": "optional"
            }
        }
    }
    
    Response Format (Experience Plane → Client):
    {
        "type": "runtime_event",
        "event_type": "agent.started" | "agent.token" | "agent.completed" | "agent.failed",
        "data": {...},
        "timestamp": "ISO timestamp"
    }
    """
    # CRITICAL: Authenticate BEFORE accepting connection to prevent resource exhaustion
    if not session_token:
        await websocket.close(code=1008, reason="Session token required")
        return
    
    # Get dependencies from app state
    # In FastAPI WebSocket, access app via websocket.app
    app = websocket.app
    if not app or not hasattr(app, 'state'):
        await websocket.close(code=1011, reason="Internal server error: app state not available")
        return
    
    try:
        # Get Security Guard SDK for authentication
        if not hasattr(app.state, "security_guard_sdk"):
            await websocket.close(code=1011, reason="Security Guard SDK not initialized")
            return
        
        security_guard = app.state.security_guard_sdk
        
        # Validate session token BEFORE accepting connection
        auth_result = await security_guard.validate_token(session_token)
        if not auth_result:
            await websocket.close(code=1008, reason="Invalid session token")
            return
        
        user_id = auth_result.user_id
        tenant_id = auth_result.tenant_id
        session_id = session_token  # Use token as session ID for now
        
        # Get connection manager (create if not exists)
        if not hasattr(app.state, "websocket_connection_manager"):
            app.state.websocket_connection_manager = WebSocketConnectionManager(max_connections=1000)
        
        connection_manager = app.state.websocket_connection_manager
        connection_id = str(uuid.uuid4())
        
        # NOW accept connection (after authentication)
        await websocket.accept()
        
        # Register connection with connection manager
        if not await connection_manager.connect(websocket, connection_id, user_id, tenant_id, session_token):
            # Connection rejected (at capacity)
            return
        
        logger.info(f"Authenticated WebSocket connection: {connection_id} (user: {user_id}, tenant: {tenant_id})")
        
        # Get Runtime client and Guide Agent Service
        if not hasattr(app.state, "runtime_client"):
            connection_manager.disconnect(connection_id)
            await websocket.close(code=1011, reason="Runtime client not initialized")
            return
        
        if not hasattr(app.state, "guide_agent_service"):
            connection_manager.disconnect(connection_id)
            await websocket.close(code=1011, reason="Guide Agent Service not initialized")
            return
        
        runtime_client = app.state.runtime_client
        guide_service = app.state.guide_agent_service
        
        # Get State Surface for persistent conversation context storage
        state_surface = None
        if hasattr(app.state, "public_works") and app.state.public_works:
            state_abstraction = app.state.public_works.get_state_abstraction()
            if state_abstraction:
                state_surface = StateSurface(
                    state_abstraction=state_abstraction,
                    use_memory=(state_abstraction is None)
                )
        
        # Main message loop
        while True:
            try:
                # Receive message from client
                message_data = await websocket.receive_text()
                message = json.loads(message_data)
                
                message_type = message.get("type")
                payload = message.get("payload", {})
                
                if message_type != "agent.message":
                    await websocket.send_json({
                        "type": "error",
                        "error": f"Unknown message type: {message_type}",
                        "timestamp": __import__("datetime").datetime.utcnow().isoformat()
                    })
                    continue
                
                # Update connection activity
                connection_manager.update_activity(connection_id)
                
                # Extract context
                context = payload.get("context", {})
                surface = context.get("surface", "general")
                conversation_id = context.get("conversation_id") or f"{surface}_{session_id}"
                user_text = payload.get("text", "")
                
                # Get conversation context from persistent storage
                conv_context = await _get_conversation_context(
                    conversation_id=conversation_id,
                    state_surface=state_surface,
                    tenant_id=tenant_id,
                    surface=surface
                )
                
                # Experience Plane: Determine agent routing
                # This is the semantic decision that belongs in Experience Plane
                agent_type, agent_id = await _determine_agent_routing(
                    surface=surface,
                    user_text=user_text,
                    conversation_context=conv_context,
                    guide_service=guide_service,
                    session_id=session_id,
                    tenant_id=tenant_id
                )
                
                conv_context["agent_type"] = agent_type
                conv_context["agent_id"] = agent_id
                conv_context["messages"].append({
                    "role": "user",
                    "text": user_text,
                    "timestamp": __import__("datetime").datetime.utcnow().isoformat()
                })
                
                logger.info(f"Routing message to agent: {agent_id} (type: {agent_type}, surface: {surface})")
                
                # Emit agent.started event
                await websocket.send_json({
                    "type": "runtime_event",
                    "event_type": "agent.started",
                    "data": {
                        "agent_id": agent_id,
                        "agent_type": agent_type,
                        "conversation_id": conversation_id
                    },
                    "timestamp": __import__("datetime").datetime.utcnow().isoformat()
                })
                
                # Experience Plane: Construct runtime invocation request
                invocation_request = {
                    "agent_id": agent_id,
                    "invocation_id": str(uuid.uuid4()),
                    "input": {
                        "text": user_text,
                        "conversation_id": conversation_id,
                        "context": context
                    },
                    "session_id": session_id,
                    "tenant_id": tenant_id,
                    "user_id": user_id
                }
                
                # Experience Plane: Invoke Runtime for agent execution
                # Runtime executes agent and emits events
                # For MVP, we'll use Runtime Client to submit intent
                # In production, this would be async invocation with event streaming
                
                if agent_type == "guide":
                    # Guide agent: Use Guide Agent Service
                    exec_context = ExecutionContext(
                        state={},
                        session_id=session_id,
                        orchestrator_context={},
                        memory=None,
                        tools=None,
                        observability=None,
                        events=[],
                        execution_id=f"exec_{session_id}_{__import__('time').time()}",
                        started_at=__import__("datetime").datetime.utcnow(),
                        updated_at=__import__("datetime").datetime.utcnow()
                    )
                    
                    result = await guide_service.process_chat_message(
                        message=user_text,
                        session_id=session_id,
                        tenant_id=tenant_id,
                        context=exec_context
                    )
                    
                    # Stream response back
                    if result.get("success"):
                        response_text = result.get("response", "")
                        
                        # Emit agent.token events (streaming tokens)
                        # For MVP, send complete response
                        await websocket.send_json({
                            "type": "runtime_event",
                            "event_type": "agent.token",
                            "data": {
                                "agent_id": agent_id,
                                "token": response_text,
                                "conversation_id": conversation_id
                            },
                            "timestamp": __import__("datetime").datetime.utcnow().isoformat()
                        })
                        
                        # Emit agent.completed event
                        await websocket.send_json({
                            "type": "runtime_event",
                            "event_type": "agent.completed",
                            "data": {
                                "agent_id": agent_id,
                                "conversation_id": conversation_id,
                                "response": response_text
                            },
                            "timestamp": __import__("datetime").datetime.utcnow().isoformat()
                        })
                        
                        conv_context["messages"].append({
                            "role": "assistant",
                            "text": response_text,
                            "timestamp": __import__("datetime").datetime.utcnow().isoformat()
                        })
                        
                        # Save conversation context to persistent storage
                        await _save_conversation_context(
                            conversation_id=conversation_id,
                            context=conv_context,
                            state_surface=state_surface,
                            tenant_id=tenant_id
                        )
                    else:
                        await websocket.send_json({
                            "type": "runtime_event",
                            "event_type": "agent.failed",
                            "data": {
                                "agent_id": agent_id,
                                "conversation_id": conversation_id,
                                "error": result.get("error", "Unknown error")
                            },
                            "timestamp": __import__("datetime").datetime.utcnow().isoformat()
                        })
                
                elif agent_type == "liaison":
                    # Liaison agent: Invoke via Runtime
                    # For MVP, submit intent to Runtime
                    # In production, this would be direct agent invocation
                    
                    intent = __import__("symphainy_platform.runtime.intent_model").IntentFactory.create_intent(
                        intent_type="agent_invoke",
                        tenant_id=tenant_id,
                        session_id=session_id,
                        solution_id="default",
                        parameters={
                            "agent_id": agent_id,
                            "message": user_text,
                            "conversation_id": conversation_id,
                            "context": context
                        },
                        metadata={}
                    )
                    
                    execution_result = await runtime_client.submit_intent(intent)
                    
                    # For MVP, we'll stream a simple response
                    # In production, Runtime would emit events that we'd forward
                    await websocket.send_json({
                        "type": "runtime_event",
                        "event_type": "agent.completed",
                        "data": {
                            "agent_id": agent_id,
                            "conversation_id": conversation_id,
                            "execution_id": execution_result.get("execution_id"),
                            "response": "Liaison agent execution initiated"
                        },
                        "timestamp": __import__("datetime").datetime.utcnow().isoformat()
                    })
                
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "error": "Invalid JSON message",
                    "timestamp": __import__("datetime").datetime.utcnow().isoformat()
                })
            except Exception as e:
                logger.error(f"Error processing agent message: {e}", exc_info=True)
                await websocket.send_json({
                    "type": "runtime_event",
                    "event_type": "agent.failed",
                    "data": {
                        "error": str(e)
                    },
                    "timestamp": __import__("datetime").datetime.utcnow().isoformat()
                })
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for agent communication")
        # Clean up connection
        if 'connection_id' in locals():
            connection_manager.disconnect(connection_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        # Clean up connection
        if 'connection_id' in locals():
            connection_manager.disconnect(connection_id)
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except Exception:
            logger.debug("WebSocket already closed, ignoring close error")


async def _determine_agent_routing(
    surface: str,
    user_text: str,
    conversation_context: Dict[str, Any],
    guide_service: GuideAgentService,
    session_id: str,
    tenant_id: str
) -> tuple[str, str]:
    """
    Determine agent routing - Experience Plane responsibility.
    
    This is the semantic decision that belongs in Experience Plane:
    - Guide vs Liaison is a semantic distinction, not technical
    - Depends on UI surface, conversation state, user role, etc.
    
    Args:
        surface: UI surface (content_pillar, insights_pillar, etc.)
        user_text: User's message
        conversation_context: Current conversation context
        guide_service: Guide Agent Service
        session_id: Session ID
        tenant_id: Tenant ID
    
    Returns:
        Tuple of (agent_type, agent_id)
        agent_type: "guide" or "liaison"
        agent_id: Specific agent identifier (e.g., "guide.content", "liaison.data")
    """
    # If conversation already has an agent, use it
    if conversation_context.get("agent_id"):
        return (
            conversation_context.get("agent_type", "guide"),
            conversation_context.get("agent_id")
        )
    
    # Determine agent based on surface and context
    # For MVP, simple routing:
    # - If surface is specific pillar → liaison agent for that pillar
    # - Otherwise → guide agent
    
    if surface in ["content_pillar", "insights_pillar", "journey_pillar", "outcomes_pillar"]:
        # Map surface to liaison agent
        pillar_map = {
            "content_pillar": "content",
            "insights_pillar": "insights",
            "journey_pillar": "journey",
            "outcomes_pillar": "outcomes"
        }
        pillar = pillar_map.get(surface, "content")
        return ("liaison", f"liaison.{pillar}")
    else:
        # Default to guide agent
        return ("guide", "guide.content")


async def _get_conversation_context(
    conversation_id: str,
    state_surface: Optional[StateSurface],
    tenant_id: str,
    surface: str
) -> Dict[str, Any]:
    """
    Get conversation context from persistent storage.
    
    Args:
        conversation_id: Conversation identifier
        state_surface: State Surface for persistent storage
        tenant_id: Tenant identifier
        surface: UI surface
    
    Returns:
        Conversation context dictionary
    """
    # Default context
    default_context = {
        "surface": surface,
        "messages": [],
        "agent_type": None,
        "agent_id": None
    }
    
    # Try to load from persistent storage
    if state_surface:
        try:
            session_state = await state_surface.get_session_state(
                conversation_id,
                tenant_id
            )
            if session_state and "conversation_context" in session_state:
                return session_state["conversation_context"]
        except Exception as e:
            logger.warning(f"Failed to load conversation context: {e}")
    
    return default_context


async def _save_conversation_context(
    conversation_id: str,
    context: Dict[str, Any],
    state_surface: Optional[StateSurface],
    tenant_id: str
):
    """
    Save conversation context to persistent storage.
    
    Args:
        conversation_id: Conversation identifier
        context: Conversation context dictionary
        state_surface: State Surface for persistent storage
        tenant_id: Tenant identifier
    """
    if not state_surface:
        return
    
    try:
        # Get existing session state
        session_state = await state_surface.get_session_state(
            conversation_id,
            tenant_id
        ) or {}
        
        # Update conversation context
        session_state["conversation_context"] = context
        
        # Save to persistent storage
        await state_surface.set_session_state(
            conversation_id,
            tenant_id,
            session_state
        )
    except Exception as e:
        logger.warning(f"Failed to save conversation context: {e}")

