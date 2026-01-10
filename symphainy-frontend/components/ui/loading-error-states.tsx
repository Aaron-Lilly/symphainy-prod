import * as React from 'react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Loader2, AlertCircle, CheckCircle, XCircle, RefreshCw } from 'lucide-react';
import { LoadingState, OperationsError } from '@/shared/types/operations';

// Loading Component with Progress
interface LoadingProps {
  state: LoadingState;
  onCancel?: () => void;
}

export function LoadingIndicator({ state, onCancel }: LoadingProps) {
  const { isLoading, operation, progress, message } = state;

  if (!isLoading) return null;

  const getOperationDisplayName = (op?: string) => {
    switch (op) {
      case 'sop_to_workflow': return 'Converting SOP to Workflow';
      case 'workflow_to_sop': return 'Converting Workflow to SOP';
      case 'coexistence_analysis': return 'Analyzing Coexistence';
      case 'roadmap_analysis': return 'Analyzing File for Roadmap';
      default: return 'Processing';
    }
  };

  return (
    <div className="flex flex-col items-center justify-center p-6 space-y-4 bg-blue-50 rounded-lg border border-blue-200">
      <div className="flex items-center space-x-3">
        <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
        <div className="text-center">
          <h3 className="text-lg font-semibold text-blue-900">
            {getOperationDisplayName(operation)}
          </h3>
          {message && (
            <p className="text-sm text-blue-700 mt-1">{message}</p>
          )}
        </div>
      </div>
      
      {progress !== undefined && (
        <div className="w-full max-w-md">
          <div className="flex justify-between text-sm text-blue-700 mb-1">
            <span>Progress</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div className="w-full bg-blue-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}
      
      {onCancel && (
        <Button
          variant="outline"
          size="sm"
          onClick={onCancel}
          className="text-blue-700 border-blue-300 hover:bg-blue-100"
        >
          Cancel
        </Button>
      )}
    </div>
  );
}

// Error Display Component
interface ErrorDisplayProps {
  error: OperationsError | null;
  onRetry?: () => void;
  onDismiss?: () => void;
  showDetails?: boolean;
}

export function ErrorDisplay({ error, onRetry, onDismiss, showDetails = false }: ErrorDisplayProps) {
  if (!error) return null;

  const getErrorIcon = (code?: string) => {
    switch (code) {
      case '401':
      case '403':
        return <XCircle className="h-5 w-5 text-red-600" />;
      case '404':
        return <AlertCircle className="h-5 w-5 text-orange-600" />;
      case '422':
        return <AlertCircle className="h-5 w-5 text-yellow-600" />;
      default:
        return <AlertCircle className="h-5 w-5 text-red-600" />;
    }
  };

  const getErrorVariant = (code?: string): "default" | "destructive" => {
    switch (code) {
      case '401':
      case '403':
      case '500':
      case '502':
      case '503':
      case '504':
        return 'destructive';
      default:
        return 'default';
    }
  };

  return (
    <Alert variant={getErrorVariant(error.code)} className="mb-4">
      <div className="flex items-start space-x-3">
        {getErrorIcon(error.code)}
        <div className="flex-1">
          <AlertTitle className="flex items-center justify-between">
            <span>Operation Failed</span>
            {onDismiss && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onDismiss}
                className="h-6 w-6 p-0 hover:bg-transparent"
              >
                ×
              </Button>
            )}
          </AlertTitle>
          <AlertDescription className="mt-2">
            <p className="text-sm">{error.message}</p>
            
            {showDetails && error.details && (
              <details className="mt-3">
                <summary className="text-xs cursor-pointer hover:text-foreground/80">
                  Technical Details
                </summary>
                <pre className="mt-2 text-xs bg-muted p-2 rounded overflow-auto">
                  {JSON.stringify(error.details, null, 2)}
                </pre>
              </details>
            )}
            
            {onRetry && (
              <div className="mt-3 flex space-x-2">
                <Button
                  size="sm"
                  onClick={onRetry}
                  className="flex items-center space-x-1"
                >
                  <RefreshCw className="h-3 w-3" />
                  <span>Try Again</span>
                </Button>
              </div>
            )}
          </AlertDescription>
        </div>
      </div>
    </Alert>
  );
}

// Success Display Component
interface SuccessDisplayProps {
  message: string;
  onDismiss?: () => void;
  showIcon?: boolean;
}

export function SuccessDisplay({ message, onDismiss, showIcon = true }: SuccessDisplayProps) {
  return (
    <Alert className="mb-4 border-green-200 bg-green-50">
      <div className="flex items-start space-x-3">
        {showIcon && <CheckCircle className="h-5 w-5 text-green-600" />}
        <div className="flex-1">
          <AlertTitle className="flex items-center justify-between">
            <span>Success</span>
            {onDismiss && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onDismiss}
                className="h-6 w-6 p-0 hover:bg-transparent"
              >
                ×
              </Button>
            )}
          </AlertTitle>
          <AlertDescription className="mt-1 text-green-800">
            {message}
          </AlertDescription>
        </div>
      </div>
    </Alert>
  );
}

// Combined State Handler
interface StateHandlerProps {
  loading: LoadingState;
  error: OperationsError | null;
  success?: string;
  onRetry?: () => void;
  onDismissError?: () => void;
  onDismissSuccess?: () => void;
  onCancel?: () => void;
  showErrorDetails?: boolean;
}

export function StateHandler({
  loading,
  error,
  success,
  onRetry,
  onDismissError,
  onDismissSuccess,
  onCancel,
  showErrorDetails = false
}: StateHandlerProps) {
  return (
    <div className="space-y-4">
      {loading.isLoading && (
        <LoadingIndicator state={loading} onCancel={onCancel} />
      )}
      
      {error && (
        <ErrorDisplay
          error={error}
          onRetry={onRetry}
          onDismiss={onDismissError}
          showDetails={showErrorDetails}
        />
      )}
      
      {success && !loading.isLoading && (
        <SuccessDisplay
          message={success}
          onDismiss={onDismissSuccess}
        />
      )}
    </div>
  );
}

// Inline Loading Spinner
interface InlineLoadingProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
}

export function InlineLoading({ size = 'md', text }: InlineLoadingProps) {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8'
  };

  return (
    <div className="flex items-center space-x-2">
      <Loader2 className={`${sizeClasses[size]} animate-spin`} />
      {text && <span className="text-sm text-muted-foreground">{text}</span>}
    </div>
  );
}

// Skeleton Loading
interface SkeletonProps {
  className?: string;
  lines?: number;
}

export function Skeleton({ className = "h-4", lines = 1 }: SkeletonProps) {
  return (
    <div className="space-y-2">
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className={`${className} bg-gray-200 rounded animate-pulse`}
        />
      ))}
    </div>
  );
} 