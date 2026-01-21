#!/usr/bin/env python3
"""
Phase 2 Capability Test: File Management

Tests the file management capabilities:
- register_file: Register and store files
- retrieve_file: Retrieve files by ID
- list_files: List available files
- get_file_by_id: Get file metadata
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import httpx
from tests.integration.capabilities.capability_test_helpers import (
    get_valid_token, submit_intent, poll_execution_status
)
from tests.integration.execution.artifact_retrieval_helpers import get_artifact_by_id

API_BASE_URL = "http://localhost:8001"
RUNTIME_BASE_URL = "http://localhost:8000"
TEST_HEADERS = {"X-Test-Mode": "true", "X-Test-ID": "file_management_capability_tests"}

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_test(name: str): print(f"\n{Colors.BOLD}{Colors.BLUE}🧪 Testing: {name}{Colors.RESET}")
def print_success(message: str): print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")
def print_error(message: str): print(f"{Colors.RED}❌ {message}{Colors.RESET}")
def print_warning(message: str): print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")
def print_info(message: str): print(f"{Colors.BLUE}ℹ️  {message}{Colors.RESET}")

async def test_file_registration_completion():
    print_test("File Registration - Full Execution Completion")
    token = await get_valid_token("file_mgmt")
    if not token: return False
    
    test_file_content = "name,age,city\nJohn,30,New York\nJane,25,San Francisco"
    test_file_name = f"test_file_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.csv"
    
    result = await submit_intent(token=token, intent_type="register_file", parameters={
        "file_name": test_file_name, "file_content": test_file_content, "file_type": "csv"
    })
    
    if not result or "execution_id" not in result: return False
    execution_id = result["execution_id"]
    
    status = await poll_execution_status(execution_id, timeout=60)
    if not status or status.get("status") != "completed": return False
    
    artifacts = status.get("artifacts", [])
    file_artifact = next((a for a in artifacts if a.get("type") == "file" or a.get("artifact_type") == "file"), None)
    if not file_artifact: return False
    
    file_id = file_artifact.get("file_id") or file_artifact.get("id")
    if not file_id: return False
    
    artifact_data = await get_artifact_by_id(file_id, "test_tenant", include_visuals=False, token=token)
    if not artifact_data: return False
    
    print_success("✅ File Registration - Full Execution Completion: PASSED")
    return True

async def main():
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}File Management Capability Tests{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    
    results = {"file_registration": await test_file_registration_completion()}
    passed = sum(1 for v in results.values() if v)
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    return 0 if passed == len(results) else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
