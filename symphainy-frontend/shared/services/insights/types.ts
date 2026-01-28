/**
 * Insights Service Types
 * Type definitions for insights service functionality
 */

export interface InsightsSessionResponse {
  session_id: string;
  status: string;
  message: string;
  data?: any;
}

export interface InsightsAnalysisResponse {
  success: boolean;
  data?: any;
  error?: string;
  session_id?: string;
  workflow_id?: string;
}

export interface InsightsSummaryResponse {
  summary: string;
  key_insights: string[];
  recommendations: string[];
  visualizations?: any[];
  metadata?: any;
}

export interface VARKInsightsRequest {
  session_token: string;
  file_uuid?: string;
  learning_style: LearningStyleType;
  user_query?: string;
  additional_context?: any;
}

export interface BusinessSummaryRequest {
  session_token: string;
  file_uuid?: string;
  analysis_results?: any;
  user_insights?: string[];
  include_recommendations?: boolean;
}

export interface CrossPillarIntegrationRequest {
  session_token: string;
  insights_summary: any;
  target_pillar?: string;
  integration_type?: string;
}

export interface SmartCityInsightsRequest {
  session_token?: string;
  user_id?: string;
  file_url?: string;
  additional_info?: string;
  context?: any;
}

export interface AGUIEvent {
  type: string;
  session_token: string;
  [key: string]: any;
}

export interface FileUrlRequest {
  file_url: string;
}

export enum LearningStyleType {
  TABULAR = "tabular",
  VISUAL = "visual"
}

export interface InsightsSessionState {
  session_id: string;
  status: 'active' | 'inactive' | 'error';
  current_file?: string;
  analysis_results?: any;
  vark_preferences?: LearningStyleType;
}

export interface InsightsSessionUpdate {
  current_file?: string;
  status?: string;
  analysis_results?: any;
  vark_preferences?: LearningStyleType;
}

// ============================================================================
// Data Mapping Types
// ============================================================================

// Backend returns the mapping result directly (no separate response/result split)
export interface DataMappingResponse {
  success: boolean;
  mapping_id: string;
  mapping_type: "unstructured_to_structured" | "structured_to_structured";
  mapping_rules: MappingRule[];
  mapped_data: {
    success: boolean;
    transformed_data?: any;
    output_file_id?: string;
    transformation_metadata?: {
      fields_mapped?: number;
      fields_unmapped?: number;
      confidence_avg?: number;
    };
    error?: string;
  };
  data_quality?: {
    success: boolean;
    validation_results: Array<{
      record_id: string;
      record_index: number;
      is_valid: boolean;
      quality_score: number;
      issues: QualityIssue[];
      missing_fields: string[];
      invalid_fields: string[];
      warnings: string[];
    }>;
    summary: {
      total_records: number;
      valid_records: number;
      invalid_records: number;
      overall_quality_score: number;
      pass_rate: number;
      common_issues: Array<{
        issue_type: string;
        field: string;
        count: number;
        percentage: number;
      }>;
    };
    has_issues: boolean;
    error?: string;
  };
  cleanup_actions?: CleanupAction[];
  output_file_id?: string;
  citations?: Array<{
    field: string;
    source: string;
    location: string;
    confidence: number;
  }>;
  confidence_scores?: Record<string, number>;
  metadata: {
    source_file_id: string;
    target_file_id: string;
    mapping_timestamp: string;
    workflow_id?: string;
  };
  workflow_id?: string;
  error?: string;
  // Extended field for runtime result
  mapping_result?: any;
}

// Alias for backward compatibility
export type DataMappingResultsResponse = DataMappingResponse;

export interface MappingRule {
  source_field: string;
  target_field: string;
  confidence: number;
  extraction_method: "llm" | "regex" | "semantic";
  transformation?: string;
}

export interface Citation {
  field: string;
  source: string;
  location: string;
  confidence: number;
}

// Backend quality_results structure (matches data_quality from backend)
export interface QualityReport {
  success: boolean;
  validation_results: Array<{
    record_id: string;
    record_index: number;
    is_valid: boolean;
    quality_score: number;
    issues: QualityIssue[];
    missing_fields: string[];
    invalid_fields: string[];
    warnings: string[];
  }>;
  summary: {
    total_records: number;
    valid_records: number;
    invalid_records: number;
    overall_quality_score: number;
    pass_rate: number;
    common_issues: Array<{
      issue_type: string;
      field: string;
      count: number;
      percentage: number;
    }>;
  };
  has_issues: boolean;
  error?: string;
}

