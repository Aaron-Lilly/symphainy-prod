"""
Docker Compose Test Utilities

Manages docker-compose services for testing.

WHAT (Test Infrastructure Role): I manage docker-compose services for testing
HOW (Test Infrastructure Implementation): I use docker-compose CLI to start/stop services
"""

import subprocess
import time
import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path
from utilities import get_logger

logger = get_logger("DockerComposeTest")


class DockerComposeTestManager:
    """Manages docker-compose services for testing."""
    
    def __init__(self, compose_file: str = "docker-compose.test.yml"):
        self.compose_file = compose_file
        self.project_root = Path(__file__).parent.parent.parent
        self.compose_path = self.project_root / compose_file
    
    async def start_services(self, services: Optional[List[str]] = None) -> bool:
        """
        Start docker-compose services.
        
        Args:
            services: List of service names to start. If None, starts all services.
        
        Returns:
            True if services started successfully
        """
        services = services or [
            "redis", "arango", "consul", "meilisearch", "gcs-emulator"
        ]
        cmd = ["docker-compose", "-f", str(self.compose_path), "up", "-d"] + services
        
        try:
            logger.info(f"Starting services: {services}")
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                logger.error(f"Failed to start services: {result.stderr}")
                return False
            
            # Wait for health checks
            await self._wait_for_health(services)
            logger.info(f"✅ Services started: {services}")
            return True
        except Exception as e:
            logger.error(f"Error starting services: {e}", exc_info=True)
            return False
    
    async def stop_services(self, services: Optional[List[str]] = None) -> bool:
        """
        Stop docker-compose services.
        
        Args:
            services: List of service names to stop. If None, stops all services.
        
        Returns:
            True if services stopped successfully
        """
        services = services or [
            "redis", "arango", "consul", "meilisearch", "gcs-emulator"
        ]
        cmd = ["docker-compose", "-f", str(self.compose_path), "stop"] + services
        
        try:
            logger.info(f"Stopping services: {services}")
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Services stopped: {services}")
                return True
            else:
                logger.warning(f"Some services may not have stopped: {result.stderr}")
                return True  # Don't fail if services are already stopped
        except Exception as e:
            logger.error(f"Error stopping services: {e}", exc_info=True)
            return False
    
    async def cleanup(self, remove_volumes: bool = False) -> bool:
        """
        Clean up test data and volumes.
        
        Args:
            remove_volumes: If True, removes volumes as well.
        
        Returns:
            True if cleanup successful
        """
        cmd = ["docker-compose", "-f", str(self.compose_path), "down"]
        if remove_volumes:
            cmd.append("-v")
        
        try:
            logger.info("Cleaning up test infrastructure...")
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                logger.info("✅ Test infrastructure cleaned up")
                return True
            else:
                logger.warning(f"Cleanup may have issues: {result.stderr}")
                return True  # Don't fail cleanup
        except Exception as e:
            logger.error(f"Error cleaning up: {e}", exc_info=True)
            return False
    
    async def _wait_for_health(self, services: List[str], timeout: int = 60):
        """
        Wait for services to become healthy.
        
        Args:
            services: List of service names
            timeout: Maximum time to wait in seconds
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            all_healthy = True
            
            for service in services:
                if service == "redis":
                    if not await self._check_redis_health():
                        all_healthy = False
                        break
                elif service == "arango":
                    if not await self._check_arango_health():
                        all_healthy = False
                        break
                elif service == "consul":
                    if not await self._check_consul_health():
                        all_healthy = False
                        break
            
            if all_healthy:
                logger.info("✅ All services are healthy")
                return
            
            await asyncio.sleep(2)
        
        logger.warning(f"⚠️ Services did not become healthy within {timeout} seconds")
    
    async def _check_redis_health(self) -> bool:
        """Check Redis health."""
        try:
            import redis
            # Use test port from environment or default
            import os
            test_port = int(os.getenv("TEST_REDIS_PORT", "6380"))
            r = redis.Redis(host="localhost", port=test_port, db=0, socket_connect_timeout=1)
            r.ping()
            return True
        except Exception:
            return False
    
    async def _check_arango_health(self) -> bool:
        """Check ArangoDB health."""
        try:
            import httpx
            import os
            test_port = int(os.getenv("TEST_ARANGO_PORT", "8530"))
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(f"http://localhost:{test_port}/_api/version")
                return response.status_code == 200
        except Exception:
            return False
    
    async def _check_consul_health(self) -> bool:
        """Check Consul health."""
        try:
            import httpx
            import os
            test_port = int(os.getenv("TEST_CONSUL_PORT", "8501"))
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(f"http://localhost:{test_port}/v1/status/leader")
                return response.status_code == 200
        except Exception:
            return False
    
    def is_service_running(self, service: str) -> bool:
        """
        Check if a service is running.
        
        Args:
            service: Service name
        
        Returns:
            True if service is running
        """
        cmd = ["docker-compose", "-f", str(self.compose_path), "ps", "-q", service]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode == 0 and result.stdout.strip() != ""
        except Exception:
            return False
