"""
Runtime Services Container

Container for all long-lived runtime services.
Makes ownership explicit and testable.

CTO Guidance: "Who keeps things alive?"
- Redis clients must stay alive
- StateSurface must be singleton
- ExecutionLifecycleManager must be singleton
- Artifact registries must be stable
- PlatformContextFactory must be singleton

This object owns all of them.
"""

from dataclasses import dataclass
from typing import Optional, Any


@dataclass
class RuntimeServices:
    """
    Container for all long-lived runtime services.
    
    This object owns all services and keeps them alive for the lifetime
    of the runtime process.
    
    Key Principle: FastAPI should not create these. Routes should not create these.
    They should only *receive* them.
    """
    # Foundation layer
    public_works: Any  # PublicWorksFoundationService
    
    # Runtime layer
    state_surface: Any  # StateSurface
    execution_lifecycle_manager: Any  # ExecutionLifecycleManager
    
    # Abstractions (from PublicWorksFoundationService)
    registry_abstraction: Any  # RegistryAbstraction
    artifact_storage: Any  # ArtifactStorageAbstraction
    file_storage: Any  # FileStorageAbstraction
    
    # Optional services
    wal: Optional[Any] = None  # WriteAheadLog
    intent_registry: Optional[Any] = None  # IntentRegistry
    solution_registry: Optional[Any] = None  # SolutionRegistry
    solution_services: Optional[Any] = None  # SolutionServices (all platform solutions)
    
    # Platform SDK (new architecture)
    platform_context_factory: Optional[Any] = None  # PlatformContextFactory
    
    def __post_init__(self):
        """Validate that required services are present."""
        required = [
            'public_works',
            'state_surface',
            'execution_lifecycle_manager',
            'registry_abstraction',
            'artifact_storage',
            'file_storage'
        ]
        
        for field in required:
            if getattr(self, field) is None:
                raise ValueError(f"Required service {field} is None")
