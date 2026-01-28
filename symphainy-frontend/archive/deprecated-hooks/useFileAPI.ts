/**
 * useFileAPI Hook
 * 
 * ✅ PHASE 2: React hook for file management API calls
 * ✅ PHASE 6: Error Handling Standardization - Returns { data, error } pattern
 * Automatically gets session tokens from SessionBoundaryProvider
 * 
 * Usage:
 * ```tsx
 * const { uploadFile, listFiles, deleteFile } = useFileAPI();
 * const result = await listFiles();
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
import * as fmsAPI from '../../lib/api/fms';
import * as fileProcessingAPI from '../../lib/api/file-processing';
import { FileMetadata, ApiUploadRequest, LinkType, FileType } from '@/shared/types/file';
import { ServiceResult, wrapServiceCall } from '../utils/serviceWrapper';
import { ErrorSignal } from '../types/errors';

export function useFileAPI() {
  const { state: sessionState } = useSessionBoundary();
  const [lastError, setLastError] = useState<ErrorSignal | null>(null);
  
  // Get session token (access_token for auth, session_id for session state)
  const getToken = useCallback((): string => {
    const accessToken = typeof window !== 'undefined' ? sessionStorage.getItem('access_token') : null;
    if (!accessToken) {
      throw new Error('Not authenticated - access token required for file operations');
    }
    return accessToken;
  }, []);

  // ✅ PHASE 6: Return { data, error } pattern
  const uploadFile = useCallback(
    async (req: ApiUploadRequest & { file?: File; copybookFile?: File }): Promise<ServiceResult<FileMetadata>> => {
      const result = await wrapServiceCall(() => fmsAPI.uploadFile(req, getToken()));
      setLastError(result.error);
      return result;
    },
    [getToken]
  );
  
  const listFiles = useCallback(async (): Promise<ServiceResult<FileMetadata[]>> => {
    const result = await wrapServiceCall(() => fmsAPI.listFiles(getToken()));
    setLastError(result.error);
    return result;
  }, [getToken]);
  
  const getFileDetails = useCallback(async (uuid: string): Promise<ServiceResult<FileMetadata>> => {
    const result = await wrapServiceCall(() => fmsAPI.getFileDetails(uuid, getToken()));
    setLastError(result.error);
    return result;
  }, [getToken]);
  
  const parseFile = useCallback(async (uuid: string): Promise<ServiceResult<any>> => {
    const result = await wrapServiceCall(() => fmsAPI.parseFile(uuid, getToken()));
    setLastError(result.error);
    return result;
  }, [getToken]);
  
  const linkFiles = useCallback(
    async (parentUuid: string, childUuid: string, linkType: LinkType): Promise<ServiceResult<{ success: boolean }>> => {
      const result = await wrapServiceCall(() => fmsAPI.linkFiles(parentUuid, childUuid, linkType, getToken()));
      setLastError(result.error);
      return result;
    },
    [getToken]
  );
  
  const updateFile = useCallback(
    async (uuid: string, updates: Partial<FileMetadata>): Promise<ServiceResult<{ success: boolean }>> => {
      const result = await wrapServiceCall(() => fmsAPI.updateFile(uuid, updates, getToken()));
      setLastError(result.error);
      return result;
    },
    [getToken]
  );
  
  const deleteFile = useCallback(async (uuid: string): Promise<ServiceResult<{ success: boolean }>> => {
    const result = await wrapServiceCall(() => fmsAPI.deleteFile(uuid, getToken()));
    setLastError(result.error);
    return result;
  }, [getToken]);
  
  // File processing operations
  const uploadAndProcessFile = useCallback(
    async (
      file: File,
      sessionId: string,
      fileType: FileType,
      token?: string
    ): Promise<ServiceResult<fileProcessingAPI.FileProcessingResult>> => {
      const authToken = token || getToken();
      const result = await wrapServiceCall(() => fileProcessingAPI.uploadAndProcessFile(file, sessionId, fileType, authToken));
      setLastError(result.error);
      return result;
    },
    [getToken]
  );

  return {
    // ✅ PHASE 6: All functions return { data, error } pattern
    uploadFile,
    listFiles,
    getFileDetails,
    parseFile,
    linkFiles,
    updateFile,
    deleteFile,
    uploadAndProcessFile,
    // ✅ PHASE 6: Expose last error and clear function
    error: lastError,
    clearError: () => setLastError(null),
  };
}
