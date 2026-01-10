/**
 * WebSocket Connection Registry
 * 
 * Manages WebSocket connections to prevent duplicate connections per session.
 * Ensures only one active connection exists per session token.
 * 
 * Features:
 * - Connection tracking per session token
 * - Automatic cleanup of stale connections
 * - Prevents duplicate connections
 * - Connection lifecycle management
 */

export class WebSocketConnectionRegistry {
  private static instance: WebSocketConnectionRegistry;
  private connections: Map<string, WebSocket> = new Map();
  private connectionMetadata: Map<string, {
    connectedAt: number;
    lastActivity: number;
    reconnectAttempts: number;
  }> = new Map();

  private constructor() {
    // Private constructor for singleton
  }

  /**
   * Get singleton instance
   */
  static getInstance(): WebSocketConnectionRegistry {
    if (!WebSocketConnectionRegistry.instance) {
      WebSocketConnectionRegistry.instance = new WebSocketConnectionRegistry();
    }
    return WebSocketConnectionRegistry.instance;
  }

  /**
   * Get existing connection for session token
   */
  getConnection(sessionToken: string): WebSocket | null {
    const connection = this.connections.get(sessionToken);
    
    // Check if connection is still open
    if (connection && connection.readyState === WebSocket.OPEN) {
      // Update last activity
      const metadata = this.connectionMetadata.get(sessionToken);
      if (metadata) {
        metadata.lastActivity = Date.now();
      }
      return connection;
    }
    
    // Connection is closed or doesn't exist
    if (connection) {
      // Clean up stale connection
      this.removeConnection(sessionToken);
    }
    
    return null;
  }

  /**
   * Register a new connection
   * Closes existing connection if one exists for the same session token
   */
  registerConnection(sessionToken: string, ws: WebSocket): void {
    // Close existing connection if any
    const existing = this.connections.get(sessionToken);
    if (existing && existing.readyState !== WebSocket.CLOSED) {
      console.log(`[WebSocketConnectionRegistry] Closing existing connection for session: ${sessionToken.substring(0, 10)}...`);
      existing.close(1000, 'Replaced by new connection');
    }
    
    // Register new connection
    this.connections.set(sessionToken, ws);
    this.connectionMetadata.set(sessionToken, {
      connectedAt: Date.now(),
      lastActivity: Date.now(),
      reconnectAttempts: 0
    });
    
    console.log(`[WebSocketConnectionRegistry] Registered connection for session: ${sessionToken.substring(0, 10)}...`);
    
    // Set up cleanup on close
    ws.addEventListener('close', () => {
      // Only remove if this is still the registered connection
      if (this.connections.get(sessionToken) === ws) {
        this.removeConnection(sessionToken);
      }
    });
  }

  /**
   * Remove connection from registry
   */
  removeConnection(sessionToken: string): void {
    const ws = this.connections.get(sessionToken);
    if (ws && ws.readyState !== WebSocket.CLOSED) {
      try {
        ws.close();
      } catch (error) {
        // Ignore errors when closing
      }
    }
    
    this.connections.delete(sessionToken);
    this.connectionMetadata.delete(sessionToken);
    
    console.log(`[WebSocketConnectionRegistry] Removed connection for session: ${sessionToken.substring(0, 10)}...`);
  }

  /**
   * Check if connection exists and is open
   */
  hasActiveConnection(sessionToken: string): boolean {
    const connection = this.getConnection(sessionToken);
    return connection !== null;
  }

  /**
   * Get all active connections
   */
  getActiveConnections(): string[] {
    const active: string[] = [];
    
    // Convert to array to avoid iteration issues
    const entries = Array.from(this.connections.entries());
    for (const [sessionToken, ws] of entries) {
      if (ws.readyState === WebSocket.OPEN) {
        active.push(sessionToken);
      } else {
        // Clean up stale connections
        this.removeConnection(sessionToken);
      }
    }
    
    return active;
  }

  /**
   * Get connection metadata
   */
  getConnectionMetadata(sessionToken: string): {
    connectedAt: number;
    lastActivity: number;
    reconnectAttempts: number;
  } | null {
    return this.connectionMetadata.get(sessionToken) || null;
  }

  /**
   * Update connection metadata
   */
  updateConnectionMetadata(sessionToken: string, updates: Partial<{
    lastActivity: number;
    reconnectAttempts: number;
  }>): void {
    const metadata = this.connectionMetadata.get(sessionToken);
    if (metadata) {
      Object.assign(metadata, updates);
    }
  }

  /**
   * Clean up all connections
   */
  cleanupAll(): void {
    console.log(`[WebSocketConnectionRegistry] Cleaning up ${this.connections.size} connections`);
    
    // Convert to array to avoid iteration issues
    const entries = Array.from(this.connections.entries());
    for (const [sessionToken, ws] of entries) {
      try {
        if (ws.readyState !== WebSocket.CLOSED) {
          ws.close(1000, 'Registry cleanup');
        }
      } catch (error) {
        // Ignore errors
      }
    }
    
    this.connections.clear();
    this.connectionMetadata.clear();
  }

  /**
   * Clean up stale connections (closed or older than maxAge)
   */
  cleanupStale(maxAge: number = 5 * 60 * 1000): void {
    const now = Date.now();
    
    // Convert to array to avoid iteration issues
    const entries = Array.from(this.connections.entries());
    for (const [sessionToken, ws] of entries) {
      const metadata = this.connectionMetadata.get(sessionToken);
      
      // Remove if connection is closed
      if (ws.readyState === WebSocket.CLOSED) {
        this.removeConnection(sessionToken);
        continue;
      }
      
      // Remove if connection is too old and inactive
      if (metadata && (now - metadata.lastActivity) > maxAge) {
        console.log(`[WebSocketConnectionRegistry] Removing stale connection: ${sessionToken.substring(0, 10)}...`);
        this.removeConnection(sessionToken);
      }
    }
  }

  /**
   * Get registry stats
   */
  getStats(): {
    totalConnections: number;
    activeConnections: number;
    staleConnections: number;
  } {
    let active = 0;
    let stale = 0;
    
    // Convert to array to avoid iteration issues
    const values = Array.from(this.connections.values());
    for (const ws of values) {
      if (ws.readyState === WebSocket.OPEN) {
        active++;
      } else {
        stale++;
      }
    }
    
    return {
      totalConnections: this.connections.size,
      activeConnections: active,
      staleConnections: stale
    };
  }
}

// Export singleton instance
export const webSocketConnectionRegistry = WebSocketConnectionRegistry.getInstance();

