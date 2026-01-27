/**
 * Runtime Client - Single WebSocket Client for Runtime Foundation
 * 
 * Provides event-driven interface to Runtime Foundation.
 * All agent interactions go through this client.
 * 
 * Architecture:
 * - Connects to single `/api/runtime/agent` endpoint (Runtime Foundation)
 * - Subscribes to runtime events (STEP_STARTED, STEP_COMPLETED, SAFETY_HALTED, etc.)
 * - Sends intents to Runtime Foundation
 * - Handles safety responses (review, approval, retry)
 * 
 * Message Format (to Runtime):
 * {
 *   "type": "intent",
 *   "intent": "user intent text",
 *   "session_id": "session_id",
 *   "agent_type": "guide" | "liaison" | "specialist",
 *   "metadata": {}
 * }
 * 
 * Or for safety responses:
 * {
 *   "type": "safety_response",
 *   "hook_id": "hook_id",
 *   "response_type": "review" | "approval" | "retry",
 *   "approved": true/false,
 *   "rejection_reason": "optional",
 *   "corrections": {}
 * }
 * 
 * Response Format (from Runtime):
 * {
 *   "type": "runtime_event",
 *   "event_type": "STEP_STARTED" | "STEP_COMPLETED" | "EXECUTION_STARTED" | "EXECUTION_COMPLETED" | "SAFETY_HALTED" | "SAFETY_REVIEW_PENDING" | "SAFETY_APPROVAL_PENDING" | "CONNECTION_ESTABLISHED",
 *   "data": {...},
 *   "timestamp": "ISO timestamp"
 * }
 */

export enum RuntimeEventType {
  CONNECTION_ESTABLISHED = "CONNECTION_ESTABLISHED",
  EXECUTION_STARTED = "EXECUTION_STARTED",
  EXECUTION_COMPLETED = "EXECUTION_COMPLETED",
  EXECUTION_FAILED = "EXECUTION_FAILED",
  STEP_STARTED = "STEP_STARTED",
  STEP_COMPLETED = "STEP_COMPLETED",
  SAFETY_HALTED = "SAFETY_HALTED",
  SAFETY_REVIEW_PENDING = "SAFETY_REVIEW_PENDING",
  SAFETY_APPROVAL_PENDING = "SAFETY_APPROVAL_PENDING",
  AGENT_RESPONSE = "AGENT_RESPONSE",
}

export interface RuntimeEvent {
  type: "runtime_event";
  event_type: RuntimeEventType;
  data: any;
  timestamp: string;
}

export interface IntentMessage {
  type: "intent";
  intent: string;
  session_id?: string;
  agent_type?: "guide" | "liaison" | "specialist";
  metadata?: Record<string, any>;
}

export interface SafetyResponseMessage {
  type: "safety_response";
  hook_id: string;
  response_type: "review" | "approval" | "retry";
  approved: boolean;
  rejection_reason?: string;
  corrections?: Record<string, any>;
}

export type RuntimeEventHandler = (data: any) => void;
export type ErrorHandler = (error: Error) => void;
export type ConnectionHandler = () => void;

export interface RuntimeClientConfig {
  baseUrl: string;
  accessToken: string;  // Access token for authentication (from Supabase)
  sessionId: string;    // Session ID for session state (from Runtime)
  autoReconnect?: boolean;
  reconnectAttempts?: number;
  reconnectDelay?: number;
}

export class RuntimeClient {
  private ws: WebSocket | null = null;
  private config: Required<RuntimeClientConfig>;
  private eventHandlers: Map<RuntimeEventType, Set<RuntimeEventHandler>> = new Map();
  private errorHandlers: Set<ErrorHandler> = new Set();
  private connectHandlers: Set<ConnectionHandler> = new Set();
  private disconnectHandlers: Set<ConnectionHandler> = new Set();
  private reconnectAttempts = 0;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private isIntentionallyDisconnected = false;

  constructor(config: RuntimeClientConfig) {
    this.config = {
      autoReconnect: true,
      reconnectAttempts: 5,
      reconnectDelay: 1000,
      ...config,
    };
  }

  /**
   * Connect to Runtime Foundation WebSocket endpoint
   */
  async connect(): Promise<void> {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return; // Already connected
    }

