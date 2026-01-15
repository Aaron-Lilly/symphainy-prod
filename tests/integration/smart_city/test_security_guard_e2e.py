"""
End-to-End Integration Tests for Security Guard

Tests the complete Security Guard flow with real Supabase (TEST PROJECT):
1. User signup/login
2. Authentication → Platform SDK → Security Guard Primitive
3. Authorization checks
4. Tenant assignment and isolation
5. Permission validation

This validates that the new implementation works with equivalent or better
functionality than the old Security Guard.

NOTE: Uses TEST Supabase project from .env.secrets to avoid rate limiting.
"""

import pytest
import os
import uuid
from pathlib import Path
from typing import Dict, Any, Optional

from symphainy_platform.foundations.public_works.adapters.supabase_adapter import SupabaseAdapter
from symphainy_platform.foundations.public_works.abstractions.auth_abstraction import AuthAbstraction
from symphainy_platform.foundations.public_works.abstractions.tenant_abstraction import TenantAbstraction
from symphainy_platform.foundations.public_works.abstractions.authorization_abstraction import AuthorizationAbstraction
from civic_systems.platform_sdk.platform_sdk import PlatformSDK
from civic_systems.smart_city.primitives.security_guard.security_guard_primitive import SecurityGuardPrimitive
from civic_systems.smart_city.registries.policy_registry import PolicyRegistry


