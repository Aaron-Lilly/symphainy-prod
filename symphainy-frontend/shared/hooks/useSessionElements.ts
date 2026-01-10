import React, { useState, useEffect, useCallback } from 'react';
import { getSessionElements, clearSessionElements } from '@/lib/api/operations';

interface SessionState {
  has_sop: boolean;
  has_workflow: boolean;
  section2_complete: boolean;
}

interface SessionElements {
  sop: any;
  workflow: any;
}

interface UseSessionElementsReturn {
  sessionState: SessionState;
  sessionElements: SessionElements | null;
  isValid: boolean;
  action: string;
  missing?: string;
  isLoading: boolean;
  error: string | null;
  refreshSession: () => Promise<void>;
  clearSession: () => Promise<void>;
}

export function useSessionElements(sessionToken: string | null): UseSessionElementsReturn {
  const [sessionState, setSessionState] = useState<SessionState>({
    has_sop: false,
    has_workflow: false,
    section2_complete: false,
  });
  const [sessionElements, setSessionElements] = useState<SessionElements | null>(null);
  const [isValid, setIsValid] = useState(false);
  const [action, setAction] = useState('redirect_to_section1');
  const [missing, setMissing] = useState<string | undefined>(undefined);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSessionElements = useCallback(async () => {
    if (!sessionToken) {
      setError('No session token provided');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await getSessionElements(sessionToken);
      
      setIsValid(result.valid);
      setAction(result.action);
      setMissing(result.missing);
      setSessionState(result.session_state);
      setSessionElements(result.elements || null);
      
      console.log('Session elements fetched:', result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch session elements');
      console.error('Error fetching session elements:', err);
    } finally {
      setIsLoading(false);
    }
  }, [sessionToken]);

  const clearSession = useCallback(async () => {
    if (!sessionToken) {
      setError('No session token provided');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      await clearSessionElements(sessionToken);
      
      // Reset state
      setSessionState({
        has_sop: false,
        has_workflow: false,
        section2_complete: false,
      });
      setSessionElements(null);
      setIsValid(false);
      setAction('redirect_to_section1');
      setMissing(undefined);
      
      console.log('Session elements cleared');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to clear session elements');
      console.error('Error clearing session elements:', err);
    } finally {
      setIsLoading(false);
    }
  }, [sessionToken]);

  // Fetch session elements on mount and when session token changes
  useEffect(() => {
    if (sessionToken) {
      fetchSessionElements();
    }
  }, [sessionToken, fetchSessionElements]);

  return {
    sessionState,
    sessionElements,
    isValid,
    action,
    missing,
    isLoading,
    error,
    refreshSession: fetchSessionElements,
    clearSession,
  };
} 