"""
Realm SDK - SDK for Creating Domain Services

DEPRECATED: RealmBase has been removed from the platform.

The platform now uses the Solution pattern natively:
- Solutions compose journeys (orchestrators)
- Journeys handle intent types and produce artifacts/events
- Solutions register intents via SUPPORTED_INTENTS class attribute

For creating new domain services, see:
- symphainy_platform/bases/solution_base.py - BaseSolution class
- symphainy_platform/solutions/SOLUTION_PATTERN.md - Solution pattern documentation
- symphainy_platform/solutions/content_solution/ - Example solution

This module is kept for backward compatibility but RealmBase should NOT be used.
Use BaseSolution instead.
"""

from typing import Dict, Any, List, Optional, Callable

from utilities import get_logger


def intent_handler(intent_type: str):
    """
    Decorator for registering intent handlers.
    
    DEPRECATED: Use BaseSolution.SUPPORTED_INTENTS instead.
    
    This decorator is kept for backward compatibility only.
    
    Usage (deprecated):
        @intent_handler("ingest_file")
        async def handle_ingest_file(intent: Intent, context: ExecutionContext) -> Dict[str, Any]:
            return {"artifacts": {...}, "events": [...]}
    """
    def decorator(func: Callable):
        # Store intent type in function metadata
        func._intent_type = intent_type
        return func
    return decorator


class RealmSDK:
    """
    SDK for creating domain services.
    
    DEPRECATED: Most methods in this class are deprecated.
    
    Use BaseSolution and SolutionBuilder instead:
    - BaseSolution for solution implementation
    - SolutionBuilder for solution configuration
    - SolutionRegistry for solution registration
    
    The only active method is create_realm_template which provides
    a template structure for documentation purposes.
    """
    
    @staticmethod
    def create_realm_from_template(
        realm_name: str,
        template_type: str = "basic"
    ) -> Dict[str, Any]:
        """
        Create realm template structure.
        
        DEPRECATED: Use BaseSolution pattern instead.
        
        This is kept for documentation generation only.
        For actual implementation, see SOLUTION_PATTERN.md.
        
        Args:
            realm_name: Name of the realm
            template_type: Template type ("basic", "with_orchestrator", "with_agents")
        
        Returns:
            Template structure dictionary
        """
        # Template shows the conceptual structure
        # Real implementation should use BaseSolution
        templates = {
            "basic": {
                "realm_name": realm_name,
                "pattern": "Use BaseSolution",
                "structure": {
                    "solution": f"{realm_name}_solution.py",
                    "journeys": f"journeys/",
                    "mcp_server": f"mcp_server/"
                },
                "example": "See symphainy_platform/solutions/content_solution/"
            },
            "with_orchestrator": {
                "realm_name": realm_name,
                "pattern": "Use BaseSolution with journey orchestrators",
                "structure": {
                    "solution": f"{realm_name}_solution.py",
                    "journeys": [f"{realm_name}_journey.py"],
                    "mcp_server": f"{realm_name}_mcp_server.py"
                },
                "example": "See symphainy_platform/solutions/insights_solution/"
            },
            "with_agents": {
                "realm_name": realm_name,
                "pattern": "Use BaseSolution with agents",
                "structure": {
                    "solution": f"{realm_name}_solution.py",
                    "journeys": [f"{realm_name}_journey.py"],
                    "agents": [f"{realm_name}_agent.py"],
                    "mcp_server": f"{realm_name}_mcp_server.py"
                },
                "example": "See symphainy_platform/solutions/operations_solution/"
            }
        }
        
        return templates.get(template_type, templates["basic"])
    
    @staticmethod
    def get_solution_pattern_info() -> Dict[str, Any]:
        """
        Get information about the Solution pattern.
        
        This replaces the deprecated RealmBase pattern.
        
        Returns:
            Dict with Solution pattern documentation
        """
        return {
            "pattern": "Solution Pattern",
            "base_class": "BaseSolution",
            "location": "symphainy_platform/bases/solution_base.py",
            "documentation": "symphainy_platform/solutions/SOLUTION_PATTERN.md",
            "key_concepts": {
                "solution": "Top-level construct that composes journeys and exposes SOA APIs",
                "journey": "Orchestrator that handles a specific workflow (e.g., file upload)",
                "mcp_server": "MCP server that exposes journeys as AI-callable tools",
                "supported_intents": "Class attribute listing all intent types the solution handles"
            },
            "runtime_contract": {
                "handle_intent": "async def handle_intent(self, intent: Intent, context: ExecutionContext) -> Dict[str, Any]",
                "returns": {"artifacts": "Dict of produced artifacts", "events": "List of events to emit"}
            },
            "examples": [
                "symphainy_platform/solutions/content_solution/content_solution.py",
                "symphainy_platform/solutions/security_solution/security_solution.py",
                "symphainy_platform/solutions/insights_solution/insights_solution.py"
            ]
        }