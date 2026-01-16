"""
Solution Builder - Builder for Creating Solutions

Provides builder pattern for creating Solutions.

WHAT (Platform SDK Role): I provide a builder for creating Solutions
HOW (Platform SDK Implementation): I use builder pattern with validation

Key Principle: Solutions are built using the builder pattern.
This ensures Solutions are correctly configured before creation.
"""

from typing import Dict, Any, List, Optional

from utilities import get_logger, generate_event_id
from .solution_model import Solution, SolutionContext, DomainServiceBinding, SyncStrategy
from .solution_registry import SolutionRegistry


class SolutionBuilder:
    """
    Builder for creating Solutions.
    
    Provides fluent API for building Solutions with validation.
    """
    
    def __init__(self, solution_id: Optional[str] = None):
        """
        Initialize solution builder.
        
        Args:
            solution_id: Optional solution ID (generated if not provided)
        """
        self.solution_id = solution_id or generate_event_id()
        self.solution_context: Optional[SolutionContext] = None
        self.domain_service_bindings: List[DomainServiceBinding] = []
        self.sync_strategies: List[SyncStrategy] = []
        self.supported_intents: List[str] = []
        self.metadata: Dict[str, Any] = {}
        self.logger = get_logger(self.__class__.__name__)
    
    def with_context(
        self,
        goals: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None,
        risk: str = "Low",
        metadata: Optional[Dict[str, Any]] = None
    ) -> "SolutionBuilder":
        """
        Set solution context.
        
        Args:
            goals: Solution goals
            constraints: Solution constraints
            risk: Risk level
            metadata: Optional context metadata
        
        Returns:
            Self for method chaining
        """
        self.solution_context = SolutionContext(
            goals=goals or [],
            constraints=constraints or [],
            risk=risk,
            metadata=metadata or {}
        )
        return self
    
    def add_domain_binding(
        self,
        domain: str,
        system_name: str,
        adapter_type: str,
        adapter_config: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "SolutionBuilder":
        """
        Add domain service binding.
        
        Args:
            domain: Domain name (e.g., "content", "insights")
            system_name: External system name
            adapter_type: Adapter type (e.g., "mainframe_adapter", "rest_adapter")
            adapter_config: Optional adapter configuration
            metadata: Optional binding metadata
        
        Returns:
            Self for method chaining
        """
        binding = DomainServiceBinding(
            domain=domain,
            system_name=system_name,
            adapter_type=adapter_type,
            adapter_config=adapter_config or {},
            metadata=metadata or {}
        )
        self.domain_service_bindings.append(binding)
        return self
    
    def add_sync_strategy(
        self,
        strategy_type: str,
        conflict_resolution: str,
        sync_interval: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "SolutionBuilder":
        """
        Add sync strategy.
        
        Args:
            strategy_type: Strategy type (e.g., "bi_directional", "unidirectional")
            conflict_resolution: Conflict resolution method
            sync_interval: Optional sync interval in seconds
            metadata: Optional strategy metadata
        
        Returns:
            Self for method chaining
        """
        strategy = SyncStrategy(
            strategy_type=strategy_type,
            conflict_resolution=conflict_resolution,
            sync_interval=sync_interval,
            metadata=metadata or {}
        )
        self.sync_strategies.append(strategy)
        return self
    
    def register_intents(self, intent_types: List[str]) -> "SolutionBuilder":
        """
        Register supported intents.
        
        Args:
            intent_types: List of supported intent types
        
        Returns:
            Self for method chaining
        """
        self.supported_intents.extend(intent_types)
        return self
    
    def with_metadata(self, metadata: Dict[str, Any]) -> "SolutionBuilder":
        """
        Add solution metadata.
        
        Args:
            metadata: Solution metadata
        
        Returns:
            Self for method chaining
        """
        self.metadata.update(metadata)
        return self
    
    def build(self) -> Solution:
        """
        Build the Solution.
        
        Returns:
            Created Solution
        
        Raises:
            ValueError: If solution is invalid
        """
        # Ensure solution context is set
        if not self.solution_context:
            self.solution_context = SolutionContext()
        
        # Create solution
        solution = Solution(
            solution_id=self.solution_id,
            solution_context=self.solution_context,
            domain_service_bindings=self.domain_service_bindings,
            sync_strategies=self.sync_strategies,
            supported_intents=self.supported_intents,
            metadata=self.metadata,
        )
        
        # Validate solution
        is_valid, error = solution.validate()
        if not is_valid:
            raise ValueError(f"Invalid solution: {error}")
        
        self.logger.info(f"Solution built: {self.solution_id}")
        return solution
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "SolutionBuilder":
        """
        Create solution builder from configuration dictionary.
        
        Args:
            config: Configuration dictionary with solution definition
        
        Returns:
            SolutionBuilder instance
        """
        builder = cls(solution_id=config.get("solution_id"))
        
        # Set context
        context_config = config.get("context", {})
        builder.with_context(
            goals=context_config.get("goals", []),
            constraints=context_config.get("constraints", []),
            risk=context_config.get("risk", "Low"),
            metadata=context_config.get("metadata", {})
        )
        
        # Add domain bindings
        for binding_config in config.get("domain_service_bindings", []):
            builder.add_domain_binding(
                domain=binding_config["domain"],
                system_name=binding_config["system_name"],
                adapter_type=binding_config["adapter_type"],
                adapter_config=binding_config.get("adapter_config", {}),
                metadata=binding_config.get("metadata", {})
            )
        
        # Add sync strategies
        for strategy_config in config.get("sync_strategies", []):
            builder.add_sync_strategy(
                strategy_type=strategy_config["strategy_type"],
                conflict_resolution=strategy_config["conflict_resolution"],
                sync_interval=strategy_config.get("sync_interval"),
                metadata=strategy_config.get("metadata", {})
            )
        
        # Register intents
        builder.register_intents(config.get("supported_intents", []))
        
        # Add metadata
        builder.with_metadata(config.get("metadata", {}))
        
        return builder
    
    def build_and_register(self, registry: SolutionRegistry) -> Solution:
        """
        Build solution and register it in the registry.
        
        Args:
            registry: Solution registry
        
        Returns:
            Created and registered Solution
        
        Raises:
            ValueError: If solution is invalid or registration fails
        """
        solution = self.build()
        
        if not registry.register_solution(solution):
            raise ValueError(f"Failed to register solution: {self.solution_id}")
        
        return solution