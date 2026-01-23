#!/usr/bin/env python3
"""
Inline Test Script for Session-First Architecture Implementation

Tests:
1. Anonymous session creation
2. Session upgrade
3. Session retrieval (anonymous and authenticated)
4. End-to-end flow
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional
from utilities import get_logger

# Import SDKs and clients
from symphainy_platform.civic_systems.smart_city.sdk.traffic_cop_sdk import TrafficCopSDK, SessionIntent
from symphainy_platform.civic_systems.smart_city.sdk.security_guard_sdk import SecurityGuardSDK
from symphainy_platform.runtime.runtime_api import RuntimeAPI, SessionCreateRequest, SessionCreateResponse
from symphainy_platform.runtime.state_surface import StateSurface
from symphainy_platform.civic_systems.experience.sdk.runtime_client import RuntimeClient

# Mock dependencies for testing
class MockStateAbstraction:
    """Mock state abstraction for testing"""
    def __init__(self):
        self._store: Dict[str, Any] = {}
    
    async def retrieve_state(self, state_id: str) -> Optional[Dict[str, Any]]:
        return self._store.get(state_id)
    
    async def store_state(self, state_id: str, state_data: Dict[str, Any]) -> bool:
        self._store[state_id] = state_data
        return True

class MockExecutionLifecycleManager:
    """Mock execution lifecycle manager for testing"""
    pass

logger = get_logger("SessionFirstTest")


async def test_anonymous_session_intent():
    """Test 1: Anonymous session intent creation"""
    print("\n" + "="*60)
    print("TEST 1: Anonymous Session Intent Creation")
    print("="*60)
    
    try:
        mock_state = MockStateAbstraction()
        traffic_cop = TrafficCopSDK(state_abstraction=mock_state)
        
        # Create anonymous session intent
        session_intent = await traffic_cop.create_anonymous_session_intent(
            metadata={"test": "anonymous_session"}
        )
        
        # Verify structure
        assert session_intent.session_id is not None, "Session ID should be generated"
        assert session_intent.tenant_id is None, "Tenant ID should be None for anonymous"
        assert session_intent.user_id is None, "User ID should be None for anonymous"
        assert session_intent.execution_contract is not None, "Execution contract should exist"
        assert session_intent.execution_contract.get("session_type") == "anonymous", "Should be anonymous session"
        
        print(f"✅ Session Intent Created:")
        print(f"   Session ID: {session_intent.session_id}")
        print(f"   Tenant ID: {session_intent.tenant_id}")
        print(f"   User ID: {session_intent.user_id}")
        print(f"   Session Type: {session_intent.execution_contract.get('session_type')}")
        
        return session_intent
        
    except Exception as e:
        print(f"❌ TEST 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_authenticated_session_intent():
    """Test 2: Authenticated session intent creation (for comparison)"""
    print("\n" + "="*60)
    print("TEST 2: Authenticated Session Intent Creation")
    print("="*60)
    
    try:
        mock_state = MockStateAbstraction()
        traffic_cop = TrafficCopSDK(state_abstraction=mock_state)
        
        # Create authenticated session intent
        session_intent = await traffic_cop.create_session_intent(
            tenant_id="test_tenant_123",
            user_id="test_user_456",
            metadata={"test": "authenticated_session"}
        )
        
        # Verify structure
        assert session_intent.session_id is not None, "Session ID should be generated"
        assert session_intent.tenant_id == "test_tenant_123", "Tenant ID should match"
        assert session_intent.user_id == "test_user_456", "User ID should match"
        assert session_intent.execution_contract is not None, "Execution contract should exist"
        
        print(f"✅ Authenticated Session Intent Created:")
        print(f"   Session ID: {session_intent.session_id}")
        print(f"   Tenant ID: {session_intent.tenant_id}")
        print(f"   User ID: {session_intent.user_id}")
        
        return session_intent
        
    except Exception as e:
        print(f"❌ TEST 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_runtime_anonymous_session_creation():
    """Test 3: Runtime creates anonymous session"""
    print("\n" + "="*60)
    print("TEST 3: Runtime Anonymous Session Creation")
    print("="*60)
    
    try:
        mock_state = MockStateAbstraction()
        state_surface = StateSurface(state_abstraction=mock_state, use_memory=True)
        execution_manager = MockExecutionLifecycleManager()
        runtime_api = RuntimeAPI(execution_manager, state_surface)
        
        # Create anonymous session request (use Traffic Cop SDK to get proper execution contract)
        traffic_cop = TrafficCopSDK(state_abstraction=mock_state)
        anonymous_intent = await traffic_cop.create_anonymous_session_intent(
            metadata={"test": "anonymous"}
        )
        
        request = SessionCreateRequest(
            intent_type="create_session",
            tenant_id=None,  # Anonymous
            user_id=None,   # Anonymous
            session_id=anonymous_intent.session_id,
            execution_contract=anonymous_intent.execution_contract
        )
        
        # Create session
        response = await runtime_api.create_session(request)
        
        # Verify response
        assert response.session_id is not None, "Session ID should be generated"
        assert response.tenant_id is None, "Tenant ID should be None for anonymous"
        assert response.user_id is None, "User ID should be None for anonymous"
        assert response.created_at is not None, "Created at should be set"
        
        # Verify session stored in state surface
        session_state = await state_surface.get_session_state(response.session_id, None)
        assert session_state is not None, "Session should be stored"
        assert session_state.get("is_anonymous") == True, "Should be marked as anonymous"
        
        print(f"✅ Anonymous Session Created:")
        print(f"   Session ID: {response.session_id}")
        print(f"   Tenant ID: {response.tenant_id}")
        print(f"   User ID: {response.user_id}")
        print(f"   Created At: {response.created_at}")
        print(f"   Is Anonymous: {session_state.get('is_anonymous')}")
        
        return response
        
    except Exception as e:
        print(f"❌ TEST 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_runtime_session_upgrade():
    """Test 4: Runtime upgrades anonymous session"""
    print("\n" + "="*60)
    print("TEST 4: Runtime Session Upgrade")
    print("="*60)
    
    try:
        mock_state = MockStateAbstraction()
        state_surface = StateSurface(state_abstraction=mock_state, use_memory=True)
        execution_manager = MockExecutionLifecycleManager()
        runtime_api = RuntimeAPI(execution_manager, state_surface)
        
        # First, create anonymous session (use Traffic Cop SDK)
        traffic_cop = TrafficCopSDK(state_abstraction=mock_state)
        anonymous_intent = await traffic_cop.create_anonymous_session_intent()
        
        anonymous_request = SessionCreateRequest(
            intent_type="create_session",
            tenant_id=None,
            user_id=None,
            session_id=anonymous_intent.session_id,
            execution_contract=anonymous_intent.execution_contract
        )
        anonymous_response = await runtime_api.create_session(anonymous_request)
        session_id = anonymous_response.session_id
        
        print(f"   Created anonymous session: {session_id}")
        
        # Now upgrade it
        upgraded = await runtime_api.upgrade_session(
            session_id=session_id,
            user_id="test_user_789",
            tenant_id="test_tenant_789",
            metadata={"upgraded_at": "2026-01-23T00:00:00Z"}
        )
        
        # Verify upgrade
        assert upgraded.get("user_id") == "test_user_789", "User ID should be set"
        assert upgraded.get("tenant_id") == "test_tenant_789", "Tenant ID should be set"
        assert upgraded.get("is_anonymous") == False, "Should no longer be anonymous"
        assert upgraded.get("upgraded_at") is not None, "Upgraded at should be set"
        
        # Verify session in state surface (with tenant_id now)
        session_state = await state_surface.get_session_state(session_id, "test_tenant_789")
        assert session_state is not None, "Session should exist"
        assert session_state.get("user_id") == "test_user_789", "User ID should match"
        
        print(f"✅ Session Upgraded:")
        print(f"   Session ID: {session_id}")
        print(f"   Tenant ID: {upgraded.get('tenant_id')}")
        print(f"   User ID: {upgraded.get('user_id')}")
        print(f"   Is Anonymous: {upgraded.get('is_anonymous')}")
        print(f"   Upgraded At: {upgraded.get('upgraded_at')}")
        
        return upgraded
        
    except Exception as e:
        print(f"❌ TEST 4 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_session_retrieval():
    """Test 5: Session retrieval (anonymous and authenticated)"""
    print("\n" + "="*60)
    print("TEST 5: Session Retrieval")
    print("="*60)
    
    try:
        mock_state = MockStateAbstraction()
        state_surface = StateSurface(state_abstraction=mock_state, use_memory=True)
        execution_manager = MockExecutionLifecycleManager()
        runtime_api = RuntimeAPI(execution_manager, state_surface)
        
        # Create anonymous session (use Traffic Cop SDK)
        traffic_cop = TrafficCopSDK(state_abstraction=mock_state)
        anonymous_intent = await traffic_cop.create_anonymous_session_intent()
        
        anonymous_request = SessionCreateRequest(
            intent_type="create_session",
            tenant_id=None,
            user_id=None,
            session_id=anonymous_intent.session_id,
            execution_contract=anonymous_intent.execution_contract
        )
        anonymous_response = await runtime_api.create_session(anonymous_request)
        anonymous_session_id = anonymous_response.session_id
        
        # Retrieve anonymous session (without tenant_id)
        anonymous_session = await state_surface.get_session_state(anonymous_session_id, None)
        assert anonymous_session is not None, "Should retrieve anonymous session"
        assert anonymous_session.get("is_anonymous") == True, "Should be anonymous"
        
        print(f"✅ Anonymous Session Retrieved:")
        print(f"   Session ID: {anonymous_session_id}")
        print(f"   Is Anonymous: {anonymous_session.get('is_anonymous')}")
        
        # Upgrade session
        await runtime_api.upgrade_session(
            session_id=anonymous_session_id,
            user_id="test_user_retrieve",
            tenant_id="test_tenant_retrieve"
        )
        
        # Retrieve authenticated session (with tenant_id)
        authenticated_session = await state_surface.get_session_state(
            anonymous_session_id, 
            "test_tenant_retrieve"
        )
        assert authenticated_session is not None, "Should retrieve authenticated session"
        assert authenticated_session.get("is_anonymous") == False, "Should not be anonymous"
        assert authenticated_session.get("user_id") == "test_user_retrieve", "User ID should match"
        
        print(f"✅ Authenticated Session Retrieved:")
        print(f"   Session ID: {anonymous_session_id}")
        print(f"   Tenant ID: {authenticated_session.get('tenant_id')}")
        print(f"   User ID: {authenticated_session.get('user_id')}")
        print(f"   Is Anonymous: {authenticated_session.get('is_anonymous')}")
        
        return True
        
    except Exception as e:
        print(f"❌ TEST 5 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_end_to_end_flow():
    """Test 6: End-to-end flow (anonymous → upgrade → retrieve)"""
    print("\n" + "="*60)
    print("TEST 6: End-to-End Flow")
    print("="*60)
    
    try:
        mock_state = MockStateAbstraction()
        state_surface = StateSurface(state_abstraction=mock_state, use_memory=True)
        execution_manager = MockExecutionLifecycleManager()
        runtime_api = RuntimeAPI(execution_manager, state_surface)
        traffic_cop = TrafficCopSDK(state_abstraction=mock_state)
        
        # Step 1: Create anonymous session intent
        print("\n   Step 1: Create anonymous session intent...")
        anonymous_intent = await traffic_cop.create_anonymous_session_intent()
        assert anonymous_intent.tenant_id is None, "Should be anonymous"
        print(f"   ✅ Anonymous intent created: {anonymous_intent.session_id}")
        
        # Step 2: Create anonymous session in Runtime
        print("\n   Step 2: Create anonymous session in Runtime...")
        anonymous_request = SessionCreateRequest(
            intent_type="create_session",
            tenant_id=None,
            user_id=None,
            session_id=anonymous_intent.session_id,
            execution_contract=anonymous_intent.execution_contract
        )
        anonymous_response = await runtime_api.create_session(anonymous_request)
        session_id = anonymous_response.session_id
        print(f"   ✅ Anonymous session created: {session_id}")
        
        # Step 3: Verify anonymous session exists
        print("\n   Step 3: Verify anonymous session exists...")
        anonymous_session = await state_surface.get_session_state(session_id, None)
        assert anonymous_session is not None, "Session should exist"
        assert anonymous_session.get("is_anonymous") == True, "Should be anonymous"
        print(f"   ✅ Anonymous session verified")
        
        # Step 4: Upgrade session with authentication
        print("\n   Step 4: Upgrade session with authentication...")
        upgraded = await runtime_api.upgrade_session(
            session_id=session_id,
            user_id="e2e_user_123",
            tenant_id="e2e_tenant_123",
            metadata={"authenticated_at": "2026-01-23T00:00:00Z"}
        )
        assert upgraded.get("user_id") == "e2e_user_123", "User ID should match"
        assert upgraded.get("tenant_id") == "e2e_tenant_123", "Tenant ID should match"
        print(f"   ✅ Session upgraded")
        
        # Step 5: Verify upgraded session
        print("\n   Step 5: Verify upgraded session...")
        upgraded_session = await state_surface.get_session_state(session_id, "e2e_tenant_123")
        assert upgraded_session is not None, "Session should exist"
        assert upgraded_session.get("is_anonymous") == False, "Should not be anonymous"
        assert upgraded_session.get("user_id") == "e2e_user_123", "User ID should match"
        print(f"   ✅ Upgraded session verified")
        
        # Step 6: Verify session_id is the same (continuity)
        print("\n   Step 6: Verify session continuity...")
        assert upgraded_session.get("session_id") == session_id, "Session ID should be the same"
        print(f"   ✅ Session ID unchanged: {session_id}")
        
        print("\n✅ END-TO-END FLOW SUCCESSFUL")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 6 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("SESSION-FIRST ARCHITECTURE - INLINE TESTS")
    print("="*60)
    
    results = []
    
    # Test 1: Anonymous session intent
    result1 = await test_anonymous_session_intent()
    results.append(("Anonymous Session Intent", result1 is not None))
    
    # Test 2: Authenticated session intent (for comparison)
    result2 = await test_authenticated_session_intent()
    results.append(("Authenticated Session Intent", result2 is not None))
    
    # Test 3: Runtime anonymous session creation
    result3 = await test_runtime_anonymous_session_creation()
    results.append(("Runtime Anonymous Session Creation", result3 is not None))
    
    # Test 4: Runtime session upgrade
    result4 = await test_runtime_session_upgrade()
    results.append(("Runtime Session Upgrade", result4 is not None))
    
    # Test 5: Session retrieval
    result5 = await test_session_retrieval()
    results.append(("Session Retrieval", result5))
    
    # Test 6: End-to-end flow
    result6 = await test_end_to_end_flow()
    results.append(("End-to-End Flow", result6))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - Ready for browser testing!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - Review before browser testing")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
