/**
 * Content API Module
 * 
 * Provides API functions for the Content pillar.
 * Uses ExperiencePlaneClient for real backend calls.
 * 
 * NOTE: These functions work outside React context. For React components,
 * prefer using useFileOperations hook when possible.
 */

import { getGlobalExperiencePlaneClient } from '@/shared/services/ExperiencePlaneClient';

// Helper to get session info
function getSessionInfo() {
  if (typeof window === 'undefined') {
    return { tenantId: 'default', sessionId: '' };
  }
  return {
    tenantId: sessionStorage.getItem('tenant_id') || 'default',
    sessionId: sessionStorage.getItem('session_id') || '',
  };
}

export interface SimpleFileData {
  id?: string;
  file_id?: string;
  filename?: string;
  ui_name?: string;
  file_type?: string;
  file_size?: number;
  status?: string;
  parsed_file_id?: string;
  created_at?: string;
}

export interface EmbeddingFile {
  id: string;
  file_id: string;
  parsed_file_id?: string;
  embedding_id?: string;
  content_id?: string;
  filename?: string;
  name?: string;
  status?: string;
  is_populated?: boolean;
  created_at?: string;
  created_at_display?: string;
  embeddings_count?: number;
  columns?: string[];
}

export interface SemanticLayerPreview {
  id: string;
  file_id: string;
  preview_data?: any;
  chunks?: any[];
  metadata?: any;
  structure?: {
    columns?: any[];
    rows?: any[];
    [key: string]: any;
  };
  columns?: any[];
  rows?: any[];
}

export interface UploadResponse {
  success: boolean;
  file_id?: string;
  error?: string;
}

export interface ParseResponse {
  success: boolean;
  parsed_data?: any;
  error?: string;
}

/**
 * List content files
 * 
 * Uses content_list_files intent.
 */
export async function listContentFiles(
  tokenOrOptions?: string | { tenantId?: string; sessionId?: string }
): Promise<SimpleFileData[]> {
  const client = getGlobalExperiencePlaneClient();
  const { tenantId: defaultTenantId, sessionId: defaultSessionId } = getSessionInfo();
  
  const options = typeof tokenOrOptions === 'object' ? tokenOrOptions : {};
  const tenantId = options.tenantId || defaultTenantId;
  const sessionId = options.sessionId || defaultSessionId;
  
  if (!sessionId) {
    console.warn('[content API] No session ID available');
    return [];
  }
  
  try {
    const submitResponse = await client.submitIntent({
      intent_type: 'content_list_files',
      tenant_id: tenantId,
      session_id: sessionId,
      parameters: {},
    });
    
    // Poll for completion
    const maxAttempts = 30;
    let attempts = 0;
    
    while (attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 500));
      const status = await client.getExecutionStatus(submitResponse.execution_id, tenantId);
      
      if (status.status === 'completed') {
        const artifacts = status.artifacts || {};
        const files = (artifacts.files || []) as Array<Record<string, unknown>>;
        
        return files.map(file => ({
          id: file.artifact_id as string || file.file_id as string || '',
          file_id: file.file_id as string || file.artifact_id as string || '',
          filename: file.name as string || file.filename as string || 'Unnamed',
          ui_name: file.name as string || file.ui_name as string,
          file_type: file.mime_type as string || file.file_type as string,
          file_size: file.size_bytes as number || file.file_size as number,
          status: file.lifecycle_state as string || file.status as string || 'uploaded',
          parsed_file_id: file.parsed_file_id as string,
          created_at: file.created_at as string,
        }));
      } else if (status.status === 'failed') {
        console.error('[content API] listContentFiles failed:', status.error);
        return [];
      }
      
      attempts++;
    }
    
    return [];
  } catch (error) {
    console.error('[content API] listContentFiles error:', error);
    return [];
  }
}

/**
 * Upload a file
 * 
 * Uses ingest_file intent.
 */
