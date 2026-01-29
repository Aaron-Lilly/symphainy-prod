"""
Experience SDK - Contract (Protocol) and Implementation for Experience Surfaces

Experience surfaces use this contract to query state, invoke intents,
trigger journeys, and subscribe to execution updates.

See: docs/architecture/EXPERIENCE_SDK_CONTRACT.md
"""

from typing import Any, AsyncIterator, Dict, Optional, Protocol

from symphainy_platform.runtime.intent_model import IntentFactory


class ExperienceSDKProtocol(Protocol):
    """
    Protocol for the Experience SDK. All experience API routes and
    in-process callers should depend on this interface.
    """

    async def query_state(
        self,
        session_id: str,
        tenant_id: Optional[str] = None,
        execution_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Return session state and optionally execution status/artifacts.
        """
        ...

    async def invoke_intent(
        self,
        intent_type: str,
        parameters: Dict[str, Any],
        tenant_id: str,
        session_id: str,
        solution_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Submit an intent. Returns execution_id, status, created_at.
        """
        ...

    async def trigger_journey(
        self,
        journey_id: str,
        parameters: Dict[str, Any],
        tenant_id: str,
        session_id: str,
        solution_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Start a journey (alias for invoke_intent with compose_journey).
        Returns execution_id, status, created_at.
        """
        ...

    async def subscribe(
        self,
        execution_id: str,
        tenant_id: str,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Yield execution updates until terminal state.
        Current: polling status; target: stream when Runtime supports it.
        """
        ...


class ExperienceSDK:
    """
    Experience SDK implementation. Delegates to RuntimeClient (HTTP to Runtime).
    All Experience API routes should use this facade instead of RuntimeClient directly.
    """

    def __init__(self, runtime_client: Any):
        """
        Args:
            runtime_client: RuntimeClient instance (from ..sdk.runtime_client).
        """
        self._client = runtime_client

    async def query_state(
        self,
        session_id: str,
        tenant_id: Optional[str] = None,
        execution_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Return session state and optionally execution status."""
        state: Dict[str, Any] = {}
        session_state = await self._client.get_session_state(session_id, tenant_id)
        if session_state:
            state["session"] = session_state
        if execution_id and tenant_id:
            try:
                status = await self._client.get_execution_status(
                    execution_id, tenant_id, include_artifacts=True
                )
                state["execution"] = status
            except Exception:
                state["execution"] = None
        return state

    async def invoke_intent(
        self,
        intent_type: str,
        parameters: Dict[str, Any],
        tenant_id: str,
        session_id: str,
        solution_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Submit an intent. Returns execution_id, status, created_at."""
        intent = IntentFactory.create_intent(
            intent_type=intent_type,
            tenant_id=tenant_id,
            session_id=session_id,
            solution_id=solution_id or "default",
            parameters=parameters,
            metadata=metadata or {},
        )
        return await self._client.submit_intent(intent)

    async def trigger_journey(
        self,
        journey_id: str,
        parameters: Dict[str, Any],
        tenant_id: str,
        session_id: str,
        solution_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Start a journey (invoke_intent with compose_journey)."""
        params = {"journey_id": journey_id, **(parameters or {})}
        return await self.invoke_intent(
            intent_type="compose_journey",
            parameters=params,
            tenant_id=tenant_id,
            session_id=session_id,
            solution_id=solution_id,
            metadata=metadata,
        )

    async def subscribe(
        self,
        execution_id: str,
        tenant_id: str,
    ) -> AsyncIterator[Dict[str, Any]]:
        """Yield execution updates until terminal (polling or stream)."""
        async for event in self._client.stream_execution(execution_id, tenant_id):
            yield event
