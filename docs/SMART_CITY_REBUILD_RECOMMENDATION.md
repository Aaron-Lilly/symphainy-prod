# Smart City Rebuild Recommendation for New Architecture

**Date:** January 2026  
**Purpose:** How to rebuild Smart City services to integrate with the new Runtime Plane + Foundations architecture

---

## Current State Analysis

### Existing Smart City Services

**Location:** `/symphainy_source/symphainy-platform/backend/smart_city/services/`

**8 Services:**
1. **City Manager** - Bootstrap and orchestration
2. **Security Guard** - Authentication, authorization, zero-trust
3. **Traffic Cop** - Session semantics, API gateway
4. **Post Office** - Event routing, messaging
5. **Conductor** - Workflow orchestration
6. **Librarian** - Knowledge governance
7. **Data Steward** - Lifecycle & policy hooks
8. **Nurse** - Telemetry, tracing, health

### Current Architecture Issues

1. **Old Base Classes:** Extends `SmartCityRoleBase` (old architecture)
2. **DI Container Dependency:** Heavy dependency on DI container
3. **No Runtime Integration:** Doesn't register with or observe Runtime
4. **Old Utility Mixins:** Uses old utility access patterns
5. **Micro-Module Complexity:** Complex dynamic loading

---

## New Architecture Requirements

### From Plan (Phase 4)

**What Smart City Does:**
- Registers with Runtime
- Observes execution
- Enforces policy
- Emits telemetry

**What Smart City Does NOT Do:**
- Execute domain logic
- Reason
- Own state

**Smart City is the governor, not the engine.**

---

## Recommended New Structure

### Directory Structure

```
symphainy_platform/
├── smart_city/
│   ├── __init__.py
│   ├── foundation_service.py          # Smart City Foundation (orchestrates all services)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── city_manager/
│   │   │   ├── __init__.py
│   │   │   ├── city_manager_service.py
│   │   │   └── modules/               # Micro-modules (if needed)
│   │   ├── security_guard/
│   │   │   ├── __init__.py
│   │   │   └── security_guard_service.py
│   │   ├── traffic_cop/
│   │   │   ├── __init__.py
│   │   │   └── traffic_cop_service.py
│   │   ├── post_office/
│   │   │   ├── __init__.py
│   │   │   └── post_office_service.py
│   │   ├── conductor/
│   │   │   ├── __init__.py
│   │   │   └── conductor_service.py
│   │   ├── librarian/
│   │   │   ├── __init__.py
│   │   │   └── librarian_service.py
│   │   ├── data_steward/
│   │   │   ├── __init__.py
│   │   │   └── data_steward_service.py
│   │   └── nurse/
│   │       ├── __init__.py
│   │       └── nurse_service.py
│   └── protocols/
│       ├── __init__.py
│       ├── smart_city_service_protocol.py
│       └── execution_observer_protocol.py
```

---

## New Service Pattern

### Base Smart City Service Pattern

```python
# symphainy_platform/smart_city/protocols/smart_city_service_protocol.py

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class SmartCityServiceProtocol(ABC):
    """
    Protocol for Smart City services.
    
    All Smart City services:
    - Register with Runtime
    - Observe execution
    - Enforce policy
    - Emit telemetry
    """
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize service and register with Runtime/Curator."""
        pass
    
    @abstractmethod
    async def observe_execution(self, execution_id: str, event: dict) -> None:
        """Observe Runtime execution events."""
        pass
    
    @abstractmethod
    async def enforce_policy(self, execution_id: str, context: dict) -> bool:
        """Enforce policy for execution context."""
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Gracefully shutdown service."""
        pass
```

### Example: Security Guard Service

