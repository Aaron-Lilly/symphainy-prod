/**
 * Error Display Component
 * 
 * Phase 6: Error Handling Standardization
 * 
 * Displays error signals in a user-friendly way with recovery actions.
 */

"use client";

import React from 'react';
import { ErrorSignal, SessionError, AgentError, AGUIError, ToolError, NetworkError } from '@/shared/types/errors';
import { getErrorDisplayMessage, getRecoveryAction, shouldRetry } from '@/shared/utils/errorSignals';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { AlertTriangle, RefreshCw, X, LogIn, Wrench } from 'lucide-react';

interface ErrorDisplayProps {
  error: ErrorSignal | null;
  onRetry?: () => void | Promise<void>;
  onDismiss?: () => void;
  onAlternative?: () => void;
  className?: string;
  showDetails?: boolean;
}

export function ErrorDisplay({
  error,
  onRetry,
  onDismiss,
  onAlternative,
  className = '',
  showDetails = false,
}: ErrorDisplayProps) {
  if (!error) {
    return null;
  }

  const displayMessage = getErrorDisplayMessage(error);
  const recoveryAction = getRecoveryAction(error, onRetry, onAlternative);
  const canRetry = shouldRetry(error);

  // Get error-specific icon and variant
  const { icon, variant } = getErrorIconAndVariant(error);

  return (
    <Alert variant={variant} className={className}>
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 mt-0.5">{icon}</div>
        <div className="flex-1 min-w-0">
          <AlertTitle className="flex items-center justify-between gap-2">
            <span>{getErrorTitle(error)}</span>
            {onDismiss && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onDismiss}
                className="h-6 w-6 p-0"
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </AlertTitle>
          <AlertDescription className="mt-2">
            <p className="text-sm">{displayMessage}</p>
            
            {/* Error-specific details */}
            {showDetails && (
              <div className="mt-3 space-y-2">
                {error.type === 'AgentError' && (error as AgentError).reasoning && (
                  <div className="text-xs text-muted-foreground">
                    <strong>Reasoning:</strong> {(error as AgentError).reasoning}
                  </div>
                )}
                
                {error.type === 'AGUIError' && (error as AGUIError).validationErrors && (
                  <div className="text-xs text-muted-foreground">
                    <strong>Validation Errors:</strong>
                    <ul className="list-disc list-inside mt-1">
                      {(error as AGUIError).validationErrors!.map((err, i) => (
                        <li key={i}>{err}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {error.type === 'ToolError' && (error as ToolError).alternativeTools && (
                  <div className="text-xs text-muted-foreground">
                    <strong>Alternative Tools:</strong>{' '}
                    {(error as ToolError).alternativeTools!.join(', ')}
                  </div>
                )}
                
                {error.type === 'NetworkError' && (error as NetworkError).statusCode && (
                  <div className="text-xs text-muted-foreground">
                    <strong>Status Code:</strong> {(error as NetworkError).statusCode}
                  </div>
                )}
              </div>
            )}

            {/* Recovery actions */}
            {recoveryAction && (
              <div className="mt-3 flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={recoveryAction.action}
                >
                  {recoveryAction.label}
                </Button>
                {canRetry && onRetry && recoveryAction.label !== 'Retry' && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={onRetry}
                  >
                    <RefreshCw className="h-4 w-4 mr-1" />
                    Retry
                  </Button>
                )}
              </div>
            )}
          </AlertDescription>
        </div>
      </div>
    </Alert>
  );
}

function getErrorIconAndVariant(error: ErrorSignal): { icon: React.ReactNode; variant: 'default' | 'destructive' } {
  switch (error.type) {
    case 'SessionError':
      return {
        icon: <LogIn className="h-4 w-4" />,
        variant: 'default' as const,
      };
    case 'AgentError':
      return {
        icon: <AlertTriangle className="h-4 w-4" />,
        variant: 'default' as const,
      };
    case 'AGUIError':
      return {
        icon: <Wrench className="h-4 w-4" />,
        variant: 'default' as const,
      };
    case 'ToolError':
      return {
        icon: <Wrench className="h-4 w-4" />,
        variant: 'default' as const,
      };
    case 'NetworkError':
      return {
        icon: <AlertTriangle className="h-4 w-4" />,
        variant: 'destructive' as const,
      };
    default:
      return {
        icon: <AlertTriangle className="h-4 w-4" />,
        variant: 'destructive' as const,
      };
  }
}

function getErrorTitle(error: ErrorSignal): string {
  switch (error.type) {
    case 'SessionError':
      return 'Session Error';
    case 'AgentError':
      return 'Agent Error';
    case 'AGUIError':
      return 'Interface Error';
    case 'ToolError':
      return 'Tool Error';
    case 'NetworkError':
      return 'Network Error';
    default:
      return 'Error';
  }
}

/**
 * Inline error display for smaller contexts
 */
export function InlineErrorDisplay({
  error,
  onRetry,
  className = '',
}: {
  error: ErrorSignal | null;
  onRetry?: () => void | Promise<void>;
  className?: string;
}) {
  if (!error) {
    return null;
  }

  const displayMessage = getErrorDisplayMessage(error);
  const canRetry = shouldRetry(error);

  return (
    <div className={`text-sm text-destructive flex items-center gap-2 ${className}`}>
      <AlertTriangle className="h-4 w-4 flex-shrink-0" />
      <span className="flex-1">{displayMessage}</span>
      {canRetry && onRetry && (
        <Button
          variant="ghost"
          size="sm"
          onClick={onRetry}
          className="h-6 px-2"
        >
          <RefreshCw className="h-3 w-3 mr-1" />
          Retry
        </Button>
      )}
    </div>
  );
}
