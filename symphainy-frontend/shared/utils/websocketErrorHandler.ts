/**
 * WebSocket Error Handler Utilities
 * 
 * Provides utilities for handling and categorizing WebSocket errors.
 * Distinguishes between auth errors, connection errors, and server errors.
 */

export type WebSocketErrorType = 'auth' | 'connection' | 'server' | 'unknown';

export interface WebSocketError {
  type: WebSocketErrorType;
  message: string;
  code?: number;
  originalError?: Error | Event;
  retryable: boolean;
}

/**
 * Determine error type from WebSocket close event
 */
export function getErrorTypeFromCloseEvent(event: CloseEvent): WebSocketErrorType {
  // Auth errors (401, 403)
  if (event.code === 1008 || event.code === 4001 || event.code === 4003) {
    return 'auth';
  }
  
  // Server errors (5xx range)
  if (event.code >= 5000 && event.code < 6000) {
    return 'server';
  }
  
  // Connection errors (network, timeout, etc.)
  if (event.code === 1006 || event.code === 1001 || event.code === 1002) {
    return 'connection';
  }
  
  // Normal closure
  if (event.code === 1000) {
    return 'unknown'; // Not really an error
  }
  
  return 'connection'; // Default to connection error
}

/**
 * Determine error type from error message
 */
export function getErrorTypeFromMessage(message: string): WebSocketErrorType {
  const lowerMessage = message.toLowerCase();
  
  // Auth-related keywords
  if (
    lowerMessage.includes('auth') ||
    lowerMessage.includes('unauthorized') ||
    lowerMessage.includes('forbidden') ||
    lowerMessage.includes('401') ||
    lowerMessage.includes('403') ||
    lowerMessage.includes('token') ||
    lowerMessage.includes('session')
  ) {
    return 'auth';
  }
  
  // Server-related keywords
  if (
    lowerMessage.includes('server') ||
    lowerMessage.includes('500') ||
    lowerMessage.includes('503') ||
    lowerMessage.includes('internal')
  ) {
    return 'server';
  }
  
  // Connection-related keywords
  if (
    lowerMessage.includes('connection') ||
    lowerMessage.includes('network') ||
    lowerMessage.includes('timeout') ||
    lowerMessage.includes('refused') ||
    lowerMessage.includes('failed to connect')
  ) {
    return 'connection';
  }
  
  return 'unknown';
}

/**
 * Check if error is retryable
 */
export function isRetryableError(errorType: WebSocketErrorType, code?: number): boolean {
  // Auth errors are NOT retryable - user must re-authenticate
  if (errorType === 'auth') {
    return false;
  }
  
  // Server errors are retryable (temporary issues)
  if (errorType === 'server') {
    return true;
  }
  
  // Connection errors are retryable (network issues)
  if (errorType === 'connection') {
    return true;
  }
  
  // Normal closure is not retryable
  if (code === 1000) {
    return false;
  }
  
  // Unknown errors - be conservative, don't retry
  return false;
}

/**
 * Create error object from WebSocket close event
 */
export function createErrorFromCloseEvent(event: CloseEvent): WebSocketError {
  const type = getErrorTypeFromCloseEvent(event);
  const retryable = isRetryableError(type, event.code);
  
  let message = event.reason || 'WebSocket connection closed';
  
  // Provide user-friendly messages
  switch (type) {
    case 'auth':
      message = 'Authentication failed. Please log in again.';
      break;
    case 'server':
      message = 'Server error. Please try again later.';
      break;
    case 'connection':
      message = 'Connection error. Please check your network.';
      break;
    default:
      message = event.reason || 'Connection closed';
  }
  
  return {
    type,
    message,
    code: event.code,
    retryable
  };
}

/**
 * Create error object from error event or Error
 */
export function createErrorFromError(error: Error | Event | string): WebSocketError {
  let message: string;
  let originalError: Error | Event | undefined;
  
  if (typeof error === 'string') {
    message = error;
  } else if (error instanceof Error) {
    message = error.message;
    originalError = error;
  } else {
    message = 'WebSocket error occurred';
    originalError = error;
  }
  
  const type = getErrorTypeFromMessage(message);
  const retryable = isRetryableError(type);
  
  return {
    type,
    message,
    retryable,
    originalError
  };
}

/**
 * Get user-friendly error message
 */
export function getUserFriendlyMessage(error: WebSocketError): string {
  switch (error.type) {
    case 'auth':
      return 'Your session has expired. Please log in again.';
    case 'server':
      return 'The server is experiencing issues. Please try again in a moment.';
    case 'connection':
      return 'Unable to connect. Please check your internet connection.';
    default:
      return error.message || 'An unexpected error occurred.';
  }
}

/**
 * Should redirect to login based on error
 */
export function shouldRedirectToLogin(error: WebSocketError): boolean {
  return error.type === 'auth';
}





