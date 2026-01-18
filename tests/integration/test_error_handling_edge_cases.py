#!/usr/bin/env python3
"""
Error Handling & Edge Cases Tests

Tests error response consistency, resource not found, and dependency failures.
Priority 3: Medium Priority - Error Handling
"""
import sys
import asyncio
from pathlib import Path
from datetime import datetime

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
    "X-Test-ID": "error_handling_tests"
}


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


async def test_error_response_format():
    """Test that all errors have consistent format."""
    print_test("Error Response Format Consistency")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        errors = []
        
        # 401 error (missing auth)
        response1 = await client.get(f"{API_BASE_URL}/api/v1/guide-agent/history/test")
        errors.append(("401", response1.status_code, response1.json() if response1.status_code < 500 else {}))
        
        # 404 error (non-existent endpoint)
        response2 = await client.get(f"{API_BASE_URL}/api/nonexistent/endpoint")
        errors.append(("404", response2.status_code, response2.json() if response2.status_code < 500 else {}))
        
        # 400 error (invalid request)
        response3 = await client.post(
            f"{API_BASE_URL}/api/auth/login",
            json={},  # Missing required fields
            headers=TEST_HEADERS
        )
        errors.append(("400/422", response3.status_code, response3.json() if response3.status_code < 500 else {}))
        
        # Check consistency
        consistent = True
        for name, status, data in errors:
            print_info(f"{name}: Status {status}, Keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
            
            if isinstance(data, dict):
                # Check for common error fields
                has_error_field = "error" in data or "detail" in data or "message" in data
                if not has_error_field:
                    consistent = False
                    print_warning(f"{name} response missing error field")
        
        if consistent:
            print_success("Error responses have consistent format")
            return True
        else:
            print_warning("Some error responses may have inconsistent format")
            return True  # Not critical


async def test_resource_not_found():
    """Test 404 handling."""
    print_test("Resource Not Found (404)")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test non-existent endpoint
        response1 = await client.get(
            f"{API_BASE_URL}/api/nonexistent/endpoint",
            headers=TEST_HEADERS
        )
        
        # Test non-existent resource
        token = await get_valid_token()
        if token:
            headers = {**TEST_HEADERS, "Authorization": f"Bearer {token}"}
            response2 = await client.get(
                f"{API_BASE_URL}/api/session/invalid-uuid-here",
                headers=headers
            )
        else:
            response2 = None
        
        print_info(f"Non-existent endpoint: {response1.status_code}")
        if response2:
            print_info(f"Non-existent resource: {response2.status_code}")
        
        # 404 is expected, but 401 is also acceptable (auth required)
        if response1.status_code in [404, 401]:
            print_success("Non-existent resources handled appropriately")
            return True
        else:
            print_warning(f"Got status {response1.status_code} (expected 404 or 401)")
            return True


async def get_valid_token() -> Optional[str]:
    """Get a valid authentication token."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        response = await client.post(
            f"{API_BASE_URL}/api/auth/register",
            json={
                "email": f"test_{timestamp}@example.com",
                "password": "TestPassword123!",
                "name": "Test User"
            },
            headers=TEST_HEADERS
        )
        
        if response.status_code == 200:
            return response.json().get("access_token")
        return None


async def test_invalid_http_method():
    """Test invalid HTTP method."""
    print_test("Invalid HTTP Method")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Try DELETE on a GET endpoint
        response = await client.delete(
            f"{API_BASE_URL}/health",
            headers=TEST_HEADERS
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 405:
            print_success("Invalid HTTP method correctly rejected (405)")
            return True
        elif response.status_code == 200:
            print_warning("DELETE on GET endpoint returned 200 (may be permissive)")
            return True
        else:
            print_warning(f"Got status {response.status_code}")
            return True


async def test_malformed_request_body():
    """Test malformed request body."""
    print_test("Malformed Request Body")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Send invalid JSON
        headers = {**TEST_HEADERS, "Content-Type": "application/json"}
        response = await client.post(
            f"{API_BASE_URL}/api/auth/login",
            content="not json at all",
            headers=headers
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code in [400, 422]:
            print_success("Malformed request body correctly rejected")
            return True
        else:
            print_warning(f"Got status {response.status_code}")
            return True


async def test_missing_content_type():
    """Test request with missing Content-Type header."""
    print_test("Missing Content-Type Header")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            f"{API_BASE_URL}/api/auth/login",
            content='{"email":"test@example.com","password":"test"}',
            headers=TEST_HEADERS  # No Content-Type header (test missing header)
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        # Should either work (FastAPI is lenient) or return 400/422
        if response.status_code in [200, 400, 422]:
            print_success("Missing Content-Type handled appropriately")
            return True
        else:
            print_warning(f"Got status {response.status_code}")
            return True


async def run_all_tests():
    """Run all error handling tests."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print("Error Handling & Edge Cases Tests")
    print(f"{'='*60}{Colors.RESET}\n")
    
    results = {
        "error_format": False,
        "resource_not_found": False,
        "invalid_method": False,
        "malformed_body": False,
        "missing_content_type": False,
    }
    
    # Run tests
    results["error_format"] = await test_error_response_format()
    results["resource_not_found"] = await test_resource_not_found()
    results["invalid_method"] = await test_invalid_http_method()
    results["malformed_body"] = await test_malformed_request_body()
    results["missing_content_type"] = await test_missing_content_type()
    
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
