"""
Security Capability Intent Services (Platform SDK Architecture)

These intent services use the PlatformIntentService base class
and receive PlatformContext (ctx) for execution.

Architecture:
    - Services extend PlatformIntentService
    - Services receive PlatformContext (ctx) at execute time
    - Services access platform via ctx.platform, ctx.governance

Authentication:
    - AuthenticateUserService: Authenticate user credentials
    - ValidateTokenService: Validate authentication token

Registration:
    - CreateUserAccountService: Register new user account
    - CheckEmailAvailabilityService: Check if email is available

Session Management:
    - CreateSessionService: Create authenticated session
    - ValidateAuthorizationService: Check user permissions
    - TerminateSessionService: Logout and terminate session
"""

from .authenticate_user_service import AuthenticateUserService
from .check_email_availability_service import CheckEmailAvailabilityService
from .create_session_service import CreateSessionService
from .create_user_account_service import CreateUserAccountService
from .terminate_session_service import TerminateSessionService
from .validate_authorization_service import ValidateAuthorizationService
from .validate_token_service import ValidateTokenService

__all__ = [
    "AuthenticateUserService",
    "CheckEmailAvailabilityService",
    "CreateSessionService",
    "CreateUserAccountService",
    "TerminateSessionService",
    "ValidateAuthorizationService",
    "ValidateTokenService",
]
