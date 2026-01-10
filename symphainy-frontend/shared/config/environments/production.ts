/**
 * Production Environment Configuration
 * Configuration specific to production environment
 */

import { UnifiedConfig } from '../core';

export const productionConfig: Partial<UnifiedConfig> = {
  api: {
    baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'https://api.symphainy.com',
    timeout: 15000, // Shorter timeout for production
    maxRetries: 2,
    retryDelay: 500,
  },
  websocket: {
    url: process.env.NEXT_PUBLIC_WEBSOCKET_URL || 'wss://api.symphainy.com/smart-chat',
    reconnectAttempts: 3,
    reconnectDelay: 1000,
    heartbeatInterval: 30000,
  },
  session: {
    tokenKey: 'guideSessionToken',
    stateKey: 'pillarStates',
    expirationTime: 24 * 60 * 60 * 1000, // 24 hours
    refreshThreshold: 5 * 60 * 1000, // 5 minutes
  },
  smartCity: {
    enabled: true,
    trafficCopUrl: process.env.NEXT_PUBLIC_TRAFFIC_COP_URL || 'https://api.symphainy.com/traffic-cop',
    archiveUrl: process.env.NEXT_PUBLIC_ARCHIVE_URL || 'https://api.symphainy.com/archive',
    conductorUrl: process.env.NEXT_PUBLIC_CONDUCTOR_URL || 'https://api.symphainy.com/conductor',
    postOfficeUrl: process.env.NEXT_PUBLIC_POST_OFFICE_URL || 'https://api.symphainy.com/post-office',
  },
  environment: {
    isDevelopment: false,
    isProduction: true,
    isTest: false,
    debugMode: false,
  },
  features: {
    smartCityIntegration: true,
    realTimeUpdates: true,
    offlineMode: false, // Disable offline mode in production
    analytics: true, // Enable analytics in production
  },
}; 