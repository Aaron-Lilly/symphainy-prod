/**
 * useFileOperations Hook
 * 
 * CANONICAL HOOK for file operations using the Runtime intent architecture.
 * Replaces useFileAPI which used stub APIs.
 * 
 * Architecture:
 * Component → useFileOperations → usePlatformState → ExperiencePlaneClient → Runtime
 * 
 * Usage:
 * ```tsx
 * const { uploadFile, parseFile, listFiles, deleteFile, isLoading, error } = useFileOperations();
 * 
 * const result = await uploadFile(file, { fileType: 'csv' });
 * if (result.success) {
 *   console.log('File ID:', result.artifacts?.file_id);
 * }
 * ```
 */

"use client";

import { useCallback, useState } from 'react';
import { usePlatformState } from '../state/PlatformStateProvider';
import { useSessionBoundary, SessionStatus } from '../state/SessionBoundaryProvider';
import type { 
  ExecutionStatusResponse,
  FileArtifact,
  ParsedContentArtifact,
} from '@/shared/types/runtime-contracts';

// =============================================================================
// TYPES
// =============================================================================

export interface FileUploadOptions {
  fileType?: 'csv' | 'json' | 'pdf' | 'docx' | 'txt' | 'xlsx' | 'xml' | 'auto';
  ingestType?: 'structured' | 'unstructured' | 'semi_structured' | 'auto';
  description?: string;
  tags?: string[];
}

export interface FileOperationResult {
  success: boolean;
  executionId?: string;
  artifacts?: Record<string, unknown>;
  error?: string;
}

export interface ParseOptions {
  parserType?: 'auto' | 'csv' | 'json' | 'pdf' | 'docx';
  autoSave?: boolean;
}

export interface FileListItem {
  artifact_id: string;
  artifact_type: string;
  name: string;
  mime_type?: string;
  size_bytes?: number;
  lifecycle_state: string;
  created_at: string;
  updated_at: string;
}

// =============================================================================
// HOOK
// =============================================================================

