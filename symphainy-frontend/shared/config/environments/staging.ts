/**
 * Staging Environment Configuration
 * Configuration specific to staging environment
 */

import { UnifiedConfig } from '../core';

export const stagingConfig: Partial<UnifiedConfig> = {
  api: {
    baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'https://staging-api.symphainy.com',
    timeout: 20000, // Medium timeout for staging
    maxRetries: 3,
    retryDelay: 1000,
  },
  websocket: {
    url: process.env.NEXT_PUBLIC_WEBSOCKET_URL || 'wss://staging-api.symphainy.com/smart-chat',
    reconnectAttempts: 5,
    reconnectDelay: 1000,
    heartbeatInterval: 20000,
  },
  session: {
    tokenKey: 'guideSessionToken_staging',
    stateKey: 'pillarStates_staging',
    expirationTime: 12 * 60 * 60 * 1000, // 12 hours for staging
    refreshThreshold: 3 * 60 * 1000, // 3 minutes
  },
  smartCity: {
    enabled: true,
    trafficCopUrl: process.env.NEXT_PUBLIC_TRAFFIC_COP_URL || 'https://staging-api.symphainy.com/traffic-cop',
    archiveUrl: process.env.NEXT_PUBLIC_ARCHIVE_URL || 'https://staging-api.symphainy.com/archive',
    conductorUrl: process.env.NEXT_PUBLIC_CONDUCTOR_URL || 'https://staging-api.symphainy.com/conductor',
    postOfficeUrl: process.env.NEXT_PUBLIC_POST_OFFICE_URL || 'https://staging-api.symphainy.com/post-office',
  },
  environment: {
    isDevelopment: false,
    isProduction: false,
    isTest: false,
    debugMode: true, // Enable debug mode for staging
  },
  features: {
    smartCityIntegration: true,
    realTimeUpdates: true,
    offlineMode: true, // Enable offline mode for staging testing
    analytics: true, // Enable analytics for staging
  },
}; 