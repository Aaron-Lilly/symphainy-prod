/**
 * Session Management Hooks
 * React hooks for session management functionality
 */

import React, { useContext, useEffect, useState, useCallback } from 'react';
import { SessionContextType, SessionStatus } from './types';
import { useGlobalSession } from './index';

// Hook for session status management
export function useSessionStatus(): {
  status: SessionStatus;
  isSessionValid: boolean;
  isLoading: boolean;
} {
  const { guideSessionToken } = useGlobalSession();
  const [status, setStatus] = useState<SessionStatus>('no_session');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!guideSessionToken) {
      setStatus('no_session');
      return;
    }

    setStatus('validating');
    setIsLoading(true);

    // Simulate validation (replace with actual Smart City validation)
    const validateSession = async () => {
      try {
        // TODO: Replace with actual Smart City validation
        await new Promise(resolve => setTimeout(resolve, 100));
        setStatus('active');
      } catch (error) {
        setStatus('error');
      } finally {
        setIsLoading(false);
      }
    };

    validateSession();
  }, [guideSessionToken]);

  const isSessionValid = status === 'active';

  return { status, isSessionValid, isLoading };
}

// Hook for pillar state management
export function usePillarState(pillar: string) {
  const { getPillarState, setPillarState } = useGlobalSession();
  const [state, setState] = useState(getPillarState(pillar));

  const updateState = useCallback(async (newState: any) => {
    await setPillarState(pillar, newState);
    setState(newState);
  }, [pillar, setPillarState]);

  return [state, updateState] as const;
}

// Hook for session lifecycle management
export function useSessionLifecycle() {
  const { guideSessionToken, resetAllState } = useGlobalSession();
  const { status, isSessionValid } = useSessionStatus();

  const resetSession = useCallback(async () => {
    await resetAllState();
  }, [resetAllState]);

  const isSessionActive = isSessionValid && !!guideSessionToken;

  return {
    isSessionActive,
    sessionStatus: status,
    resetSession,
  };
} 