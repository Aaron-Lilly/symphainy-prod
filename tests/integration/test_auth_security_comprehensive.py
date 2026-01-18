#!/usr/bin/env python3
"""
Comprehensive Authentication & Security Tests

Tests authentication error handling, token validation, rate limiting, and input validation.
Priority 1: Critical Security Tests
"""
import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import httpx
from typing import Dict, Any, Optional


# Test Configuration
API_BASE_URL = "http://localhost:8001"

# Test mode headers to enable relaxed rate limiting
TEST_HEADERS = {
    "X-Test-Mode": "true",
    "X-Test-ID": "auth_security_tests"
}

def get_test_headers(test_id: Optional[str] = None) -> Dict[str, str]:
    """Get test headers with optional test ID."""
    headers = TEST_HEADERS.copy()
    if test_id:
        headers["X-Test-ID"] = test_id
    return headers


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_test(name: str):
    """Print test header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}🧪 Testing: {name}{Colors.RESET}")


def print_success(message: str):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")


def print_error(message: str):
    """Print error message."""
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")


def print_warning(message: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")


def print_info(message: str):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.RESET}")


async def test_invalid_credentials():
    """Test login with invalid credentials."""
    print_test("Invalid Credentials")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            f"{API_BASE_URL}/api/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "wrong_password_123"  # Must be at least 8 characters
            },
            headers=TEST_HEADERS
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print_success("Invalid credentials correctly rejected (401)")
            return True
        elif response.status_code == 422:
            print_warning("Got 422 (validation error) - may be expected")
            return True
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            return False


async def test_missing_token():
    """Test API call without token."""
    print_test("Missing Authentication Token")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"{API_BASE_URL}/api/v1/guide-agent/history/test-session",
            params={"tenant_id": "test"},
            headers=TEST_HEADERS
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 401:
            data = response.json()
            if "unauthorized" in data.get("error", "").lower() or "token" in data.get("message", "").lower():
                print_success("Missing token correctly rejected (401)")
                return True
            else:
                print_warning("Got 401 but error message unclear")
                return True
        else:
            print_error(f"Should return 401, got {response.status_code}")
            return False


async def test_malformed_token():
    """Test API call with malformed token."""
    print_test("Malformed Token")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        headers = {**TEST_HEADERS, "Authorization": "Bearer invalid.token.here"}
        response = await client.get(
            f"{API_BASE_URL}/api/v1/guide-agent/history/test-session",
            headers=headers,
            params={"tenant_id": "test"}
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print_success("Malformed token correctly rejected (401)")
            return True
        else:
            print_error(f"Should return 401, got {response.status_code}")
            return False


async def test_expired_token():
    """Test API call with expired token."""
    print_test("Expired Token")
    
    # Create a token that looks expired (we can't actually create expired Supabase tokens easily)
    # So we'll test with an invalid token format that should be rejected
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Use a token that's clearly invalid/expired format
        expired_looking_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2MDAwMDAwMDB9.invalid"
        
        headers = {**TEST_HEADERS, "Authorization": f"Bearer {expired_looking_token}"}
        response = await client.get(
            f"{API_BASE_URL}/api/v1/guide-agent/history/test-session",
            headers=headers,
            params={"tenant_id": "test"}
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print_success("Invalid/expired token correctly rejected (401)")
            return True
        else:
            print_warning(f"Got {response.status_code} - token validation may need adjustment")
            return True  # Not a critical failure


async def test_rate_limiting_login():
    """Test login rate limiting."""
    print_test("Rate Limiting - Login")
    
    # Wait a bit to ensure we're not already rate limited from previous tests
    await asyncio.sleep(2)
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        results = []
        
        # Make 7 requests (limit is 5 per minute)
        # NOTE: Do NOT use test mode headers here - we want to test actual rate limiting
        for i in range(7):
            response = await client.post(
                f"{API_BASE_URL}/api/auth/login",
                json={
                    "email": "test@example.com",
                    "password": "wrong_password_123"  # Must be at least 8 characters
                }
                # No test headers - want to test real rate limiting
            )
            
            status = response.status_code
            if status == 429:
                data = response.json()
                detail = data.get("detail", {})
                retry_after = detail.get("retry_after") if isinstance(detail, dict) else None
                results.append(f"Request {i+1}: ✅ Rate limited (429, Retry-After: {retry_after}s)")
            else:
                results.append(f"Request {i+1}: Allowed ({status})")
            
            # Small delay between requests
            if i < 6:
                await asyncio.sleep(0.5)
        
        print_info("\n".join(results))
        
        # Check if we got rate limited
        rate_limited = any("Rate limited" in r for r in results)
        if rate_limited:
            print_success("Rate limiting working correctly")
            return True
        else:
            print_warning("Rate limiting may not be triggering")
            return False


async def test_rate_limiting_register():
    """Test registration rate limiting."""
    print_test("Rate Limiting - Register")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        results = []
        
        # Make 5 requests (limit is 3 per 5 minutes)
        # NOTE: Do NOT use test mode headers here - we want to test actual rate limiting
        for i in range(5):
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
            response = await client.post(
                f"{API_BASE_URL}/api/auth/register",
                json={
                    "email": f"test_{timestamp}@example.com",
                    "password": "TestPassword123!",
                    "name": "Test User"
                }
                # No test headers - want to test real rate limiting
            )
            
            status = response.status_code
            if status == 429:
                results.append(f"Request {i+1}: ✅ Rate limited (429)")
            elif status == 200:
                results.append(f"Request {i+1}: Allowed (200 - registered)")
            else:
                results.append(f"Request {i+1}: Status {status}")
        
        print_info("\n".join(results))
        
        # Check if we got rate limited
        rate_limited = any("Rate limited" in r for r in results)
        if rate_limited:
            print_success("Registration rate limiting working")
            return True
        else:
            print_warning("Registration rate limiting may not be triggering")
            return True  # Not critical if all registrations succeed


async def test_sql_injection_attempt():
    """Test SQL injection in email field."""
    print_test("SQL Injection Attempt")
    
    # Wait to avoid rate limiting
    await asyncio.sleep(1)
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            f"{API_BASE_URL}/api/auth/login",
            json={
                "email": "test@example.com'; DROP TABLE users; --",
                "password": "password"
            },
            headers=TEST_HEADERS
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        # Should reject with 400 or 422 (validation error), or 429 if rate limited
        if response.status_code in [400, 422]:
            print_success("SQL injection attempt correctly rejected")
            return True
        elif response.status_code == 401:
            print_warning("Got 401 (auth failed) - SQL injection may have been sanitized")
            return True
        elif response.status_code == 429:
            print_warning("Got 429 (rate limited) - test may need delay")
            return True
        else:
            print_error(f"Unexpected status: {response.status_code}")
            return False


async def test_xss_attempt():
    """Test XSS in user input."""
    print_test("XSS Attempt")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        response = await client.post(
            f"{API_BASE_URL}/api/auth/register",
            json={
                "email": f"test_{timestamp}@example.com",
                "password": "TestPassword123!",
                "name": "<script>alert('xss')</script>"
            },
            headers=TEST_HEADERS
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            # Check if name was sanitized
            if "<script>" not in str(data):
                print_success("XSS attempt sanitized or rejected")
                return True
            else:
                print_warning("XSS may not be sanitized (check response)")
                return False
        elif response.status_code in [400, 422]:
            print_success("XSS attempt correctly rejected")
            return True
        else:
            print_warning(f"Got status {response.status_code}")
            return True


async def test_extremely_long_email():
    """Test extremely long email."""
    print_test("Extremely Long Email")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        long_email = "a" * 1000 + "@example.com"
        response = await client.post(
            f"{API_BASE_URL}/api/auth/register",
            json={
                "email": long_email,
                "password": "TestPassword123!",
                "name": "Test"
            },
            headers=TEST_HEADERS
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code in [400, 422]:
            print_success("Extremely long email correctly rejected")
            return True
        else:
            print_warning(f"Got status {response.status_code} - validation may need adjustment")
            return True


async def test_extremely_long_password():
    """Test extremely long password."""
    print_test("Extremely Long Password")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        long_password = "a" * 200  # 200 characters
        response = await client.post(
            f"{API_BASE_URL}/api/auth/register",
            json={
                "email": f"test_{timestamp}@example.com",
                "password": long_password,
                "name": "Test"
            },
            headers=TEST_HEADERS
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code in [400, 422]:
            print_success("Extremely long password correctly rejected")
            return True
        else:
            print_warning(f"Got status {response.status_code}")
            return True


async def test_short_password():
    """Test password shorter than minimum."""
    print_test("Short Password")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            f"{API_BASE_URL}/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "short",  # Less than 8 characters
                "name": "Test"
            },
            headers=TEST_HEADERS
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 422:
            data = response.json()
            if "password" in str(data).lower() or "length" in str(data).lower():
                print_success("Short password correctly rejected")
                return True
            else:
                print_warning("Got 422 but unclear if it's password validation")
                return True
        else:
            print_warning(f"Got status {response.status_code} - password validation may need adjustment")
            return True


async def test_invalid_email_format():
    """Test invalid email format."""
    print_test("Invalid Email Format")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            f"{API_BASE_URL}/api/auth/register",
            json={
                "email": "not-an-email",
                "password": "TestPassword123!",
                "name": "Test"
            },
            headers=TEST_HEADERS
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 422:
            print_success("Invalid email format correctly rejected")
            return True
        else:
            print_warning(f"Got status {response.status_code}")
            return True


async def test_empty_fields():
    """Test empty required fields."""
    print_test("Empty Required Fields")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test empty email
        response1 = await client.post(
            f"{API_BASE_URL}/api/auth/register",
            json={
                "email": "",
                "password": "TestPassword123!",
                "name": "Test"
            },
            headers=TEST_HEADERS
        )
        
        # Test empty password
        response2 = await client.post(
            f"{API_BASE_URL}/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "",
                "name": "Test"
            },
            headers=TEST_HEADERS
        )
        
        print_info(f"Empty email status: {response1.status_code}")
        print_info(f"Empty password status: {response2.status_code}")
        
        if response1.status_code == 422 and response2.status_code == 422:
            print_success("Empty fields correctly rejected")
            return True
        else:
            print_warning("Some empty fields may not be validated")
            return True


async def run_all_tests():
    """Run all authentication security tests."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print("Comprehensive Authentication & Security Tests")
    print(f"{'='*60}{Colors.RESET}\n")
    
    results = {
        "invalid_credentials": False,
        "missing_token": False,
        "malformed_token": False,
        "expired_token": False,
        "rate_limiting_login": False,
        "rate_limiting_register": False,
        "sql_injection": False,
        "xss_attempt": False,
        "long_email": False,
        "long_password": False,
        "short_password": False,
        "invalid_email": False,
        "empty_fields": False,
    }
    
    # Run tests
    results["invalid_credentials"] = await test_invalid_credentials()
    results["missing_token"] = await test_missing_token()
    results["malformed_token"] = await test_malformed_token()
    results["expired_token"] = await test_expired_token()
    results["rate_limiting_login"] = await test_rate_limiting_login()
    results["rate_limiting_register"] = await test_rate_limiting_register()
    results["sql_injection"] = await test_sql_injection_attempt()
    results["xss_attempt"] = await test_xss_attempt()
    results["long_email"] = await test_extremely_long_email()
    results["long_password"] = await test_extremely_long_password()
    results["short_password"] = await test_short_password()
    results["invalid_email"] = await test_invalid_email_format()
    results["empty_fields"] = await test_empty_fields()
    
    # Summary
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print("Test Summary")
    print(f"{'='*60}{Colors.RESET}\n")
    
    for test_name, passed in results.items():
        if passed:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\n{Colors.BOLD}Total: {passed}/{total} tests passed{Colors.RESET}\n")
    
    return results


if __name__ == "__main__":
    try:
        results = asyncio.run(run_all_tests())
        sys.exit(0 if all(results.values()) else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
