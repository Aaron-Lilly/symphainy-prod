// Operations Service Types
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
    sop: any;
    workflow: any;
  };
}

export interface OperationsWorkflowResponse {
  workflow: any;
  sop: any;
  analysis_results?: {
    errors?: Array<{ type: string; error: string }>;
    analysis_type?: string;
  };
  session_token: string;
  status: 'success' | 'error';
  message?: string;
}

export interface OperationsCoexistenceResponse {
  deliverable?: {
    content?: {
      optimized_sop?: string;
      optimized_workflow?: any;
    };
    [key: string]: any;
  };
  blueprint?: any;
  optimized_sop?: string;
  optimized_workflow?: any;
  session_token: string;
  status: 'success' | 'error';
  message?: string;
}

export interface OperationsWizardResponse {
  agent_response: string;
  draft_sop?: any;
  sop?: any;
  workflow?: any;
  session_token: string;
  status: 'success' | 'error';
  message?: string;
}

export interface OperationsErrorResponse {
  message: string;
  operation: 'sop_to_workflow' | 'workflow_to_sop' | 'coexistence_analysis' | 'wizard_start' | 'wizard_chat' | 'wizard_publish';
  code?: string;
  file_uuid?: string;
  details?: any;
}

export interface WorkflowGenerationRequest {
  sopFileUuid?: string;
  sopContent?: Record<string, any>;
  workflowOptions?: Record<string, any>;
  sessionToken: string;
  userId?: string;
  sessionId?: string;
}

export interface SopGenerationRequest {
  workflowFileUuid?: string;
  workflowContent?: Record<string, any>;
  sopOptions?: Record<string, any>;
  sessionToken: string;
  userId?: string;
  sessionId?: string;
}

export interface CoexistenceAnalysisRequest {
  sessionToken: string;
  sopInputFileUuid?: string;
  workflowInputFileUuid?: string;
  sopContent?: string | Record<string, any>;
  workflowContent?: Record<string, any>;
  currentState?: Record<string, any>;
  targetState?: Record<string, any>;
  analysisOptions?: Record<string, any>;
  userId?: string;
  sessionId?: string;
}

export interface CoexistenceContentRequest {
  sessionToken: string;
  sopContent: string;
  workflowContent: any;
}

export interface WizardRequest {
  sessionToken: string;
  userMessage?: string;
}

export interface BlueprintSaveRequest {
  blueprint: any;
  userId: string;
}

export interface OperationsQueryRequest {
  session_id: string;
  query: string;
  file_url?: string;
  context?: any;
}

export interface OperationsConversationRequest {
  session_id: string;
  message: string;
  context?: any;
}

export interface OperationsState {
  selected: {
    [type: string]: any | null;
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
  operationFiles: any[];
  isLoadingFiles: boolean;
  initialized: boolean;
}

export interface OperationsLiaisonEvent {
  type: 'operations_analysis_request' | 'operations_query_request' | 'operations_wizard_request';
  session_token: string;
  agent_type: 'operations_liaison';
  pillar: 'operations';
  data: {
    query?: string;
    operation?: string;
    files?: any[];
    context?: any;
  };
} 