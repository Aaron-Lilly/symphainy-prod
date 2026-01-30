"""
Reasoning Service (ctx.reasoning) - Agentic Integration

Wraps the Agentic civic system into a unified reasoning interface.

Components:
    - llm     → LLM completion (OpenAI, HuggingFace, etc.)
    - agents  → Agent registry and invocation

Usage:
    # LLM completion
    result = await ctx.reasoning.llm.complete(prompt, model="gpt-4")
    
    # Get an agent
    agent = ctx.reasoning.agents.get("guide_agent")
    
    # Invoke an agent
    result = await ctx.reasoning.agents.invoke("sop_generation_agent", params)
    
    # Multi-agent collaboration
    result = await ctx.reasoning.agents.collaborate([agent1, agent2], task)
"""

from dataclasses import dataclass, field
from typing import Any, Optional, Dict, List

from utilities import get_logger


@dataclass
class LLMService:
    """
    LLM Service - Language model completion.
    
    Wraps OpenAI and HuggingFace adapters from Public Works.
    """
    _openai_adapter: Optional[Any] = None
    _huggingface_adapter: Optional[Any] = None
    _default_model: str = "gpt-4"
    
    def __post_init__(self):
        self._logger = get_logger("LLMService")
    
    async def complete(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Complete a prompt using LLM.
        
        Args:
            prompt: The prompt to complete
            model: Model to use (default: gpt-4)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional model-specific parameters
        
        Returns:
            Dict with completion result
        """
        model = model or self._default_model
        
        # Route to appropriate adapter based on model
        if model.startswith("gpt") or model.startswith("o1"):
            return await self._complete_openai(prompt, model, temperature, max_tokens, **kwargs)
        elif model.startswith("hf-") or "huggingface" in model.lower():
            return await self._complete_huggingface(prompt, model, temperature, max_tokens, **kwargs)
        else:
            # Default to OpenAI
            return await self._complete_openai(prompt, model, temperature, max_tokens, **kwargs)
    
    async def _complete_openai(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> Dict[str, Any]:
        """Complete using OpenAI adapter."""
        if not self._openai_adapter:
            raise RuntimeError("OpenAI adapter not available. Check LLMService initialization.")
        
        try:
            # Use OpenAI adapter's completion method
            response = await self._openai_adapter.complete(
                prompt=prompt,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return {
                "content": response.get("content", ""),
                "model": model,
                "usage": response.get("usage", {}),
                "finish_reason": response.get("finish_reason", "stop")
            }
        except Exception as e:
            self._logger.error(f"OpenAI completion failed: {e}")
            raise
    
    async def _complete_huggingface(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> Dict[str, Any]:
        """Complete using HuggingFace adapter."""
        if not self._huggingface_adapter:
            raise RuntimeError("HuggingFace adapter not available. Check LLMService initialization.")
        
        try:
            response = await self._huggingface_adapter.generate(
                prompt=prompt,
                model=model.replace("hf-", ""),
                temperature=temperature,
                max_new_tokens=max_tokens,
                **kwargs
            )
            return {
                "content": response.get("generated_text", ""),
                "model": model,
                "usage": {},
                "finish_reason": "stop"
            }
        except Exception as e:
            self._logger.error(f"HuggingFace completion failed: {e}")
            raise
    
    async def embed(
        self,
        content: str,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate embeddings for content.
        
        Args:
            content: Text to embed
            model: Embedding model to use
        
        Returns:
            Dict with embedding vector and metadata
        """
        model = model or "text-embedding-ada-002"
        
        if not self._openai_adapter:
            raise RuntimeError("OpenAI adapter not available for embeddings.")
        
        try:
            response = await self._openai_adapter.embed(content=content, model=model)
            return {
                "embedding": response.get("embedding", []),
                "model": model,
                "dimensions": len(response.get("embedding", []))
            }
        except Exception as e:
            self._logger.error(f"Embedding generation failed: {e}")
            raise


@dataclass
class AgentService:
    """
    Agent Service - Agent registry and invocation.
    
    Wraps AgentRegistry from Agentic civic system.
    """
    _agent_registry: Optional[Any] = None
    _agent_factory: Optional[Any] = None
    
    def __post_init__(self):
        self._logger = get_logger("AgentService")
    
    def get(self, agent_id: str) -> Optional[Any]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: Agent identifier
        
        Returns:
            Agent instance or None
        """
        if not self._agent_registry:
            raise RuntimeError("AgentRegistry not available. Check AgentService initialization.")
        
        return self._agent_registry.get_agent(agent_id)
    
    def get_by_type(self, agent_type: str) -> Optional[Any]:
        """
        Get an agent by type.
        
        Args:
            agent_type: Agent type (e.g., "guide_agent", "sop_generation")
        
        Returns:
            Agent instance or None
        """
        if not self._agent_registry:
            raise RuntimeError("AgentRegistry not available. Check AgentService initialization.")
        
        return self._agent_registry.get_agent_by_type(agent_type)
    
    def list(self) -> List[Dict[str, Any]]:
        """
        List all registered agents.
        
        Returns:
            List of agent metadata
        """
        if not self._agent_registry:
            return []
        
        return self._agent_registry.list_agents()
    
    def list_types(self) -> List[str]:
        """
        List all registered agent types.
        
        Returns:
            List of agent type strings
        """
        if not self._agent_registry:
            return []
        
        return self._agent_registry.list_agent_types()
    
    async def invoke(
        self,
        agent_id: str,
        params: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Invoke an agent.
        
        Args:
            agent_id: Agent identifier
            params: Parameters for the agent
            context: Optional execution context
        
        Returns:
            Agent execution result
        """
        agent = self.get(agent_id)
        if not agent:
            raise ValueError(f"Agent not found: {agent_id}")
        
        try:
            # Most agents have a process() or execute() method
            if hasattr(agent, 'process'):
                result = await agent.process(params, context or {})
            elif hasattr(agent, 'execute'):
                result = await agent.execute(params, context or {})
            elif hasattr(agent, 'run'):
                result = await agent.run(params, context or {})
            else:
                raise AttributeError(f"Agent {agent_id} has no process/execute/run method")
            
            return {
                "agent_id": agent_id,
                "result": result,
                "status": "completed"
            }
        except Exception as e:
            self._logger.error(f"Agent invocation failed: {e}")
            return {
                "agent_id": agent_id,
                "error": str(e),
                "status": "failed"
            }
    
    async def invoke_by_type(
        self,
        agent_type: str,
        params: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Invoke an agent by type.
        
        Args:
            agent_type: Agent type
            params: Parameters for the agent
            context: Optional execution context
        
        Returns:
            Agent execution result
        """
        agent = self.get_by_type(agent_type)
        if not agent:
            raise ValueError(f"No agent found for type: {agent_type}")
        
        return await self.invoke(agent.agent_id, params, context)
    
    async def collaborate(
        self,
        agent_ids: List[str],
        task: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Multi-agent collaboration on a task.
        
        Args:
            agent_ids: List of agent IDs to collaborate
            task: Task definition
            context: Optional execution context
        
        Returns:
            Collaboration result
        """
        results = []
        current_context = context or {}
        
        for agent_id in agent_ids:
            try:
                result = await self.invoke(
                    agent_id,
                    {**task, "previous_results": results},
                    current_context
                )
                results.append(result)
                
                # Update context with results for next agent
                current_context["previous_agent"] = agent_id
                current_context["previous_result"] = result
                
            except Exception as e:
                self._logger.error(f"Collaboration failed at agent {agent_id}: {e}")
                results.append({
                    "agent_id": agent_id,
                    "error": str(e),
                    "status": "failed"
                })
        
        return {
            "agent_ids": agent_ids,
            "results": results,
            "status": "completed" if all(r.get("status") == "completed" for r in results) else "partial"
        }


@dataclass
class ReasoningService:
    """
    Unified reasoning interface wrapping Agentic civic system.
    
    Available via ctx.reasoning in PlatformContext.
    
    Components:
        - llm: LLM completion service
        - agents: Agent registry and invocation service
    """
    llm: LLMService = field(default_factory=LLMService)
    agents: AgentService = field(default_factory=AgentService)
    
    def __init__(self, public_works: Optional[Any] = None):
        """
        Initialize ReasoningService from Public Works.
        
        Args:
            public_works: Public Works foundation service
        """
        self._logger = get_logger("ReasoningService")
        self._public_works = public_works
        
        # Initialize LLM service
        self.llm = LLMService(
            _openai_adapter=getattr(public_works, 'openai_adapter', None) if public_works else None,
            _huggingface_adapter=getattr(public_works, 'huggingface_adapter', None) if public_works else None
        )
        
        # Initialize Agent service
        agent_registry = None
        agent_factory = None
        
        try:
            from symphainy_platform.civic_systems.agentic.agent_registry import AgentRegistry
            # AgentRegistry is typically a singleton or provided via service factory
            # For now, we'll create one - in production this should be injected
            agent_registry = AgentRegistry()
            self._logger.debug("✅ AgentRegistry initialized")
        except Exception as e:
            self._logger.warning(f"Failed to initialize AgentRegistry: {e}")
        
        try:
            from symphainy_platform.civic_systems.agentic.agent_factory import AgentFactory
            agent_factory = AgentFactory()
            self._logger.debug("✅ AgentFactory initialized")
        except Exception as e:
            self._logger.warning(f"Failed to initialize AgentFactory: {e}")
        
        self.agents = AgentService(
            _agent_registry=agent_registry,
            _agent_factory=agent_factory
        )
    
    def get_available_components(self) -> Dict[str, bool]:
        """
        Get availability status of reasoning components.
        
        Returns:
            Dict mapping component name to availability boolean
        """
        return {
            "llm_openai": self.llm._openai_adapter is not None,
            "llm_huggingface": self.llm._huggingface_adapter is not None,
            "agents": self.agents._agent_registry is not None,
            "agent_factory": self.agents._agent_factory is not None,
        }
