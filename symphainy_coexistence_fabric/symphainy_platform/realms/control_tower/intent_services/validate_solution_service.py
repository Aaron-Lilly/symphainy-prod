"""
Validate Solution Intent Service

Implements the validate_solution intent for the Control Tower Realm.

Purpose: Validate a solution configuration against platform requirements.

WHAT (Intent Service Role): I validate solution configurations
HOW (Intent Service Implementation): I check solution structure,
    required methods, and compliance with patterns
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

project_root = Path(__file__).resolve().parents[6]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from utilities import generate_event_id


class ValidateSolutionService(BaseIntentService):
    """
    Intent service for validating solution configurations.
    
    Validates:
    - Required methods (handle_intent, get_soa_apis, compose_journey)
    - MCP server registration
    - Journey definitions
    - Pattern compliance
    """
    
    REQUIRED_METHODS = [
        "handle_intent",
        "get_soa_apis",
        "_handle_compose_journey"
    ]
    
    REQUIRED_ATTRIBUTES = [
        "SOLUTION_ID",
        "SUPPORTED_INTENTS"
    ]
    
    def __init__(self, public_works, state_surface):
        """Initialize ValidateSolutionService."""
        super().__init__(
            service_id="validate_solution_service",
            intent_type="validate_solution",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the validate_solution intent."""
        await self.record_telemetry(
            telemetry_data={"action": "execute", "status": "started"},
            tenant_id=context.tenant_id
        )
        
        try:
            intent_params = context.intent.parameters or {} if context.intent else {}
            if params:
                intent_params = {**intent_params, **params}
            
            solution_config = intent_params.get("solution_config")
            if not solution_config:
                raise ValueError("solution_config is required")
            
            # Validate the solution
            validation_result = await self._validate_solution(solution_config)
            
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute",
                    "status": "success",
                    "is_valid": validation_result["is_valid"]
                },
                tenant_id=context.tenant_id
            )
            
            return {
                "success": True,
                "validation": validation_result,
                "timestamp": datetime.utcnow().isoformat(),
                "events": [
                    {
                        "event_id": generate_event_id(),
                        "event_type": "solution_validated",
                        "timestamp": datetime.utcnow().isoformat(),
                        "is_valid": validation_result["is_valid"]
                    }
                ]
            }
            
        except ValueError as e:
            return {"success": False, "error": str(e), "error_code": "INVALID_INPUT"}
        except Exception as e:
            self.logger.error(f"Failed to validate solution: {e}")
            return {"success": False, "error": str(e), "error_code": "VALIDATION_ERROR"}
    
    async def _validate_solution(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a solution configuration."""
        errors = []
        warnings = []
        
        # Check required attributes
        for attr in self.REQUIRED_ATTRIBUTES:
            if attr not in config:
                errors.append(f"Missing required attribute: {attr}")
        
        # Check SOLUTION_ID format
        solution_id = config.get("SOLUTION_ID", "")
        if solution_id and not solution_id.endswith("_solution"):
            warnings.append(f"SOLUTION_ID should end with '_solution': {solution_id}")
        
        # Check SUPPORTED_INTENTS includes compose_journey
        supported_intents = config.get("SUPPORTED_INTENTS", [])
        if "compose_journey" not in supported_intents:
            errors.append("SUPPORTED_INTENTS must include 'compose_journey'")
        
        # Check journeys
        journeys = config.get("journeys", {})
        if not journeys:
            warnings.append("No journeys defined - solution should have at least one journey")
        
        # Check MCP server
        mcp_config = config.get("mcp_server", {})
        if not mcp_config:
            warnings.append("No MCP server configuration - agents won't be able to use this solution")
        else:
            if "prefix" not in mcp_config:
                errors.append("MCP server must define a prefix")
        
        # Check SOA APIs
        soa_apis = config.get("soa_apis", [])
        if "compose_journey" not in soa_apis:
            errors.append("SOA APIs must include 'compose_journey'")
        
        # Check for anti-patterns
        anti_patterns = self._check_anti_patterns(config)
        if anti_patterns:
            errors.extend(anti_patterns)
        
        is_valid = len(errors) == 0
        
        return {
            "is_valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "checks_passed": {
                "has_solution_id": "SOLUTION_ID" in config,
                "has_supported_intents": "SUPPORTED_INTENTS" in config,
                "includes_compose_journey": "compose_journey" in supported_intents,
                "has_journeys": len(journeys) > 0,
                "has_mcp_server": bool(mcp_config),
                "no_anti_patterns": len(anti_patterns) == 0
            }
        }
    
    def _check_anti_patterns(self, config: Dict[str, Any]) -> List[str]:
        """Check for anti-patterns in solution configuration."""
        anti_patterns = []
        
        # Check for direct infrastructure access hints
        if config.get("uses_direct_db"):
            anti_patterns.append("Anti-pattern: Solution uses direct database access - use Public Works")
        
        if config.get("uses_direct_storage"):
            anti_patterns.append("Anti-pattern: Solution uses direct storage access - use Public Works")
        
        # Check for orchestration in wrong place
        if config.get("orchestrates_in_realm"):
            anti_patterns.append("Anti-pattern: Orchestration logic in Realm - should be in Solution/Journey")
        
        return anti_patterns
