"""
Generate SOP From Chat Intent Service

Implements the generate_sop_from_chat intent for the Operations Realm.

Contract: docs/intent_contracts/journey_sop_management/intent_generate_sop_from_chat.md

Purpose: Start interactive SOP generation session via chat with Journey Liaison Agent.

WHAT (Intent Service Role): I initiate interactive SOP generation sessions
HOW (Intent Service Implementation): I create a chat session for SOP generation
    and return initial context for the conversation

Naming Convention:
- Realm: Operations Realm
- Artifacts: operations_sop_chat_session
- Solution = platform construct (OperationsSolution)
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from utilities import generate_event_id


class GenerateSOPFromChatService(BaseIntentService):
    """
    Intent service for interactive SOP generation.
    
    Initiates chat session with:
    - Session context
    - Initial prompts
    - SOP template structure
    """
    
    def __init__(self, public_works, state_surface):
        """Initialize GenerateSOPFromChatService."""
        super().__init__(
            service_id="generate_sop_from_chat_service",
            intent_type="generate_sop_from_chat",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the generate_sop_from_chat intent."""
        await self.record_telemetry(
            telemetry_data={"action": "execute", "status": "started", "intent_type": self.intent_type},
            tenant_id=context.tenant_id
        )
        
        try:
            intent_params = context.intent.parameters or {} if context.intent else {}
            if params:
                intent_params = {**intent_params, **params}
            
            sop_topic = intent_params.get("sop_topic", "New Standard Operating Procedure")
            initial_context = intent_params.get("initial_context", {})
            
            # Create chat session
            chat_session_id = f"sop_chat_{generate_event_id()}"
            
            # Initialize SOP draft
            sop_draft = {
                "title": sop_topic,
                "purpose": "",
                "scope": "",
                "procedure_steps": [],
                "roles": [],
                "status": "draft"
            }
            
            # Generate initial message
            initial_message = self._generate_initial_message(sop_topic)
            
            # Build session data
            session = {
                "chat_session_id": chat_session_id,
                "sop_topic": sop_topic,
                "sop_draft": sop_draft,
                "conversation_history": [
                    {
                        "role": "assistant",
                        "content": initial_message,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                ],
                "current_stage": "purpose",
                "stages_completed": [],
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Store session in state surface
            if context.state_surface:
                try:
                    await context.state_surface.set_execution_state(
                        key=f"sop_chat_session_{chat_session_id}",
                        state=session,
                        tenant_id=context.tenant_id
                    )
                except Exception as e:
                    self.logger.warning(f"Could not store session: {e}")
            
            self.logger.info(f"SOP chat session started: {chat_session_id}")
            
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute", "status": "completed", "intent_type": self.intent_type,
                    "chat_session_id": chat_session_id
                },
                tenant_id=context.tenant_id
            )
            
            return {
                "artifacts": {
                    "chat_session": session,
                    "initial_message": initial_message
                },
                "events": [
                    {
                        "type": "sop_chat_session_started",
                        "chat_session_id": chat_session_id,
                        "sop_topic": sop_topic
                    }
                ]
            }
            
        except Exception as e:
            await self.record_telemetry(
                telemetry_data={"action": "execute", "status": "failed", "error": str(e)},
                tenant_id=context.tenant_id
            )
            raise
    
    def _generate_initial_message(self, sop_topic: str) -> str:
        """Generate initial assistant message."""
        return f"""Hello! I'm here to help you create a Standard Operating Procedure (SOP) for "{sop_topic}".

Let's build this SOP together step by step. I'll guide you through each section:

1. **Purpose** - Why does this procedure exist?
2. **Scope** - Who does this apply to?
3. **Procedure Steps** - What are the steps involved?
4. **Roles & Responsibilities** - Who does what?
5. **Prerequisites** - What's needed before starting?

Let's start with the **Purpose**. Can you describe why this procedure is needed and what it aims to accomplish?"""
