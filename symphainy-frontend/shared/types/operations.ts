// Core Operations Types

export interface WorkflowNode {
  id: string;
  label: string;
  type?: string;
  metadata?: Record<string, any>;
}

export interface WorkflowEdge {
  from: string;
  to: string;
  label?: string;
  metadata?: Record<string, any>;
}

export interface WorkflowGraph {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  name?: string;
  version?: string;
  description?: string;
}

// API Response Types
export interface SOPToWorkflowResponse {
  sop_text: string;
  workflow: WorkflowGraph;
}

export interface WorkflowToSOPResponse {
  workflow_text: string;
  sop: string;
}

export interface CoexistenceAnalysisResponse {
  workflow_text: string;
  sop_text: string;
  coexistence_analysis: string;
  optimized_sop?: string;
  optimized_workflow?: WorkflowGraph;
}

// Error Types
export interface APIError {
  message: string;
  code?: string;
  details?: any;
}

export interface OperationsError extends APIError {
  operation: 'sop_to_workflow' | 'workflow_to_sop' | 'coexistence_analysis' | 'roadmap_analysis' | 'wizard_start' | 'wizard_chat' | 'wizard_publish';
  file_uuid?: string;
}

// Loading States
export interface LoadingState {
  isLoading: boolean;
  operation?: string;
  progress?: number;
  message?: string;
}

// File Selection Types
export interface FileSelection {
  SOP: string | null;
  workflow: string | null;
}

export interface FileSelectionState {
  selected: FileSelection;
  available: {
    SOP: Array<{ uuid: string; name: string; type: string }>;
    workflow: Array<{ uuid: string; name: string; type: string }>;
  };
}

// Operations Journey Types
export type OperationsJourney = 'select' | 'wizard' | 'analysis' | 'results' | null;

export interface OperationsState {
  journey: OperationsJourney;
  loading: LoadingState;
  error: OperationsError | null;
  results: {
    sopToWorkflow?: SOPToWorkflowResponse;
    workflowToSop?: WorkflowToSOPResponse;
    coexistence?: CoexistenceAnalysisResponse;
  };
  fileSelection: FileSelectionState;
}

// Validation Types
export interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

export interface FileValidationResult extends ValidationResult {
  file_uuid: string;
  file_type: 'SOP' | 'workflow';
  supported_formats: string[];
} 