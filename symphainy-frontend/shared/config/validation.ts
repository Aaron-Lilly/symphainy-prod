/**
 * Configuration Validation
 * Validates configuration values and provides error handling
 */

import { UnifiedConfig } from './core';

export interface ValidationError {
  field: string;
  message: string;
  value?: any;
}

export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
}

export class ConfigValidator {
  // Validate required fields
  static validateRequired(config: Partial<UnifiedConfig>): ValidationResult {
    const errors: ValidationError[] = [];

    // Validate API configuration
    if (!config.api?.baseURL) {
      errors.push({
        field: 'api.baseURL',
        message: 'API base URL is required',
        value: config.api?.baseURL,
      });
    }

    // Validate WebSocket configuration
    if (!config.websocket?.url) {
      errors.push({
        field: 'websocket.url',
        message: 'WebSocket URL is required',
        value: config.websocket?.url,
      });
    }

    // Validate session configuration
    if (!config.session?.tokenKey) {
      errors.push({
        field: 'session.tokenKey',
        message: 'Session token key is required',
        value: config.session?.tokenKey,
      });
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  // Validate URL formats
  static validateUrls(config: Partial<UnifiedConfig>): ValidationResult {
    const errors: ValidationError[] = [];

    const urlFields = [
      { field: 'api.baseURL', value: config.api?.baseURL },
      { field: 'websocket.url', value: config.websocket?.url },
      { field: 'smartCity.trafficCopUrl', value: config.smartCity?.trafficCopUrl },
      { field: 'smartCity.archiveUrl', value: config.smartCity?.archiveUrl },
      { field: 'smartCity.conductorUrl', value: config.smartCity?.conductorUrl },
      { field: 'smartCity.postOfficeUrl', value: config.smartCity?.postOfficeUrl },
    ];

    urlFields.forEach(({ field, value }) => {
      if (value && !this.isValidUrl(value)) {
        errors.push({
          field,
          message: 'Invalid URL format',
          value,
        });
      }
    });

    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  // Helper method to validate URL format
  private static isValidUrl(url: string): boolean {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  }

  // Main validation method
  static validateConfig(config: UnifiedConfig): ValidationResult {
    const requiredValidation = this.validateRequired(config);
    const urlValidation = this.validateUrls(config);

    const allErrors = [
      ...requiredValidation.errors,
      ...urlValidation.errors,
    ];

    return {
      isValid: allErrors.length === 0,
      errors: allErrors,
    };
  }
} 