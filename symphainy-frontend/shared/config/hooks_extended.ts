/**
 * Extended Configuration Hooks
 * Additional React hooks for configuration management
 */

import React, { useCallback } from 'react';
import { useUnifiedConfig } from './hooks';

// Hook for WebSocket configuration
export function useWebSocketConfig() {
  const { config } = useUnifiedConfig();
  
  return {
    url: config.websocket.url,
    reconnectAttempts: config.websocket.reconnectAttempts,
    reconnectDelay: config.websocket.reconnectDelay,
    heartbeatInterval: config.websocket.heartbeatInterval,
    websocketConfig: config.websocket,
  };
}

// Hook for Smart City configuration
export function useSmartCityConfig() {
  const { config } = useUnifiedConfig();
  
  return {
    enabled: config.smartCity.enabled,
    trafficCopUrl: config.smartCity.trafficCopUrl,
    archiveUrl: config.smartCity.archiveUrl,
    conductorUrl: config.smartCity.conductorUrl,
    postOfficeUrl: config.smartCity.postOfficeUrl,
    smartCityConfig: config.smartCity,
  };
}

// Hook for feature flags
export function useFeatureFlags() {
  const { config } = useUnifiedConfig();
  
  return {
    smartCityIntegration: config.features.smartCityIntegration,
    realTimeUpdates: config.features.realTimeUpdates,
    offlineMode: config.features.offlineMode,
    analytics: config.features.analytics,
    features: config.features,
  };
}

// Hook for session configuration
export function useSessionConfig() {
  const { config } = useUnifiedConfig();
  
  return {
    tokenKey: config.session.tokenKey,
    stateKey: config.session.stateKey,
    expirationTime: config.session.expirationTime,
    refreshThreshold: config.session.refreshThreshold,
    sessionConfig: config.session,
  };
} 