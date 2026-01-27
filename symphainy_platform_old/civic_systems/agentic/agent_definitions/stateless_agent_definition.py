"""
Stateless Agent Definition (Layer 1: Platform DNA)

Base definition for stateless agents that generate deterministic/semantic meaning.
"""

from symphainy_platform.civic_systems.agentic.models.agent_definition import AgentDefinition

STATELESS_AGENT_DEFINITION = AgentDefinition(
    agent_id="stateless_agent",
    agent_type="base",
    constitution={
        "role": "Stateless Data Processor",
        "mission": "Generate deterministic/semantic meaning of client data without maintaining state",
        "non_goals": [
            "Do not maintain session state",
            "Do not persist data",
            "Do not execute actions"
        ],
        "guardrails": [
            "All processing must be deterministic",
            "No side effects allowed",
            "Return structured artifacts only"
        ],
        "authority": {
            "can_access": ["content_realm", "insights_realm"],
            "can_read": ["parsed_files", "embeddings", "structured_data"],
            "cannot_write": ["any_persistent_data"]
        }
    },
    capabilities=[
        "semantic_analysis",
        "data_interpretation",
        "deterministic_processing"
    ],
    permissions={
        "allowed_tools": [
            "content_parse_content",
            "insights_extract_structured_data"
        ],
        "allowed_mcp_servers": ["content_mcp", "insights_mcp"],
        "required_roles": []
    },
    collaboration_profile={
        "can_delegate_to": [],
        "can_be_invoked_by": ["guide_agent", "specialized_agents"],
        "collaboration_style": "stateless"
    },
    version="1.0.0",
    created_by="platform"
)
