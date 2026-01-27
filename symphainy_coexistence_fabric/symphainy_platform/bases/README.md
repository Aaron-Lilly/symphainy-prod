# Base Classes

This directory contains base classes for platform components.

## Base Classes

### BaseOrchestrator (`orchestrator_base.py`)
Base class for journey orchestrators.

**To Be Created:**
- Logger and clock utilities
- Public Works access
- Intent service composition
- SOA API registration
- MCP tool exposure
- Saga coordination
- Telemetry reporting (via Nurse SDK)

### BaseIntentService (`intent_service_base.py`)
Base class for intent services.

**To Be Created:**
- Logger and clock utilities
- Public Works access
- Execution context handling
- Artifact creation and registration
- Telemetry reporting (via Nurse SDK)
- Contract compliance validation

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

## Status

✅ **IMPLEMENTED** - Base classes created and ready for use.

**Created:**
- `orchestrator_base.py` - BaseOrchestrator class (330+ lines)
- `intent_service_base.py` - BaseIntentService class (350+ lines)

---

**Last Updated:** January 27, 2026
