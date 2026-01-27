/**
 * useInsightsAPI Hook
 * 
 * ✅ PHASE 2: React hook for insights API calls
 * ✅ PHASE 6: Error Handling Standardization - Returns { data, error } pattern
 * Automatically gets session tokens from SessionBoundaryProvider
 * 
 * Usage:
 * ```tsx
 * const { processNaturalLanguageQuery, processChatMessage, listFiles } = useInsightsAPI();
 * const result = await processNaturalLanguageQuery({ query: "..." });
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
import * as insightsAPI from '../../lib/api/insights';
import * as fmsInsightsAPI from '../../lib/api/fms-insights';
import { FileMetadata } from '@/shared/types/file';
import { ServiceResult, wrapServiceCall } from '../utils/serviceWrapper';
import { ErrorSignal } from '../types/errors';
import { createSessionError } from '../utils/errorSignals';

export interface ProcessNaturalLanguageQueryParams {
  query: string;
  file_url?: string | null;
  context?: any;
}

export interface ProcessChatMessageParams {
  message: string;
  context?: any;
}

export function useInsightsAPI() {
  const { state: sessionState } = useSessionBoundary();
  const [lastError, setLastError] = useState<ErrorSignal | null>(null);
  
  // Get session token (access_token for auth, session_id for session state)
  const getToken = useCallback((): string => {
    const accessToken = typeof window !== 'undefined' ? sessionStorage.getItem('access_token') : null;
    if (!accessToken) {
      throw new Error('Not authenticated - access token required for insights operations');
    }
    return accessToken;
  }, []);

  const getSessionId = useCallback((): string | null => {
    return sessionState.sessionId;
  }, [sessionState.sessionId]);

  // ✅ PHASE 6: Return { data, error } pattern
  const listFiles = useCallback(async (userId?: string, teamId?: string): Promise<ServiceResult<FileMetadata[]>> => {
    const result = await wrapServiceCall(() => fmsInsightsAPI.listFiles(userId, teamId));
    setLastError(result.error);
    return result;
  }, []);
  
  const processNaturalLanguageQuery = useCallback(
    async (params: ProcessNaturalLanguageQueryParams): Promise<ServiceResult<any>> => {
      const sessionId = getSessionId();
      if (!sessionId) {
        const error = createSessionError('SESSION_REQUIRED', 'Session ID required for processNaturalLanguageQuery');
        setLastError(error);
        return { data: null, error };
      }
      const result = await wrapServiceCall(() => insightsAPI.processNaturalLanguageQuery({
        session_id: sessionId,
        query: params.query,
        file_url: params.file_url,
        context: params.context,
        sessionToken: sessionId,
        token: getToken(),
      }));
      setLastError(result.error);
      return result;
    },
    [getSessionId, getToken]
  );
  
  const processChatMessage = useCallback(
    async (params: ProcessChatMessageParams): Promise<ServiceResult<any>> => {
      const sessionId = getSessionId();
      if (!sessionId) {
        const error = createSessionError('SESSION_REQUIRED', 'Session ID required for processChatMessage');
        setLastError(error);
        return { data: null, error };
      }
      const result = await wrapServiceCall(() => insightsAPI.processChatMessage({
        session_id: sessionId,
        message: params.message,
        context: params.context,
        sessionToken: sessionId,
        token: getToken(),
      }));
      setLastError(result.error);
      return result;
    },
    [getSessionId, getToken]
  );

  return {
    // ✅ PHASE 6: All functions return { data, error } pattern
    listFiles,
    processNaturalLanguageQuery,
    processChatMessage,
    // ✅ PHASE 6: Expose last error and clear function
    error: lastError,
    clearError: () => setLastError(null),
  };
}
