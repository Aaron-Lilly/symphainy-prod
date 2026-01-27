/**
 * Service Wrapper Utility
 * 
 * Phase 6: Error Handling Standardization
 * 
 * Wraps service calls to return { data, error } pattern instead of throwing exceptions.
 */

import { ErrorSignal } from '../types/errors';
import { errorToSignal, createNetworkError } from './errorSignals';

/**
 * Service result type - all services should return this pattern
 */
export interface ServiceResult<T> {
  data: T | null;
  error: ErrorSignal | null;
}

/**
 * Wrap a service call to return { data, error } pattern
 * 
 * @param serviceCall - The service function to wrap
 * @returns Promise<ServiceResult<T>>
 * 
 * @example
 * ```typescript
 * const result = await wrapServiceCall(() => myService.getData());
 * if (result.error) {
 *   // Handle error
 * } else {
 *   // Use result.data
 * }
 * ```
 */
export async function wrapServiceCall<T>(
  serviceCall: () => Promise<T>
): Promise<ServiceResult<T>> {
  try {
    const data = await serviceCall();
    return { data, error: null };
  } catch (error: unknown) {
    const errorSignal = errorToSignal(error);
    return { data: null, error: errorSignal };
  }
}

/**
 * Wrap a service call with custom error handling
 * 
 * @param serviceCall - The service function to wrap
 * @param errorHandler - Optional custom error handler
 * @returns Promise<ServiceResult<T>>
 */
export async function wrapServiceCallWithHandler<T>(
  serviceCall: () => Promise<T>,
  errorHandler?: (error: unknown) => ErrorSignal
): Promise<ServiceResult<T>> {
  try {
    const data = await serviceCall();
    return { data, error: null };
  } catch (error: unknown) {
    const errorSignal = errorHandler ? errorHandler(error) : errorToSignal(error);
    return { data: null, error: errorSignal };
  }
}

/**
 * Wrap a fetch call to return { data, error } pattern
 * 
 * @param fetchCall - The fetch function to wrap
 * @returns Promise<ServiceResult<T>>
 */
export async function wrapFetchCall<T>(
  fetchCall: () => Promise<Response>
): Promise<ServiceResult<T>> {
  try {
    const response = await fetchCall();
    
    if (!response.ok) {
      // Try to parse error response
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      let errorDetails: any = null;
      
      try {
        const errorText = await response.text();
        try {
          errorDetails = JSON.parse(errorText);
          errorMessage = errorDetails.detail || errorDetails.message || errorDetails.error || errorMessage;
        } catch {
          errorMessage = errorText || errorMessage;
        }
      } catch {
        // Couldn't read response body
      }
      
      const networkError = createNetworkError(
        `HTTP_${response.status}`,
        errorMessage,
        {
          statusCode: response.status,
          originalError: errorDetails,
          retryable: response.status >= 500 || response.status === 429,
        }
      );
      
      return { data: null, error: networkError };
    }
    
    // Parse successful response
    const contentType = response.headers.get('content-type');
    let data: T;
    
    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      const text = await response.text();
      data = text as unknown as T;
    }
    
    return { data, error: null };
  } catch (error: unknown) {
    const errorSignal = errorToSignal(error);
    return { data: null, error: errorSignal };
  }
}
