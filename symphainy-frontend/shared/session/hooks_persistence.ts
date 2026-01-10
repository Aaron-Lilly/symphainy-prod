/**
 * Session Persistence Hooks
 * React hooks for session persistence functionality
 */

import React, { useCallback } from 'react';
import { useGlobalSession } from './index';

// Hook for session persistence
export function useSessionPersistence() {
  const { guideSessionToken, setGuideSessionToken } = useGlobalSession();

  const persistSession = useCallback(async (token: string) => {
    await setGuideSessionToken(token);
    localStorage.setItem('guideSessionToken', token);
  }, [setGuideSessionToken]);

  const clearPersistedSession = useCallback(() => {
    localStorage.removeItem('guideSessionToken');
  }, []);

  const getPersistedSession = useCallback(() => {
    return localStorage.getItem('guideSessionToken');
  }, []);

  return {
    persistSession,
    clearPersistedSession,
    getPersistedSession,
    hasPersistedSession: !!getPersistedSession(),
  };
}

// Hook for Smart City session integration
export function useSmartCitySession() {
  const { guideSessionToken } = useGlobalSession();

  // TODO: Replace with actual Smart City integration
  const smartCityFeatures = {
    isEnabled: !!guideSessionToken,
    sessionId: guideSessionToken,
    status: guideSessionToken ? 'active' : 'no_session',
  };

  return smartCityFeatures;
} 