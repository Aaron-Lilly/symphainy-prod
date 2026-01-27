"""
Agent Base - Core Agent Class

Base class for all agents with policy-governed collaboration support.

WHAT (Agent Role): I provide intelligent agent capabilities
HOW (Agent Implementation): I reason, collaborate, and produce proposals

Key Principle: Agents reason. They do not execute.
Agents may collaborate, but they may not commit.
"""

import sys
from pathlib import Path

# Add project root to path
# Find project root by looking for common markers (pyproject.toml, requirements.txt, etc.)
current = Path(__file__).resolve()
project_root = current
for _ in range(10):  # Max 10 levels up
    if (project_root / "pyproject.toml").exists() or (project_root / "requirements.txt").exists():
        break
    project_root = project_root.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from utilities import get_logger

from symphainy_platform.runtime.execution_context import ExecutionContext
from .collaboration.contribution_request import ContributionRequest, ContributionResponse
from .collaboration.collaboration_router import CollaborationRouter
from .models.agent_definition import AgentDefinition
from .models.agent_posture import AgentPosture
from .models.agent_runtime_context import AgentRuntimeContext
from .mcp_client_manager import MCPClientManager


class AgentBase(ABC):
    """
    Base class for all agents.
    
    Provides:
    - Request processing (abstract)
    - Agent description (abstract)
    - Platform integration (tools, session state)
    - Policy-governed collaboration
    - Structured output (proposals, blueprints, ranked options)
    """
    
    def __init__(
        self,
        agent_id: str,
        agent_type: str = None,
        capabilities: List[str] = None,
        # 4-Layer Model Support
        agent_definition: Optional[AgentDefinition] = None,  # Layer 1: Platform DNA
        agent_definition_id: Optional[str] = None,  # Load from registry
        agent_posture: Optional[AgentPosture] = None,  # Layer 2: Tenant/Solution
        agent_posture_id: Optional[str] = None,  # Load from registry
        tenant_id: Optional[str] = None,  # For posture lookup
        solution_id: Optional[str] = None,  # For posture lookup
        # Collaboration and Infrastructure
        collaboration_router: Optional[CollaborationRouter] = None,
        public_works: Optional[Any] = None,
        # Dependencies
        mcp_client_manager: Optional[MCPClientManager] = None,  # MCP integration
        agent_definition_registry: Optional[Any] = None,  # For loading definitions
        agent_posture_registry: Optional[Any] = None,  # For loading postures
        telemetry_service: Optional[Any] = None  # Telemetry
    ):
        """
        Initialize agent with 4-layer model support.
        
        Args:
            agent_id: Unique agent identifier
            agent_type: Agent type (prefer using agent_definition)
            capabilities: List of agent capabilities (prefer using agent_definition)
            agent_definition: AgentDefinition instance (Layer 1: Platform DNA) - RECOMMENDED
            agent_definition_id: Load definition from registry
            agent_posture: AgentPosture instance (Layer 2: Tenant/Solution)
            agent_posture_id: Load posture from registry
            tenant_id: Tenant identifier (for posture lookup)
            solution_id: Solution identifier (for posture lookup)
            collaboration_router: Optional collaboration router
            public_works: Optional Public Works Foundation Service
            mcp_client_manager: MCP Client Manager for tool access
            agent_definition_registry: Registry for loading definitions
            agent_posture_registry: Registry for loading postures
            telemetry_service: Telemetry service
        """
        # Initialize logger
        self.logger = get_logger(f"Agent:{agent_id}")
        
        # Load definition if definition_id provided
        if agent_definition_id and not agent_definition:
            if agent_definition_registry:
                # Async load will happen in initialize()
                self._agent_definition_id = agent_definition_id
            else:
                self.logger.warning(f"agent_definition_id provided but no registry available")
        
        # Load posture if posture_id provided (with fallback hierarchy)
        if agent_posture_id and not agent_posture:
            if agent_posture_registry:
                # Async load will happen in initialize()
                self._agent_posture_id = agent_posture_id
            else:
                self.logger.warning(f"agent_posture_id provided but no registry available")
        
        # Initialize with definition (Layer 1: Identity) - REQUIRED
        if agent_definition:
            self.agent_definition = agent_definition
            self.agent_id = agent_definition.agent_id
            self.agent_type = agent_definition.agent_type
            self.constitution = agent_definition.constitution
            self.capabilities = agent_definition.capabilities
            self.permissions = agent_definition.permissions
            self.collaboration_profile = agent_definition.collaboration_profile
        elif agent_definition_id:
            # Definition will be loaded in initialize()
            self.agent_id = agent_id
            self.agent_type = agent_type or "unknown"
            self.capabilities = capabilities or []
            self.constitution = {}
            self.permissions = {}
            self.collaboration_profile = {}
        else:
            # No definition provided - use direct parameters but log warning
            self.logger.warning(f"Agent {agent_id} initialized without AgentDefinition - this is deprecated")
            self.agent_id = agent_id
            self.agent_type = agent_type or "unknown"
            self.capabilities = capabilities or []
            self.constitution = {}
            self.permissions = {}
            self.collaboration_profile = {}
        
        # Initialize with posture (Layer 2: Behavioral tuning)
        if agent_posture:
            self.agent_posture = agent_posture
            self.posture = agent_posture.posture
            self.llm_defaults = agent_posture.llm_defaults
        else:
            self.agent_posture = None
            self.posture = {}
            self.llm_defaults = {}
        
        # Store dependencies
        self.collaboration_router = collaboration_router
        self.public_works = public_works
        self.mcp_client_manager = mcp_client_manager
        self.agent_definition_registry = agent_definition_registry
        self.agent_posture_registry = agent_posture_registry
        self.telemetry_service = telemetry_service
        self.tenant_id = tenant_id
        self.solution_id = solution_id
        
        # Track if initialized
        self._initialized = False
    
    async def process_request(
        self,
        request: Dict[str, Any],
        context: ExecutionContext,
        runtime_context: Optional[AgentRuntimeContext] = None
    ) -> Dict[str, Any]:
        """
        Process request with 4-layer model.
        
        Layers:
        1. Agent Definition (identity) - already loaded
        2. Agent Posture (behavior) - already loaded
        3. Runtime Context (hydration) - provided by orchestrator (call site responsibility)
        4. Prompt Assembly (derived) - assembled at call time
        
        ARCHITECTURAL PRINCIPLE: Runtime context is assembled by orchestrator (call site),
        not by agent. Agent treats it as read-only.
        
        Args:
            request: Request dictionary
            context: Runtime execution context
            runtime_context: Optional pre-assembled runtime context (from orchestrator)
        
        Returns:
            Dict with non-executing artifacts
        """
        # Ensure initialized (load definitions/postures if needed)
        if not self._initialized:
            await self._initialize_4_layer_model()
        
        # Layer 3: Use provided runtime context, or assemble if not provided (fallback)
        if runtime_context is None:
            # Fallback: Agent can assemble if orchestrator didn't provide (for backward compatibility)
            self.logger.debug("Runtime context not provided by orchestrator, assembling as fallback")
            runtime_context = await AgentRuntimeContext.from_request(request, context)
        else:
            # Use provided runtime context (read-only)
            self.logger.debug(f"Using runtime context provided by orchestrator: goal={runtime_context.journey_goal[:50] if runtime_context.journey_goal else 'none'}")
        
        # Layer 4: Assemble prompt (derived from layers 1-3)
        system_message = self._assemble_system_message(runtime_context)
        user_message = self._assemble_user_message(request, runtime_context)
        
        # Process with assembled prompt
        return await self._process_with_assembled_prompt(
            system_message=system_message,
            user_message=user_message,
            runtime_context=runtime_context,
            context=context
        )
    
    async def _initialize_4_layer_model(self):
        """Initialize 4-layer model (load definitions/postures if needed)."""
        try:
            # Load definition if needed
            if hasattr(self, '_agent_definition_id') and self.agent_definition_registry:
                definition = await self.agent_definition_registry.get_definition(self._agent_definition_id)
                if definition:
                    self.agent_definition = definition
                    self.agent_id = definition.agent_id
                    self.agent_type = definition.agent_type
                    self.constitution = definition.constitution
                    self.capabilities = definition.capabilities
                    self.permissions = definition.permissions
                    self.collaboration_profile = definition.collaboration_profile
            
            # Load posture if needed (with fallback hierarchy)
            if hasattr(self, '_agent_posture_id') and self.agent_posture_registry:
                posture = await self.agent_posture_registry.get_posture(
                    agent_id=self.agent_id,
                    tenant_id=self.tenant_id,
                    solution_id=self.solution_id
                )
                if posture:
                    self.agent_posture = posture
                    self.posture = posture.posture
                    self.llm_defaults = posture.llm_defaults
            
            # Initialize MCP Client Manager if available
            if self.mcp_client_manager and not self.mcp_client_manager._initialized:
                await self.mcp_client_manager.initialize()
            
            self._initialized = True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize 4-layer model: {e}", exc_info=True)
            # Continue with legacy mode
    
    def _assemble_system_message(self, runtime_context: AgentRuntimeContext) -> str:
        """
        Assemble system message from layers 1-3.
        
        This is where the magic happens - clean separation of concerns.
        """
        parts = []
        
        # Layer 1: Constitution (identity)
        if self.constitution:
            parts.append(f"You are the {self.constitution.get('role', 'Agent')}.")
            if self.constitution.get('mission'):
                parts.append(f"Mission: {self.constitution.get('mission')}")
            if self.constitution.get('non_goals'):
                parts.append("\nNon-goals:")
                for non_goal in self.constitution['non_goals']:
                    parts.append(f"  - {non_goal}")
            if self.constitution.get('guardrails'):
                parts.append("\nGuardrails:")
                for guardrail in self.constitution['guardrails']:
                    parts.append(f"  - {guardrail}")
        
        # Layer 2: Posture (behavioral tuning)
        if self.posture:
            parts.append("\nBehavioral Posture:")
            if self.posture.get('autonomy_level'):
                parts.append(f"  - Autonomy: {self.posture.get('autonomy_level')}")
            if self.posture.get('risk_tolerance'):
                parts.append(f"  - Risk Tolerance: {self.posture.get('risk_tolerance')}")
            if self.posture.get('compliance_mode'):
                parts.append(f"  - Compliance: {self.posture.get('compliance_mode')}")
            if self.posture.get('explain_decisions'):
                parts.append("  - Always explain your decisions")
        
        # Layer 3: Runtime Context (hydration)
        if runtime_context.business_context:
            parts.append("\nBusiness Context:")
            if runtime_context.business_context.get('industry'):
                parts.append(f"  - Industry: {runtime_context.business_context.get('industry')}")
            if runtime_context.business_context.get('systems'):
                parts.append(f"  - Systems: {', '.join(runtime_context.business_context['systems'])}")
            if runtime_context.business_context.get('constraints'):
                parts.append("  - Constraints:")
                for constraint in runtime_context.business_context['constraints']:
                    parts.append(f"    - {constraint}")
        
        if runtime_context.journey_goal:
            parts.append(f"\nCurrent Goal: {runtime_context.journey_goal}")
        
        return "\n".join(parts)
    
    def _assemble_user_message(
        self,
        request: Dict[str, Any],
        runtime_context: AgentRuntimeContext
    ) -> str:
        """
        Assemble user message from request and runtime context.
        
        Args:
            request: Request dictionary
            runtime_context: Runtime context
        
        Returns:
            User message string
        """
        # Extract user message from request
        user_message = request.get("message", request.get("prompt", request.get("goal", "")))
        
        # Add available artifacts if any
        if runtime_context.available_artifacts:
            user_message += f"\n\nAvailable artifacts: {', '.join(runtime_context.available_artifacts)}"
        
        # Add human preferences if any
        if runtime_context.human_preferences:
            prefs = []
            if runtime_context.human_preferences.get('detail_level'):
                prefs.append(f"Detail level: {runtime_context.human_preferences['detail_level']}")
            if runtime_context.human_preferences.get('wants_visuals'):
                prefs.append("Include visualizations")
            if prefs:
                user_message += f"\n\nPreferences: {', '.join(prefs)}"
        
        return user_message
    
    @abstractmethod
    async def _process_with_assembled_prompt(
        self,
        system_message: str,
        user_message: str,
        runtime_context: AgentRuntimeContext,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Process request with assembled prompt (abstract method).
        
        Subclasses implement this to handle the actual agent logic.
        
        Args:
            system_message: Assembled system message (from layers 1-3)
            user_message: Assembled user message
            runtime_context: Runtime context
            context: Execution context
        
        Returns:
            Dict with non-executing artifacts
        """
        pass
    
    @abstractmethod
    async def get_agent_description(self) -> str:
        """
        Get agent description for discovery.
        
        Returns:
            Agent description string
        """
        pass
    
    async def use_tool(
        self,
        tool_name: str,
        params: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Use a Smart City tool (via MCP) - REAL implementation.
        
        Args:
            tool_name: Tool name (e.g., "insights_extract_structured_data")
            params: Tool parameters
            context: Execution context
        
        Returns:
            Tool result
        """
        if not self.mcp_client_manager:
            self.logger.warning("MCP Client Manager not available, falling back to placeholder")
            return {
                "tool": tool_name,
                "params": params,
                "result": "tool_execution_placeholder",
                "status": "not_implemented",
                "note": "MCP Client Manager not available"
            }
        
        # Validate tool access (check allowed_tools from permissions)
        allowed_tools = self.permissions.get("allowed_tools", [])
        if allowed_tools and tool_name not in allowed_tools:
            self.logger.error(f"Tool {tool_name} not allowed for agent {self.agent_id}")
            return {
                "success": False,
                "error": f"Tool {tool_name} not allowed for agent {self.agent_id}"
            }
        
        # Resolve server name from tool name
        server_name = self._resolve_server_for_tool(tool_name)
        if not server_name:
            self.logger.error(f"Could not resolve server for tool {tool_name}")
            return {
                "success": False,
                "error": f"Could not resolve server for tool {tool_name}"
            }
        
        # Execute via MCP Client Manager
        try:
            from datetime import datetime
            start_time = datetime.utcnow()
            
            result = await self.mcp_client_manager.execute_tool(
                server_name=server_name,
                tool_name=tool_name,
                parameters=params,
                user_context={
                    "tenant_id": context.tenant_id,
                    "session_id": context.session_id,
                    "solution_id": context.solution_id
                }
            )
            
            # Calculate latency
            end_time = datetime.utcnow()
            latency_ms = (end_time - start_time).total_seconds() * 1000
            
            # Track tool usage (telemetry)
            await self._track_tool_usage(tool_name, params, result, context, latency_ms)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to execute tool {tool_name}: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def _resolve_server_for_tool(self, tool_name: str) -> Optional[str]:
        """
        Resolve MCP server name from tool name.
        
        Args:
            tool_name: Tool name (e.g., "insights_extract_structured_data")
        
        Returns:
            Server name (e.g., "insights_mcp") or None
        """
        # Tool naming convention: {realm}_{tool_name}
        # Extract realm prefix
        if tool_name.startswith("insights_"):
            return "insights_mcp"
        elif tool_name.startswith("content_"):
            return "content_mcp"
        elif tool_name.startswith("journey_"):
            return "journey_mcp"
        elif tool_name.startswith("outcomes_"):
            return "outcomes_mcp"
        else:
            # Try to find in allowed_mcp_servers
            allowed_servers = self.permissions.get("allowed_mcp_servers", [])
            if allowed_servers:
                # Return first allowed server (could be enhanced to be smarter)
                return allowed_servers[0]
            return None
    
    async def _track_tool_usage(
        self,
        tool_name: str,
        params: Dict[str, Any],
        result: Dict[str, Any],
        context: ExecutionContext,
        latency_ms: Optional[float] = None
    ):
        """Track tool usage for telemetry."""
        if self.telemetry_service:
            try:
                await self.telemetry_service.record_agent_tool_usage(
                    agent_id=self.agent_id,
                    tool_name=tool_name,
                    parameters=params,
                    result=result,
                    context=context,
                    latency_ms=latency_ms
                )
            except Exception as e:
                self.logger.debug(f"Telemetry tracking failed (non-critical): {e}")
    
    async def get_session_state(
        self,
        session_id: str,
        context: ExecutionContext
    ) -> Optional[Dict[str, Any]]:
        """
        Get session state (via Runtime).
        
        Args:
            session_id: Session identifier
            context: Execution context
        
        Returns:
            Session state dictionary, or None if not found
        """
        if context.state_surface:
            return await context.state_surface.get_session_state(session_id, context.tenant_id)
        return None
    
    async def request_contribution(
        self,
        agent_type: str,
        request: Dict[str, Any],
        context: ExecutionContext
    ) -> Optional[Dict[str, Any]]:
        """
        Request a bounded contribution from another agent (Policy-Governed).
        
        This is NOT orchestration - it's reasoning collaboration.
        Returns non-executing artifacts only (proposals, blueprints).
        
        Flow:
        1. Agent emits contribution_request
        2. Runtime asks Smart City primitives: Is this allowed?
        3. If allowed, Runtime routes to target agent
        4. Target agent returns non-executing artifact
        5. No side effects, no execution, no commits
        
        Args:
            agent_type: Type of agent to request contribution from
            request: Contribution request (purpose, constraints, data)
            context: Execution context
        
        Returns:
            Non-executing artifact (proposal, blueprint, ranked options), or None if failed
        """
        if not self.collaboration_router:
            self.logger.warning("Collaboration router not available")
            return None
        
        # Create contribution request
        contribution_request = ContributionRequest.create(
            caller_agent_id=self.agent_id,
            target_agent_type=agent_type,
            purpose=request.get("purpose", "collaboration"),
            request_data=request.get("data", {}),
            constraints=request.get("constraints", {}),
            session_id=context.session_id,
            execution_id=context.execution_id
        )
        
        # Route via collaboration router (validated by Smart City)
        # Note: In full implementation, this would go through Runtime
        # For MVP: Direct routing
        # Get agent registry from context if available
        agent_registry = None
        if hasattr(context, "agent_registry"):
            agent_registry = context.agent_registry
        elif hasattr(context, "state_surface") and hasattr(context.state_surface, "agent_registry"):
            agent_registry = context.state_surface.agent_registry
        
        response = await self.collaboration_router.route_contribution_request(
            contribution_request,
            agent_registry=agent_registry
        )
        
        if response:
            return {
                "artifact_type": response.artifact_type,
                "artifact": response.artifact,
                "confidence": response.confidence,
                "notes": response.notes
            }
        
        return None
    
    async def process_contribution_request(
        self,
        request: ContributionRequest
    ) -> ContributionResponse:
        """
        Process a contribution request from another agent.
        
        This is called by CollaborationRouter when routing requests.
        
        Args:
            request: Contribution request
        
        Returns:
            Contribution response with non-executing artifact
        """
        # Default implementation: Return empty artifact
        # Subclasses should override this
        return ContributionResponse(
            request_id=request.request_id,
            target_agent_id=self.agent_id,
            artifact_type="proposal",
            artifact={},
            confidence=0.0,
            notes="Not implemented"
        )
    
    def validate_output(self, output: Dict[str, Any]) -> bool:
        """
        Validate agent output (ensures "No Commit" rule).
        
        Args:
            output: Agent output dictionary
        
        Returns:
            True if output is valid (non-executing), False otherwise
        """
        # Check for forbidden output types
        forbidden_keys = ["state_mutation", "service_invocation", "execution_commit"]
        for key in forbidden_keys:
            if key in output:
                self.logger.error(f"Agent output contains forbidden key: {key}")
                return False
        
        # Check for allowed output types
        allowed_types = ["proposal", "blueprint", "ranked_options", "suggested_intents"]
        artifact_type = output.get("artifact_type", "")
        
        if artifact_type not in allowed_types:
            # Execution plan is only allowed if Solution-owned
            if artifact_type == "execution_plan" and output.get("solution_owned", False):
                return True
            if artifact_type:
                self.logger.warning(f"Unknown artifact type: {artifact_type}")
        
        return True
    
    async def _call_llm(
        self,
        prompt: str,
        system_message: str,
        model: str = "gpt-4o-mini",
        max_tokens: int = 1000,
        temperature: float = 0.3,
        user_context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        context: Optional[ExecutionContext] = None
    ) -> str:
        """
        Call LLM via agentic system (governed access with telemetry).
        
        This ensures:
        - Cost tracking
        - Rate limiting
        - Audit trail
        - Policy enforcement
        - Telemetry recording
        
        Args:
            prompt: User prompt
            system_message: System message
            model: Model name (default: gpt-4o-mini, can be overridden by posture)
            max_tokens: Maximum tokens (can be overridden by posture)
            temperature: Temperature (can be overridden by posture)
            user_context: Optional user context
            metadata: Optional metadata for tracking
            context: Optional execution context (for telemetry)
        
        Returns:
            Response text from LLM
        
        Raises:
            ValueError: If Public Works or LLM adapter not available
            RuntimeError: If LLM call fails
        """
        if not self.public_works:
            raise ValueError("Public Works not available - cannot access LLM adapter")
        
        llm_adapter = self.public_works.get_llm_adapter()
        if not llm_adapter:
            raise ValueError("LLM adapter not available - ensure OpenAI adapter is configured")
        
        # Override with posture LLM defaults if available
        if self.llm_defaults:
            model = self.llm_defaults.get("model", model)
            max_tokens = self.llm_defaults.get("max_tokens", max_tokens)
            temperature = self.llm_defaults.get("temperature", temperature)
        
        # Prepare request with governance metadata
        request = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        # Track usage (governance)
        self.logger.info(
            f"🤖 LLM call via agent {self.agent_id}: model={model}, "
            f"prompt_length={len(prompt)}, max_tokens={max_tokens}"
        )
        
        # Track start time for latency
        from datetime import datetime
        start_time = datetime.utcnow()
        
        try:
            # Call via adapter (with governance)
            response = await llm_adapter.generate_completion(request)
            
            # Calculate latency
            end_time = datetime.utcnow()
            latency_ms = (end_time - start_time).total_seconds() * 1000
            
            # Check for errors
            if "error" in response:
                error_msg = response["error"]
                self.logger.error(f"❌ LLM call failed: {error_msg}")
                
                # Record telemetry for failure
                if self.telemetry_service and context:
                    await self.telemetry_service.record_agent_execution(
                        agent_id=self.agent_id,
                        agent_name=getattr(self, 'agent_definition', {}).get('constitution', {}).get('role', self.agent_id) if hasattr(self, 'agent_definition') else self.agent_id,
                        prompt=prompt,
                        response="",
                        model_name=model,
                        tokens={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                        cost=0.0,
                        latency_ms=latency_ms,
                        context=context,
                        success=False,
                        error_message=error_msg
                    )
                
                raise RuntimeError(f"LLM call failed: {error_msg}")
            
            # Extract text from response
            choices = response.get("choices", [])
            if not choices:
                raise RuntimeError("LLM call returned no choices")
            
            content = choices[0].get("message", {}).get("content", "")
            
            # Extract usage info
            usage = response.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", 0)
            
            # Estimate cost (rough estimate: $0.00001 per token for GPT-4O-MINI)
            cost = total_tokens * 0.00001 if total_tokens > 0 else 0.0
            
            # Log usage (for cost tracking)
            self.logger.info(
                f"✅ LLM call completed: prompt_tokens={prompt_tokens}, "
                f"completion_tokens={completion_tokens}, "
                f"total_tokens={total_tokens}"
            )
            
            # Record telemetry
            if self.telemetry_service and context:
                await self.telemetry_service.record_agent_execution(
                    agent_id=self.agent_id,
                    agent_name=getattr(self, 'agent_definition', {}).get('constitution', {}).get('role', self.agent_id) if hasattr(self, 'agent_definition') else self.agent_id,
                    prompt=prompt,
                    response=content,
                    model_name=model,
                    tokens={
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "total_tokens": total_tokens
                    },
                    cost=cost,
                    latency_ms=latency_ms,
                    context=context,
                    success=True
                )
            
            return content
            
        except Exception as e:
            # Record telemetry for exception
            if self.telemetry_service and context:
                end_time = datetime.utcnow()
                latency_ms = (end_time - start_time).total_seconds() * 1000
                await self.telemetry_service.record_agent_execution(
                    agent_id=self.agent_id,
                    agent_name=getattr(self, 'agent_definition', {}).get('constitution', {}).get('role', self.agent_id) if hasattr(self, 'agent_definition') else self.agent_id,
                    prompt=prompt,
                    response="",
                    model_name=model,
                    tokens={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                    cost=0.0,
                    latency_ms=latency_ms,
                    context=context,
                    success=False,
                    error_message=str(e)
                )
            raise