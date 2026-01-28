/**
 * Operations Service Types
 * 
 * Properly typed interfaces for the Operations pillar services.
 * Aligned with backend contracts and the SOPModel/WorkflowGraph definitions.
 */

import { 
  WorkflowGraph, 
  SOPModel, 
  CoexistenceBlueprint,
  CoexistenceRecommendation 
} from '../../types/responses';

// =============================================================================
// SOP and Workflow Element Types
// =============================================================================

export interface SOPElement {
  id: string;
  title: string;
  content: string;
  steps: SOPStepElement[];
  metadata?: Record<string, unknown>;
}

export interface SOPStepElement {
  id: string;
  order: number;
  title: string;
  description: string;
  responsible?: string;
  dependencies?: string[];
}

export interface WorkflowElement {
  id: string;
  name: string;
  nodes: WorkflowNodeElement[];
  edges: WorkflowEdgeElement[];
  metadata?: Record<string, unknown>;
}

export interface WorkflowNodeElement {
  id: string;
  type: string;
  label: string;
  position?: { x: number; y: number };
  data?: Record<string, unknown>;
}

export interface WorkflowEdgeElement {
  id: string;
  source: string;
  target: string;
  label?: string;
}

// =============================================================================
// Session Response Types
// =============================================================================

export interface OperationsSessionResponse {
  valid: boolean;
  action: string;
  missing?: string;
  session_state: {
    has_sop: boolean;
    has_workflow: boolean;
    section2_complete: boolean;
  };
  elements?: {
    sop: SOPElement | null;
    workflow: WorkflowElement | null;
  };
}

export interface OperationsWorkflowResponse {
  workflow: WorkflowGraph | null;
  sop: SOPModel | null;
  analysis_results?: {
    errors?: Array<{ type: string; error: string }>;
    analysis_type?: string;
  };
  session_token: string;
  status: 'success' | 'error';
  message?: string;
}

// =============================================================================
// Coexistence Types
// =============================================================================

export interface OptimizedWorkflow {
  id: string;
  name: string;
  nodes: WorkflowNodeElement[];
  edges: WorkflowEdgeElement[];
  optimizations_applied: string[];
}

export interface CoexistenceDeliverable {
  content?: {
    optimized_sop?: string;
    optimized_workflow?: OptimizedWorkflow;
  };
  summary?: string;
  recommendations?: CoexistenceRecommendation[];
  [key: string]: unknown;
}

export interface OperationsCoexistenceResponse {
  deliverable?: CoexistenceDeliverable;
  blueprint?: CoexistenceBlueprint;
  optimized_sop?: string;
  optimized_workflow?: OptimizedWorkflow;
  session_token: string;
  status: 'success' | 'error';
  message?: string;
}

// =============================================================================
// Wizard Types
// =============================================================================

export interface DraftSOP {
  id: string;
  title: string;
  content: string;
  steps: SOPStepElement[];
  status: 'draft' | 'review' | 'approved';
}

export interface OperationsWizardResponse {
  agent_response: string;
  draft_sop?: DraftSOP;
  sop?: SOPModel;
  workflow?: WorkflowGraph;
  session_token: string;
  status: 'success' | 'error';
  message?: string;
}

// =============================================================================
// Error Types
// =============================================================================

export interface OperationsErrorResponse {
  message: string;
  operation: 'sop_to_workflow' | 'workflow_to_sop' | 'coexistence_analysis' | 'wizard_start' | 'wizard_chat' | 'wizard_publish';
  code?: string;
  file_uuid?: string;
  details?: Record<string, unknown>;
}

// =============================================================================
// Request Types
// =============================================================================

export interface SOPContent {
  title?: string;
  sections?: Array<{
    title: string;
    content: string;
  }>;
  steps?: SOPStepElement[];
}

export interface WorkflowContent {
  nodes?: WorkflowNodeElement[];
  edges?: WorkflowEdgeElement[];
  metadata?: Record<string, unknown>;
}

export interface WorkflowOptions {
  include_swimlanes?: boolean;
  include_decision_points?: boolean;
  output_format?: 'bpmn' | 'json';
}

export interface SOPOptions {
  include_responsibilities?: boolean;
  include_dependencies?: boolean;
  output_format?: 'markdown' | 'json';
}

export interface WorkflowGenerationRequest {
  sopFileUuid?: string;
  sopContent?: SOPContent;
  workflowOptions?: WorkflowOptions;
  sessionToken: string;
  userId?: string;
  sessionId?: string;
}

export interface SopGenerationRequest {
  workflowFileUuid?: string;
  workflowContent?: WorkflowContent;
  sopOptions?: SOPOptions;
  sessionToken: string;
  userId?: string;
  sessionId?: string;
}

export interface AnalysisOptions {
  depth?: 'quick' | 'standard' | 'deep';
  include_recommendations?: boolean;
  include_gap_analysis?: boolean;
}

export interface CoexistenceAnalysisRequest {
  sessionToken: string;
  sopInputFileUuid?: string;
  workflowInputFileUuid?: string;
  sopContent?: string | SOPContent;
  workflowContent?: WorkflowContent;
  currentState?: Record<string, unknown>;
  targetState?: Record<string, unknown>;
  analysisOptions?: AnalysisOptions;
  userId?: string;
  sessionId?: string;
}

export interface CoexistenceContentRequest {
  sessionToken: string;
  sopContent: string;
  workflowContent: WorkflowContent;
}

export interface WizardRequest {
  sessionToken: string;
  userMessage?: string;
}

export interface BlueprintSaveRequest {
  blueprint: CoexistenceBlueprint;
  userId: string;
}

// =============================================================================
// Query and Conversation Types
// =============================================================================

export interface QueryContext {
  current_operation?: string;
  selected_files?: string[];
  analysis_type?: string;
}

export interface OperationsQueryRequest {
  session_id: string;
  query: string;
  file_url?: string;
  context?: QueryContext;
}

export interface ConversationContext {
  history?: Array<{ role: string; content: string }>;
  current_step?: string;
  artifacts?: string[];
}

export interface OperationsConversationRequest {
  session_id: string;
  message: string;
  context?: ConversationContext;
}

// =============================================================================
// State Types
// =============================================================================

export interface SelectedOperationsItem {
  id: string;
  type: 'sop' | 'workflow' | 'file';
  name: string;
  data?: SOPElement | WorkflowElement | Record<string, unknown>;
}

export interface OperationsFile {
  uuid: string;
  filename: string;
  file_type: string;
  status: string;
  upload_date: string;
}

export interface OperationsState {
  selected: {
    [type: string]: SelectedOperationsItem | null;
  };
  loading: {
    isLoading: boolean;
    operation?: string;
    progress?: number;
    message?: string;
  };
  error: OperationsErrorResponse | null;
  success?: string;
  journey: "select" | "wizard" | null;
  operationFiles: OperationsFile[];
  isLoadingFiles: boolean;
  initialized: boolean;
}

// =============================================================================
// Liaison Event Types
// =============================================================================

export interface OperationsLiaisonEventData {
  query?: string;
  operation?: string;
  files?: OperationsFile[];
  context?: QueryContext | ConversationContext;
}

export interface OperationsLiaisonEvent {
  type: 'operations_analysis_request' | 'operations_query_request' | 'operations_wizard_request';
  session_token: string;
  agent_type: 'operations_liaison';
  pillar: 'operations';
  data: OperationsLiaisonEventData;
} 