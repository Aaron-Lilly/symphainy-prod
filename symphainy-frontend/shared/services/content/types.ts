/**
 * Content Service Types
 * Type definitions for content service functionality
 */

export interface SimpleFileData {
  id: string;
  user_id: string;
  ui_name: string;
  file_type: string;
  mime_type: string;
  original_path: string;
  status: string;
  metadata: any;
  created_at: string;
  updated_at: string;
}

export interface ParseFileRequest {
  file_id: string;
  user_id?: string;
  session_token?: string;
}

export interface ParseFileResponse {
  file_id: string;
  workflow_id?: string;
  result: any;
  message: string;
}

export interface AnalyzeFileRequest {
  file_id: string;
  analysis_type?: string;
  user_id?: string;
  session_token?: string;
}

export interface AnalyzeFileResponse {
  file_id: string;
  workflow_id?: string;
  result: any;
  message: string;
}

export interface FilePreviewData {
  content: string;
  metadata: any;
  file_info: any;
}

export interface FileAnalysisData {
  analysis_results: any;
  insights: any;
  recommendations: any;
}

export interface ContentSessionStatus {
  session_token: string;
  files: SimpleFileData[];
  current_file?: string;
  status: 'active' | 'inactive' | 'error';
}

export interface ContentSessionUpdate {
  current_file?: string;
  status?: string;
  metadata?: any;
} 