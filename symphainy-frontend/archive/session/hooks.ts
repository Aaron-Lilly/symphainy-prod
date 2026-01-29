/**
 * ⚠️ PHASE 1: DEPRECATED - Session Management Hooks
 * 
 * These hooks depend on archived GlobalSessionProvider.
 * Migration guide:
 * - useSessionStatus → use useSessionBoundary from '@/shared/state/SessionBoundaryProvider'
 * - usePillarState → use usePlatformState from '@/shared/state/PlatformStateProvider'
 * - useSessionLifecycle → use useSessionBoundary from '@/shared/state/SessionBoundaryProvider'
 */

import React, { useContext, useEffect, useState, useCallback } from 'react';
import { SessionContextType, SessionStatus } from './types';
// ✅ PHASE 1: useGlobalSession archived - use useSessionBoundary instead
import { useSessionBoundary } from '../state/SessionBoundaryProvider';

// ⚠️ DEPRECATED: Use useSessionBoundary instead
export function useSessionStatus(): {
  status: SessionStatus;
  isSessionValid: boolean;
  isLoading: boolean;
} {
  console.warn('⚠️ useSessionStatus is deprecated. Use useSessionBoundary from @/shared/state/SessionBoundaryProvider instead.');
  const { state: sessionState } = useSessionBoundary();
  const guideSessionToken = sessionState.sessionId;
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

// ⚠️ DEPRECATED: Use usePlatformState instead
export function usePillarState(pillar: string) {
  console.warn('⚠️ usePillarState is deprecated. Use usePlatformState from @/shared/state/PlatformStateProvider instead.');
  // Return empty state - migration needed
  const [state, setState] = useState(null);
  return [state, setState] as const;
}

// ⚠️ DEPRECATED: Use useSessionBoundary instead
export function useSessionLifecycle() {
  console.warn('⚠️ useSessionLifecycle is deprecated. Use useSessionBoundary from @/shared/state/SessionBoundaryProvider instead.');
  const { state: sessionState, invalidateSession } = useSessionBoundary();
  const { status, isSessionValid } = useSessionStatus();

  const resetSession = useCallback(async () => {
    invalidateSession();
  }, [invalidateSession]);

  const isSessionActive = isSessionValid && !!sessionState.sessionId;

  return {
    isSessionActive,
    sessionStatus: status,
    resetSession,
  };
} 