export async function uploadFile(
  file: File,
  options?: { tenantId?: string; sessionId?: string }
): Promise<UploadResponse> {
  const client = getGlobalExperiencePlaneClient();
  const { tenantId: defaultTenantId, sessionId: defaultSessionId } = getSessionInfo();
  
  const tenantId = options?.tenantId || defaultTenantId;
  const sessionId = options?.sessionId || defaultSessionId;
  
  if (!sessionId) {
    return { success: false, error: 'No active session' };
  }
  
  try {
    // Convert file to base64
    const fileContent = await file.arrayBuffer();
    const base64Content = btoa(
      Array.from(new Uint8Array(fileContent))
        .map(byte => String.fromCharCode(byte))
        .join('')
    );
    
    const submitResponse = await client.submitIntent({
      intent_type: 'ingest_file',
      tenant_id: tenantId,
      session_id: sessionId,
      parameters: {
        file_content: base64Content,
        file_name: file.name,
        file_size: file.size,
        mime_type: file.type || 'application/octet-stream',
        file_type: 'auto',
        ingest_type: 'auto',
      },
    });
    
    // Poll for completion
    const maxAttempts = 60;
    let attempts = 0;
    
    while (attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 500));
      const status = await client.getExecutionStatus(submitResponse.execution_id, tenantId);
      
      if (status.status === 'completed') {
        const artifacts = status.artifacts || {};
        const fileArtifact = artifacts.file as { semantic_payload?: { file_id?: string } } | undefined;
        return { 
          success: true, 
          file_id: fileArtifact?.semantic_payload?.file_id || artifacts.file_id as string || submitResponse.execution_id
        };
      } else if (status.status === 'failed') {
        return { success: false, error: status.error || 'Upload failed' };
      }
      
      attempts++;
    }
    
    return { success: false, error: 'Upload timed out' };
  } catch (error) {
    console.error('[content API] uploadFile error:', error);
    return { success: false, error: error instanceof Error ? error.message : 'Upload failed' };
  }
}

/**
 * Parse a file
 * 
 * Uses parse_content intent.
 */
export async function parseFile(
  fileId: string,
  options?: { tenantId?: string; sessionId?: string }
): Promise<ParseResponse> {
  const client = getGlobalExperiencePlaneClient();
  const { tenantId: defaultTenantId, sessionId: defaultSessionId } = getSessionInfo();
  
  const tenantId = options?.tenantId || defaultTenantId;
  const sessionId = options?.sessionId || defaultSessionId;
  
  if (!sessionId) {
    return { success: false, error: 'No active session' };
  }
  
  try {
    const submitResponse = await client.submitIntent({
      intent_type: 'parse_content',
      tenant_id: tenantId,
      session_id: sessionId,
      parameters: {
        artifact_id: fileId,
        parser_type: 'auto',
        auto_save: true,
      },
    });
    
    // Poll for completion
    const maxAttempts = 60;
    let attempts = 0;
    
    while (attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 500));
      const status = await client.getExecutionStatus(submitResponse.execution_id, tenantId);
      
      if (status.status === 'completed') {
        const artifacts = status.artifacts || {};
        return { 
          success: true, 
          parsed_data: artifacts.parsed_content || artifacts.parsed_file || {}
        };
      } else if (status.status === 'failed') {
        return { success: false, error: status.error || 'Parsing failed' };
      }
      
      attempts++;
    }
    
    return { success: false, error: 'Parsing timed out' };
  } catch (error) {
    console.error('[content API] parseFile error:', error);
    return { success: false, error: error instanceof Error ? error.message : 'Parsing failed' };
  }
}

/**
 * Get file metadata
 */
export async function getFileMetadata(
  fileId: string,
  options?: { tenantId?: string; sessionId?: string }
): Promise<{ success: boolean; metadata?: any; error?: string }> {
  console.warn('[content API] getFileMetadata - stub implementation');
  return { success: true, metadata: {} };
}

/**
 * Delete a file
 */
export async function deleteFile(
  fileId: string,
  options?: { tenantId?: string; sessionId?: string }
): Promise<{ success: boolean; error?: string }> {
  console.warn('[content API] deleteFile - stub implementation');
  return { success: true };
}

/**
 * List embeddings for a file
 */
