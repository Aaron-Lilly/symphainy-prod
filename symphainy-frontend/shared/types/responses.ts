/**
 * Standardized Response Types
 * Matches backend response models for consistent API contracts
 * 
 * Note: Uses Record<string, unknown> for dynamic data that varies by context,
 * with specific types defined where structure is known.
 */

import { FileMetadata } from './file';
import { 
  WorkflowArtifact, 
  SOPArtifact, 
  RoadmapArtifact, 
  POCArtifact,
  ExecutionStatusResponse as RuntimeExecutionStatus 
} from './runtime-contracts';

// Base response interface with generic type parameter
export interface StandardResponse<T = unknown> {
  status: 'success' | 'error';
  data: T;
  message: string;
  pillar: string;
  version: string;
  timestamp: string;
}

// Error response interface with properly typed fields
export interface ErrorResponse {
  status: 'error';
  data: null;
  message: string;
  pillar: string;
  version: string;
  timestamp: string;
  error_code: string;
  error_details?: Record<string, unknown>;
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

/**
 * Workflow graph structure for operations responses
 */
export interface WorkflowGraph {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  metadata?: Record<string, unknown>;
}

export interface WorkflowNode {
  id: string;
  type: string;
  label: string;
  data?: Record<string, unknown>;
  position?: { x: number; y: number };
}

export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
}

/**
 * SOP model structure
 */
export interface SOPModel {
  id: string;
  title: string;
  steps: SOPStep[];
  metadata?: Record<string, unknown>;
}

export interface SOPStep {
  id: string;
  order: number;
  title: string;
  description: string;
  responsible?: string;
  dependencies?: string[];
}

/**
 * Coexistence blueprint structure
 */
export interface CoexistenceBlueprint {
  id: string;
  current_state: Record<string, unknown>;
  target_state: Record<string, unknown>;
  gaps: CoexistenceGap[];
  recommendations: CoexistenceRecommendation[];
}

export interface CoexistenceGap {
  id: string;
  area: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
}

export interface CoexistenceRecommendation {
  id: string;
  gap_id: string;
  action: string;
  priority: number;
  effort: 'low' | 'medium' | 'high';
}

export interface OperationsWorkflowResponse extends OperationsResponse {
  operation_type: string;
  workflow_data: WorkflowGraph;
  sop_data?: SOPModel;
}

export interface OperationsCoexistenceResponse extends OperationsResponse {
  coexistence_analysis: CoexistenceBlueprint;
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

/**
 * Roadmap data structure
 */
export interface RoadmapData {
  id: string;
  title: string;
  phases: RoadmapPhaseData[];
  goals: string[];
  estimated_duration_weeks: number;
  created_at: string;
}

export interface RoadmapPhaseData {
  id: string;
  name: string;
  description: string;
  duration_weeks: number;
  milestones: RoadmapMilestoneData[];
  deliverables: string[];
}

export interface RoadmapMilestoneData {
  id: string;
  title: string;
  target_date: string;
  status: 'pending' | 'in_progress' | 'completed';
}

/**
 * POC proposal structure
 */
export interface POCProposal {
  id: string;
  title: string;
  objectives: string[];
  scope: string;
  requirements: POCRequirementData[];
  timeline: POCTimelineData;
  resources: POCResourceData[];
  estimated_cost?: number;
  risk_assessment?: Record<string, unknown>;
}

export interface POCRequirementData {
  id: string;
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  category: string;
}

export interface POCTimelineData {
  start_date: string;
  end_date: string;
  duration_weeks: number;
  phases: { name: string; duration: string }[];
}

export interface POCResourceData {
  id: string;
  name: string;
  type: 'human' | 'technical' | 'financial';
  allocation: number;
}

/**
 * Experience session data structure
 */
export interface ExperienceSessionData {
  session_id: string;
  created_at: string;
  last_activity: string;
  source_files: string[];
  current_state: 'initialized' | 'analyzing' | 'generating' | 'completed';
  artifacts: string[];
}

/**
 * Document response structure
 */
export interface DocumentResponseData {
  document_id: string;
  title: string;
  content_type: string;
  content: string;
  format: 'pdf' | 'docx' | 'markdown' | 'html';
  generated_at: string;
}

export interface ExperienceRoadmapResponse extends ExperienceResponse {
  roadmap_data: RoadmapData;
  analysis_type: string;
  file_source?: string;
}

export interface ExperiencePOCResponse extends ExperienceResponse {
  poc_proposal: POCProposal;
  proposal_type: string;
  includes_insights: boolean;
  includes_operations: boolean;
}

export interface ExperienceSessionResponse extends ExperienceResponse {
  session_data: ExperienceSessionData;
  session_status: string;
  available_operations: string[];
}

export interface ExperienceDocumentResponse extends ExperienceResponse {
  document_data: DocumentResponseData;
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

/**
 * File upload event structure
 */
export interface FileUploadEvent {
  event_id: string;
  file_id: string;
  event_type: 'upload_started' | 'upload_completed' | 'upload_failed';
  timestamp: string;
  details?: Record<string, unknown>;
}

/**
 * Content analysis result structure
 */
export interface ContentAnalysisResult {
  analysis_id: string;
  file_id: string;
  analysis_type: 'schema' | 'content' | 'quality';
  results: {
    summary: string;
    findings: AnalysisFinding[];
    metrics: Record<string, number>;
  };
  confidence_score: number;
}

export interface AnalysisFinding {
  type: string;
  severity: 'info' | 'warning' | 'error';
  message: string;
  location?: string;
}

/**
 * File preview data structure
 */
export interface FilePreviewData {
  file_id: string;
  preview_type: 'text' | 'table' | 'image' | 'binary';
  content: string | string[][];
  truncated: boolean;
  total_rows?: number;
  total_columns?: number;
}

/**
 * Content session data structure
 */
export interface ContentSessionData {
  session_id: string;
  created_at: string;
  files: string[];
  current_operation?: string;
  state: Record<string, unknown>;
}

export interface ContentFileListResponse extends ContentResponse {
  files: FileMetadata[];
  total_count: number;
  page_size?: number;
  page_number?: number;
}

export interface ContentFileUploadResponse extends ContentResponse {
  upload_event: FileUploadEvent;
  file_metadata: FileMetadata;
  upload_status: string;
  processing_status: string;
}

export interface ContentFileAnalysisResponse extends ContentResponse {
  analysis_result: ContentAnalysisResult;
  analysis_type: string;
  processing_time_ms?: number;
}

export interface ContentFilePreviewResponse extends ContentResponse {
  preview_data: FilePreviewData;
  preview_available: boolean;
  file_type: string;
  preview_format?: string;
}

export interface ContentSessionResponse extends ContentResponse {
  session_data: ContentSessionData;
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
  metadata?: Record<string, unknown>;
}

export interface LegacyActionRequiredResponse {
  type: "action_required";
  action: string;
  message: string;
  metadata?: Record<string, unknown>;
}

/**
 * Legacy AGUI response types for backward compatibility
 */
export interface LegacyGenericResponse {
  type: string;
  data?: unknown;
  metadata?: Record<string, unknown>;
}

export type LegacyAGUIResponse =
  | LegacyAgentMessageResponse
  | LegacyActionRequiredResponse
  | LegacyGenericResponse; 