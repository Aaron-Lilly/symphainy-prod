"""
LLM Protocol - Abstraction Contract (Layer 2)

Defines the interface for LLM completion and embedding operations.
Enables swappability between OpenAI, HuggingFace, and other providers.
Consumed by ReasoningService (ctx.reasoning.llm) — no adapter at boundary.

WHAT (Infrastructure Role): I define the contract for LLM operations
HOW (Infrastructure Implementation): I specify complete() and embed() only
"""

from typing import Protocol, Dict, Any, Optional


class LLMProtocol(Protocol):
    """
    Protocol for LLM completion and embedding.
    
    Implementations wrap OpenAIAdapter, HuggingFaceAdapter, etc. internally.
    ReasoningService receives this via get_llm_abstraction(); never raw adapters.
    """

    async def complete(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Complete a prompt using an LLM.

        Args:
            prompt: The prompt to complete
            model: Model to use (e.g. gpt-4, hf-...)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional model-specific parameters

        Returns:
            Dict with at least: content (str), model (str), usage (dict), finish_reason (str)
        """
        ...

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
            Dict with at least: embedding (list), model (str), dimensions (int)
        """
        ...
