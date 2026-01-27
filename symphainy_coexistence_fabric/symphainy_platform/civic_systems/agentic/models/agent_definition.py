"""
Agent Definition Model - Layer 1: Platform DNA

Agent Definition represents the stable, platform-owned identity of an agent.
This is who the agent is, what it's allowed to do, and how it behaves under pressure.

WHAT (Model Role): I define agent identity, capabilities, and permissions
HOW (Model Implementation): I use JSON Schema for validation and Supabase for storage

Key Principle: This is identity, not instruction. No prompt prose here.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import json


@dataclass
class AgentDefinition:
    """
    Agent Definition - Platform-owned, stable identity.
    
    This is Layer 1 of the 4-layer model:
    - Layer 1: AgentDefinition (Platform DNA - stable identity)
    - Layer 2: AgentPosture (Tenant/Solution - behavioral tuning)
    - Layer 3: AgentRuntimeContext (Journey/Session - ephemeral)
    - Layer 4: Prompt Assembly (derived at runtime)
    
    Attributes:
        agent_id: Unique agent identifier
        agent_type: Agent type (stateless, conversational, specialized, orchestrator)
        constitution: Agent constitution (role, mission, non_goals, guardrails)
        capabilities: List of agent capabilities
        permissions: Agent permissions (allowed_tools, allowed_mcp_servers, required_roles)
        collaboration_profile: Collaboration rules (can_delegate_to, can_be_invoked_by)
        version: Version string
        created_by: Creator identifier
    """
    
    agent_id: str
    agent_type: str  # "stateless", "conversational", "specialized", "orchestrator"
    constitution: Dict[str, Any]  # role, mission, non_goals, guardrails
    capabilities: List[str]
    permissions: Dict[str, Any]  # allowed_tools, allowed_mcp_servers, required_roles
    collaboration_profile: Dict[str, Any] = field(default_factory=dict)  # can_delegate_to, can_be_invoked_by
    version: str = "1.0.0"
    created_by: Optional[str] = None
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate agent definition against schema.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            import jsonschema
            jsonschema.validate(instance=self.to_dict(), schema=AGENT_DEFINITION_SCHEMA)
            return True, None
        except ImportError:
            # jsonschema not available - do basic validation
            if not self.agent_id:
                return False, "agent_id is required"
            if not self.agent_type:
                return False, "agent_type is required"
            if not self.constitution:
                return False, "constitution is required"
            if not self.capabilities:
                return False, "capabilities is required"
            return True, None
        except jsonschema.ValidationError as e:
            return False, f"Schema validation failed: {e.message}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "constitution": self.constitution,
            "capabilities": self.capabilities,
            "permissions": self.permissions,
            "collaboration_profile": self.collaboration_profile,
            "version": self.version,
            "created_by": self.created_by
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentDefinition":
        """Create from dictionary."""
        return cls(
            agent_id=data["agent_id"],
            agent_type=data["agent_type"],
            constitution=data["constitution"],
            capabilities=data["capabilities"],
            permissions=data.get("permissions", {}),
            collaboration_profile=data.get("collaboration_profile", {}),
            version=data.get("version", "1.0.0"),
            created_by=data.get("created_by")
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "AgentDefinition":
        """Create from JSON string."""
        return cls.from_dict(json.loads(json_str))


# JSON Schema for AgentDefinition validation
AGENT_DEFINITION_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "agent_id": {
            "type": "string",
            "description": "Unique agent identifier"
        },
        "agent_type": {
            "type": "string",
            "enum": ["stateless", "conversational", "specialized", "orchestrator"],
            "description": "Agent type"
        },
        "constitution": {
            "type": "object",
            "properties": {
                "role": {
                    "type": "string",
                    "description": "Agent's role (e.g., 'Journey Liaison')"
                },
                "mission": {
                    "type": "string",
                    "description": "Agent's mission statement"
                },
                "non_goals": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Things this agent should NOT do"
                },
                "guardrails": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Governance constraints and rules"
                }
            },
            "required": ["role", "mission"],
            "additionalProperties": True
        },
        "capabilities": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of agent capabilities",
            "minItems": 1
        },
        "permissions": {
            "type": "object",
            "properties": {
                "allowed_tools": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Tools this agent can use"
                },
                "allowed_mcp_servers": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "MCP servers this agent can access"
                },
                "required_roles": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Smart City roles required for this agent"
                }
            },
            "additionalProperties": True
        },
        "collaboration_profile": {
            "type": "object",
            "properties": {
                "can_delegate_to": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Agent IDs this agent can delegate to"
                },
                "can_be_invoked_by": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Agent IDs that can invoke this agent"
                }
            },
            "additionalProperties": True
        },
        "version": {
            "type": "string",
            "description": "Version string",
            "default": "1.0.0"
        },
        "created_by": {
            "type": ["string", "null"],
            "description": "Creator identifier"
        }
    },
    "required": ["agent_id", "agent_type", "constitution", "capabilities"],
    "additionalProperties": False
}
