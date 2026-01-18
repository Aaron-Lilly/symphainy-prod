"""
Content Liaison Agent - Conversational Agent for Content Realm

User-facing agent that routes content-related requests and provides conversational interface.
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

from typing import Dict, Any, List, Optional

from .conversational_agent import ConversationalAgentBase
from symphainy_platform.runtime.execution_context import ExecutionContext


class ContentLiaisonAgent(ConversationalAgentBase):
    """
    Content Liaison Agent - Conversational agent for Content realm.
    
    Handles user-facing interactions for content operations:
    - File upload guidance
    - Parsing status queries
    - Semantic interpretation explanations
    """
    
    def __init__(
        self,
        agent_id: str,
        capabilities: List[str],
        collaboration_router=None,
        orchestrator=None  # Content orchestrator reference
    ):
        super().__init__(
            agent_id=agent_id,
            capabilities=capabilities,
            state_awareness="full",
            collaboration_router=collaboration_router
        )
        self.orchestrator = orchestrator
    
    async def process_request(
        self,
        request: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Process content-related conversational request.
        """
        message = request.get("message", "")
        
        # Determine intent from message
        intent = self._determine_intent(message)
        
        # Route to appropriate handler
        if intent == "upload_file":
            response = await self._handle_upload_guidance(message, context)
        elif intent == "check_parsing_status":
            response = await self._handle_status_query(message, context)
        elif intent == "explain_semantic":
            response = await self._handle_semantic_explanation(message, context)
        else:
            response = await self._handle_general_query(message, context)
        
        return {
            "artifact_type": "proposal",
            "artifact": {
                "response": response,
                "intent": intent
            },
            "confidence": 0.9
        }
    
    async def get_agent_description(self) -> str:
        """Get agent description."""
        return f"Content Liaison Agent ({self.agent_id}) - Conversational interface for content operations"
    
    async def generate_response(
        self,
        message: str,
        session_state: Optional[Dict[str, Any]],
        context: ExecutionContext
    ) -> str:
        """Generate conversational response."""
        # For MVP: Simple response generation
        # In full implementation: Use LLM for natural language generation
        return f"I can help you with content operations. You said: {message}"
    
    def _determine_intent(self, message: str) -> str:
        """Determine intent from message (simple keyword matching for MVP)."""
        message_lower = message.lower()
        if "upload" in message_lower or "file" in message_lower:
            return "upload_file"
        elif "status" in message_lower or "parsing" in message_lower:
            return "check_parsing_status"
        elif "semantic" in message_lower or "meaning" in message_lower:
            return "explain_semantic"
        else:
            return "general_query"
    
    async def _handle_upload_guidance(
        self,
        message: str,
        context: ExecutionContext
    ) -> str:
        """Handle file upload guidance."""
        return "I can help you upload files. Supported formats include CSV, JSON, PDF, and more."
    
    async def _handle_status_query(
        self,
        message: str,
        context: ExecutionContext
    ) -> str:
        """Handle parsing status query."""
        return "I can check the parsing status of your files. Let me look that up for you."
    
    async def _handle_semantic_explanation(
        self,
        message: str,
        context: ExecutionContext
    ) -> str:
        """Handle semantic interpretation explanation."""
        return "I can explain the semantic interpretation of your data. This shows the meaning and structure of your content."
    
    async def _handle_general_query(
        self,
        message: str,
        context: ExecutionContext
    ) -> str:
        """Handle general content-related query."""
        return "I'm here to help with content operations. What would you like to know?"
