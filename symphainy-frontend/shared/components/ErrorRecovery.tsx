/**
 * Error Recovery Components
 * 
 * Provides user-friendly error recovery mechanisms and fallback UI
 * for different types of errors and recovery scenarios.
 */

import React from 'react';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  RefreshCw, 
  AlertTriangle, 
  Wifi, 
  Shield, 
  FileText, 
  Home, 
  ArrowLeft,
  Settings,
  HelpCircle,
  ExternalLink,
} from 'lucide-react';
import { useErrorHandler, ErrorUtils } from '../hooks/useErrorHandler';

// ============================================
// Types and Interfaces
// ============================================

export interface ErrorRecoveryProps {
  error: Error;
  errorId?: string;
  retryCount?: number;
  onRetry?: () => void;
  onGoBack?: () => void;
  onGoHome?: () => void;
  onRefresh?: () => void;
  onContactSupport?: () => void;
  showTechnicalDetails?: boolean;
  className?: string;
}

export interface NetworkErrorProps extends ErrorRecoveryProps {
  onCheckConnection?: () => void;
  onTryAlternativeEndpoint?: () => void;
}

export interface AuthErrorProps extends ErrorRecoveryProps {
  onLogin?: () => void;
  onRefreshToken?: () => void;
}

export interface ValidationErrorProps extends ErrorRecoveryProps {
  field?: string;
  onFixInput?: () => void;
  onClearForm?: () => void;
}

// ============================================
// Generic Error Recovery Component
// ============================================

