"""
Runtime Client - HTTP Client for Runtime Service

Experience service uses this to communicate with Runtime.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[6]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import httpx
from typing import Dict, Any, Optional, AsyncIterator
from utilities import get_logger

from symphainy_platform.runtime.intent_model import Intent, IntentFactory


class RuntimeClient:
    """
    HTTP client for Runtime service.
    
    Experience service uses this to:
    - Submit intents to Runtime
    - Create sessions via Runtime
    - Stream execution updates
    """
    
    def __init__(self, runtime_url: str = "http://runtime:8000"):
        """
        Initialize Runtime client.
        
        Args:
            runtime_url: Runtime service URL
        """
        self.runtime_url = runtime_url.rstrip("/")
        self.logger = get_logger(self.__class__.__name__)
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def create_session(
        self,
        session_intent: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create session via Runtime.
        
        Args:
            session_intent: Session intent prepared by Traffic Cop SDK
        
        Returns:
            Dict with session_id and metadata
        """
        try:
            response = await self.client.post(
                f"{self.runtime_url}/api/session/create",
                json=session_intent
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to create session: {e}", exc_info=True)
            raise
    
    async def submit_intent(
        self,
        intent: Intent
    ) -> Dict[str, Any]:
        """
        Submit intent to Runtime.
        
        Args:
            intent: Intent to submit
        
        Returns:
            Dict with execution_id and metadata
        """
        try:
            response = await self.client.post(
                f"{self.runtime_url}/api/intent/submit",
                json=intent.to_dict()
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to submit intent: {e}", exc_info=True)
            raise
    
    async def stream_execution(
        self,
        execution_id: str
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream execution updates from Runtime.
        
        Args:
            execution_id: Execution identifier
        
        Yields:
            Execution update events
        """
        try:
            async with self.client.stream(
                "GET",
                f"{self.runtime_url}/api/execution/{execution_id}/stream"
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        try:
                            import json
                            event = json.loads(line)
                            yield event
                        except json.JSONDecodeError:
                            self.logger.warning(f"Failed to parse event: {line}")
        except Exception as e:
            self.logger.error(f"Failed to stream execution: {e}", exc_info=True)
            raise
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
