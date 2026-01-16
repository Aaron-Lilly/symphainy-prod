"""
Control Room Service - Platform Observability

Provides platform statistics, metrics, and health monitoring.

WHAT (Control Room Role): I provide platform observability
HOW (Control Room Implementation): I aggregate data from Runtime, Realms, Solutions, Telemetry
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[6]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from utilities import get_logger


class ControlRoomService:
    """
    Control Room Service - Platform observability.
    
    Provides:
    - Platform statistics
    - Execution metrics
    - Realm health
    - Solution registry status
    - System health
    - Real-time monitoring
    """
    
    def __init__(
        self,
        runtime_client: Optional[Any] = None,
        realm_registry: Optional[Any] = None,
        solution_registry: Optional[Any] = None,
        public_works: Optional[Any] = None
    ):
        """
        Initialize Control Room Service.
        
        Args:
            runtime_client: Runtime client for execution metrics
            realm_registry: Realm registry for realm health
            solution_registry: Solution registry for solution status
            public_works: Public Works Foundation Service
        """
        self.logger = get_logger(self.__class__.__name__)
        self.runtime_client = runtime_client
        self.realm_registry = realm_registry
        self.solution_registry = solution_registry
        self.public_works = public_works
    
    async def get_platform_statistics(self) -> Dict[str, Any]:
        """
        Get overall platform statistics.
        
        Returns:
            Dict with platform statistics
        """
        # Get realm count from Runtime client or registry
        realm_count = 0
        realm_names = []
        if self.runtime_client:
            try:
                realms_data = await self.runtime_client.get_realms()
                realm_count = realms_data.get("total", 0)
                realm_names = realms_data.get("realm_names", [])
            except Exception:
                pass
        elif self.realm_registry:
            realm_names = self.realm_registry.list_realms()
            realm_count = len(realm_names)
        
        stats = {
            "timestamp": datetime.utcnow().isoformat(),
            "realms": {
                "total": realm_count,
                "registered": realm_names
            },
            "solutions": {
                "total": len(self.solution_registry.list_solutions()) if self.solution_registry else 0,
                "active": len(self.solution_registry.list_solutions(active_only=True)) if self.solution_registry else 0
            },
            "system_health": await self._get_system_health()
        }
        
        return stats
    
    async def get_execution_metrics(
        self,
        time_range: str = "1h"
    ) -> Dict[str, Any]:
        """
        Get execution metrics.
        
        Args:
            time_range: Time range for metrics (e.g., "1h", "24h", "7d")
        
        Returns:
            Dict with execution metrics
        """
        # For MVP: Return basic structure
        # In Phase 2: Aggregate from Runtime WAL, State Surface
        
        metrics = {
            "time_range": time_range,
            "timestamp": datetime.utcnow().isoformat(),
            "total_intents": 0,  # TODO: Aggregate from WAL
            "success_rate": 0.0,  # TODO: Calculate from execution results
            "average_execution_time": 0.0,  # TODO: Calculate from execution times
            "intent_distribution": {},  # TODO: Group by intent type
            "error_rate": 0.0  # TODO: Calculate from errors
        }
        
        return metrics
    
    async def get_realm_health(self) -> Dict[str, Any]:
        """
        Get realm health status.
        
        Returns:
            Dict with realm health information
        """
        # Try to get realms from Runtime via Runtime client
        if self.runtime_client:
            try:
                realms_data = await self.runtime_client.get_realms()
                realms_list = realms_data.get("realms", [])
                
                # Add health status to each realm
                for realm in realms_list:
                    realm["status"] = "healthy"  # TODO: Check actual health
                
                return {
                    "realms": realms_list,
                    "total": len(realms_list),
                    "timestamp": datetime.utcnow().isoformat()
                }
            except Exception as e:
                self.logger.warning(f"Failed to get realms from Runtime: {e}")
        
        # Fallback: Use realm_registry if available
        if self.realm_registry:
            realms = []
            for realm_name in self.realm_registry.list_realms():
                realm = self.realm_registry.get_realm(realm_name)
                if realm:
                    realms.append({
                        "name": realm_name,
                        "status": "healthy",  # TODO: Check actual health
                        "intents_supported": len(realm.declare_intents()) if hasattr(realm, 'declare_intents') else 0,
                        "intents": realm.declare_intents() if hasattr(realm, 'declare_intents') else []
                    })
            
            return {
                "realms": realms,
                "total": len(realms),
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # No realm data available
        return {
            "realms": [],
            "total": 0,
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Realm registry not available"
        }
    
    async def get_solution_registry_status(self) -> Dict[str, Any]:
        """
        Get solution registry status.
        
        Returns:
            Dict with solution registry information
        """
        if not self.solution_registry:
            return {
                "solutions": [],
                "total": 0,
                "active": 0
            }
        
        solutions = self.solution_registry.list_solutions()
        active_solutions = self.solution_registry.list_solutions(active_only=True)
        
        solution_list = []
        for solution in solutions:
            solution_list.append({
                "solution_id": solution.solution_id,
                "status": "active" if self.solution_registry.is_solution_active(solution.solution_id) else "inactive",
                "domains": [binding.domain for binding in solution.domain_service_bindings],
                "intents": solution.supported_intents,
                "created_at": solution.created_at.isoformat() if hasattr(solution.created_at, 'isoformat') else str(solution.created_at)
            })
        
        return {
            "solutions": solution_list,
            "total": len(solutions),
            "active": len(active_solutions),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_system_health(self) -> Dict[str, Any]:
        """
        Get system health status.
        
        Returns:
            Dict with system health information
        """
        health = {
            "runtime": await self._get_runtime_health(),
            "infrastructure": await self._get_infrastructure_health(),
            "overall": "healthy"  # TODO: Calculate from components
        }
        
        return health
    
    async def _get_runtime_health(self) -> Dict[str, Any]:
        """Get Runtime health status."""
        # For MVP: Basic health check
        # In Phase 2: Detailed health from Runtime
        
        if self.runtime_client:
            try:
                # Try to get health from Runtime
                # This would be a health check endpoint
                return {"status": "healthy", "available": True}
            except Exception as e:
                return {"status": "unhealthy", "available": False, "error": str(e)}
        
        return {"status": "unknown", "available": False}
    
    async def _get_infrastructure_health(self) -> Dict[str, Any]:
        """Get infrastructure health status."""
        if not self.public_works:
            return {"status": "unknown"}
        
        # Check Public Works adapters
        adapters_health = {}
        
        # Check ArangoDB
        if hasattr(self.public_works, 'arango_adapter') and self.public_works.arango_adapter:
            adapters_health["arango"] = {"status": "healthy"}  # TODO: Actual health check
        
        # Check Redis
        if hasattr(self.public_works, 'redis_adapter') and self.public_works.redis_adapter:
            adapters_health["redis"] = {"status": "healthy"}  # TODO: Actual health check
        
        # Check GCS
        if hasattr(self.public_works, 'gcs_adapter') and self.public_works.gcs_adapter:
            adapters_health["gcs"] = {"status": "healthy"}  # TODO: Actual health check
        
        return {
            "adapters": adapters_health,
            "status": "healthy" if adapters_health else "unknown"
        }
    
    async def _get_system_health(self) -> Dict[str, Any]:
        """Get overall system health (helper method)."""
        runtime_health = await self._get_runtime_health()
        infrastructure_health = await self._get_infrastructure_health()
        
        # Calculate overall health
        if runtime_health.get("status") == "healthy" and infrastructure_health.get("status") == "healthy":
            return "healthy"
        elif runtime_health.get("status") == "unhealthy" or infrastructure_health.get("status") == "unhealthy":
            return "unhealthy"
        else:
            return "degraded"
