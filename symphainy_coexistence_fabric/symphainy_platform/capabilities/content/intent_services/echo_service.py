"""
Echo Intent Service - Test Service for Platform SDK Wiring

A simple test service that validates the PlatformContext (ctx) wiring.
This service echoes back information about the context it receives.

Intent Type: echo
Parameters:
    - message: str - Message to echo back

Returns:
    artifacts:
        echo:
            result_type: "echo"
            semantic_payload:
                message: The echoed message
                ctx_info: Information about the PlatformContext
            renderings: {}
"""

from typing import Dict, Any, Optional

from symphainy_platform.civic_systems.platform_sdk import PlatformIntentService, PlatformContext


class EchoService(PlatformIntentService):
    """
    Echo Intent Service.
    
    Test service to validate PlatformContext wiring.
    Echoes back the message and context information.
    """
    
    intent_type = "echo"
    
    def __init__(self, service_id: Optional[str] = None):
        """
        Initialize Echo Service.
        
        Args:
            service_id: Optional service identifier
        """
        super().__init__(
            service_id=service_id or "echo_service",
            intent_type="echo"
        )
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """
        Execute the echo intent.
        
        Args:
            ctx: PlatformContext with full platform access
        
        Returns:
            Execution result with echo artifact
        """
        self.logger.info(f"🔊 EchoService executing with PlatformContext")
        
        # Get message from intent parameters
        message = ctx.intent.parameters.get("message", "Hello from PlatformContext!")
        
        # Build context info to demonstrate what's available
        ctx_info = {
            "execution_id": ctx.execution_id,
            "tenant_id": ctx.tenant_id,
            "session_id": ctx.session_id,
            "solution_id": ctx.solution_id,
            "intent_type": ctx.intent.intent_type,
            "has_state_surface": ctx.state_surface is not None,
            "has_wal": ctx.wal is not None,
            "has_artifacts": ctx.artifacts is not None,
            "has_platform_service": ctx.platform is not None,
            "has_governance_service": ctx.governance is not None,
            "has_reasoning_service": ctx.reasoning is not None,
        }
        
        # Record telemetry
        await self.record_telemetry(ctx, {
            "action": "echo",
            "message_length": len(message),
            "ctx_services_available": sum([
                ctx.platform is not None,
                ctx.governance is not None,
                ctx.reasoning is not None,
            ])
        })
        
        self.logger.info(f"🔊 Echo: {message}")
        self.logger.info(f"🔊 Context info: {ctx_info}")
        
        # Return structured artifact
        return {
            "artifacts": {
                "echo": {
                    "result_type": "echo",
                    "semantic_payload": {
                        "message": message,
                        "original_intent_type": ctx.intent.intent_type,
                        "ctx_info": ctx_info,
                        "timestamp": self.clock.now_iso()
                    },
                    "renderings": {
                        "text": f"Echo: {message}"
                    }
                }
            },
            "events": [
                {
                    "event_type": "echo_completed",
                    "event_data": {
                        "message": message,
                        "execution_id": ctx.execution_id
                    }
                }
            ]
        }
