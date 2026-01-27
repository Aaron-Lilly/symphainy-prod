"""
Nurse SDK - Telemetry, Retries, and Self-Healing Coordination

SDK for Nurse coordination (used by Experience, Solution, Realms).
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional
from dataclasses import dataclass

from utilities import get_logger, get_clock


@dataclass
class TelemetryRecord:
    """Telemetry record with execution contract."""
    telemetry_data: Dict[str, Any]
    execution_contract: Dict[str, Any]


@dataclass
class RetryRequest:
    """Retry request with execution contract."""
    execution_id: str
    retry_config: Dict[str, Any]
    execution_contract: Dict[str, Any]


class NurseSDK:
    """
    Nurse SDK - Coordination Logic
    
    Coordinates telemetry, retries, and self-healing.
    """
    
    def __init__(
        self,
        telemetry_abstraction: Optional[Any] = None,
        policy_resolver: Optional[Any] = None
    ):
        self.telemetry_abstraction = telemetry_abstraction
        self.policy_resolver = policy_resolver
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
    
    async def record_telemetry(
        self,
        telemetry_data: Dict[str, Any],
        tenant_id: str
    ) -> TelemetryRecord:
        """Record telemetry (prepare telemetry contract)."""
        execution_contract = {
            "action": "record_telemetry",
            "telemetry_data": telemetry_data,
            "tenant_id": tenant_id,
            "timestamp": self.clock.now_iso()
        }
        
        return TelemetryRecord(
            telemetry_data=telemetry_data,
            execution_contract=execution_contract
        )
    
    async def schedule_retry(
        self,
        execution_id: str,
        retry_config: Dict[str, Any],
        tenant_id: str
    ) -> RetryRequest:
        """Schedule retry (prepare retry contract)."""
        execution_contract = {
            "action": "schedule_retry",
            "execution_id": execution_id,
            "retry_config": retry_config,
            "tenant_id": tenant_id,
            "timestamp": self.clock.now_iso()
        }
        
        return RetryRequest(
            execution_id=execution_id,
            retry_config=retry_config,
            execution_contract=execution_contract
        )
    
    async def get_health_status(
        self,
        component_id: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        """Get health status (prepare health contract)."""
        execution_contract = {
            "action": "get_health_status",
            "component_id": component_id,
            "tenant_id": tenant_id,
            "timestamp": self.clock.now_iso()
        }
        
        return {
            "component_id": component_id,
            "status": "healthy",
            "execution_contract": execution_contract
        }
