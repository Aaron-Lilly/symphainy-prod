"""
Runtime Client - HTTP Client for Runtime Service

Experience service uses this to communicate with Runtime.
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
    
    async def get_session(self, session_id: str, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get session details from Runtime (anonymous or authenticated).
        
        Args:
            session_id: Session identifier
            tenant_id: Tenant identifier (optional for anonymous sessions)
            
        Returns:
            Session data dictionary
        """
        params = {}
        if tenant_id:
            params["tenant_id"] = tenant_id
        
        response = await self.client.get(
            f"{self.runtime_url}/api/session/{session_id}",
            params=params if params else None
        )
        response.raise_for_status()
        return response.json()
    
    async def get_session_state(
        self,
        session_id: str,
        tenant_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get session state from Runtime (anonymous or authenticated).
        Uses GET /api/session/{session_id} — same payload as session details (no /state path).
        
        Args:
            session_id: Session identifier
            tenant_id: Tenant identifier (optional for anonymous sessions)
            
        Returns:
            Session state dictionary, or None if not found
        """
        try:
            params = {}
            if tenant_id:
                params["tenant_id"] = tenant_id
            
            response = await self.client.get(
                f"{self.runtime_url}/api/session/{session_id}",
                params=params if params else None
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise
        except Exception as e:
            self.logger.debug(f"Failed to get session state: {e}")
            return None
    
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
    
    async def upgrade_session(
        self,
        session_id: str,
        user_id: str,
        tenant_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Upgrade anonymous session with user_id and tenant_id.
        
        Args:
            session_id: Existing session identifier (anonymous)
            user_id: User identifier to attach
            tenant_id: Tenant identifier to attach
            metadata: Optional metadata to add
        
        Returns:
            Updated session state
        """
        try:
            response = await self.client.patch(
                f"{self.runtime_url}/api/session/{session_id}/upgrade",
                json={
                    "user_id": user_id,
                    "tenant_id": tenant_id,
                    "metadata": metadata or {}
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to upgrade session: {e}", exc_info=True)
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
    
    async def get_execution_status(
        self,
        execution_id: str,
        tenant_id: str,
        include_artifacts: bool = False,
        include_visuals: bool = False
    ) -> Dict[str, Any]:
        """
        Get execution status from Runtime (GET /api/execution/{id}/status).
        Used for polling when stream is not available.
        """
        try:
            response = await self.client.get(
                f"{self.runtime_url}/api/execution/{execution_id}/status",
                params={
                    "tenant_id": tenant_id,
                    "include_artifacts": include_artifacts,
                    "include_visuals": include_visuals,
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to get execution status: {e}", exc_info=True)
            raise

    async def stream_execution(
        self,
        execution_id: str,
        tenant_id: Optional[str] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream execution updates from Runtime.
        Tries GET /api/execution/{id}/stream first; if Runtime returns 404,
        falls back to polling GET /api/execution/{id}/status until terminal.
        See EXPERIENCE_SDK_CONTRACT: subscribe is polling until Runtime supports stream.
        
        Args:
            execution_id: Execution identifier
            tenant_id: Tenant identifier (required for polling fallback)
        
        Yields:
            Execution update events (stream events or status payloads when polling)
        """
        import asyncio
        # Try stream first (Runtime may not expose it yet)
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
                return
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                pass  # Fall through to polling
            else:
                raise
        except Exception as e:
            self.logger.debug(f"Stream not available, falling back to polling: {e}")
        # Polling fallback: poll status until terminal
        if not tenant_id:
            self.logger.warning("stream_execution: tenant_id required for polling fallback")
            return
        terminal_statuses = {"completed", "failed", "cancelled", "unknown"}
        while True:
            status = await self.get_execution_status(execution_id, tenant_id)
            yield status
            if status.get("status") in terminal_statuses:
                break
            await asyncio.sleep(1)

    async def get_realms(self) -> Dict[str, Any]:
        """
        Get list of registered realms from Runtime.
        Runtime may not expose GET /api/realms yet; on 404 returns empty structure
        so callers (e.g. control room) can fall back to local registry.
        """
        try:
            response = await self.client.get(f"{self.runtime_url}/api/realms")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"total": 0, "realm_names": [], "realms": []}
            raise
        except Exception as e:
            self.logger.debug(f"Failed to get realms (Runtime may not expose /api/realms): {e}")
            return {"total": 0, "realm_names": [], "realms": []}
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
