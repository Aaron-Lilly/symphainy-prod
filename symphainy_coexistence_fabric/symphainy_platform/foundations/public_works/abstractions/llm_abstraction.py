"""
LLM Abstraction - Protocol implementation wrapping OpenAI and HuggingFace adapters

Implements LLMProtocol. Used by ReasoningService via get_llm_abstraction() only.
Adapters stay inside Public Works; no adapter at boundary.
"""

from typing import Any, Dict, List, Optional

from utilities import get_logger


class LLMAbstraction:
    """
    Implements LLMProtocol by delegating to OpenAI and HuggingFace adapters.
    
    Complete: routes to OpenAI (generate_completion) or HuggingFace (if text-gen endpoint added later).
    Embed: routes to OpenAI (generate_embeddings) or HuggingFace (generate_embedding).
    """

    def __init__(
        self,
        openai_adapter: Optional[Any] = None,
        huggingface_adapter: Optional[Any] = None,
        default_model: str = "gpt-4",
        default_embed_model: str = "text-embedding-ada-002",
    ):
        self._openai = openai_adapter
        self._huggingface = huggingface_adapter
        self._default_model = default_model
        self._default_embed_model = default_embed_model
        self._logger = get_logger("LLMAbstraction")

    async def complete(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Complete a prompt. Routes to OpenAI or HuggingFace based on model."""
        model = model or self._default_model

        if model.startswith("gpt") or model.startswith("o1") or not model.startswith("hf-"):
            return await self._complete_openai(prompt, model, temperature, max_tokens, **kwargs)
        if model.startswith("hf-") or "huggingface" in model.lower():
            return await self._complete_huggingface(prompt, model, temperature, max_tokens, **kwargs)
        return await self._complete_openai(prompt, model, temperature, max_tokens, **kwargs)

    async def _complete_openai(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        **kwargs: Any
    ) -> Dict[str, Any]:
        if not self._openai:
            raise RuntimeError("OpenAI adapter not available. Check Public Works LLM configuration.")
        messages = []
        if kwargs.get("system_message"):
            messages.append({"role": "system", "content": kwargs["system_message"]})
        messages.append({"role": "user", "content": prompt})
        request = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **{k: v for k, v in kwargs.items() if k in ("top_p", "frequency_penalty", "presence_penalty", "stop")},
        }
        response = await self._openai.generate_completion(request)
        if response.get("error"):
            raise RuntimeError(f"OpenAI completion failed: {response['error']}")
        choices = response.get("choices", [])
        content = choices[0].get("message", {}).get("content", "") if choices else ""
        return {
            "content": content,
            "model": response.get("model", model),
            "usage": response.get("usage", {}),
            "finish_reason": choices[0].get("finish_reason", "stop") if choices else "stop",
        }

    async def _complete_huggingface(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        **kwargs: Any
    ) -> Dict[str, Any]:
        if not self._huggingface:
            raise RuntimeError("HuggingFace adapter not available for text generation.")
        if not hasattr(self._huggingface, "generate") and not hasattr(self._huggingface, "inference"):
            raise RuntimeError("HuggingFace adapter does not support text generation (generate/inference).")
        try:
            if hasattr(self._huggingface, "generate"):
                response = await self._huggingface.generate(
                    prompt=prompt,
                    model=model.replace("hf-", ""),
                    temperature=temperature,
                    max_new_tokens=max_tokens,
                    **kwargs,
                )
            else:
                response = await self._huggingface.inference(
                    inputs=prompt,
                    model=model.replace("hf-", ""),
                    **kwargs,
                )
            return {
                "content": response.get("generated_text", response.get("content", str(response))),
                "model": model,
                "usage": response.get("usage", {}),
                "finish_reason": "stop",
            }
        except Exception as e:
            self._logger.error(f"HuggingFace completion failed: {e}")
            raise

    async def embed(
        self,
        content: str,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate embeddings. Routes by model/config (OpenAI or HuggingFace). No silent fallback on API failure; raises if unavailable."""
        model = model or self._default_embed_model

        if self._openai and (model.startswith("text-embedding") or "openai" in model.lower() or not model.startswith("hf-")):
            emb = await self._openai.generate_embeddings(content, model)
            return {
                "embedding": emb if isinstance(emb, list) else list(emb),
                "model": model,
                "dimensions": len(emb) if isinstance(emb, (list, tuple)) else 0,
            }
        if self._huggingface:
            response = await self._huggingface.generate_embedding(
                text=content,
                model=model.replace("hf-", "") if model else "sentence-transformers/all-mpnet-base-v2",
            )
            emb = response.get("embedding", [])
            return {
                "embedding": emb if isinstance(emb, list) else [emb],
                "model": response.get("model", model),
                "dimensions": len(emb) if isinstance(emb, (list, tuple)) else response.get("dimension", 0),
            }
        raise RuntimeError("No LLM adapter available for embeddings. Check Public Works LLM configuration.")