    if (this.ws?.readyState === WebSocket.CONNECTING) {
      return; // Already connecting
    }

    this.isIntentionallyDisconnected = false;
    this.reconnectAttempts = 0;

    return this._connect();
  }

  private async _connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        // Build WebSocket URL
        const wsUrl = this._buildWebSocketUrl();
        
        console.log('🔌 [RuntimeClient] Connecting to Runtime Foundation:', {
          url: wsUrl.replace(/access_token=[^&]*/, 'access_token=***').replace(/session_id=[^&]*/, 'session_id=***'),
          hasAccessToken: !!this.config.accessToken,
          hasSessionId: !!this.config.sessionId,
        });

        this.ws = new WebSocket(wsUrl);

        // Connection timeout
        const timeout = setTimeout(() => {
          if (this.ws?.readyState !== WebSocket.OPEN) {
            this.ws?.close();
            reject(new Error('Runtime WebSocket connection timeout'));
          }
        }, 10000); // 10 second timeout

        this.ws.onopen = () => {
          clearTimeout(timeout);
          console.log('✅ [RuntimeClient] Connected to Runtime Foundation');
          this.reconnectAttempts = 0;
          this._notifyConnect();
          resolve();
        };

        this.ws.onerror = (error) => {
          clearTimeout(timeout);
          console.error('❌ [RuntimeClient] Connection error:', error);
          const err = new Error('Runtime WebSocket connection error');
          this._notifyError(err);
          reject(err);
        };

        this.ws.onclose = (event) => {
          clearTimeout(timeout);
          console.log('🔌 [RuntimeClient] Disconnected:', {
            code: event.code,
            reason: event.reason,
            wasClean: event.wasClean,
          });
          this._notifyDisconnect();

          // ✅ SESSION BOUNDARY PATTERN: Do NOT retry on 403/401 (session invalid)
          // These are session invalidation signals, not connection errors
          const isSessionInvalid = event.code === 403 || event.code === 401;
          
          if (isSessionInvalid) {
            console.info('ℹ️ [RuntimeClient] Session invalid (403/401) - not retrying. SessionBoundaryProvider will handle recovery.');
            // Don't retry - SessionBoundaryProvider will handle session recovery
            return;
          }

          // Auto-reconnect only for non-session errors and if not intentionally disconnected
          if (!this.isIntentionallyDisconnected && this.config.autoReconnect) {
            this._attemptReconnect();
          }
        };

        this.ws.onmessage = (event) => {
          try {
            const runtimeEvent: RuntimeEvent = JSON.parse(event.data);
            this._handleEvent(runtimeEvent);
          } catch (error) {
            console.error('❌ [RuntimeClient] Failed to parse message:', error);
            this._notifyError(new Error('Failed to parse Runtime event'));
          }
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * Submit intent to Runtime Foundation
   */
  submitIntent(intent: Omit<IntentMessage, 'type'>): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error('Runtime WebSocket is not connected');
    }

    try {
      const message: IntentMessage = {
        type: "intent",
        ...intent,
      };
      
      this.ws.send(JSON.stringify(message));
      console.log('📤 [RuntimeClient] Sent intent:', {
        intent: intent.intent.substring(0, 50) + '...',
        agent_type: intent.agent_type,
      });
    } catch (error) {
      console.error('❌ [RuntimeClient] Failed to send intent:', error);
      this._notifyError(error as Error);
      throw error;
    }
  }

  /**
   * Submit safety response to Runtime Foundation
   */
  submitSafetyResponse(response: Omit<SafetyResponseMessage, 'type'>): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error('Runtime WebSocket is not connected');
    }

    try {
      const message: SafetyResponseMessage = {
        type: "safety_response",
        ...response,
      };
      
      this.ws.send(JSON.stringify(message));
      console.log('📤 [RuntimeClient] Sent safety response:', {
        hook_id: response.hook_id,
        response_type: response.response_type,
        approved: response.approved,
      });
    } catch (error) {
      console.error('❌ [RuntimeClient] Failed to send safety response:', error);
      this._notifyError(error as Error);
      throw error;
    }
  }

  /**
   * Subscribe to runtime events
   */
  on(eventType: RuntimeEventType, handler: RuntimeEventHandler): () => void {
    if (!this.eventHandlers.has(eventType)) {
      this.eventHandlers.set(eventType, new Set());
    }
    this.eventHandlers.get(eventType)!.add(handler);
    
    // Return unsubscribe function
    return () => {
      this.eventHandlers.get(eventType)?.delete(handler);
    };
  }

  /**
   * Unsubscribe from runtime events
   */
  off(eventType: RuntimeEventType, handler: RuntimeEventHandler): void {
    this.eventHandlers.get(eventType)?.delete(handler);
  }

  /**
   * Subscribe to errors
   */
  onError(handler: ErrorHandler): () => void {
    this.errorHandlers.add(handler);
    return () => {
      this.errorHandlers.delete(handler);
    };
  }

  /**
   * Subscribe to connection events
   */
  onConnect(handler: ConnectionHandler): () => void {
    this.connectHandlers.add(handler);
    return () => {
      this.connectHandlers.delete(handler);
    };
  }

  /**
   * Subscribe to disconnection events
   */
  onDisconnect(handler: ConnectionHandler): () => void {
    this.disconnectHandlers.add(handler);
    return () => {
      this.disconnectHandlers.delete(handler);
    };
  }

  /**
   * Disconnect from Runtime Foundation
   */
  disconnect(): void {
    this.isIntentionallyDisconnected = true;
    this._clearReconnectTimer();

    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN || false;
  }

  /**
   * Get connection state
   */
  getConnectionState(): 'connecting' | 'connected' | 'disconnected' | 'error' {
    if (!this.ws) return 'disconnected';
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'connecting';
      case WebSocket.OPEN:
        return 'connected';
      case WebSocket.CLOSING:
      case WebSocket.CLOSED:
        return 'disconnected';
      default:
        return 'error';
    }
  }

  // Private methods

  private _buildWebSocketUrl(): string {
    const baseUrl = this.config.baseUrl.replace(/^https?:\/\//, '').replace(/\/$/, '');
    const protocol = this.config.baseUrl.startsWith('https') ? 'wss' : 'ws';
    // Use both access_token (for authentication) and session_id (for session state)
    // Backend validates access_token (JWT) and uses session_id for session state
    return `${protocol}://${baseUrl}/api/runtime/agent?access_token=${encodeURIComponent(this.config.accessToken)}&session_id=${encodeURIComponent(this.config.sessionId)}`;
  }

  private _handleEvent(event: RuntimeEvent): void {
    // Notify all handlers for this event type
    const handlers = this.eventHandlers.get(event.event_type);
    if (handlers) {
      handlers.forEach((handler) => {
        try {
          handler(event.data);
        } catch (error) {
          console.error(`❌ [RuntimeClient] Error in event handler for ${event.event_type}:`, error);
        }
      });
    }
  }

  private _attemptReconnect(): void {
    if (this.reconnectAttempts >= this.config.reconnectAttempts) {
      console.error('❌ [RuntimeClient] Max reconnect attempts reached');
      this._notifyError(new Error('Max reconnect attempts reached'));
      return;
    }

    this.reconnectAttempts++;
    const delay = this.config.reconnectDelay * this.reconnectAttempts; // Exponential backoff

    console.log(`🔄 [RuntimeClient] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.config.reconnectAttempts})`);

    this.reconnectTimer = setTimeout(() => {
      this._connect().catch((error) => {
        console.error('❌ [RuntimeClient] Reconnection failed:', error);
      });
    }, delay);
  }

  private _clearReconnectTimer(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  private _notifyConnect(): void {
    this.connectHandlers.forEach((handler) => {
      try {
        handler();
      } catch (error) {
        console.error('❌ [RuntimeClient] Error in connect handler:', error);
      }
    });
  }

  private _notifyDisconnect(): void {
    this.disconnectHandlers.forEach((handler) => {
      try {
        handler();
      } catch (error) {
        console.error('❌ [RuntimeClient] Error in disconnect handler:', error);
      }
    });
  }

  private _notifyError(error: Error): void {
    this.errorHandlers.forEach((handler) => {
      try {
        handler(error);
      } catch (err) {
        console.error('❌ [RuntimeClient] Error in error handler:', err);
      }
    });
  }
}








