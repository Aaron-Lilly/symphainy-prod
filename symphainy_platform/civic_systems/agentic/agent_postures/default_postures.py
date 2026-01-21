"""
Default Agent Postures (Layer 2: Tenant/Solution Scoped)

Pre-configured postures for common scenarios.
"""

from symphainy_platform.civic_systems.agentic.models.agent_posture import AgentPosture

# Default posture (platform-wide)
DEFAULT_POSTURE = AgentPosture(
    agent_id="*",  # Wildcard for all agents
    tenant_id=None,  # Platform default
    solution_id=None,
    posture={
        "autonomy_level": "guided",
        "risk_tolerance": "medium",
        "human_interaction_style": "collaborative",
        "compliance_mode": "standard",
        "explain_decisions": True
    },
    llm_defaults={
        "model": "gpt-4o-mini",
        "temperature": 0.3,
        "max_tokens": 2000
    },
    custom_properties={},
    version="1.0",
    created_by="platform"
)

# Conservative posture (high compliance, low risk)
CONSERVATIVE_POSTURE = AgentPosture(
    agent_id="*",
    tenant_id=None,
    solution_id=None,
    posture={
        "autonomy_level": "supervised",
        "risk_tolerance": "low",
        "human_interaction_style": "confirmatory",
        "compliance_mode": "strict",
        "explain_decisions": True,
        "require_confirmation": True
    },
    llm_defaults={
        "model": "gpt-4o-mini",
        "temperature": 0.1,
        "max_tokens": 1500
    },
    custom_properties={},
    version="1.0",
    created_by="platform"
)

# Exploratory posture (high autonomy, experimental)
EXPLORATORY_POSTURE = AgentPosture(
    agent_id="*",
    tenant_id=None,
    solution_id=None,
    posture={
        "autonomy_level": "autonomous",
        "risk_tolerance": "high",
        "human_interaction_style": "informative",
        "compliance_mode": "relaxed",
        "explain_decisions": False,
        "allow_experimentation": True
    },
    llm_defaults={
        "model": "gpt-4o",
        "temperature": 0.7,
        "max_tokens": 4000
    },
    custom_properties={},
    version="1.0",
    created_by="platform"
)

# Production posture (balanced, reliable)
PRODUCTION_POSTURE = AgentPosture(
    agent_id="*",
    tenant_id=None,
    solution_id=None,
    posture={
        "autonomy_level": "guided",
        "risk_tolerance": "medium",
        "human_interaction_style": "collaborative",
        "compliance_mode": "standard",
        "explain_decisions": True,
        "performance_optimized": True
    },
    llm_defaults={
        "model": "gpt-4o-mini",
        "temperature": 0.3,
        "max_tokens": 2000
    },
    custom_properties={},
    version="1.0",
    created_by="platform"
)
