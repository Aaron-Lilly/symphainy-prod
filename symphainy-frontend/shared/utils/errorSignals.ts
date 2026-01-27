/**
 * Error Signal Utilities
 * 
 * Phase 6: Error Handling Standardization
 * 
 * Utilities for creating, handling, and displaying error signals.
 */

import {
  ErrorSignal,
  SessionError,
  AgentError,
  AGUIError,
  ToolError,
  NetworkError,
  ErrorType,
  isErrorSignal,
} from '../types/errors';

/**
 * Create a base error signal
 */
function createBaseErrorSignal(
  type: ErrorType,
  code: string,
  message: string,
  options?: {
    details?: any;
    recoverable?: boolean;
    retryable?: boolean;
    context?: Record<string, any>;
  }
): ErrorSignal {
  return {
    type,
    code,
    message,
    details: options?.details,
    timestamp: Date.now(),
    recoverable: options?.recoverable ?? false,
    retryable: options?.retryable ?? false,
    context: options?.context,
  };
}

/**
 * Create a SessionError
 */
export function createSessionError(
  code: string,
  message: string,
  options?: {
    sessionStatus?: string;
    requiresAuth?: boolean;
    sessionToken?: string;
    details?: any;
    recoverable?: boolean;
  }
): SessionError {
  const base = createBaseErrorSignal('SessionError', code, message, {
    recoverable: options?.recoverable ?? true,
    details: options?.details,
  });
  return {
    ...base,
    type: 'SessionError' as const,
    sessionStatus: options?.sessionStatus,
    requiresAuth: options?.requiresAuth ?? false,
    sessionToken: options?.sessionToken,
  };
}

/**
 * Create an AgentError
 */
export function createAgentError(
  code: string,
  message: string,
  options?: {
    agentType?: string;
    reasoning?: string;
    partialResponse?: string;
    details?: any;
    recoverable?: boolean;
    retryable?: boolean;
  }
): AgentError {
  const base = createBaseErrorSignal('AgentError', code, message, {
    recoverable: options?.recoverable ?? true,
    retryable: options?.retryable ?? true,
    details: options?.details,
  });
  return {
    ...base,
    type: 'AgentError' as const,
    agentType: options?.agentType,
    reasoning: options?.reasoning,
    partialResponse: options?.partialResponse,
  };
}

/**
 * Create an AGUIError
 */
export function createAGUIError(
  code: string,
  message: string,
  options?: {
    validationErrors?: string[];
    intentId?: string;
    aguiState?: any;
    details?: any;
    recoverable?: boolean;
  }
): AGUIError {
  const base = createBaseErrorSignal('AGUIError', code, message, {
    recoverable: options?.recoverable ?? true,
    details: options?.details,
  });
  return {
    ...base,
    type: 'AGUIError' as const,
    validationErrors: options?.validationErrors,
    intentId: options?.intentId,
    aguiState: options?.aguiState,
  };
}

/**
 * Create a ToolError
 */
export function createToolError(
  code: string,
  message: string,
  options?: {
    toolName?: string;
    alternativeTools?: string[];
    toolContext?: Record<string, any>;
    details?: any;
    recoverable?: boolean;
  }
): ToolError {
  const base = createBaseErrorSignal('ToolError', code, message, {
    recoverable: options?.recoverable ?? true,
    details: options?.details,
  });
  return {
    ...base,
    type: 'ToolError' as const,
    toolName: options?.toolName,
    alternativeTools: options?.alternativeTools,
    toolContext: options?.toolContext,
  };
}

/**
 * Create a NetworkError
 */
export function createNetworkError(
  code: string,
  message: string,
  options?: {
    statusCode?: number;
    retryAfter?: number;
    isTimeout?: boolean;
    originalError?: any;
    details?: any;
    retryable?: boolean;
  }
): NetworkError {
  const base = createBaseErrorSignal('NetworkError', code, message, {
    recoverable: options?.retryable !== false,
    retryable: options?.retryable ?? true,
    details: options?.details,
  });
  return {
    ...base,
    type: 'NetworkError' as const,
    statusCode: options?.statusCode,
    retryAfter: options?.retryAfter,
    isTimeout: options?.isTimeout ?? false,
    originalError: options?.originalError,
  };
}

