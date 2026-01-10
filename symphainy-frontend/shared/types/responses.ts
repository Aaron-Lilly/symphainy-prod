/**
 * Standardized Response Types
 * Matches backend response models for consistent API contracts
 */

// Base response interface
export interface StandardResponse<T = any> {
  status: 'success' | 'error';
  data: T;
  message: string;
  pillar: string;
  version: string;
  timestamp: string;
}

// Error response interface
export interface ErrorResponse {
  status: 'error';
  data: any;
  message: string;
  pillar: string;
  version: string;
  timestamp: string;
  error_code: string;
  error_details?: Record<string, any>;
  retry_after?: number;
}

// --- Insights Response Types ---
export interface InsightsResponse extends StandardResponse {
  pillar: 'insights';
}

export interface InsightsSessionResponse extends InsightsResponse {
  session_id: string;
  session_status: string;
}

export interface InsightsAnalysisResponse extends InsightsResponse {
  analysis_type: string;
  analysis_status: string;
  processing_time_ms?: number;
}

export interface InsightsErrorResponse extends ErrorResponse {
  pillar: 'insights';
}

// --- Operations Response Types ---
export interface OperationsResponse extends StandardResponse {
  pillar: 'operations';
}

export interface OperationsWorkflowResponse extends OperationsResponse {
  operation_type: string;
  workflow_data: any; // WorkflowGraph
  sop_data?: any; // SOPModel
}

export interface OperationsCoexistenceResponse extends OperationsResponse {
  coexistence_analysis: any; // CoexistenceBlueprint
  optimization_status: string;
  recommendations_count: number;
}

export interface OperationsWizardResponse extends OperationsResponse {
  wizard_session_id: string;
  wizard_status: string;
  current_step?: string;
  total_steps?: number;
}

export interface OperationsErrorResponse extends ErrorResponse {
  pillar: 'operations';
}

// --- Experience Response Types ---
export interface ExperienceResponse extends StandardResponse {
  pillar: 'experience';
}

export interface ExperienceRoadmapResponse extends ExperienceResponse {
  roadmap_data: any; // RoadmapData
  analysis_type: string;
  file_source?: string;
}

export interface ExperiencePOCResponse extends ExperienceResponse {
  poc_proposal: any; // POCProposal
  proposal_type: string;
  includes_insights: boolean;
  includes_operations: boolean;
}

export interface ExperienceSessionResponse extends ExperienceResponse {
  session_data: any; // ExperienceSession
  session_status: string;
  available_operations: string[];
}

export interface ExperienceDocumentResponse extends ExperienceResponse {
  document_data: any; // POCDocumentResponse
  document_type: string;
  file_size_bytes: number;
  download_url?: string;
}

export interface ExperienceErrorResponse extends ErrorResponse {
  pillar: 'experience';
}

// --- Content Response Types ---
export interface ContentResponse extends StandardResponse {
  pillar: 'content';
}

export interface ContentFileListResponse extends ContentResponse {
  files: any[]; // FileMetadataResponse[]
  total_count: number;
  page_size?: number;
  page_number?: number;
}

export interface ContentFileUploadResponse extends ContentResponse {
  upload_event: any; // FileUploadEvent
  file_metadata: any; // FileMetadataResponse
  upload_status: string;
  processing_status: string;
}

export interface ContentFileAnalysisResponse extends ContentResponse {
  analysis_result: any; // ContentAnalysisResult
  analysis_type: string;
  processing_time_ms?: number;
}

export interface ContentFilePreviewResponse extends ContentResponse {
  preview_data: any; // FilePreviewData
  preview_available: boolean;
  file_type: string;
  preview_format?: string;
}

export interface ContentSessionResponse extends ContentResponse {
  session_data: any; // ContentSession
  session_status: string;
  file_count: number;
}

export interface ContentErrorResponse extends ErrorResponse {
  pillar: 'content';
}

// --- Union Types for API Functions ---
export type InsightsAPIResponse = 
  | InsightsResponse 
  | InsightsSessionResponse 
  | InsightsAnalysisResponse 
  | InsightsErrorResponse;

export type OperationsAPIResponse = 
  | OperationsResponse 
  | OperationsWorkflowResponse 
  | OperationsCoexistenceResponse 
  | OperationsWizardResponse 
  | OperationsErrorResponse;

export type ExperienceAPIResponse = 
  | ExperienceResponse 
  | ExperienceRoadmapResponse 
  | ExperiencePOCResponse 
  | ExperienceSessionResponse 
  | ExperienceDocumentResponse 
  | ExperienceErrorResponse;

export type ContentAPIResponse = 
  | ContentResponse 
  | ContentFileListResponse 
  | ContentFileUploadResponse 
  | ContentFileAnalysisResponse 
  | ContentFilePreviewResponse 
  | ContentSessionResponse 
  | ContentErrorResponse;

// --- Legacy Support Types ---
// These maintain backward compatibility with existing frontend code
export interface LegacyStartSessionResponse {
  session_token: string;
  message: string;
}

export interface LegacyAgentMessageResponse {
  type: "agent_message";
  content: string;
  metadata?: Record<string, any>;
}

export interface LegacyActionRequiredResponse {
  type: "action_required";
  action: string;
  message: string;
  metadata?: Record<string, any>;
}

export type LegacyAGUIResponse =
  | LegacyAgentMessageResponse
  | LegacyActionRequiredResponse
  | { type: string; [key: string]: any }; 