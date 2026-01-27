/**
 * useContentAPI Hook
 * 
 * ✅ PHASE 2: React hook for content API calls
 * ✅ PHASE 6: Error Handling Standardization - Returns { data, error } pattern
 * Automatically gets session tokens from SessionBoundaryProvider
 * 
 * Usage:
 * ```tsx
 * const { listContentFiles, error } = useContentAPI();
 * const result = await listContentFiles();
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
import * as contentAPI from '../../lib/api/content';
import { ServiceResult, wrapServiceCall } from '../utils/serviceWrapper';
import { ErrorSignal } from '../types/errors';

// Re-export SimpleFileData type from content API
export type SimpleFileData = {
  id?: string;
  file_id?: string;
  name?: string;
  file_name?: string;
  ui_name?: string;
  type?: string;
  file_type?: string;
  size?: number;
  uploaded_at?: string;
  created_at?: string;
  status?: string;
  metadata?: Record<string, any>;
  [key: string]: any;
};

export function useContentAPI() {
  const { state: sessionState } = useSessionBoundary();
  const [lastError, setLastError] = useState<ErrorSignal | null>(null);
  
  // Get session token (access_token for auth)
  const getToken = useCallback((): string => {
    const accessToken = typeof window !== 'undefined' ? sessionStorage.getItem('access_token') : null;
    if (!accessToken) {
      throw new Error('Not authenticated - access token required for content operations');
    }
    return accessToken;
  }, []);

  // ✅ PHASE 6: Return { data, error } pattern
  const listContentFiles = useCallback(async (): Promise<ServiceResult<SimpleFileData[]>> => {
    const result = await wrapServiceCall(() => contentAPI.listContentFiles(getToken()));
    setLastError(result.error);
    return result;
  }, [getToken]);
    
  // ✅ PHASE 6: Return { data, error } pattern for all API functions
  const listEmbeddings = useCallback(async (fileId?: string, token?: string): Promise<ServiceResult<any>> => {
    const result = await wrapServiceCall(() => contentAPI.listEmbeddings(fileId, token || getToken()));
    setLastError(result.error);
    return result;
  }, [getToken]);
  
  const listEmbeddingFiles = useCallback(async (token?: string, parsedFileId?: string, fileId?: string): Promise<ServiceResult<any>> => {
    const result = await wrapServiceCall(() => contentAPI.listEmbeddingFiles(token || getToken(), parsedFileId, fileId));
    setLastError(result.error);
    return result;
  }, [getToken]);
  
  const previewEmbeddings = useCallback(
    async (fileId: string, token?: string): Promise<ServiceResult<any>> => {
      const result = await wrapServiceCall(() => contentAPI.previewEmbeddings(fileId, token || getToken()));
      setLastError(result.error);
      return result;
    },
    [getToken]
  );
  
  const createEmbeddings = useCallback(
    async (parsedFileId: string, fileId?: string, token?: string): Promise<ServiceResult<any>> => {
      const result = await wrapServiceCall(() => contentAPI.createEmbeddings(parsedFileId, token || getToken(), fileId));
      setLastError(result.error);
      return result;
    },
    [getToken]
  );
  
  const listParsedFilesWithEmbeddings = useCallback(
    async (token?: string): Promise<ServiceResult<any>> => {
      const result = await wrapServiceCall(() => contentAPI.listParsedFilesWithEmbeddings(token || getToken()));
      setLastError(result.error);
      return result;
    },
    [getToken]
  );
  
  const getMashContext = useCallback(
    async (
      options: {
        content_id?: string;
        file_id?: string;
        parsed_file_id?: string;
      },
      token?: string
    ): Promise<ServiceResult<any>> => {
      const result = await wrapServiceCall(() => contentAPI.getMashContext(options, token || getToken()));
      setLastError(result.error);
      return result;
    },
    [getToken]
  );

  return {
    // ✅ PHASE 6: All functions return { data, error } pattern
    listContentFiles,
    listEmbeddings,
    listEmbeddingFiles,
    previewEmbeddings,
    createEmbeddings,
    listParsedFilesWithEmbeddings,
    getMashContext,
    // ✅ PHASE 6: Expose last error and clear function
    error: lastError,
    clearError: () => setLastError(null),
  };
}
