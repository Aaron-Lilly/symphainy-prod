/**
 * Error Handling Test Suite
 * 
 * Tests the error handling system including:
 * - Error boundary component
 * - Error handling hooks
 * - Error recovery components
 * - Error utilities and reporting
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, renderHook, act } from '@testing-library/react';
import { 
  ErrorBoundary, 
  ErrorRecovery, 
  NetworkErrorRecovery, 
  AuthErrorRecovery, 
  ValidationErrorRecovery,
  withErrorBoundary,
} from '../shared/components/ErrorBoundary';
import { 
  useErrorHandler, 
  useAsyncError, 
  useServiceError,
  useNetworkError,
  useAuthError,
  useValidationError,
  ErrorUtils,
} from '../shared/hooks/useErrorHandler';
import { SessionProvider } from '../shared/components/SessionProvider';

// Mock fetch for error reporting
global.fetch = jest.fn();

// Test wrapper component
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <SessionProvider autoInitialize={false}>
    {children}
  </SessionProvider>
);

// Component that throws an error for testing
const ThrowError: React.FC<{ shouldThrow: boolean }> = ({ shouldThrow }) => {
  if (shouldThrow) {
    throw new Error('Test error');
  }
  return <div>No error</div>;
};

describe('Error Handling System', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  describe('Error Boundary Component', () => {
    it('should catch errors and display fallback UI', () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(screen.getByText('Something went wrong')).toBeInTheDocument();
      expect(screen.getByText('Try Again')).toBeInTheDocument();
      expect(screen.getByText('Reload Page')).toBeInTheDocument();

      consoleSpy.mockRestore();
    });

    it('should not display fallback UI when no error occurs', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={false} />
        </ErrorBoundary>
      );

      expect(screen.getByText('No error')).toBeInTheDocument();
      expect(screen.queryByText('Something went wrong')).not.toBeInTheDocument();
    });

    it('should call custom error handler', () => {
      const onError = jest.fn();
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

      render(
        <ErrorBoundary onError={onError}>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(onError).toHaveBeenCalledWith(
        expect.any(Error),
        expect.objectContaining({
          componentStack: expect.any(String),
        })
      );

      consoleSpy.mockRestore();
    });

    it('should reset error state when retry button is clicked', () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

      const { rerender } = render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(screen.getByText('Something went wrong')).toBeInTheDocument();

      // Click retry button
      fireEvent.click(screen.getByText('Try Again'));

      // Re-render with no error
      rerender(
        <ErrorBoundary>
          <ThrowError shouldThrow={false} />
        </ErrorBoundary>
      );

      expect(screen.getByText('No error')).toBeInTheDocument();

      consoleSpy.mockRestore();
    });

    it('should show technical details when enabled', () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

      render(
        <ErrorBoundary showErrorDetails={true}>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(screen.getByText('Show technical details')).toBeInTheDocument();

      consoleSpy.mockRestore();
    });

    it('should handle custom fallback component', () => {
      const CustomFallback = ({ error, retry }: { error: Error; retry: () => void }) => (
        <div>
          <h1>Custom Error UI</h1>
          <p>{error.message}</p>
          <button onClick={retry}>Custom Retry</button>
        </div>
      );

      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

      render(
        <ErrorBoundary fallback={CustomFallback}>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(screen.getByText('Custom Error UI')).toBeInTheDocument();
      expect(screen.getByText('Test error')).toBeInTheDocument();
      expect(screen.getByText('Custom Retry')).toBeInTheDocument();

      consoleSpy.mockRestore();
    });
  });

  describe('Error Handling Hooks', () => {
    describe('useErrorHandler', () => {
      it('should handle errors and provide error state', () => {
        const { result } = renderHook(() => useErrorHandler());

        act(() => {
          result.current.handleError(new Error('Test error'));
        });

        expect(result.current.errorState.hasError).toBe(true);
        expect(result.current.errorState.error).toBeInstanceOf(Error);
        expect(result.current.errorState.error?.message).toBe('Test error');
        expect(result.current.errorState.errorId).toBeDefined();
      });

      it('should clear errors', () => {
        const { result } = renderHook(() => useErrorHandler());

        act(() => {
          result.current.handleError(new Error('Test error'));
        });

        expect(result.current.errorState.hasError).toBe(true);

        act(() => {
          result.current.clearError();
        });

        expect(result.current.errorState.hasError).toBe(false);
        expect(result.current.errorState.error).toBeNull();
      });

      it('should retry with delay', () => {
        const { result } = renderHook(() => useErrorHandler({ retryDelay: 1000 }));

        act(() => {
          result.current.handleError(new Error('Test error'));
        });

        expect(result.current.errorState.hasError).toBe(true);

        act(() => {
          result.current.retry();
        });

        expect(result.current.errorState.isRetrying).toBe(true);

        // Fast-forward time
        act(() => {
          jest.advanceTimersByTime(1000);
        });

        expect(result.current.errorState.hasError).toBe(false);
      });

      it('should respect max retries', () => {
        const { result } = renderHook(() => useErrorHandler({ maxRetries: 2 }));

        act(() => {
          result.current.handleError(new Error('Test error'));
        });

        expect(result.current.errorState.retryCount).toBe(1);

        act(() => {
          result.current.retry();
        });

        expect(result.current.errorState.retryCount).toBe(2);

        act(() => {
          result.current.retry();
        });

        // Should not increment beyond max retries
        expect(result.current.errorState.retryCount).toBe(2);
      });

      it('should call custom error handler', () => {
        const onError = jest.fn();
        const { result } = renderHook(() => useErrorHandler({ onError }));

        act(() => {
          result.current.handleError(new Error('Test error'));
        });

        expect(onError).toHaveBeenCalledWith(expect.any(Error));
      });
    });

    describe('useAsyncError', () => {
      it('should execute async functions and handle errors', async () => {
        const { result } = renderHook(() => useAsyncError());

        // Test successful execution
        const successResult = await act(async () => {
          return await result.current.execute(async () => 'success');
        });

        expect(successResult).toBe('success');
        expect(result.current.errorState.hasError).toBe(false);

        // Test error execution
        const errorResult = await act(async () => {
          return await result.current.execute(async () => {
            throw new Error('Async error');
          });
        });

        expect(errorResult).toBe(null);
        expect(result.current.errorState.hasError).toBe(true);
        expect(result.current.errorState.error?.message).toBe('Async error');
      });
    });

    describe('useServiceError', () => {
      it('should handle service errors', () => {
        const { result } = renderHook(() => useServiceError(), {
          wrapper: TestWrapper,
        });

        act(() => {
          result.current.handleServiceError(new Error('Service error'));
        });

        expect(result.current.errorState.hasError).toBe(true);
        expect(result.current.errorState.error?.message).toBe('Service error');
      });

      it('should handle string errors', () => {
        const { result } = renderHook(() => useServiceError(), {
          wrapper: TestWrapper,
        });

        act(() => {
          result.current.handleServiceError('String error');
        });

        expect(result.current.errorState.hasError).toBe(true);
        expect(result.current.errorState.error?.message).toBe('String error');
      });

      it('should handle error objects with status', () => {
        const { result } = renderHook(() => useServiceError(), {
          wrapper: TestWrapper,
        });

        act(() => {
          result.current.handleServiceError({ 
            message: 'HTTP error', 
            status: 404,
            code: 'NOT_FOUND'
          });
        });

        expect(result.current.errorState.hasError).toBe(true);
        expect(result.current.errorState.error?.message).toBe('HTTP error');
        expect(result.current.errorState.error?.name).toBe('NOT_FOUND');
      });
    });

    describe('Convenience Hooks', () => {
      it('should provide network error handling', () => {
        const { result } = renderHook(() => useNetworkError());

        expect(result.current.errorState.hasError).toBe(false);
        expect(result.current.isRetryable).toBeDefined();
      });

      it('should provide auth error handling', () => {
        const { result } = renderHook(() => useAuthError());

        expect(result.current.errorState.hasError).toBe(false);
        expect(result.current.getErrorSeverity).toBeDefined();
      });

      it('should provide validation error handling', () => {
        const { result } = renderHook(() => useValidationError());

        expect(result.current.errorState.hasError).toBe(false);
        expect(result.current.getErrorMessage).toBeDefined();
      });
    });
  });

  describe('Error Recovery Components', () => {
    it('should render generic error recovery', () => {
      const error = new Error('Test error');
      
      render(
        <ErrorRecovery 
          error={error}
          onRetry={() => {}}
          onGoBack={() => {}}
          onGoHome={() => {}}
        />
      );

      expect(screen.getByText('Something went wrong')).toBeInTheDocument();
      expect(screen.getByText('Try Again')).toBeInTheDocument();
      expect(screen.getByText('Go Back')).toBeInTheDocument();
      expect(screen.getByText('Go Home')).toBeInTheDocument();
    });

    it('should render network error recovery', () => {
      const error = new Error('Network error');
      
      render(
        <NetworkErrorRecovery 
          error={error}
          onRetry={() => {}}
          onCheckConnection={() => {}}
        />
      );

      expect(screen.getByText('Network Connection Error')).toBeInTheDocument();
      expect(screen.getByText('Retry Connection')).toBeInTheDocument();
      expect(screen.getByText('Check Connection')).toBeInTheDocument();
    });

    it('should render auth error recovery', () => {
      const error = new Error('Authentication required');
      
      render(
        <AuthErrorRecovery 
          error={error}
          onLogin={() => {}}
          onRefreshToken={() => {}}
        />
      );

      expect(screen.getByText('Authentication Required')).toBeInTheDocument();
      expect(screen.getByText('Sign In')).toBeInTheDocument();
      expect(screen.getByText('Refresh Session')).toBeInTheDocument();
    });

    it('should render validation error recovery', () => {
      const error = new Error('Invalid input');
      
      render(
        <ValidationErrorRecovery 
          error={error}
          field="email"
          onFixInput={() => {}}
          onClearForm={() => {}}
        />
      );

      expect(screen.getByText('Validation Error')).toBeInTheDocument();
      expect(screen.getByText('Fix Input')).toBeInTheDocument();
      expect(screen.getByText('Clear Form')).toBeInTheDocument();
    });

    it('should handle retry actions', () => {
      const onRetry = jest.fn();
      const error = new Error('Test error');
      
      render(
        <ErrorRecovery 
          error={error}
          onRetry={onRetry}
        />
      );

      fireEvent.click(screen.getByText('Try Again'));
      expect(onRetry).toHaveBeenCalled();
    });

    it('should handle navigation actions', () => {
      const onGoBack = jest.fn();
      const onGoHome = jest.fn();
      const error = new Error('Test error');
      
      render(
        <ErrorRecovery 
          error={error}
          onGoBack={onGoBack}
          onGoHome={onGoHome}
        />
      );

      fireEvent.click(screen.getByText('Go Back'));
      expect(onGoBack).toHaveBeenCalled();

      fireEvent.click(screen.getByText('Go Home'));
      expect(onGoHome).toHaveBeenCalled();
    });
  });

  describe('Error Utilities', () => {
    describe('ErrorUtils', () => {
      it('should generate error IDs', () => {
        const errorId1 = ErrorUtils.generateErrorId();
        const errorId2 = ErrorUtils.generateErrorId();

        expect(errorId1).toMatch(/^error_\d+_[a-z0-9]+$/);
        expect(errorId2).toMatch(/^error_\d+_[a-z0-9]+$/);
        expect(errorId1).not.toBe(errorId2);
      });

      it('should identify retryable errors', () => {
        expect(ErrorUtils.isRetryable(new Error('Network error'))).toBe(true);
        expect(ErrorUtils.isRetryable(new Error('timeout error'))).toBe(true);
        expect(ErrorUtils.isRetryable(new Error('503 Service Unavailable'))).toBe(true);
        expect(ErrorUtils.isRetryable(new Error('429 Rate Limit'))).toBe(true);
        expect(ErrorUtils.isRetryable(new Error('Connection refused'))).toBe(true);
        expect(ErrorUtils.isRetryable(new Error('Validation error'))).toBe(false);
      });

      it('should get user-friendly error messages', () => {
        expect(ErrorUtils.getErrorMessage(new Error('Network error'))).toBe(
          'Network error. Please check your connection and try again.'
        );
        expect(ErrorUtils.getErrorMessage(new Error('401 Unauthorized'))).toBe(
          'Authentication required. Please log in and try again.'
        );
        expect(ErrorUtils.getErrorMessage(new Error('404 Not Found'))).toBe(
          'Resource not found. Please check the URL and try again.'
        );
        expect(ErrorUtils.getErrorMessage(new Error('500 Internal Server Error'))).toBe(
          'Server error. Please try again later.'
        );
      });

      it('should determine error severity', () => {
        expect(ErrorUtils.getErrorSeverity(new Error('401 Unauthorized'))).toBe('critical');
        expect(ErrorUtils.getErrorSeverity(new Error('403 Forbidden'))).toBe('critical');
        expect(ErrorUtils.getErrorSeverity(new Error('TypeError'))).toBe('high');
        expect(ErrorUtils.getErrorSeverity(new Error('Network error'))).toBe('medium');
        expect(ErrorUtils.getErrorSeverity(new Error('404 Not Found'))).toBe('medium');
        expect(ErrorUtils.getErrorSeverity(new Error('Unknown error'))).toBe('low');
      });

      it('should determine if errors should be reported', () => {
        expect(ErrorUtils.shouldReportError(new Error('Network error'))).toBe(true);
        expect(ErrorUtils.shouldReportError(new Error('User cancelled'))).toBe(false);
        expect(ErrorUtils.shouldReportError(new Error('Expected error'))).toBe(false);
        expect(ErrorUtils.shouldReportError(new Error('Handled error'))).toBe(false);
      });
    });
  });

  describe('Higher-Order Component', () => {
    it('should wrap component with error boundary', () => {
      const WrappedComponent = withErrorBoundary(ThrowError);
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

      render(<WrappedComponent shouldThrow={true} />);

      expect(screen.getByText('Something went wrong')).toBeInTheDocument();

      consoleSpy.mockRestore();
    });

    it('should pass through props to wrapped component', () => {
      const WrappedComponent = withErrorBoundary(ThrowError);

      render(<WrappedComponent shouldThrow={false} />);

      expect(screen.getByText('No error')).toBeInTheDocument();
    });
  });

  describe('Error Reporting', () => {
    it('should report errors when enabled', async () => {
      const mockFetch = fetch as jest.MockedFunction<typeof fetch>;
      mockFetch.mockResolvedValueOnce({ ok: true } as Response);

      // Set environment to enable error reporting
      const originalEnv = process.env.NEXT_PUBLIC_ENABLE_ERROR_REPORTING;
      process.env.NEXT_PUBLIC_ENABLE_ERROR_REPORTING = 'true';

      const { result } = renderHook(() => useErrorHandler({ errorReporting: true }));

      act(() => {
        result.current.handleError(new Error('Test error'));
      });

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/errors'),
          expect.objectContaining({
            method: 'POST',
            headers: expect.objectContaining({
              'Content-Type': 'application/json',
            }),
            body: expect.stringContaining('Test error'),
          })
        );
      });

      // Restore environment
      process.env.NEXT_PUBLIC_ENABLE_ERROR_REPORTING = originalEnv;
    });

    it('should not report errors when disabled', () => {
      const mockFetch = fetch as jest.MockedFunction<typeof fetch>;

      const { result } = renderHook(() => useErrorHandler({ errorReporting: false }));

      act(() => {
        result.current.handleError(new Error('Test error'));
      });

      expect(mockFetch).not.toHaveBeenCalled();
    });
  });
}); 