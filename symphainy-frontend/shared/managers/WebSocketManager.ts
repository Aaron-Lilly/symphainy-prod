/**
 * WebSocket Manager
 * Stub implementation for WebSocket management
 */

export class WebSocketManager {
  constructor() {
    console.warn('WebSocketManager - Stub implementation');
  }

  async connect(sessionToken?: string): Promise<void> {
    console.warn('WebSocketManager.connect() - Not yet implemented', { sessionToken });
  }

  disconnect(): void {
    console.warn('WebSocketManager.disconnect() - Not yet implemented');
  }

  sendMessage(message: string): void {
    console.warn('WebSocketManager.sendMessage() - Not yet implemented');
  }

  isConnected(): boolean {
    return false; // Stub - always returns false
  }

  onConnectionChange(callback: (connected: boolean) => void): () => void {
    console.warn('WebSocketManager.onConnectionChange() - Not yet implemented');
    // Return unsubscribe function
    return () => {};
  }
}

export default WebSocketManager;

