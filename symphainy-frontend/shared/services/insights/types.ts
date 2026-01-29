/**
 * Insights Service Types
 * Type definitions for insights service functionality
 */

/**
 * Insights session data structure
 */
export interface InsightsSessionData {
  current_file?: string;
  analysis_status?: string;
  results?: Record<string, unknown>;
}

export interface InsightsSessionResponse {
  session_id: string;
  status: string;
  message: string;
  data?: InsightsSessionData;
}

/**
 * Analysis result data structure
 */
export interface AnalysisResultData {
  summary?: string;
  findings?: string[];
  visualizations?: VisualizationConfig[];
  metadata?: Record<string, unknown>;
}

export interface InsightsAnalysisResponse {
  success: boolean;
  data?: AnalysisResultData;
  error?: string;
  session_id?: string;
  workflow_id?: string;
}

/**
 * Visualization configuration
 */
export interface VisualizationConfig {
  type: 'chart' | 'table' | 'graph' | 'map';
  config: Record<string, unknown>;
  data?: unknown[];
}

/**
 * Summary metadata structure
 */
export interface SummaryMetadata {
  source_files?: string[];
  analysis_type?: string;
  generated_at?: string;
  confidence_score?: number;
}

export interface InsightsSummaryResponse {
  summary: string;
  key_insights: string[];
  recommendations: string[];
  visualizations?: VisualizationConfig[];
  metadata?: SummaryMetadata;
}

/**
 * Additional context for VARK insights
 */
export interface VARKAdditionalContext {
  file_context?: string;
  user_preferences?: Record<string, unknown>;
  previous_insights?: string[];
}

export interface VARKInsightsRequest {
  session_token: string;
  file_uuid?: string;
  learning_style: LearningStyleType;
  user_query?: string;
  additional_context?: VARKAdditionalContext;
}

/**
 * Analysis results for business summary
 */
export interface BusinessAnalysisResults {
  data_summary?: string;
  key_metrics?: Record<string, number>;
  trends?: string[];
  anomalies?: string[];
}

export interface BusinessSummaryRequest {
  session_token: string;
  file_uuid?: string;
  analysis_results?: BusinessAnalysisResults;
  user_insights?: string[];
  include_recommendations?: boolean;
}

/**
 * Insights summary for cross-pillar integration
 */
export interface CrossPillarInsightsSummary {
  summary_text: string;
  key_findings: string[];
  data_context?: Record<string, unknown>;
}

export interface CrossPillarIntegrationRequest {
  session_token: string;
  insights_summary: CrossPillarInsightsSummary;
  target_pillar?: string;
  integration_type?: string;
}

/**
 * Smart city context structure
 */
export interface SmartCityContext {
  department?: string;
  data_type?: string;
  priority?: string;
  additional_params?: Record<string, unknown>;
}

export interface SmartCityInsightsRequest {
  session_token?: string;
  user_id?: string;
  file_url?: string;
  additional_info?: string;
  context?: SmartCityContext;
}

/**
 * AGUI event data structure
 */
export interface AGUIEventData {
  action?: string;
  parameters?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
}

export interface AGUIEvent {
  type: string;
  session_token: string;
  data?: AGUIEventData;
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
  analysis_results?: AnalysisResultData;
  vark_preferences?: LearningStyleType;
}

export interface InsightsSessionUpdate {
  current_file?: string;
  status?: string;
  analysis_results?: AnalysisResultData;
  vark_preferences?: LearningStyleType;
}

// ============================================================================
// Data Mapping Types
// ============================================================================

/**
 * Transformed data structure from mapping
 */
export interface TransformedData {
  records: Array<Record<string, unknown>>;
  schema?: Record<string, string>;
  row_count?: number;
}

// Backend returns the mapping result directly (no separate response/result split)
export interface DataMappingResponse {
  success: boolean;
  mapping_id: string;
  mapping_type: "unstructured_to_structured" | "structured_to_structured";
  mapping_rules: MappingRule[];
  mapped_data: {
    success: boolean;
    transformed_data?: TransformedData;
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
  mapping_result?: Record<string, unknown>;
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
  source_value?: string | number | boolean | null;
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

/**
 * Permit metadata structure
 */
export interface PermitMetadata {
  classification?: string;
  review_status?: string;
  last_reviewed?: string;
  reviewer?: string;
  notes?: string[];
  custom_fields?: Record<string, unknown>;
}

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
  metadata?: PermitMetadata;
  created_at: string;
  updated_at: string;
}

/**
 * Threshold value structure
 */
export interface ThresholdValue {
  value: number;
  unit?: string;
  comparator?: 'lt' | 'lte' | 'gt' | 'gte' | 'eq';
  min?: number;
  max?: number;
}

/**
 * Obligation metadata structure
 */
export interface ObligationMetadata {
  priority?: 'low' | 'medium' | 'high' | 'critical';
  category?: string;
  review_notes?: string;
  automated?: boolean;
}

export interface Obligation {
  obligation_id: string;
  obligation_type: "reporting" | "threshold" | "notification" | "operational" | "other";
  action: string;
  trigger?: string;
  condition?: string;
  metric?: string;
  threshold?: ThresholdValue;
  unit?: string;
  frequency?: string;
  deadline?: string;
  enforcement_reference?: string;
  confidence: number;
  source_provenance?: SourceProvenance;
  metadata?: ObligationMetadata;
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