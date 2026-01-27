"""
Agent Posture Model - Layer 2: Tenant/Solution Scoped

Agent Posture represents behavioral tuning for a specific tenant or solution.
This is how the agent should behave in this environment.

WHAT (Model Role): I define agent behavioral tuning per tenant/solution
HOW (Model Implementation): I use JSON Schema for validation and Supabase for storage

Key Principle: This is behavioral tuning, not identity. Changes slowly and deliberately.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import json


@dataclass
class AgentPosture:
    """
    Agent Posture - Tenant/Solution scoped behavioral tuning.
    
    This is Layer 2 of the 4-layer model:
    - Layer 1: AgentDefinition (Platform DNA - stable identity)
    - Layer 2: AgentPosture (Tenant/Solution - behavioral tuning)
    - Layer 3: AgentRuntimeContext (Journey/Session - ephemeral)
    - Layer 4: Prompt Assembly (derived at runtime)
    
    Attributes:
        agent_id: Agent identifier (references AgentDefinition)
        tenant_id: Tenant identifier (None = platform default)
        solution_id: Solution identifier (None = tenant default)
        posture: Behavioral posture (autonomy_level, risk_tolerance, compliance_mode, etc.)
        llm_defaults: LLM configuration defaults (model, temperature, max_tokens, etc.)
        custom_properties: Custom properties for extensibility
        version: Version string
        created_by: Creator identifier
    """
    
    agent_id: str
    tenant_id: Optional[str] = None  # None = platform default
    solution_id: Optional[str] = None  # None = tenant default
    posture: Dict[str, Any] = field(default_factory=dict)  # autonomy_level, risk_tolerance, etc.
    llm_defaults: Dict[str, Any] = field(default_factory=dict)  # model, temperature, max_tokens
    custom_properties: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"
    created_by: Optional[str] = None
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate agent posture against schema.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            import jsonschema
            jsonschema.validate(instance=self.to_dict(), schema=AGENT_POSTURE_SCHEMA)
            return True, None
        except ImportError:
            # jsonschema not available - do basic validation
            if not self.agent_id:
                return False, "agent_id is required"
            if not self.posture:
                return False, "posture is required"
            if not self.llm_defaults:
                return False, "llm_defaults is required"
            return True, None
        except jsonschema.ValidationError as e:
            return False, f"Schema validation failed: {e.message}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "agent_id": self.agent_id,
            "tenant_id": self.tenant_id,
            "solution_id": self.solution_id,
            "posture": self.posture,
            "llm_defaults": self.llm_defaults,
            "custom_properties": self.custom_properties,
            "version": self.version,
            "created_by": self.created_by
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentPosture":
        """Create from dictionary."""
        return cls(
            agent_id=data["agent_id"],
            tenant_id=data.get("tenant_id"),
            solution_id=data.get("solution_id"),
            posture=data.get("posture", {}),
            llm_defaults=data.get("llm_defaults", {}),
            custom_properties=data.get("custom_properties", {}),
            version=data.get("version", "1.0"),
            created_by=data.get("created_by")
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "AgentPosture":
        """Create from JSON string."""
        return cls.from_dict(json.loads(json_str))


# JSON Schema for AgentPosture validation
AGENT_POSTURE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "agent_id": {
            "type": "string",
            "description": "Agent identifier (references AgentDefinition)"
        },
        "tenant_id": {
            "type": ["string", "null"],
            "description": "Tenant identifier (None = platform default)"
        },
        "solution_id": {
            "type": ["string", "null"],
            "description": "Solution identifier (None = tenant default)"
        },
        "posture": {
            "type": "object",
            "properties": {
                "autonomy_level": {
                    "type": "string",
                    "enum": ["autonomous", "guided", "supervised"],
                    "description": "Level of agent autonomy"
                },
                "risk_tolerance": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "Risk tolerance level"
                },
                "human_interaction_style": {
                    "type": "string",
                    "enum": ["collaborative", "delegative", "autonomous"],
                    "description": "How agent interacts with humans"
                },
                "compliance_mode": {
                    "type": "string",
                    "enum": ["strict", "moderate", "permissive"],
                    "description": "Compliance strictness level"
                },
                "explain_decisions": {
                    "type": "boolean",
                    "description": "Whether agent should explain decisions"
                }
            },
            "additionalProperties": True,
            "required": []
        },
        "llm_defaults": {
            "type": "object",
            "properties": {
                "model": {
                    "type": "string",
                    "description": "Default LLM model (e.g., 'gpt-4o-mini')"
                },
                "temperature": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 2.0,
                    "description": "Default temperature"
                },
                "max_tokens": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Default max tokens"
                },
                "timeout": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Default timeout in seconds"
                }
            },
            "additionalProperties": True,
            "required": []
        },
        "custom_properties": {
            "type": "object",
            "additionalProperties": True,
            "description": "Custom properties for extensibility"
        },
        "version": {
            "type": "string",
            "description": "Version string",
            "default": "1.0"
        },
        "created_by": {
            "type": ["string", "null"],
            "description": "Creator identifier"
        }
    },
    "required": ["agent_id", "posture", "llm_defaults"],
    "additionalProperties": False
}
