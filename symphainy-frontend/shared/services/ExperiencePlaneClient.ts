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

import { UnifiedWebSocketClient, WebSocketChannel } from './UnifiedWebSocketClient';
import { getApiUrl, getApiEndpointUrl } from '@/shared/config/api-config';
import type {
  SessionCreateRequest,
  SessionCreateResponse,
  Session,
  IntentSubmitRequest,
  IntentSubmitResponse,
  ExecutionStatusResponse,
  ExecutionStatus,
} from '@/shared/types/runtime-contracts';

// Re-export types for consumers
export type {
  SessionCreateRequest,
  SessionCreateResponse,
  Session,
  IntentSubmitRequest,
  IntentSubmitResponse,
  ExecutionStatusResponse,
  ExecutionStatus,
};

/**
 * Extended execution status with additional fields for streaming
 */
export interface StreamingExecutionStatus extends ExecutionStatusResponse {
  tenant_id?: string;
  session_id?: string;
  started_at?: string;
  completed_at?: string;
  metadata?: Record<string, unknown>;
}

/**
 * Custom error for session not found
 */
export class SessionNotFoundError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = 'SessionNotFoundError';
    this.status = status;
  }
}

/**
 * Custom error for API requests
 */
export class ApiRequestError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiRequestError';
    this.status = status;
  }
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
   * Create anonymous session (no authentication required)
   * 
   * ✅ SESSION-FIRST PATTERN: Sessions exist before authentication
   */
  async createAnonymousSession(): Promise<SessionCreateResponse> {
    const url = getApiEndpointUrl('/api/session/create-anonymous');
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({}),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to create anonymous session' }));
      throw new Error(error.detail || `Failed to create anonymous session: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Upgrade anonymous session with authentication
   * 
   * ✅ SESSION-FIRST PATTERN: Authentication upgrades existing session
   */
  async upgradeSession(
    sessionId: string,
    userData: { user_id: string; tenant_id: string; access_token: string; metadata?: Record<string, unknown> }
  ): Promise<Session> {
    const url = getApiEndpointUrl(`/api/session/${sessionId}/upgrade`);
    
    const response = await fetch(url, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${userData.access_token}`,
      },
      body: JSON.stringify({
        user_id: userData.user_id,
        tenant_id: userData.tenant_id,
        access_token: userData.access_token,
        metadata: userData.metadata,
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to upgrade session' }));
      throw new Error(error.detail || `Failed to upgrade session: ${response.statusText}`);
    }

    const data = await response.json();
    return {
      session_id: data.session_id,
      tenant_id: data.tenant_id,
      user_id: data.user_id,
      created_at: data.created_at,
      metadata: data.metadata || {},
    };
  }

  /**
   * Get session details (anonymous or authenticated)
   * 
   * ✅ SESSION-FIRST PATTERN: Allow session calls without authentication
   */
  async getSession(sessionId: string, tenantId?: string): Promise<Session> {
    const url = getApiEndpointUrl(`/api/session/${sessionId}`);
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    // Add Authorization header if access_token exists (optional)
    const accessToken = typeof window !== 'undefined' ? sessionStorage.getItem("access_token") : null;
    if (accessToken) {
      headers['Authorization'] = `Bearer ${accessToken}`;
    }
    
    // Add tenant_id as query param if provided
    const params = new URLSearchParams();
    if (tenantId) {
      params.append('tenant_id', tenantId);
    }
    const urlWithParams = params.toString() ? `${url}?${params.toString()}` : url;
    
    const response = await fetch(urlWithParams, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      if (response.status === 404) {
        // Session doesn't exist - return a structured error that can be caught
        const error = new SessionNotFoundError(`Session ${sessionId} not found`, 404);
        throw error;
      }
      const errorData = await response.json().catch(() => ({ detail: 'Failed to get session' }));
      const error = new ApiRequestError(
        errorData.detail || `Failed to get session: ${response.statusText}`,
        response.status
      );
      throw error;
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
    const wsClient = this.getWebSocketClient();
    
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
          session_id: response.data.session_id || '',
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
    metadata?: Record<string, unknown>
  ): Promise<void> {
    const wsClient = this.getWebSocketClient();
    
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
    return this.getWebSocketClient();
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
