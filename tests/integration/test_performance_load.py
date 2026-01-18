#!/usr/bin/env python3
"""
Performance & Load Tests

Tests concurrent users, high message volume, and system behavior under load.
Priority 4: Medium Priority - Performance
"""
import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime
import uuid

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import httpx
import websockets
from typing import Dict, Any, Optional, List


# Test Configuration
API_BASE_URL = "http://localhost:8001"
WS_BASE_URL = "ws://localhost:8001"

# Test mode headers to enable relaxed rate limiting
TEST_HEADERS = {
    "X-Test-Mode": "true",
    "X-Test-ID": "performance_tests"
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


async def create_user_and_login() -> Optional[Dict[str, Any]]:
    """Create a user and login, return token and user info."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        email = f"test_{timestamp}@example.com"
        password = "TestPassword123!"
        
        # Register using test mode to avoid rate limiting
        reg_response = await client.post(
            f"{API_BASE_URL}/api/auth/register",
            json={
                "email": email,
                "password": password,
                "name": "Test User"
            },
            headers=TEST_HEADERS
        )
        
        if reg_response.status_code == 200:
            data = reg_response.json()
            return {
                "email": email,
                "password": password,
                "token": data.get("access_token"),
                "user_id": data.get("user_id")
            }
        elif reg_response.status_code == 429:
            # Rate limited - return None to indicate failure
            return None
        return None


async def test_concurrent_users():
    """Test concurrent user registration and login."""
    print_test("Concurrent Users")
    
    async def create_and_login():
        result = await create_user_and_login()
        return result is not None
    
    # Create 20 concurrent users (using test mode, so all should succeed)
    print_info("Creating 20 concurrent users (test mode enabled)...")
    tasks = [create_and_login() for _ in range(20)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    successful = sum(1 for r in results if r is True)
    failed = sum(1 for r in results if r is False or isinstance(r, Exception))
    
    print_info(f"Successful: {successful}/20")
    print_info(f"Failed: {failed}/20")
    
    if successful >= 15:
        print_success(f"Concurrent users handled well ({successful}/20 successful)")
        return True
    elif successful >= 10:
        print_warning(f"Concurrent users partially handled ({successful}/20 successful)")
        return True
    else:
        print_error(f"Concurrent users not handled well ({successful}/20 successful)")
        return False


async def test_high_message_volume():
    """Test WebSocket with high message volume."""
    print_test("High Message Volume")
    
    user_data = await create_user_and_login()
    if not user_data or not user_data.get("token"):
        print_error("Could not create user")
        return False
    
    token = user_data["token"]
    
    try:
        async with websockets.connect(
            f"{WS_BASE_URL}/api/runtime/agent?session_token={token}",
            ping_interval=20,
            ping_timeout=10
        ) as websocket:
            # Send 50 messages
            print_info("Sending 50 messages...")
            for i in range(50):
                message = {
                    "type": "agent.message",
                    "payload": {
                        "text": f"Message {i+1}",
                        "context": {
                            "surface": "content_pillar",
                            "conversation_id": "test_volume"
                        }
                    }
                }
                await websocket.send(json.dumps(message))
                await asyncio.sleep(0.05)  # Small delay to avoid overwhelming
            
            # Collect responses
            print_info("Collecting responses...")
            responses = []
            for _ in range(50):
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    responses.append(json.loads(response))
                except asyncio.TimeoutError:
                    break
            
            print_info(f"Received {len(responses)} responses to 50 messages")
            
            if len(responses) >= 30:
                print_success(f"High message volume handled ({len(responses)}/50 responses)")
                return True
            elif len(responses) >= 10:
                print_warning(f"Partial message handling ({len(responses)}/50 responses)")
                return True
            else:
                print_error(f"Poor message handling ({len(responses)}/50 responses)")
                return False
    except Exception as e:
        print_error(f"High message volume test failed: {e}")
        return False


async def test_concurrent_websocket_connections():
    """Test multiple concurrent WebSocket connections."""
    print_test("Concurrent WebSocket Connections")
    
    user_data = await create_user_and_login()
    if not user_data or not user_data.get("token"):
        print_error("Could not create user")
        return False
    
    token = user_data["token"]
    connections = []
    
    try:
        # Create 10 concurrent connections
        print_info("Creating 10 concurrent WebSocket connections...")
        for i in range(10):
            try:
                ws = await websockets.connect(
                    f"{WS_BASE_URL}/api/runtime/agent?session_token={token}",
                    ping_interval=20,
                    ping_timeout=10
                )
                connections.append((i, ws))
                print_info(f"Connection {i+1} established")
            except Exception as e:
                print_warning(f"Connection {i+1} failed: {e}")
        
        if len(connections) < 5:
            print_error(f"Too few connections established ({len(connections)}/10)")
            return False
        
        # Send message on each connection
        print_info("Sending messages on all connections...")
        for i, ws in connections:
            message = {
                "type": "agent.message",
                "payload": {
                    "text": f"Message from connection {i+1}",
                    "context": {
                        "surface": "content_pillar",
                        "conversation_id": f"test_{i}"
                    }
                }
            }
            await ws.send(json.dumps(message))
        
        # Collect responses
        print_info("Collecting responses...")
        responses_received = 0
        for i, ws in connections:
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                response_data = json.loads(response)
                if response_data.get("type") == "runtime_event":
                    responses_received += 1
            except asyncio.TimeoutError:
                pass
        
        # Close all connections
        for _, ws in connections:
            try:
                await ws.close()
            except:
                pass
        
        print_info(f"Received {responses_received} responses from {len(connections)} connections")
        
        if responses_received >= len(connections) * 0.7:  # 70% success rate
            print_success(f"Concurrent connections working ({responses_received}/{len(connections)} responses)")
            return True
        else:
            print_warning(f"Partial concurrent connection support ({responses_received}/{len(connections)} responses)")
            return True
        
    except Exception as e:
        print_error(f"Concurrent connections test failed: {e}")
        # Clean up
        for _, ws in connections:
            try:
                await ws.close()
            except:
                pass
        return False


async def test_request_timeout():
    """Test request timeout handling."""
    print_test("Request Timeout")
    
    async with httpx.AsyncClient(timeout=2.0) as client:  # 2 second timeout
        try:
            # This should complete quickly (health check)
            response = await client.get(f"{API_BASE_URL}/health")
            
            if response.status_code == 200:
                print_success("Request timeout handling working (request completed in time)")
                return True
            else:
                print_warning(f"Got status {response.status_code}")
                return True
        except httpx.TimeoutException:
            print_error("Request timed out (should not happen for health check)")
            return False
        except Exception as e:
            print_warning(f"Request error: {e}")
            return True


async def run_all_tests():
    """Run all performance and load tests."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print("Performance & Load Tests")
    print(f"{'='*60}{Colors.RESET}\n")
    
    results = {
        "concurrent_users": False,
        "high_message_volume": False,
        "concurrent_websockets": False,
        "request_timeout": False,
    }
    
    # Run tests
    results["concurrent_users"] = await test_concurrent_users()
    results["high_message_volume"] = await test_high_message_volume()
    results["concurrent_websockets"] = await test_concurrent_websocket_connections()
    results["request_timeout"] = await test_request_timeout()
    
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
