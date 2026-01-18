/**
 * Core Unified Configuration System
 * Centralized configuration management for the frontend application
 */

import { UnifiedConfig } from './types';

// Re-export the type for external use
export type { UnifiedConfig };

export class UnifiedConfigManager {
  private config: UnifiedConfig;
  private listeners: ((config: UnifiedConfig) => void)[] = [];

  constructor(initialConfig?: Partial<UnifiedConfig>) {
    this.config = this.loadConfiguration(initialConfig);
  }

  // Load configuration from environment and defaults
  private loadConfiguration(overrides?: Partial<UnifiedConfig>): UnifiedConfig {
    // Use centralized API config (imported to avoid circular dependency)
    // Import here to use the centralized config service
    const { getApiUrl, getRuntimeWebSocketUrl } = require('./api-config');
    
    const getApiBaseURL = () => {
      try {
        return getApiUrl();
      } catch (error) {
        // Fallback only for development - production should fail fast
        if (process.env.NODE_ENV === 'development') {
          console.warn('⚠️ Using development fallback for API URL');
          return 'http://localhost:8000';
        }
        throw error;
      }
    };
    
    const getWebSocketBaseURL = () => {
      const apiBaseURL = getApiBaseURL();
      return apiBaseURL.replace(/^http/, 'ws');
    };
    
    const defaultConfig: UnifiedConfig = {
      api: {
        baseURL: getApiBaseURL(),
        timeout: 30000,
        maxRetries: 3,
        retryDelay: 1000,
      },
      websocket: {
        // NEW: Single WebSocket endpoint via Post Office Gateway
        url: process.env.NEXT_PUBLIC_WEBSOCKET_URL || `${getWebSocketBaseURL()}/ws`,
        reconnectAttempts: 5,
        reconnectDelay: 1000,
        heartbeatInterval: 30000,
      },
      session: {
        // Note: Session tokens now managed by PlatformStateProvider
        // Auth tokens stored in sessionStorage (see AuthProvider)
        tokenKey: 'auth_token', // Updated to match new AuthProvider
        stateKey: 'platform_state', // Updated to match PlatformStateProvider
        expirationTime: 24 * 60 * 60 * 1000, // 24 hours
        refreshThreshold: 5 * 60 * 1000, // 5 minutes
      },
      smartCity: {
        enabled: process.env.NEXT_PUBLIC_SMART_CITY_ENABLED === 'true',
        trafficCopUrl: process.env.NEXT_PUBLIC_TRAFFIC_COP_URL || '',
        archiveUrl: process.env.NEXT_PUBLIC_ARCHIVE_URL || '',
        conductorUrl: process.env.NEXT_PUBLIC_CONDUCTOR_URL || '',
        postOfficeUrl: process.env.NEXT_PUBLIC_POST_OFFICE_URL || '',
      },
      environment: {
        isDevelopment: process.env.NODE_ENV === 'development',
        isProduction: process.env.NODE_ENV === 'production',
        isTest: process.env.NODE_ENV === 'test',
        debugMode: process.env.NEXT_PUBLIC_DEBUG_MODE === 'true',
      },
      features: {
        smartCityIntegration: true,
        realTimeUpdates: true,
        offlineMode: false,
        analytics: process.env.NEXT_PUBLIC_ANALYTICS_ENABLED === 'true',
      },
    };

    return { ...defaultConfig, ...overrides };
  }

  // Get entire configuration
  getConfig(): UnifiedConfig {
    return { ...this.config };
  }

  // Get specific configuration section
  getSection<K extends keyof UnifiedConfig>(section: K): UnifiedConfig[K] {
    return { ...this.config[section] };
  }

  // Update configuration
  updateConfig(updates: Partial<UnifiedConfig>): void {
    this.config = { ...this.config, ...updates };
    this.notifyListeners();
  }

  // Update specific section
  updateSection<K extends keyof UnifiedConfig>(
    section: K, 
    updates: Partial<UnifiedConfig[K]>
  ): void {
    this.config[section] = { ...this.config[section], ...updates };
    this.notifyListeners();
  }

  // Observer pattern for configuration changes
  subscribe(listener: (config: UnifiedConfig) => void): () => void {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  private notifyListeners(): void {
    this.listeners.forEach(listener => listener(this.getConfig()));
  }
} 