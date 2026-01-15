"""
Policy Library - Policy Schema Definitions.

Phase 1: Scaffold structure, define schemas
Phase 2: Full validation/evaluation implementation
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class PolicyType(str, Enum):
    """Policy types."""
    AUTH = "auth"
    ISOLATION = "isolation"
    DATA_ACCESS = "data_access"
    EXECUTION = "execution"
    TENANT_OVERRIDE = "tenant_override"


class AuthPolicyRule(BaseModel):
    """
    Authentication policy rule schema.
    
    Phase 1: Basic structure
    Phase 2: Full validation
    """
    zero_trust_enabled: bool = Field(default=False, description="Enable zero-trust policy")
    require_mfa: bool = Field(default=False, description="Require multi-factor authentication")
    allowed_actions: List[str] = Field(default_factory=list, description="List of allowed actions")
    denied_actions: List[str] = Field(default_factory=list, description="List of denied actions")
    policy_source: str = Field(default="default", description="Source of policy (default, tenant, custom)")


class TenantIsolationRule(BaseModel):
    """
    Tenant isolation policy rule schema.
    
    Phase 1: Basic structure
    Phase 2: Full validation
    """
    isolation_level: str = Field(default="strict", description="Isolation level (strict, moderate, permissive)")
    allow_admin_override: bool = Field(default=False, description="Allow admin to override isolation")
    allowed_cross_tenant_actions: List[str] = Field(default_factory=list, description="Actions allowed across tenants")
    policy_source: str = Field(default="default", description="Source of policy")


class DataAccessPolicyRule(BaseModel):
    """
    Data access policy rule schema.
    
    Phase 1: Basic structure
    Phase 2: Full validation
    """
    allowed_resources: List[str] = Field(default_factory=list, description="List of allowed resources")
    denied_resources: List[str] = Field(default_factory=list, description="List of denied resources")
    require_encryption: bool = Field(default=False, description="Require encryption for data access")
    policy_source: str = Field(default="default", description="Source of policy")


class ExecutionPolicyRule(BaseModel):
    """
    Execution policy rule schema.
    
    Phase 1: Basic structure
    Phase 2: Full validation
    """
    allowed_execution_modes: List[str] = Field(default_factory=list, description="Allowed execution modes")
    max_execution_time: Optional[int] = Field(default=None, description="Maximum execution time in seconds")
    require_approval: bool = Field(default=False, description="Require approval before execution")
    policy_source: str = Field(default="default", description="Source of policy")


class PolicyRule(BaseModel):
    """
    Generic policy rule schema (flexible JSONB structure).
    
    Phase 1: Basic structure
    Phase 2: Full validation
    """
    policy_id: Optional[str] = Field(default=None, description="Policy ID")
    policy_type: PolicyType = Field(description="Type of policy")
    policy_data: Dict[str, Any] = Field(description="Policy data (flexible JSONB structure)")
    tenant_id: Optional[str] = Field(default=None, description="Tenant ID for tenant-specific policies")
    version: str = Field(default="1.0.0", description="Policy version")
    status: str = Field(default="active", description="Policy status (active, deprecated, maintenance)")
    created_at: Optional[str] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[str] = Field(default=None, description="Update timestamp")