```python
# symphainy_platform/smart_city/services/security_guard/security_guard_service.py

from typing import Dict, Any, Optional
from symphainy_platform.smart_city.protocols.smart_city_service_protocol import SmartCityServiceProtocol
from symphainy_platform.foundations.public_works.foundation_service import PublicWorksFoundationService
from symphainy_platform.foundations.curator.foundation_service import CuratorFoundationService
from symphainy_platform.runtime.runtime_service import RuntimeService
from utilities import get_logger, get_clock, LogLevel, LogCategory

class SecurityGuardService(SmartCityServiceProtocol):
    """
    Security Guard Service - New Architecture
    
    WHAT: I enforce security, zero-trust, multi-tenancy
    HOW: I observe Runtime execution and enforce security policies
    
    Responsibilities:
    - Authentication
    - Authorization
    - Zero-trust policy enforcement
    - Multi-tenancy isolation
    """
    
    def __init__(
        self,
        public_works_foundation: PublicWorksFoundationService,
        curator_foundation: CuratorFoundationService,
        runtime_service: RuntimeService
    ):
        self.public_works = public_works_foundation
        self.curator = curator_foundation
        self.runtime = runtime_service
        self.logger = get_logger("security_guard", LogLevel.INFO, LogCategory.PLATFORM)
        self.clock = get_clock()
        
        # Security state
        self.security_policies: Dict[str, Dict[str, Any]] = {}
        self.tenant_contexts: Dict[str, Dict[str, Any]] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
        self.is_initialized = False
    
    async def initialize(self) -> bool:
        """Initialize Security Guard and register with Runtime/Curator."""
        try:
            self.logger.info("Initializing Security Guard Service")
            
            # Register with Curator
            await self.curator.register_service(
                service_instance=self,
                service_metadata={
                    "service_name": "SecurityGuardService",
                    "service_type": "smart_city",
                    "realm": "smart_city",
                    "capabilities": [
                        "authentication",
                        "authorization",
                        "zero_trust_policy",
                        "multi_tenancy"
                    ]
                }
            )
            
            # Register with Runtime as observer
            await self.runtime.register_observer(
                observer_id="security_guard",
                observer=self
            )
            
            # Load security policies (from Public Works or config)
            await self._load_security_policies()
            
            self.is_initialized = True
            self.logger.info("Security Guard Service initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Security Guard: {e}", exc_info=e)
            return False
    
    async def observe_execution(self, execution_id: str, event: dict) -> None:
        """
        Observe Runtime execution events and enforce security.
        
        Events observed:
        - session_created
        - intent_submitted
        - execution_started
        - execution_completed
        """
        event_type = event.get("event_type")
        
        if event_type == "session_created":
            await self._validate_session_security(event)
        elif event_type == "intent_submitted":
            await self._validate_intent_authorization(event)
        elif event_type == "execution_started":
            await self._enforce_execution_policy(event)
        
        # Log security observation
        self.logger.info(
            "Security observation",
            metadata={
                "execution_id": execution_id,
                "event_type": event_type,
                "timestamp": self.clock.now_iso()
            }
        )
    
    async def enforce_policy(self, execution_id: str, context: dict) -> bool:
        """
        Enforce security policy for execution context.
        
        Returns:
            True if policy allows, False if denied
        """
        # Check zero-trust policy
        # Check multi-tenancy isolation
        # Check authorization
        # Return True if allowed, False if denied
        return True
    
    async def _load_security_policies(self):
        """Load security policies from configuration."""
        # Load from Public Works config or environment
        pass
    
    async def _validate_session_security(self, event: dict):
        """Validate session security."""
        pass
    
    async def _validate_intent_authorization(self, event: dict):
        """Validate intent authorization."""
        pass
    
    async def _enforce_execution_policy(self, event: dict):
        """Enforce execution policy."""
        pass
    
    async def shutdown(self) -> None:
        """Gracefully shutdown Security Guard."""
        self.logger.info("Shutting down Security Guard Service")
        # Cleanup
        self.is_initialized = False
```

### Example: Nurse Service

