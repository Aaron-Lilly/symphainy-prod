"""
Solution Model - Solution Schema and Binding Model

Defines the formal structure for Solutions.

WHAT (Platform SDK Role): I define what Solutions look like
HOW (Platform SDK Implementation): I provide Solution schema and validation

Key Principle: The platform runs Solutions; Solutions run systems.
Solutions bind domain services to external systems.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime

from utilities import get_logger, get_clock


@dataclass
class SolutionContext:
    """Solution context (goals, constraints, risk)."""
    goals: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    risk: str = "Low"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "goals": self.goals,
            "constraints": self.constraints,
            "risk": self.risk,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SolutionContext":
        """Create from dictionary."""
        return cls(
            goals=data.get("goals", []),
            constraints=data.get("constraints", []),
            risk=data.get("risk", "Low"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class DomainServiceBinding:
    """Domain service binding to external system."""
    domain: str  # e.g., "content", "insights"
    system_name: str  # External system name
    adapter_type: str  # e.g., "mainframe_adapter", "rest_adapter"
    adapter_config: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "domain": self.domain,
            "system_name": self.system_name,
            "adapter_type": self.adapter_type,
            "adapter_config": self.adapter_config,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DomainServiceBinding":
        """Create from dictionary."""
        return cls(
            domain=data["domain"],
            system_name=data["system_name"],
            adapter_type=data["adapter_type"],
            adapter_config=data.get("adapter_config", {}),
            metadata=data.get("metadata", {}),
        )


@dataclass
class SyncStrategy:
    """Sync strategy for keeping external systems in sync."""
    strategy_type: str  # e.g., "bi_directional", "unidirectional", "event_driven"
    conflict_resolution: str  # e.g., "last_write_wins", "merge", "manual"
    sync_interval: Optional[int] = None  # Optional sync interval in seconds
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "strategy_type": self.strategy_type,
            "conflict_resolution": self.conflict_resolution,
            "sync_interval": self.sync_interval,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SyncStrategy":
        """Create from dictionary."""
        return cls(
            strategy_type=data["strategy_type"],
            conflict_resolution=data["conflict_resolution"],
            sync_interval=data.get("sync_interval"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class Solution:
    """
    Solution - The vehicle for running systems.
    
    A Solution:
    - defines solution context (goals, constraints, risk)
    - declares supported intents
    - binds domain services to external systems
    """
    solution_id: str
    solution_context: SolutionContext
    domain_service_bindings: List[DomainServiceBinding] = field(default_factory=list)
    sync_strategies: List[SyncStrategy] = field(default_factory=list)
    supported_intents: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: get_clock().now_utc())
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate solution structure.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate required fields
        if not self.solution_id:
            return False, "solution_id is required"
        
        if not self.solution_context:
            return False, "solution_context is required"
        
        # Validate domain service bindings
        for binding in self.domain_service_bindings:
            if not binding.domain:
                return False, "domain_service_binding.domain is required"
            if not binding.system_name:
                return False, "domain_service_binding.system_name is required"
            if not binding.adapter_type:
                return False, "domain_service_binding.adapter_type is required"
        
        # Validate sync strategies
        for strategy in self.sync_strategies:
            if not strategy.strategy_type:
                return False, "sync_strategy.strategy_type is required"
            if not strategy.conflict_resolution:
                return False, "sync_strategy.conflict_resolution is required"
        
        return True, None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert solution to dictionary."""
        return {
            "solution_id": self.solution_id,
            "solution_context": self.solution_context.to_dict(),
            "domain_service_bindings": [b.to_dict() for b in self.domain_service_bindings],
            "sync_strategies": [s.to_dict() for s in self.sync_strategies],
            "supported_intents": self.supported_intents,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Solution":
        """Create solution from dictionary."""
        return cls(
            solution_id=data["solution_id"],
            solution_context=SolutionContext.from_dict(data["solution_context"]),
            domain_service_bindings=[
                DomainServiceBinding.from_dict(b)
                for b in data.get("domain_service_bindings", [])
            ],
            sync_strategies=[
                SyncStrategy.from_dict(s)
                for s in data.get("sync_strategies", [])
            ],
            supported_intents=data.get("supported_intents", []),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data.get("created_at", get_clock().now_utc().isoformat())),
        )
