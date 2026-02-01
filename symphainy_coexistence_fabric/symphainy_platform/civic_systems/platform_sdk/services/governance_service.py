"""
Governance Service (ctx.governance) - Smart City SDKs

Wraps all 9 Smart City roles into a unified governance interface.

Roles:
    - data_steward  → Data boundaries, materialization, Records of Fact
    - auth          → Security Guard SDK (authentication, authorization)
    - registry      → Curator SDK (capability registries)
    - search        → Librarian SDK (knowledge search, schemas)
    - policy        → City Manager SDK (global policy, tenancy)
    - sessions      → Traffic Cop SDK (session management)
    - events        → Post Office SDK (event routing)
    - workflows     → Conductor SDK (workflow/saga primitives)
    - telemetry     → Nurse SDK (telemetry, retries, self-healing)

Usage:
    # Check data access
    access = await ctx.governance.data_steward.request_data_access(...)
    
    # Validate session
    session = await ctx.governance.sessions.validate_session(session_id)
    
    # Search knowledge
    results = await ctx.governance.search.search_knowledge(query)
"""

from dataclasses import dataclass
from typing import Any, Optional, Dict

from utilities import get_logger


@dataclass
class GovernanceService:
    """
    Unified governance interface wrapping all 9 Smart City SDKs.
    
    Available via ctx.governance in PlatformContext.
    """
    
    # Smart City SDKs
    _data_steward_sdk: Optional[Any] = None
    _security_guard_sdk: Optional[Any] = None
    _curator_sdk: Optional[Any] = None
    _librarian_sdk: Optional[Any] = None
    _city_manager_sdk: Optional[Any] = None
    _traffic_cop_sdk: Optional[Any] = None
    _post_office_sdk: Optional[Any] = None
    _conductor_sdk: Optional[Any] = None
    _nurse_sdk: Optional[Any] = None
    _materialization_policy_sdk: Optional[Any] = None
    
    def __init__(self, public_works: Optional[Any] = None):
        """
        Initialize GovernanceService from Public Works.
        
        Args:
            public_works: Public Works foundation service
        """
        self._logger = get_logger("GovernanceService")
        self._public_works = public_works
        
        if public_works:
            self._initialize_sdks(public_works)
    
    def _initialize_sdks(self, public_works: Any) -> None:
        """Initialize Smart City SDKs from Public Works abstractions."""
        try:
            # Data Steward SDK — boundary getter only; no adapter at boundary (CTA §1.3, §2.2)
            from symphainy_platform.civic_systems.smart_city.sdk.data_steward_sdk import DataStewardSDK

            data_steward_primitives = (
                public_works.get_data_governance_abstraction()
                if hasattr(public_works, "get_data_governance_abstraction")
                else None
            )
            materialization_policy = (
                public_works.get_materialization_policy()
                if hasattr(public_works, "get_materialization_policy")
                else None
            )

            self._data_steward_sdk = DataStewardSDK(
                data_governance_abstraction=data_steward_primitives,
                data_steward_primitives=data_steward_primitives,
                materialization_policy=materialization_policy,
            )
            self._logger.debug("✅ DataStewardSDK initialized (get_data_governance_abstraction only)")
        except Exception as e:
            self._logger.warning(f"Failed to initialize DataStewardSDK: {e}")
        
        try:
            # Security Guard SDK
            from symphainy_platform.civic_systems.smart_city.sdk.security_guard_sdk import SecurityGuardSDK
            self._security_guard_sdk = SecurityGuardSDK(
                auth_abstraction=public_works.get_auth_abstraction() if hasattr(public_works, "get_auth_abstraction") else None
            )
            self._logger.debug("✅ SecurityGuardSDK initialized")
        except Exception as e:
            self._logger.warning(f"Failed to initialize SecurityGuardSDK: {e}")
        
        try:
            # Curator SDK — required for platform; must be Supabase-backed (no in-memory-only as final answer)
            from symphainy_platform.civic_systems.smart_city.sdk.curator_sdk import CuratorSDK
            from symphainy_platform.foundations.curator.foundation_service import CuratorFoundationService
            registry = public_works.get_registry_abstraction() if hasattr(public_works, 'get_registry_abstraction') else None
            curator_foundation = CuratorFoundationService(public_works_foundation=public_works)
            curator_service = public_works.get_curator_service() if hasattr(public_works, 'get_curator_service') else None
            if not curator_service:
                raise RuntimeError(
                    "Curator is required for the platform to run and is only valid with Supabase. "
                    "Curator service is missing. Ensure Public Works has been initialized (await public_works.initialize()) with Supabase and artifact storage configured."
                )
            self._curator_sdk = CuratorSDK(
                registry_abstraction=registry,
                curator_foundation=curator_foundation,
                curator_service=curator_service,
            )
            self._logger.debug("✅ CuratorSDK initialized (required; Supabase-backed)")
        except RuntimeError:
            raise
        except Exception as e:
            self._logger.error(f"Failed to initialize CuratorSDK: {e}", exc_info=True)
            raise RuntimeError(
                "Curator is required for the platform to run. CuratorSDK initialization failed."
            ) from e
        
        try:
            # Librarian SDK — use boundary getter
            from symphainy_platform.civic_systems.smart_city.sdk.librarian_sdk import LibrarianSDK
            knowledge = public_works.get_knowledge_discovery_abstraction() if hasattr(public_works, 'get_knowledge_discovery_abstraction') else None
            self._librarian_sdk = LibrarianSDK(knowledge_discovery_abstraction=knowledge)
            self._logger.debug("✅ LibrarianSDK initialized")
        except Exception as e:
            self._logger.warning(f"Failed to initialize LibrarianSDK: {e}")
        
        try:
            # City Manager SDK — use boundary getter
            from symphainy_platform.civic_systems.smart_city.sdk.city_manager_sdk import CityManagerSDK
            tenant = public_works.get_tenant_abstraction() if hasattr(public_works, 'get_tenant_abstraction') else None
            self._city_manager_sdk = CityManagerSDK(tenant_abstraction=tenant)
            self._logger.debug("✅ CityManagerSDK initialized")
        except Exception as e:
            self._logger.warning(f"Failed to initialize CityManagerSDK: {e}")
        
        try:
            # Traffic Cop SDK — use boundary getter
            from symphainy_platform.civic_systems.smart_city.sdk.traffic_cop_sdk import TrafficCopSDK
            state = public_works.get_state_abstraction() if hasattr(public_works, 'get_state_abstraction') else None
            self._traffic_cop_sdk = TrafficCopSDK(state_abstraction=state)
            self._logger.debug("✅ TrafficCopSDK initialized")
        except Exception as e:
            self._logger.warning(f"Failed to initialize TrafficCopSDK: {e}")
        
        try:
            # Post Office SDK — use boundary getter
            from symphainy_platform.civic_systems.smart_city.sdk.post_office_sdk import PostOfficeSDK
            event_pub = public_works.get_event_publisher_abstraction() if hasattr(public_works, 'get_event_publisher_abstraction') else None
            self._post_office_sdk = PostOfficeSDK(event_publisher_abstraction=event_pub)
            self._logger.debug("✅ PostOfficeSDK initialized")
        except Exception as e:
            self._logger.warning(f"Failed to initialize PostOfficeSDK: {e}")
        
        try:
            # Conductor SDK
            from symphainy_platform.civic_systems.smart_city.sdk.conductor_sdk import ConductorSDK
            self._conductor_sdk = ConductorSDK()
            self._logger.debug("✅ ConductorSDK initialized")
        except Exception as e:
            self._logger.warning(f"Failed to initialize ConductorSDK: {e}")
        
        try:
            # Nurse SDK — use boundary getter
            from symphainy_platform.civic_systems.smart_city.sdk.nurse_sdk import NurseSDK
            telemetry = public_works.get_telemetry_abstraction() if hasattr(public_works, 'get_telemetry_abstraction') else None
            self._nurse_sdk = NurseSDK(telemetry_abstraction=telemetry)
            self._logger.debug("✅ NurseSDK initialized")
        except Exception as e:
            self._logger.warning(f"Failed to initialize NurseSDK: {e}")
        
        try:
            # Materialization Policy SDK
            from symphainy_platform.civic_systems.smart_city.sdk.materialization_policy_sdk import MaterializationPolicySDK
            self._materialization_policy_sdk = MaterializationPolicySDK()
            self._logger.debug("✅ MaterializationPolicySDK initialized")
        except Exception as e:
            self._logger.warning(f"Failed to initialize MaterializationPolicySDK: {e}")
    
    # ========================================================================
    # Property accessors for each Smart City role
    # ========================================================================
    
    @property
    def data_steward(self) -> Any:
        """
        Data Steward SDK - Data boundaries, materialization, Records of Fact.
        
        Operations:
            - request_data_access(intent, context, source_type, source_id, metadata)
            - authorize_materialization(contract_id, tenant_id, requested_type)
            - promote_to_record_of_fact(source_file_id, contract_id, tenant_id, record_type, content)
            - record_provenance(data_id, tenant_id, provenance_data)
        """
        if not self._data_steward_sdk:
            raise RuntimeError("DataStewardSDK not available. Check GovernanceService initialization.")
        return self._data_steward_sdk
    
    @property
    def auth(self) -> Any:
        """
        Security Guard SDK - Authentication and authorization.
        
        Operations:
            - authenticate(credentials)
            - validate_token(token)
            - check_authorization(user_id, resource, action)
        """
        if not self._security_guard_sdk:
            raise RuntimeError("SecurityGuardSDK not available. Check GovernanceService initialization.")
        return self._security_guard_sdk
    
    @property
    def registry(self) -> Any:
        """
        Curator SDK - Capability registries.
        
        Operations:
            - register_capability(capability_def)
            - get_capability(capability_id)
            - list_capabilities(filters)
            - promote_outcome(outcome_id, target_registry)
        """
        if not self._curator_sdk:
            raise RuntimeError("CuratorSDK not available. Check GovernanceService initialization.")
        return self._curator_sdk
    
    @property
    def search(self) -> Any:
        """
        Librarian SDK - Knowledge search and schemas.
        
        Operations:
            - search_knowledge(query, tenant_id, filters)
            - get_schema(schema_id, tenant_id)
            - discover_relationships(entity_id, tenant_id)
        """
        if not self._librarian_sdk:
            raise RuntimeError("LibrarianSDK not available. Check GovernanceService initialization.")
        return self._librarian_sdk
    
    @property
    def policy(self) -> Any:
        """
        City Manager SDK - Global policy and tenancy.
        
        Operations:
            - get_tenant_policy(tenant_id)
            - check_policy(policy_id, context)
            - escalate(issue, context)
        """
        if not self._city_manager_sdk:
            raise RuntimeError("CityManagerSDK not available. Check GovernanceService initialization.")
        return self._city_manager_sdk
    
    @property
    def sessions(self) -> Any:
        """
        Traffic Cop SDK - Session management.
        
        Operations:
            - validate_session(session_id, tenant_id)
            - create_session(tenant_id, user_id, metadata)
            - correlate_execution(session_id, execution_id)
        """
        if not self._traffic_cop_sdk:
            raise RuntimeError("TrafficCopSDK not available. Check GovernanceService initialization.")
        return self._traffic_cop_sdk
    
    @property
    def events(self) -> Any:
        """
        Post Office SDK - Event routing and ordering.
        
        Operations:
            - publish_event(topic, event_type, event_data)
            - subscribe(topic, handler)
            - route_event(event, routing_rules)
        """
        if not self._post_office_sdk:
            raise RuntimeError("PostOfficeSDK not available. Check GovernanceService initialization.")
        return self._post_office_sdk
    
    @property
    def workflows(self) -> Any:
        """
        Conductor SDK - Workflow and saga primitives.
        
        Operations:
            - create_saga(saga_def)
            - execute_step(saga_id, step_id, context)
            - compensate(saga_id, from_step)
        """
        if not self._conductor_sdk:
            raise RuntimeError("ConductorSDK not available. Check GovernanceService initialization.")
        return self._conductor_sdk
    
    @property
    def telemetry(self) -> Any:
        """
        Nurse SDK - Telemetry, retries, and self-healing.
        
        Operations:
            - record_telemetry(telemetry_data, tenant_id)
            - schedule_retry(operation_id, retry_config)
            - report_health(component_id, health_status)
        """
        if not self._nurse_sdk:
            raise RuntimeError("NurseSDK not available. Check GovernanceService initialization.")
        return self._nurse_sdk
    
    @property
    def materialization_policy(self) -> Any:
        """
        Materialization Policy SDK - Materialization policy management.
        
        Operations:
            - get_policy(tenant_id, policy_id)
            - evaluate_policy(context, request)
        """
        if not self._materialization_policy_sdk:
            raise RuntimeError("MaterializationPolicySDK not available. Check GovernanceService initialization.")
        return self._materialization_policy_sdk
    
    def get_available_roles(self) -> Dict[str, bool]:
        """
        Get availability status of all Smart City roles.
        
        Returns:
            Dict mapping role name to availability boolean
        """
        return {
            "data_steward": self._data_steward_sdk is not None,
            "auth": self._security_guard_sdk is not None,
            "registry": self._curator_sdk is not None,
            "search": self._librarian_sdk is not None,
            "policy": self._city_manager_sdk is not None,
            "sessions": self._traffic_cop_sdk is not None,
            "events": self._post_office_sdk is not None,
            "workflows": self._conductor_sdk is not None,
            "telemetry": self._nurse_sdk is not None,
            "materialization_policy": self._materialization_policy_sdk is not None,
        }