```python
# symphainy_platform/smart_city/services/nurse/nurse_service.py

from typing import Dict, Any, Optional
from symphainy_platform.smart_city.protocols.smart_city_service_protocol import SmartCityServiceProtocol
from symphainy_platform.foundations.public_works.foundation_service import PublicWorksFoundationService
from symphainy_platform.foundations.curator.foundation_service import CuratorFoundationService
from symphainy_platform.runtime.runtime_service import RuntimeService
from utilities import get_logger, get_clock, LogLevel, LogCategory

class NurseService(SmartCityServiceProtocol):
    """
    Nurse Service - New Architecture
    
    WHAT: I monitor health, collect telemetry, manage tracing
    HOW: I observe Runtime execution and emit telemetry
    
    Responsibilities:
    - Health monitoring
    - Telemetry collection
    - Distributed tracing
    - Alert management
    """
    
    def __init__(
        self,
        public_works_foundation: PublicWorksFoundationService,
        curator_foundation: CuratorFoundationService,
        runtime_service: RuntimeService
    ):
        self.public_works = public_works_foundation
        self.curator = curator_foundation
        self.runtime = runtime_service
        self.logger = get_logger("nurse", LogLevel.INFO, LogCategory.PLATFORM)
        self.clock = get_clock()
        
        # Telemetry state
        self.health_metrics: Dict[str, Any] = {}
        self.traces: Dict[str, list] = {}
        
        self.is_initialized = False
    
    async def initialize(self) -> bool:
        """Initialize Nurse and register with Runtime/Curator."""
        try:
            self.logger.info("Initializing Nurse Service")
            
            # Register with Curator
            await self.curator.register_service(
                service_instance=self,
                service_metadata={
                    "service_name": "NurseService",
                    "service_type": "smart_city",
                    "realm": "smart_city",
                    "capabilities": [
                        "health_monitoring",
                        "telemetry_collection",
                        "distributed_tracing",
                        "alert_management"
                    ]
                }
            )
            
            # Register with Runtime as observer
            await self.runtime.register_observer(
                observer_id="nurse",
                observer=self
            )
            
            self.is_initialized = True
            self.logger.info("Nurse Service initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Nurse: {e}", exc_info=e)
            return False
    
    async def observe_execution(self, execution_id: str, event: dict) -> None:
        """
        Observe Runtime execution and collect telemetry.
        
        Events observed:
        - All execution events
        - Performance metrics
        - Error events
        """
        event_type = event.get("event_type")
        
        # Collect telemetry
        await self._collect_telemetry(execution_id, event)
        
        # Update health metrics
        await self._update_health_metrics(execution_id, event)
        
        # Manage traces
        await self._manage_trace(execution_id, event)
    
    async def enforce_policy(self, execution_id: str, context: dict) -> bool:
        """Nurse doesn't enforce policy, only observes."""
        return True
    
    async def _collect_telemetry(self, execution_id: str, event: dict):
        """Collect telemetry data."""
        # Emit to telemetry abstraction (Public Works)
        pass
    
    async def _update_health_metrics(self, execution_id: str, event: dict):
        """Update health metrics."""
        pass
    
    async def _manage_trace(self, execution_id: str, event: dict):
        """Manage distributed trace."""
        pass
    
    async def shutdown(self) -> None:
        """Gracefully shutdown Nurse."""
        self.logger.info("Shutting down Nurse Service")
        self.is_initialized = False
```

---

## Smart City Foundation Service

### Orchestrates All Smart City Services

```python
# symphainy_platform/smart_city/foundation_service.py

from typing import Dict, Any, Optional
from symphainy_platform.foundations.public_works.foundation_service import PublicWorksFoundationService
from symphainy_platform.foundations.curator.foundation_service import CuratorFoundationService
from symphainy_platform.runtime.runtime_service import RuntimeService
from symphainy_platform.smart_city.services.city_manager.city_manager_service import CityManagerService
from symphainy_platform.smart_city.services.security_guard.security_guard_service import SecurityGuardService
from symphainy_platform.smart_city.services.traffic_cop.traffic_cop_service import TrafficCopService
from symphainy_platform.smart_city.services.post_office.post_office_service import PostOfficeService
from symphainy_platform.smart_city.services.conductor.conductor_service import ConductorService
from symphainy_platform.smart_city.services.librarian.librarian_service import LibrarianService
from symphainy_platform.smart_city.services.data_steward.data_steward_service import DataStewardService
from symphainy_platform.smart_city.services.nurse.nurse_service import NurseService
from utilities import get_logger, LogLevel, LogCategory

class SmartCityFoundationService:
    """
    Smart City Foundation Service
    
    Orchestrates all Smart City services and provides unified access.
    
    Responsibilities:
    - Initialize all Smart City services
    - Register services with Runtime/Curator
    - Provide unified access to services
    - Coordinate service lifecycle
    """
    
    def __init__(
        self,
        public_works_foundation: PublicWorksFoundationService,
        curator_foundation: CuratorFoundationService,
        runtime_service: RuntimeService
    ):
        self.public_works = public_works_foundation
        self.curator = curator_foundation
        self.runtime = runtime_service
        self.logger = get_logger("smart_city_foundation", LogLevel.INFO, LogCategory.PLATFORM)
        
        # Smart City services
        self.services: Dict[str, Any] = {}
        self.is_initialized = False
    
    async def initialize(self) -> bool:
        """Initialize all Smart City services."""
        try:
            self.logger.info("Initializing Smart City Foundation")
            
            # Initialize all services
            self.services["city_manager"] = CityManagerService(
                public_works_foundation=self.public_works,
                curator_foundation=self.curator,
                runtime_service=self.runtime
            )
            
            self.services["security_guard"] = SecurityGuardService(
                public_works_foundation=self.public_works,
                curator_foundation=self.curator,
                runtime_service=self.runtime
            )
            
            self.services["traffic_cop"] = TrafficCopService(
                public_works_foundation=self.public_works,
                curator_foundation=self.curator,
                runtime_service=self.runtime
            )
            
            self.services["post_office"] = PostOfficeService(
                public_works_foundation=self.public_works,
                curator_foundation=self.curator,
                runtime_service=self.runtime
            )
            
            self.services["conductor"] = ConductorService(
                public_works_foundation=self.public_works,
                curator_foundation=self.curator,
                runtime_service=self.runtime
            )
            
            self.services["librarian"] = LibrarianService(
                public_works_foundation=self.public_works,
                curator_foundation=self.curator,
                runtime_service=self.runtime
            )
            
            self.services["data_steward"] = DataStewardService(
                public_works_foundation=self.public_works,
                curator_foundation=self.curator,
                runtime_service=self.runtime
            )
            
            self.services["nurse"] = NurseService(
                public_works_foundation=self.public_works,
                curator_foundation=self.curator,
                runtime_service=self.runtime
            )
            
            # Initialize all services
            for service_name, service in self.services.items():
                success = await service.initialize()
                if not success:
                    self.logger.error(f"Failed to initialize {service_name}")
                    return False
            
            self.is_initialized = True
            self.logger.info("Smart City Foundation initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Smart City Foundation: {e}", exc_info=e)
            return False
    
    def get_service(self, service_name: str) -> Optional[Any]:
        """Get Smart City service by name."""
        return self.services.get(service_name)
    
    async def shutdown(self) -> None:
        """Shutdown all Smart City services."""
        self.logger.info("Shutting down Smart City Foundation")
        
        for service_name, service in self.services.items():
            try:
                await service.shutdown()
            except Exception as e:
                self.logger.error(f"Error shutting down {service_name}: {e}")
        
        self.is_initialized = False
```

