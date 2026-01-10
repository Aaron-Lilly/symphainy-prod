/**
 * Error Handling Hooks
 * 
 * Provides standardized error handling patterns and utilities
 * for consistent error handling across the application.
 */

import React, { useState, useCallback, useRef, useEffect } from 'react';
// Service layer will be dynamically imported when needed

// ============================================
// Types and Interfaces
// ============================================

export interface ErrorState {
  hasError: boolean;
  error: Error | null;
  errorId: string | null;
  timestamp: number | null;
  retryCount: number;
  isRetrying: boolean;
}

export interface ErrorHandlerOptions {
  maxRetries?: number;
  retryDelay?: number;
  autoRetry?: boolean;
  onError?: (error: Error) => void;
  onRetry?: (retryCount: number) => void;
  onSuccess?: () => void;
  errorReporting?: boolean;
}

export interface UseErrorHandlerReturn {
  errorState: ErrorState;
  handleError: (error: Error) => void;
  clearError: () => void;
  retry: () => void;
  isRetryable: (error: Error) => boolean;
  getErrorMessage: (error: Error) => string;
  getErrorSeverity: (error: Error) => 'low' | 'medium' | 'high' | 'critical';
}

export interface UseAsyncErrorReturn {
  errorState: ErrorState;
  execute: <T>(asyncFn: () => Promise<T>) => Promise<T | null>;
  retry: () => void;
  clearError: () => void;
}

export interface UseServiceErrorReturn {
  errorState: ErrorState;
  handleServiceError: (error: any) => void;
  clearError: () => void;
  retry: () => void;
}

// ============================================
// Error Utilities
// ============================================

