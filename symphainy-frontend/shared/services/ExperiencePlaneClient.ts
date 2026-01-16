/**
 * Experience Plane Client
 * 
 * Unified client for Experience Plane API interactions.
 * Handles session management, intent submission, and execution status.
 * 
 * Architecture:
 * - Session Management → Traffic Cop SDK → Runtime
 * - Intent Submission → Runtime Client → Runtime
 * - Execution Status → Runtime Client → Runtime
 * - WebSocket Streaming → UnifiedWebSocketClient
 */

import { UnifiedWebSocketClient, WebSocketChannel, WebSocketIntent } from './UnifiedWebSocketClient';
import { getApiUrl, getApiEndpointUrl } from '@/shared/config/api-config';

export interface SessionCreateRequest {
  tenant_id: string;
  user_id: string;
  session_id?: string;
  execution_contract?: Record<string, any>;
  metadata?: Record<string, any>;
}

export interface SessionCreateResponse {
  session_id: string;
  tenant_id: string;
  user_id: string;
  created_at: string;
  metadata?: Record<string, any>;
}

export interface Session {
  session_id: string;
  tenant_id: string;
  user_id: string;
  created_at: string;
  metadata?: Record<string, any>;
  state?: Record<string, any>;
}

export interface IntentSubmitRequest {
  intent_type: string;
  tenant_id: string;
  session_id: string;
  solution_id?: string;
  parameters?: Record<string, any>;
  metadata?: Record<string, any>;
}

export interface IntentSubmitResponse {
  execution_id: string;
  intent_id: string;
  status: "accepted" | "rejected";
  tenant_id: string;
  session_id: string;
  created_at: string;
  metadata?: Record<string, any>;
}

export interface ExecutionStatus {
  execution_id: string;
  status: "pending" | "running" | "completed" | "failed" | "cancelled";
  intent_id: string;
  tenant_id: string;
  session_id: string;
  started_at?: string;
  completed_at?: string;
  error?: string;
  artifacts?: Record<string, any>;
  events?: Array<Record<string, any>>;
  metadata?: Record<string, any>;
}

export interface ExecutionStatusResponse {
  execution_id: string;
  status: "pending" | "running" | "completed" | "failed" | "cancelled";
  intent_id: string;
  tenant_id: string;
  session_id: string;
  started_at?: string;
  completed_at?: string;
  error?: string;
  artifacts?: Record<string, any>;
  events?: Array<Record<string, any>>;
  metadata?: Record<string, any>;
}

export class ExperiencePlaneClient {
  private baseUrl: string;
  private wsClient: UnifiedWebSocketClient | null = null;

  constructor(baseUrl?: string) {
    this.baseUrl = baseUrl || getApiUrl();
  }

  /**
   * Get or create WebSocket client
   */
  private getWebSocketClient(): UnifiedWebSocketClient {
    if (!this.wsClient) {
      this.wsClient = new UnifiedWebSocketClient();
    }
    return this.wsClient;
  }

  /**
   * Create a new session
   * 
   * Flow: Experience Plane → Traffic Cop SDK → Runtime
   */
  async createSession(request: SessionCreateRequest): Promise<SessionCreateResponse> {
    const url = getApiEndpointUrl('/api/session/create');
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to create session' }));
      throw new Error(error.detail || `Failed to create session: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get session details
   */
  async getSession(sessionId: string, tenantId: string): Promise<Session> {
    const url = getApiEndpointUrl(`/api/session/${sessionId}`);
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      // Note: tenant_id might need to be in query params or headers
      // Adjust based on actual API implementation
    });

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error(`Session ${sessionId} not found`);
      }
      const error = await response.json().catch(() => ({ detail: 'Failed to get session' }));
      throw new Error(error.detail || `Failed to get session: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Submit intent for execution
   * 
   * Flow: Experience Plane → Runtime Client → Runtime
   */
  async submitIntent(request: IntentSubmitRequest): Promise<IntentSubmitResponse> {
    const url = getApiEndpointUrl('/api/intent/submit');
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to submit intent' }));
      throw new Error(error.detail || `Failed to submit intent: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get execution status
   * 
   * Flow: Experience Plane → Runtime Client → Runtime
   */
  async getExecutionStatus(executionId: string, tenantId: string): Promise<ExecutionStatusResponse> {
    const url = getApiEndpointUrl(`/api/execution/${executionId}/status`);
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      // Note: tenant_id might need to be in query params
      // Adjust based on actual API implementation
    });

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error(`Execution ${executionId} not found`);
      }
      const error = await response.json().catch(() => ({ detail: 'Failed to get execution status' }));
      throw new Error(error.detail || `Failed to get execution status: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Stream execution updates via WebSocket
   * 
   * Uses UnifiedWebSocketClient for real-time updates
   */
  streamExecution(
    executionId: string,
    onUpdate: (status: ExecutionStatus) => void,
    onError?: (error: Error) => void
  ): () => void {
    const wsClient = this.getWebSocketClientInstance();
    
    // Connect if not already connected
    if (!wsClient.isConnected()) {
      wsClient.connect().catch(error => {
        if (onError) {
          onError(error);
        }
      });
    }

    // Subscribe to execution updates
    // Note: This assumes the backend WebSocket gateway supports execution streaming
    // Adjust channel/intent based on actual backend implementation
    const unsubscribe = wsClient.onMessage((response) => {
      // Filter for execution-related messages
      if (response.data?.execution_id === executionId) {
        const status: ExecutionStatus = {
          execution_id: executionId,
          status: response.data.status || 'running',
          intent_id: response.data.intent_id || '',
          tenant_id: response.data.tenant_id || '',
          started_at: response.data.started_at,
          completed_at: response.data.completed_at,
          error: response.data.error,
          artifacts: response.data.artifacts,
          events: response.data.events,
          metadata: response.data.metadata,
        };
        onUpdate(status);
      }
    });

    // Handle errors
    if (onError) {
      wsClient.onError(onError);
    }

    // Return unsubscribe function
    return () => {
      unsubscribe();
    };
  }

  /**
   * Send chat message via WebSocket
   * 
   * Uses UnifiedWebSocketClient for agent chat
   */
  async sendChatMessage(
    channel: WebSocketChannel,
    message: string,
    conversationId?: string,
    metadata?: Record<string, any>
  ): Promise<void> {
    const wsClient = this.getWebSocketClientInstance();
    
    // Connect if not already connected
    if (!wsClient.isConnected()) {
      await wsClient.connect();
    }

    wsClient.sendMessage(channel, 'chat', message, conversationId, metadata);
  }

  /**
   * Get WebSocket client (for advanced usage)
   */
  getWebSocket(): UnifiedWebSocketClient {
    return this.getWebSocketClientInstance();
  }

  /**
   * Get base URL
   */
  getBaseUrl(): string {
    return this.baseUrl;
  }

  /**
   * Disconnect WebSocket (cleanup)
   */
  disconnect(): void {
    if (this.wsClient) {
      this.wsClient.disconnect();
      this.wsClient = null;
    }
  }
}

// Singleton instance (optional)
let globalExperiencePlaneClient: ExperiencePlaneClient | null = null;

export function getGlobalExperiencePlaneClient(): ExperiencePlaneClient {
  if (!globalExperiencePlaneClient) {
    globalExperiencePlaneClient = new ExperiencePlaneClient();
  }
  return globalExperiencePlaneClient;
}
