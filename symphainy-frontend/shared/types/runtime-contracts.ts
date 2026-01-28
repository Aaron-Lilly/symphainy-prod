/**
 * Runtime Contract Types
 * 
 * CANONICAL TYPE DEFINITIONS - Generated from backend Pydantic models
 * Source: symphainy_coexistence_fabric/symphainy_platform/runtime/runtime_api.py
 * 
 * DO NOT add `any` types to this file.
 * All types must exactly match the backend contracts.
 */

// =============================================================================
// SESSION TYPES
// =============================================================================

/**
 * Request to create a session (anonymous or authenticated)
 * Maps to: SessionCreateRequest in runtime_api.py
 */
export interface SessionCreateRequest {
  intent_type?: string; // Default: "create_session"
  tenant_id?: string | null; // Optional for anonymous sessions
  user_id?: string | null; // Optional for anonymous sessions
  session_id?: string | null;
  execution_contract?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
}

/**
 * Response from session creation
 * Maps to: SessionCreateResponse in runtime_api.py
 */
export interface SessionCreateResponse {
  session_id: string;
  tenant_id?: string | null;
  user_id?: string | null;
  created_at: string;
}

/**
 * Full session object with state
 */
export interface Session {
  session_id: string;
  tenant_id: string | null;
  user_id: string | null;
  created_at: string;
  metadata?: Record<string, unknown>;
  state?: Record<string, unknown>;
}

// =============================================================================
// INTENT TYPES
// =============================================================================

/**
 * Request to submit an intent
 * Maps to: IntentSubmitRequest in runtime_api.py
 */
export interface IntentSubmitRequest {
  intent_id?: string | null;
  intent_type: string;
  tenant_id: string;
  session_id: string;
  solution_id: string;
  parameters?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
}

/**
 * Response from intent submission
 * Maps to: IntentSubmitResponse in runtime_api.py
 */
export interface IntentSubmitResponse {
  execution_id: string;
  intent_id: string;
  status: IntentStatus;
  created_at: string;
}

/**
 * Intent status values
 */
export type IntentStatus = 'accepted' | 'rejected' | 'pending' | 'processing';

// =============================================================================
// EXECUTION TYPES
// =============================================================================

/**
 * Response from execution status query
 * Maps to: ExecutionStatusResponse in runtime_api.py
 */
export interface ExecutionStatusResponse {
  execution_id: string;
  status: ExecutionStatus;
  intent_id: string;
  artifacts?: Record<string, unknown>;
  events?: ExecutionEvent[];
  error?: string | null;
}

/**
 * Execution status values
 */
export type ExecutionStatus = 
  | 'pending' 
  | 'running' 
  | 'completed' 
  | 'failed' 
  | 'cancelled';

/**
 * Execution event
 */
export interface ExecutionEvent {
  event_type: string;
  timestamp: string;
  data?: Record<string, unknown>;
}

// =============================================================================
// ARTIFACT TYPES
// =============================================================================

/**
 * Request to resolve an artifact
 * Maps to: ArtifactResolveRequest in runtime_api.py
 */
export interface ArtifactResolveRequest {
  artifact_id: string;
  artifact_type: string;
  tenant_id: string;
}

/**
 * Response from artifact resolution
 * Maps to: ArtifactResolveResponse in runtime_api.py
 */
export interface ArtifactResolveResponse {
  artifact_id: string;
  artifact_type: string;
  tenant_id: string;
  lifecycle_state: ArtifactLifecycleState;
  semantic_descriptor: SemanticDescriptor;
  materializations: Materialization[];
  parent_artifacts: string[];
  produced_by: ProducedBy;
  created_at: string;
  updated_at: string;
}

/**
 * Artifact lifecycle states
 */
export type ArtifactLifecycleState = 'draft' | 'active' | 'archived';

/**
 * Semantic descriptor for an artifact
 */
export interface SemanticDescriptor {
  name?: string;
  description?: string;
  tags?: string[];
  [key: string]: unknown;
}

/**
 * Materialization of an artifact
 */
export interface Materialization {
  materialization_type: string;
  location: string;
  format?: string;
  metadata?: Record<string, unknown>;
}

/**
 * Produced by information
 */
export interface ProducedBy {
  intent_type: string;
  execution_id: string;
}

/**
 * Request to list artifacts
 * Maps to: ArtifactListRequest in runtime_api.py
 */
export interface ArtifactListRequest {
  tenant_id: string;
  artifact_type?: string | null;
  lifecycle_state?: ArtifactLifecycleState | null;
  eligible_for?: string | null; // Next intent that needs this artifact
  limit?: number; // Default: 100
  offset?: number; // Default: 0
}

/**
 * Single artifact in list response
 * Maps to: ArtifactListItem in runtime_api.py
 */
