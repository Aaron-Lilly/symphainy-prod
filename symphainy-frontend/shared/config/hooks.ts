/**
 * Configuration Management Hooks
 * React hooks for configuration management functionality
 */

import React, { useState, useEffect, useCallback } from 'react';
import { UnifiedConfigManager, UnifiedConfig } from './core';
import { ConfigValidator, ValidationResult } from './validation';

// Hook for configuration management
export function useUnifiedConfig(initialConfig?: Partial<UnifiedConfig>) {
  const [configManager] = useState(() => new UnifiedConfigManager(initialConfig));
  const [config, setConfig] = useState(configManager.getConfig());
  const [validation, setValidation] = useState<ValidationResult>({ isValid: true, errors: [] });

  useEffect(() => {
    const unsubscribe = configManager.subscribe((newConfig) => {
      setConfig(newConfig);
      const validationResult = ConfigValidator.validateRequired(newConfig);
      setValidation(validationResult);
    });

    return unsubscribe;
  }, [configManager]);

  const updateConfig = useCallback((updates: Partial<UnifiedConfig>) => {
    configManager.updateConfig(updates);
  }, [configManager]);

  const updateSection = useCallback(<K extends keyof UnifiedConfig>(
    section: K,
    updates: Partial<UnifiedConfig[K]>
  ) => {
    configManager.updateSection(section, updates);
  }, [configManager]);

  return {
    config,
    validation,
    updateConfig,
    updateSection,
    isValid: validation.isValid,
    errors: validation.errors,
  };
}

// Hook for environment-specific configuration
export function useEnvironmentConfig() {
  const { config } = useUnifiedConfig();
  
  return {
    isDevelopment: config.environment.isDevelopment,
    isProduction: config.environment.isProduction,
    isTest: config.environment.isTest,
    debugMode: config.environment.debugMode,
    environment: config.environment,
  };
}

// Hook for API configuration
export function useAPIConfig() {
  const { config } = useUnifiedConfig();
  
  return {
    baseURL: config.api.baseURL,
    timeout: config.api.timeout,
    maxRetries: config.api.maxRetries,
    retryDelay: config.api.retryDelay,
    apiConfig: config.api,
  };
} 