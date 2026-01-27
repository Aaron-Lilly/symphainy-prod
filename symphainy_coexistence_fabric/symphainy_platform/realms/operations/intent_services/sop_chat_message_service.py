"""
SOP Chat Message Intent Service

Implements the sop_chat_message intent for the Operations Realm.

Contract: docs/intent_contracts/journey_sop_management/intent_sop_chat_message.md

Purpose: Process chat message in SOP generation session. Updates SOP draft
based on conversation and advances through SOP sections.

WHAT (Intent Service Role): I process chat messages in SOP sessions
HOW (Intent Service Implementation): I analyze messages, update SOP draft,
    and generate contextual responses

Naming Convention:
- Realm: Operations Realm
- Artifacts: operations_sop_chat_session
- Solution = platform construct (OperationsSolution)
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parents[6]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from utilities import generate_event_id


class SOPChatMessageService(BaseIntentService):
    """
    Intent service for SOP chat message processing.
    
    Processes chat messages:
    - Updates SOP draft based on user input
    - Advances through SOP sections
    - Generates contextual responses
    - Completes SOP when all sections done
    """
    
    SOP_STAGES = ["purpose", "scope", "procedure_steps", "roles", "prerequisites", "complete"]
    
    def __init__(self, public_works, state_surface):
        """Initialize SOPChatMessageService."""
        super().__init__(
            service_id="sop_chat_message_service",
            intent_type="sop_chat_message",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the sop_chat_message intent."""
        await self.record_telemetry(
            telemetry_data={"action": "execute", "status": "started", "intent_type": self.intent_type},
            tenant_id=context.tenant_id
        )
        
        try:
            intent_params = context.intent.parameters or {} if context.intent else {}
            if params:
                intent_params = {**intent_params, **params}
            
            chat_session_id = intent_params.get("chat_session_id")
            user_message = intent_params.get("message")
            
            if not chat_session_id:
                raise ValueError("chat_session_id is required")
            if not user_message:
                raise ValueError("message is required")
            
            # Get session data
            session = await self._get_session(chat_session_id, context)
            if not session:
                raise ValueError(f"Session not found: {chat_session_id}")
            
            # Add user message to history
            session["conversation_history"].append({
                "role": "user",
                "content": user_message,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Process message and update SOP draft
            current_stage = session.get("current_stage", "purpose")
            sop_draft = session.get("sop_draft", {})
            
            # Update SOP based on current stage
            sop_draft = self._update_sop_draft(sop_draft, current_stage, user_message)
            
            # Generate response and determine next stage
            response, next_stage, is_complete = self._generate_response(
                current_stage, sop_draft, user_message
            )
            
            # Add assistant response to history
            session["conversation_history"].append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Update session
            if current_stage != next_stage:
                session["stages_completed"].append(current_stage)
            session["current_stage"] = next_stage
            session["sop_draft"] = sop_draft
            session["updated_at"] = datetime.utcnow().isoformat()
            
            # If complete, store final SOP
            sop_artifact_id = None
            if is_complete:
                sop_artifact_id = await self._store_completed_sop(sop_draft, context)
                session["sop_artifact_id"] = sop_artifact_id
                session["status"] = "completed"
            
            # Save session
            await self._save_session(chat_session_id, session, context)
            
            self.logger.info(f"SOP chat message processed: {chat_session_id} (stage: {next_stage})")
            
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute", "status": "completed", "intent_type": self.intent_type,
                    "chat_session_id": chat_session_id,
                    "current_stage": next_stage,
                    "is_complete": is_complete
                },
                tenant_id=context.tenant_id
            )
            
            return {
                "artifacts": {
                    "response": response,
                    "current_stage": next_stage,
                    "is_complete": is_complete,
                    "sop_draft": sop_draft,
                    "sop_artifact_id": sop_artifact_id
                },
                "events": [
                    {
                        "type": "sop_chat_message_processed",
                        "chat_session_id": chat_session_id,
                        "stage": next_stage,
                        "is_complete": is_complete
                    }
                ]
            }
            
        except Exception as e:
            await self.record_telemetry(
                telemetry_data={"action": "execute", "status": "failed", "error": str(e)},
                tenant_id=context.tenant_id
            )
            raise
    
    async def _get_session(self, chat_session_id: str, context: ExecutionContext) -> Optional[Dict[str, Any]]:
        """Get chat session from state surface."""
        if context.state_surface:
            try:
                return await context.state_surface.get_execution_state(
                    key=f"sop_chat_session_{chat_session_id}",
                    tenant_id=context.tenant_id
                )
            except Exception:
                pass
        return None
    
    async def _save_session(self, chat_session_id: str, session: Dict[str, Any], context: ExecutionContext):
        """Save chat session to state surface."""
        if context.state_surface:
            try:
                await context.state_surface.set_execution_state(
                    key=f"sop_chat_session_{chat_session_id}",
                    state=session,
                    tenant_id=context.tenant_id
                )
            except Exception as e:
                self.logger.warning(f"Could not save session: {e}")
    
    def _update_sop_draft(
        self,
        sop_draft: Dict[str, Any],
        stage: str,
        message: str
    ) -> Dict[str, Any]:
        """Update SOP draft based on current stage and user message."""
        if stage == "purpose":
            sop_draft["purpose"] = message
        elif stage == "scope":
            sop_draft["scope"] = message
        elif stage == "procedure_steps":
            # Parse steps from message
            steps = self._parse_procedure_steps(message)
            sop_draft["procedure_steps"] = steps
        elif stage == "roles":
            # Parse roles from message
            roles = self._parse_roles(message)
            sop_draft["roles"] = roles
        elif stage == "prerequisites":
            # Parse prerequisites from message
            prerequisites = self._parse_prerequisites(message)
            sop_draft["prerequisites"] = prerequisites
        
        return sop_draft
    
    def _parse_procedure_steps(self, message: str) -> List[Dict[str, Any]]:
        """Parse procedure steps from user message."""
        steps = []
        lines = message.strip().split("\n")
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line:
                # Remove numbering if present
                if line[0].isdigit() and (line[1] == "." or line[1] == ")"):
                    line = line[2:].strip()
                
                steps.append({
                    "step_number": i,
                    "title": line[:50] if len(line) > 50 else line,
                    "description": line,
                    "responsible_role": "Operator"
                })
        
        return steps if steps else [{"step_number": 1, "title": message[:50], "description": message, "responsible_role": "Operator"}]
    
    def _parse_roles(self, message: str) -> List[Dict[str, Any]]:
        """Parse roles from user message."""
        roles = []
        lines = message.strip().split("\n")
        
        for line in lines:
            line = line.strip()
            if line:
                # Try to extract role name and responsibility
                if ":" in line:
                    parts = line.split(":", 1)
                    role_name = parts[0].strip()
                    responsibility = parts[1].strip()
                else:
                    role_name = line
                    responsibility = "Responsible for executing assigned tasks"
                
                roles.append({
                    "role_name": role_name,
                    "responsibilities": [responsibility]
                })
        
        return roles if roles else [{"role_name": "Operator", "responsibilities": [message]}]
    
    def _parse_prerequisites(self, message: str) -> List[str]:
        """Parse prerequisites from user message."""
        prerequisites = []
        lines = message.strip().split("\n")
        
        for line in lines:
            line = line.strip()
            if line:
                # Remove bullet points or numbering
                if line[0] in ["-", "*", "•"]:
                    line = line[1:].strip()
                elif line[0].isdigit() and len(line) > 1 and line[1] in [".", ")"]:
                    line = line[2:].strip()
                
                prerequisites.append(line)
        
        return prerequisites if prerequisites else [message]
    
    def _generate_response(
        self,
        current_stage: str,
        sop_draft: Dict[str, Any],
        user_message: str
    ) -> tuple:
        """Generate response and determine next stage."""
        stage_index = self.SOP_STAGES.index(current_stage) if current_stage in self.SOP_STAGES else 0
        next_index = stage_index + 1
        
        if next_index >= len(self.SOP_STAGES) - 1:
            # Complete
            is_complete = True
            next_stage = "complete"
            response = self._generate_completion_message(sop_draft)
        else:
            is_complete = False
            next_stage = self.SOP_STAGES[next_index]
            response = self._generate_stage_prompt(next_stage, sop_draft)
        
        return response, next_stage, is_complete
    
    def _generate_stage_prompt(self, stage: str, sop_draft: Dict[str, Any]) -> str:
        """Generate prompt for the next stage."""
        prompts = {
            "scope": f"""Great! I've noted the purpose: "{sop_draft.get('purpose', '')[:100]}..."

Now let's define the **Scope**. Who does this procedure apply to? What systems or processes are covered?""",
            
            "procedure_steps": """Excellent! Now let's define the **Procedure Steps**.

Please list the steps involved in this procedure. You can provide them as a numbered list or describe them in detail. For example:
1. Step one description
2. Step two description
3. Step three description""",
            
            "roles": """Perfect! I've captured the procedure steps.

Now let's identify the **Roles & Responsibilities**. Who is responsible for each part of this process? You can list them like:
- Process Owner: Responsible for overall process
- Operator: Executes daily tasks
- Reviewer: Approves completed work""",
            
            "prerequisites": """Almost done! Let's add the **Prerequisites**.

What needs to be in place before starting this procedure? For example:
- Required system access
- Training completed
- Approvals obtained"""
        }
        
        return prompts.get(stage, "Please continue providing information for the SOP.")
    
    def _generate_completion_message(self, sop_draft: Dict[str, Any]) -> str:
        """Generate completion message with SOP summary."""
        steps_count = len(sop_draft.get("procedure_steps", []))
        roles_count = len(sop_draft.get("roles", []))
        
        return f"""Congratulations! Your SOP has been created successfully!

**SOP Summary:**
- **Title:** {sop_draft.get('title', 'Untitled')}
- **Purpose:** {sop_draft.get('purpose', 'Not specified')[:100]}...
- **Procedure Steps:** {steps_count} steps defined
- **Roles:** {roles_count} roles identified

The SOP has been saved and is ready for review. You can:
1. Export it to different formats (DOCX, PDF)
2. Create a workflow from this SOP
3. Analyze coexistence opportunities

Would you like to do any of these?"""
    
    async def _store_completed_sop(self, sop_draft: Dict[str, Any], context: ExecutionContext) -> Optional[str]:
        """Store completed SOP in Artifact Plane."""
        sop_draft["sop_id"] = f"sop_{generate_event_id()}"
        sop_draft["status"] = "completed"
        sop_draft["created_at"] = datetime.utcnow().isoformat()
        
        if self.public_works:
            try:
                artifact_plane = self.public_works.get_artifact_plane()
                if artifact_plane:
                    result = await artifact_plane.create_artifact(
                        artifact_type="sop",
                        content=sop_draft,
                        metadata={"title": sop_draft.get("title")},
                        tenant_id=context.tenant_id,
                        include_payload=True
                    )
                    return result.get("artifact_id")
            except Exception as e:
                self.logger.warning(f"Could not store SOP: {e}")
        return None
