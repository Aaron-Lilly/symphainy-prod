"""
Security Realm - Authentication, Authorization, and Session Management

The Security Realm provides foundational security services for the platform.
All other solutions depend on Security Realm for authentication and authorization.

WHAT (Realm Role): I provide security services (auth, sessions, permissions)
HOW (Realm Implementation): I provide intent services that wrap Security Guard SDK

Key Principles:
- Intent services are pure services (wrap Security Guard SDK)
- All services use Public Works abstractions (auth_abstraction, tenancy_abstraction)
- Artifacts stored in Artifact Plane (session records, audit logs)
- Services exposed as SOA APIs by SecuritySolution

Architecture:
- Security Realm wraps existing Security Guard SDK infrastructure
- Intent services provide consistent interface for solution pattern
- SecuritySolution composes Authentication and Registration journeys
- MCP tools enable agent-based security operations

Naming Convention:
- Realm: Security Realm (foundational)
- Solution: SecuritySolution (platform construct)
- Artifacts: security_* (e.g., security_session, security_audit_log)
"""

from .intent_services import (
    AuthenticateUserService,
    CreateUserAccountService,
    CreateSessionService,
    ValidateAuthorizationService,
    TerminateSessionService,
    CheckEmailAvailabilityService,
    ValidateTokenService
)

__all__ = [
    "AuthenticateUserService",
    "CreateUserAccountService",
    "CreateSessionService",
    "ValidateAuthorizationService",
    "TerminateSessionService",
    "CheckEmailAvailabilityService",
    "ValidateTokenService"
]