export async function listEmbeddings(
  fileId: string,
  token?: string
): Promise<{ success: boolean; embeddings?: any[]; error?: string }> {
  console.warn('[content API] listEmbeddings - stub implementation');
  return { success: true, embeddings: [] };
}

/**
 * List embedding files
 */
export async function listEmbeddingFiles(
  token?: string,
  parsedFileId?: string,
  fileId?: string
): Promise<{ success: boolean; files?: any[]; error?: string }> {
  console.warn('[content API] listEmbeddingFiles - stub implementation');
  return { success: true, files: [] };
}

/**
 * Preview embeddings for a file
 */
export async function previewEmbeddings(
  fileId: string,
  token?: string
): Promise<{ success: boolean; preview?: any; error?: string }> {
  console.warn('[content API] previewEmbeddings - stub implementation');
  return { success: true, preview: {} };
}

/**
 * Create embeddings for a parsed file
 */
export async function createEmbeddings(
  parsedFileId: string,
  token?: string,
  fileId?: string
): Promise<{ success: boolean; embedding_id?: string; error?: string }> {
  console.warn('[content API] createEmbeddings - stub implementation');
  return { success: true, embedding_id: `emb_${Date.now()}` };
}

/**
 * List parsed files with embeddings
 */
export async function listParsedFilesWithEmbeddings(
  token?: string
): Promise<{ success: boolean; parsed_files?: any[]; files?: any[]; error?: string }> {
  console.warn('[content API] listParsedFilesWithEmbeddings - stub implementation');
  return { success: true, parsed_files: [], files: [] };
}

/**
 * Get mash context
 */
export async function getMashContext(
  options?: any,
  token?: string
): Promise<{ success: boolean; context?: any; error?: string }> {
  console.warn('[content API] getMashContext - stub implementation');
  return { success: true, context: {} };
}

// Enhanced File Processing Types
export interface EnhancedFileProcessingRequest {
  file_id?: string;
  file_data?: any;
  filename?: string;
  file_type?: string;
  user_id?: string;
  session_token?: string;
  options?: {
    extract_tables?: boolean;
    extract_metadata?: boolean;
    auto_track_lineage?: boolean;
    [key: string]: any;
  };
  processing_options?: {
    extract_metadata?: boolean;
    generate_preview?: boolean;
    create_embeddings?: boolean;
  };
  [key: string]: any;
}

export interface EnhancedFileProcessingResponse {
  success: boolean;
  file_id: string;
  filename: string;
  file_type: string;
  processing_time_seconds: number;
  parsing_result: {
    document_type: string;
    tables?: Array<{
      table_id: string;
      columns: string[];
      row_count: number;
      column_count: number;
    }>;
    text?: string;
  };
  metadata: any;
  lineage: any;
  storage: any;
  error?: string;
}

export interface FileMetadataResponse {
  success: boolean;
  metadata?: {
    file_id: string;
    filename: string;
    file_type: string;
    file_size: number;
    created_at: string;
    [key: string]: any;
  };
  error?: string;
}

export interface FileLineageResponse {
  success: boolean;
  lineage?: {
    file_id: string;
    parent_id?: string;
    children?: string[];
    transformations?: any[];
  };
  error?: string;
}

/**
 * Process file with enhanced metadata extraction
 */
export async function processFileWithMetadata(
  tokenOrRequest: string | EnhancedFileProcessingRequest,
  request?: EnhancedFileProcessingRequest
): Promise<EnhancedFileProcessingResponse> {
  console.warn('[content API] processFileWithMetadata - stub implementation');
  const actualRequest = typeof tokenOrRequest === 'string' ? request : tokenOrRequest;
  return {
    success: true,
    file_id: actualRequest?.file_id || '',
    filename: actualRequest?.filename || '',
    file_type: actualRequest?.file_type || '',
    processing_time_seconds: 0,
    parsing_result: { document_type: 'unknown' },
    metadata: {},
    lineage: {},
    storage: {}
  };
}

/**
 * Get file lineage information
 */
export async function getFileLineage(
  fileId: string
): Promise<FileLineageResponse> {
  console.warn('[content API] getFileLineage - stub implementation');
  return { success: true, lineage: { file_id: fileId } };
}
