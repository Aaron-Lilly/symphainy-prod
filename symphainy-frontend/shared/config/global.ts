/**
 * Global Configuration Instance
 * Singleton configuration instance for the entire application
 */

import { UnifiedConfigManager, UnifiedConfig } from './core';
import { getCurrentEnvironmentConfig } from './environments';
import { ConfigValidator } from './validation';

// Global configuration instance
let globalConfigManager: UnifiedConfigManager | null = null;

/**
 * Get the global configuration instance
 * Creates a singleton instance if it doesn't exist
 */
export function getGlobalConfig(): UnifiedConfigManager {
  if (!globalConfigManager) {
    // Load environment-specific configuration
    const envConfig = getCurrentEnvironmentConfig();
    
    // Create the global configuration manager
    globalConfigManager = new UnifiedConfigManager(envConfig);
    
    // Validate the configuration
    const validation = ConfigValidator.validateConfig(globalConfigManager.getConfig());
    
    if (!validation.isValid) {
      console.warn('Configuration validation failed:', validation.errors);
    }
    
    console.log('Global configuration initialized for environment:', process.env.NODE_ENV);
  }
  
  return globalConfigManager;
}

/**
 * Reset the global configuration instance
 * Useful for testing or when environment changes
 */
export function resetGlobalConfig(): void {
  globalConfigManager = null;
}

/**
 * Update global configuration
 * Convenience function to update the global config
 */
export function updateGlobalConfig(updates: Partial<UnifiedConfig>): void {
  const config = getGlobalConfig();
  config.updateConfig(updates);
}

/**
 * Get current configuration values
 * Convenience function to get current config
 */
export function getCurrentConfig(): UnifiedConfig {
  const config = getGlobalConfig();
  return config.getConfig();
} 