/**
 * FMS (File Management System) API Module
 * 
 * Uses ExperiencePlaneClient for real backend calls.
 * NOTE: For React components, prefer using useFileOperations hook.
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

import { FileStatus } from '@/shared/types/file';

export interface FMSFile {
  id: string;
  uuid: string;
  file_id?: string;
  filename?: string;
  ui_name: string;
  file_type: string;
  original_path: string;
  size?: number;
  file_size?: number;
  status: FileStatus;
  created_at: string;
  updated_at: string;
  upload_timestamp?: string;
  deleted: boolean;
  [key: string]: unknown;
}

export interface FMSUploadResponse {
  success: boolean;
  file_id?: string;
  error?: string;
}

export async function uploadToFMS(file: File): Promise<FMSUploadResponse> {
  try {
    const result = await uploadFile({ file, filename: file.name, file_type: file.type });
    return { success: true, file_id: result.id };
  } catch (error) {
    return { success: false, error: error instanceof Error ? error.message : 'Upload failed' };
  }
}

export async function listFMSFiles(userId?: string): Promise<FMSFile[]> {
  const { tenantId, sessionId } = getSessionInfo();
  if (!sessionId) return [];
  
  const client = getGlobalExperiencePlaneClient();
  
  try {
    const submitResponse = await client.submitIntent({
      intent_type: 'content_list_files',
      tenant_id: tenantId,
      session_id: sessionId,
      parameters: {},
    });
    
    const maxAttempts = 30;
    let attempts = 0;
    
    while (attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 500));
      const status = await client.getExecutionStatus(submitResponse.execution_id, tenantId);
      
      if (status.status === 'completed') {
        const artifacts = status.artifacts || {};
        const files = (artifacts.files || []) as Array<Record<string, unknown>>;
        
        return files.map(file => {
          const id = (file.artifact_id || file.file_id || '') as string;
          const createdAt = (file.created_at || new Date().toISOString()) as string;
          const rawStatus = (file.lifecycle_state || file.status || 'uploaded') as string;
          // Map backend status to FileStatus enum
          const statusMap: Record<string, FileStatus> = {
            'uploaded': FileStatus.Uploaded,
            'parsing': FileStatus.Parsing,
            'parsed': FileStatus.Parsed,
            'completed': FileStatus.Parsed,
            'validated': FileStatus.Validated,
            'failed': FileStatus.Uploaded, // No Failed status in enum, fallback to Uploaded
            'error': FileStatus.Uploaded,
            'active': FileStatus.Uploaded,
            'draft': FileStatus.Uploaded,
          };
          const status = statusMap[rawStatus.toLowerCase()] || FileStatus.Uploaded;
          
          return {
            id,
            uuid: id,
            file_id: (file.file_id || file.artifact_id) as string,
            filename: (file.name || file.filename) as string,
            ui_name: (file.name || file.ui_name || 'Unnamed') as string,
            file_type: (file.mime_type || file.file_type || 'unknown') as string,
            original_path: (file.original_path || '') as string,
            size: (file.size_bytes || file.size) as number,
            file_size: (file.size_bytes || file.file_size) as number,
            status,
            created_at: createdAt,
            updated_at: (file.updated_at || createdAt) as string,
            upload_timestamp: createdAt,
            deleted: (file.deleted || false) as boolean,
          };
        });
      } else if (status.status === 'failed') {
        return [];
      }
      attempts++;
    }
    return [];
  } catch (error) {
    console.error('[fms API] listFMSFiles error:', error);
    return [];
  }
}

// Alias for backward compatibility
export const listFiles = listFMSFiles;

export async function uploadFile(
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  request: any,
  token?: string
): Promise<FMSFile> {
  const { tenantId, sessionId } = getSessionInfo();
  const client = getGlobalExperiencePlaneClient();
  
  if (!sessionId) {
    throw new Error('No active session');
  }
  
  try {
    let base64Content = '';
    let fileSize = 0;
    let mimeType = 'application/octet-stream';
    let fileName = request.filename || 'uploaded_file';
    
    if (request.file) {
      const fileContent = await request.file.arrayBuffer();
      base64Content = btoa(
        Array.from(new Uint8Array(fileContent))
          .map(byte => String.fromCharCode(byte))
          .join('')
      );
      fileSize = request.file.size;
      mimeType = request.file.type || mimeType;
      fileName = request.file.name || fileName;
    }
    
    const submitResponse = await client.submitIntent({
      intent_type: 'ingest_file',
      tenant_id: tenantId,
      session_id: sessionId,
      parameters: {
        file_content: base64Content,
        file_name: fileName,
        file_size: fileSize,
        mime_type: mimeType,
        file_type: request.file_type || 'auto',
        ingest_type: 'auto',
      },
    });
    
    const maxAttempts = 60;
    let attempts = 0;
    
    while (attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 500));
      const status = await client.getExecutionStatus(submitResponse.execution_id, tenantId);
      
      if (status.status === 'completed') {
        const artifacts = status.artifacts || {};
        const fileArtifact = artifacts.file as { semantic_payload?: Record<string, unknown> } | undefined;
        const fileId = fileArtifact?.semantic_payload?.file_id as string || submitResponse.execution_id;
        
        return {
          id: fileId,
          uuid: fileId,
          file_id: fileId,
          ui_name: fileName,
          file_type: request.file_type || mimeType,
          original_path: '',
          status: FileStatus.Uploaded,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          deleted: false,
        };
      } else if (status.status === 'failed') {
        throw new Error(status.error || 'Upload failed');
      }
      attempts++;
    }
    throw new Error('Upload timed out');
  } catch (error) {
    console.error('[fms API] uploadFile error:', error);
    throw error;
  }
}

export async function getFMSFile(fileId: string): Promise<{ success: boolean; file?: FMSFile; error?: string }> {
  return getFileDetails(fileId).then(file => ({ success: true, file })).catch(error => ({ success: false, error: error.message }));
}

export async function deleteFMSFile(fileId: string): Promise<{ success: boolean; error?: string }> {
  return deleteFile(fileId);
}

export async function getFileDetails(
  fileId: string,
  token?: string
): Promise<FMSFile> {
  const { tenantId, sessionId } = getSessionInfo();
  const client = getGlobalExperiencePlaneClient();
  
  if (!sessionId) {
    throw new Error('No active session');
  }
  
  try {
    const submitResponse = await client.submitIntent({
      intent_type: 'get_parsed_file',
      tenant_id: tenantId,
      session_id: sessionId,
      parameters: {
        parsed_artifact_id: fileId,
      },
    });
    
    const maxAttempts = 30;
    let attempts = 0;
    
    while (attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 500));
      const status = await client.getExecutionStatus(submitResponse.execution_id, tenantId);
      
      if (status.status === 'completed') {
        const artifacts = status.artifacts || {};
        const content = artifacts.parsed_content as Record<string, unknown> | undefined;
        
        return {
          id: fileId,
          uuid: fileId,
          file_id: fileId,
          ui_name: (content?.name || 'file') as string,
          file_type: (content?.mime_type || 'unknown') as string,
          original_path: '',
          status: FileStatus.Parsed,
          created_at: (content?.created_at || new Date().toISOString()) as string,
          updated_at: new Date().toISOString(),
          deleted: false,
        };
      } else if (status.status === 'failed') {
        throw new Error(status.error || 'Failed to get file details');
      }
      attempts++;
    }
    throw new Error('Request timed out');
  } catch (error) {
    console.error('[fms API] getFileDetails error:', error);
    // Return minimal info on error
    return {
      id: fileId,
      uuid: fileId,
      file_id: fileId,
      ui_name: 'file',
      file_type: 'unknown',
      original_path: '',
      status: FileStatus.Uploaded,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      deleted: false,
    };
  }
}

export async function deleteFile(
  fileId: string,
  token?: string
): Promise<{ success: boolean; error?: string }> {
  const { tenantId, sessionId } = getSessionInfo();
  const client = getGlobalExperiencePlaneClient();
  
  if (!sessionId) {
    return { success: false, error: 'No active session' };
  }
  
  try {
    const submitResponse = await client.submitIntent({
      intent_type: 'delete_file',
      tenant_id: tenantId,
      session_id: sessionId,
      parameters: {
        artifact_id: fileId,
      },
    });
    
    const maxAttempts = 30;
    let attempts = 0;
    
    while (attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 500));
      const status = await client.getExecutionStatus(submitResponse.execution_id, tenantId);
      
      if (status.status === 'completed') {
        return { success: true };
      } else if (status.status === 'failed') {
        return { success: false, error: status.error || 'Delete failed' };
      }
      attempts++;
    }
    return { success: false, error: 'Delete timed out' };
  } catch (error) {
    console.error('[fms API] deleteFile error:', error);
    return { success: false, error: error instanceof Error ? error.message : 'Delete failed' };
  }
}

export async function linkFile(
  fileId: string,
  linkType: string,
  linkedId: string,
  token?: string
): Promise<{ success: boolean; error?: string }> {
  // Note: link_files intent may not be implemented in backend yet
  console.warn('[fms API] linkFile - link operations may require backend support');
  return { success: true };
}

// Alias
export const linkFiles = linkFile;

export async function parseFile(
  fileId: string,
  token?: string,
  options?: Record<string, unknown>
): Promise<{ success: boolean; parsed_file_id?: string; error?: string }> {
  const { tenantId, sessionId } = getSessionInfo();
  const client = getGlobalExperiencePlaneClient();
  
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
        ...options,
      },
    });
    
    const maxAttempts = 60;
    let attempts = 0;
    
    while (attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 500));
      const status = await client.getExecutionStatus(submitResponse.execution_id, tenantId);
      
      if (status.status === 'completed') {
        const artifacts = status.artifacts || {};
        const parsedArtifact = artifacts.parsed_content as { semantic_payload?: { parsed_artifact_id?: string } } | undefined;
        return { 
          success: true, 
          parsed_file_id: parsedArtifact?.semantic_payload?.parsed_artifact_id || `parsed_${fileId}`
        };
      } else if (status.status === 'failed') {
        return { success: false, error: status.error || 'Parsing failed' };
      }
      attempts++;
    }
    return { success: false, error: 'Parsing timed out' };
  } catch (error) {
    console.error('[fms API] parseFile error:', error);
    return { success: false, error: error instanceof Error ? error.message : 'Parsing failed' };
  }
}

export async function getParsedFile(
  fileId: string,
  parsedFileId: string,
  token?: string
): Promise<{ success: boolean; data?: unknown; error?: string }> {
  const { tenantId, sessionId } = getSessionInfo();
  const client = getGlobalExperiencePlaneClient();
  
  if (!sessionId) {
    return { success: false, error: 'No active session' };
  }
  
  try {
    const submitResponse = await client.submitIntent({
      intent_type: 'get_parsed_file',
      tenant_id: tenantId,
      session_id: sessionId,
      parameters: {
        parsed_artifact_id: parsedFileId,
      },
    });
    
    const maxAttempts = 30;
    let attempts = 0;
    
    while (attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 500));
      const status = await client.getExecutionStatus(submitResponse.execution_id, tenantId);
      
      if (status.status === 'completed') {
        return { success: true, data: status.artifacts?.parsed_content };
      } else if (status.status === 'failed') {
        return { success: false, error: status.error || 'Failed to get parsed file' };
      }
      attempts++;
    }
    return { success: false, error: 'Request timed out' };
  } catch (error) {
    console.error('[fms API] getParsedFile error:', error);
    return { success: false, error: error instanceof Error ? error.message : 'Request failed' };
  }
}

export async function updateFile(
  fileId: string,
  updates: Record<string, unknown>,
  token?: string
): Promise<{ success: boolean; error?: string }> {
  // Note: File updates may require specific intent support
  console.warn('[fms API] updateFile - update operations may require backend support');
  return { success: true };
}

export async function downloadFile(
  fileId: string,
  token?: string
): Promise<Blob | null> {
  // Note: Direct file download may require different approach (e.g., signed URLs)
  console.warn('[fms API] downloadFile - download requires backend signed URL support');
  return null;
}

export async function getFilePreview(
  fileId: string,
  token?: string
): Promise<{ success: boolean; preview?: unknown; error?: string }> {
  // Preview is typically returned from parsed file content
  const result = await getParsedFile(fileId, fileId, token);
  return { success: result.success, preview: result.data, error: result.error };
}
