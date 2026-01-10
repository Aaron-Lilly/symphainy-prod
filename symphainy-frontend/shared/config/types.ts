/**
 * Configuration Types
 * TypeScript interfaces for configuration management
 */

export interface UnifiedConfig {
  // API Configuration
  api: {
    baseURL: string;
    timeout: number;
    maxRetries: number;
    retryDelay: number;
  };
  
  // WebSocket Configuration
  websocket: {
    url: string;
    reconnectAttempts: number;
    reconnectDelay: number;
    heartbeatInterval: number;
  };
  
  // Session Configuration
  session: {
    tokenKey: string;
    stateKey: string;
    expirationTime: number;
    refreshThreshold: number;
  };
  
  // Smart City Configuration
  smartCity: {
    enabled: boolean;
    trafficCopUrl: string;
    archiveUrl: string;
    conductorUrl: string;
    postOfficeUrl: string;
  };
  
  // Environment Configuration
  environment: {
    isDevelopment: boolean;
    isProduction: boolean;
    isTest: boolean;
    debugMode: boolean;
  };
  
  // Feature Flags
  features: {
    smartCityIntegration: boolean;
    realTimeUpdates: boolean;
    offlineMode: boolean;
    analytics: boolean;
  };
} 