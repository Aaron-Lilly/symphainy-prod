# Base Classes

This directory contains base classes for platform components. **Common pattern:** concrete base, no ABC, no Protocol—type-hint as BaseX. See `docs/architecture/PLATFORM_BASES_DISCIPLINE.md`.

## Base Classes (this directory)

### BaseSolution (`solution_base.py`)
Concrete base for solutions. Defaults: get_journeys, get_journey, get_experience_sdk_config, build_journey_result. Subclass implements handle_intent, get_soa_apis.

### BaseOrchestrator (`orchestrator_base.py`)
Concrete base for journey orchestrators. Logger, clock, telemetry, SOA API registry. Subclass implements compose_journey.

### BaseIntentService (`intent_service_base.py`)
Concrete base for intent services. Logger, clock, telemetry, artifact helpers. Subclass implements execute.

## Usage

```python
from symphainy_platform.bases.orchestrator_base import BaseOrchestrator
from symphainy_platform.bases.intent_service_base import BaseIntentService

class MyJourneyOrchestrator(BaseOrchestrator):
    async def compose_journey(self, journey_id: str, context: ExecutionContext) -> Dict[str, Any]:
        # Compose intent services into journey
        pass

class MyIntentService(BaseIntentService):
    async def execute(self, context: ExecutionContext, params: Dict) -> Artifact:
        # Execute intent service logic
        pass
```

## Other platform bases (elsewhere)

- **AgentBase** — `symphainy_platform/civic_systems/agentic/agent_base.py`
- **MCPServerBase** — `symphainy_platform/civic_systems/agentic/mcp_server_base.py`
- **RealmBase** — `symphainy_platform/civic_systems/platform_sdk/realm_sdk.py` — **Unused in fabric.** Realms = solution + orchestrators + intent services; no XRealm(RealmBase). Legacy.

Same discipline for AgentBase and MCPServerBase: concrete base, no ABC, no Protocol; type-hint as BaseX.

---

**Last Updated:** January 2026
