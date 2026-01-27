/**
 * Centralized API Configuration Service
 * 
 * Single source of truth for all API URLs and WebSocket endpoints.
 * NO hardcoded values - all configuration from environment variables.
 * 
 * Usage:
 *   import { getApiUrl, getWebSocketUrl } from '@/shared/config/api-config';
 *   const apiUrl = getApiUrl();
 *   const wsUrl = getWebSocketUrl(sessionToken);
 */

/**
 * Get the base API URL from environment variables
 * 
 * Priority:
 * 1. NEXT_PUBLIC_API_URL (primary)
 * 2. NEXT_PUBLIC_BACKEND_URL (fallback)
 * 3. NEXT_PUBLIC_API_BASE_URL (legacy fallback)
 * 
 * @throws Error if no API URL is configured (required for production)
 */
export function getApiUrl(): string {
  const apiUrl = 
    process.env.NEXT_PUBLIC_API_URL || 
    process.env.NEXT_PUBLIC_BACKEND_URL || 
    process.env.NEXT_PUBLIC_API_BASE_URL;

  if (!apiUrl) {
    // In development, allow localhost fallback
    if (process.env.NODE_ENV === 'development') {
      console.warn(
        '⚠️ No API URL configured. Using localhost:8000 for development. ' +
        'Set NEXT_PUBLIC_API_URL environment variable for production.'
      );
      return 'http://localhost:8000';
    }
    
    // In production, fail fast if not configured
    throw new Error(
      'API URL is required but not configured. ' +
      'Please set NEXT_PUBLIC_API_URL environment variable.'
    );
  }

  // Normalize URL: remove trailing slash only
  // DO NOT strip ports - they are part of the URL and may be required
  return apiUrl.replace(/\/$/, '');
}

/**
 * Get the full API URL for a specific endpoint
 * 
 * @param endpoint - API endpoint path (e.g., '/api/v1/content-pillar/upload-file')
 * @returns Full URL to the endpoint
 */
export function getApiEndpointUrl(endpoint: string): string {
  const baseUrl = getApiUrl();
  const normalizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${baseUrl}${normalizedEndpoint}`;
}

// NOTE: getWebSocketUrl() has been removed as a breaking change.
// Use getRuntimeWebSocketUrl() instead for Runtime Foundation WebSocket endpoint.

/**
 * Get Runtime Foundation WebSocket URL (NEW)
 * 
 * @param sessionToken - Session token to include in query string (required)
 * @returns WebSocket URL (ws:// or wss://) for Runtime Foundation
 */
export function getRuntimeWebSocketUrl(sessionToken: string): string {
  const apiUrl = getApiUrl();
  
  // Convert http/https to ws/wss
  const wsBaseUrl = apiUrl.replace(/^http/, 'ws');
  
  // Build WebSocket URL with session token
  const tokenParam = `?session_token=${encodeURIComponent(sessionToken)}`;
  
  // NEW: Single WebSocket endpoint via Runtime Foundation
  return `${wsBaseUrl}/api/runtime/agent${tokenParam}`;
}

/**
 * Get the frontend URL (for CORS, redirects, etc.)
 * 
 * Priority:
 * 1. NEXT_PUBLIC_FRONTEND_URL
 * 2. NEXT_PUBLIC_APP_URL
 * 3. Derived from window.location (client-side only)
 * 
 * @returns Frontend URL
 */
export function getFrontendUrl(): string {
  // Server-side: use environment variable
  if (typeof window === 'undefined') {
    const frontendUrl = 
      process.env.NEXT_PUBLIC_FRONTEND_URL || 
      process.env.NEXT_PUBLIC_APP_URL;
    
    if (!frontendUrl) {
      if (process.env.NODE_ENV === 'development') {
        return 'http://localhost:3000';
      }
      throw new Error(
        'Frontend URL is required but not configured. ' +
        'Please set NEXT_PUBLIC_FRONTEND_URL environment variable.'
      );
    }
    
    return frontendUrl.replace(/\/$/, '');
  }
  
  // Client-side: use window.location as fallback
  const envUrl = 
    process.env.NEXT_PUBLIC_FRONTEND_URL || 
    process.env.NEXT_PUBLIC_APP_URL;
  
  if (envUrl) {
    return envUrl.replace(/\/$/, '');
  }
  
  // Fallback to current origin (client-side only)
  return window.location.origin;
}

/**
 * Check if we're in development mode
 */
export function isDevelopment(): boolean {
  return process.env.NODE_ENV === 'development';
}

/**
 * Check if we're in production mode
 */
export function isProduction(): boolean {
  return process.env.NODE_ENV === 'production';
}

/**
 * Get environment name
 */
export function getEnvironment(): 'development' | 'production' | 'test' {
  const env = process.env.NODE_ENV;
  if (env === 'development' || env === 'production' || env === 'test') {
    return env;
  }
  return 'development';
}