export function ErrorRecovery({
  error,
  errorId,
  retryCount = 0,
  onRetry,
  onGoBack,
  onGoHome,
  onRefresh,
  onContactSupport,
  showTechnicalDetails = false,
  className = '',
}: ErrorRecoveryProps) {
  const severity = ErrorUtils.getErrorSeverity(error);
  const isRetryable = ErrorUtils.isRetryable(error);
  const errorMessage = ErrorUtils.getErrorMessage(error);

  const getSeverityColor = () => {
    switch (severity) {
      case 'critical': return 'destructive';
      case 'high': return 'destructive';
      case 'medium': return 'default';
      case 'low': return 'secondary';
      default: return 'secondary';
    }
  };

  const getSeverityIcon = () => {
    switch (severity) {
      case 'critical':
      case 'high':
        return <AlertTriangle className="h-5 w-5 text-red-500" />;
      case 'medium':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      case 'low':
        return <HelpCircle className="h-5 w-5 text-blue-500" />;
      default:
        return <AlertTriangle className="h-5 w-5 text-gray-500" />;
    }
  };

  return (
    <div className={`error-recovery ${className}`}>
      <Card className="max-w-2xl mx-auto">
        <CardHeader>
          <div className="flex items-center space-x-2">
            {getSeverityIcon()}
            <CardTitle className="text-gray-900">Something went wrong</CardTitle>
          </div>
          <CardDescription>
            {errorMessage}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Error Information */}
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <Badge variant={getSeverityColor()} className="text-xs">
                {severity.toUpperCase()}
              </Badge>
              {isRetryable && (
                <Badge variant="outline" className="text-xs">
                  RETRYABLE
                </Badge>
              )}
              {errorId && (
                <Badge variant="outline" className="text-xs font-mono">
                  {errorId.slice(-8)}
                </Badge>
              )}
              {retryCount > 0 && (
                <Badge variant="outline" className="text-xs">
                  RETRY {retryCount}
                </Badge>
              )}
            </div>

            {showTechnicalDetails && (
              <details className="mt-4">
                <summary className="cursor-pointer text-sm text-gray-600 hover:text-gray-800">
                  Show technical details
                </summary>
                <pre className="mt-2 p-3 bg-gray-100 rounded text-xs overflow-auto max-h-40">
                  {error.stack}
                </pre>
              </details>
            )}
          </div>

          {/* Recovery Actions */}
          <div className="flex flex-wrap gap-2">
            {isRetryable && onRetry && (
              <Button 
                onClick={onRetry}
                className="flex items-center space-x-2"
              >
                <RefreshCw className="h-4 w-4" />
                <span>Try Again</span>
              </Button>
            )}
            
            {onRefresh && (
              <Button 
                variant="outline"
                onClick={onRefresh}
                className="flex items-center space-x-2"
              >
                <RefreshCw className="h-4 w-4" />
                <span>Refresh Page</span>
              </Button>
            )}
            
            {onGoBack && (
              <Button 
                variant="outline"
                onClick={onGoBack}
                className="flex items-center space-x-2"
              >
                <ArrowLeft className="h-4 w-4" />
                <span>Go Back</span>
              </Button>
            )}
            
            {onGoHome && (
              <Button 
                variant="outline"
                onClick={onGoHome}
                className="flex items-center space-x-2"
              >
                <Home className="h-4 w-4" />
                <span>Go Home</span>
              </Button>
            )}
            
            {onContactSupport && (
              <Button 
                variant="outline"
                onClick={onContactSupport}
                className="flex items-center space-x-2"
              >
                <HelpCircle className="h-4 w-4" />
                <span>Contact Support</span>
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// ============================================
// Network Error Recovery Component
// ============================================

export function NetworkErrorRecovery({
  error,
  onRetry,
  onCheckConnection,
  onTryAlternativeEndpoint,
  onRefresh,
  onGoBack,
  onGoHome,
  ...props
}: NetworkErrorProps) {
  return (
    <div className="network-error-recovery">
      <Card className="max-w-2xl mx-auto">
        <CardHeader>
          <div className="flex items-center space-x-2">
            <Wifi className="h-5 w-5 text-red-500" />
            <CardTitle className="text-red-600">Network Connection Error</CardTitle>
          </div>
          <CardDescription>
            Unable to connect to the server. Please check your internet connection and try again.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Connection Status */}
          <Alert>
            <Wifi className="h-4 w-4" />
            <AlertTitle>Connection Status</AlertTitle>
            <AlertDescription>
              Your device appears to be offline or unable to reach our servers.
            </AlertDescription>
          </Alert>

          {/* Recovery Actions */}
          <div className="flex flex-wrap gap-2">
            {onRetry && (
              <Button 
                onClick={onRetry}
                className="flex items-center space-x-2"
              >
                <RefreshCw className="h-4 w-4" />
                <span>Retry Connection</span>
              </Button>
            )}
            
            {onCheckConnection && (
              <Button 
                variant="outline"
                onClick={onCheckConnection}
                className="flex items-center space-x-2"
              >
                <Wifi className="h-4 w-4" />
                <span>Check Connection</span>
              </Button>
            )}
            
            {onTryAlternativeEndpoint && (
              <Button 
                variant="outline"
                onClick={onTryAlternativeEndpoint}
                className="flex items-center space-x-2"
              >
                <Settings className="h-4 w-4" />
                <span>Try Alternative Server</span>
              </Button>
            )}
            
            {onRefresh && (
              <Button 
                variant="outline"
                onClick={onRefresh}
                className="flex items-center space-x-2"
              >
                <RefreshCw className="h-4 w-4" />
                <span>Refresh Page</span>
              </Button>
            )}
            
            {onGoBack && (
              <Button 
                variant="outline"
                onClick={onGoBack}
                className="flex items-center space-x-2"
              >
                <ArrowLeft className="h-4 w-4" />
                <span>Go Back</span>
              </Button>
            )}
            
            {onGoHome && (
              <Button 
                variant="outline"
                onClick={onGoHome}
                className="flex items-center space-x-2"
              >
                <Home className="h-4 w-4" />
                <span>Go Home</span>
              </Button>
            )}
          </div>

          {/* Troubleshooting Tips */}
          <div className="mt-4 p-4 bg-blue-50 rounded-lg">
            <h4 className="font-medium text-blue-900 mb-2">Troubleshooting Tips:</h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Check your internet connection</li>
              <li>• Try refreshing the page</li>
              <li>• Check if our servers are online</li>
              <li>• Try using a different network</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// ============================================
// Authentication Error Recovery Component
// ============================================

export function AuthErrorRecovery({
  error,
  onRetry,
  onLogin,
  onRefreshToken,
  onGoBack,
  onGoHome,
  ...props
}: AuthErrorProps) {
  return (
    <div className="auth-error-recovery">
      <Card className="max-w-2xl mx-auto">
        <CardHeader>
          <div className="flex items-center space-x-2">
            <Shield className="h-5 w-5 text-red-500" />
            <CardTitle className="text-red-600">Authentication Required</CardTitle>
          </div>
          <CardDescription>
            You need to be logged in to access this resource. Please sign in and try again.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Authentication Status */}
          <Alert>
            <Shield className="h-4 w-4" />
            <AlertTitle>Authentication Status</AlertTitle>
            <AlertDescription>
              Your session has expired or you don't have permission to access this resource.
            </AlertDescription>
          </Alert>

          {/* Recovery Actions */}
          <div className="flex flex-wrap gap-2">
            {onLogin && (
              <Button 
                onClick={onLogin}
                className="flex items-center space-x-2"
              >
                <Shield className="h-4 w-4" />
                <span>Sign In</span>
              </Button>
            )}
            
            {onRefreshToken && (
              <Button 
                variant="outline"
                onClick={onRefreshToken}
                className="flex items-center space-x-2"
              >
                <RefreshCw className="h-4 w-4" />
                <span>Refresh Session</span>
              </Button>
            )}
            
            {onRetry && (
              <Button 
                variant="outline"
                onClick={onRetry}
                className="flex items-center space-x-2"
              >
                <RefreshCw className="h-4 w-4" />
                <span>Try Again</span>
              </Button>
            )}
            
            {onGoBack && (
              <Button 
                variant="outline"
                onClick={onGoBack}
                className="flex items-center space-x-2"
              >
                <ArrowLeft className="h-4 w-4" />
                <span>Go Back</span>
              </Button>
            )}
            
            {onGoHome && (
              <Button 
                variant="outline"
                onClick={onGoHome}
                className="flex items-center space-x-2"
              >
                <Home className="h-4 w-4" />
                <span>Go Home</span>
              </Button>
            )}
          </div>

          {/* Help Information */}
          <div className="mt-4 p-4 bg-yellow-50 rounded-lg">
            <h4 className="font-medium text-yellow-900 mb-2">Need Help?</h4>
            <p className="text-sm text-yellow-800 mb-2">
              If you're having trouble signing in, you can:
            </p>
            <ul className="text-sm text-yellow-800 space-y-1">
              <li>• Reset your password</li>
              <li>• Contact support for account issues</li>
              <li>• Check if your account is active</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// ============================================
// Validation Error Recovery Component
// ============================================

export function ValidationErrorRecovery({
  error,
  field,
  onRetry,
  onFixInput,
  onClearForm,
  onGoBack,
  ...props
}: ValidationErrorProps) {
  return (
    <div className="validation-error-recovery">
      <Card className="max-w-2xl mx-auto">
        <CardHeader>
          <div className="flex items-center space-x-2">
            <FileText className="h-5 w-5 text-yellow-500" />
            <CardTitle className="text-yellow-600">Validation Error</CardTitle>
          </div>
          <CardDescription>
            There's an issue with the information you provided. Please check and fix the errors.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Error Details */}
          <Alert>
            <FileText className="h-4 w-4" />
            <AlertTitle>Validation Issue</AlertTitle>
            <AlertDescription>
              {field ? `Error in field "${field}": ${error.message}` : error.message}
            </AlertDescription>
          </Alert>

          {/* Recovery Actions */}
          <div className="flex flex-wrap gap-2">
            {onFixInput && (
              <Button 
                onClick={onFixInput}
                className="flex items-center space-x-2"
              >
                <FileText className="h-4 w-4" />
                <span>Fix Input</span>
              </Button>
            )}
            
            {onClearForm && (
              <Button 
                variant="outline"
                onClick={onClearForm}
                className="flex items-center space-x-2"
              >
                <RefreshCw className="h-4 w-4" />
                <span>Clear Form</span>
              </Button>
            )}
            
            {onRetry && (
              <Button 
                variant="outline"
                onClick={onRetry}
                className="flex items-center space-x-2"
              >
                <RefreshCw className="h-4 w-4" />
                <span>Try Again</span>
              </Button>
            )}
            
            {onGoBack && (
              <Button 
                variant="outline"
                onClick={onGoBack}
                className="flex items-center space-x-2"
              >
                <ArrowLeft className="h-4 w-4" />
                <span>Go Back</span>
              </Button>
            )}
          </div>

          {/* Validation Tips */}
          <div className="mt-4 p-4 bg-green-50 rounded-lg">
            <h4 className="font-medium text-green-900 mb-2">Validation Tips:</h4>
            <ul className="text-sm text-green-800 space-y-1">
              <li>• Check that all required fields are filled</li>
              <li>• Ensure email addresses are valid</li>
              <li>• Verify that passwords meet requirements</li>
              <li>• Check for special characters in text fields</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// ============================================
// Error Recovery Hook
// ============================================

export function useErrorRecovery() {
  const { errorState, handleError, clearError, retry } = useErrorHandler();

  const handleNetworkError = (error: Error) => {
    handleError(error);
  };

  const handleAuthError = (error: Error) => {
    handleError(error);
  };

  const handleValidationError = (error: Error) => {
    handleError(error);
  };

  const goBack = () => {
    window.history.back();
  };

  const goHome = () => {
    if (typeof window !== 'undefined') window.location.href = '/';
  };

  const refresh = () => {
    if (typeof window !== 'undefined') window.location.reload();
  };

  const contactSupport = () => {
    // Open support contact form or redirect to support page
    window.open('/support', '_blank');
  };

  return {
    errorState,
    handleNetworkError,
    handleAuthError,
    handleValidationError,
    clearError,
    retry,
    goBack,
    goHome,
    refresh,
    contactSupport,
  };
} 