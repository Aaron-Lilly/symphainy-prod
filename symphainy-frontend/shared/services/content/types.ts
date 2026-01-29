/**
 * Content Service Types
 * Type definitions for content service functionality
 */

/**
 * File metadata structure
 */
export interface SimpleFileMetadata {
  content_type?: string;
  file_type_category?: string;
  row_count?: number;
  column_count?: number;
  parsed?: boolean;
  embedded?: boolean;
  custom_fields?: Record<string, unknown>;
}

export interface SimpleFileData {
  id: string;
  user_id: string;
  ui_name: string;
  file_type: string;
  mime_type: string;
  original_path: string;
  status: string;
  metadata: SimpleFileMetadata;
  created_at: string;
  updated_at: string;
}

export interface ParseFileRequest {
  file_id: string;
  user_id?: string;
  session_token?: string;
}

/**
 * Parse result structure
 */
export interface ParseResult {
  success: boolean;
  parsed_file_id?: string;
  parsed_content?: {
    content_type?: string;
    row_count?: number;
    column_count?: number;
    columns?: Array<{ name: string; type: string }>;
    sample_data?: unknown[][];
  };
  error?: string;
}

export interface ParseFileResponse {
  file_id: string;
  workflow_id?: string;
  result: ParseResult;
  message: string;
}

export interface AnalyzeFileRequest {
  file_id: string;
  analysis_type?: string;
  user_id?: string;
  session_token?: string;
}

/**
 * Analysis result structure
 */
export interface AnalysisResult {
  success: boolean;
  analysis_type?: string;
  summary?: string;
  findings?: string[];
  metrics?: Record<string, number>;
  visualizations?: Array<{ type: string; config: Record<string, unknown> }>;
  error?: string;
}

export interface AnalyzeFileResponse {
  file_id: string;
  workflow_id?: string;
  result: AnalysisResult;
  message: string;
}

/**
 * Preview metadata structure
 */
export interface PreviewMetadata {
  preview_type: 'text' | 'table' | 'binary';
  truncated: boolean;
  total_rows?: number;
  total_columns?: number;
}

/**
 * File info structure for preview
 */
export interface PreviewFileInfo {
  file_id: string;
  file_name: string;
  file_type: string;
  file_size?: number;
}

export interface FilePreviewData {
  content: string;
  metadata: PreviewMetadata;
  file_info: PreviewFileInfo;
}

/**
 * Analysis results structure
 */
export interface AnalysisResults {
  data_summary?: string;
  schema?: Record<string, string>;
  statistics?: Record<string, number>;
  quality_score?: number;
}

/**
 * File insights structure
 */
export interface FileInsights {
  key_findings?: string[];
  data_patterns?: string[];
  anomalies?: string[];
  summary?: string;
}

/**
 * Analysis recommendations structure
 */
export interface AnalysisRecommendations {
  next_steps?: string[];
  suggested_analyses?: string[];
  data_quality_improvements?: string[];
}

export interface FileAnalysisData {
  analysis_results: AnalysisResults;
  insights: FileInsights;
  recommendations: AnalysisRecommendations;
}

export interface ContentSessionStatus {
  session_token: string;
  files: SimpleFileData[];
  current_file?: string;
  status: 'active' | 'inactive' | 'error';
}

/**
 * Session update metadata
 */
export interface SessionUpdateMetadata {
  operation?: string;
  progress?: number;
  artifacts?: string[];
}

export interface ContentSessionUpdate {
  current_file?: string;
  status?: string;
  metadata?: SessionUpdateMetadata;
} 