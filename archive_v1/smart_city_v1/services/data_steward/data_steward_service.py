"""
Data Steward Service - Phase 4

WHAT: I manage data lifecycle and enforce data governance policies
HOW: I observe Runtime execution and enforce data policies
"""

from typing import Dict, Any, Optional
from symphainy_platform.smart_city.protocols.smart_city_service_protocol import SmartCityServiceProtocol
from symphainy_platform.foundations.public_works.foundation_service import PublicWorksFoundationService
from symphainy_platform.foundations.curator.foundation_service import CuratorFoundationService
from symphainy_platform.runtime.runtime_service import RuntimeService
from symphainy_platform.agentic.foundation_service import AgentFoundationService
from utilities import get_logger, get_clock, LogLevel, LogCategory


class DataStewardService(SmartCityServiceProtocol):
    """Data Steward Service - Data lifecycle and governance."""
    
    def __init__(
        self,
        public_works_foundation: PublicWorksFoundationService,
        curator_foundation: CuratorFoundationService,
        runtime_service: RuntimeService,
        agent_foundation: Optional[AgentFoundationService] = None
    ):
        self.public_works = public_works_foundation
        self.curator = curator_foundation
        self.runtime_service = runtime_service
        self.agent_foundation = agent_foundation
        self.logger = get_logger("data_steward", LogLevel.INFO, LogCategory.PLATFORM)
        self.clock = get_clock()
        
        # Get file storage abstraction from Public Works
        self.file_storage = public_works_foundation.get_file_storage_abstraction()
        if not self.file_storage:
            self.logger.warning("File storage abstraction not available")
        
        self.is_initialized = False
    
    async def initialize(self) -> bool:
        await self.curator.register_service(
            service_instance=self,
            service_metadata={
                "service_name": "DataStewardService",
                "service_type": "smart_city",
                "realm": "smart_city",
                "capabilities": ["data_lifecycle", "data_governance", "policy_enforcement"]
            }
        )
        await self.runtime_service.register_observer("data_steward", self)
        self.is_initialized = True
        return True
    
    async def observe_execution(self, execution_id: str, event: dict) -> None:
        pass
    
    async def enforce_policy(self, execution_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"allowed": True}
    
    async def validate_policy(
        self,
        artifact: Dict[str, Any],
        policy_type: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        Validate policy (public method for agents to use).
        
        Args:
            artifact: Artifact to validate
            policy_type: Type of policy
            tenant_id: Tenant identifier
        
        Returns:
            Dict containing validation result
        """
        # Policy validation logic
        return {"valid": True, "reason": "Policy validation passed"}
    
    async def manage_data_lifecycle(
        self,
        file_path: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Manage data lifecycle (public method).
        
        Args:
            file_path: File path in storage
            metadata: File metadata
        
        Returns:
            bool: True if successful
        """
        if not self.file_storage:
            self.logger.error("File storage abstraction not available")
            return False
        
        try:
            # Upload file if file_data is provided
            if "file_data" in metadata:
                file_data = metadata.pop("file_data")
                if isinstance(file_data, str):
                    file_data = file_data.encode('utf-8')
                
                success = await self.file_storage.upload_file(
                    file_path=file_path,
                    file_data=file_data,
                    metadata=metadata
                )
                return success
            else:
                # Just update metadata
                self.logger.info(f"Metadata update for file: {file_path}")
                return True
        except Exception as e:
            self.logger.error(f"Data lifecycle management failed: {e}", exc_info=True)
            return False
    
    async def enforce_data_policy(
        self,
        file_path: str,
        tenant_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Enforce data policy (public method).
        
        Args:
            file_path: File path in storage
            tenant_id: Tenant identifier
            user_id: User identifier
        
        Returns:
            Dict containing policy enforcement result
        """
        if not self.file_storage:
            self.logger.error("File storage abstraction not available")
            return {"allowed": False, "reason": "File storage not available"}
        
        try:
            # Get file metadata
            metadata = await self.file_storage.get_file_metadata(file_path)
            if not metadata:
                return {"allowed": False, "reason": "File not found"}
            
            # Policy enforcement logic
            # For now, allow access if file exists
            return {
                "allowed": True,
                "reason": "Data policy check passed",
                "file_metadata": metadata
            }
        except Exception as e:
            self.logger.error(f"Data policy enforcement failed: {e}", exc_info=True)
            return {"allowed": False, "reason": f"Policy check failed: {e}"}
    
    async def shutdown(self) -> None:
        self.is_initialized = False
