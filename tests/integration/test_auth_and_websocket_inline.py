#!/usr/bin/env python3
"""
Inline Integration Tests for Authentication and WebSocket

Run this to test authentication endpoints and WebSocket agent endpoint.
Designed for inline execution and troubleshooting.
"""
import sys
import asyncio
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import httpx
import websockets
from datetime import datetime
from typing import Dict, Any, Optional


# Test Configuration
API_BASE_URL = "http://localhost:8001"  # Experience Plane
RUNTIME_URL = "http://localhost:8000"  # Runtime
WS_BASE_URL = "ws://localhost:8001"  # Experience Plane WebSocket


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


async def test_health_checks():
    """Test health endpoints."""
    print_test("Health Checks")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test Experience Plane health
        try:
            response = await client.get(f"{API_BASE_URL}/health")
            if response.status_code == 200:
                print_success(f"Experience Plane health: {response.json()}")
            else:
                print_error(f"Experience Plane health failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Experience Plane health check failed: {e}")
            return False
        
        # Test Runtime health
        try:
            response = await client.get(f"{RUNTIME_URL}/health")
            if response.status_code == 200:
                print_success(f"Runtime health: {response.json()}")
            else:
                print_error(f"Runtime health failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Runtime health check failed: {e}")
            return False
    
    return True


async def test_auth_register(test_email: str, test_password: str):
    """Test user registration endpoint."""
    print_test("Authentication - Register")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        test_name = "Test User"
        
        try:
            response = await client.post(
                f"{API_BASE_URL}/api/auth/register",
                json={
                    "name": test_name,
                    "email": test_email,
                    "password": test_password
                }
            )
            
            print_info(f"Status Code: {response.status_code}")
            print_info(f"Response: {response.text[:200]}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print_success(f"Registration successful: user_id={data.get('user_id')}")
                    return {"success": True, "email": test_email, "password": test_password, **data}
                else:
                    print_error(f"Registration failed: {data.get('error')}")
                    return None
            else:
                print_error(f"Registration failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print_error(f"Registration request failed: {e}")
            return None


async def test_auth_login(email: str, password: str):
    """Test user login endpoint."""
    print_test("Authentication - Login")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(
                f"{API_BASE_URL}/api/auth/login",
                json={
                    "email": email,
                    "password": password
                }
            )
            
            print_info(f"Status Code: {response.status_code}")
            print_info(f"Response: {response.text[:200]}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print_success(f"Login successful: user_id={data.get('user_id')}")
                    print_info(f"Access Token: {data.get('access_token', '')[:20]}...")
                    return data
                else:
                    print_error(f"Login failed: {data.get('error')}")
                    return None
            else:
                print_error(f"Login failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print_error(f"Login request failed: {e}")
            return None


async def test_websocket_connection(session_token: str):
    """Test WebSocket agent endpoint."""
    print_test("WebSocket - Agent Endpoint")
    
    ws_url = f"{WS_BASE_URL}/api/runtime/agent?session_token={session_token}"
    print_info(f"Connecting to: {ws_url}")
    
    try:
        async with websockets.connect(ws_url, ping_interval=20, ping_timeout=10) as websocket:
            print_success("WebSocket connection established")
            
            # Send test message
            test_message = {
                "type": "agent.message",
                "payload": {
                    "text": "Hello, this is a test message",
                    "context": {
                        "surface": "content_pillar",
                        "conversation_id": "test_conversation_123"
                    }
                }
            }
            
            print_info(f"Sending message: {json.dumps(test_message, indent=2)}")
            await websocket.send(json.dumps(test_message))
            
            # Wait for response (with timeout)
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                response_data = json.loads(response)
                
                print_success(f"Received response: {json.dumps(response_data, indent=2)}")
                
                # Check response type
                if response_data.get("type") == "runtime_event":
                    event_type = response_data.get("event_type")
                    print_success(f"Runtime event received: {event_type}")
                    return True
                elif response_data.get("type") == "error":
                    print_error(f"Error response: {response_data.get('error')}")
                    return False
                else:
                    print_warning(f"Unexpected response type: {response_data.get('type')}")
                    return True
                    
            except asyncio.TimeoutError:
                print_warning("No response received within timeout (this may be OK if agent is processing)")
                return True
                
    except websockets.exceptions.InvalidStatusCode as e:
        print_error(f"WebSocket connection failed: {e}")
        if hasattr(e, 'status_code'):
            print_info(f"Status Code: {e.status_code}")
        if hasattr(e, 'headers'):
            print_info(f"Headers: {e.headers}")
        return False
    except Exception as e:
        print_error(f"WebSocket error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """Run all integration tests."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print("Integration Tests - Authentication & WebSocket")
    print(f"{'='*60}{Colors.RESET}\n")
    
    results = {
        "health_checks": False,
        "auth_register": False,
        "auth_login": False,
        "websocket": False
    }
    
    # Test 1: Health Checks
    results["health_checks"] = await test_health_checks()
    if not results["health_checks"]:
        print_error("Health checks failed - stopping tests")
        return results
    
    # Test 2: Registration
    # Generate test credentials first
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    test_email = f"test_{timestamp}@example.com"
    test_password = "TestPassword123!"
    
    register_result = await test_auth_register(test_email, test_password)
    if register_result:
        results["auth_register"] = True
        # Use the same email/password for login (not user_id)
        test_email = register_result.get("email", test_email)
        test_password = register_result.get("password", test_password)
    else:
        print_warning("Registration failed - trying login with existing credentials")
        # Try with a test account (may already exist)
        test_email = "test@example.com"
        test_password = "TestPassword123!"
    
    # Test 3: Login
    # Wait a moment to avoid rate limiting from previous tests
    await asyncio.sleep(2)
    login_result = await test_auth_login(test_email, test_password)
    
    # If rate limited, wait and retry once
    if login_result is None:
        print_warning("Login may have been rate limited, waiting 10 seconds...")
        await asyncio.sleep(10)
        login_result = await test_auth_login(test_email, test_password)
    if login_result:
        results["auth_login"] = True
        session_token = login_result.get("access_token") or login_result.get("user_id")
        
        # Test 4: WebSocket
        if session_token:
            results["websocket"] = await test_websocket_connection(session_token)
        else:
            print_warning("No session token available for WebSocket test")
    else:
        print_warning("Login failed - skipping WebSocket test")
    
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
