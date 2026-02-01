"""List Solutions Service (Platform SDK)

Requires get_solution_registry() from ctx.platform. Fails fast if registry is not available (no silent fallback).
"""

from typing import Dict, Any, List
from utilities import get_logger
from symphainy_platform.civic_systems.platform_sdk import PlatformIntentService, PlatformContext


class ListSolutionsService(PlatformIntentService):
    """List Solutions Service using Platform SDK."""
    
    intent_type = "list_solutions"
    
    def __init__(self, service_id: str = "list_solutions_service"):
        super().__init__(service_id=service_id, intent_type="list_solutions")
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        self.logger.info(f"Executing list_solutions: {ctx.execution_id}")
        params = getattr(ctx.intent, "parameters", None) or getattr(ctx, "parameters", None) or {}
        active_only = params.get("active_only", False)
        domain = params.get("domain")

        reg = None
        if ctx.platform and hasattr(ctx.platform, "get_solution_registry"):
            reg = ctx.platform.get_solution_registry()
        if not reg or not hasattr(reg, "list_solutions"):
            raise RuntimeError(
                "Solution registry not available; cannot list solutions. "
                "Ensure Public Works provides get_solution_registry() and initialize() has run."
            )
        solutions_list = reg.list_solutions(active_only=active_only, domain=domain)
        solutions: List[Dict[str, Any]] = []
        for s in solutions_list:
            sid = getattr(s, "solution_id", str(s))
            status = "active" if (hasattr(reg, "is_solution_active") and reg.is_solution_active(sid)) else "inactive"
            to_dict = getattr(s, "to_dict", None)
            if callable(to_dict):
                row = to_dict()
                if isinstance(row, dict):
                    row["status"] = row.get("status", status)
                    row["id"] = row.get("solution_id", row.get("id", sid))
                    row["name"] = row.get("name", sid)
                else:
                    row = {"id": sid, "name": sid, "status": status}
            else:
                row = {"id": sid, "name": sid, "status": status}
            solutions.append(row)
        return {"artifacts": {"solutions": solutions}, "events": []}