export class ErrorUtils {
  static generateErrorId(): string {
    return `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  static isRetryable(error: Error): boolean {
    // Network errors are retryable
    if (error.message.includes('Network') || error.message.includes('fetch')) {
      return true;
    }
    
    // Timeout errors are retryable
    if (error.message.includes('timeout') || error.message.includes('Timeout')) {
      return true;
    }
    
    // Service unavailable errors are retryable
    if (error.message.includes('503') || error.message.includes('Service Unavailable')) {
      return true;
    }
    
    // Rate limit errors are retryable (with backoff)
    if (error.message.includes('429') || error.message.includes('Rate Limit')) {
      return true;
    }
    
    // Connection errors are retryable
    if (error.message.includes('Connection') || error.message.includes('ECONNREFUSED')) {
      return true;
    }
    
    return false;
  }

  static getErrorMessage(error: Error): string {
    // Handle different error types
    if (error.name === 'TypeError') {
      return 'A type error occurred. Please check your input and try again.';
    }
    
    if (error.name === 'ReferenceError') {
      return 'A reference error occurred. Please refresh the page and try again.';
    }
    
    if (error.name === 'SyntaxError') {
      return 'A syntax error occurred. Please check your input and try again.';
    }
    
    if (error.message.includes('Network')) {
      return 'Network error. Please check your connection and try again.';
    }
    
    if (error.message.includes('timeout')) {
      return 'Request timed out. Please try again.';
    }
    
    if (error.message.includes('401') || error.message.includes('Unauthorized')) {
      return 'Authentication required. Please log in and try again.';
    }
    
    if (error.message.includes('403') || error.message.includes('Forbidden')) {
      return 'Access denied. You don\'t have permission to perform this action.';
    }
    
    if (error.message.includes('404') || error.message.includes('Not Found')) {
      return 'Resource not found. Please check the URL and try again.';
    }
    
    if (error.message.includes('429') || error.message.includes('Rate Limit')) {
      return 'Too many requests. Please wait a moment and try again.';
    }
    
    if (error.message.includes('500') || error.message.includes('Internal Server Error')) {
      return 'Server error. Please try again later.';
    }
    
    // Default error message
    return error.message || 'An unexpected error occurred. Please try again.';
  }

  static getErrorSeverity(error: Error): 'low' | 'medium' | 'high' | 'critical' {
    // Critical errors
    if (error.message.includes('Authentication') || error.message.includes('Unauthorized')) {
      return 'critical';
    }
    
    if (error.message.includes('Permission') || error.message.includes('Forbidden')) {
      return 'critical';
    }
    
    // High severity errors
    if (error.name === 'TypeError' || error.name === 'ReferenceError') {
      return 'high';
    }
    
    if (error.message.includes('500') || error.message.includes('Internal Server Error')) {
      return 'high';
    }
    
    // Medium severity errors
    if (error.message.includes('Network') || error.message.includes('timeout')) {
      return 'medium';
    }
    
    if (error.message.includes('404') || error.message.includes('Not Found')) {
      return 'medium';
    }
    
    if (error.message.includes('429') || error.message.includes('Rate Limit')) {
      return 'medium';
    }
    
    // Low severity errors
    return 'low';
  }

  static shouldReportError(error: Error): boolean {
    // Don't report user errors
    if (error.message.includes('User cancelled') || error.message.includes('User denied')) {
      return false;
    }
    
    // Don't report expected errors
    if (error.message.includes('Expected error') || error.message.includes('Handled error')) {
      return false;
    }
    
    // Report all other errors
    return true;
  }
}

// ============================================
// Base Error Handler Hook
// ============================================

export function useErrorHandler(options: ErrorHandlerOptions = {}): UseErrorHandlerReturn {
  const {
    maxRetries = 3,
    retryDelay = 1000,
    autoRetry = false,
    onError,
    onRetry,
    onSuccess,
    errorReporting = true,
  } = options;

  const [errorState, setErrorState] = useState<ErrorState>({
    hasError: false,
    error: null,
    errorId: null,
    timestamp: null,
    retryCount: 0,
    isRetrying: false,
  });

  const retryTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const handleError = useCallback((error: Error) => {
    const errorId = ErrorUtils.generateErrorId();
    const timestamp = Date.now();
    
    setErrorState(prev => ({
      hasError: true,
      error,
      errorId,
      timestamp,
      retryCount: prev.retryCount + 1,
      isRetrying: false,
    }));

    // Call custom error handler
    if (onError) {
      try {
        onError(error);
      } catch (handlerError) {
        console.error('Error in error handler:', handlerError);
      }
    }

    // Report error if enabled
    if (errorReporting && ErrorUtils.shouldReportError(error)) {
      reportError(error, errorId);
    }

    // Auto-retry if enabled and error is retryable
    if (autoRetry && ErrorUtils.isRetryable(error) && errorState.retryCount < maxRetries) {
      retry();
    }
  }, [autoRetry, errorReporting, maxRetries, onError, errorState.retryCount]);

  const clearError = useCallback(() => {
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current);
      retryTimeoutRef.current = null;
    }

    setErrorState({
      hasError: false,
      error: null,
      errorId: null,
      timestamp: null,
      retryCount: 0,
      isRetrying: false,
    });

    if (onSuccess) {
      try {
        onSuccess();
      } catch (successError) {
        console.error('Error in success handler:', successError);
      }
    }
  }, [onSuccess]);

  const retry = useCallback(() => {
    if (errorState.retryCount >= maxRetries) {
      console.warn('Max retries exceeded');
      return;
    }

    setErrorState(prev => ({ ...prev, isRetrying: true }));

    if (onRetry) {
      try {
        onRetry(errorState.retryCount);
      } catch (retryError) {
        console.error('Error in retry handler:', retryError);
      }
    }

    // Clear error after retry delay
    retryTimeoutRef.current = setTimeout(() => {
      clearError();
    }, retryDelay);
  }, [errorState.retryCount, maxRetries, retryDelay, onRetry, clearError]);

  const isRetryable = useCallback((error: Error) => {
    return ErrorUtils.isRetryable(error);
  }, []);

  const getErrorMessage = useCallback((error: Error) => {
    return ErrorUtils.getErrorMessage(error);
  }, []);

  const getErrorSeverity = useCallback((error: Error) => {
    return ErrorUtils.getErrorSeverity(error);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current);
      }
    };
  }, []);

  return {
    errorState,
    handleError,
    clearError,
    retry,
    isRetryable,
    getErrorMessage,
    getErrorSeverity,
  };
}

// ============================================
// Async Error Handler Hook
// ============================================

export function useAsyncError(options: ErrorHandlerOptions = {}): UseAsyncErrorReturn {
  const { handleError, clearError, retry, errorState } = useErrorHandler(options);

  const execute = useCallback(async <T>(asyncFn: () => Promise<T>): Promise<T | null> => {
    try {
      clearError();
      const result = await asyncFn();
      return result;
    } catch (error) {
      handleError(error instanceof Error ? error : new Error(String(error)));
      return null;
    }
  }, [handleError, clearError]);

  return {
    errorState,
    execute,
    retry,
    clearError,
  };
}

// ============================================
// Service Error Handler Hook
// ============================================

export function useServiceError(options: ErrorHandlerOptions = {}): UseServiceErrorReturn {
  const [api, setApi] = useState<any>(null);
  const { handleError, clearError, retry, errorState } = useErrorHandler(options);

  const handleServiceError = useCallback((error: any) => {
    // Convert service errors to standard Error objects
    let standardError: Error;

    if (error instanceof Error) {
      standardError = error;
    } else if (typeof error === 'string') {
      standardError = new Error(error);
    } else if (error?.message) {
      standardError = new Error(error.message);
    } else {
      standardError = new Error('Unknown service error');
    }

    // Add service-specific error information
    if (error?.status) {
      standardError.name = `HTTP${error.status}`;
    }
    if (error?.code) {
      standardError.name = error.code;
    }

    handleError(standardError);
  }, [handleError]);

  return {
    errorState,
    handleServiceError,
    clearError,
    retry,
  };
}

// ============================================
// Error Reporting
// ============================================

async function reportError(error: Error, errorId: string): Promise<void> {
  const endpoint = process.env.NEXT_PUBLIC_ERROR_REPORTING_ENDPOINT || '/api/errors';
  const enabled = process.env.NODE_ENV === 'production' || process.env.NEXT_PUBLIC_ENABLE_ERROR_REPORTING === 'true';

  if (!enabled) {
    console.log('Error reporting disabled, error:', error);
    return;
  }

  try {
    const errorReport = {
      errorId,
      error: {
        name: error.name,
        message: error.message,
        stack: error.stack,
      },
      timestamp: Date.now(),
      userAgent: navigator.userAgent,
      url: typeof window !== 'undefined' ? window.location.href : 'unknown',
      severity: ErrorUtils.getErrorSeverity(error),
      retryable: ErrorUtils.isRetryable(error),
    };

    await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(errorReport),
    });
  } catch (reportError) {
    console.error('Failed to report error:', reportError);
  }
}

// ============================================
// Convenience Hooks
// ============================================

export function useNetworkError(options: ErrorHandlerOptions = {}) {
  return useErrorHandler({
    ...options,
    autoRetry: true,
    maxRetries: 3,
    retryDelay: 2000,
  });
}

export function useAuthError(options: ErrorHandlerOptions = {}) {
  return useErrorHandler({
    ...options,
    autoRetry: false,
    maxRetries: 0,
  });
}

export function useValidationError(options: ErrorHandlerOptions = {}) {
  return useErrorHandler({
    ...options,
    autoRetry: false,
    maxRetries: 0,
    errorReporting: false,
  });
} 