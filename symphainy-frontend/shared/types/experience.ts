/**
 * Experience Pillar Types
 * Aligned with backend Pydantic models in experience_model.py
 */

// Roadmap Models
export interface RoadmapPhase {
  phase: string;  // e.g., "Phase 1: Foundation (Weeks 1-4)"
  title: string;  // e.g., "Data Integration & Initial Insights"
  items: string[];  // List of bullet points for the phase
}

export interface RoadmapData {
  roadmap: string;  // Raw roadmap text from agent
  phases?: RoadmapPhase[];  // Parsed phases
  generated_at?: string;
  file_url?: string;  // Source file that was analyzed
}

// POC Proposal Models
export interface POCBudget {
  total_cost: number;
  currency: string;
  payment_schedule: Array<{
    milestone: string;
    percentage: number;
    amount: number;
  }>;
  includes: string[];
  excludes: string[];
}

export interface POCTimeline {
  total_duration_days: number;
  start_date: string;  // ISO format
  end_date: string;  // ISO format
  phases: Array<{
    phase: string;
    duration_days: number;
    deliverables: string[];
  }>;
}

export interface POCRiskAssessment {
  risk: string;
  impact: string;  // "Low", "Medium", "High"
  probability: string;  // "Low", "Medium", "High"
  mitigation: string;
}

export interface POCResourceRequirements {
  client_team: string[];
  symphainy_team: string[];
  infrastructure: string[];
}

export interface POCProposal {
  title: string;
  executive_summary: string;
  business_case: string;
  poc_scope: string[];
  timeline: POCTimeline;
  budget: POCBudget;
  success_metrics: string[];
  risk_assessment: POCRiskAssessment[];
  resource_requirements: POCResourceRequirements;
  next_steps: string;
  generated_at: string;
  proposal_valid_until: string;
  data_sources?: Record<string, boolean>;  // Which data sources were used
}

// Experience Session Models
export interface ExperienceSession {
  session_id: string;
  selected_file?: Record<string, any>;
  roadmap_result?: RoadmapData;
  poc_proposal?: POCProposal;
  analysis_status: "pending" | "in_progress" | "completed" | "error";
  created_at: string;
  updated_at: string;
}

// Experience Analysis Models
export interface ExperienceAnalysis {
  agent_type: string;  // "RoadmapAgent", "ScopingAgent", "WorkspaceAgent", "SeniorSolutionArchitectAgent"
  analysis_data: Record<string, any>;
  status: "pending" | "in_progress" | "completed" | "error";
  error_message?: string;
  generated_at: string;
}

// Request/Response Models
export interface RoadmapAnalysisRequest {
  file_url: string;
  session_token?: string;
}

export interface RoadmapAnalysisResponse {
  roadmap: string;
  phases?: RoadmapPhase[];
  status: "success" | "error";
  error_message?: string;
}

export interface POCProposalRequest {
  insights_summary?: Record<string, any>;
  operations_coexistence?: Record<string, any>;
  roadmap_data?: Record<string, any>;
  business_context?: string;
  budget_range?: "economy" | "standard" | "premium";
  timeline_preference?: "60_days" | "90_days" | "120_days";
}

export interface POCDocumentRequest {
  poc_proposal: POCProposal;
  format: "docx" | "pdf";
}

export interface POCDocumentResponse {
  file_path?: string;
  file_size: number;
  format: string;
  generated_at: string;
  error?: string;
}

// Error Models
export interface ExperienceError {
  error_type: "validation_error" | "processing_error" | "agent_error";
  message: string;
  details?: Record<string, any>;
  timestamp: string;
}

// Legacy types for backward compatibility
export interface ExperienceResult {
  // Legacy interface - consider migrating to ExperienceSession
  [key: string]: any;
}
