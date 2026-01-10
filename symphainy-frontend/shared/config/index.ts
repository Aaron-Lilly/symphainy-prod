/**
 * Configuration Management Orchestrator
 * Provides unified access to all configuration functionality
 */

// Export core functionality
export { UnifiedConfigManager } from './core';
export type { UnifiedConfig } from './types';

// Export extended manager
export { ExtendedConfigManager } from './manager';

// Export environment configurations
export {
  getEnvironmentConfig,
  getCurrentEnvironment,
  getCurrentEnvironmentConfig,
  developmentConfig,
  productionConfig,
  testConfig,
  stagingConfig
} from './environments';
export type { Environment } from './environments';

// Export validation
export { ConfigValidator } from './validation';
export { ExtendedConfigValidator } from './validation_extended';
export type { ValidationError, ValidationResult } from './validation';

// Export hooks
export {
  useUnifiedConfig,
  useEnvironmentConfig,
  useAPIConfig
} from './hooks';

export {
  useWebSocketConfig,
  useSmartCityConfig,
  useFeatureFlags,
  useSessionConfig
} from './hooks_extended';

// Export global configuration instance
export { getGlobalConfig } from './global';

// Export API configuration utilities (NO hardcoded values)
export {
  getApiUrl,
  getApiEndpointUrl,
  getRuntimeWebSocketUrl,
  getFrontendUrl,
  isDevelopment,
  isProduction,
  getEnvironment
} from './api-config'; 