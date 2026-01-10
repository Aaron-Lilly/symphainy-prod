/**
 * Test Environment Configuration
 * Configuration specific to test environment
 */

import { UnifiedConfig } from '../core';

export const testConfig: Partial<UnifiedConfig> = {
  api: {
    baseURL: 'http://localhost:8000',
    timeout: 5000, // Short timeout for tests
    maxRetries: 1,
    retryDelay: 100,
  },
  websocket: {
    url: 'ws://localhost:8000/smart-chat',
    reconnectAttempts: 2,
    reconnectDelay: 100,
    heartbeatInterval: 5000, // Very frequent heartbeats for tests
  },
  session: {
    tokenKey: 'guideSessionToken_test',
    stateKey: 'pillarStates_test',
    expirationTime: 10 * 60 * 1000, // 10 minutes for tests
    refreshThreshold: 1 * 60 * 1000, // 1 minute
  },
  smartCity: {
    enabled: false, // Disable Smart City for tests
    trafficCopUrl: '',
    archiveUrl: '',
    conductorUrl: '',
    postOfficeUrl: '',
  },
  environment: {
    isDevelopment: false,
    isProduction: false,
    isTest: true,
    debugMode: true,
  },
  features: {
    smartCityIntegration: false, // Disable for tests
    realTimeUpdates: false, // Disable for tests
    offlineMode: false,
    analytics: false,
  },
}; 