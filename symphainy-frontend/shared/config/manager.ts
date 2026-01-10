/**
 * Configuration Manager Methods
 * Extended methods for the UnifiedConfigManager
 */

import { UnifiedConfig, UnifiedConfigManager } from './core';

export class ExtendedConfigManager extends UnifiedConfigManager {
  // Validate configuration on load
  validateConfiguration(): boolean {
    const config = this.getConfig();
    
    // Basic validation
    if (!config.api.baseURL) {
      console.error('API base URL is required');
      return false;
    }
    
    if (!config.websocket.url) {
      console.error('WebSocket URL is required');
      return false;
    }
    
    if (config.api.timeout < 1000 || config.api.timeout > 120000) {
      console.error('API timeout must be between 1000ms and 120000ms');
      return false;
    }
    
    return true;
  }

  // Get configuration for specific environment
  getEnvironmentConfig(): Partial<UnifiedConfig> {
    const config = this.getConfig();
    const env = config.environment;
    
    if (env.isDevelopment) {
      return {
        api: { ...config.api, timeout: 60000 },
        websocket: { ...config.websocket, reconnectAttempts: 10 },
        session: { ...config.session, expirationTime: 60 * 60 * 1000 },
      };
    }
    
    if (env.isProduction) {
      return {
        api: { ...config.api, timeout: 15000 },
        websocket: { ...config.websocket, reconnectAttempts: 3 },
        features: { ...config.features, offlineMode: false },
      };
    }
    
    return {};
  }

  // Reset configuration to defaults
  resetToDefaults(): void {
    this.updateConfig({});
  }

  // Export configuration for debugging
  exportConfig(): string {
    return JSON.stringify(this.getConfig(), null, 2);
  }

  // Import configuration from JSON
  importConfig(configJson: string): boolean {
    try {
      const config = JSON.parse(configJson);
      this.updateConfig(config);
      return true;
    } catch (error) {
      console.error('Failed to import configuration:', error);
      return false;
    }
  }
} 