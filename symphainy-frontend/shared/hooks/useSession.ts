/**
 * Unified Session Management Hook
 * 
 * This hook provides a single source of truth for all session-related state
 * across the application. It consolidates global session, pillar-specific sessions,
 * and chatbot state into a unified interface with automatic synchronization.
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { atom, useAtom, useAtomValue } from 'jotai';
import { getSessionElements, clearSessionElements } from '@/lib/api/operations';

// ============================================
// Session Types and Interfaces
// ============================================

export interface SessionState {
  // Global session state
  globalToken: string | null;
  isAuthenticated: boolean;
  
  // Pillar-specific session state
  has_sop: boolean;
  has_workflow: boolean;
  section2_complete: boolean;
  
  // Chatbot session state
  chatbotOpen: boolean;
  chatbotAgentInfo: {
    title: string;
    agent: string;
    file_url: string;
    additional_info: string;
  };
  
  // Session metadata
  lastActivity: Date | null;
  sessionStartTime: Date | null;
  isValid: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface SessionElements {
  sop: any;
  workflow: any;
}

export interface SessionAction {
  action: string;
  missing?: string;
}

export interface UseSessionReturn {
  // Session state
  sessionState: SessionState;
  sessionElements: SessionElements | null;
  sessionAction: SessionAction;
  
  // Session operations
  initializeSession: (token: string) => Promise<void>;
  refreshSession: () => Promise<void>;
  clearSession: () => Promise<void>;
  updateSessionState: (updates: Partial<SessionState>) => void;
  
  // Chatbot operations
  setChatbotOpen: (open: boolean) => void;
  setChatbotAgentInfo: (info: SessionState['chatbotAgentInfo']) => void;
  
  // Utility functions
  isSessionValid: () => boolean;
  getSessionAge: () => number; // in minutes
  updateLastActivity: () => void;
}

// ============================================
// Jotai Atoms for Global Session State
// ============================================

// Main session atom - single source of truth
export const sessionAtom = atom<SessionState>({
  globalToken: null,
  isAuthenticated: false,
  has_sop: false,
  has_workflow: false,
  section2_complete: false,
  chatbotOpen: true,
  chatbotAgentInfo: {
    title: "",
    agent: "",
    file_url: "",
    additional_info: "",
  },
  lastActivity: null,
  sessionStartTime: null,
  isValid: false,
  isLoading: false,
  error: null,
});

// Derived atoms for specific session aspects
export const globalSessionAtom = atom(
  (get) => ({
    token: get(sessionAtom).globalToken,
    isAuthenticated: get(sessionAtom).isAuthenticated,
  }),
  (get, set, update: { token?: string | null; isAuthenticated?: boolean }) => {
    const current = get(sessionAtom);
    set(sessionAtom, {
      ...current,
      globalToken: update.token ?? current.globalToken,
      isAuthenticated: update.isAuthenticated ?? current.isAuthenticated,
    });
  }
);

export const pillarSessionAtom = atom(
  (get) => ({
    has_sop: get(sessionAtom).has_sop,
    has_workflow: get(sessionAtom).has_workflow,
    section2_complete: get(sessionAtom).section2_complete,
  }),
  (get, set, update: Partial<Pick<SessionState, 'has_sop' | 'has_workflow' | 'section2_complete'>>) => {
    const current = get(sessionAtom);
    set(sessionAtom, {
      ...current,
      ...update,
    });
  }
);

export const chatbotSessionAtom = atom(
  (get) => ({
    chatbotOpen: get(sessionAtom).chatbotOpen,
    chatbotAgentInfo: get(sessionAtom).chatbotAgentInfo,
  }),
  (get, set, update: Partial<Pick<SessionState, 'chatbotOpen' | 'chatbotAgentInfo'>>) => {
    const current = get(sessionAtom);
    set(sessionAtom, {
      ...current,
      ...update,
    });
  }
);

// ============================================
// Session Management Hook
// ============================================

export function useSession(): UseSessionReturn {
  const [sessionState, setSessionState] = useAtom(sessionAtom);
  const [sessionElements, setSessionElements] = useState<SessionElements | null>(null);
  const [sessionAction, setSessionAction] = useState<SessionAction>({
    action: 'redirect_to_section1',
  });
  
  // Refs for tracking async operations
  const refreshTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const activityTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // ============================================
  // Session Operations
  // ============================================

  const initializeSession = useCallback(async (token: string) => {
    if (!token) {
      setSessionState(prev => ({
        ...prev,
        error: 'No session token provided',
        isLoading: false,
      }));
      return;
    }

    setSessionState(prev => ({
      ...prev,
      globalToken: token,
      isAuthenticated: true,
      sessionStartTime: new Date(),
      lastActivity: new Date(),
      isLoading: true,
      error: null,
    }));

    try {
      // Fetch initial session elements
      const result = await getSessionElements(token);
      
      setSessionState(prev => ({
        ...prev,
        has_sop: result.session_state.has_sop,
        has_workflow: result.session_state.has_workflow,
        section2_complete: result.session_state.section2_complete,
        isValid: result.valid,
        isLoading: false,
      }));

      setSessionElements(result.elements || null);
      setSessionAction({
        action: result.action,
        missing: result.missing,
      });

      // Set up automatic session refresh
      setupSessionRefresh();
      
      // Set up activity tracking
      setupActivityTracking();

      console.log('Session initialized successfully:', result);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to initialize session';
      setSessionState(prev => ({
        ...prev,
        error: errorMessage,
        isLoading: false,
        isValid: false,
      }));
      console.error('Error initializing session:', err);
    }
  }, [setSessionState]);

  const refreshSession = useCallback(async () => {
    if (!sessionState.globalToken) {
      setSessionState(prev => ({
        ...prev,
        error: 'No session token available for refresh',
      }));
      return;
    }

    setSessionState(prev => ({
      ...prev,
      isLoading: true,
      error: null,
    }));

    try {
      const result = await getSessionElements(sessionState.globalToken);
      
      setSessionState(prev => ({
        ...prev,
        has_sop: result.session_state.has_sop,
        has_workflow: result.session_state.has_workflow,
        section2_complete: result.session_state.section2_complete,
        isValid: result.valid,
        isLoading: false,
        lastActivity: new Date(),
      }));

      setSessionElements(result.elements || null);
      setSessionAction({
        action: result.action,
        missing: result.missing,
      });

      console.log('Session refreshed successfully:', result);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to refresh session';
      setSessionState(prev => ({
        ...prev,
        error: errorMessage,
        isLoading: false,
      }));
      console.error('Error refreshing session:', err);
    }
  }, [sessionState.globalToken, setSessionState]);

  const clearSession = useCallback(async () => {
    if (!sessionState.globalToken) {
      return;
    }

    setSessionState(prev => ({
      ...prev,
      isLoading: true,
      error: null,
    }));

    try {
      await clearSessionElements(sessionState.globalToken);
      
      // Clear all session state
      setSessionState({
        globalToken: null,
        isAuthenticated: false,
        has_sop: false,
        has_workflow: false,
        section2_complete: false,
        chatbotOpen: true,
        chatbotAgentInfo: {
          title: "",
          agent: "",
          file_url: "",
          additional_info: "",
        },
        lastActivity: null,
        sessionStartTime: null,
        isValid: false,
        isLoading: false,
        error: null,
      });

      setSessionElements(null);
      setSessionAction({
        action: 'redirect_to_section1',
      });

      // Clear timeouts
      if (refreshTimeoutRef.current) {
        clearTimeout(refreshTimeoutRef.current);
        refreshTimeoutRef.current = null;
      }
      if (activityTimeoutRef.current) {
        clearTimeout(activityTimeoutRef.current);
        activityTimeoutRef.current = null;
      }

      console.log('Session cleared successfully');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to clear session';
      setSessionState(prev => ({
        ...prev,
        error: errorMessage,
        isLoading: false,
      }));
      console.error('Error clearing session:', err);
    }
  }, [sessionState.globalToken, setSessionState]);

  const updateSessionState = useCallback((updates: Partial<SessionState>) => {
    setSessionState(prev => ({
      ...prev,
      ...updates,
      lastActivity: new Date(),
    }));
  }, [setSessionState]);

  // ============================================
  // Chatbot Operations
  // ============================================

  const setChatbotOpen = useCallback((open: boolean) => {
    setSessionState(prev => ({
      ...prev,
      chatbotOpen: open,
      lastActivity: new Date(),
    }));
  }, [setSessionState]);

  const setChatbotAgentInfo = useCallback((info: SessionState['chatbotAgentInfo']) => {
    setSessionState(prev => ({
      ...prev,
      chatbotAgentInfo: info,
      lastActivity: new Date(),
    }));
  }, [setSessionState]);

  // ============================================
  // Utility Functions
  // ============================================

  const isSessionValid = useCallback(() => {
    return sessionState.isValid && sessionState.isAuthenticated && !!sessionState.globalToken;
  }, [sessionState.isValid, sessionState.isAuthenticated, sessionState.globalToken]);

  const getSessionAge = useCallback(() => {
    if (!sessionState.sessionStartTime) return 0;
    const now = new Date();
    const diffMs = now.getTime() - sessionState.sessionStartTime.getTime();
    return Math.floor(diffMs / (1000 * 60)); // Convert to minutes
  }, [sessionState.sessionStartTime]);

  const updateLastActivity = useCallback(() => {
    setSessionState(prev => ({
      ...prev,
      lastActivity: new Date(),
    }));
  }, [setSessionState]);

  // ============================================
  // Automatic Session Management
  // ============================================

  const setupSessionRefresh = useCallback(() => {
    // Refresh session every 5 minutes
    if (refreshTimeoutRef.current) {
      clearTimeout(refreshTimeoutRef.current);
    }
    
    refreshTimeoutRef.current = setTimeout(() => {
      refreshSession();
      setupSessionRefresh(); // Set up next refresh
    }, 5 * 60 * 1000); // 5 minutes
  }, [refreshSession]);

  const setupActivityTracking = useCallback(() => {
    // Update last activity on user interactions
    const handleActivity = () => {
      updateLastActivity();
    };

    // Track various user activities
    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];
    events.forEach(event => {
      document.addEventListener(event, handleActivity, { passive: true });
    });

    // Cleanup function
    return () => {
      events.forEach(event => {
        document.removeEventListener(event, handleActivity);
      });
    };
  }, [updateLastActivity]);

  // ============================================
  // Effect Hooks
  // ============================================

  // Set up activity tracking on mount
  useEffect(() => {
    if (sessionState.isAuthenticated) {
      const cleanup = setupActivityTracking();
      return cleanup;
    }
  }, [sessionState.isAuthenticated, setupActivityTracking]);

  // Cleanup timeouts on unmount
  useEffect(() => {
    return () => {
      if (refreshTimeoutRef.current) {
        clearTimeout(refreshTimeoutRef.current);
      }
      if (activityTimeoutRef.current) {
        clearTimeout(activityTimeoutRef.current);
      }
    };
  }, []);

  // ============================================
  // Return Interface
  // ============================================

  return {
    // Session state
    sessionState,
    sessionElements,
    sessionAction,
    
    // Session operations
    initializeSession,
    refreshSession,
    clearSession,
    updateSessionState,
    
    // Chatbot operations
    setChatbotOpen,
    setChatbotAgentInfo,
    
    // Utility functions
    isSessionValid,
    getSessionAge,
    updateLastActivity,
  };
}

// ============================================
// Convenience Hooks for Specific Use Cases
// ============================================

export function useGlobalSession() {
  const [globalSession, setGlobalSession] = useAtom(globalSessionAtom);
  return { globalSession, setGlobalSession };
}

export function usePillarSession() {
  const [pillarSession, setPillarSession] = useAtom(pillarSessionAtom);
  return { pillarSession, setPillarSession };
}

export function useChatbotSession() {
  const [chatbotSession, setChatbotSession] = useAtom(chatbotSessionAtom);
  return { chatbotSession, setChatbotSession };
}

export function useSessionState() {
  return useAtomValue(sessionAtom);
} 