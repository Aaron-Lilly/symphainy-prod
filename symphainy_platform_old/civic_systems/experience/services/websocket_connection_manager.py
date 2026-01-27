"""
WebSocket Connection Manager

Manages WebSocket connections with limits, tracking, and cleanup.
"""
import sys
from pathlib import Path

# Add project root to path
current = Path(__file__).resolve()
project_root = current
for _ in range(10):
    if (project_root / "pyproject.toml").exists() or (project_root / "requirements.txt").exists():
        break
    project_root = project_root.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, Set
from datetime import datetime, timedelta
from fastapi import WebSocket
from utilities import get_logger

logger = get_logger("WebSocketConnectionManager")


class WebSocketConnectionManager:
    """
    Manages WebSocket connections with limits and tracking.
    
    Features:
    - Connection limits (max connections)
    - Connection tracking (user_id, tenant_id, metadata)
    - Automatic cleanup on disconnect
    - Connection health monitoring
    """
    
    def __init__(self, max_connections: int = 1000):
        """
        Initialize connection manager.
        
        Args:
            max_connections: Maximum number of concurrent connections
        """
        self.max_connections = max_connections
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        self.user_connections: Dict[str, Set[str]] = {}  # user_id -> set of connection_ids
        self.logger = logger
    
    async def connect(
        self,
        websocket: WebSocket,
        connection_id: str,
        user_id: str,
        tenant_id: str,
        session_token: Optional[str] = None
    ) -> bool:
        """
        Register a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            connection_id: Unique connection identifier
            user_id: User identifier
            tenant_id: Tenant identifier
            session_token: Optional session token
        
        Returns:
            True if connection accepted, False if rejected (at capacity)
        """
        # Check connection limit
        if len(self.active_connections) >= self.max_connections:
            self.logger.warning(f"Connection limit reached ({self.max_connections}), rejecting connection")
            await websocket.close(code=1013, reason="Server at capacity")
            return False
        
        # Register connection
        self.active_connections[connection_id] = websocket
        self.connection_metadata[connection_id] = {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "session_token": session_token,
            "connected_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "message_count": 0
        }
        
        # Track user connections
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(connection_id)
        
        self.logger.info(
            f"Connection registered: {connection_id} (user: {user_id}, tenant: {tenant_id}, "
            f"total: {len(self.active_connections)})"
        )
        
        return True
    
    def disconnect(self, connection_id: str):
        """
        Remove a WebSocket connection.
        
        Args:
            connection_id: Connection identifier to remove
        """
        if connection_id not in self.active_connections:
            return
        
        # Get metadata before removal
        metadata = self.connection_metadata.get(connection_id, {})
        user_id = metadata.get("user_id")
        
        # Remove from active connections
        del self.active_connections[connection_id]
        del self.connection_metadata[connection_id]
        
        # Remove from user connections
        if user_id and user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        self.logger.info(
            f"Connection removed: {connection_id} (user: {user_id}, "
            f"total: {len(self.active_connections)})"
        )
    
    def update_activity(self, connection_id: str):
        """Update last activity timestamp for a connection."""
        if connection_id in self.connection_metadata:
            self.connection_metadata[connection_id]["last_activity"] = datetime.utcnow()
            self.connection_metadata[connection_id]["message_count"] = (
                self.connection_metadata[connection_id].get("message_count", 0) + 1
            )
    
    def get_connection(self, connection_id: str) -> Optional[WebSocket]:
        """Get WebSocket connection by ID."""
        return self.active_connections.get(connection_id)
    
    def get_connection_metadata(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """Get connection metadata by ID."""
        return self.connection_metadata.get(connection_id)
    
    def get_user_connections(self, user_id: str) -> Set[str]:
        """Get all connection IDs for a user."""
        return self.user_connections.get(user_id, set())
    
    def get_connection_count(self) -> int:
        """Get current number of active connections."""
        return len(self.active_connections)
    
    def get_user_connection_count(self, user_id: str) -> int:
        """Get number of connections for a specific user."""
        return len(self.user_connections.get(user_id, set()))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get connection statistics."""
        total_messages = sum(
            meta.get("message_count", 0)
            for meta in self.connection_metadata.values()
        )
        
        # Calculate average connection age
        now = datetime.utcnow()
        connection_ages = [
            (now - meta.get("connected_at", now)).total_seconds()
            for meta in self.connection_metadata.values()
        ]
        avg_age = sum(connection_ages) / len(connection_ages) if connection_ages else 0
        
        return {
            "total_connections": len(self.active_connections),
            "max_connections": self.max_connections,
            "unique_users": len(self.user_connections),
            "total_messages": total_messages,
            "average_connection_age_seconds": avg_age
        }
    
    async def cleanup_idle_connections(self, max_idle_seconds: int = 3600):
        """
        Clean up connections that have been idle for too long.
        
        Args:
            max_idle_seconds: Maximum idle time in seconds before cleanup
        """
        now = datetime.utcnow()
        idle_connections = []
        
        for connection_id, metadata in self.connection_metadata.items():
            last_activity = metadata.get("last_activity", metadata.get("connected_at"))
            idle_seconds = (now - last_activity).total_seconds()
            
            if idle_seconds > max_idle_seconds:
                idle_connections.append(connection_id)
        
        for connection_id in idle_connections:
            websocket = self.active_connections.get(connection_id)
            if websocket:
                try:
                    await websocket.close(code=1008, reason="Connection idle timeout")
                except Exception as e:
                    self.logger.debug(f"Error closing idle connection {connection_id}: {e}")
            
            self.disconnect(connection_id)
            self.logger.info(f"Cleaned up idle connection: {connection_id}")
        
        if idle_connections:
            self.logger.info(f"Cleaned up {len(idle_connections)} idle connections")
