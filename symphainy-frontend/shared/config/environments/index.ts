/**
 * Environment Configuration Orchestrator
 * Provides unified access to environment-specific configurations
 */

import { developmentConfig } from './development';
import { productionConfig } from './production';
import { testConfig } from './test';
import { stagingConfig } from './staging';
import { UnifiedConfig } from '../core';

export type Environment = 'development' | 'production' | 'test' | 'staging';

export const environmentConfigs: Record<Environment, Partial<UnifiedConfig>> = {
  development: developmentConfig,
  production: productionConfig,
  test: testConfig,
  staging: stagingConfig,
};

export function getEnvironmentConfig(environment: Environment): Partial<UnifiedConfig> {
  return environmentConfigs[environment] || developmentConfig;
}

export function getCurrentEnvironment(): Environment {
  const nodeEnv = process.env.NODE_ENV;
  
  switch (nodeEnv) {
    case 'production':
      return 'production';
    case 'test':
      return 'test';
    case 'development':
    default:
      return 'development';
  }
}

export function getCurrentEnvironmentConfig(): Partial<UnifiedConfig> {
  const currentEnv = getCurrentEnvironment();
  return getEnvironmentConfig(currentEnv);
}

// Export individual configs for direct access
export { developmentConfig, productionConfig, testConfig, stagingConfig }; 