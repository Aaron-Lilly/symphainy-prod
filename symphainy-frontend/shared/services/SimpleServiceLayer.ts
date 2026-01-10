/**
 * Simple Service Layer
 * 
 * A completely client-side only service layer that avoids all SSR issues
 * by not importing React or any client-side dependencies at the module level.
 */

// ============================================
// Simple API Service
// ============================================

export class SimpleAPIService {
  private baseURL: string;
  private sessionToken?: string;

  constructor(baseURL?: string, sessionToken?: string) {
    // Use configured API URL (Traefik route on port 80, not :8000)
    // Override via NEXT_PUBLIC_API_URL environment variable
    // Use centralized API config (NO hardcoded values)
    const { getApiUrl } = require('@/shared/config/api-config');
    const apiBaseURL = baseURL || getApiUrl();
    this.baseURL = apiBaseURL.replace(':8000', '').replace(/\/$/, ''); // Remove port 8000 and trailing slash
    this.sessionToken = sessionToken;
  }

  setSessionToken(token: string) {
    this.sessionToken = token;
  }

  private async makeRequest<T = any>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<{ success: boolean; data?: T; error?: string }> {
    try {
      const url = `${this.baseURL}${endpoint}`;
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        ...(options.headers as Record<string, string>),
      };

      if (this.sessionToken) {
        headers['Authorization'] = `Bearer ${this.sessionToken}`;
      }

      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (!response.ok) {
        const errorText = await response.text();
        return { success: false, error: errorText };
      }

      const data = await response.json();
      return { success: true, data };
    } catch (error: any) {
      return { success: false, error: error.message };
    }
  }

  async get<T = any>(endpoint: string): Promise<{ success: boolean; data?: T; error?: string }> {
    return this.makeRequest<T>(endpoint, { method: 'GET' });
  }

  async post<T = any>(endpoint: string, body?: any): Promise<{ success: boolean; data?: T; error?: string }> {
    return this.makeRequest<T>(endpoint, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async put<T = any>(endpoint: string, body?: any): Promise<{ success: boolean; data?: T; error?: string }> {
    return this.makeRequest<T>(endpoint, {
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async delete<T = any>(endpoint: string): Promise<{ success: boolean; data?: T; error?: string }> {
    return this.makeRequest<T>(endpoint, { method: 'DELETE' });
  }
}

// ============================================
// Simple WebSocket Service
// ============================================
// 
// ⚠️ DEPRECATED: This class is deprecated and will be removed.
// 
// Migration Guide:
// - Use `RuntimeClient` from `@/shared/services/RuntimeClient` instead
// 
// Example migration:
// ```typescript
// // Before:
// const ws = new SimpleWebSocketService();
// ws.setSessionToken(token);
// await ws.connect('/ws');
// 
// // After:
// const client = new RuntimeClient({ baseUrl: getApiUrl(), sessionToken: token });
// await client.connect();
// client.submitIntent({ intent: 'Hello', agent_type: 'guide' });
// ```
//
// This class is kept temporarily for backward compatibility but should not be used in new code.
// It will be removed in a future release.

export class SimpleWebSocketService {
  /**
   * @deprecated Use RuntimeClient instead
   */
  constructor() {
    console.warn('⚠️ SimpleWebSocketService is deprecated. Use RuntimeClient instead.');
  }

  /**
   * @deprecated Use RuntimeClient instead
   */
  setSessionToken(token: string) {
    console.warn('⚠️ SimpleWebSocketService.setSessionToken is deprecated. Use RuntimeClient instead.');
  }

  /**
   * @deprecated Use RuntimeClient instead
   */
  async connect(url: string, options: { requireAuth?: boolean; autoReconnect?: boolean } = {}): Promise<string> {
    throw new Error('SimpleWebSocketService is deprecated. Please migrate to RuntimeClient. See shared/services/RuntimeClient.ts for migration guide.');
  }

  /**
   * @deprecated Use RuntimeClient instead
   */
  subscribe(connectionId: string, eventType: string, callback: (message: any) => void) {
    throw new Error('SimpleWebSocketService is deprecated. Please migrate to RuntimeClient.');
  }

  /**
   * @deprecated Use RuntimeClient instead
   */
  send(connectionId: string, message: any) {
    throw new Error('SimpleWebSocketService is deprecated. Please migrate to RuntimeClient.');
  }

  /**
   * @deprecated Use RuntimeClient instead
   */
  disconnect(connectionId: string) {
    // No-op for backward compatibility
  }

  /**
   * @deprecated Use RuntimeClient instead
   */
  disconnectAll() {
    // No-op for backward compatibility
  }

  /**
   * @deprecated Use RuntimeClient instead
   */
  getConnections() {
    return [];
  }

  /**
   * @deprecated Use RuntimeClient instead
   */
  isConnected(connectionId: string): boolean {
    return false;
  }
}

// ============================================
// Simple Service Layer Manager
// ============================================

export class SimpleServiceLayerManager {
  private apiService: SimpleAPIService;
  private webSocketService: SimpleWebSocketService;
  private sessionToken?: string;

  constructor() {
    this.apiService = new SimpleAPIService();
    this.webSocketService = new SimpleWebSocketService();
  }

  initialize(config: { sessionToken: string }) {
    this.sessionToken = config.sessionToken;
    this.apiService.setSessionToken(config.sessionToken);
    this.webSocketService.setSessionToken(config.sessionToken);
  }

  getAPIService(): SimpleAPIService {
    return this.apiService;
  }

  getWebSocketService(): SimpleWebSocketService {
    return this.webSocketService;
  }

  cleanup() {
    this.webSocketService.disconnectAll();
  }
}

// ============================================
// Global Service Layer Instance
// ============================================

export const simpleServiceLayerManager = new SimpleServiceLayerManager();

// ============================================
// Convenience Functions
// ============================================

export function createSimpleServiceLayer(sessionToken?: string) {
  const manager = new SimpleServiceLayerManager();
  if (sessionToken) {
    manager.initialize({ sessionToken });
  }
  return manager;
}
