"""
Intent Executor - Routes Runtime Intents to Realm Orchestrators

WHAT (Runtime): I execute intents by routing to appropriate realm orchestrators
HOW (Executor): I lookup capabilities via Curator and invoke realm handlers
"""

from typing import Dict, Any, Optional
from utilities import get_logger


class IntentExecutor:
    """
    Intent Executor - Routes intents to realm orchestrators.
    
    This class bridges Runtime and Realms, executing intents by:
    1. Looking up capability via Curator
    2. Routing to appropriate realm orchestrator
    3. Executing intent handler
    4. Returning result
    """
    
    def __init__(
        self,
        curator: Any,
        realm_handlers: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Intent Executor.
        
        Args:
            curator: Curator Foundation Service
            realm_handlers: Dictionary mapping realm names to orchestrator instances
        """
        self.curator = curator
        self.realm_handlers = realm_handlers or {}
        self.logger = get_logger(self.__class__.__name__)
    
    def register_realm_handler(
        self,
        realm_name: str,
        orchestrator: Any
    ) -> None:
        """
        Register a realm orchestrator handler.
        
        Args:
            realm_name: Realm name (e.g., "content", "insights")
            orchestrator: Realm orchestrator instance
        """
        self.realm_handlers[realm_name] = orchestrator
        self.logger.info(f"Registered realm handler: {realm_name}")
    
    async def execute_intent(
        self,
        intent_type: str,
        realm: str,
        payload: Dict[str, Any],
        execution_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute an intent by routing to appropriate realm orchestrator.
        
        Args:
            intent_type: Intent type (e.g., "content.upload", "data_mash.create")
            realm: Target realm (e.g., "content", "insights")
            payload: Intent payload
            execution_context: Execution context (tenant_id, session_id, etc.)
        
        Returns:
            Execution result
        """
        try:
            # Lookup capability via Curator
            capability = None
            if self.curator:
                try:
                    capabilities = await self.curator.lookup_capability_by_intent(intent_type)
                    if capabilities:
                        capability = capabilities[0]
                except Exception as e:
                    self.logger.warning(f"Capability lookup failed: {e}")
            
            # Get realm handler
            realm_handler = self.realm_handlers.get(realm)
            if not realm_handler:
                return {
                    "success": False,
                    "error": f"Realm handler not found: {realm}"
                }
            
            # Route to appropriate handler method based on intent type
            if intent_type == "content.upload":
                if hasattr(realm_handler, 'handle_upload_intent'):
                    # Add file_storage_abstraction to execution_context if available
                    # (This would come from Public Works, but for now we'll get it from orchestrator)
                    if hasattr(realm_handler, 'file_storage'):
                        execution_context['file_storage_abstraction'] = realm_handler.file_storage
                    if hasattr(realm_handler, 'state_surface'):
                        execution_context['state_surface'] = realm_handler.state_surface
                    
                    return await realm_handler.handle_upload_intent(
                        intent_payload=payload,
                        execution_context=execution_context
                    )
                else:
                    return {
                        "success": False,
                        "error": f"Handler method not found for intent: {intent_type}"
                    }
            
            elif intent_type == "content.parse":
                if hasattr(realm_handler, 'parse_file'):
                    return await realm_handler.parse_file(
                        file_reference=payload.get("file_reference"),
                        filename=payload.get("filename"),
                        parsing_type=payload.get("parsing_type"),
                        options=payload.get("options", {})
                    )
                else:
                    return {
                        "success": False,
                        "error": f"Handler method not found for intent: {intent_type}"
                    }
            
            elif intent_type == "data_mash.create":
                if hasattr(realm_handler, 'create_mash'):
                    # Add state_surface to execution_context if available
                    if hasattr(realm_handler, 'state_surface'):
                        execution_context['state_surface'] = realm_handler.state_surface
                    
                    return await realm_handler.create_mash(
                        content_refs=payload.get("content_refs", []),
                        options=payload.get("options", {}),
                        execution_context=execution_context
                    )
                else:
                    return {
                        "success": False,
                        "error": f"Handler method not found for intent: {intent_type}"
                    }
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown intent type: {intent_type}"
                }
        
        except Exception as e:
            self.logger.error(f"❌ Intent execution failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Intent execution failed: {str(e)}"
            }