---

## Runtime Integration

### Runtime Observer Pattern

```python
# symphainy_platform/runtime/runtime_service.py (additions)

class RuntimeService:
    # ... existing code ...
    
    def __init__(self, ...):
        # ... existing code ...
        self.observers: Dict[str, Any] = {}  # Smart City observers
    
    async def register_observer(self, observer_id: str, observer: Any) -> None:
        """Register Smart City service as observer."""
        self.observers[observer_id] = observer
        self.logger.info(f"Registered observer: {observer_id}")
    
    async def _notify_observers(self, execution_id: str, event: dict) -> None:
        """Notify all observers of execution event."""
        for observer_id, observer in self.observers.items():
            try:
                await observer.observe_execution(execution_id, event)
            except Exception as e:
                self.logger.error(f"Observer {observer_id} error: {e}")
    
    # In execution methods, call _notify_observers after events
    async def submit_intent(self, ...):
        # ... existing code ...
        await self._notify_observers(execution_id, {
            "event_type": "intent_submitted",
            "intent": intent,
            "timestamp": get_clock().now_iso()
        })
```

---

## Key Differences from Old Architecture

### 1. No DI Container Dependency
- Direct injection of foundations and runtime
- Cleaner dependencies

### 2. Runtime Integration
- Register as observer
- Observe execution events
- Enforce policies

### 3. Curator Registration
- Register capabilities
- Not just service registration

### 4. Use New Utilities
- `get_logger()` from utilities
- `get_clock()` from utilities
- No old utility mixins

### 5. Governance Focus
- Observe and enforce
- Don't execute domain logic
- Don't reason

### 6. Foundation Service Pattern
- Smart City Foundation orchestrates all services
- Similar to Public Works Foundation pattern

---

## Migration Strategy

### Step 1: Create New Structure
- Create new directory structure
- Create protocols
- Create foundation service

### Step 2: Rebuild Services One by One
- Start with City Manager (bootstrap)
- Then Security Guard (governance)
- Then Nurse (observability)
- Then others

### Step 3: Integrate with Runtime
- Add observer pattern to Runtime
- Register services as observers
- Test observation flow

### Step 4: Update Main Entry Point
- Initialize Smart City Foundation
- Pass to Runtime
- Coordinate lifecycle

---

## Next Steps

1. **Decide on order** (Smart City first vs Agents first)
2. **If Smart City first:**
   - Create new structure
   - Rebuild services using new pattern
   - Integrate with Runtime
3. **If Agents first:**
   - Proceed with Phase 3
   - Rebuild Smart City after agents
