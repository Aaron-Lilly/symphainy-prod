"""
Post Office SDK - Event Routing and WebSocket Coordination

SDK for Post Office coordination (used by Experience, Solution, Realms).

WHAT (Smart City Role): I coordinate event routing, ordering, and WebSocket streaming
HOW (SDK Implementation): I use Public Works abstractions to prepare execution contracts

⚠️ CRITICAL: NO Runtime dependency.
SDKs prepare execution contracts. Runtime validates and executes them.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List, AsyncIterator, TYPE_CHECKING
from dataclasses import dataclass

from utilities import get_logger, get_clock

if TYPE_CHECKING:
    from symphainy_platform.foundations.public_works.protocols.event_log_protocol import EventLogProtocol


@dataclass
class EventRoutingIntent:
    """Event routing intent with execution contract."""
    event_type: str
    tenant_id: str
    payload: Dict[str, Any]
    execution_contract: Dict[str, Any]  # Prepared for Runtime validation


@dataclass
class StreamSubscription:
    """WebSocket stream subscription."""
    stream_name: str
    tenant_id: str
    filters: Optional[Dict[str, Any]] = None


class PostOfficeSDK:
    """
    Post Office SDK - Coordination Logic
    
    Coordinates event routing, ordering, and WebSocket streaming.
    Prepares execution contracts for Runtime validation.
    
    ⚠️ NO Runtime dependency - SDKs prepare, Runtime executes.
    """
    
    def __init__(
        self,
        event_log: Optional["EventLogProtocol"] = None,
        policy_resolver: Optional[Any] = None  # Policy library (optional for MVP)
    ):
        """
        Initialize Post Office SDK.

        Uses EventLogProtocol (e.g. from public_works.get_wal_backend()); adapters must not escape Public Works.

        Args:
            event_log: Event log backend (from Public Works get_wal_backend()) for stream read
            policy_resolver: Optional policy resolver (for routing policies)
        """
        self.event_log = event_log
        self.policy_resolver = policy_resolver
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        
        self.logger.info("Post Office SDK initialized (NO Runtime dependency)")
    
    async def route_event(
        self,
        event_type: str,
        tenant_id: str,
        payload: Dict[str, Any],
        target_stream: Optional[str] = None
    ) -> EventRoutingIntent:
        """
        Route event (SDK - prepares execution contract).
        
        This prepares the event routing intent for Runtime validation.
        Runtime will use Post Office Primitives to validate and route the event.
        
        Args:
            event_type: Event type identifier
            tenant_id: Tenant identifier
            payload: Event payload
            target_stream: Optional target stream name
        
        Returns:
            EventRoutingIntent with execution contract
        """
        # Resolve routing policies (preparation, not validation)
        routing_policies = []
        if self.policy_resolver:
            try:
                routing_policies = await self.policy_resolver.get_routing_policies(tenant_id, event_type)
            except Exception as e:
                self.logger.warning(f"Routing policy resolution failed (non-fatal): {e}")
        
        # Determine target stream (if not provided)
        if not target_stream:
            target_stream = f"events:{tenant_id}:{event_type}"
        
        # Prepare execution contract (for Runtime validation)
        execution_contract = {
            "action": "route_event",
            "event_type": event_type,
            "tenant_id": tenant_id,
            "target_stream": target_stream,
            "routing_policies": routing_policies,  # Prepared for Runtime validation
            "timestamp": self.clock.now_iso()
        }
        
        return EventRoutingIntent(
            event_type=event_type,
            tenant_id=tenant_id,
            payload=payload,
            execution_contract=execution_contract
        )
    
    async def publish_event(
        self,
        event_type: str,
        tenant_id: str,
        payload: Dict[str, Any],
        target_stream: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Publish event (SDK - prepares execution contract).
        
        This is a convenience method that prepares the event for routing.
        In MVP, this can directly publish to Redis Streams.
        In full, this prepares the contract for Runtime validation.
        
        Args:
            event_type: Event type identifier
            tenant_id: Tenant identifier
            payload: Event payload
            target_stream: Optional target stream name
        
        Returns:
            Dict with publication preparation
        """
        # Prepare routing intent
        routing_intent = await self.route_event(event_type, tenant_id, payload, target_stream)
        
        return {
            "prepared": True,
            "execution_contract": routing_intent.execution_contract,
            "event_type": event_type,
            "tenant_id": tenant_id
        }
    
    async def subscribe_to_stream(
        self,
        stream_name: str,
        tenant_id: str,
        filters: Optional[Dict[str, Any]] = None,
        consumer_group: Optional[str] = None,
        consumer_name: Optional[str] = None
    ) -> StreamSubscription:
        """
        Subscribe to stream (SDK - prepares subscription contract).
        
        This prepares the stream subscription for Runtime validation.
        Runtime will use Post Office Primitives to validate and create the subscription.
        
        Args:
            stream_name: Stream name
            tenant_id: Tenant identifier
            filters: Optional event filters
            consumer_group: Optional consumer group name
            consumer_name: Optional consumer name
        
        Returns:
            StreamSubscription with execution contract
        """
        # Resolve subscription policies (preparation)
        subscription_policies = []
        if self.policy_resolver:
            try:
                subscription_policies = await self.policy_resolver.get_subscription_policies(tenant_id, stream_name)
            except Exception as e:
                self.logger.warning(f"Subscription policy resolution failed (non-fatal): {e}")
        
        # Prepare execution contract (for Runtime validation)
        execution_contract = {
            "action": "subscribe_to_stream",
            "stream_name": stream_name,
            "tenant_id": tenant_id,
            "filters": filters or {},
            "consumer_group": consumer_group,
            "consumer_name": consumer_name,
            "subscription_policies": subscription_policies,  # Prepared for Runtime validation
            "timestamp": self.clock.now_iso()
        }
        
        return StreamSubscription(
            stream_name=stream_name,
            tenant_id=tenant_id,
            filters=filters
        )
    
    async def get_stream_events(
        self,
        stream_name: str,
        tenant_id: str,
        limit: int = 100,
        start_id: str = "-",
        end_id: str = "+"
    ) -> List[Dict[str, Any]]:
        """
        Get stream events (SDK - coordination only, no validation needed).
        
        This is a read operation, so it doesn't need Runtime validation.
        It directly uses Redis adapter to read events.
        
        Args:
            stream_name: Stream name
            tenant_id: Tenant identifier
            limit: Maximum number of events
            start_id: Start message ID
            end_id: End message ID
        
        Returns:
            List of event dictionaries
        """
        if not self.event_log:
            raise RuntimeError(
                "Event log not wired; cannot get stream events. Platform contract §8A."
            )
        
        try:
            entries = await self.event_log.xrange(
                stream_name=stream_name,
                start=start_id,
                end=end_id,
                count=limit
            )
            
            # Convert to event format
            events = []
            for msg_id, fields in entries:
                events.append({
                    "message_id": msg_id,
                    "event_type": fields.get("event_type"),
                    "tenant_id": fields.get("tenant_id"),
                    "payload": fields.get("payload", {}),
                    "timestamp": fields.get("timestamp")
                })
            
            return events
            
        except Exception as e:
            self.logger.error(f"Failed to get stream events: {e}", exc_info=True)
            return []
