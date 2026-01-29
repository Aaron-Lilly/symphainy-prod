"""
Base Solution - Concrete Base for All Solutions

Concrete base class for solution constructs. No ABC, no Protocol—type-hint as
BaseSolution. Single source of truth; no protocol to keep in sync.

WHAT (Solution Role): I define the solution contract and shared behavior
HOW (Implementation): Default implementations for get_journeys, get_journey,
    get_experience_sdk_config; helper build_journey_result for standard result shape.

DISCIPLINE (see docs/architecture/SOLUTION_BASE_DISCIPLINE.md):
- This file stays under 250 lines. No compliance layers; no lazy services.
- Only what fixes the 10 mismatches: get_journey/get_journeys, build_journey_result,
  default get_experience_sdk_config, async initialize_mcp_server.
- New behavior goes in solutions/journeys or SOLUTION_PATTERN.md, not here.

Reference: docs/architecture/SOLUTION_CONTRACT_RESOLUTION.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

def _find_project_root():
    path = Path(__file__).resolve()
    for parent in path.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    return path.parents[3]

_project_root = _find_project_root()
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from utilities import get_logger, get_clock


# ---------------------------------------------------------------------------
# BaseSolution - Concrete base (no ABC, no Protocol; type-hint as BaseSolution)
# ---------------------------------------------------------------------------

class BaseSolution:
    """
    Concrete base for all solutions. Provides default implementations for
    get_journeys(), get_journey(), get_experience_sdk_config(), and
    build_journey_result() for standard journey result shape.

    Subclasses MUST:
    - Set SOLUTION_ID (and optionally SOLUTION_NAME, SUPPORTED_INTENTS)
    - Call super().__init__() and populate self._journeys in _initialize_journeys()
    - Implement handle_intent() and get_soa_apis()
    - Implement or override initialize_mcp_server() as needed

    Subclasses MAY override get_experience_sdk_config() for custom config shape.
    """

    SOLUTION_ID: str = "base_solution"
    SOLUTION_NAME: str = "Base Solution"
    SUPPORTED_INTENTS: List[str] = ["compose_journey"]

    def __init__(
        self,
        public_works: Optional[Any] = None,
        state_surface: Optional[Any] = None,
    ):
        self.public_works = public_works
        self.state_surface = state_surface
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        self.solution_id = getattr(self.__class__, "SOLUTION_ID", "base_solution")
        self.solution_name = getattr(self.__class__, "SOLUTION_NAME", "Base Solution")
        self._journeys: Dict[str, Any] = {}
        self._mcp_server: Optional[Any] = None
        self._initialize_journeys()

    def _initialize_journeys(self) -> None:
        """Subclasses override to populate self._journeys."""
        pass

    # ---------- Journey access (default impls from _journeys) ----------

    def get_journeys(self) -> Dict[str, Any]:
        """Get all journey orchestrators. Default: copy of _journeys."""
        return self._journeys.copy()

    def get_journey(self, journey_id: str) -> Optional[Any]:
        """Get a specific journey orchestrator. Default: _journeys.get(journey_id)."""
        return self._journeys.get(journey_id)

    # ---------- Standard journey result shape ----------

    @staticmethod
    def build_journey_result(
        success: bool,
        journey_id: str,
        journey_execution_id: str,
        artifacts: Optional[Dict[str, Any]] = None,
        events: Optional[List[Dict[str, Any]]] = None,
        error: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Build the standard journey result shape. All journeys SHOULD return
        this shape so tests and frontend can assert on success, artifacts, events.

        Returns dict with: success, journey_id, journey_execution_id, artifacts, events.
        On failure, set success=False and put error details in artifacts or events.
        """
        return {
            "success": success,
            "journey_id": journey_id,
            "journey_execution_id": journey_execution_id,
            "artifacts": artifacts or {},
            "events": events or [],
            **({"error": error} if error else {}),
        }

    # ---------- Experience SDK config (default impl with top-level available_journeys) ----------

    def get_experience_sdk_config(self) -> Dict[str, Any]:
        """
        Default Experience SDK config. Includes top-level available_journeys
        for backward compatibility with tests/frontend; also nested
        integration_patterns.journey_invocation.available_journeys.
        Subclasses may override for custom shape.
        """
        journey_ids = list(self._journeys.keys())
        journeys_list = [
            {
                "journey_id": jid,
                "journey_name": getattr(j, "JOURNEY_NAME", jid),
            }
            for jid, j in self._journeys.items()
        ]
        soa_apis = self.get_soa_apis()
        return {
            "solution_id": self.solution_id,
            "solution_name": self.solution_name,
            "supported_intents": getattr(self.__class__, "SUPPORTED_INTENTS", ["compose_journey"]),
            "available_journeys": journey_ids,
            "journeys": journeys_list,
            "soa_apis": {
                name: {
                    "input_schema": api_def.get("input_schema", {}),
                    "description": api_def.get("description", ""),
                }
                for name, api_def in soa_apis.items()
            },
            "integration_patterns": {
                "intent_submission": {
                    "description": "Submit intents via Experience SDK submitIntent()",
                },
                "journey_invocation": {
                    "description": "Invoke journeys directly via compose_journey intent",
                    "available_journeys": journey_ids,
                },
            },
        }

    # ---------- Subclass must implement ----------

    def get_soa_apis(self) -> Dict[str, Dict[str, Any]]:
        """Subclasses must implement. Default returns empty dict."""
        return {}

    async def handle_intent(self, intent: Any, context: Any) -> Dict[str, Any]:
        """Subclasses must implement. Default raises NotImplementedError."""
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement handle_intent(intent, context)"
        )

    async def initialize_mcp_server(self) -> Any:
        """
        Initialize MCP server for this solution. Async—callers MUST use await.
        Default returns None; subclasses override to create and initialize server.
        """
        return None


# Backward-compatibility alias (e.g. get_code_examples_service, get_patterns_service)
SolutionBase = BaseSolution
