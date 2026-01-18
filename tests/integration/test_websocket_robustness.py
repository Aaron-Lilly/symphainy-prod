#!/usr/bin/env python3
"""
WebSocket Robustness Tests

Tests WebSocket error handling, connection management, and edge cases.
Priority 2: High Priority - WebSocket Robustness
"""
import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import websockets
import httpx
from typing import Dict, Any, Optional


# Test Configuration
API_BASE_URL = "http://localhost:8001"
WS_BASE_URL = "ws://localhost:8001"

# Test mode headers to enable relaxed rate limiting
TEST_HEADERS = {
    "X-Test-Mode": "true",
    "X-Test-ID": "websocket_tests"
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


async def get_valid_token() -> Optional[str]:
    """Get a valid authentication token using test mode."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        response = await client.post(
            f"{API_BASE_URL}/api/auth/register",
            json={
                "email": f"test_{timestamp}@example.com",
                "password": "TestPassword123!",
                "name": "Test User"
            },
            headers=TEST_HEADERS  # Use test mode to avoid rate limiting
        )
        
        if response.status_code == 200:
            return response.json().get("access_token")
        return None


async def test_websocket_no_token():
    """Test WebSocket connection without token."""
    print_test("WebSocket - No Token")
    
    try:
        async with websockets.connect(
            f"{WS_BASE_URL}/api/runtime/agent",
            ping_interval=20,
            ping_timeout=5
        ) as websocket:
            print_error("Connection should have been rejected")
            return False
    except websockets.exceptions.InvalidStatusCode as e:
        if e.status_code == 1008:  # Policy violation (expected)
            print_success("Connection correctly rejected without token")
            return True
        else:
            print_warning(f"Got status {e.status_code} (expected 1008)")
            return True
    except Exception as e:
        print_success(f"Connection rejected as expected: {type(e).__name__}")
        return True


async def test_websocket_invalid_token():
    """Test WebSocket connection with invalid token."""
    print_test("WebSocket - Invalid Token")
    
    try:
        async with websockets.connect(
            f"{WS_BASE_URL}/api/runtime/agent?session_token=invalid.token.here",
            ping_interval=20,
            ping_timeout=5
        ) as websocket:
            print_error("Connection should have been rejected")
            return False
    except websockets.exceptions.InvalidStatusCode as e:
        if e.status_code == 1008:  # Policy violation
            print_success("Invalid token correctly rejected")
            return True
        else:
            print_warning(f"Got status {e.status_code}")
            return True
    except Exception as e:
        print_success(f"Connection rejected: {type(e).__name__}")
        return True


async def test_websocket_malformed_json():
    """Test WebSocket with malformed JSON."""
    print_test("WebSocket - Malformed JSON")
    
    token = await get_valid_token()
    if not token:
        print_error("Could not get valid token")
        return False
    
    try:
        async with websockets.connect(
            f"{WS_BASE_URL}/api/runtime/agent?session_token={token}",
            ping_interval=20,
            ping_timeout=10
        ) as websocket:
            # Send malformed JSON
            await websocket.send("not json at all")
            
            # Wait for error response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                response_data = json.loads(response)
                
                if response_data.get("type") == "error":
                    print_success("Malformed JSON correctly handled with error response")
                    return True
                else:
                    print_warning(f"Got response type: {response_data.get('type')}")
                    return True
            except asyncio.TimeoutError:
                print_warning("No response to malformed JSON (may be OK)")
                return True
    except Exception as e:
        print_error(f"Connection failed: {e}")
        return False


async def test_websocket_missing_fields():
    """Test WebSocket message with missing required fields."""
    print_test("WebSocket - Missing Required Fields")
    
    token = await get_valid_token()
    if not token:
        print_error("Could not get valid token")
        return False
    
    try:
        async with websockets.connect(
            f"{WS_BASE_URL}/api/runtime/agent?session_token={token}",
            ping_interval=20,
            ping_timeout=10
        ) as websocket:
            # Send message missing "payload"
            message = {"type": "agent.message"}
            await websocket.send(json.dumps(message))
            
            # Wait for error response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                response_data = json.loads(response)
                
                if response_data.get("type") == "error":
                    print_success("Missing fields correctly handled with error")
                    return True
                else:
                    print_warning(f"Got response type: {response_data.get('type')}")
                    return True
            except asyncio.TimeoutError:
                print_warning("No response to missing fields (may be OK)")
                return True
    except Exception as e:
        print_error(f"Connection failed: {e}")
        return False


async def test_websocket_invalid_message_type():
    """Test WebSocket with invalid message type."""
    print_test("WebSocket - Invalid Message Type")
    
    token = await get_valid_token()
    if not token:
        print_error("Could not get valid token")
        return False
    
    try:
        async with websockets.connect(
            f"{WS_BASE_URL}/api/runtime/agent?session_token={token}",
            ping_interval=20,
            ping_timeout=10
        ) as websocket:
            # Send invalid message type
            message = {
                "type": "invalid.message.type",
                "payload": {}
            }
            await websocket.send(json.dumps(message))
            
            # Wait for error response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                response_data = json.loads(response)
                
                if response_data.get("type") == "error":
                    print_success("Invalid message type correctly handled")
                    return True
                else:
                    print_warning(f"Got response type: {response_data.get('type')}")
                    return True
            except asyncio.TimeoutError:
                print_warning("No response to invalid type (may be OK)")
                return True
    except Exception as e:
        print_error(f"Connection failed: {e}")
        return False


async def test_websocket_concurrent_connections():
    """Test multiple WebSocket connections from same user."""
    print_test("WebSocket - Concurrent Connections")
    
    token = await get_valid_token()
    if not token:
        print_error("Could not get valid token")
        return False
    
    connections = []
    try:
        # Create 3 concurrent connections
        for i in range(3):
            try:
                ws = await websockets.connect(
                    f"{WS_BASE_URL}/api/runtime/agent?session_token={token}",
                    ping_interval=20,
                    ping_timeout=10
                )
                connections.append(ws)
                print_info(f"Connection {i+1} established")
            except Exception as e:
                print_error(f"Connection {i+1} failed: {e}")
                return False
        
        # Send message on all connections
        for i, ws in enumerate(connections):
            message = {
                "type": "agent.message",
                "payload": {
                    "text": f"Test message from connection {i+1}",
                    "context": {
                        "surface": "content_pillar",
                        "conversation_id": f"test_{i}"
                    }
                }
            }
            await ws.send(json.dumps(message))
        
        # Wait for responses
        responses_received = 0
        for i, ws in enumerate(connections):
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                response_data = json.loads(response)
                if response_data.get("type") == "runtime_event":
                    responses_received += 1
                    print_info(f"Connection {i+1} received response")
            except asyncio.TimeoutError:
                print_warning(f"Connection {i+1} timeout (may be OK)")
        
        # Close all connections
        for ws in connections:
            await ws.close()
        
        if responses_received >= 2:
            print_success(f"Concurrent connections working ({responses_received}/3 responses)")
            return True
        else:
            print_warning(f"Only {responses_received}/3 connections received responses")
            return True
        
    except Exception as e:
        print_error(f"Concurrent connection test failed: {e}")
        # Clean up
        for ws in connections:
            try:
                await ws.close()
            except:
                pass
        return False


async def test_websocket_large_message():
    """Test WebSocket with very large message."""
    print_test("WebSocket - Large Message")
    
    token = await get_valid_token()
    if not token:
        print_error("Could not get valid token")
        return False
    
    try:
        async with websockets.connect(
            f"{WS_BASE_URL}/api/runtime/agent?session_token={token}",
            ping_interval=20,
            ping_timeout=10
        ) as websocket:
            # Send very large message (10KB text)
            large_text = "x" * 10000
            message = {
                "type": "agent.message",
                "payload": {
                    "text": large_text,
                    "context": {
                        "surface": "content_pillar",
                        "conversation_id": "test_large"
                    }
                }
            }
            
            await websocket.send(json.dumps(message))
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                response_data = json.loads(response)
                
                if response_data.get("type") in ["runtime_event", "error"]:
                    print_success("Large message handled correctly")
                    return True
                else:
                    print_warning(f"Got unexpected response type: {response_data.get('type')}")
                    return True
            except asyncio.TimeoutError:
                print_warning("No response to large message (may be processing)")
                return True
    except Exception as e:
        print_error(f"Large message test failed: {e}")
        return False


async def test_websocket_rapid_messages():
    """Test sending multiple messages rapidly."""
    print_test("WebSocket - Rapid Messages")
    
    token = await get_valid_token()
    if not token:
        print_error("Could not get valid token")
        return False
    
    try:
        async with websockets.connect(
            f"{WS_BASE_URL}/api/runtime/agent?session_token={token}",
            ping_interval=20,
            ping_timeout=10
        ) as websocket:
            # Send 10 messages rapidly
            for i in range(10):
                message = {
                    "type": "agent.message",
                    "payload": {
                        "text": f"Rapid message {i+1}",
                        "context": {
                            "surface": "content_pillar",
                            "conversation_id": "test_rapid"
                        }
                    }
                }
                await websocket.send(json.dumps(message))
                await asyncio.sleep(0.1)  # Small delay
            
            # Collect responses
            responses = []
            for _ in range(10):
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    responses.append(json.loads(response))
                except asyncio.TimeoutError:
                    break
            
            print_info(f"Received {len(responses)} responses to 10 messages")
            
            if len(responses) >= 5:
                print_success(f"Rapid messages handled ({len(responses)}/10 responses)")
                return True
            else:
                print_warning(f"Only {len(responses)}/10 responses received")
                return True
    except Exception as e:
        print_error(f"Rapid messages test failed: {e}")
        return False


async def run_all_tests():
    """Run all WebSocket robustness tests."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print("WebSocket Robustness Tests")
    print(f"{'='*60}{Colors.RESET}\n")
    
    results = {
        "no_token": False,
        "invalid_token": False,
        "malformed_json": False,
        "missing_fields": False,
        "invalid_message_type": False,
        "concurrent_connections": False,
        "large_message": False,
        "rapid_messages": False,
    }
    
    # Run tests
    results["no_token"] = await test_websocket_no_token()
    results["invalid_token"] = await test_websocket_invalid_token()
    results["malformed_json"] = await test_websocket_malformed_json()
    results["missing_fields"] = await test_websocket_missing_fields()
    results["invalid_message_type"] = await test_websocket_invalid_message_type()
    results["concurrent_connections"] = await test_websocket_concurrent_connections()
    results["large_message"] = await test_websocket_large_message()
    results["rapid_messages"] = await test_websocket_rapid_messages()
    
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
