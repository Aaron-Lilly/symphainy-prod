"""
Process Guide Agent Message Intent Service

Implements the process_guide_agent_message intent for the Coexistence Realm.

Purpose: Process a user message through the Guide Agent, generating
appropriate responses and actions.

WHAT (Intent Service Role): I process messages through Guide Agent
HOW (Intent Service Implementation): I analyze user intent, determine
    appropriate actions, and generate responses
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from utilities import generate_event_id


class ProcessGuideAgentMessageService(BaseIntentService):
    """
    Intent service for processing Guide Agent messages.
    
    Analyzes user messages and:
    - Determines user intent
    - Suggests appropriate actions
    - Routes to specialized agents if needed
    - Executes platform operations
    """
    
    # Intent classification keywords
    INTENT_KEYWORDS = {
        "upload": ["upload", "ingest", "add file", "import"],
        "analyze": ["analyze", "quality", "assess", "interpret", "understand"],
        "sop": ["sop", "procedure", "process", "workflow", "document"],
        "outcome": ["roadmap", "poc", "blueprint", "outcome", "strategy"],
        "help": ["help", "how", "what", "explain", "guide"],
        "navigate": ["go to", "show", "navigate", "find", "where"]
    }
    
    def __init__(self, public_works, state_surface):
        """Initialize ProcessGuideAgentMessageService."""
        super().__init__(
            service_id="process_guide_agent_message_service",
            intent_type="process_guide_agent_message",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the process_guide_agent_message intent."""
        await self.record_telemetry(
            telemetry_data={"action": "execute", "status": "started"},
            tenant_id=context.tenant_id
        )
        
        try:
            intent_params = context.intent.parameters or {} if context.intent else {}
            if params:
                intent_params = {**intent_params, **params}
            
            guide_session_id = intent_params.get("guide_session_id")
            message = intent_params.get("message")
            
            if not guide_session_id:
                raise ValueError("guide_session_id is required")
            if not message:
                raise ValueError("message is required")
            
            # Process the message
            response = await self._process_message(guide_session_id, message, context)
            
            await self.record_telemetry(
                telemetry_data={"action": "execute", "status": "success"},
                tenant_id=context.tenant_id
            )
            
            return {
                "success": True,
                "response": response,
                "timestamp": datetime.utcnow().isoformat(),
                "events": [
                    {
                        "event_id": generate_event_id(),
                        "event_type": "guide_message_processed",
                        "timestamp": datetime.utcnow().isoformat(),
                        "guide_session_id": guide_session_id
                    }
                ]
            }
            
        except ValueError as e:
            return {"success": False, "error": str(e), "error_code": "INVALID_INPUT"}
        except Exception as e:
            self.logger.error(f"Failed to process message: {e}")
            return {"success": False, "error": str(e)}
    
    async def _process_message(
        self, 
        guide_session_id: str, 
        message: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Process a user message and generate response."""
        # Classify user intent
        classified_intent = self._classify_intent(message)
        
        # Generate response based on intent
        response = await self._generate_response(classified_intent, message, context)
        
        return {
            "message_id": generate_event_id(),
            "guide_session_id": guide_session_id,
            "user_message": message,
            "classified_intent": classified_intent,
            "agent_response": response["text"],
            "suggested_actions": response.get("actions", []),
            "handoff_recommended": response.get("handoff_recommended", False),
            "handoff_agent": response.get("handoff_agent"),
            "tools_available": response.get("tools", [])
        }
    
    def _classify_intent(self, message: str) -> str:
        """Classify user intent from message."""
        message_lower = message.lower()
        
        for intent, keywords in self.INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return intent
        
        return "general"
    
    async def _generate_response(
        self, 
        intent: str, 
        message: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Generate response based on classified intent."""
        responses = {
            "upload": {
                "text": "I can help you upload files to the platform. You can use the Content Solution to ingest files from various sources. Would you like me to guide you through the upload process, or would you prefer to work directly with the Content Liaison Agent?",
                "actions": [
                    {"action": "navigate_to_solution", "params": {"solution_id": "content_solution"}},
                    {"action": "compose_journey", "params": {"journey": "FileIngestionJourney"}}
                ],
                "handoff_recommended": True,
                "handoff_agent": "ContentLiaisonAgent",
                "tools": ["content_ingest_file", "content_parse"]
            },
            "analyze": {
                "text": "I can help you analyze your data. The Insights Solution provides data quality assessment, AI-powered interpretation, and relationship mapping. What data would you like to analyze?",
                "actions": [
                    {"action": "navigate_to_solution", "params": {"solution_id": "insights_solution"}},
                    {"action": "list_artifacts", "params": {}}
                ],
                "handoff_recommended": True,
                "handoff_agent": "InsightsLiaisonAgent",
                "tools": ["insights_assess_quality", "insights_interpret"]
            },
            "sop": {
                "text": "I can help you create Standard Operating Procedures. The Operations Solution can generate SOPs from process descriptions, optimize workflows, and analyze coexistence patterns. Would you like to describe the process you want to document?",
                "actions": [
                    {"action": "navigate_to_solution", "params": {"solution_id": "operations_solution"}},
                    {"action": "compose_journey", "params": {"journey": "SOPGenerationJourney"}}
                ],
                "handoff_recommended": True,
                "handoff_agent": "OperationsLiaisonAgent",
                "tools": ["ops_generate_sop", "ops_create_workflow"]
            },
            "outcome": {
                "text": "I can help you create strategic deliverables. The Outcomes Solution can synthesize insights into outcomes, generate roadmaps, create POCs, and design blueprints. What outcome are you looking to create?",
                "actions": [
                    {"action": "navigate_to_solution", "params": {"solution_id": "outcomes_solution"}},
                    {"action": "compose_journey", "params": {"journey": "OutcomeSynthesisJourney"}}
                ],
                "handoff_recommended": True,
                "handoff_agent": "OutcomesLiaisonAgent",
                "tools": ["outcomes_synthesize", "outcomes_roadmap"]
            },
            "help": {
                "text": "I'm here to help! I can guide you through the platform's capabilities, help you navigate to different solutions, or connect you with specialized agents. What would you like to know more about?",
                "actions": [
                    {"action": "show_solution_catalog", "params": {}},
                    {"action": "get_documentation", "params": {"topic": "getting_started"}}
                ],
                "handoff_recommended": False,
                "tools": ["coexist_introduce_platform", "coexist_show_catalog"]
            },
            "navigate": {
                "text": "I can help you navigate to different parts of the platform. We have Content, Insights, Operations, and Outcomes solutions. Which area interests you?",
                "actions": [
                    {"action": "show_solution_catalog", "params": {}}
                ],
                "handoff_recommended": False,
                "tools": ["coexist_navigate_to_solution"]
            },
            "general": {
                "text": "I understand you're asking about the platform. I can help you with file management (Content), data analysis (Insights), workflow optimization (Operations), or strategic deliverables (Outcomes). Could you tell me more about what you're trying to accomplish?",
                "actions": [
                    {"action": "show_solution_catalog", "params": {}}
                ],
                "handoff_recommended": False,
                "tools": []
            }
        }
        
        return responses.get(intent, responses["general"])
