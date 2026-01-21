#!/usr/bin/env python3
"""
HuggingFace Adapter - Raw Technology Client

Raw HuggingFace Inference Endpoints client wrapper with no business logic.
This is Layer 0 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I provide raw HuggingFace model endpoint operations
HOW (Infrastructure Implementation): I use real HuggingFace Inference Endpoints API with no business logic
"""

import os
import httpx
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class HuggingFaceAdapter:
    """
    Raw HuggingFace Inference Endpoints client wrapper - no business logic.
    
    This adapter provides direct access to HuggingFace Inference Endpoints
    without any business logic or abstraction. It's the raw technology layer.
    """
    
    def __init__(self, endpoint_url: str = None, api_key: str = None, config_adapter = None):
        """
        Initialize HuggingFace adapter.
        
        Args:
            endpoint_url: HuggingFace Inference Endpoint URL (takes precedence)
            api_key: HuggingFace API key/token (takes precedence)
            config_adapter: ConfigAdapter for reading configuration (REQUIRED if parameters not provided)
        
        Raises:
            ValueError: If required configuration is missing
        """
        self.config_adapter = config_adapter
        
        # Get from parameters or ConfigAdapter (no fallback to os.getenv)
        if endpoint_url:
            self.endpoint_url = endpoint_url
        elif config_adapter:
            # Support both .get() method (dict-like) and attribute access
            if hasattr(config_adapter, 'get'):
                self.endpoint_url = config_adapter.get("HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL")
            elif hasattr(config_adapter, 'HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL'):
                self.endpoint_url = getattr(config_adapter, "HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL", None)
            else:
                self.endpoint_url = None
            
            if not self.endpoint_url:
                raise ValueError(
                    "HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL not found in configuration. "
                    "Either provide endpoint_url parameter or ensure config contains HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL."
                )
        else:
            raise ValueError(
                "ConfigAdapter is required. "
                "Pass config_adapter from Public Works Foundation. "
                "Example: HuggingFaceAdapter(config_adapter=config_adapter)"
            )
        
        if api_key:
            self.api_key = api_key
        elif config_adapter:
            # Support both .get() method (dict-like) and attribute access
            if hasattr(config_adapter, 'get'):
                self.api_key = config_adapter.get("HUGGINGFACE_EMBEDDINGS_API_KEY") or config_adapter.get("HUGGINGFACE_API_KEY")
            elif hasattr(config_adapter, 'HUGGINGFACE_EMBEDDINGS_API_KEY'):
                self.api_key = getattr(config_adapter, "HUGGINGFACE_EMBEDDINGS_API_KEY", None) or getattr(config_adapter, "HUGGINGFACE_API_KEY", None)
            else:
                self.api_key = None
            
            if not self.api_key:
                raise ValueError(
                    "HUGGINGFACE_EMBEDDINGS_API_KEY or HUGGINGFACE_API_KEY not found in configuration. "
                    "Either provide api_key parameter or ensure config contains HUGGINGFACE_EMBEDDINGS_API_KEY."
                )
        else:
            raise ValueError(
                "ConfigAdapter is required. "
                "Pass config_adapter from Public Works Foundation. "
                "Example: HuggingFaceAdapter(config_adapter=config_adapter)"
            )
        
        logger.info(f"✅ HuggingFace adapter initialized for endpoint: {self.endpoint_url[:50]}...")
    
    async def generate_embedding(
        self,
        text: str,
        model: str = "sentence-transformers/all-mpnet-base-v2"
    ) -> Dict[str, Any]:
        """
        Generate embedding using HuggingFace Inference Endpoint.
        
        Args:
            text: Text to generate embedding for
            model: Model name (for reference, endpoint is already configured)
        
        Returns:
            Dict with embedding and metadata
        """
        return await self.inference(
            inputs=text,
            model=model
        )
    
    async def inference(
        self,
        inputs: str,
        model: str = "sentence-transformers/all-mpnet-base-v2",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Call HuggingFace Inference Endpoint.
        
        Args:
            inputs: Input text/data
            model: Model name (for reference)
            **kwargs: Additional parameters
        
        Returns:
            Response from HuggingFace endpoint
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "X-Scale-Up-Timeout": "600"  # Wait for cold start if needed
        }
        
        payload = {
            "inputs": inputs,
            **kwargs
        }
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    self.endpoint_url,
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                result = response.json()
                
                # Handle different response formats
                if isinstance(result, list) and len(result) > 0:
                    embedding = result[0] if isinstance(result[0], list) else result
                elif isinstance(result, dict) and "embedding" in result:
                    embedding = result["embedding"]
                else:
                    embedding = result
                
                return {
                    "embedding": embedding if isinstance(embedding, list) else [embedding],
                    "model": model,
                    "dimension": len(embedding) if isinstance(embedding, list) else 1
                }
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 503:
                logger.warning("⚠️ 503 Service Unavailable - endpoint may be scaling up (cold start)")
                raise RuntimeError("HF endpoint is scaling up, please retry in 30-60 seconds")
            elif e.response.status_code == 401:
                logger.error("❌ 401 Unauthorized - check your HF API key")
                raise ValueError("Invalid HuggingFace API key")
            else:
                logger.error(f"❌ HTTP Error {e.response.status_code}: {e.response.text}")
                raise
        
        except httpx.TimeoutException:
            logger.error("❌ Timeout - endpoint may be taking too long to scale up")
            raise RuntimeError("HF endpoint timeout, please retry")
        
        except Exception as e:
            logger.error(f"❌ HF inference failed: {e}")
            raise
