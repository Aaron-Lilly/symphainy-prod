/**
 * Service Layer Index
 * 
 * Exports all service layer components for easy importing and usage.
 * Provides a unified interface for all external service interactions.
 */

// React import only needed for hooks

// ============================================
// Core Services
// ============================================

export { 
  APIService, 
  apiService, 
  apiGet,
  apiPost,
  apiPut,
  apiDelete,
  apiPatch,
} from './APIService';

// ⚠️ DEPRECATED: WebSocketService is deprecated
// Use UnifiedWebSocketClient instead - see shared/archived/README.md for migration guide
// export {
//   WebSocketService,
//   webSocketService,
//   wsConnect,
//   wsDisconnect,
//   wsSend,
//   wsSubscribe,
// } from './WebSocketService'; // DEPRECATED - Archived

// Runtime Client (NEW - Phase 5 Breaking Change)
export {
  RuntimeClient,
  RuntimeEventType,
} from './RuntimeClient';

// Export types separately to avoid duplicates
export type {
  RuntimeEvent,
  IntentMessage,
  SafetyResponseMessage,
} from './RuntimeClient';

// NOTE: UnifiedWebSocketClient has been removed as a breaking change.
// Use RuntimeClient instead for Runtime Foundation WebSocket endpoint.

// ============================================
// Service Layer Manager
// ============================================

import { APIService } from './APIService';
import { WebSocketService } from './WebSocketService';

/**
 * Service Layer Manager
 * 
 * Manages all service layer instances and provides unified configuration.
 */
export class ServiceLayerManager {
  private apiService: APIService;
  // ⚠️ DEPRECATED: WebSocketService is deprecated - use UnifiedWebSocketClient instead
  // private webSocketService: WebSocketService;
  private sessionContext?: any;

  constructor() {
    this.apiService = new APIService();
    // WebSocketService is deprecated - use UnifiedWebSocketClient instead
    // this.webSocketService = new WebSocketService();
  }

  /**
   * Initialize all services with session context
   */
  initialize(sessionContext: any) {
    this.sessionContext = sessionContext;
    // Note: APIService doesn't have setSessionContext method
    // WebSocketService is deprecated - use UnifiedWebSocketClient instead
    // this.webSocketService.setSessionContext(sessionContext);
  }

  /**
   * Get API service instance
   */
  getAPIService(): APIService {
    return this.apiService;
  }

  /**
   * Get WebSocket service instance
   * @deprecated Use UnifiedWebSocketClient instead
   */
  getWebSocketService(): any {
    console.warn('⚠️ ServiceLayerManager.getWebSocketService is deprecated. Use UnifiedWebSocketClient instead.');
    return null;
  }

  /**
   * Update configuration for all services
   */
  updateConfig(config: {
    api?: any;
    websocket?: any; // WebSocketService is deprecated
  }) {
    if (config.api) {
      // Note: APIService doesn't have updateConfig method
      console.warn('APIService updateConfig not implemented');
    }
    if (config.websocket) {
      console.warn('⚠️ WebSocketService configuration is deprecated. Use UnifiedWebSocketClient instead.');
      // this.webSocketService.updateConfig(config.websocket);
    }
  }

  /**
   * Cleanup all services
   */
  cleanup() {
    // WebSocketService is deprecated - use UnifiedWebSocketClient instead
    // this.webSocketService.disconnectAll();
  }
}

// ============================================
// Global Service Layer Manager Instance
// ============================================

export const serviceLayerManager = new ServiceLayerManager();

// ============================================
// Service Layer Manager Export
// ============================================

// The useServiceLayer hook is now in a separate file to avoid SSR issues
// Import it from: @/shared/hooks/useServiceLayer

// ============================================
// Convenience Exports
// ============================================

// Re-export commonly used types
export type {
  APIResponse,
  APIError,
} from './APIService';

// ⚠️ DEPRECATED: WebSocketService types are deprecated
// Use UnifiedWebSocketClient types instead
// export type {
//   WebSocketMessage,
//   WebSocketConfig,
//   WebSocketConnection,
//   WebSocketError,
//   WebSocketEventListener,
// } from './WebSocketService'; // DEPRECATED - Archived

// Runtime Client types are already exported above - no need to re-export

// NOTE: UnifiedWebSocketClient types have been removed as a breaking change.
// Use RuntimeClient types instead.

// ============================================
// Service Layer Utilities
// ============================================

/**
 * Create a service layer configuration for different environments
 */
export function createServiceConfig(environment: 'development' | 'staging' | 'production') {
  const baseConfig = {
    api: {
      timeout: 30000,
      maxRetries: 3,
      retryDelay: 1000,
    },
    websocket: {
      reconnectAttempts: 5,
      reconnectDelay: 1000,
      maxReconnectDelay: 30000,
      heartbeatInterval: 30000,
      heartbeatTimeout: 10000,
    },
  };

  switch (environment) {
    case 'development':
      // Use centralized API config (NO hardcoded values)
      const { getApiUrl, getRuntimeWebSocketUrl } = require('@/shared/config/api-config');
      return {
        ...baseConfig,
        api: {
          ...baseConfig.api,
          baseURL: getApiUrl(),
        },
        websocket: {
          ...baseConfig.websocket,
          // NOTE: getWebSocketUrl() removed - use getRuntimeWebSocketUrl() with session token
          baseURL: getApiUrl(), // Base URL for Runtime Client
        },
      };

    case 'staging':
      return {
        ...baseConfig,
        api: {
          ...baseConfig.api,
          baseURL: process.env.NEXT_PUBLIC_STAGING_API_URL || 'https://staging-api.symphainy.com',
          timeout: 45000,
          maxRetries: 5,
        },
        websocket: {
          ...baseConfig.websocket,
          baseURL: process.env.NEXT_PUBLIC_STAGING_WS_URL || 'wss://staging-ws.symphainy.com',
          reconnectAttempts: 10,
        },
      };

    case 'production':
      return {
        ...baseConfig,
        api: {
          ...baseConfig.api,
          baseURL: process.env.NEXT_PUBLIC_PRODUCTION_API_URL || 'https://api.symphainy.com',
          timeout: 60000,
          maxRetries: 7,
        },
        websocket: {
          ...baseConfig.websocket,
          baseURL: process.env.NEXT_PUBLIC_PRODUCTION_WS_URL || 'wss://ws.symphainy.com',
          reconnectAttempts: 15,
          heartbeatInterval: 45000,
        },
      };

    default:
      return baseConfig;
  }
}

/**
 * Initialize service layer with environment-specific configuration
 */
export function initializeServiceLayer(environment: 'development' | 'staging' | 'production' = 'development') {
  const config = createServiceConfig(environment);
  serviceLayerManager.updateConfig(config);
  
  console.log(`Service layer initialized for ${environment} environment`);
  return serviceLayerManager;
} 