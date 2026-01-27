/**
 * Session Provider Component
 * 
 * Provides unified session management to the entire application.
 * Handles session initialization, cleanup, and provides session context.
 */

import React, { createContext, useContext, useEffect, ReactNode } from 'react';
import { useSession, SessionState, UseSessionReturn } from '../hooks/useSession';

// ============================================
// Session Context
// ============================================

interface SessionContextType extends UseSessionReturn {
  // Additional context-specific methods
  isInitialized: boolean;
  isSessionExpired: boolean;
}

const SessionContext = createContext<SessionContextType | null>(null);

// ============================================
// Session Provider Component
// ============================================

interface SessionProviderProps {
  children: ReactNode;
  initialToken?: string | null;
  autoInitialize?: boolean;
  sessionTimeoutMinutes?: number;
}

export function SessionProvider({
  children,
  initialToken = null,
  autoInitialize = true,
  sessionTimeoutMinutes = 30,
}: SessionProviderProps) {
  const session = useSession();
  const [isInitialized, setIsInitialized] = React.useState(false);

  // ============================================
  // Session Initialization
  // ============================================

  useEffect(() => {
    if (autoInitialize && initialToken && !session.sessionState.isAuthenticated) {
      session.initializeSession(initialToken)
        .then(() => {
          setIsInitialized(true);
          console.log('Session auto-initialized with token');
        })
        .catch((error) => {
          console.error('Failed to auto-initialize session:', error);
          setIsInitialized(true); // Mark as initialized even if failed
        });
    } else {
      setIsInitialized(true);
    }
  }, [autoInitialize, initialToken, session]);

  // ============================================
  // Session Expiration Check
  // ============================================

  const isSessionExpired = React.useMemo(() => {
    if (!session.sessionState.lastActivity) return false;
    
    const now = new Date();
    const lastActivity = session.sessionState.lastActivity;
    const diffMs = now.getTime() - lastActivity.getTime();
    const diffMinutes = diffMs / (1000 * 60);
    
    return diffMinutes > sessionTimeoutMinutes;
  }, [session.sessionState.lastActivity, sessionTimeoutMinutes]);

  // ============================================
  // Session Expiration Handling
  // ============================================

  useEffect(() => {
    if (isSessionExpired && session.sessionState.isAuthenticated) {
      console.warn('Session expired due to inactivity');
      
      // Clear the session
      session.clearSession()
        .then(() => {
          console.log('Expired session cleared');
          // Optionally redirect to login or show session expired message
        })
        .catch((error) => {
          console.error('Failed to clear expired session:', error);
        });
    }
  }, [isSessionExpired, session]);

  // ============================================
  // Context Value
  // ============================================

  const contextValue: SessionContextType = {
    ...session,
    isInitialized,
    isSessionExpired,
  };

  // ============================================
  // Loading State
  // ============================================

  if (!isInitialized) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Initializing session...</p>
        </div>
      </div>
    );
  }

  // ============================================
  // Session Expired State
  // ============================================

  if (isSessionExpired && session.sessionState.isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="text-red-600 mb-4">
            <svg className="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Session Expired</h2>
          <p className="text-gray-600 mb-4">Your session has expired due to inactivity.</p>
          <button
            onClick={() => typeof window !== 'undefined' && window.location.reload()}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            Refresh Page
          </button>
        </div>
      </div>
    );
  }

  // ============================================
  // Error State
  // ============================================

  if (session.sessionState.error && session.sessionState.isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="text-red-600 mb-4">
            <svg className="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Session Error</h2>
          <p className="text-gray-600 mb-4">{session.sessionState.error}</p>
          <div className="space-x-2">
            <button
              onClick={() => session.refreshSession()}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
            >
              Retry
            </button>
            <button
              onClick={() => session.clearSession()}
              className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
            >
              Clear Session
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ============================================
  // Main Render
  // ============================================

  return (
    <SessionContext.Provider value={contextValue}>
      {children}
    </SessionContext.Provider>
  );
}

// ============================================
// Session Hook
// ============================================

export function useSessionContext(): SessionContextType {
  const context = useContext(SessionContext);
  if (!context) {
    throw new Error('useSessionContext must be used within a SessionProvider');
  }
  return context;
}

// ============================================
// Session Status Component
// ============================================

interface SessionStatusProps {
  showDetails?: boolean;
  className?: string;
}

export function SessionStatus({ showDetails = false, className = '' }: SessionStatusProps) {
  const session = useSessionContext();

  if (!session.sessionState.isAuthenticated) {
    return (
      <div className={`text-sm text-gray-500 ${className}`}>
        Not authenticated
      </div>
    );
  }

  return (
    <div className={`text-sm ${className}`}>
      <div className="flex items-center space-x-2">
        <div className={`w-2 h-2 rounded-full ${session.isSessionValid() ? 'bg-green-500' : 'bg-red-500'}`}></div>
        <span className={session.isSessionValid() ? 'text-green-600' : 'text-red-600'}>
          {session.isSessionValid() ? 'Active' : 'Invalid'}
        </span>
      </div>
      
      {showDetails && (
        <div className="mt-1 text-xs text-gray-500">
          <div>Session age: {session.getSessionAge()} minutes</div>
          <div>Last activity: {session.sessionState.lastActivity?.toLocaleTimeString()}</div>
          {session.sessionState.isLoading && <div>Loading...</div>}
        </div>
      )}
    </div>
  );
}

// ============================================
// Session Debug Component (Development Only)
// ============================================

export function SessionDebug() {
  const session = useSessionContext();

  if (process.env.NODE_ENV !== 'development') {
    return null;
  }

  return (
    <div className="fixed bottom-4 right-4 bg-black bg-opacity-75 text-white p-4 rounded text-xs max-w-sm">
      <h3 className="font-semibold mb-2">Session Debug</h3>
      <pre className="whitespace-pre-wrap">
        {JSON.stringify({
          isAuthenticated: session.sessionState.isAuthenticated,
          isValid: session.sessionState.isValid,
          isLoading: session.sessionState.isLoading,
          hasError: !!session.sessionState.error,
          sessionAge: session.getSessionAge(),
          lastActivity: session.sessionState.lastActivity?.toISOString(),
          chatbotOpen: session.sessionState.chatbotOpen,
          hasSop: session.sessionState.has_sop,
          hasWorkflow: session.sessionState.has_workflow,
        }, null, 2)}
      </pre>
    </div>
  );
} 