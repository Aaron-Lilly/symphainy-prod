// ProcessBlueprint Types
export interface ProcessBlueprintProps {
  operationsState?: {
    optimizedWorkflow?: any;
    workflowData?: any;
    optimizedSop?: string;
    sopText?: string;
    analysisResults?: {
      errors?: Array<{ type: string; error: string }>;
      analysisType?: string;
    };
  };
  onGenerateWorkflowFromSop?: () => Promise<void>;
  onGenerateSopFromWorkflow?: () => Promise<void>;
  isLoading?: boolean;
}

export interface ProcessBlueprintState {
  sopContent: string;
  workflowContent: string;
  workflowData: any;
  analysisResults: {
    errors?: Array<{ type: string; error: string }>;
    analysisType?: string;
  } | null;
}

export interface ProcessBlueprintActions {
  formatSOPContent: (sop: any) => string;
  getSafeTextContent: (data: any) => string;
}

export interface ProcessBlueprintUIProps {
  sopContent: string;
  workflowContent: string;
  workflowData: any;
  analysisResults: {
    errors?: Array<{ type: string; error: string }>;
    analysisType?: string;
  } | null;
  isLoading: boolean;
  onGenerateWorkflowFromSop?: () => Promise<void>;
  onGenerateSopFromWorkflow?: () => Promise<void>;
  formatSOPContent: (sop: any) => string;
  getSafeTextContent: (data: any) => string;
}

export interface SOPStep {
  step_number: number;
  title: string;
  description: string;
  responsible_role?: string;
  expected_output?: string;
}

export interface SOPData {
  title: string;
  description?: string;
  steps: SOPStep[];
}

export interface WorkflowNode {
  id: string;
  label: string;
  type: string;
  metadata?: {
    design_pattern?: string;
    expected_outcome?: string;
    step_number?: number;
    responsible_role?: string;
    expected_output?: string;
  };
}

export interface WorkflowEdge {
  source: string;
  target: string;
  label?: string;
  metadata?: {
    condition?: string;
    action?: string;
  };
}

export interface WorkflowData {
  description?: string;
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
} 