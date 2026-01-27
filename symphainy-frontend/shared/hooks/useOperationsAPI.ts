/**
 * useOperationsAPI Hook
 * 
 * ✅ PHASE 2: React hook for operations/workflow API calls
 * ✅ PHASE 6: Error Handling Standardization - Returns { data, error } pattern
 * Automatically gets session tokens from SessionBoundaryProvider
 * 
 * Usage:
 * ```tsx
 * const { optimizeCoexistence, saveBlueprint, startWizard, wizardChat } = useOperationsAPI();
 * const result = await optimizeCoexistence({ ... });
 * if (result.error) {
 *   // Display error using <ErrorDisplay error={result.error} />
 * } else {
 *   // Use result.data
 * }
 * ```
 */

"use client";

import { useCallback, useState } from 'react';
import { useSessionBoundary } from '../state/SessionBoundaryProvider';
import * as operationsAPI from '../../lib/api/operations';
import { ServiceResult, wrapServiceCall } from '../utils/serviceWrapper';
import { ErrorSignal } from '../types/errors';
import { createSessionError } from '../utils/errorSignals';

export interface OptimizeCoexistenceParams {
  sopInputFileUuid: string;
  workflowInputFileUuid: string;
  sessionToken?: string;
}

export interface OptimizeCoexistenceWithContentParams {
  sopContent: string;
  workflowContent: any;
  sessionToken?: string;
}

export interface SaveBlueprintParams {
  blueprint: any;
  sessionToken?: string;
  userId?: string;
}

export function useOperationsAPI() {
  const { state: sessionState } = useSessionBoundary();
  const [lastError, setLastError] = useState<ErrorSignal | null>(null);
  
  // Get session token (access_token for auth)
  const getToken = useCallback((): string => {
    const accessToken = typeof window !== 'undefined' ? sessionStorage.getItem('access_token') : null;
    if (!accessToken) {
      throw new Error('Not authenticated - access token required for operations');
    }
    return accessToken;
  }, []);

  const getSessionId = useCallback((): string | null => {
    return sessionState.sessionId;
  }, [sessionState.sessionId]);

  // ✅ PHASE 6: Return { data, error } pattern
  const optimizeCoexistence = useCallback(
    async (params: OptimizeCoexistenceParams): Promise<ServiceResult<any>> => {
      const sessionToken = params.sessionToken || getSessionId();
      if (!sessionToken) {
        const error = createSessionError('SESSION_REQUIRED', 'Session token required for optimizeCoexistence');
        setLastError(error);
        return { data: null, error };
      }
      const result = await wrapServiceCall(() => operationsAPI.optimizeCoexistence(
        sessionToken,
        params.sopInputFileUuid,
        params.workflowInputFileUuid
      ));
      setLastError(result.error);
      return result;
    },
    [getSessionId]
  );
  
  const optimizeCoexistenceWithContent = useCallback(
    async (params: OptimizeCoexistenceWithContentParams): Promise<ServiceResult<any>> => {
      const sessionToken = params.sessionToken || getSessionId();
      if (!sessionToken) {
        const error = createSessionError('SESSION_REQUIRED', 'Session token required for optimizeCoexistenceWithContent');
        setLastError(error);
        return { data: null, error };
      }
      const result = await wrapServiceCall(() => operationsAPI.optimizeCoexistenceWithContent(
        sessionToken,
        params.sopContent,
        params.workflowContent
      ));
      setLastError(result.error);
      return result;
    },
    [getSessionId]
  );
  
  const saveBlueprint = useCallback(
    async (params: SaveBlueprintParams): Promise<ServiceResult<any>> => {
      const userId = params.userId || sessionState.userId;
      if (!userId) {
        const error = createSessionError('USER_REQUIRED', 'User ID required for saveBlueprint');
        setLastError(error);
        return { data: null, error };
      }
      const result = await wrapServiceCall(() => operationsAPI.saveBlueprint(
        params.blueprint,
        userId
      ));
      setLastError(result.error);
      return result;
    },
    [sessionState.userId]
  );
  
  const startWizard = useCallback(async (): Promise<ServiceResult<any>> => {
    const sessionToken = getSessionId();
    const result = await wrapServiceCall(() => operationsAPI.startWizard(sessionToken || undefined, sessionState.userId || undefined));
    setLastError(result.error);
    return result;
  }, [getSessionId, sessionState.userId]);
  
  const wizardChat = useCallback(
    async (userMessage: string): Promise<ServiceResult<any>> => {
      const sessionToken = getSessionId();
      if (!sessionToken) {
        const error = createSessionError('SESSION_REQUIRED', 'Session token required for wizardChat');
        setLastError(error);
        return { data: null, error };
      }
      const result = await wrapServiceCall(() => operationsAPI.wizardChat(sessionToken, userMessage));
      setLastError(result.error);
      return result;
    },
    [getSessionId]
  );
  
  const wizardPublish = useCallback(async (): Promise<ServiceResult<any>> => {
    const sessionToken = getSessionId();
    if (!sessionToken) {
      const error = createSessionError('SESSION_REQUIRED', 'Session token required for wizardPublish');
      setLastError(error);
      return { data: null, error };
    }
    const result = await wrapServiceCall(() => operationsAPI.wizardPublish(sessionToken, sessionState.userId || undefined));
    setLastError(result.error);
    return result;
  }, [getSessionId, sessionState.userId]);

  return {
    // ✅ PHASE 6: All functions return { data, error } pattern
    optimizeCoexistence,
    optimizeCoexistenceWithContent,
    saveBlueprint,
    startWizard,
    wizardChat,
    wizardPublish,
    // ✅ PHASE 6: Expose last error and clear function
    error: lastError,
    clearError: () => setLastError(null),
  };
}
