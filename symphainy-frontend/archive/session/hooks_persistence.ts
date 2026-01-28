/**
 * Session Persistence Hooks
 * React hooks for session persistence functionality
 */

import React, { useCallback } from 'react';
// ✅ PHASE 1: useGlobalSession archived - use useSessionBoundary instead
import { useSessionBoundary } from '../state/SessionBoundaryProvider';

// ⚠️ DEPRECATED: SessionBoundaryProvider handles persistence automatically
export function useSessionPersistence() {
  console.warn('⚠️ useSessionPersistence is deprecated. SessionBoundaryProvider handles persistence automatically.');
  const { state: sessionState } = useSessionBoundary();
  const guideSessionToken = sessionState.sessionId;

  // SessionBoundaryProvider handles persistence automatically
  const persistSession = useCallback(async (token: string) => {
    console.warn('⚠️ persistSession is deprecated. SessionBoundaryProvider handles persistence automatically.');
    // No-op - SessionBoundaryProvider manages this
  }, []);

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

// ⚠️ DEPRECATED: Use useSessionBoundary instead
export function useSmartCitySession() {
  console.warn('⚠️ useSmartCitySession is deprecated. Use useSessionBoundary from @/shared/state/SessionBoundaryProvider instead.');
  const { state: sessionState } = useSessionBoundary();
  const guideSessionToken = sessionState.sessionId;

  // TODO: Replace with actual Smart City integration
  const smartCityFeatures = {
    isEnabled: !!guideSessionToken,
    sessionId: guideSessionToken,
    status: guideSessionToken ? 'active' : 'no_session',
  };

  return smartCityFeatures;
} 