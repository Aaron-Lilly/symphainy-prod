#!/usr/bin/env python3
"""
Test Script: Two-Phase Materialization Flow

Tests the new boundary contract architecture:
1. Upload → Creates boundary contract (pending materialization)
2. Save → Authorizes materialization (active) with workspace scope
3. List → Filters by workspace scope
"""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from utilities import get_logger

logger = get_logger("test_materialization")

# Test configuration
TEST_CONFIG = {
    "base_url": "http://localhost:8000",
    "tenant_id": "test_tenant",
    "user_id": "test_user",
    "session_id": "test_session_123"
}

async def test_upload_file():
    """Test Phase 1: Upload file (creates pending boundary contract)"""
    import aiohttp
    
    logger.info("=" * 60)
    logger.info("TEST 1: Upload File (Phase 1 - Pending Materialization)")
    logger.info("=" * 60)
    
    # Simple test file content ("Hello World" in hex)
    file_content_hex = "48656c6c6f20576f726c64"
    
    request_data = {
        "tenant_id": TEST_CONFIG["tenant_id"],
        "intent_type": "ingest_file",
        "parameters": {
            "ingestion_type": "upload",
            "file_content": file_content_hex,
            "ui_name": "test_file.txt",
            "file_type": "unstructured",
            "mime_type": "text/plain"
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "x-user-id": TEST_CONFIG["user_id"],
        "x-session-id": TEST_CONFIG["session_id"]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{TEST_CONFIG['base_url']}/api/intent/submit",
            json=request_data,
            headers=headers
        ) as response:
            result = await response.json()
            
            logger.info(f"Status: {response.status}")
            logger.info(f"Response: {json.dumps(result, indent=2)}")
            
            if response.status == 200:
                # Extract boundary_contract_id and file_id from response
                execution_id = result.get("execution_id")
                logger.info(f"✅ Upload successful! Execution ID: {execution_id}")
                
                # Get execution status to find artifacts
                await asyncio.sleep(1)  # Wait for execution to complete
                
                async with session.get(
                    f"{TEST_CONFIG['base_url']}/api/execution/{execution_id}/status",
                    params={"tenant_id": TEST_CONFIG["tenant_id"]}
                ) as status_response:
                    status_result = await status_response.json()
                    logger.info(f"Execution Status: {json.dumps(status_result, indent=2)}")
                    
                    # Extract boundary_contract_id and file_id from artifacts
                    artifacts = status_result.get("artifacts", {})
                    file_artifact = artifacts.get("file", {})
                    semantic_payload = file_artifact.get("semantic_payload", {})
                    
                    boundary_contract_id = semantic_payload.get("boundary_contract_id")
                    file_id = semantic_payload.get("file_id")
                    materialization_pending = semantic_payload.get("materialization_pending", False)
                    
                    logger.info(f"📋 Boundary Contract ID: {boundary_contract_id}")
                    logger.info(f"📋 File ID: {file_id}")
                    logger.info(f"📋 Materialization Pending: {materialization_pending}")
                    
                    if boundary_contract_id and file_id:
                        TEST_CONFIG["boundary_contract_id"] = boundary_contract_id
                        TEST_CONFIG["file_id"] = file_id
                        logger.info("✅ Test 1 PASSED - Boundary contract created (pending)")
                        return True
                    else:
                        logger.error("❌ Test 1 FAILED - Missing boundary_contract_id or file_id")
                        return False
            else:
                logger.error(f"❌ Test 1 FAILED - Status: {response.status}")
                return False

async def test_save_materialization():
    """Test Phase 2: Save materialization (authorizes with workspace scope)"""
    import aiohttp
    
    logger.info("=" * 60)
    logger.info("TEST 2: Save Materialization (Phase 2 - Authorize Materialization)")
    logger.info("=" * 60)
    
    if not TEST_CONFIG.get("boundary_contract_id") or not TEST_CONFIG.get("file_id"):
        logger.error("❌ Test 2 SKIPPED - Missing boundary_contract_id or file_id from Test 1")
        return False
    
    request_data = {
        "boundary_contract_id": TEST_CONFIG["boundary_contract_id"],
        "file_id": TEST_CONFIG["file_id"],
        "tenant_id": TEST_CONFIG["tenant_id"]
    }
    
    headers = {
        "Content-Type": "application/json",
        "x-user-id": TEST_CONFIG["user_id"],
        "x-session-id": TEST_CONFIG["session_id"]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{TEST_CONFIG['base_url']}/api/content/save_materialization",
            json=request_data,
            headers=headers
        ) as response:
            result = await response.json()
            
            logger.info(f"Status: {response.status}")
            logger.info(f"Response: {json.dumps(result, indent=2)}")
            
            if response.status == 200 and result.get("success"):
                logger.info("✅ Test 2 PASSED - Materialization saved")
                return True
            else:
                logger.error(f"❌ Test 2 FAILED - Status: {response.status}, Result: {result}")
                return False

async def test_list_files():
    """Test Phase 3: List files (filtered by workspace scope)"""
    import aiohttp
    
    logger.info("=" * 60)
    logger.info("TEST 3: List Files (Workspace Scope Filtering)")
    logger.info("=" * 60)
    
    request_data = {
        "tenant_id": TEST_CONFIG["tenant_id"],
        "session_id": TEST_CONFIG["session_id"],
        "solution_id": "default",
        "intent_type": "list_files",
        "parameters": {}
    }
    
    headers = {
        "Content-Type": "application/json",
        "x-user-id": TEST_CONFIG["user_id"],
        "x-session-id": TEST_CONFIG["session_id"]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{TEST_CONFIG['base_url']}/api/intent/submit",
            json=request_data,
            headers=headers
        ) as response:
            result = await response.json()
            
            logger.info(f"Status: {response.status}")
            
            execution_id = result.get("execution_id")
            if execution_id:
                await asyncio.sleep(1)  # Wait for execution
                
                async with session.get(
                    f"{TEST_CONFIG['base_url']}/api/execution/{execution_id}/status",
                    params={"tenant_id": TEST_CONFIG["tenant_id"]}
                ) as status_response:
                    status_result = await status_response.json()
                    
                    artifacts = status_result.get("artifacts", {})
                    file_list_artifact = artifacts.get("file_list", {})
                    semantic_payload = file_list_artifact.get("semantic_payload", {})
                    files = semantic_payload.get("files", [])
                    
                    logger.info(f"Found {len(files)} file(s)")
                    
                    # Check if our saved file is in the list
                    file_ids = [f.get("file_id") for f in files]
                    if TEST_CONFIG.get("file_id") in file_ids:
                        logger.info(f"✅ Test 3 PASSED - Saved file appears in list")
                        logger.info(f"   File IDs in list: {file_ids}")
                        return True
                    else:
                        logger.warning(f"⚠️ Test 3 PARTIAL - File list returned but saved file not found")
                        logger.info(f"   Expected file_id: {TEST_CONFIG.get('file_id')}")
                        logger.info(f"   File IDs in list: {file_ids}")
                        return False
            else:
                logger.error(f"❌ Test 3 FAILED - No execution_id in response")
                return False

async def verify_database_state():
    """Verify database state after tests"""
    logger.info("=" * 60)
    logger.info("DATABASE VERIFICATION")
    logger.info("=" * 60)
    logger.info("Run these SQL queries in Supabase to verify:")
    logger.info("")
    logger.info("-- Check boundary contract:")
    logger.info(f"SELECT contract_id, contract_status, materialization_allowed,")
    logger.info(f"       materialization_scope, reference_scope")
    logger.info(f"FROM data_boundary_contracts")
    logger.info(f"WHERE contract_id = '{TEST_CONFIG.get('boundary_contract_id', 'YOUR_CONTRACT_ID')}';")
    logger.info("")
    logger.info("-- Check materialization index:")
    logger.info(f"SELECT uuid, ui_name, boundary_contract_id, representation_type,")
    logger.info(f"       materialization_scope")
    logger.info(f"FROM project_files")
    logger.info(f"WHERE uuid = '{TEST_CONFIG.get('file_id', 'YOUR_FILE_ID')}';")
    logger.info("")

async def main():
    """Run all tests"""
    logger.info("🚀 Starting Two-Phase Materialization Flow Tests")
    logger.info("")
    
    results = {}
    
    # Test 1: Upload
    try:
        results["upload"] = await test_upload_file()
    except Exception as e:
        logger.error(f"❌ Test 1 FAILED with exception: {e}", exc_info=True)
        results["upload"] = False
    
    if not results["upload"]:
        logger.error("❌ Cannot continue - Upload test failed")
        return
    
    logger.info("")
    
    # Test 2: Save
    try:
        results["save"] = await test_save_materialization()
    except Exception as e:
        logger.error(f"❌ Test 2 FAILED with exception: {e}", exc_info=True)
        results["save"] = False
    
    logger.info("")
    
    # Test 3: List
    try:
        results["list"] = await test_list_files()
    except Exception as e:
        logger.error(f"❌ Test 3 FAILED with exception: {e}", exc_info=True)
        results["list"] = False
    
    logger.info("")
    
    # Summary
    logger.info("=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Upload (Phase 1): {'✅ PASSED' if results.get('upload') else '❌ FAILED'}")
    logger.info(f"Save (Phase 2):   {'✅ PASSED' if results.get('save') else '❌ FAILED'}")
    logger.info(f"List (Phase 3):   {'✅ PASSED' if results.get('list') else '❌ FAILED'}")
    logger.info("")
    
    if all(results.values()):
        logger.info("🎉 ALL TESTS PASSED!")
    else:
        logger.warning("⚠️ Some tests failed - check logs above")
    
    logger.info("")
    await verify_database_state()

if __name__ == "__main__":
    asyncio.run(main())
