/**
 * Extended Configuration Validation
 * Additional validation methods for configuration
 */

import { ValidationError, ValidationResult } from './validation';
import { UnifiedConfig } from './core';

export class ExtendedConfigValidator {
  // Validate numeric ranges
  static validateNumericRanges(config: Partial<UnifiedConfig>): ValidationResult {
    const errors: ValidationError[] = [];

    // Validate API timeout
    if (config.api?.timeout && (config.api.timeout < 1000 || config.api.timeout > 120000)) {
      errors.push({
        field: 'api.timeout',
        message: 'API timeout must be between 1000ms and 120000ms',
        value: config.api.timeout,
      });
    }

    // Validate retry attempts
    if (config.api?.maxRetries && (config.api.maxRetries < 0 || config.api.maxRetries > 10)) {
      errors.push({
        field: 'api.maxRetries',
        message: 'Max retries must be between 0 and 10',
        value: config.api.maxRetries,
      });
    }

    // Validate session expiration
    if (config.session?.expirationTime && (config.session.expirationTime < 60000 || config.session.expirationTime > 604800000)) {
      errors.push({
        field: 'session.expirationTime',
        message: 'Session expiration must be between 1 minute and 7 days',
        value: config.session.expirationTime,
      });
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  // Comprehensive validation
  static validateConfig(config: Partial<UnifiedConfig>): ValidationResult {
    const requiredValidation = this.validateRequired(config);
    const urlValidation = this.validateUrls(config);
    const numericValidation = this.validateNumericRanges(config);

    const allErrors = [
      ...requiredValidation.errors,
      ...urlValidation.errors,
      ...numericValidation.errors,
    ];

    return {
      isValid: allErrors.length === 0,
      errors: allErrors,
    };
  }

  // Validate required fields (imported from base validator)
  static validateRequired(config: Partial<UnifiedConfig>): ValidationResult {
    const errors: ValidationError[] = [];

    if (!config.api?.baseURL) {
      errors.push({
        field: 'api.baseURL',
        message: 'API base URL is required',
        value: config.api?.baseURL,
      });
    }

    if (!config.websocket?.url) {
      errors.push({
        field: 'websocket.url',
        message: 'WebSocket URL is required',
        value: config.websocket?.url,
      });
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  // Validate URLs (imported from base validator)
  static validateUrls(config: Partial<UnifiedConfig>): ValidationResult {
    const errors: ValidationError[] = [];

    const urlFields = [
      { field: 'api.baseURL', value: config.api?.baseURL },
      { field: 'websocket.url', value: config.websocket?.url },
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

  private static isValidUrl(url: string): boolean {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  }
} 