export function useFileOperations() {
  const { state: sessionState } = useSessionBoundary();
  const { state: platformState, submitIntent, getExecutionStatus } = usePlatformState();
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Wait for execution to complete with polling
   */
  const waitForExecution = useCallback(async (
    executionId: string,
    maxWaitMs: number = 30000,
    pollIntervalMs: number = 1000
  ): Promise<ExecutionStatusResponse | null> => {
    const startTime = Date.now();
    
    while (Date.now() - startTime < maxWaitMs) {
      const status = await getExecutionStatus(executionId);
      
      if (!status) {
        await new Promise(resolve => setTimeout(resolve, pollIntervalMs));
        continue;
      }
      
      if (status.status === 'completed' || status.status === 'failed') {
        return status;
      }
      
      await new Promise(resolve => setTimeout(resolve, pollIntervalMs));
    }
    
    return null;
  }, [getExecutionStatus]);

  /**
   * Upload a file using ingest_file intent
   */
  const uploadFile = useCallback(async (
    file: File,
    options: FileUploadOptions = {}
  ): Promise<FileOperationResult> => {
    if (sessionState.status !== SessionStatus.Active) {
      return { success: false, error: 'Session not active' };
    }

    setIsLoading(true);
    setError(null);

    try {
      // Convert file to base64 for transmission
      const fileContent = await file.arrayBuffer();
      const base64Content = btoa(
        Array.from(new Uint8Array(fileContent))
          .map(byte => String.fromCharCode(byte))
          .join('')
      );

      // Submit ingest_file intent
      const executionId = await submitIntent('ingest_file', {
        file_content: base64Content,
        file_name: file.name,
        file_size: file.size,
        mime_type: file.type || 'application/octet-stream',
        file_type: options.fileType || 'auto',
        ingest_type: options.ingestType || 'auto',
        description: options.description,
        tags: options.tags,
      });

      // Wait for execution to complete
      const result = await waitForExecution(executionId);

      if (!result) {
        return { 
          success: false, 
          executionId, 
          error: 'Execution timed out' 
        };
      }

      if (result.status === 'failed') {
        return { 
          success: false, 
          executionId, 
          error: result.error || 'Upload failed' 
        };
      }

      return {
        success: true,
        executionId,
        artifacts: result.artifacts,
      };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Upload failed';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setIsLoading(false);
    }
  }, [sessionState.status, submitIntent, waitForExecution]);

  /**
   * Parse a file using parse_content intent
   */
  const parseFile = useCallback(async (
    artifactId: string,
    options: ParseOptions = {}
  ): Promise<FileOperationResult> => {
    if (sessionState.status !== SessionStatus.Active) {
      return { success: false, error: 'Session not active' };
    }

    setIsLoading(true);
    setError(null);

    try {
      const executionId = await submitIntent('parse_content', {
        artifact_id: artifactId,
        parser_type: options.parserType || 'auto',
        auto_save: options.autoSave ?? true,
      });

      const result = await waitForExecution(executionId);

      if (!result) {
        return { success: false, executionId, error: 'Execution timed out' };
      }

      if (result.status === 'failed') {
        return { 
          success: false, 
          executionId, 
          error: result.error || 'Parse failed' 
        };
      }

      return {
        success: true,
        executionId,
        artifacts: result.artifacts,
      };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Parse failed';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setIsLoading(false);
    }
  }, [sessionState.status, submitIntent, waitForExecution]);

  /**
   * List files using content_list_files intent
   */
  const listFiles = useCallback(async (
    filters?: {
      artifactType?: 'file' | 'parsed_content' | 'embeddings';
      lifecycleState?: 'draft' | 'active' | 'archived';
    }
  ): Promise<{ success: boolean; files?: FileListItem[]; error?: string }> => {
    if (sessionState.status !== SessionStatus.Active) {
      return { success: false, error: 'Session not active' };
    }

    setIsLoading(true);
    setError(null);

    try {
      const executionId = await submitIntent('content_list_files', {
        artifact_type: filters?.artifactType,
        lifecycle_state: filters?.lifecycleState,
      });

      const result = await waitForExecution(executionId);

      if (!result) {
        return { success: false, error: 'Execution timed out' };
      }

      if (result.status === 'failed') {
        return { success: false, error: result.error || 'List files failed' };
      }

      // Extract files from artifacts
      const files = (result.artifacts?.files as FileListItem[]) || [];
      
      return {
        success: true,
        files,
      };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'List files failed';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setIsLoading(false);
    }
  }, [sessionState.status, submitIntent, waitForExecution]);

  /**
   * Delete a file using delete_file intent
   */
  const deleteFile = useCallback(async (
    artifactId: string
  ): Promise<FileOperationResult> => {
    if (sessionState.status !== SessionStatus.Active) {
      return { success: false, error: 'Session not active' };
    }

    setIsLoading(true);
    setError(null);

    try {
      const executionId = await submitIntent('delete_file', {
        artifact_id: artifactId,
      });

      const result = await waitForExecution(executionId);

      if (!result) {
        return { success: false, executionId, error: 'Execution timed out' };
      }

      if (result.status === 'failed') {
        return { 
          success: false, 
          executionId, 
          error: result.error || 'Delete failed' 
        };
      }

      return {
        success: true,
        executionId,
        artifacts: result.artifacts,
      };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Delete failed';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setIsLoading(false);
    }
  }, [sessionState.status, submitIntent, waitForExecution]);

  /**
   * Get parsed file content using get_parsed_file intent
   */
  const getParsedFile = useCallback(async (
    parsedArtifactId: string
  ): Promise<{ success: boolean; content?: unknown; error?: string }> => {
    if (sessionState.status !== SessionStatus.Active) {
      return { success: false, error: 'Session not active' };
    }

    setIsLoading(true);
    setError(null);

    try {
      const executionId = await submitIntent('get_parsed_file', {
        parsed_artifact_id: parsedArtifactId,
      });

      const result = await waitForExecution(executionId);

      if (!result) {
        return { success: false, error: 'Execution timed out' };
      }

      if (result.status === 'failed') {
        return { success: false, error: result.error || 'Get parsed file failed' };
      }

      return {
        success: true,
        content: result.artifacts?.parsed_content,
      };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Get parsed file failed';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setIsLoading(false);
    }
  }, [sessionState.status, submitIntent, waitForExecution]);

  /**
   * Create embeddings using create_deterministic_embeddings intent
   */
  const createEmbeddings = useCallback(async (
    parsedArtifactId: string,
    options?: {
      embeddingModel?: string;
      chunkStrategy?: string;
    }
  ): Promise<FileOperationResult> => {
    if (sessionState.status !== SessionStatus.Active) {
      return { success: false, error: 'Session not active' };
    }

    setIsLoading(true);
    setError(null);

    try {
      const executionId = await submitIntent('create_deterministic_embeddings', {
        parsed_artifact_id: parsedArtifactId,
        embedding_model: options?.embeddingModel || 'text-embedding-ada-002',
        chunk_strategy: options?.chunkStrategy || 'semantic',
      });

      const result = await waitForExecution(executionId);

      if (!result) {
        return { success: false, executionId, error: 'Execution timed out' };
      }

      if (result.status === 'failed') {
        return { 
          success: false, 
          executionId, 
          error: result.error || 'Create embeddings failed' 
        };
      }

      return {
        success: true,
        executionId,
        artifacts: result.artifacts,
      };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Create embeddings failed';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setIsLoading(false);
    }
  }, [sessionState.status, submitIntent, waitForExecution]);

  return {
    // Operations
    uploadFile,
    parseFile,
    listFiles,
    deleteFile,
    getParsedFile,
    createEmbeddings,
    
    // State
    isLoading,
    error,
    clearError: () => setError(null),
    
    // Session info
    isSessionActive: sessionState.status === SessionStatus.Active,
  };
}
