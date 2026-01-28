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

export async function getFMSFile(fileId: string): Promise<{ success: boolean; file?: FMSFile; error?: string }> {
  console.warn('[fms API] getFMSFile - stub implementation');
  return { success: true };
}

export async function deleteFMSFile(fileId: string): Promise<{ success: boolean; error?: string }> {
  console.warn('[fms API] deleteFMSFile - stub implementation');
  return { success: true };
}
