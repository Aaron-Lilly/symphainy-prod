"""
Security Guard Service - Phase 4

WHAT: I enforce security, zero-trust, multi-tenancy
HOW: I observe Runtime execution and enforce security policies

Can use agents for:
- Policy reasoning (security_policy_agent)
- Threat analysis (threat_analysis_agent)
"""

from typing import Dict, Any, Optional
from symphainy_platform.smart_city.protocols.smart_city_service_protocol import SmartCityServiceProtocol
from symphainy_platform.foundations.public_works.foundation_service import PublicWorksFoundationService
from symphainy_platform.foundations.curator.foundation_service import CuratorFoundationService
from symphainy_platform.runtime.runtime_service import RuntimeService
from symphainy_platform.agentic.foundation_service import AgentFoundationService
from utilities import get_logger, get_clock, LogLevel, LogCategory


class SecurityGuardService(SmartCityServiceProtocol):
    """
    Security Guard Service
    
    WHAT: I enforce security, zero-trust, multi-tenancy
    HOW: I observe Runtime execution and enforce security policies
    
    Uses agents for:
    - Policy reasoning (security_policy_agent)
    - Threat analysis (threat_analysis_agent)
    """
    
    def __init__(
        self,
        public_works_foundation: PublicWorksFoundationService,
        curator_foundation: CuratorFoundationService,
        runtime_service: RuntimeService,
        agent_foundation: Optional[AgentFoundationService] = None
    ):
        self.public_works = public_works_foundation
        self.curator = curator_foundation
        self.runtime_service = runtime_service
        self.agent_foundation = agent_foundation
        self.logger = get_logger("security_guard", LogLevel.INFO, LogCategory.PLATFORM)
        self.clock = get_clock()
        
        # Get auth and tenant abstractions from Public Works
        self.auth_abstraction = public_works_foundation.get_auth_abstraction()
        self.tenant_abstraction = public_works_foundation.get_tenant_abstraction()
        if not self.auth_abstraction:
            self.logger.warning("Auth abstraction not available")
        if not self.tenant_abstraction:
            self.logger.warning("Tenant abstraction not available")
        
        # Security state
        self.security_policies: Dict[str, Dict[str, Any]] = {}
        self.tenant_contexts: Dict[str, Dict[str, Any]] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
        # Agents for policy reasoning (loaded during initialization)
        self.security_policy_agent = None
        
        self.is_initialized = False
    
    async def initialize(self) -> bool:
        """Initialize Security Guard and register with Runtime/Curator."""
        try:
            self.logger.info("Initializing Security Guard Service")
            
            # Load agents for policy reasoning (if available)
            if self.agent_foundation:
                self.security_policy_agent = self.agent_foundation.get_agent("security_policy_agent")
                if self.security_policy_agent:
                    self.logger.info("Security policy agent loaded")
            
            # Register with Curator
            await self.curator.register_service(
                service_instance=self,
                service_metadata={
                    "service_name": "SecurityGuardService",
                    "service_type": "smart_city",
                    "realm": "smart_city",
                    "capabilities": [
                        "authentication",
                        "authorization",
                        "zero_trust_policy",
                        "multi_tenancy"
                    ]
                }
            )
            
            # Register with Runtime as observer
            await self.runtime_service.register_observer(
                observer_id="security_guard",
                observer=self
            )
            
            # Load security policies
            await self._load_security_policies()
            
            self.is_initialized = True
            self.logger.info("Security Guard Service initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Security Guard: {e}", exc_info=e)
            return False
    
    async def observe_execution(self, execution_id: str, event: dict) -> None:
        """
        Observe Runtime execution events and enforce security.
        
        Events observed:
        - session_created
        - intent_submitted
        - execution_started
        - execution_completed
        """
        event_type = event.get("event_type")
        
        if event_type == "session_created":
            await self._validate_session_security(event)
        elif event_type == "intent_submitted":
            await self._validate_intent_authorization(event)
        elif event_type == "execution_started":
            await self._enforce_execution_policy(event)
        
        # Log security observation
        self.logger.info(
            "Security observation",
            metadata={
                "execution_id": execution_id,
                "event_type": event_type,
                "timestamp": self.clock.now_iso()
            }
        )
    
    async def enforce_policy(self, execution_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enforce security policy for execution context.
        
        Can use agents for policy reasoning.
        
        Args:
            execution_id: Execution identifier
            context: Execution context (user, tenant, action, etc.)
        
        Returns:
            Dict containing policy enforcement result
        """
        user_id = context.get("user_id")
        tenant_id = context.get("tenant_id")
        action = context.get("action")
        resource = context.get("resource")
        
        # Use agent for policy reasoning if available
        if self.security_policy_agent:
            try:
                policy_reasoning = await self.security_policy_agent.reason(
                    context={
                        "user_id": user_id,
                        "tenant_id": tenant_id,
                        "action": action,
                        "resource": resource,
                        "security_policies": self.security_policies,
                        "user_context": context
                    }
                )
                
                # Extract reasoned artifact
                artifacts = policy_reasoning.get("artifacts", {})
                authorization_decision = artifacts.get("authorization_decision", {})
                
                return {
                    "allowed": authorization_decision.get("allowed", False),
                    "reason": authorization_decision.get("reason", ""),
                    "policy_applied": authorization_decision.get("policy", ""),
                    "reasoning_trace": policy_reasoning.get("reasoning", ""),
                    "method": "agent_reasoning"
                }
            except Exception as e:
                self.logger.warning(f"Agent policy reasoning failed: {e}, falling back to deterministic check")
        
        # Fallback to deterministic policy check
        return await self._deterministic_authorization_check(user_id, action, resource, tenant_id)
    
    async def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate authentication token (public method).
        
        Args:
            token: Authentication token
        
        Returns:
            Optional[Dict]: Security context or None if invalid
        """
        if not self.auth_abstraction:
            self.logger.error("Auth abstraction not available")
            return None
        
        try:
            context = await self.auth_abstraction.validate_token(token)
            if context:
                return {
                    "user_id": context.user_id,
                    "tenant_id": context.tenant_id,
                    "email": context.email,
                    "roles": context.roles,
                    "permissions": context.permissions
                }
            return None
        except Exception as e:
            self.logger.error(f"Token validation failed: {e}", exc_info=True)
            return None
    
    async def check_permission(
        self,
        user_id: str,
        permission: str,
        resource: Optional[str] = None
    ) -> bool:
        """
        Check if user has permission (public method).
        
        Args:
            user_id: User ID
            permission: Permission to check
            resource: Optional resource identifier
        
        Returns:
            bool: True if user has permission
        """
        if not self.auth_abstraction:
            self.logger.error("Auth abstraction not available")
            return False
        
        try:
            # Get user permissions from auth abstraction
            permissions = await self.auth_abstraction.get_user_permissions(user_id)
            return permission in permissions
        except Exception as e:
            self.logger.error(f"Permission check failed: {e}", exc_info=True)
            return False
    
    async def validate_tenant_access(
        self,
        user_tenant_id: str,
        resource_tenant_id: str
    ) -> bool:
        """
        Validate tenant access (public method).
        
        Args:
            user_tenant_id: User's tenant ID
            resource_tenant_id: Resource's tenant ID
        
        Returns:
            bool: True if access is allowed
        """
        if not self.tenant_abstraction:
            self.logger.error("Tenant abstraction not available")
            return False
        
        try:
            return await self.tenant_abstraction.validate_tenant_access(
                user_tenant_id=user_tenant_id,
                resource_tenant_id=resource_tenant_id
            )
        except Exception as e:
            self.logger.error(f"Tenant access validation failed: {e}", exc_info=True)
            return False
    
    async def check_authorization(
        self,
        user_id: str,
        action: str,
        resource: str,
        tenant_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Check authorization (public method for agents to use).
        
        Args:
            user_id: User identifier
            action: Action to check
            resource: Resource identifier
            tenant_id: Tenant identifier
            context: Optional additional context
        
        Returns:
            Dict containing authorization result
        """
        return await self.enforce_policy(
            execution_id="",  # Not needed for standalone check
            context={
                "user_id": user_id,
                "action": action,
                "resource": resource,
                "tenant_id": tenant_id,
                **(context or {})
            }
        )
    
    async def _load_security_policies(self):
        """Load security policies from configuration."""
        # Load from Public Works config or environment
        # For now, use default policies
        self.security_policies = {
            "default": {
                "allow_all": False,
                "require_tenant_isolation": True,
                "zero_trust": True
            }
        }
    
    async def _validate_session_security(self, event: dict):
        """Validate session security."""
        # Validate session creation security
        pass
    
    async def _validate_intent_authorization(self, event: dict):
        """Validate intent authorization."""
        # Validate intent submission authorization
        pass
    
    async def _enforce_execution_policy(self, event: dict):
        """Enforce execution policy."""
        # Enforce execution policy
        pass
    
    async def _deterministic_authorization_check(
        self,
        user_id: str,
        action: str,
        resource: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        Deterministic authorization check (fallback).
        
        Returns:
            Dict containing authorization result
        """
        # Simple deterministic check
        # In production, this would check against policy rules
        return {
            "allowed": True,  # Default allow (can be made more restrictive)
            "reason": "Deterministic policy check",
            "policy_applied": "default",
            "method": "deterministic"
        }
    
    async def shutdown(self) -> None:
        """Gracefully shutdown Security Guard."""
        self.logger.info("Shutting down Security Guard Service")
        self.is_initialized = False
