/**
 * MVP Solution Service Types
 * 
 * Types for MVP Solution Orchestrator API interactions
 */

export interface SolutionPillar {
  name: "content" | "insights" | "operations" | "business-outcomes";
  enabled: boolean;
  priority: number; // 1-4, lower is higher priority
  navigation_order: number;
  customizations: {
    focus_areas?: string[];
    workflows?: string[];
    data_types?: string[];
  };
}

export interface SolutionStructure {
  pillars: SolutionPillar[];
  recommended_data_types: string[];
  strategic_focus: string;
  customization_options: {
    workflow_creation: boolean;
    interactive_guidance: boolean;
    automated_analysis: boolean;
  };
}

export interface SolutionReasoning {
  analysis: string;
  key_insights: string[];
  recommendations: string[];
  confidence: number; // 0.0-1.0
}

export interface SolutionStructureResponse {
  success: boolean;
  solution_structure: SolutionStructure;
  reasoning: SolutionReasoning;
  workflow_id?: string;
  error?: string;
}

export interface UserCustomizations {
  pillars?: Partial<SolutionPillar>[];
  recommended_data_types?: string[];
  strategic_focus?: string;
  customization_options?: Partial<SolutionStructure["customization_options"]>;
}

export interface CustomizeSolutionResponse {
  success: boolean;
  solution_structure: SolutionStructure;
  customizations_applied: UserCustomizations;
  workflow_id?: string;
  error?: string;
}

export interface MVPSessionResponse {
  success: boolean;
  session_id?: string;
  workflow_id?: string;
  error?: string;
}

export interface PillarNavigationResponse {
  success: boolean;
  pillar_context?: {
    pillar: string;
    session_id: string;
    available_actions: string[];
  };
  workflow_id?: string;
  error?: string;
}











