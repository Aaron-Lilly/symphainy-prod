/**
 * Enhanced Smart City WebSocket Client
 * Stub implementation - replaced by RuntimeClient
 * @deprecated Use RuntimeClient from '../services/RuntimeClient' instead
 */

import { RuntimeClient } from '../services/RuntimeClient';

/**
 * @deprecated This class is deprecated. Use RuntimeClient instead.
 */
export class EnhancedSmartCityWebSocketClient {
  private runtimeClient: RuntimeClient | null = null;

  constructor(config?: { baseUrl?: string; sessionToken?: string }) {
    console.warn('EnhancedSmartCityWebSocketClient is deprecated. Use RuntimeClient instead.');
    if (config?.baseUrl && config?.sessionToken) {
      // Get both access_token and session_id from storage
      const accessToken = typeof window !== 'undefined' ? sessionStorage.getItem("access_token") : null;
      const sessionId = config.sessionToken; // sessionToken is actually session_id
      
      if (!accessToken || !sessionId) {
        console.warn("Missing access_token or session_id, cannot create RuntimeClient");
        return;
      }
      
      this.runtimeClient = new RuntimeClient({
        baseUrl: config.baseUrl,
        accessToken: accessToken,
        sessionId: sessionId,
        autoReconnect: true,
      });
    }
  }

  async connect(): Promise<void> {
    if (this.runtimeClient) {
      await this.runtimeClient.connect();
    }
  }

  disconnect(): void {
    if (this.runtimeClient) {
      this.runtimeClient.disconnect();
    }
  }

  sendMessage(message: string | any): void {
    if (this.runtimeClient) {
      // If message is an object, try to extract intent or stringify it
      let intent: string;
      let sessionId: string = 'default';
      let agentType: 'guide' | 'liaison' | 'specialist' = 'guide';
      
      if (typeof message === 'string') {
        intent = message;
      } else if (message.intent) {
        intent = message.intent;
        sessionId = message.session_id || message.sessionToken || 'default';
        agentType = message.agent_type || 'guide';
      } else {
        intent = JSON.stringify(message);
      }
      // RuntimeClient uses submitIntent for agent messages
      this.runtimeClient.submitIntent({
        intent,
        session_id: sessionId,
        agent_type: agentType,
        metadata: typeof message === 'object' ? message.metadata : {}
      });
    } else {
      console.warn('EnhancedSmartCityWebSocketClient.sendMessage() - RuntimeClient not initialized');
    }
  }

  isConnected(): boolean {
    return this.runtimeClient?.isConnected() ?? false;
  }

  onMessage(callback: (message: any) => void): () => void {
    if (this.runtimeClient) {
      // RuntimeClient uses on() method with RuntimeEventType
      const { RuntimeEventType } = require('../services/RuntimeClient');
      return this.runtimeClient.on(RuntimeEventType.STEP_COMPLETED, callback);
    }
    return () => {};
  }

  onError(callback: (error: Error) => void): () => void {
    if (this.runtimeClient) {
      return this.runtimeClient.onError(callback);
    }
    return () => {};
  }

  onConnect(callback: () => void): () => void {
    if (this.runtimeClient) {
      return this.runtimeClient.onConnect(callback);
    }
    return () => {};
  }

  onDisconnect(callback: () => void): () => void {
    if (this.runtimeClient) {
      return this.runtimeClient.onDisconnect(callback);
    }
    return () => {};
  }

  shutdown(): void {
    this.disconnect();
  }

  async storeSession(sessionId: string, data: any): Promise<void> {
    console.warn('EnhancedSmartCityWebSocketClient.storeSession() - Not yet implemented', { sessionId, data });
    // Stub implementation - would send session data to backend
  }

  async deleteSession(sessionId: string): Promise<void> {
    console.warn('EnhancedSmartCityWebSocketClient.deleteSession() - Not yet implemented', { sessionId });
    // Stub implementation - would delete session data from backend
  }
}

