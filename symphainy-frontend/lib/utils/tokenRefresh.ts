/**
 * Token Refresh Utility
 * 
 * Provides authenticated fetch with automatic token refresh.
 */

export interface AuthenticatedFetchOptions extends RequestInit {
  token?: string;
}

export async function authenticatedFetch(
  url: string,
  options: AuthenticatedFetchOptions = {}
): Promise<Response> {
  const { token, ...fetchOptions } = options;
  
  // Stub implementation - just does a regular fetch
  return fetch(url, {
    ...fetchOptions,
    headers: {
      ...(fetchOptions.headers || {}),
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    },
  });
}

export async function refreshToken(): Promise<string | null> {
  console.warn('[tokenRefresh] refreshToken - stub implementation');
  return null;
}

export function getStoredToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('auth_token');
}

export function setStoredToken(token: string): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem('auth_token', token);
}

export function clearStoredToken(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem('auth_token');
}
