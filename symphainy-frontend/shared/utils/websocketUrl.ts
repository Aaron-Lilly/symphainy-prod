/**
 * WebSocket URL Utility
 * 
 * Centralized utility for constructing WebSocket URLs that work in all environments.
 * Ensures all WebSocket connections use the correct base URL (Traefik route, not direct backend port).
 */

import { getApiUrl } from '@/shared/config/api-config';

/**
 * Get the base API URL for HTTP requests
 * Uses centralized API config (NO hardcoded values)
 * @deprecated Use getApiUrl() from '@/shared/config/api-config' directly
 */
export function getApiBaseURL(): string {
  return getApiUrl();
}

/**
 * Get the WebSocket base URL
 * Converts HTTP URL to WebSocket URL (http -> ws, https -> wss)
 */
export function getWebSocketBaseURL(): string {
  const apiBaseURL = getApiBaseURL();
  return apiBaseURL.replace(/^http/, 'ws');
}

/**
 * Construct a full WebSocket URL for an endpoint
 * @param endpoint - The WebSocket endpoint path (e.g., '/ws' - single Post Office Gateway endpoint)
 * @param sessionToken - Optional session token to include as query parameter
 * @returns Full WebSocket URL
 */
export function getWebSocketURL(endpoint: string, sessionToken?: string | null): string {
  const wsBaseURL = getWebSocketBaseURL();
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  const tokenParam = sessionToken ? `?session_token=${encodeURIComponent(sessionToken)}` : '';
  return `${wsBaseURL}${cleanEndpoint}${tokenParam}`;
}

/**
 * Get the base API URL for HTTP requests (alias for getApiBaseURL for consistency)
 */
export function getBaseURL(): string {
  return getApiBaseURL();
}






