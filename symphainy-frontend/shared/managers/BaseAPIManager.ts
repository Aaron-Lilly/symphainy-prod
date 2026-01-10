/**
 * Base API Manager
 * 
 * Base class for all API managers providing common functionality:
 * - Base URL management
 * - Session token handling
 * - Authenticated fetch with token refresh
 * - Error handling
 * - User context construction
 * - Consistent request/response patterns
 * 
 * All API managers should extend this class.
 */

export interface UserContext {
  user_id?: string;
  tenant_id?: string;
  session_id?: string;
  [key: string]: any;
}

export interface APIRequestOptions extends RequestInit {
  includeUserContext?: boolean;
  userContext?: UserContext;
}

export interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  status?: number;
}

export abstract class BaseAPIManager {
  protected baseURL: string;
  protected sessionToken: string;
  protected userContext?: UserContext;

  constructor(sessionToken: string, baseURL?: string, userContext?: UserContext) {
    this.sessionToken = sessionToken;
    this.userContext = userContext;
    
    // Use centralized API config (NO hardcoded values)
    if (baseURL) {
      this.baseURL = baseURL.replace(':8000', '').replace(/\/$/, '');
    } else {
      // Import here to avoid circular dependency issues
      const { getApiUrl } = require('@/shared/config/api-config');
      this.baseURL = getApiUrl();
    }
  }

  /**
   * Set session token
   */
  setSessionToken(token: string): void {
    this.sessionToken = token;
  }

  /**
   * Set user context (for tenant_id, user_id, etc.)
   */
  setUserContext(context: UserContext): void {
    this.userContext = context;
  }

  /**
   * Get user context
   */
  getUserContext(): UserContext | undefined {
    return this.userContext;
  }

  /**
   * Build user context from available sources
   */
  protected buildUserContext(additionalContext?: UserContext): UserContext {
    const context: UserContext = {
      ...this.userContext,
      ...additionalContext,
    };

    // Extract user_id from session token if available (JWT decode)
    // Note: In production, you might want to decode the JWT to get user_id
    // For now, we rely on it being passed in userContext

    return context;
  }

  /**
   * Authenticated fetch helper that automatically handles token refresh on 401 errors.
   */
  protected async authenticatedFetch(
    url: string,
    options: APIRequestOptions = {}
  ): Promise<Response> {
    // Import authenticatedFetch dynamically to avoid circular dependencies
    const { authenticatedFetch } = await import('../../lib/utils/tokenRefresh');
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'X-Session-Token': this.sessionToken,
      ...(options.headers as Record<string, string>),
    };

    // Add Authorization header
    if (this.sessionToken) {
      headers['Authorization'] = `Bearer ${this.sessionToken}`;
    }

    // Build request body with user context if needed
    let body = options.body;
    if (options.includeUserContext && options.method !== 'GET') {
      try {
        const requestBody = body ? JSON.parse(body as string) : {};
        const userContext = this.buildUserContext(options.userContext);
        requestBody.user_context = userContext;
        body = JSON.stringify(requestBody);
      } catch (error) {
        // If body is not JSON, just add user_context as query param or header
        console.warn('Could not add user_context to request body, body may not be JSON');
      }
    }

    const response = await authenticatedFetch(url, {
      ...options,
      headers,
      body,
      token: this.sessionToken,
    });
    
    return response;
  }

  /**
   * Make a request with consistent error handling
   */
  protected async makeRequest<T = any>(
    endpoint: string,
    options: APIRequestOptions = {}
  ): Promise<APIResponse<T>> {
    try {
      const url = `${this.baseURL}${endpoint}`;
      const response = await this.authenticatedFetch(url, options);

      if (!response.ok) {
        const errorText = await response.text();
        let errorMessage = errorText;
        
        // Try to parse error as JSON
        try {
          const errorJson = JSON.parse(errorText);
          errorMessage = errorJson.error || errorJson.message || errorText;
        } catch {
          // Not JSON, use text as-is
        }

        return {
          success: false,
          error: errorMessage,
          status: response.status,
        };
      }

      const data = await response.json();
      return {
        success: true,
        data,
        status: response.status,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Request failed',
      };
    }
  }

  /**
   * GET request
   */
  protected async get<T = any>(
    endpoint: string,
    options: APIRequestOptions = {}
  ): Promise<APIResponse<T>> {
    return this.makeRequest<T>(endpoint, {
      ...options,
      method: 'GET',
    });
  }

  /**
   * POST request
   */
  protected async post<T = any>(
    endpoint: string,
    body?: any,
    options: APIRequestOptions = {}
  ): Promise<APIResponse<T>> {
    return this.makeRequest<T>(endpoint, {
      ...options,
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
      includeUserContext: true,
    });
  }

  /**
   * PUT request
   */
  protected async put<T = any>(
    endpoint: string,
    body?: any,
    options: APIRequestOptions = {}
  ): Promise<APIResponse<T>> {
    return this.makeRequest<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
      includeUserContext: true,
    });
  }

  /**
   * DELETE request
   */
  protected async delete<T = any>(
    endpoint: string,
    options: APIRequestOptions = {}
  ): Promise<APIResponse<T>> {
    return this.makeRequest<T>(endpoint, {
      ...options,
      method: 'DELETE',
    });
  }

  /**
   * PATCH request
   */
  protected async patch<T = any>(
    endpoint: string,
    body?: any,
    options: APIRequestOptions = {}
  ): Promise<APIResponse<T>> {
    return this.makeRequest<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: body ? JSON.stringify(body) : undefined,
      includeUserContext: true,
    });
  }
}










