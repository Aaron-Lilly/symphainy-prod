/**
 * Type Adapters for Response Compatibility
 * 
 * These adapters provide backward compatibility between our new standardized
 * response types and existing component expectations, ensuring a smooth
 * transition without breaking existing functionality.
 */

import type {
  ExperienceRoadmapResponse,
  ExperiencePOCResponse,
  ExperienceDocumentResponse,
  InsightsAnalysisResponse,
  OperationsAPIResponse
} from './responses';

// --- Experience Pillar Adapters ---

export interface LegacyRoadmapData {
  roadmap: string;
  phases: Array<{ title: string; items: string[] }>;
  analysis_type: string;
  file_source?: string;
}

export interface LegacyPOCProposal {
  title: string;
  executive_summary: string;
  business_case: string;
  poc_scope: string[];
  timeline: {
    total_duration_days: number;
    phases: Array<{ name: string; duration_days: number }>;
  };
  budget: {
    total_cost: number;
    currency: string;
    breakdown: Array<{ item: string; cost: number }>;
  };
}

export interface LegacyDocumentResponse {
  file_path: string;
  file_size_bytes: number;
  download_url?: string;
  document_type: string;
}

// Adapter functions
export function adaptRoadmapResponse(response: ExperienceRoadmapResponse): LegacyRoadmapData {
  return {
    roadmap: response.roadmap_data?.roadmap || '',
    phases: response.roadmap_data?.phases || [],
    analysis_type: response.analysis_type,
    file_source: response.file_source
  };
}

export function adaptPOCResponse(response: ExperiencePOCResponse): LegacyPOCProposal {
  const proposal = response.poc_proposal;
  return {
    title: proposal?.title || 'POC Proposal',
    executive_summary: proposal?.executive_summary || '',
    business_case: proposal?.business_case || '',
    poc_scope: proposal?.poc_scope || [],
    timeline: proposal?.timeline || {
      total_duration_days: 30,
      phases: []
    },
    budget: proposal?.budget || {
      total_cost: 0,
      currency: 'USD',
      breakdown: []
    }
  };
}

export function adaptDocumentResponse(response: ExperienceDocumentResponse): LegacyDocumentResponse {
  return {
    file_path: response.document_data?.file_path || '',
    file_size_bytes: response.file_size_bytes,
    download_url: response.download_url,
    document_type: response.document_type
  };
}

// --- Insights Pillar Adapters ---

export interface LegacyInsightsData {
  summary_text: string;
  insights_summary: any;
}

export function adaptInsightsResponse(response: InsightsAnalysisResponse): LegacyInsightsData {
  return {
    summary_text: response.data?.summary_text || '',
    insights_summary: response.data
  };
}

// --- Operations Pillar Adapters ---

export interface LegacyOperationsData {
  operations_coexistence: any;
  optimized_workflow: any;
  workflowData: any;
}

export function adaptOperationsResponse(response: OperationsAPIResponse): LegacyOperationsData {
  return {
    operations_coexistence: response.data?.coexistence_analysis || {},
    optimized_workflow: response.data?.optimized_workflow || {},
    workflowData: response.data?.workflow_data || {}
  };
}

// --- Session Adapters ---

export interface LegacySessionResponse {
  session_id: string;
  analysis_status: string;
  created_at: string;
}

export function adaptSessionResponse(response: any): LegacySessionResponse {
  return {
    session_id: response.data?.session_id || response.session_id || '',
    analysis_status: response.data?.analysis_status || 'pending',
    created_at: response.data?.created_at || new Date().toISOString()
  };
}

// --- Utility Type Guards ---

export function isExperienceRoadmapResponse(response: any): response is ExperienceRoadmapResponse {
  return response && response.pillar === 'experience' && response.roadmap_data;
}

export function isExperiencePOCResponse(response: any): response is ExperiencePOCResponse {
  return response && response.pillar === 'experience' && response.poc_proposal;
}

export function isInsightsAnalysisResponse(response: any): response is InsightsAnalysisResponse {
  return response && response.pillar === 'insights' && response.analysis_type;
}

export function isOperationsAPIResponse(response: any): response is OperationsAPIResponse {
  return response && response.pillar === 'operations';
}

// --- Smart Adapter Function ---

export function adaptResponse<T>(response: any): T {
  if (isExperienceRoadmapResponse(response)) {
    return adaptRoadmapResponse(response) as T;
  }
  if (isExperiencePOCResponse(response)) {
    return adaptPOCResponse(response) as T;
  }
  if (isInsightsAnalysisResponse(response)) {
    return adaptInsightsResponse(response) as T;
  }
  if (isOperationsAPIResponse(response)) {
    return adaptOperationsResponse(response) as T;
  }
  
  // Fallback: return response as-is
  return response as T;
} 