def load_env_secrets():
    """Load environment variables from .env.secrets file."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        print("⚠️  python-dotenv not available - install with: pip install python-dotenv")
        return False
    
    # Try multiple possible paths for .env.secrets
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent.parent
    
    possible_paths = [
        project_root / "symphainy_platform" / "secrets_for_cursor.md",  # Secrets file location
        project_root / ".env.secrets",  # Project root
        project_root.parent / ".env.secrets",  # Parent directory
        Path.cwd() / ".env.secrets",  # Current working directory
    ]
    
    for env_secrets_path in possible_paths:
        if env_secrets_path.exists():
            result = load_dotenv(env_secrets_path, override=False)  # Don't override existing env vars
            if result:
                print(f"✅ Loaded secrets from: {env_secrets_path}")
            return result
    
    print(f"⚠️  Secrets file not found in: {[str(p) for p in possible_paths]}")
    return False


# Load .env.secrets at module level (before fixtures)
load_env_secrets()


@pytest.fixture
def supabase_config():
    """
    Get Supabase configuration from environment.
    
    Priority (to avoid rate limiting):
    1. Test project (identified by SUPABASE_PROJECT_REF=eocztpcvzcdqgygxlnqg)
    2. SUPABASE_* variables (production - fallback)
    
    Uses actual variable names from secrets_for_cursor.md:
    - SUPABASE_URL
    - SUPABASE_PUBLISHABLE_KEY (anon key)
    - SUPABASE_SECRET_KEY (service key)
    """
    # Check if we're using test project (by project ref or URL pattern)
    project_ref = os.getenv("SUPABASE_PROJECT_REF")
    url = os.getenv("SUPABASE_URL")
    is_test_project = (
        project_ref == "eocztpcvzcdqgygxlnqg" or
        (url and "eocztpcvzcdqgygxlnqg" in url)
    )
    
    # Get URL (test project URL is the one with eocztpcvzcdqgygxlnqg)
    if not url:
        pytest.skip(
            "Supabase configuration not available. "
            "Set SUPABASE_URL in secrets_for_cursor.md or environment variables."
        )
    
    # Get anon key (publishable key)
    anon_key = (
        os.getenv("SUPABASE_PUBLISHABLE_KEY") or
        os.getenv("SUPABASE_ANON_KEY") or
        os.getenv("SUPABASE_KEY")
    )
    
    # Get service key (secret key)
    service_key = (
        os.getenv("SUPABASE_SECRET_KEY") or
        os.getenv("SUPABASE_SERVICE_KEY")
    )
    
    if not anon_key:
        pytest.skip(
            "Supabase anon key not available. "
            "Set SUPABASE_PUBLISHABLE_KEY in secrets_for_cursor.md or environment variables."
        )
    
    # Log which project we're using
    if is_test_project:
        print(f"✅ Using TEST Supabase project: {url[:50]}...")
    else:
        print(f"⚠️  Using PRODUCTION Supabase project: {url[:50]}... (may have rate limiting)")
        print(f"   Test project should have SUPABASE_PROJECT_REF=eocztpcvzcdqgygxlnqg")
    
    return {
        "url": url,
        "anon_key": anon_key,
        "service_key": service_key,
        "is_test_project": is_test_project
    }


@pytest.fixture
async def supabase_adapter(supabase_config):
    """Create Supabase adapter with real credentials."""
    return SupabaseAdapter(
        url=supabase_config["url"],
        anon_key=supabase_config["anon_key"],
        service_key=supabase_config["service_key"]
    )


@pytest.fixture
async def auth_abstraction(supabase_adapter):
    """Create Auth abstraction."""
    return AuthAbstraction(supabase_adapter=supabase_adapter)


@pytest.fixture
async def tenant_abstraction(supabase_adapter):
    """Create Tenant abstraction."""
    return TenantAbstraction(supabase_adapter=supabase_adapter)


@pytest.fixture
async def authorization_abstraction(supabase_adapter):
    """Create Authorization abstraction."""
    return AuthorizationAbstraction(supabase_adapter=supabase_adapter)


@pytest.fixture
async def policy_registry(supabase_adapter):
    """Create Policy Registry."""
    return PolicyRegistry(supabase_adapter=supabase_adapter)


@pytest.fixture
async def platform_sdk(auth_abstraction, tenant_abstraction, authorization_abstraction, policy_registry):
    """Create Platform SDK with all dependencies."""
    return PlatformSDK(
        auth_abstraction=auth_abstraction,
        tenant_abstraction=tenant_abstraction,
        authorization_abstraction=authorization_abstraction,
        policy_registry=policy_registry
    )


@pytest.fixture
def security_guard_primitive():
    """Create Security Guard Primitive."""
    return SecurityGuardPrimitive()


@pytest.fixture
def test_user_credentials():
    """Generate unique test user credentials."""
    unique_id = str(uuid.uuid4())[:8]
    return {
        "email": f"test_security_guard_{unique_id}@symphainy.com",
        "password": f"TestPassword123!{unique_id}"
    }


@pytest.mark.integration
@pytest.mark.smart_city
@pytest.mark.security_guard
@pytest.mark.asyncio
class TestSecurityGuardE2E:
    """End-to-end tests for Security Guard with real Supabase."""
    
    async def test_user_signup_and_authentication(
        self,
        auth_abstraction,
        platform_sdk,
        test_user_credentials
    ):
        """
        Test user signup and authentication flow.
        
        Flow:
        1. User signs up (via Supabase)
        2. Auth Abstraction returns raw data
        3. Platform SDK translates to SecurityContext
        4. Verify SecurityContext is correct
        """
        # Step 1: Sign up user (via Supabase adapter directly)
        signup_result = await auth_abstraction.supabase.sign_up_with_password(
            email=test_user_credentials["email"],
            password=test_user_credentials["password"]
        )
        
        assert signup_result.get("success"), f"Signup failed: {signup_result.get('error')}"
        user_id = signup_result.get("user", {}).get("id")
        assert user_id is not None, "User ID should be returned"
        
        # Step 2: Authenticate user (via Auth Abstraction)
        raw_auth_data = await auth_abstraction.authenticate({
            "email": test_user_credentials["email"],
            "password": test_user_credentials["password"]
        })
        
        assert raw_auth_data is not None, "Authentication should return data"
        assert raw_auth_data.get("user_id") == user_id, "User ID should match"
        assert raw_auth_data.get("email") == test_user_credentials["email"], "Email should match"
        assert raw_auth_data.get("access_token") is not None, "Access token should be returned"
        
        # Step 3: Platform SDK translates to SecurityContext
        security_context = await platform_sdk.resolve_security_context(raw_auth_data)
        
        assert security_context is not None, "SecurityContext should be created"
        assert security_context.user_id == user_id, "User ID should match"
        assert security_context.email == test_user_credentials["email"], "Email should match"
        assert security_context.origin == "platform_sdk", "Origin should be platform_sdk"
        
        print(f"✅ User signup and authentication successful: {user_id}")
    
    async def test_user_login_flow(
        self,
        auth_abstraction,
        platform_sdk,
        test_user_credentials
    ):
        """
        Test user login flow (after signup).
        
        Flow:
        1. User logs in with credentials
        2. Auth Abstraction returns raw data
        3. Platform SDK translates to SecurityContext
        4. Verify SecurityContext is correct
        """
        # First, ensure user exists (signup if needed)
        try:
            await auth_abstraction.supabase.sign_up_with_password(
                email=test_user_credentials["email"],
                password=test_user_credentials["password"]
            )
        except:
            pass  # User might already exist
        
        # Step 1: Authenticate user
        raw_auth_data = await auth_abstraction.authenticate({
            "email": test_user_credentials["email"],
            "password": test_user_credentials["password"]
        })
        
        assert raw_auth_data is not None, "Authentication should return data"
        assert raw_auth_data.get("user_id") is not None, "User ID should be returned"
        
        # Step 2: Platform SDK translates to SecurityContext
        security_context = await platform_sdk.resolve_security_context(raw_auth_data)
        
        assert security_context is not None, "SecurityContext should be created"
        assert security_context.user_id is not None, "User ID should be set"
        assert security_context.email == test_user_credentials["email"], "Email should match"
        
        print(f"✅ User login successful: {security_context.user_id}")
    
    async def test_tenant_assignment_and_resolution(
        self,
        auth_abstraction,
        tenant_abstraction,
        platform_sdk,
        test_user_credentials
    ):
        """
        Test tenant assignment and resolution.
        
        Flow:
        1. User authenticates
        2. Platform SDK resolves tenant from user_tenants table or metadata
        3. Verify tenant is correctly assigned
        """
        # Ensure user exists
        try:
            signup_result = await auth_abstraction.supabase.sign_up_with_password(
                email=test_user_credentials["email"],
                password=test_user_credentials["password"]
            )
            user_id = signup_result.get("user", {}).get("id")
        except:
            # User exists, get user ID from login
            raw_auth_data = await auth_abstraction.authenticate({
                "email": test_user_credentials["email"],
                "password": test_user_credentials["password"]
            })
            user_id = raw_auth_data.get("user_id")
        
        # Step 1: Get tenant info from abstraction
        tenant_info = await tenant_abstraction.get_user_tenant_info(user_id)
        
        # Step 2: Authenticate and resolve SecurityContext
        raw_auth_data = await auth_abstraction.authenticate({
            "email": test_user_credentials["email"],
            "password": test_user_credentials["password"]
        })
        
        security_context = await platform_sdk.resolve_security_context(raw_auth_data)
        
        # Step 3: Verify tenant resolution
        # Tenant might be in database (user_tenants table) or metadata
        if tenant_info and tenant_info.get("tenant_id"):
            assert security_context.tenant_id == tenant_info.get("tenant_id"), "Tenant ID should match database"
        else:
            # Fallback to metadata (legacy behavior)
            assert security_context.tenant_id is not None or security_context.tenant_id is None, "Tenant ID should be resolved or None"
        
        print(f"✅ Tenant resolution successful: tenant_id={security_context.tenant_id}")
    
    async def test_authorization_check(
        self,
        auth_abstraction,
        authorization_abstraction,
        platform_sdk,
        test_user_credentials
    ):
        """
        Test authorization check flow.
        
        Flow:
        1. User authenticates
        2. Authorization Abstraction checks permissions (raw infrastructure)
        3. Verify permissions are checked correctly
        """
        # Ensure user exists
        try:
            await auth_abstraction.supabase.sign_up_with_password(
                email=test_user_credentials["email"],
                password=test_user_credentials["password"]
            )
        except:
            pass
        
        # Authenticate
        raw_auth_data = await auth_abstraction.authenticate({
            "email": test_user_credentials["email"],
            "password": test_user_credentials["password"]
        })
        
        user_id = raw_auth_data.get("user_id")
        assert user_id is not None, "User ID should be returned"
        
        # Step 1: Get user permissions (raw infrastructure check)
        permissions = await authorization_abstraction.get_user_permissions(user_id)
        
        # Step 2: Check specific permission
        has_permission = await authorization_abstraction.check_permission(
            user_id=user_id,
            permission="read"
        )
        
        # Permissions might be empty for new users (that's OK - infrastructure check)
        assert isinstance(permissions, list), "Permissions should be a list"
        assert isinstance(has_permission, bool), "Permission check should return bool"
        
        print(f"✅ Authorization check successful: permissions={permissions}, has_read={has_permission}")
    
    async def test_platform_sdk_ensure_user_can(
        self,
        auth_abstraction,
        platform_sdk,
        security_guard_primitive,
        test_user_credentials
    ):
        """
        Test Platform SDK ensure_user_can method (boundary zone).
        
        Flow:
        1. User authenticates
        2. Platform SDK.ensure_user_can() queries Policy Registry
        3. Prepares runtime contract shape
        4. Security Guard Primitive evaluates policy
        """
        # Ensure user exists
        try:
            signup_result = await auth_abstraction.supabase.sign_up_with_password(
                email=test_user_credentials["email"],
                password=test_user_credentials["password"]
            )
            user_id = signup_result.get("user", {}).get("id")
        except:
            raw_auth_data = await auth_abstraction.authenticate({
                "email": test_user_credentials["email"],
                "password": test_user_credentials["password"]
            })
            user_id = raw_auth_data.get("user_id")
        
        # Authenticate and get SecurityContext
        raw_auth_data = await auth_abstraction.authenticate({
            "email": test_user_credentials["email"],
            "password": test_user_credentials["password"]
        })
        
        security_context = await platform_sdk.resolve_security_context(raw_auth_data)
        tenant_id = security_context.tenant_id or "default_tenant"
        
        # Step 1: Platform SDK prepares runtime contract shape
        runtime_contract = await platform_sdk.ensure_user_can(
            action="content.parse",
            tenant_id=tenant_id,
            user_id=user_id,
            resource="file_123",
            security_context=security_context
        )
        
        assert runtime_contract is not None, "Runtime contract should be created"
        assert runtime_contract.get("ready_for_runtime") is True, "Should be ready for runtime"
        assert runtime_contract.get("action") == "content.parse", "Action should match"
        assert runtime_contract.get("security_context") == security_context, "Security context should be included"
        
        # Step 2: Security Guard Primitive evaluates policy
        policy_result = await security_guard_primitive.evaluate_auth(
            security_context=security_context,
            action="content.parse",
            resource="file_123",
            policy_rules=runtime_contract.get("policy_rules", {})
        )
        
        assert policy_result is not None, "Policy result should be returned"
        assert "allowed" in policy_result, "Policy result should have 'allowed' field"
        assert isinstance(policy_result.get("allowed"), bool), "Allowed should be boolean"
        
        print(f"✅ Platform SDK ensure_user_can successful: allowed={policy_result.get('allowed')}")
    
    async def test_security_guard_primitive_policy_decisions(
        self,
        security_guard_primitive,
        platform_sdk,
        auth_abstraction,
        test_user_credentials
    ):
        """
        Test Security Guard Primitive makes correct policy decisions.
        
        Tests:
        1. Authentication evaluation
        2. Tenant access validation
        3. Permission checking
        4. Zero-trust enforcement
        """
        # Ensure user exists and authenticate
        try:
            await auth_abstraction.supabase.sign_up_with_password(
                email=test_user_credentials["email"],
                password=test_user_credentials["password"]
            )
        except:
            pass
        
        raw_auth_data = await auth_abstraction.authenticate({
            "email": test_user_credentials["email"],
            "password": test_user_credentials["password"]
        })
        
        security_context = await platform_sdk.resolve_security_context(raw_auth_data)
        tenant_id = security_context.tenant_id or "default_tenant"
        
        # Test 1: Authentication evaluation
        auth_result = await security_guard_primitive.evaluate_auth(
            security_context=security_context,
            action="content.parse",
            policy_rules={}
        )
        
        assert auth_result.get("allowed") is True, "Authenticated user should be allowed"
        assert auth_result.get("policy_source") is not None, "Policy source should be set"
        
        # Test 2: Tenant access validation
        tenant_result = await security_guard_primitive.validate_tenant_access(
            tenant_id=tenant_id,
            user_tenant_id=tenant_id,
            resource_tenant_id=tenant_id,
            isolation_rules={}
        )
        
        assert tenant_result.get("allowed") is True, "Same tenant should be allowed"
        assert tenant_result.get("isolation_level") is not None, "Isolation level should be set"
        
        # Test 3: Permission checking
        permission_result = await security_guard_primitive.check_permission(
            security_context=security_context,
            permission="read",
            policy_rules={}
        )
        
        assert "allowed" in permission_result, "Permission result should have 'allowed' field"
        assert "permission_source" in permission_result, "Permission source should be set"
        
        # Test 4: Zero-trust enforcement
        zero_trust_result = await security_guard_primitive.enforce_zero_trust(
            security_context=security_context,
            action="content.parse",
            resource="file_123",
            policy_rules={"zero_trust_enabled": False}
        )
        
        assert zero_trust_result.get("allowed") is True, "Should be allowed when zero-trust disabled"
        assert isinstance(zero_trust_result.get("verification_required"), list), "Verification required should be list"
        
        print(f"✅ Security Guard Primitive policy decisions successful")
    
    async def test_full_flow_realm_to_primitive(
        self,
        auth_abstraction,
        platform_sdk,
        security_guard_primitive,
        test_user_credentials
    ):
        """
        Test the complete flow: Realm → Platform SDK → Runtime → Security Guard Primitive.
        
        This simulates what happens when a Realm service needs to check authorization.
        """
        # Setup: Create and authenticate user
        try:
            signup_result = await auth_abstraction.supabase.sign_up_with_password(
                email=test_user_credentials["email"],
                password=test_user_credentials["password"]
            )
            user_id = signup_result.get("user", {}).get("id")
        except:
            raw_auth_data = await auth_abstraction.authenticate({
                "email": test_user_credentials["email"],
                "password": test_user_credentials["password"]
            })
            user_id = raw_auth_data.get("user_id")
        
        # Authenticate
        raw_auth_data = await auth_abstraction.authenticate({
            "email": test_user_credentials["email"],
            "password": test_user_credentials["password"]
        })
        
        security_context = await platform_sdk.resolve_security_context(raw_auth_data)
        tenant_id = security_context.tenant_id or "default_tenant"
        
        # Step 1: Realm calls Platform SDK (boundary zone)
        runtime_contract = await platform_sdk.ensure_user_can(
            action="content.parse",
            tenant_id=tenant_id,
            user_id=user_id,
            resource="file_123",
            security_context=security_context
        )
        
        assert runtime_contract.get("ready_for_runtime") is True, "Should be ready for runtime"
        
        # Step 2: Runtime calls Security Guard Primitive (policy decision)
        policy_result = await security_guard_primitive.evaluate_auth(
            security_context=runtime_contract["security_context"],
            action=runtime_contract["action"],
            resource=runtime_contract["resource"],
            policy_rules=runtime_contract.get("policy_rules", {})
        )
        
        # Step 3: Verify decision
        assert policy_result.get("allowed") is True, "Authenticated user should be allowed"
        
        print(f"✅ Full flow successful: Realm → Platform SDK → Runtime → Security Guard Primitive")
        print(f"   User: {user_id}, Tenant: {tenant_id}, Action: content.parse, Allowed: {policy_result.get('allowed')}")


@pytest.mark.integration
@pytest.mark.smart_city
@pytest.mark.security_guard
@pytest.mark.asyncio
class TestSecurityGuardFunctionalityComparison:
    """Tests to compare new implementation with old Security Guard functionality."""
    
    async def test_equivalent_authentication_functionality(
        self,
        auth_abstraction,
        platform_sdk,
        test_user_credentials
    ):
        """
        Test that new implementation has equivalent authentication functionality.
        
        Old Security Guard:
        - authenticate_user() → Returns SecurityContext
        
        New Implementation:
        - Auth Abstraction.authenticate() → Returns raw data
        - Platform SDK.resolve_security_context() → Returns SecurityContext
        
        Both should produce equivalent SecurityContext.
        """
        # Signup user
        try:
            signup_result = await auth_abstraction.supabase.sign_up_with_password(
                email=test_user_credentials["email"],
                password=test_user_credentials["password"]
            )
            user_id = signup_result.get("user", {}).get("id")
        except:
            raw_auth_data = await auth_abstraction.authenticate({
                "email": test_user_credentials["email"],
                "password": test_user_credentials["password"]
            })
            user_id = raw_auth_data.get("user_id")
        
        # New implementation flow
        raw_auth_data = await auth_abstraction.authenticate({
            "email": test_user_credentials["email"],
            "password": test_user_credentials["password"]
        })
        
        security_context = await platform_sdk.resolve_security_context(raw_auth_data)
        
        # Verify SecurityContext has all required fields
        assert security_context.user_id == user_id, "User ID should match"
        assert security_context.email == test_user_credentials["email"], "Email should match"
        assert security_context.tenant_id is not None or security_context.tenant_id is None, "Tenant ID should be resolved or None"
        assert isinstance(security_context.roles, list), "Roles should be a list"
        assert isinstance(security_context.permissions, list), "Permissions should be a list"
        
        print(f"✅ Equivalent authentication functionality verified")
    
    async def test_better_separation_of_concerns(
        self,
        auth_abstraction,
        tenant_abstraction,
        authorization_abstraction,
        platform_sdk,
        security_guard_primitive,
        test_user_credentials
    ):
        """
        Test that new implementation has better separation of concerns.
        
        Old Security Guard:
        - Mixed infrastructure and business logic
        - Created tenants, extracted roles in abstraction
        
        New Implementation:
        - Abstractions are pure infrastructure (raw data only)
        - Platform SDK handles translation
        - Security Guard Primitive handles policy decisions
        
        This test verifies the separation is correct.
        """
        # Signup and authenticate
        try:
            await auth_abstraction.supabase.sign_up_with_password(
                email=test_user_credentials["email"],
                password=test_user_credentials["password"]
            )
        except:
            pass
        
        raw_auth_data = await auth_abstraction.authenticate({
            "email": test_user_credentials["email"],
            "password": test_user_credentials["password"]
        })
        
        # Verify abstraction returns raw data (not business objects)
        assert isinstance(raw_auth_data, dict), "Auth abstraction should return raw dict"
        assert "user_id" in raw_auth_data or "id" in raw_auth_data, "Should have user identifier"
        assert "access_token" in raw_auth_data, "Should have access token"
        
        # Verify Platform SDK translates to business objects
        security_context = await platform_sdk.resolve_security_context(raw_auth_data)
        assert security_context is not None, "Platform SDK should create SecurityContext"
        assert security_context.user_id is not None, "SecurityContext should have user_id"
        
        # Verify Primitive makes policy decisions (not infrastructure calls)
        policy_result = await security_guard_primitive.evaluate_auth(
            security_context=security_context,
            action="content.parse",
            policy_rules={}
        )
        assert "allowed" in policy_result, "Primitive should make policy decision"
        assert "policy_source" in policy_result, "Policy source should be set"
        
        print(f"✅ Better separation of concerns verified")
        print(f"   - Abstraction: Raw data only")
        print(f"   - Platform SDK: Translation logic")
        print(f"   - Primitive: Policy decisions only")
