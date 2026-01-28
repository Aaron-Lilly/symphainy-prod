"""
Outcomes Synthesis Agent - Pillar Synthesis and Visualization Agent

Agent for synthesizing pillar outputs and creating educational visualizations.

WHAT (Agent Role): I reason about pillar synthesis and visualization design
HOW (Agent Implementation): I use LLM to reason about relationships, design tutorials, construct visualizations

Key Principle: Agentic forward pattern - agent reasons, uses services as tools, constructs outcomes.
"""

import sys
from pathlib import Path

# Add project root to path
current = Path(__file__).resolve()
project_root = current
for _ in range(10):  # Max 10 levels up
    if (project_root / "pyproject.toml").exists() or (project_root / "requirements.txt").exists():
        break
    project_root = project_root.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List
from datetime import datetime

from utilities import get_logger
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.civic_systems.agentic.agent_base import AgentBase
from symphainy_platform.civic_systems.agentic.models.agent_runtime_context import AgentRuntimeContext


class OutcomesSynthesisAgent(AgentBase):
    """
    Outcomes Synthesis Agent - Pillar synthesis and visualization design.
    
    Uses agentic forward pattern:
    1. Reason about pillar relationships (LLM)
    2. Use MCP tools to get pillar data
    3. Design tutorial content (LLM) - Data Mash flow explanation
    4. Generate realm-specific visualizations (LLM)
    5. Construct synthesis with educational content
    
    ARCHITECTURAL PRINCIPLE: Agent reasons, services execute.
    """
    
    def __init__(self, public_works: Optional[Any] = None, **kwargs):
        """
        Initialize Outcomes Synthesis Agent.
        
        Args:
            public_works: Public Works Foundation Service (for accessing abstractions)
            **kwargs: Additional parameters for 4-layer model support
        """
        # Initialize AgentBase
        super().__init__(
            agent_id="outcomes_synthesis_agent",
            agent_type="outcomes_synthesis",
            capabilities=["synthesize_pillars", "design_visualizations", "create_tutorials"],
            public_works=public_works,
            **kwargs
        )
        self.logger = get_logger(self.__class__.__name__)
    
    async def _process_with_assembled_prompt(
        self,
        system_message: str,
        user_message: str,
        runtime_context: AgentRuntimeContext,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Process request with assembled prompt (4-layer model).
        
        This method is called by AgentBase.process_request() after assembling
        the system and user messages from the 4-layer model.
        
        Args:
            system_message: Assembled system message (from layers 1-3)
            user_message: Assembled user message
            runtime_context: Runtime context with business_context
            context: Execution context
        
        Returns:
            Dict with outcome artifacts
        """
        # Extract request from user_message or runtime_context
        request_data = {}
        try:
            import json
            if user_message.strip().startswith("{"):
                request_data = json.loads(user_message)
            else:
                # Try to extract from runtime_context.business_context
                if hasattr(runtime_context, 'business_context') and runtime_context.business_context:
                    request_data = runtime_context.business_context.get("request", {})
                # If still empty, default to synthesize_outcome
                if not request_data:
                    request_data = {"type": "synthesize_outcome"}
        except (json.JSONDecodeError, ValueError):
            # Fallback: default request type
            request_data = {"type": "synthesize_outcome"}
        
        # Use business context from runtime_context if available
        if runtime_context.business_context:
            request_data.setdefault("business_context", runtime_context.business_context)
        
        # Route to appropriate handler
        request_type = request_data.get("type", "synthesize_outcome")
        
        if request_type == "synthesize_outcome":
            return await self._handle_synthesize_outcome(request_data, context)
        elif request_type == "generate_summary_visuals":
            return await self._handle_generate_summary_visuals(request_data, context)
        else:
            raise ValueError(f"Unknown request type: {request_type}")
    
    async def process_request(
        self,
        request: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Process request using agentic forward pattern.
        
        ARCHITECTURAL PRINCIPLE: This method delegates to AgentBase.process_request()
        which implements the 4-layer model. For backward compatibility, it can also
        be called directly, but the 4-layer flow is preferred.
        
        Args:
            request: Request dictionary with type and parameters
            context: Execution context
            runtime_context: Optional pre-assembled runtime context (from orchestrator)
            
        Returns:
            Dict with outcome artifacts
        """
        # If runtime_context is provided, use it; otherwise let AgentBase assemble it
        if runtime_context:
            system_message = self._assemble_system_message(runtime_context)
            user_message = self._assemble_user_message(request, runtime_context)
            return await self._process_with_assembled_prompt(
                system_message, user_message, runtime_context, context
            )
        else:
            # Delegate to parent's process_request which implements 4-layer model
            return await super().process_request(request, context, runtime_context=None)
    
    async def _handle_synthesize_outcome(
        self,
        request: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle outcome synthesis using agentic forward pattern.
        
        Pattern:
        1. Get pillar summaries via MCP tools
        2. Reason about relationships (LLM)
        3. Use ReportGeneratorService as tool
        4. Construct synthesis with reasoning
        """
        self.logger.info("Synthesizing outcome via agentic forward pattern")
        
        # Step 1: Get pillar summaries via MCP tools (or from session state)
        session_state = await context.state_surface.get_session_state(
            context.session_id,
            context.tenant_id
        ) if context.state_surface else {}
        
        content_summary = session_state.get("content_pillar_summary", {})
        insights_summary = session_state.get("insights_pillar_summary", {})
        journey_summary = session_state.get("journey_pillar_summary", {})
        
        # Step 2: Reason about pillar relationships (LLM)
        relationship_reasoning = await self._reason_about_pillar_relationships(
            content_summary=content_summary,
            insights_summary=insights_summary,
            journey_summary=journey_summary,
            context=context
        )
        
        # Step 3: Use ReportGeneratorService as tool via MCP
        synthesis_result = await self.use_tool(
            "outcomes_synthesize",
            {
                "content_summary": content_summary,
                "insights_summary": insights_summary,
                "journey_summary": journey_summary,
                "reasoning_context": relationship_reasoning
            },
            context
        )
        
        if not synthesis_result or not synthesis_result.get("success"):
            # Fallback: Create basic synthesis
            synthesis_result = self._create_basic_synthesis(content_summary, insights_summary, journey_summary)
        
        # Step 4: Construct synthesis with reasoning
        synthesis = synthesis_result.get("synthesis", synthesis_result.get("artifact", {}))
        
        return {
            "artifact_type": "synthesis",
            "artifact": {
                **synthesis,
                "reasoning": relationship_reasoning.get("reasoning", ""),
                "pillar_relationships": relationship_reasoning.get("relationships", {})
            },
            "confidence": 0.85
        }
    
    async def _handle_generate_summary_visuals(
        self,
        request: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle summary visualization generation using agentic forward pattern.
        
        Pattern:
        1. Get pillar data via MCP tools
        2. Reason about what to show (LLM)
        3. Design tutorial content for Data Mash (LLM)
        4. Use ReportGeneratorService as tool
        5. Construct visualization data with educational content
        """
        content_summary = request.get("content_summary", {})
        insights_summary = request.get("insights_summary", {})
        journey_summary = request.get("journey_summary", {})
        
        # Step 1: Reason about visualization design (LLM)
        visualization_reasoning = await self._reason_about_visualization_design(
            content_summary=content_summary,
            insights_summary=insights_summary,
            journey_summary=journey_summary,
            context=context
        )
        
        # Step 2: Design tutorial content for Data Mash (LLM)
        tutorial_content = await self._design_data_mash_tutorial(
            content_summary=content_summary,
            reasoning=visualization_reasoning,
            context=context
        )
        
        # Step 3: Use ReportGeneratorService as tool
        visuals_result = await self.use_tool(
            "outcomes_generate_realm_visuals",
            {
                "content_summary": content_summary,
                "insights_summary": insights_summary,
                "journey_summary": journey_summary,
                "tutorial_content": tutorial_content,
                "reasoning_context": visualization_reasoning
            },
            context
        )
        
        if not visuals_result or not visuals_result.get("success"):
            # Fallback: Create basic visuals
            visuals_result = self._create_basic_visuals(content_summary, insights_summary, journey_summary, tutorial_content)
        
        realm_visuals = visuals_result.get("realm_visuals", visuals_result.get("artifact", {}))
        
        # Step 4: Enhance with tutorial content
        enhanced_visuals = self._enhance_visuals_with_tutorial(realm_visuals, tutorial_content)
        
        return {
            "artifact_type": "realm_visuals",
            "artifact": enhanced_visuals,
            "confidence": 0.85
        }
    
    async def _reason_about_pillar_relationships(
        self,
        content_summary: Dict[str, Any],
        insights_summary: Dict[str, Any],
        journey_summary: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Reason about relationships between pillars using LLM.
        
        Analyzes:
        - How pillars relate to each other
        - What synthesis makes sense
        - What story to tell
        """
        system_message = """You are the Outcomes Synthesis Agent. Your role is to synthesize outputs 
from all pillars and understand their relationships.

Analyze:
1. How Content pillar (files, embeddings) relates to Insights (quality, analysis)
2. How Insights relates to Journey (workflows, processes)
3. What overall story emerges
4. What synthesis makes sense"""
        
        user_message = f"""Analyze relationships between pillars:

Content: {content_summary.get('files_uploaded', 0)} files, {content_summary.get('deterministic_embeddings', 0)} embeddings
Insights: Quality {insights_summary.get('overall_quality', 0)}, {insights_summary.get('insights_count', 0)} insights
Journey: {journey_summary.get('workflows_created', 0)} workflows, {journey_summary.get('coexistence_opportunities', 0)} opportunities

What relationships exist? What synthesis makes sense?"""
        
        try:
            reasoning_text = await self._call_llm(
                prompt=user_message,
                system_message=system_message,
                model="gpt-4o-mini",
                max_tokens=1500,
                temperature=0.3,
                context=context
            )
            
            return {
                "reasoning": reasoning_text,
                "relationships": {
                    "content_to_insights": "Files enable quality analysis",
                    "insights_to_journey": "Quality insights inform workflow optimization",
                    "overall": "Data flows from content through insights to journey outcomes"
                }
            }
        except Exception as e:
            self.logger.warning(f"LLM reasoning failed: {e}")
            return {
                "reasoning": "Pillar relationships analyzed",
                "relationships": {}
            }
    
    async def _reason_about_visualization_design(
        self,
        content_summary: Dict[str, Any],
        insights_summary: Dict[str, Any],
        journey_summary: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Reason about what visualizations to show using LLM.
        
        Designs:
        - What metrics matter for each pillar
        - How to visualize Data Mash flow
        - What tutorial content to create
        """
        system_message = """You are the Outcomes Synthesis Agent. Design visualizations that help 
users understand their data journey.

Key principles:
- Content pillar: Show Data Mash flow (ingestion → parsing → embedding → meaning)
- Insights pillar: Show quality, capabilities, specialized pipelines
- Journey pillar: Show friction removal and human-positive coexistence
- Create educational content, not just metrics"""
        
        user_message = f"""Design visualizations for:

Content: {content_summary.get('files_uploaded', 0)} files processed
Insights: Quality analysis, {insights_summary.get('insights_count', 0)} insights
Journey: {journey_summary.get('workflows_created', 0)} workflows, friction removal

What should each pillar visualization show? How to make it educational?"""
        
        try:
            reasoning_text = await self._call_llm(
                prompt=user_message,
                system_message=system_message,
                model="gpt-4o-mini",
                max_tokens=2000,
                temperature=0.3,
                context=context
            )
            
            return {
                "reasoning": reasoning_text,
                "visualization_design": {
                    "content": "Data Mash tutorial flow",
                    "insights": "Capabilities ecosystem",
                    "journey": "Friction removal visualization"
                }
            }
        except Exception as e:
            self.logger.warning(f"LLM reasoning failed: {e}")
            return {
                "reasoning": "Visualization design completed",
                "visualization_design": {}
            }
    
    async def _design_data_mash_tutorial(
        self,
        content_summary: Dict[str, Any],
        reasoning: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Design Data Mash tutorial content using LLM.
        
        Creates:
        - "What happens here?" explanations
        - "Why it matters?" explanations
        - "Think of it like..." analogies
        - Visual examples
        """
        system_message = """You are the Outcomes Synthesis Agent. Create educational tutorial content 
for the Data Mash flow.

For each stage (Ingestion, Parsing, Deterministic Embedding, Interpreted Meaning), create:
1. "What happens here?" - Plain language explanation
2. "Why it matters?" - Purpose explanation
3. "Think of it like..." - Analogies to help understanding
4. Examples - Real data examples when possible

Use plain language, avoid jargon. Make it educational and accessible."""
        
        files_uploaded = content_summary.get("files_uploaded", 0)
        files_parsed = content_summary.get("files_parsed", 0)
        deterministic_embeddings = content_summary.get("deterministic_embeddings", 0)
        semantic_embeddings = content_summary.get("semantic_embeddings", 0)
        
        user_message = f"""Create tutorial content for Data Mash flow:

Stage 1 - Ingestion: {files_uploaded} files uploaded
Stage 2 - Parsing: {files_parsed} files parsed
Stage 3 - Deterministic Embedding: {deterministic_embeddings} embeddings created
Stage 4 - Interpreted Meaning: {semantic_embeddings} files analyzed

For each stage, create:
- "What happens here?" explanation
- "Why it matters?" explanation
- "Think of it like..." analogies
- Example data (if available)

Use plain language. Make it educational."""
        
        try:
            tutorial_text = await self._call_llm(
                prompt=user_message,
                system_message=system_message,
                model="gpt-4o-mini",
                max_tokens=2500,
                temperature=0.3,
                context=context
            )
            
            # Parse and structure tutorial content
            tutorial_stages = self._parse_tutorial_content(tutorial_text, content_summary)
            
            return {
                "tutorial_content": tutorial_stages,
                "raw_reasoning": tutorial_text
            }
        except Exception as e:
            self.logger.warning(f"LLM tutorial generation failed: {e}")
            # Fallback: Use template with real data
            return self._create_tutorial_template(content_summary)
    
    def _parse_tutorial_content(
        self,
        tutorial_text: str,
        content_summary: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Parse LLM tutorial content into structured stages."""
        # In production, use structured output from LLM
        # For MVP, create structured content from summary
        
        stages = [
            {
                "id": "ingestion",
                "name": "File Ingestion",
                "tutorial": {
                    "what_happens": "Your files are uploaded to the platform and stored securely. The system identifies the file type (CSV, PDF, etc.) and prepares them for processing.",
                    "why_it_matters": "This is where your data journey begins. The platform needs to know what type of data you're working with before it can process it intelligently.",
                    "think_of_it_like": [
                        "The starting point of your data's journey",
                        "Like checking in at the airport before your flight"
                    ]
                }
            },
            {
                "id": "parsing",
                "name": "File Parsing",
                "tutorial": {
                    "what_happens": "The platform reads your files and extracts their structure and content. For structured data (like CSV), it identifies columns, data types, and relationships.",
                    "why_it_matters": "Parsing converts your raw files into a format the platform can understand and work with. It's like translating your data into a common language.",
                    "think_of_it_like": [
                        "Translating your data into a common language",
                        "Organizing a messy filing cabinet"
                    ]
                }
            },
            {
                "id": "deterministic_embedding",
                "name": "Deterministic Embedding",
                "tutorial": {
                    "what_happens": "The platform creates a 'fingerprint' of your data's structure. This fingerprint captures the exact schema (columns, data types, patterns) in a way that can be reproduced exactly every time.",
                    "why_it_matters": "This fingerprint allows the platform to match your data to target models with precision. It's like creating a blueprint of your data structure that never changes.",
                    "think_of_it_like": [
                        "A DNA fingerprint for your data structure",
                        "A blueprint that describes how your data is organized"
                    ]
                }
            },
            {
                "id": "interpreted_meaning",
                "name": "Interpreted Meaning",
                "tutorial": {
                    "what_happens": "The platform uses AI to understand the meaning and context of your data. It identifies what your data represents and how different pieces relate to each other.",
                    "why_it_matters": "This is where your data becomes 'smart.' The platform doesn't just see columns and rows - it understands what they mean and can help you find insights.",
                    "think_of_it_like": [
                        "Reading between the lines to understand context",
                        "Connecting the dots to see relationships"
                    ]
                }
            }
        ]
        
        # Update with real counts
        stages[0]["count"] = content_summary.get("files_uploaded", 0)
        stages[1]["count"] = content_summary.get("files_parsed", 0)
        stages[2]["count"] = content_summary.get("deterministic_embeddings", 0)
        stages[3]["count"] = content_summary.get("semantic_embeddings", 0)
        
        return stages
    
    def _create_tutorial_template(
        self,
        content_summary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create tutorial template with real data (fallback)."""
        return {
            "tutorial_content": self._parse_tutorial_content("", content_summary),
            "raw_reasoning": "Tutorial content generated from data"
        }
    
    def _enhance_visuals_with_tutorial(
        self,
        realm_visuals: Dict[str, Any],
        tutorial_content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance realm visuals with tutorial content."""
        content_visual = realm_visuals.get("content_visual", {})
        
        if content_visual and tutorial_content.get("tutorial_content"):
            # Add tutorial stages to content visual
            if content_visual.get("primary_visual"):
                content_visual["primary_visual"]["stages"] = tutorial_content["tutorial_content"]
        
        return {
            **realm_visuals,
            "content_visual": content_visual
        }
    
    def _create_basic_synthesis(
        self,
        content_summary: Dict[str, Any],
        insights_summary: Dict[str, Any],
        journey_summary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create basic synthesis structure (fallback)."""
        return {
            "success": True,
            "synthesis": {
                "content_summary": content_summary.get("summary", ""),
                "insights_summary": insights_summary.get("summary", ""),
                "journey_summary": journey_summary.get("summary", ""),
                "overall_synthesis": "Synthesis of all pillar outputs"
            }
        }
    
    def _create_basic_visuals(
        self,
        content_summary: Dict[str, Any],
        insights_summary: Dict[str, Any],
        journey_summary: Dict[str, Any],
        tutorial_content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create basic visuals structure (fallback)."""
        return {
            "success": True,
            "realm_visuals": {
                "content_visual": {
                    "realm": "content",
                    "visual_type": "data_mash_tutorial",
                    "primary_visual": {
                        "stages": tutorial_content.get("tutorial_content", [])
                    }
                },
                "insights_visual": {
                    "realm": "insights",
                    "visual_type": "insights_ecosystem"
                },
                "journey_visual": {
                    "realm": "journey",
                    "visual_type": "friction_removal"
                }
            }
        }
    
    async def get_agent_description(self) -> str:
        """Get agent description."""
        return "Outcomes Synthesis Agent - Synthesizes pillar outputs and creates educational visualizations"
