/**
 * API Service
 * 
 * Provides standardized API requests with error handling, retry logic,
 * and session integration. Uses unified configuration management.
 */

// useSessionContext will be passed as parameter instead of imported
import { getGlobalConfig, UnifiedConfig } from '../config';

// ============================================
// Types and Interfaces
// ============================================

export interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  headers?: Record<string, string>;
  body?: any;
  timeout?: number;
  retries?: number;
  retryDelay?: number;
  requireAuth?: boolean;
}

export interface APIResponse<T = any> {
  data: T;
  status: number;
  statusText: string;
  headers: Record<string, string>;
  success: boolean;
  error?: string;
  retryCount?: number;
}

export interface APIError {
  message: string;
  status?: number;
  code?: string;
  details?: any;
  retryable: boolean;
}

// ============================================
// API Service Class
// ============================================

export class APIService {
  private config = getGlobalConfig();

  // ============================================
  // Core Request Method
  // ============================================

  async request<T = any>(
    endpoint: string,
    options: RequestOptions = {}
  ): Promise<APIResponse<T>> {
    const apiConfig = this.config.getSection('api');
    const {
      method = 'GET',
      headers = {},
      body,
      timeout = apiConfig.timeout,
      retries = apiConfig.maxRetries,
      retryDelay = apiConfig.retryDelay,
      requireAuth = true,
    } = options;

    let lastError: APIError | null = null;
    let retryCount = 0;

    while (retryCount <= retries) {
      try {
        const response = await this.makeRequest<T>(endpoint, {
          method,
          headers,
          body,
          timeout,
          requireAuth,
        });

        return response;
      } catch (error) {
        lastError = this.handleError(error);
        
        if (!lastError.retryable || retryCount >= retries) {
          break;
        }

        retryCount++;
        await this.delay(retryDelay * retryCount);
      }
    }

    throw lastError || new Error('Request failed');
  }

  // ============================================
  // Convenience Methods
  // ============================================

  async get<T = any>(endpoint: string, options: Omit<RequestOptions, 'method'> = {}): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'GET' });
  }

  async post<T = any>(endpoint: string, body?: any, options: Omit<RequestOptions, 'method' | 'body'> = {}): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'POST', body });
  }

  async put<T = any>(endpoint: string, body?: any, options: Omit<RequestOptions, 'method' | 'body'> = {}): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'PUT', body });
  }

  async delete<T = any>(endpoint: string, options: Omit<RequestOptions, 'method'> = {}): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' });
  }

  async patch<T = any>(endpoint: string, body?: any, options: Omit<RequestOptions, 'method' | 'body'> = {}): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'PATCH', body });
  }

  // ============================================
  // Private Methods
  // ============================================

  private async makeRequest<T>(
    endpoint: string,
    options: {
      method: string;
      headers: Record<string, string>;
      body?: any;
      timeout: number;
      requireAuth: boolean;
    }
  ): Promise<APIResponse<T>> {
    const apiConfig = this.config.getSection('api');
    const url = `${apiConfig.baseURL}${endpoint}`;
    
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    const requestOptions: RequestInit = {
      method: options.method,
      headers,
      body: options.body ? JSON.stringify(options.body) : undefined,
    };

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), options.timeout);

    try {
      const response = await fetch(url, {
        ...requestOptions,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      const data = await this.parseResponse<T>(response);
      const responseHeaders = this.parseHeaders(response.headers);

      return {
        data,
        status: response.status,
        statusText: response.statusText,
        headers: responseHeaders,
        success: response.ok,
      };
    } catch (error) {
      clearTimeout(timeoutId);
      throw error;
    }
  }

  private async parseResponse<T>(response: Response): Promise<T> {
    const contentType = response.headers.get('content-type');
    
    if (contentType?.includes('application/json')) {
      return response.json();
    }
    
    if (contentType?.includes('text/')) {
      return response.text() as T;
    }
    
    return response.blob() as T;
  }

  private parseHeaders(headers: Headers): Record<string, string> {
    const result: Record<string, string> = {};
    headers.forEach((value, key) => {
      result[key] = value;
    });
    return result;
  }

  private handleError(error: any): APIError {
    if (error.name === 'AbortError') {
      return {
        message: 'Request timeout',
        code: 'TIMEOUT',
        retryable: true,
      };
    }

    if (error instanceof Response) {
      return this.createHTTPError(error, {});
    }

    return {
      message: error.message || 'Unknown error',
      code: 'UNKNOWN',
      retryable: false,
    };
  }

  private createHTTPError(response: Response, data: any): APIError {
    return {
      message: data.message || response.statusText,
      status: response.status,
      code: data.code || `HTTP_${response.status}`,
      details: data,
      retryable: this.isRetryableStatus(response.status),
    };
  }

  private isRetryableStatus(status: number): boolean {
    return status >= 500 || status === 429;
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// ============================================
// Global API Service Instance
// ============================================

const globalAPIService = new APIService();

// Export as apiService for backward compatibility
export const apiService = globalAPIService;

// ============================================
// Hook for API Service
// ============================================

// useAPIService hook removed to avoid React import issues

// ============================================
// Convenience Functions
// ============================================

export async function apiGet<T = any>(endpoint: string, options?: Omit<RequestOptions, 'method'>): Promise<APIResponse<T>> {
  return globalAPIService.get<T>(endpoint, options);
}

export async function apiPost<T = any>(endpoint: string, body?: any, options?: Omit<RequestOptions, 'method' | 'body'>): Promise<APIResponse<T>> {
  return globalAPIService.post<T>(endpoint, body, options);
}

export async function apiPut<T = any>(endpoint: string, body?: any, options?: Omit<RequestOptions, 'method' | 'body'>): Promise<APIResponse<T>> {
  return globalAPIService.put<T>(endpoint, body, options);
}

export async function apiDelete<T = any>(endpoint: string, options?: Omit<RequestOptions, 'method'>): Promise<APIResponse<T>> {
  return globalAPIService.delete<T>(endpoint, options);
}

export async function apiPatch<T = any>(endpoint: string, body?: any, options?: Omit<RequestOptions, 'method' | 'body'>): Promise<APIResponse<T>> {
  return globalAPIService.patch<T>(endpoint, body, options);
} 