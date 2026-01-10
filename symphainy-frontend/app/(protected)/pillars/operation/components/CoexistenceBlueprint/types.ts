// CoexistenceBlueprint Types
export interface CoexistenceDeliverable {
  content?: {
    optimized_sop?: string;
    optimized_workflow?: any;
  };
  [key: string]: any;
}

export interface OptimizeResponse {
  deliverable?: CoexistenceDeliverable;
  blueprint?: any;
  optimized_sop?: string;
  optimized_workflow?: any;
}

export interface CoexistenceBlueprintProps {
  sopText?: string | any;
  workflowData?: any;
  generatedSopUuid?: string;
  generatedWorkflowUuid?: string;
  selectedSopFileUuid?: string | null;
  selectedWorkflowFileUuid?: string | null;
  sessionToken?: string;
  sessionState?: any;
  isEnabled?: boolean;
}

export interface CoexistenceBlueprintState {
  loading: boolean;
  error: string | null;
  optimizedSop: string | null;
  optimizedWorkflow: any | null;
  blueprint: any | null;
}

export interface CoexistenceBlueprintActions {
  handleOptimize: () => Promise<void>;
  handleSaveBlueprint: () => Promise<void>;
  formatSOPContent: (sop: any) => string;
  formatWorkflowContent: (workflow: any) => string;
  getSafeFormattedContent: (data: any, type: 'sop' | 'workflow') => string;
}

export interface CoexistenceBlueprintUIProps {
  loading: boolean;
  error: string | null;
  optimizedSop: string | null;
  optimizedWorkflow: any | null;
  blueprint: any | null;
  sopText?: string | any;
  workflowData?: any;
  isEnabled: boolean;
  onOptimize: () => Promise<void>;
  onSaveBlueprint: () => Promise<void>;
  formatSOPContent: (sop: any) => string;
  formatWorkflowContent: (workflow: any) => string;
  getSafeFormattedContent: (data: any, type: 'sop' | 'workflow') => string;
}

export interface BlueprintSaveRequest {
  blueprint: any;
  userId: string;
}

export interface BlueprintSaveResponse {
  blueprint_id: string;
}

export interface OptimizationRequest {
  sessionToken: string;
  sopContent: string;
  workflowContent: any;
}

export interface OptimizationResponse {
  deliverable?: CoexistenceDeliverable;
  blueprint?: any;
  optimized_sop?: string;
  optimized_workflow?: any;
  status: 'success' | 'error';
  message?: string;
} 