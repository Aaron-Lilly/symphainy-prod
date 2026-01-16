/**
 * Unified WebSocket Client
 * 
 * Single WebSocket connection for all agent communications (Guide + Liaison).
 * Implements channel-based routing aligned with backend Post Office SDK.
 * 
 * Message Format:
 * {
 *   channel: "guide" | "pillar:content" | "pillar:insights" | "pillar:journey" | "pillar:outcomes",
 *   intent: "chat" | "query" | "command",
 *   payload: {
 *     message: string,
 *     conversation_id?: string,
 *     metadata?: {...}
 *   }
 * }
 * 
 * Response Format:
 * {
 *   type: "response" | "error" | "system",
 *   message: string,
 *   agent_type: "guide" | "liaison",
 *   pillar?: string,
 *   conversation_id: string,
 *   data?: {...},
 *   timestamp: string
 * }
 */

export type WebSocketChannel = 
  | "guide"
  | "pillar:content"
  | "pillar:insights"
  | "pillar:journey"
  | "pillar:outcomes";

export type WebSocketIntent = "chat" | "query" | "command";

export interface WebSocketMessage {
  channel: WebSocketChannel;
  intent: WebSocketIntent;
  payload: {
    message: string;
    conversation_id?: string;
    metadata?: Record<string, any>;
  };
}

export interface WebSocketResponse {
  type: "response" | "error" | "system";
  message: string;
  agent_type: "guide" | "liaison";
  pillar?: string;
  conversation_id: string;
  data?: any;
  timestamp: string;
}

export type WebSocketStatus = "disconnected" | "connecting" | "connected" | "error";

export type MessageHandler = (response: WebSocketResponse) => void;
export type StatusHandler = (status: WebSocketStatus) => void;
export type ErrorHandler = (error: Error) => void;

export class UnifiedWebSocketClient {
  private ws: WebSocket | null = null;
  private url: string;
  private status: WebSocketStatus = "disconnected";
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // Start with 1 second
  private reconnectTimer: NodeJS.Timeout | null = null;
  private messageHandlers: Set<MessageHandler> = new Set();
  private statusHandlers: Set<StatusHandler> = new Set();
  private errorHandlers: Set<ErrorHandler> = new Set();
  private shouldReconnect = true;

  constructor(url?: string) {
    // Default to /ws endpoint (backend WebSocket gateway)
    this.url = url || this.getWebSocketUrl();
  }

  private getWebSocketUrl(): string {
    // Get base URL from environment or config
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || 
                   process.env.NEXT_PUBLIC_EXPERIENCE_URL ||
                   "http://localhost:8001";
    
    // Convert http:// to ws:// or https:// to wss://
    const wsProtocol = baseUrl.startsWith("https") ? "wss" : "ws";
    const wsBaseUrl = baseUrl.replace(/^https?:\/\//, "");
    
    return `${wsProtocol}://${wsBaseUrl}/ws`;
  }

  /**
   * Connect to WebSocket server
   */
  async connect(): Promise<void> {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return; // Already connected
    }

    if (this.ws?.readyState === WebSocket.CONNECTING) {
      return; // Already connecting
    }

    this.setStatus("connecting");

    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          this.setStatus("connected");
          this.reconnectAttempts = 0;
          this.reconnectDelay = 1000;
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const response: WebSocketResponse = JSON.parse(event.data);
            this.handleMessage(response);
          } catch (error) {
            console.error("Failed to parse WebSocket message:", error);
            this.handleError(new Error("Invalid message format"));
          }
        };

        this.ws.onerror = (error) => {
          console.error("WebSocket error:", error);
          this.setStatus("error");
          this.handleError(new Error("WebSocket connection error"));
          reject(error);
        };

        this.ws.onclose = (event) => {
          this.setStatus("disconnected");
          
          // Attempt to reconnect if not intentionally closed
          if (this.shouldReconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.scheduleReconnect();
          }
        };
      } catch (error) {
        this.setStatus("error");
        reject(error);
      }
    });
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    this.shouldReconnect = false;
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }

    this.setStatus("disconnected");
  }

  /**
   * Send message via WebSocket
   */
  sendMessage(
    channel: WebSocketChannel,
    intent: WebSocketIntent,
    message: string,
    conversationId?: string,
    metadata?: Record<string, any>
  ): void {
    if (this.status !== "connected" || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error("WebSocket is not connected");
    }

    const wsMessage: WebSocketMessage = {
      channel,
      intent,
      payload: {
        message,
        conversation_id: conversationId,
        metadata,
      },
    };

    this.ws.send(JSON.stringify(wsMessage));
  }

  /**
   * Register message handler
   */
  onMessage(handler: MessageHandler): () => void {
    this.messageHandlers.add(handler);
    
    // Return unsubscribe function
    return () => {
      this.messageHandlers.delete(handler);
    };
  }

  /**
   * Register status change handler
   */
  onStatusChange(handler: StatusHandler): () => void {
    this.statusHandlers.add(handler);
    
    // Return unsubscribe function
    return () => {
      this.statusHandlers.delete(handler);
    };
  }

  /**
   * Register error handler
   */
  onError(handler: ErrorHandler): () => void {
    this.errorHandlers.add(handler);
    
    // Return unsubscribe function
    return () => {
      this.errorHandlers.delete(handler);
    };
  }

  /**
   * Get current connection status
   */
  getStatus(): WebSocketStatus {
    return this.status;
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.status === "connected" && 
           this.ws?.readyState === WebSocket.OPEN;
  }

  private setStatus(status: WebSocketStatus): void {
    if (this.status !== status) {
      this.status = status;
      this.statusHandlers.forEach(handler => handler(status));
    }
  }

  private handleMessage(response: WebSocketResponse): void {
    this.messageHandlers.forEach(handler => handler(response));
  }

  private handleError(error: Error): void {
    this.errorHandlers.forEach(handler => handler(error));
  }

  private scheduleReconnect(): void {
    if (this.reconnectTimer) {
      return; // Already scheduled
    }

    this.reconnectAttempts++;
    const delay = Math.min(
      this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1),
      30000 // Max 30 seconds
    );

    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this.connect().catch(error => {
        console.error("Reconnection failed:", error);
      });
    }, delay);
  }
}

// Singleton instance (optional - can be instantiated per component if needed)
let globalWebSocketClient: UnifiedWebSocketClient | null = null;

export function getGlobalWebSocketClient(): UnifiedWebSocketClient {
  if (!globalWebSocketClient) {
    globalWebSocketClient = new UnifiedWebSocketClient();
  }
  return globalWebSocketClient;
}
