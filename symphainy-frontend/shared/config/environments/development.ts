/**
 * Development Environment Configuration
 * Configuration specific to development environment
 */

import { UnifiedConfig } from '../core';

export const developmentConfig: Partial<UnifiedConfig> = {
  api: {
    baseURL: 'http://127.0.0.1:8000',
    timeout: 60000, // Longer timeout for development
    maxRetries: 5,
    retryDelay: 2000,
  },
  websocket: {
    url: 'ws://127.0.0.1:8000/smart-chat',
    reconnectAttempts: 10,
    reconnectDelay: 2000,
    heartbeatInterval: 15000, // More frequent heartbeats
  },
  session: {
    tokenKey: 'guideSessionToken_dev',
    stateKey: 'pillarStates_dev',
    expirationTime: 60 * 60 * 1000, // 1 hour for development
    refreshThreshold: 2 * 60 * 1000, // 2 minutes
  },
  smartCity: {
    enabled: true,
    trafficCopUrl: 'http://127.0.0.1:8000/traffic-cop',
    archiveUrl: 'http://127.0.0.1:8000/archive',
    conductorUrl: 'http://127.0.0.1:8000/conductor',
    postOfficeUrl: 'http://127.0.0.1:8000/post-office',
  },
  environment: {
    isDevelopment: true,
    isProduction: false,
    isTest: false,
    debugMode: true,
  },
  features: {
    smartCityIntegration: true,
    realTimeUpdates: true,
    offlineMode: true, // Enable offline mode for development
    analytics: false, // Disable analytics in development
  },
}; 