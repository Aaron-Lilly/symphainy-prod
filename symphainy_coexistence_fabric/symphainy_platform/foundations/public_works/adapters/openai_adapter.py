#!/usr/bin/env python3
"""
OpenAI Infrastructure Adapter

Raw OpenAI client wrapper for LLM operations.
Thin wrapper around OpenAI SDK with no business logic.

WHAT (Infrastructure Role): I provide raw OpenAI API operations
HOW (Infrastructure Implementation): I use OpenAI SDK with no business logic
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import os
import json
import logging

try:
    from openai import AsyncOpenAI
    try:
        from openai.types.chat import ChatCompletion
    except ImportError:
        ChatCompletion = None
    try:
        from openai.types.embeddings import Embedding
    except ImportError:
        Embedding = None
except ImportError:
    AsyncOpenAI = None
    ChatCompletion = None
    Embedding = None

logger = logging.getLogger(__name__)


class OpenAIAdapter:
    """Raw OpenAI adapter for LLM operations."""
    
    def __init__(self, api_key: str = None, base_url: str = None, config_adapter = None, **kwargs):
        """
        Initialize OpenAI adapter.
        
        Args:
            api_key: OpenAI API key (takes precedence)
            base_url: OpenAI base URL (for custom endpoints)
            config_adapter: ConfigAdapter for reading configuration (REQUIRED if api_key not provided)
        
        Raises:
            ValueError: If neither api_key nor config_adapter is provided
        """
        self.config_adapter = config_adapter
        self.logger = logger
        
        # Support both LLM_OPENAI_API_KEY and OPENAI_API_KEY for compatibility
        # Priority: parameter > ConfigAdapter (no fallback to os.getenv)
        if api_key:
            self.api_key = api_key
        elif config_adapter:
            # Support both .get() method (dict-like) and attribute access
            if hasattr(config_adapter, 'get'):
                self.api_key = config_adapter.get("LLM_OPENAI_API_KEY") or config_adapter.get("OPENAI_API_KEY")
            elif hasattr(config_adapter, 'LLM_OPENAI_API_KEY'):
                self.api_key = getattr(config_adapter, "LLM_OPENAI_API_KEY", None) or getattr(config_adapter, "OPENAI_API_KEY", None)
            else:
                self.api_key = None
            
            if not self.api_key:
                raise ValueError(
                    "LLM_OPENAI_API_KEY or OPENAI_API_KEY not found in configuration. "
                    "Either provide api_key parameter or ensure config contains LLM_OPENAI_API_KEY."
                )
        else:
            raise ValueError(
                "ConfigAdapter is required. "
                "Pass config_adapter from Public Works Foundation. "
                "Example: OpenAIAdapter(config_adapter=config_adapter)"
            )
        
        self.base_url = base_url
        if not hasattr(self, 'logger'):
            self.logger = logger
        
        # OpenAI client (private - use wrapper methods instead)
        self._client = None
        
        # Initialize OpenAI client
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client. Fails fast: raises if SDK missing or client cannot be created."""
        if AsyncOpenAI is None:
            raise RuntimeError(
                "OpenAI SDK not installed. Install with: pip install openai"
            )
        try:
            self._client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            self.client = self._client
            self.logger.info("✅ OpenAI adapter initialized")
        except Exception as e:
            self._client = None
            self.client = None
            raise RuntimeError(
                f"OpenAI client initialization failed: {e}. Check API key and network."
            ) from e
    
    async def generate_completion(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate completion using OpenAI.
        Fails fast: raises if client is not initialized or API call fails.
        """
        if not self._client:
            raise RuntimeError(
                "OpenAI client not initialized. Check LLM configuration (e.g. openai_api_key) and that the OpenAI SDK is installed."
            )
        try:
            response = await self._client.chat.completions.create(**request)
            return {
                "id": response.id,
                "choices": [
                    {
                        "message": {
                            "role": choice.message.role,
                            "content": choice.message.content
                        },
                        "finish_reason": choice.finish_reason
                    }
                    for choice in response.choices
                ],
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "model": response.model,
                "created": response.created
            }
        except Exception as e:
            self.logger.error(f"OpenAI completion failed: {e}")
            raise RuntimeError(
                f"OpenAI API request failed: {e}. Check API key, network, and model availability."
            ) from e
    
    async def generate_embeddings(self, text: str, model: str = "text-embedding-ada-002") -> List[float]:
        """
        Generate embeddings using OpenAI.
        Fails fast: raises if client is not initialized or API call fails.
        """
        if not self._client:
            raise RuntimeError(
                "OpenAI client not initialized. Check LLM configuration (e.g. openai_api_key) and that the OpenAI SDK is installed."
            )
        try:
            response = await self._client.embeddings.create(
                input=text,
                model=model
            )
            if not response.data:
                raise RuntimeError("OpenAI returned no embedding data; check API response.")
            embeddings = response.data[0].embedding
            self.logger.info(f"✅ Embeddings generated for text (length: {len(text)})")
            return embeddings
        except Exception as e:
            self.logger.error(f"Failed to generate embeddings: {e}")
            raise RuntimeError(
                f"OpenAI embeddings API failed: {e}. Check API key, network, and model availability."
            ) from e
    
    async def get_models(self) -> List[Dict[str, Any]]:
        """
        Get available models from OpenAI.
        
        Returns:
            List[Dict]: Available models
        """
        if not self._client:
            return []
            
        try:
            # Get models
            response = await self._client.models.list()
            
            # Convert to list of dicts
            models = [
                {
                    "id": model.id,
                    "object": model.object,
                    "created": model.created,
                    "owned_by": model.owned_by
                }
                for model in response.data
            ]
            
            self.logger.info(f"✅ Retrieved {len(models)} models")
            return models
            
        except Exception as e:
            self.logger.error(f"Failed to get models: {e}")
            return []
    
    async def is_model_available(self, model: str) -> bool:
        """
        Check if model is available.
        
        Args:
            model: Model name
            
        Returns:
            bool: Model availability
        """
        if not self._client:
            return False
            
        try:
            # Get models and check availability
            models = await self.get_models()
            model_ids = [m["id"] for m in models]
            
            available = model in model_ids
            self.logger.info(f"✅ Model {model} availability: {available}")
            return available
            
        except Exception as e:
            self.logger.error(f"Failed to check model availability {model}: {e}")
            return False
    
    async def get_model_info(self, model: str) -> Dict[str, Any]:
        """
        Get model information.
        
        Args:
            model: Model name
            
        Returns:
            Dict: Model information
        """
        if not self._client:
            return {}
            
        try:
            # Get model info
            response = await self._client.models.retrieve(model)
            
            # Convert to dict
            model_info = {
                "id": response.id,
                "object": response.object,
                "created": response.created,
                "owned_by": response.owned_by
            }
            
            self.logger.info(f"✅ Retrieved model info for {model}")
            return model_info
            
        except Exception as e:
            self.logger.error(f"Failed to get model info for {model}: {e}")
            return {}
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check.
        
        Returns:
            Dict: Health check result
        """
        try:
            if not self._client:
                return {
                    "healthy": False,
                    "error": "OpenAI client not initialized"
                }
            
            # Test with a simple request
            test_response = await self.generate_completion({
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 5
            })
            
            if "error" in test_response:
                return {
                    "healthy": False,
                    "error": test_response["error"]
                }
            
            return {
                "healthy": True,
                "model": test_response.get("model"),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e)
            }
