/**
 * Enhanced File Processor Types
 * Type definitions for enhanced file processing component
 */

export interface EnhancedFileProcessorProps {
  file: {
    id: string;
    filename: string;
    file_type: string;
    status: string;
    created_at: string;
    metadata?: any;
  };
  onProcessingComplete?: (result: EnhancedFileProcessingResponse) => void;
  onError?: (error: string) => void;
  className?: string;
}

export interface ProcessingState {
  isProcessing: boolean;
  isComplete: boolean;
  error: string | null;
  processingTime: number;
  result: EnhancedFileProcessingResponse | null;
}

export interface MetadataDisplay {
  content_type: string;
  data_structure: {
    type: string;
    tables?: Array<{
      table_id: string;
      columns: string[];
      row_count: number;
      column_count: number;
    }>;
    text_length?: number;
    has_text_content?: boolean;
  };
  content_patterns: {
    has_id_columns?: boolean;
    has_date_columns?: boolean;
    has_email_columns?: boolean;
    has_numeric_columns?: boolean;
  };
  business_context: {
    domain: string;
    data_category: string;
    business_relevance: string;
  };
  data_quality: {
    completeness_score: number;
    consistency_score: number;
    accuracy_score: number;
    overall_score: number;
  };
}

export interface EnhancedFileProcessingResponse {
  success: boolean;
  file_id: string;
  filename: string;
  file_type: string;
  processing_time_seconds: number;
  parsing_result: {
    document_type: string;
    tables?: Array<{
      table_id: string;
      columns: string[];
      row_count: number;
      column_count: number;
    }>;
    text?: string;
  };
  metadata: MetadataDisplay;
  lineage: any;
  storage: any;
}




