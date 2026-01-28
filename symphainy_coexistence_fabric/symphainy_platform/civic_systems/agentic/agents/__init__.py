"""
Agents - Canonical Agent Implementations

All agents belong here in civic_systems/agentic/agents/.
Agents reason and produce proposals - they do NOT call services directly.
Agents call MCP tools exposed by orchestrators/solutions.

Organization:
- Base classes: Define agent types and patterns
- Specialized agents: Implement specific capabilities
- Liaison agents: Coordinate between realms/domains

Usage:
    from symphainy_platform.civic_systems.agentic.agents import GuideAgent
    from symphainy_platform.civic_systems.agentic.agents import BlueprintCreationAgent
"""

# === BASE CLASSES ===
from .stateless_agent import StatelessAgentBase
from .stateless_embedding_agent import StatelessEmbeddingAgent
from .conversational_agent import ConversationalAgentBase
from .eda_analysis_agent import EDAAnalysisAgentBase
from .workflow_optimization_agent import WorkflowOptimizationAgentBase
from .proposal_agent import ProposalAgentBase

# === CORE AGENTS ===
from .guide_agent import GuideAgent
from .structured_extraction_agent import StructuredExtractionAgent
from .embedding_agent import EmbeddingService as EmbeddingAgent
from .semantic_signal_extractor import SemanticSignalExtractor

# === CONTENT REALM AGENTS ===
from .content_liaison_agent import ContentLiaisonAgent

# === INSIGHTS REALM AGENTS ===
from .insights_liaison_agent import InsightsLiaisonAgent
from .business_analysis_agent import BusinessAnalysisAgent
from .insights_eda_agent import InsightsEDAAgent

# === OPERATIONS/JOURNEY REALM AGENTS ===
from .operations_liaison_agent import OperationsLiaisonAgent
from .journey_liaison_agent import JourneyLiaisonAgent
from .coexistence_analysis_agent import CoexistenceAnalysisAgent
from .sop_generation_agent import SOPGenerationAgent
from .workflow_optimization_specialist import WorkflowOptimizationSpecialist

# === OUTCOMES REALM AGENTS ===
from .outcomes_liaison_agent import OutcomesLiaisonAgent
from .outcomes_synthesis_agent import OutcomesSynthesisAgent
from .poc_generation_agent import POCGenerationAgent
from .blueprint_creation_agent import BlueprintCreationAgent
from .roadmap_generation_agent import RoadmapGenerationAgent
from .roadmap_proposal_agent import RoadmapProposalAgent

__all__ = [
    # Base classes
    "StatelessAgentBase",
    "StatelessEmbeddingAgent",
    "ConversationalAgentBase",
    "EDAAnalysisAgentBase",
    "WorkflowOptimizationAgentBase",
    "ProposalAgentBase",
    
    # Core agents
    "GuideAgent",
    "StructuredExtractionAgent",
    "EmbeddingAgent",
    "SemanticSignalExtractor",
    
    # Content realm
    "ContentLiaisonAgent",
    
    # Insights realm
    "InsightsLiaisonAgent",
    "BusinessAnalysisAgent",
    "InsightsEDAAgent",
    
    # Operations/Journey realm
    "OperationsLiaisonAgent",
    "JourneyLiaisonAgent",
    "CoexistenceAnalysisAgent",
    "SOPGenerationAgent",
    "WorkflowOptimizationSpecialist",
    
    # Outcomes realm
    "OutcomesLiaisonAgent",
    "OutcomesSynthesisAgent",
    "POCGenerationAgent",
    "BlueprintCreationAgent",
    "RoadmapGenerationAgent",
    "RoadmapProposalAgent",
]