// Helper interface for frontend display (derived from backend structure)
export interface QualityReportDisplay {
  overall_score: number;
  pass_rate: number;
  completeness: number;  // Calculated from validation_results
  accuracy: number;  // Calculated from validation_results
  record_count: number;
  quality_issues: QualityIssue[];
  metrics: {
    total_records: number;
    passed_records: number;
    failed_records: number;
    records_with_issues: number;
  };
}

export interface QualityIssue {
  record_id?: string;  // May not be present in all contexts
  field: string;
  issue_type: "missing" | "missing_required" | "invalid_type" | "invalid_format" | "out_of_range";
  severity: "high" | "medium" | "low" | "error" | "warning";
  message: string;
  suggested_fix?: string;
  source_field?: string;
  target_field?: string;
  source_value?: any;
  expected_type?: string;
  expected_format?: string;
}

export interface CleanupAction {
  action_id: string;
  priority: "high" | "medium" | "low";
  action_type: "fix_missing" | "fix_format" | "fix_type" | "transform";
  description: string;
  affected_records: number;
  example_fix: string;
  suggested_transformation?: string;
}

export interface DataMappingOptions {
  mapping_type?: "auto" | "unstructured_to_structured" | "structured_to_structured";
  quality_validation?: boolean;
  min_confidence?: number;
  include_citations?: boolean;
}

// ============================================================================
// Permit Semantic Object (PSO) Types
// ============================================================================

export interface PermitSemanticObject {
  pso_id: string;
  permit_id: string;
  permit_type: "air_quality" | "water_discharge" | "construction" | "waste_management" | "other";
  issuing_authority: string;
  jurisdiction: string;
  legal_citations: string[];
  effective_period: {
    start?: string;
    end?: string;
  };
  covered_entities: string[];
  obligations: Obligation[];
  source_provenance?: SourceProvenance;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Obligation {
  obligation_id: string;
  obligation_type: "reporting" | "threshold" | "notification" | "operational" | "other";
  action: string;
  trigger?: string;
  condition?: string;
  metric?: string;
  threshold?: any;
  unit?: string;
  frequency?: string;
  deadline?: string;
  enforcement_reference?: string;
  confidence: number;
  source_provenance?: SourceProvenance;
  metadata?: Record<string, any>;
}

export interface SourceProvenance {
  document_id: string;
  page_numbers: number[];
  section_reference?: string;
  extraction_method: string;
  confidence: number;
  timestamp: string;
}

export interface PermitProcessingRequest {
  permit_file_id: string;
  target_systems: TargetSystem[];
  processing_options?: PermitProcessingOptions;
}

export interface TargetSystem {
  system: "compliance" | "task_management" | "environmental" | "erp";
  target_file_id: string;
}

export interface PermitProcessingOptions {
  include_citations?: boolean;
  validation_level?: "strict" | "moderate" | "lenient";
}

export interface PermitProcessingResponse {
  success: boolean;
  workflow_id: string;
  pso_id: string;
  permit_id: string;
  permit_type: string;
  obligations_count: number;
  mapping_results: SystemMappingResult[];
  validation_result: PSOValidationResult;
  report: MappingReport;
  metadata: {
    permit_file_id: string;
    target_systems: string[];
    processing_timestamp: string;
  };
  error?: string;
}

export interface SystemMappingResult {
  success: boolean;
  system: string;
  output_file_id?: string;
  error?: string;
  mapping_id?: string;
  mapping_type?: string;
}

export interface PSOValidationResult {
  valid: boolean;
  issues: string[];
  obligations_count: number;
  citations_count: number;
}

export interface MappingReport {
  pso_id: string;
  permit_id: string;
  validation: PSOValidationResult;
  mapping_summary: {
    total_systems: number;
    successful: number;
    failed: number;
  };
  mapping_details: Array<{
    system: string;
    success: boolean;
    output_file_id?: string;
    error?: string;
  }>;
  generated_at: string;
} 