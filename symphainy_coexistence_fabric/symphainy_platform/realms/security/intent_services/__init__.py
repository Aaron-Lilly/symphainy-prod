"""
Security Realm Intent Services

Intent services for the Security Realm. Each service implements a single intent type
following the BaseIntentService pattern.

Architecture:
- Intent services wrap Security Guard SDK (infrastructure layer)
- All services use Public Works abstractions (auth, tenancy)
- Services provide consistent interface for solution pattern
- Enables MCP tools and agent-based security operations

Services:
- AuthenticateUserService: Authenticate user credentials
- CreateUserAccountService: Register new user account
- CreateSessionService: Create authenticated session
- ValidateAuthorizationService: Check user permissions
- TerminateSessionService: Logout and terminate session
- CheckEmailAvailabilityService: Check if email is available
- ValidateTokenService: Validate authentication token
"""

from .authenticate_user_service import AuthenticateUserService
from .create_user_account_service import CreateUserAccountService
from .create_session_service import CreateSessionService
from .validate_authorization_service import ValidateAuthorizationService
from .terminate_session_service import TerminateSessionService
from .check_email_availability_service import CheckEmailAvailabilityService
from .validate_token_service import ValidateTokenService

__all__ = [
    "AuthenticateUserService",
    "CreateUserAccountService",
    "CreateSessionService",
    "ValidateAuthorizationService",
    "TerminateSessionService",
    "CheckEmailAvailabilityService",
    "ValidateTokenService"
]
