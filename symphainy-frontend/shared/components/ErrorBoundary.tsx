/**
 * Error Boundary Component
 * 
 * Provides error catching, error reporting, and recovery mechanisms
 * for React components. Catches JavaScript errors anywhere in the
 * component tree and displays fallback UI.
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { RefreshCw, AlertTriangle, Bug, Home, ArrowLeft } from 'lucide-react';

// ============================================
// Types and Interfaces
// ============================================

export interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  errorId: string | null;
  retryCount: number;
  lastErrorTime: number | null;
}

export interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode | ((error: Error, errorInfo: ErrorInfo, retry: () => void) => ReactNode);
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  onReset?: () => void;
  maxRetries?: number;
  retryDelay?: number;
  showErrorDetails?: boolean;
  errorReporting?: boolean;
  className?: string;
}

export interface ErrorReport {
  errorId: string;
  error: Error;
  errorInfo: ErrorInfo;
  timestamp: number;
  userAgent: string;
  url: string;
  componentStack: string;
  retryCount: number;
}

// ============================================
// Error Boundary Component
// ============================================

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  private retryTimeout: NodeJS.Timeout | null = null;
  private errorReportingService: ErrorReportingService;

  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: null,
      retryCount: 0,
      lastErrorTime: null,
    };
    this.errorReportingService = new ErrorReportingService();
  }

  // ============================================
  // Error Boundary Lifecycle
  // ============================================

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return {
      hasError: true,
      error,
      errorId: ErrorBoundary.generateErrorId(),
      lastErrorTime: Date.now(),
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    const { onError, errorReporting = true } = this.props;
    const { retryCount } = this.state;

    // Update state with error info
    this.setState({
      errorInfo,
      retryCount: retryCount + 1,
    });

    // Call custom error handler
    if (onError) {
      try {
        onError(error, errorInfo);
      } catch (handlerError) {
        console.error('Error in error boundary handler:', handlerError);
      }
    }

    // Report error if enabled
    if (errorReporting) {
      this.reportError(error, errorInfo);
    }

    // Log error for debugging
    console.error('Error Boundary caught an error:', error, errorInfo);
  }

  componentWillUnmount() {
    if (this.retryTimeout) {
      clearTimeout(this.retryTimeout);
    }
  }

  // ============================================
  // Error Recovery Methods
  // ============================================

  resetErrorBoundary = () => {
    const { onReset, maxRetries = 3 } = this.props;
    const { retryCount } = this.state;

    // Check if we've exceeded max retries
    if (retryCount >= maxRetries) {
      this.setState({
        hasError: false,
        error: null,
        errorInfo: null,
        errorId: null,
        retryCount: 0,
        lastErrorTime: null,
      });
      return;
    }

    // Call custom reset handler
    if (onReset) {
      try {
        onReset();
      } catch (resetError) {
        console.error('Error in error boundary reset handler:', resetError);
      }
    }

    // Reset error state
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: null,
    });
  };

  retryWithDelay = () => {
    const { retryDelay = 1000 } = this.props;

    // Clear any existing timeout
    if (this.retryTimeout) {
      clearTimeout(this.retryTimeout);
    }

    // Retry after delay
    this.retryTimeout = setTimeout(() => {
      this.resetErrorBoundary();
    }, retryDelay);
  };

  // ============================================
  // Error Reporting
  // ============================================

  private reportError = async (error: Error, errorInfo: ErrorInfo) => {
    const { errorId, retryCount } = this.state;

    if (!errorId) return;

    const errorReport: ErrorReport = {
      errorId,
      error,
      errorInfo,
      timestamp: Date.now(),
      userAgent: navigator.userAgent,
      url: typeof window !== 'undefined' ? window.location.href : 'unknown',
      componentStack: errorInfo.componentStack,
      retryCount,
    };

    try {
      await this.errorReportingService.reportError(errorReport);
    } catch (reportError) {
      console.error('Failed to report error:', reportError);
    }
  };

  // ============================================
  // Utility Methods
  // ============================================

  private static generateErrorId(): string {
    return `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private getErrorSeverity(): 'low' | 'medium' | 'high' | 'critical' {
    const { error } = this.state;
    if (!error) return 'low';

    // Determine severity based on error type and message
    if (error.name === 'TypeError' || error.name === 'ReferenceError') {
      return 'high';
    }
    if (error.message.includes('Network') || error.message.includes('fetch')) {
      return 'medium';
    }
    if (error.message.includes('Authentication') || error.message.includes('Unauthorized')) {
      return 'critical';
    }
    return 'low';
  }

  private getErrorCategory(): string {
    const { error } = this.state;
    if (!error) return 'Unknown';

    if (error.name === 'TypeError') return 'Type Error';
    if (error.name === 'ReferenceError') return 'Reference Error';
    if (error.name === 'SyntaxError') return 'Syntax Error';
    if (error.message.includes('Network')) return 'Network Error';
    if (error.message.includes('Authentication')) return 'Authentication Error';
    if (error.message.includes('Permission')) return 'Permission Error';
    return 'Runtime Error';
  }

  // ============================================
  // Render Methods
  // ============================================

  render() {
    const { 
      children, 
      fallback, 
      showErrorDetails = false,
      className = '',
    } = this.props;
    const { hasError, error, errorInfo, errorId, retryCount, lastErrorTime } = this.state;

    if (!hasError) {
      return children;
    }

    // Custom fallback
    if (fallback) {
      if (typeof fallback === 'function') {
        return fallback(error!, errorInfo!, this.resetErrorBoundary);
      }
      return fallback;
    }

    // Default error UI
    return (
      <div className={`error-boundary ${className}`}>
        <Card className="max-w-2xl mx-auto mt-8">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              <CardTitle className="text-red-600">Something went wrong</CardTitle>
            </div>
            <CardDescription>
              An unexpected error occurred. We've been notified and are working to fix it.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Error Information */}
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <Badge variant="outline" className="text-xs">
                  {this.getErrorCategory()}
                </Badge>
                <Badge variant={this.getErrorSeverity() === 'critical' ? 'destructive' : 'secondary'} className="text-xs">
                  {this.getErrorSeverity().toUpperCase()}
                </Badge>
                {errorId && (
                  <Badge variant="outline" className="text-xs font-mono">
                    {errorId.slice(-8)}
                  </Badge>
                )}
              </div>
              
              {error && (
                <Alert>
                  <Bug className="h-4 w-4" />
                  <AlertTitle>Error Details</AlertTitle>
                  <AlertDescription className="font-mono text-sm">
                    {error.message}
                  </AlertDescription>
                </Alert>
              )}

              {showErrorDetails && errorInfo && (
                <details className="mt-4">
                  <summary className="cursor-pointer text-sm text-gray-600 hover:text-gray-800">
                    Show technical details
                  </summary>
                  <pre className="mt-2 p-3 bg-gray-100 rounded text-xs overflow-auto max-h-40">
                    {errorInfo.componentStack}
                  </pre>
                </details>
              )}
            </div>

            {/* Error Metadata */}
            <div className="text-xs text-gray-500 space-y-1">
              {lastErrorTime && (
                <div>Time: {new Date(lastErrorTime).toLocaleString()}</div>
              )}
              {retryCount > 0 && (
                <div>Retry attempts: {retryCount}</div>
              )}
              <div>URL: {typeof window !== 'undefined' ? window.location.pathname : 'unknown'}</div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-wrap gap-2 pt-4">
              <Button 
                onClick={this.resetErrorBoundary}
                className="flex items-center space-x-2"
              >
                <RefreshCw className="h-4 w-4" />
                <span>Try Again</span>
              </Button>
              
              <Button 
                variant="outline"
                onClick={() => typeof window !== 'undefined' && window.location.reload()}
                className="flex items-center space-x-2"
              >
                <RefreshCw className="h-4 w-4" />
                <span>Reload Page</span>
              </Button>
              
              <Button 
                variant="outline"
                onClick={() => window.history.back()}
                className="flex items-center space-x-2"
              >
                <ArrowLeft className="h-4 w-4" />
                <span>Go Back</span>
              </Button>
              
              <Button 
                variant="outline"
                onClick={() => typeof window !== 'undefined' && (window.location.href = '/')}
                className="flex items-center space-x-2"
              >
                <Home className="h-4 w-4" />
                <span>Go Home</span>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }
}

