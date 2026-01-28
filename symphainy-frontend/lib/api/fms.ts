/**
 * FMS (File Management System) API Module
 * 
 * Stub implementation for file management operations.
 */

export interface FMSFile {
  id: string;
  uuid?: string;
  filename?: string;
  ui_name?: string;
  file_type: string;
  original_path?: string;
  size?: number;
  file_size?: number;
  status?: string;
  created_at?: string;
  upload_timestamp?: string;
  [key: string]: any;
}

export interface FMSUploadResponse {
  success: boolean;
  file_id?: string;
  error?: string;
}

export async function uploadToFMS(file: File): Promise<FMSUploadResponse> {
  console.warn('[fms API] uploadToFMS - stub implementation');
  return { success: true, file_id: `fms_${Date.now()}` };
}

export async function listFMSFiles(userId?: string): Promise<any[]> {
  console.warn('[fms API] listFMSFiles - stub implementation');
  return [];
}

// Alias for backward compatibility
export const listFiles = listFMSFiles;

export async function uploadFile(
  request: any,
  token?: string
): Promise<any> {
  console.warn('[fms API] uploadFile - stub implementation');
  return {
    uuid: `file_${Date.now()}`,
    file_id: `file_${Date.now()}`,
    ui_name: request?.filename || 'uploaded_file',
    file_type: request?.file_type || 'unknown',
    original_path: '',
    status: 'uploaded',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    deleted: false
  };
}

export async function getFMSFile(fileId: string): Promise<{ success: boolean; file?: FMSFile; error?: string }> {
  console.warn('[fms API] getFMSFile - stub implementation');
  return { success: true };
}

export async function deleteFMSFile(fileId: string): Promise<{ success: boolean; error?: string }> {
  console.warn('[fms API] deleteFMSFile - stub implementation');
  return { success: true };
}

export async function getFileDetails(
  fileId: string,
  token?: string
): Promise<any> {
  console.warn('[fms API] getFileDetails - stub implementation');
  return {
    uuid: fileId,
    file_id: fileId,
    ui_name: 'file',
    file_type: 'unknown',
    original_path: '',
    status: 'completed',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    deleted: false
  };
}

export async function deleteFile(
  fileId: string,
  token?: string
): Promise<{ success: boolean; error?: string }> {
  console.warn('[fms API] deleteFile - stub implementation');
  return { success: true };
}

export async function linkFile(
  fileId: string,
  linkType: string,
  linkedId: string,
  token?: string
): Promise<{ success: boolean; error?: string }> {
  console.warn('[fms API] linkFile - stub implementation');
  return { success: true };
}

// Alias
export const linkFiles = linkFile;

export async function parseFile(
  fileId: string,
  token?: string,
  options?: any
): Promise<{ success: boolean; parsed_file_id?: string; error?: string }> {
  console.warn('[fms API] parseFile - stub implementation');
  return { success: true, parsed_file_id: `parsed_${fileId}` };
}

export async function getParsedFile(
  fileId: string,
  parsedFileId: string,
  token?: string
): Promise<{ success: boolean; data?: any; error?: string }> {
  console.warn('[fms API] getParsedFile - stub implementation');
  return { success: true, data: {} };
}

export async function updateFile(
  fileId: string,
  updates: any,
  token?: string
): Promise<any> {
  console.warn('[fms API] updateFile - stub implementation');
  return { success: true };
}

export async function downloadFile(
  fileId: string,
  token?: string
): Promise<Blob | null> {
  console.warn('[fms API] downloadFile - stub implementation');
  return null;
}

export async function getFilePreview(
  fileId: string,
  token?: string
): Promise<{ success: boolean; preview?: any; error?: string }> {
  console.warn('[fms API] getFilePreview - stub implementation');
  return { success: true, preview: {} };
}
