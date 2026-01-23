"""
Traffic Cop SDK - Session Coordination and Execution Correlation

SDK for Traffic Cop coordination (used by Experience, Solution, Realms).

WHAT (Smart City Role): I coordinate sessions, execution IDs, and correlation
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

from typing import Dict, Any, Optional
from dataclasses import dataclass

from utilities import get_logger, get_clock, generate_event_id
from symphainy_platform.foundations.public_works.protocols.state_protocol import StateManagementProtocol


@dataclass
class SessionIntent:
    """Session creation intent with execution contract."""
    session_id: str
    tenant_id: Optional[str]  # Optional for anonymous sessions
    user_id: Optional[str]    # Optional for anonymous sessions
    execution_contract: Dict[str, Any]  # Prepared for Runtime validation


@dataclass
class SessionValidation:
    """Session validation result with execution contract."""
    session_id: str
    tenant_id: str
    user_id: Optional[str]
    is_valid: bool
    execution_contract: Dict[str, Any]  # Prepared for Runtime validation


class TrafficCopSDK:
    """
    Traffic Cop SDK - Coordination Logic
    
    Coordinates session management and execution correlation.
    Prepares execution contracts for Runtime validation.
    
    ⚠️ NO Runtime dependency - SDKs prepare, Runtime executes.
    """
    
    def __init__(
        self,
        state_abstraction: StateManagementProtocol,
        policy_resolver: Optional[Any] = None  # Policy library (optional for MVP)
    ):
        """
        Initialize Traffic Cop SDK.
        
        Args:
            state_abstraction: State management abstraction (from Public Works)
            policy_resolver: Optional policy resolver (for rate limiting preparation)
        """
        self.state_abstraction = state_abstraction
        self.policy_resolver = policy_resolver
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        
        self.logger.info("Traffic Cop SDK initialized (NO Runtime dependency)")
    
    async def create_session_intent(
        self,
        tenant_id: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SessionIntent:
        """
        Create session intent (SDK - prepares execution contract).
        
        This prepares the session creation intent for Runtime validation.
        Runtime will use Traffic Cop Primitives to validate and create the session.
        
        Args:
            tenant_id: Tenant identifier
            user_id: User identifier
            metadata: Optional session metadata
        
        Returns:
            SessionIntent with execution contract
        """
        # Generate session ID
        session_id = generate_event_id()
        
        # Resolve rate limiting policies (preparation, not validation)
        rate_limit_policies = []
        if self.policy_resolver:
            try:
                rate_limit_policies = await self.policy_resolver.get_rate_limit_policies(tenant_id)
            except Exception as e:
                self.logger.warning(f"Rate limit policy resolution failed (non-fatal): {e}")
        
        # Prepare execution contract (for Runtime validation)
        execution_contract = {
            "action": "create_session",
            "session_id": session_id,
            "tenant_id": tenant_id,
            "user_id": user_id,
            "metadata": metadata or {},
            "rate_limit_policies": rate_limit_policies,  # Prepared for Runtime validation
            "timestamp": self.clock.now_iso()
        }
        
        return SessionIntent(
            session_id=session_id,
            tenant_id=tenant_id,
            user_id=user_id,
            execution_contract=execution_contract
        )
    
    async def create_anonymous_session_intent(
        self,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SessionIntent:
        """
        Create anonymous session intent (SDK - prepares execution contract for anonymous sessions).
        
        This prepares an anonymous session creation intent (no tenant_id, user_id).
        Anonymous sessions are ephemeral and non-privileged, used for continuity before authentication.
        
        Args:
            metadata: Optional session metadata
        
        Returns:
            SessionIntent with execution contract (tenant_id=None, user_id=None)
        """
        # Generate session ID
        session_id = generate_event_id()
        
        # Prepare execution contract for anonymous session (no rate limit policies needed)
        execution_contract = {
            "action": "create_session",
            "session_type": "anonymous",
            "session_id": session_id,
            "tenant_id": None,  # Anonymous - no tenant
            "user_id": None,    # Anonymous - no user
            "metadata": metadata or {},
            "rate_limit_policies": [],  # Anonymous sessions have no rate limits (MVP)
            "timestamp": self.clock.now_iso()
        }
        
        return SessionIntent(
            session_id=session_id,
            tenant_id=None,  # Anonymous
            user_id=None,    # Anonymous
            execution_contract=execution_contract
        )
    
    async def get_session(
        self,
        session_id: str,
        tenant_id: str
    ) -> Optional[SessionValidation]:
        """
        Get session (SDK - prepares validation contract).
        
        This prepares the session retrieval for Runtime validation.
        Runtime will use Traffic Cop Primitives to validate session access.
        
        Args:
            session_id: Session identifier
            tenant_id: Tenant identifier
        
        Returns:
            SessionValidation with execution contract, or None if not found
        """
        try:
            # 1. Get session state (pure infrastructure)
            state_id = f"session:{tenant_id}:{session_id}"
            session_state = await self.state_abstraction.retrieve_state(state_id)
            
            if not session_state:
                return None
            
            # Extract session data
            user_id = session_state.get("user_id")
            is_valid = session_state.get("is_valid", True)
            
            # 2. Resolve access policies (preparation)
            access_policies = []
            if self.policy_resolver:
                try:
                    access_policies = await self.policy_resolver.get_session_access_policies(tenant_id)
                except Exception as e:
                    self.logger.warning(f"Session access policy resolution failed (non-fatal): {e}")
            
            # 3. Prepare execution contract (for Runtime validation)
            execution_contract = {
                "action": "get_session",
                "session_id": session_id,
                "tenant_id": tenant_id,
                "user_id": user_id,
                "access_policies": access_policies,  # Prepared for Runtime validation
                "timestamp": self.clock.now_iso()
            }
            
            return SessionValidation(
                session_id=session_id,
                tenant_id=tenant_id,
                user_id=user_id,
                is_valid=is_valid,
                execution_contract=execution_contract
            )
            
        except Exception as e:
            self.logger.error(f"Session retrieval coordination failed: {e}", exc_info=True)
            return None
    
    async def validate_session(
        self,
        session_id: str,
        tenant_id: str
    ) -> SessionValidation:
        """
        Validate session (SDK - prepares validation contract).
        
        This is a convenience method that calls get_session and ensures validation.
        
        Args:
            session_id: Session identifier
            tenant_id: Tenant identifier
        
        Returns:
            SessionValidation with execution contract
        """
        session = await self.get_session(session_id, tenant_id)
        
        if not session:
            # Return invalid session validation
            execution_contract = {
                "action": "validate_session",
                "session_id": session_id,
                "tenant_id": tenant_id,
                "timestamp": self.clock.now_iso()
            }
            return SessionValidation(
                session_id=session_id,
                tenant_id=tenant_id,
                user_id=None,
                is_valid=False,
                execution_contract=execution_contract
            )
        
        return session
    
    async def correlate_execution(
        self,
        session_id: str,
        execution_id: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        Correlate execution with session (SDK - prepares correlation contract).
        
        This prepares the execution correlation for Runtime validation.
        
        Args:
            session_id: Session identifier
            execution_id: Execution identifier
            tenant_id: Tenant identifier
        
        Returns:
            Dict with correlation preparation (not correlation result)
        """
        # Prepare execution contract (for Runtime validation)
        execution_contract = {
            "action": "correlate_execution",
            "session_id": session_id,
            "execution_id": execution_id,
            "tenant_id": tenant_id,
            "timestamp": self.clock.now_iso()
        }
        
        return {
            "prepared": True,
            "execution_contract": execution_contract
        }