export interface ArtifactListItem {
  artifact_id: string;
  artifact_type: string;
  lifecycle_state: ArtifactLifecycleState;
  semantic_descriptor: SemanticDescriptor;
  created_at: string;
  updated_at: string;
}

/**
 * Response from artifact listing
 * Maps to: ArtifactListResponse in runtime_api.py
 */
export interface ArtifactListResponse {
  artifacts: ArtifactListItem[];
  total: number;
  limit: number;
  offset: number;
}

// =============================================================================
// PENDING INTENT TYPES
// =============================================================================

/**
 * Request to list pending intents
 * Maps to: PendingIntentListRequest in runtime_api.py
 */
export interface PendingIntentListRequest {
  tenant_id: string;
  target_artifact_id?: string | null;
  intent_type?: string | null;
}

/**
 * Single pending intent in list response
 * Maps to: PendingIntentItem in runtime_api.py
 */
export interface PendingIntentItem {
  intent_id: string;
  intent_type: string;
  status: string;
  target_artifact_id?: string | null;
  context: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

/**
 * Response from pending intent listing
 * Maps to: PendingIntentListResponse in runtime_api.py
 */
export interface PendingIntentListResponse {
  intents: PendingIntentItem[];
  total: number;
}

/**
 * Request to create pending intent
 * Maps to: PendingIntentCreateRequest in runtime_api.py
 */
export interface PendingIntentCreateRequest {
  intent_id?: string | null; // Auto-generated if not provided
  intent_type: string;
  target_artifact_id: string;
  context: Record<string, unknown>; // ingestion_profile, parse_options, etc.
  tenant_id: string;
  user_id?: string | null;
  session_id?: string | null;
}

/**
 * Response from pending intent creation
 * Maps to: PendingIntentCreateResponse in runtime_api.py
 */
export interface PendingIntentCreateResponse {
  intent_id: string;
  status: string;
}

// =============================================================================
// REALM-SPECIFIC ARTIFACT TYPES
// =============================================================================

/**
 * Content realm file artifact
 */
export interface FileArtifact {
  artifact_id: string;
  artifact_type: 'file';
  tenant_id: string;
  lifecycle_state: ArtifactLifecycleState;
  semantic_descriptor: FileSemanticDescriptor;
  materializations: FileMaterialization[];
  parent_artifacts: string[];
  produced_by: ProducedBy;
  created_at: string;
  updated_at: string;
}

export interface FileSemanticDescriptor {
  name: string;
  original_filename: string;
  mime_type: string;
  size_bytes: number;
  description?: string;
  tags?: string[];
}

export interface FileMaterialization {
  materialization_type: 'raw_file' | 'parsed_content' | 'embeddings';
  location: string;
  format: string;
  metadata?: Record<string, unknown>;
}

/**
 * Content realm parsed content artifact
 */
export interface ParsedContentArtifact {
  artifact_id: string;
  artifact_type: 'parsed_content';
  tenant_id: string;
  lifecycle_state: ArtifactLifecycleState;
  semantic_descriptor: ParsedContentSemanticDescriptor;
  materializations: ParsedContentMaterialization[];
  parent_artifacts: string[]; // Reference to source file artifact
  produced_by: ProducedBy;
  created_at: string;
  updated_at: string;
}

export interface ParsedContentSemanticDescriptor {
  name: string;
  source_file_id: string;
  content_type: string;
  row_count?: number;
  column_count?: number;
  columns?: ColumnDescriptor[];
  description?: string;
  tags?: string[];
}

export interface ColumnDescriptor {
  name: string;
  data_type: string;
  nullable: boolean;
  description?: string;
}

export interface ParsedContentMaterialization {
  materialization_type: 'structured_data' | 'text_chunks';
  location: string;
  format: 'json' | 'parquet' | 'csv';
  metadata?: Record<string, unknown>;
}

/**
 * Content realm embeddings artifact
 */
export interface EmbeddingsArtifact {
  artifact_id: string;
  artifact_type: 'embeddings';
  tenant_id: string;
  lifecycle_state: ArtifactLifecycleState;
  semantic_descriptor: EmbeddingsSemanticDescriptor;
  materializations: EmbeddingsMaterialization[];
  parent_artifacts: string[]; // Reference to parsed content artifact
  produced_by: ProducedBy;
  created_at: string;
  updated_at: string;
}

export interface EmbeddingsSemanticDescriptor {
  name: string;
  source_content_id: string;
  model: string;
  dimensions: number;
  chunk_count: number;
  description?: string;
  tags?: string[];
}

export interface EmbeddingsMaterialization {
  materialization_type: 'vector_index';
  location: string;
  format: string;
  metadata?: {
    index_type?: string;
    distance_metric?: string;
  };
}

// =============================================================================
// INSIGHTS REALM TYPES
// =============================================================================

/**
 * Insights realm analysis artifact
 */
export interface AnalysisArtifact {
  artifact_id: string;
  artifact_type: 'analysis';
  tenant_id: string;
  lifecycle_state: ArtifactLifecycleState;
  semantic_descriptor: AnalysisSemanticDescriptor;
  materializations: AnalysisMaterialization[];
  parent_artifacts: string[]; // Reference to source data artifacts
  produced_by: ProducedBy;
  created_at: string;
  updated_at: string;
}

export interface AnalysisSemanticDescriptor {
  name: string;
  analysis_type: 'eda' | 'visualization' | 'business' | 'anomaly';
  source_artifacts: string[];
  summary?: string;
  description?: string;
  tags?: string[];
}

export interface AnalysisMaterialization {
  materialization_type: 'analysis_result' | 'visualization';
  location: string;
  format: 'json' | 'html' | 'svg' | 'png';
  metadata?: Record<string, unknown>;
}

// =============================================================================
// JOURNEY REALM TYPES
// =============================================================================

/**
 * Journey realm workflow artifact
 */
export interface WorkflowArtifact {
  artifact_id: string;
  artifact_type: 'workflow';
  tenant_id: string;
  lifecycle_state: ArtifactLifecycleState;
  semantic_descriptor: WorkflowSemanticDescriptor;
  materializations: WorkflowMaterialization[];
  parent_artifacts: string[];
  produced_by: ProducedBy;
  created_at: string;
  updated_at: string;
}

export interface WorkflowSemanticDescriptor {
  name: string;
  workflow_type: 'bpmn' | 'custom';
  step_count: number;
  description?: string;
  tags?: string[];
}

export interface WorkflowMaterialization {
  materialization_type: 'workflow_definition';
  location: string;
  format: 'bpmn' | 'json';
  metadata?: Record<string, unknown>;
}

/**
 * Journey realm SOP artifact
 */
export interface SOPArtifact {
  artifact_id: string;
  artifact_type: 'sop';
  tenant_id: string;
  lifecycle_state: ArtifactLifecycleState;
  semantic_descriptor: SOPSemanticDescriptor;
  materializations: SOPMaterialization[];
  parent_artifacts: string[]; // Reference to source workflow
  produced_by: ProducedBy;
  created_at: string;
  updated_at: string;
}

export interface SOPSemanticDescriptor {
  name: string;
  source_workflow_id?: string;
  step_count: number;
  description?: string;
  tags?: string[];
}

export interface SOPMaterialization {
  materialization_type: 'sop_document';
  location: string;
  format: 'markdown' | 'pdf' | 'docx';
  metadata?: Record<string, unknown>;
}

// =============================================================================
// OUTCOMES REALM TYPES
// =============================================================================

/**
 * Outcomes realm roadmap artifact
 */
export interface RoadmapArtifact {
  artifact_id: string;
  artifact_type: 'roadmap';
  tenant_id: string;
  lifecycle_state: ArtifactLifecycleState;
  semantic_descriptor: RoadmapSemanticDescriptor;
  materializations: RoadmapMaterialization[];
  parent_artifacts: string[];
  produced_by: ProducedBy;
  created_at: string;
  updated_at: string;
}

export interface RoadmapSemanticDescriptor {
  name: string;
  goals: string[];
  phase_count: number;
  estimated_duration_weeks?: number;
  description?: string;
  tags?: string[];
}

export interface RoadmapMaterialization {
  materialization_type: 'roadmap_document';
  location: string;
  format: 'json' | 'markdown';
  metadata?: Record<string, unknown>;
}

/**
 * Outcomes realm POC artifact
 */
export interface POCArtifact {
  artifact_id: string;
  artifact_type: 'poc';
  tenant_id: string;
  lifecycle_state: ArtifactLifecycleState;
  semantic_descriptor: POCSemanticDescriptor;
  materializations: POCMaterialization[];
  parent_artifacts: string[];
  produced_by: ProducedBy;
  created_at: string;
  updated_at: string;
}

export interface POCSemanticDescriptor {
  name: string;
  objectives: string[];
  scope: string;
  deliverables: string[];
  estimated_duration_weeks: number;
  description?: string;
  tags?: string[];
}

export interface POCMaterialization {
  materialization_type: 'poc_document';
  location: string;
  format: 'json' | 'markdown';
  metadata?: Record<string, unknown>;
}

// =============================================================================
// UTILITY TYPES
// =============================================================================

/**
 * Generic API response wrapper
 */
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: ApiError;
}

/**
 * API error structure
 */
export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

/**
 * Pagination parameters
 */
export interface PaginationParams {
  limit?: number;
  offset?: number;
}

/**
 * Paginated response
 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}
