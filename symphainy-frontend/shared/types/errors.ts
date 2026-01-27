/**
 * Error Signal Taxonomy
 * 
 * Phase 6: Error Handling Standardization
 * 
 * All errors in the platform are represented as error signals, not exceptions.
 * Error signals flow through the system and are handled by appropriate handlers.
 */

export type ErrorType = 
  | 'SessionError'
  | 'AgentError'
  | 'AGUIError'
  | 'ToolError'
  | 'NetworkError';

/**
 * Base error signal interface
 * 
 * All errors in the platform follow this structure.
 */
export interface ErrorSignal {
  /** Error type from taxonomy */
  type: ErrorType;
  
  /** Machine-readable error code */
  code: string;
  
  /** Human-readable error message */
  message: string;
  
  /** Additional error details (optional) */
  details?: any;
  
  /** Timestamp when error occurred */
  timestamp: number;
  
  /** Whether error can be recovered from */
  recoverable: boolean;
  
  /** Whether error can be retried */
  retryable?: boolean;
  
  /** Additional context about the error */
  context?: Record<string, any>;
}

/**
 * SessionError - Session management, authentication, session invalidation
 * 
 * Handled by: SessionBoundaryProvider
 * Display: Session status UI, redirect to login if needed
 * Recovery: Automatic session recovery or user re-authentication
 */
export interface SessionError extends ErrorSignal {
  type: 'SessionError';
  
  /** Current session status */
  sessionStatus?: string;
  
  /** Whether authentication is required */
  requiresAuth?: boolean;
  
  /** Session token if available */
  sessionToken?: string;
}

/**
 * AgentError - Agent/LLM responses, agent failures, reasoning errors
 * 
 * Handled by: Agent components (chatbot, guide agent)
 * Display: User-friendly message with context, reasoning if available
 * Recovery: Retry, switch agent, or provide alternative
 */
export interface AgentError extends ErrorSignal {
  type: 'AgentError';
  
  /** Type of agent that generated the error */
  agentType?: string;
  
  /** Agent reasoning/explanation if available */
  reasoning?: string;
  
  /** Agent response if partial */
  partialResponse?: string;
}

/**
 * AGUIError - AGUI validation, state errors, intent compilation failures
 * 
 * Handled by: AGUIStateProvider or AGUI components
 * Display: Validation messages, state error indicators
 * Recovery: Fix validation issues, reset AGUI state
 */
export interface AGUIError extends ErrorSignal {
  type: 'AGUIError';
  
  /** Validation errors if applicable */
  validationErrors?: string[];
  
  /** Intent ID if applicable */
  intentId?: string;
  
  /** AGUI state snapshot if available */
  aguiState?: any;
}

/**
 * ToolError - Tool execution failures, capability unavailable
 * 
 * Handled by: Tool execution components
 * Display: "Capability unavailable" message, alternative suggestions
 * Recovery: Use alternative tool, wait for capability availability
 */
export interface ToolError extends ErrorSignal {
  type: 'ToolError';
  
  /** Name of the tool that failed */
  toolName?: string;
  
  /** Alternative tools that could be used */
  alternativeTools?: string[];
  
  /** Tool execution context */
  toolContext?: Record<string, any>;
}

/**
 * NetworkError - Network failures, timeouts, connection issues
 * 
 * Handled by: Service layer, WebSocket connections
 * Display: Connection status, retry prompts
 * Recovery: Automatic retry with backoff, manual retry option
 */
export interface NetworkError extends ErrorSignal {
  type: 'NetworkError';
  
  /** HTTP status code if applicable */
  statusCode?: number;
  
  /** Retry after this many seconds */
  retryAfter?: number;
  
  /** Whether this is a timeout */
  isTimeout?: boolean;
  
  /** Original network error if available */
  originalError?: any;
}

/**
 * Type guard to check if an error is an ErrorSignal
 */
export function isErrorSignal(error: any): error is ErrorSignal {
  return (
    error &&
    typeof error === 'object' &&
    'type' in error &&
    'code' in error &&
    'message' in error &&
    'timestamp' in error &&
    'recoverable' in error &&
    typeof error.type === 'string' &&
    typeof error.code === 'string' &&
    typeof error.message === 'string' &&
    typeof error.timestamp === 'number' &&
    typeof error.recoverable === 'boolean'
  );
}

/**
 * Type guard for specific error types
 */
export function isSessionError(error: ErrorSignal): error is SessionError {
  return error.type === 'SessionError';
}

export function isAgentError(error: ErrorSignal): error is AgentError {
  return error.type === 'AgentError';
}

export function isAGUIError(error: ErrorSignal): error is AGUIError {
  return error.type === 'AGUIError';
}

export function isToolError(error: ErrorSignal): error is ToolError {
  return error.type === 'ToolError';
}

export function isNetworkError(error: ErrorSignal): error is NetworkError {
  return error.type === 'NetworkError';
}
