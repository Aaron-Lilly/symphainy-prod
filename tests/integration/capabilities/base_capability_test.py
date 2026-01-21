#!/usr/bin/env python3
"""
Base Capability Test Class

Provides common functionality for all capability tests.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from tests.integration.capabilities.capability_test_helpers import (
    get_valid_token, submit_intent, poll_execution_status
)
from tests.integration.execution.artifact_retrieval_helpers import (
    get_artifact_by_id, get_visual_by_path
)

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class BaseCapabilityTest(ABC):
    def __init__(self, test_name: str, test_id_prefix: str = "test"):
        self.test_name = test_name
        self.test_id_prefix = test_id_prefix
        self.token: Optional[str] = None
    
    def print_test(self, name: str):
        print(f"\n{Colors.BOLD}{Colors.BLUE}🧪 Testing: {name}{Colors.RESET}")
    
    def print_success(self, message: str):
        print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")
    
    def print_error(self, message: str):
        print(f"{Colors.RED}❌ {message}{Colors.RESET}")
    
    def print_warning(self, message: str):
        print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")
    
    def print_info(self, message: str):
        print(f"{Colors.BLUE}ℹ️  {message}{Colors.RESET}")
    
    async def authenticate(self) -> bool:
        self.print_info("Step 1: Authenticating")
        self.token = await get_valid_token(self.test_id_prefix)
        if not self.token:
            self.print_error("Failed to get authentication token")
            return False
        return True
    
    async def submit_intent_and_poll(self, intent_type: str, parameters: Dict[str, Any], timeout: int = 60, session_id: str = None) -> Optional[Dict[str, Any]]:
        if not self.token:
            if not await self.authenticate():
                return None
        
        self.print_info(f"Submitting {intent_type} intent")
        result = await submit_intent(token=self.token, intent_type=intent_type, parameters=parameters, session_id=session_id)
        
        if not result or "execution_id" not in result:
            self.print_error(f"Failed to submit {intent_type} intent")
            return None
        
        execution_id = result["execution_id"]
        self.print_success(f"{intent_type} intent submitted: {execution_id}")
        
        self.print_info("Polling execution status")
        status = await poll_execution_status(execution_id, timeout=timeout)
        
        if not status:
            self.print_error("Could not get execution status")
            return None
        
        if status.get("status") != "completed":
            self.print_error(f"Execution did not complete: {status.get('status')} - {status.get('error', 'Unknown error')}")
            return None
        
        self.print_success("Execution completed successfully")
        return status
    
    async def get_artifact_by_id(self, artifact_id: str, include_visuals: bool = False) -> Optional[Dict[str, Any]]:
        return await get_artifact_by_id(artifact_id, "test_tenant", include_visuals=include_visuals, token=self.token)
    
    async def save_materialization(self, boundary_contract_id: str, file_id: str, tenant_id: str = "test_tenant", user_id: str = None, session_id: str = None) -> bool:
        """
        Save materialization (Phase 2 of two-phase flow).
        
        This is required before files can be parsed.
        """
        import httpx
        from tests.integration.capabilities.capability_test_helpers import RUNTIME_BASE_URL
        
        if not self.token:
            if not await self.authenticate():
                return False
        
        # Use provided IDs or generate defaults
        if not user_id:
            user_id = f"test_user_{self.test_id_prefix}"
        if not session_id:
            from datetime import datetime
            session_id = f"test_session_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        self.print_info(f"Saving materialization (boundary_contract_id: {boundary_contract_id}, file_id: {file_id})")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{RUNTIME_BASE_URL}/api/content/save_materialization",
                params={
                    "boundary_contract_id": boundary_contract_id,
                    "file_id": file_id,
                    "tenant_id": tenant_id
                },
                headers={
                    "Content-Type": "application/json",
                    "x-user-id": user_id,
                    "x-session-id": session_id
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.print_success("Materialization saved successfully")
                    return True
                else:
                    self.print_error(f"Save materialization returned success=False: {data.get('error', 'Unknown error')}")
                    return False
            else:
                self.print_error(f"Save materialization failed with status {response.status_code}: {response.text}")
                return False
    
    def find_artifact_by_type(self, artifacts: Any, artifact_type: str, alternative_types: list = None) -> Optional[Dict[str, Any]]:
        """
        Find artifact by type, handling structured artifacts.
        
        Structured format: artifacts["file"]["result_type"] == "file"
        """
        if alternative_types is None:
            alternative_types = []
        
        # Handle dict (current pattern - structured artifacts)
        if isinstance(artifacts, dict):
            # Check structured format
            for key, value in artifacts.items():
                if isinstance(value, dict) and value.get("result_type") == artifact_type:
                    return value
            
            # Check alternative types
            for alt_type in alternative_types:
                for key, value in artifacts.items():
                    if isinstance(value, dict):
                        result_type = value.get("result_type", "")
                        if alt_type in str(result_type).lower():
                            return value
        
        # Handle list (legacy - should not happen after refactoring)
        elif isinstance(artifacts, list):
            for artifact in artifacts:
                if not isinstance(artifact, dict):
                    continue
                # Check structured format
                if artifact.get("result_type") == artifact_type:
                    return artifact
                # Check legacy format (for backward compatibility during transition)
                artifact_type_field = artifact.get("type") or artifact.get("artifact_type")
                if artifact_type_field == artifact_type:
                    return artifact
        
        return None
    
    @abstractmethod
    async def run_test(self) -> bool:
        pass
    
    async def execute(self) -> bool:
        self.print_test(self.test_name)
        try:
            return await self.run_test()
        except Exception as e:
            self.print_error(f"Test execution error: {e}")
            import traceback
            traceback.print_exc()
            return False