/**
 * Convert an exception/error to an error signal
 */
export function errorToSignal(error: unknown): ErrorSignal {
  // If already an error signal, return as-is
  if (isErrorSignal(error)) {
    return error;
  }

  // If it's an Error object, extract information
  if (error instanceof Error) {
    // Try to determine error type from error message or name
    const errorMessage = error.message.toLowerCase();
    const errorName = error.name.toLowerCase();

    // Network errors
    if (
      errorMessage.includes('network') ||
      errorMessage.includes('fetch') ||
      errorMessage.includes('timeout') ||
      errorMessage.includes('connection') ||
      errorName.includes('network') ||
      errorName.includes('timeout')
    ) {
      return createNetworkError(
        'NETWORK_ERROR',
        error.message || 'Network error occurred',
        {
          originalError: error,
          isTimeout: errorMessage.includes('timeout'),
        }
      );
    }

    // Default to NetworkError for unknown errors
    return createNetworkError(
      'UNKNOWN_ERROR',
      error.message || 'An unexpected error occurred',
      {
        originalError: error,
        details: { name: error.name, stack: error.stack },
      }
    );
  }

  // If it's a string, create a generic error
  if (typeof error === 'string') {
    return createNetworkError('UNKNOWN_ERROR', error);
  }

  // Fallback for unknown error types
  return createNetworkError(
    'UNKNOWN_ERROR',
    'An unexpected error occurred',
    {
      details: error,
    }
  );
}

/**
 * Get user-friendly display message from error signal
 */
export function getErrorDisplayMessage(error: ErrorSignal): string {
  // Use the message directly, or provide fallback
  if (error.message) {
    return error.message;
  }

  // Type-specific fallbacks
  switch (error.type) {
    case 'SessionError':
      return 'Session error occurred. Please try logging in again.';
    case 'AgentError':
      return 'Agent error occurred. Please try again.';
    case 'AGUIError':
      return 'Interface error occurred. Please refresh the page.';
    case 'ToolError':
      return 'Tool error occurred. This capability may be unavailable.';
    case 'NetworkError':
      return 'Network error occurred. Please check your connection and try again.';
    default:
      return 'An error occurred. Please try again.';
  }
}

/**
 * Determine if error should be retried
 */
export function shouldRetry(error: ErrorSignal): boolean {
  if (error.retryable === false) {
    return false;
  }

  if (error.retryable === true) {
    return true;
  }

  // Default retry logic by type
  switch (error.type) {
    case 'NetworkError':
      return true; // Network errors are usually retryable
    case 'AgentError':
      return true; // Agent errors can often be retried
    case 'SessionError':
      return false; // Session errors need user action
    case 'AGUIError':
      return false; // AGUI errors need state fix
    case 'ToolError':
      return false; // Tool errors need alternative
    default:
      return false;
  }
}

/**
 * Get recovery action for error
 */
export interface RecoveryAction {
  label: string;
  action: () => void | Promise<void>;
}

export function getRecoveryAction(
  error: ErrorSignal,
  onRetry?: () => void | Promise<void>,
  onAlternative?: () => void | Promise<void>
): RecoveryAction | null {
  if (!error.recoverable) {
    return null;
  }

  // Network errors - retry
  if (error.type === 'NetworkError' && shouldRetry(error) && onRetry) {
    return {
      label: 'Retry',
      action: onRetry,
    };
  }

  // Agent errors - retry
  if (error.type === 'AgentError' && shouldRetry(error) && onRetry) {
    return {
      label: 'Retry',
      action: onRetry,
    };
  }

  // Tool errors - try alternative
  if (error.type === 'ToolError' && onAlternative) {
    return {
      label: 'Try Alternative',
      action: onAlternative,
    };
  }

  // Session errors - re-authenticate
  if (error.type === 'SessionError') {
    return {
      label: 'Re-authenticate',
      action: () => {
        // Redirect to login or trigger re-auth
        window.location.href = '/login';
      },
    };
  }

  return null;
}