// ============================================
// Error Reporting Service
// ============================================

class ErrorReportingService {
  private endpoint: string;
  private enabled: boolean;

  constructor() {
    this.endpoint = process.env.NEXT_PUBLIC_ERROR_REPORTING_ENDPOINT || '/api/errors';
    this.enabled = process.env.NODE_ENV === 'production' || process.env.NEXT_PUBLIC_ENABLE_ERROR_REPORTING === 'true';
  }

  async reportError(errorReport: ErrorReport): Promise<void> {
    if (!this.enabled) {
      console.log('Error reporting disabled, error report:', errorReport);
      return;
    }

    try {
      const response = await fetch(this.endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(errorReport),
      });

      if (!response.ok) {
        throw new Error(`Error reporting failed: ${response.status}`);
      }
    } catch (error) {
      console.error('Failed to report error:', error);
      // Don't throw - error reporting failure shouldn't break the app
    }
  }
}

// ============================================
// Higher-Order Component
// ============================================

export function withErrorBoundary<P extends object>(
  Component: React.ComponentType<P>,
  errorBoundaryProps?: Omit<ErrorBoundaryProps, 'children'>
) {
  const WrappedComponent = (props: P) => (
    <ErrorBoundary {...errorBoundaryProps}>
      <Component {...props} />
    </ErrorBoundary>
  );

  WrappedComponent.displayName = `withErrorBoundary(${Component.displayName || Component.name})`;
  return WrappedComponent;
}

// ============================================
// Hook for Error Boundary Context
// ============================================

export function useErrorBoundary() {
  const [error, setError] = React.useState<Error | null>(null);

  const throwError = React.useCallback((error: Error) => {
    setError(error);
  }, []);

  const clearError = React.useCallback(() => {
    setError(null);
  }, []);

  return {
    error,
    throwError,
    clearError,
  };
} 