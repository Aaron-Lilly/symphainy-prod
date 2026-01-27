"""
Stateless Embedding Agent - Lightweight Governance for Embedding Generation

Lightweight agent for embedding generation with governance.
Uses HuggingFaceAdapter via Public Works for actual embedding generation.

WHAT (Agent Role): I provide governed access to embedding generation
HOW (Agent Implementation): I wrap HuggingFaceAdapter calls with governance (tracking, audit)

Key Principle: Lightweight governance - all external calls must be tracked, but without CrewAI overhead.
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

from typing import Dict, Any, List, Optional
from ..agent_base import AgentBase
from symphainy_platform.runtime.execution_context import ExecutionContext


class StatelessEmbeddingAgent(AgentBase):
    """
    Stateless Embedding Agent - Lightweight governance for embedding generation.
    
    Purpose: Provide governed access to HuggingFaceAdapter for embedding generation.
    Ensures all embedding calls are tracked (cost, usage, audit) without heavy agent overhead.
    """
    
    def __init__(
        self,
        agent_id: str = "stateless_embedding_agent",
        capabilities: List[str] = None,
        collaboration_router=None,
        public_works: Optional[Any] = None,
        **kwargs
    ):
        """
        Initialize Stateless Embedding Agent.
        
        Args:
            agent_id: Agent identifier
            capabilities: List of capabilities (default: ["embedding_generation"])
            collaboration_router: Optional collaboration router
            public_works: Public Works Foundation Service (REQUIRED for HuggingFaceAdapter access)
        """
        if capabilities is None:
            capabilities = ["embedding_generation"]
        
        super().__init__(
            agent_id=agent_id,
            agent_type="stateless_embedding",
            capabilities=capabilities,
            collaboration_router=collaboration_router,
            public_works=public_works
        )
        
        if not public_works:
            self.logger.warning("Public Works not provided - embedding generation will fail")
    
    async def process_request(
        self,
        request: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Process embedding generation request.
        
        Args:
            request: Request dictionary with 'text' and optional 'model'
            context: Execution context
        
        Returns:
            Dict with embedding result
        """
        text = request.get("text")
        if not text:
            return {
                "artifact_type": "error",
                "artifact": {"error": "text parameter required"},
                "confidence": 0.0
            }
        
        model = request.get("model", "sentence-transformers/all-mpnet-base-v2")
        
        # Generate embedding via governed access
        result = await self.generate_embedding(text, model, context)
        
        return {
            "artifact_type": "embedding",
            "artifact": result,
            "confidence": 1.0
        }
    
    async def _process_with_assembled_prompt(
        self,
        system_message: str,
        user_message: str,
        runtime_context: Any,  # AgentRuntimeContext
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
            Dict with embedding result:
            {
                "artifact_type": "embedding",
                "artifact": {
                    "embedding": List[float],
                    "model": str,
                    "dimension": int
                },
                "confidence": float
            }
        """
        # Extract text from runtime_context.business_context or user_message
        text = None
        model = "sentence-transformers/all-mpnet-base-v2"
        
        # Try to get from business_context first
        if hasattr(runtime_context, 'business_context') and runtime_context.business_context:
            text = runtime_context.business_context.get("text")
            model = runtime_context.business_context.get("model", model)
        
        # Fallback to user_message if text not found
        if not text:
            # Try to extract from user_message (could be the text itself or in a structured format)
            text = user_message.strip()
            # If user_message looks like JSON, try to parse it
            if text.startswith("{") or text.startswith("["):
                try:
                    import json
                    parsed = json.loads(text)
                    if isinstance(parsed, dict):
                        text = parsed.get("text", text)
                        model = parsed.get("model", model)
                except (json.JSONDecodeError, ValueError):
                    pass  # Use user_message as-is
        
        if not text:
            return {
                "artifact_type": "error",
                "artifact": {"error": "text parameter required for embedding generation"},
                "confidence": 0.0
            }
        
        # Generate embedding via governed access
        try:
            result = await self.generate_embedding(text, model, context)
            return {
                "artifact_type": "embedding",
                "artifact": result,
                "confidence": 1.0
            }
        except Exception as e:
            self.logger.error(f"Embedding generation failed in _process_with_assembled_prompt: {e}")
            return {
                "artifact_type": "error",
                "artifact": {"error": str(e)},
                "confidence": 0.0
            }
    
    async def get_agent_description(self) -> str:
        """Get agent description."""
        return f"Stateless Embedding Agent ({self.agent_id}) - Governed embedding generation via HuggingFace"
    
    async def generate_embedding(
        self,
        text: str,
        model: str = "sentence-transformers/all-mpnet-base-v2",
        context: Optional[ExecutionContext] = None
    ) -> Dict[str, Any]:
        """
        Generate embedding via HuggingFaceAdapter with governance.
        
        This method ensures:
        - Usage tracking (cost, metadata, audit)
        - Error handling
        - Governance compliance
        
        Args:
            text: Text to generate embedding for
            model: Model name (for reference)
            context: Optional execution context
        
        Returns:
            Dict with embedding and metadata:
            {
                "embedding": List[float],
                "model": str,
                "dimension": int
            }
        
        Raises:
            ValueError: If Public Works or HuggingFaceAdapter not available
            RuntimeError: If embedding generation fails
        """
        if not self.public_works:
            raise ValueError("Public Works not available - cannot access HuggingFaceAdapter")
        
        hf_adapter = self.public_works.get_huggingface_adapter()
        if not hf_adapter:
            raise ValueError("HuggingFaceAdapter not available - ensure HuggingFace adapter is configured")
        
        # Track usage (governance)
        tenant_id = context.tenant_id if context else None
        self.logger.info(
            f"🧬 Embedding generation via agent {self.agent_id}: "
            f"model={model}, text_length={len(text)}, tenant_id={tenant_id}"
        )
        
        try:
            # Call HuggingFaceAdapter (with governance tracking)
            result = await hf_adapter.generate_embedding(text, model)
            
            # Validate result
            if not result or "embedding" not in result:
                raise RuntimeError("HuggingFaceAdapter returned invalid result")
            
            embedding = result.get("embedding", [])
            dimension = result.get("dimension", len(embedding) if isinstance(embedding, list) else 0)
            
            # Log success (for audit)
            self.logger.info(
                f"✅ Embedding generated: dimension={dimension}, "
                f"model={model}, agent_id={self.agent_id}"
            )
            
            return {
                "embedding": embedding,
                "model": model,
                "dimension": dimension
            }
            
        except Exception as e:
            self.logger.error(f"❌ Embedding generation failed: {e}")
            raise RuntimeError(f"Embedding generation failed: {str(e)}")
