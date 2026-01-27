"""
Business Analysis Agent - Data Interpretation and Business Reasoning

Agent for reasoning about data meaning and generating business interpretations.

WHAT (Agent Role): I reason about data meaning and generate business interpretations
HOW (Agent Implementation): I use LLM to reason about data, use MCP tools to access data, construct business analysis outcomes

Key Principle: Agentic forward pattern - agent reasons, uses services as tools, constructs outcomes.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List

from utilities import get_logger
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.civic_systems.agentic.agent_base import AgentBase
from symphainy_platform.civic_systems.agentic.models.agent_runtime_context import AgentRuntimeContext


class BusinessAnalysisAgent(AgentBase):
    """
    Business Analysis Agent - Data interpretation and business reasoning.
    
    Uses agentic forward pattern:
    1. Get parsed data and embeddings via MCP tools
    2. Reason about data meaning (LLM)
    3. Identify data type in business terms (LLM)
    4. Generate business interpretations (LLM)
    5. Construct business analysis outcome
    
    ARCHITECTURAL PRINCIPLE: Agent reasons, services execute.
    """
    
    def __init__(
        self,
        agent_definition_id: str = "business_analysis_agent",
        public_works: Optional[Any] = None,
        agent_definition_registry: Optional[Any] = None,
        mcp_client_manager: Optional[Any] = None,
        telemetry_service: Optional[Any] = None,
        **kwargs
    ):
        """
        Initialize Business Analysis Agent.
        
        Args:
            agent_definition_id: Agent definition ID (loads from JSON config)
            public_works: Public Works Foundation Service (for accessing abstractions)
            agent_definition_registry: Registry for loading agent definitions
            mcp_client_manager: MCP Client Manager for tool access
            telemetry_service: Telemetry service
        """
        # Initialize AgentBase with 4-layer model support
        super().__init__(
            agent_id=agent_definition_id,
            agent_type="specialized",
            capabilities=["business_interpretation", "data_type_identification", "context_understanding"],
            agent_definition_id=agent_definition_id,
            public_works=public_works,
            agent_definition_registry=agent_definition_registry,
            mcp_client_manager=mcp_client_manager,
            telemetry_service=telemetry_service
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
            Dict with business analysis outcome artifacts
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
                # If still empty, try to infer from user_message
                if not request_data:
                    # Check if user_message contains parsed_file_id
                    if "parsed_file_id" in user_message.lower():
                        # Try to extract
                        import re
                        file_id_match = re.search(r'parsed_file_id["\']?\s*[:=]\s*["\']?([^"\'\s]+)', user_message)
                        if file_id_match:
                            request_data = {"type": "interpret_data", "parsed_file_id": file_id_match.group(1)}
                    else:
                        # Default: treat as interpret_data request
                        request_data = {"type": "interpret_data"}
        except (json.JSONDecodeError, ValueError):
            # Fallback: treat as interpret_data request
            request_data = {"type": "interpret_data"}
        
        # Use business context from runtime_context if available
        if runtime_context.business_context:
            request_data.setdefault("business_context", runtime_context.business_context)
        
        # Route to appropriate handler
        request_type = request_data.get("type", "interpret_data")
        
        if request_type == "interpret_data":
            return await self._handle_interpret_data(request_data, context)
        else:
            raise ValueError(f"Unknown request type: {request_type}")
    
    async def process_request(
        self,
        request: Dict[str, Any],
        context: ExecutionContext,
        runtime_context: Optional[AgentRuntimeContext] = None
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
            Dict with business analysis outcome artifacts
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
    
    async def _handle_interpret_data(
        self,
        request: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle data interpretation using agentic forward pattern.
        
        Pattern:
        1. Get parsed data via MCP tool
        2. Get semantic embeddings via MCP tool
        3. Reason about data meaning (LLM)
        4. Identify data type in business terms (LLM)
        5. Generate business interpretations (LLM)
        6. Construct business analysis outcome
        """
        parsed_file_id = request.get("parsed_file_id")
        if not parsed_file_id:
            raise ValueError("parsed_file_id is required for data interpretation")
        
        self.logger.info(f"Interpreting data for parsed_file_id={parsed_file_id} via agentic forward pattern")
        
        # Step 1: Get parsed data via MCP tool
        parsed_data_result = await self.use_tool(
            "insights_get_parsed_data",
            {"parsed_file_id": parsed_file_id},
            context
        )
        
        if not parsed_data_result or not parsed_data_result.get("success"):
            raise ValueError(f"Failed to retrieve parsed data for {parsed_file_id}")
        
        parsed_data = parsed_data_result.get("parsed_data", {})
        
        # Step 2: Get semantic embeddings via MCP tool
        embeddings_result = await self.use_tool(
            "insights_get_embeddings",
            {"parsed_file_id": parsed_file_id},
            context
        )
        
        embeddings = []
        if embeddings_result and embeddings_result.get("success"):
            embeddings = embeddings_result.get("embeddings", [])
        
        # Step 3: Reason about data meaning (LLM)
        data_meaning = await self._reason_about_data_meaning(
            parsed_data=parsed_data,
            embeddings=embeddings,
            context=context
        )
        
        # Step 4: Identify data type in business terms (LLM)
        business_data_type = await self._identify_business_data_type(
            parsed_data=parsed_data,
            embeddings=embeddings,
            data_meaning=data_meaning,
            context=context
        )
        
        # Step 5: Generate business interpretations (LLM)
        business_interpretation = await self._generate_business_interpretation(
            parsed_data=parsed_data,
            embeddings=embeddings,
            data_meaning=data_meaning,
            business_data_type=business_data_type,
            context=context
        )
        
        # Step 6: Construct business analysis outcome
        outcome = {
            "parsed_file_id": parsed_file_id,
            "business_data_type": business_data_type.get("type"),
            "business_data_type_description": business_data_type.get("description"),
            "business_interpretation": business_interpretation.get("interpretation"),
            "key_insights": business_interpretation.get("insights", []),
            "business_implications": business_interpretation.get("implications", []),
            "confidence": business_interpretation.get("confidence", 0.0),
            "data_meaning": data_meaning,
            "reasoning": business_interpretation.get("reasoning", "")
        }
        
        return {
            "artifact_type": "business_analysis",
            "artifact": outcome,
            "reasoning": business_interpretation.get("reasoning", "")
        }
    
    async def _reason_about_data_meaning(
        self,
        parsed_data: Dict[str, Any],
        embeddings: List[Dict[str, Any]],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Reason about what the data represents using LLM.
        
        Args:
            parsed_data: Parsed file data
            embeddings: Semantic embeddings
            context: Execution context
        
        Returns:
            Dict with data meaning analysis
        """
        # Extract key information from parsed data
        data_structure = parsed_data.get("structure", {})
        columns = data_structure.get("columns", []) if isinstance(data_structure, dict) else []
        sample_data = parsed_data.get("data", [])[:5]  # First 5 rows
        
        # Extract semantic meanings from embeddings
        semantic_info = []
        for emb in embeddings[:10]:  # First 10 embeddings
            semantic_info.append({
                "column": emb.get("column_name", ""),
                "meaning": emb.get("semantic_meaning", ""),
                "type": emb.get("column_type", "")
            })
        
        # Build prompt for LLM reasoning
        system_message = """You are a business analyst analyzing data to understand what it represents.

Your task is to reason about the data structure, content, and semantic meaning to determine what business context this data fits into.

Consider:
- Column names and types
- Sample data values
- Semantic meanings from embeddings
- Patterns in the data
- Business domain indicators

Return a structured analysis of what the data represents."""
        
        user_message = f"""Analyze this data:

Data Structure:
- Columns: {[col.get('name', col) if isinstance(col, dict) else col for col in columns]}
- Sample Data: {sample_data[:3]}

Semantic Information:
{chr(10).join([f"- {si['column']}: {si['meaning']} ({si['type']})" for si in semantic_info[:5]])}

What does this data represent? What business context does it fit into?"""
        
        try:
            reasoning_text = await self._call_llm(
                prompt=user_message,
                system_message=system_message,
                model="gpt-4o-mini",
                max_tokens=500,
                temperature=0.3,
                context=context
            )
            
            return {
                "meaning": reasoning_text,
                "columns_analyzed": len(columns),
                "embeddings_analyzed": len(embeddings)
            }
        except Exception as e:
            self.logger.warning(f"LLM reasoning failed: {e}")
            return {
                "meaning": "Unable to determine data meaning",
                "error": str(e)
            }
    
    async def _identify_business_data_type(
        self,
        parsed_data: Dict[str, Any],
        embeddings: List[Dict[str, Any]],
        data_meaning: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Identify data type in business terms (e.g., "aging report", "claim report").
        
        Args:
            parsed_data: Parsed file data
            embeddings: Semantic embeddings
            data_meaning: Data meaning analysis
            context: Execution context
        
        Returns:
            Dict with business data type identification
        """
        system_message = """You are a business analyst identifying data types in business terms.

Based on the data structure, content, and semantic meaning, identify what type of business document or report this is.

Examples:
- "aging report" for collections/accounts receivable data
- "claim report" for insurance claims data
- "policy data" for insurance policy information
- "customer data" for customer information
- "transaction data" for financial transactions

Return the data type and a brief description."""
        
        user_message = f"""Data Meaning Analysis:
{data_meaning.get('meaning', 'No meaning determined')}

What type of business document or report is this? Provide:
1. Data type (e.g., "aging_report", "claim_report", "policy_data")
2. Description (1-2 sentences explaining what this data represents)"""
        
        try:
            response_text = await self._call_llm(
                prompt=user_message,
                system_message=system_message,
                model="gpt-4o-mini",
                max_tokens=200,
                temperature=0.3,
                context=context
            )
            
            # Parse response to extract type and description
            lines = response_text.strip().split('\n')
            data_type = "unknown"
            description = response_text
            
            for line in lines:
                if "data type" in line.lower() or "type:" in line.lower():
                    # Extract type
                    if ":" in line:
                        data_type = line.split(":")[-1].strip().lower().replace(" ", "_")
                elif "description" in line.lower() or len(line) > 20:
                    description = line.strip()
            
            return {
                "type": data_type if data_type != "unknown" else "general_data",
                "description": description,
                "confidence": 0.8 if data_type != "unknown" else 0.5
            }
        except Exception as e:
            self.logger.warning(f"Business data type identification failed: {e}")
            return {
                "type": "unknown",
                "description": "Unable to identify business data type",
                "confidence": 0.0
            }
    
    async def _generate_business_interpretation(
        self,
        parsed_data: Dict[str, Any],
        embeddings: List[Dict[str, Any]],
        data_meaning: Dict[str, Any],
        business_data_type: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Generate business interpretation with insights and implications.
        
        Args:
            parsed_data: Parsed file data
            embeddings: Semantic embeddings
            data_meaning: Data meaning analysis
            business_data_type: Business data type identification
            context: Execution context
        
        Returns:
            Dict with business interpretation, insights, and implications
        """
        system_message = """You are a business analyst generating interpretations and insights.

Based on the data analysis, generate:
1. A clear business interpretation of what the data represents
2. Key insights (patterns, trends, notable observations)
3. Business implications (what this means for the business)
4. Confidence level (0.0 to 1.0)

Be specific and actionable. Use business language, not technical jargon."""
        
        sample_data = parsed_data.get("data", [])[:3]
        
        user_message = f"""Generate business interpretation:

Data Type: {business_data_type.get('type')} - {business_data_type.get('description')}

Data Meaning: {data_meaning.get('meaning', 'No meaning determined')}

Sample Data: {sample_data}

Generate:
1. Business interpretation (2-3 sentences)
2. Key insights (3-5 bullet points)
3. Business implications (2-3 bullet points)
4. Confidence level (0.0 to 1.0)"""
        
        try:
            response_text = await self._call_llm(
                prompt=user_message,
                system_message=system_message,
                model="gpt-4o-mini",
                max_tokens=800,
                temperature=0.3,
                context=context
            )
            
            # Parse response to extract structured information
            interpretation = response_text
            insights = []
            implications = []
            confidence = business_data_type.get("confidence", 0.7)
            
            # Try to extract structured sections
            lines = response_text.split('\n')
            current_section = None
            
            for line in lines:
                line_lower = line.lower().strip()
                if "interpretation" in line_lower or "business interpretation" in line_lower:
                    current_section = "interpretation"
                elif "insights" in line_lower or "key insights" in line_lower:
                    current_section = "insights"
                elif "implications" in line_lower or "business implications" in line_lower:
                    current_section = "implications"
                elif "confidence" in line_lower:
                    # Extract confidence number
                    import re
                    conf_match = re.search(r'0\.\d+|1\.0', line)
                    if conf_match:
                        confidence = float(conf_match.group())
                elif line.strip().startswith('-') or line.strip().startswith('•'):
                    # Bullet point
                    if current_section == "insights":
                        insights.append(line.strip().lstrip('-•').strip())
                    elif current_section == "implications":
                        implications.append(line.strip().lstrip('-•').strip())
            
            return {
                "interpretation": interpretation,
                "insights": insights if insights else ["Data analysis completed"],
                "implications": implications if implications else ["Further analysis may be needed"],
                "confidence": confidence,
                "reasoning": response_text
            }
        except Exception as e:
            self.logger.warning(f"Business interpretation generation failed: {e}")
            return {
                "interpretation": f"This appears to be {business_data_type.get('description', 'data')}.",
                "insights": ["Data analysis completed"],
                "implications": ["Further analysis may be needed"],
                "confidence": 0.5,
                "reasoning": f"Interpretation generated with limited context: {str(e)}"
            }
    
    async def get_agent_description(self) -> str:
        """Get agent description (required by AgentBase)."""
        return "Business Analysis Agent - Provides data interpretation and business reasoning"