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
  // Cast to unknown first then to Record to handle property mismatch between new and legacy types
  const roadmapData = response.roadmap_data as unknown as Record<string, unknown> | undefined;
  return {
    roadmap: (roadmapData?.roadmap as string) || (roadmapData?.title as string) || '',
    phases: ((roadmapData?.phases as Array<Record<string, unknown>>)?.map(phase => ({
      title: (phase.name as string) || (phase.title as string) || '',
      items: (phase.deliverables as string[]) || (phase.items as string[]) || []
    }))) || [],
    analysis_type: response.analysis_type,
    file_source: response.file_source
  };
}

export function adaptPOCResponse(response: ExperiencePOCResponse): LegacyPOCProposal {
  // Cast to unknown first then to Record to handle property mismatch between new and legacy types
  const proposal = response.poc_proposal as unknown as Record<string, unknown> | undefined;
  return {
    title: (proposal?.title as string) || 'POC Proposal',
    executive_summary: (proposal?.executive_summary as string) || (proposal?.scope as string) || '',
    business_case: (proposal?.business_case as string) || '',
    poc_scope: (proposal?.poc_scope as string[]) || (proposal?.objectives as string[]) || [],
    timeline: (proposal?.timeline as LegacyPOCProposal['timeline']) || {
      total_duration_days: 30,
      phases: []
    },
    budget: (proposal?.budget as LegacyPOCProposal['budget']) || {
      total_cost: (proposal?.estimated_cost as number) || 0,
      currency: 'USD',
      breakdown: []
    }
  };
}

export function adaptDocumentResponse(response: ExperienceDocumentResponse): LegacyDocumentResponse {
  // document_data has document_id and title, not file_path
  const docData = response.document_data as unknown as Record<string, unknown> | undefined;
  return {
    file_path: (docData?.file_path as string) || response.download_url || '',
    file_size_bytes: response.file_size_bytes,
    download_url: response.download_url,
    document_type: response.document_type
  };
}

// --- Insights Pillar Adapters ---

/**
 * Insights summary structure
 */
export interface InsightsSummary {
  summary_text?: string;
  key_findings?: string[];
  recommendations?: string[];
  visualizations?: Array<{ type: string; data: Record<string, unknown> }>;
  metadata?: Record<string, unknown>;
}

export interface LegacyInsightsData {
  summary_text: string;
  insights_summary: InsightsSummary;
}

export function adaptInsightsResponse(response: InsightsAnalysisResponse): LegacyInsightsData {
  const data = response.data as InsightsSummary | undefined;
  return {
    summary_text: data?.summary_text || '',
    insights_summary: data || {}
  };
}

// --- Operations Pillar Adapters ---

/**
 * Coexistence analysis structure
 */
export interface CoexistenceAnalysis {
  gaps?: Array<{ area: string; severity: string; description: string }>;
  recommendations?: Array<{ action: string; priority: number }>;
  summary?: string;
}

/**
 * Optimized workflow structure
 */
export interface OptimizedWorkflowData {
  workflow_id?: string;
  name?: string;
  nodes?: Array<{ id: string; type: string; label: string }>;
  edges?: Array<{ source: string; target: string }>;
  optimizations?: string[];
}

/**
 * Workflow graph data structure
 */
export interface WorkflowDataStructure {
  nodes: Array<{ id: string; type: string; label: string }>;
  edges: Array<{ source: string; target: string }>;
  metadata?: Record<string, unknown>;
}

export interface LegacyOperationsData {
  operations_coexistence: CoexistenceAnalysis;
  optimized_workflow: OptimizedWorkflowData;
  workflowData: WorkflowDataStructure;
}

export function adaptOperationsResponse(response: OperationsAPIResponse): LegacyOperationsData {
  const data = response.data as Record<string, unknown> | undefined;
  return {
    operations_coexistence: (data?.coexistence_analysis as CoexistenceAnalysis) || {},
    optimized_workflow: (data?.optimized_workflow as OptimizedWorkflowData) || {},
    workflowData: (data?.workflow_data as WorkflowDataStructure) || { nodes: [], edges: [] }
  };
}

// --- Session Adapters ---

export interface LegacySessionResponse {
  session_id: string;
  analysis_status: string;
  created_at: string;
}

/**
 * Generic session response that may come from various endpoints
 */
interface GenericSessionResponse {
  data?: {
    session_id?: string;
    analysis_status?: string;
    created_at?: string;
  };
  session_id?: string;
}

export function adaptSessionResponse(response: GenericSessionResponse): LegacySessionResponse {
  return {
    session_id: response.data?.session_id || response.session_id || '',
    analysis_status: response.data?.analysis_status || 'pending',
    created_at: response.data?.created_at || new Date().toISOString()
  };
}

// --- Utility Type Guards ---

/**
 * Base response shape for type guards
 */
interface BaseApiResponse {
  pillar?: string;
  roadmap_data?: unknown;
  poc_proposal?: unknown;
  analysis_type?: string;
}

export function isExperienceRoadmapResponse(response: unknown): response is ExperienceRoadmapResponse {
  const r = response as BaseApiResponse | null;
  return r !== null && r?.pillar === 'experience' && r?.roadmap_data !== undefined;
}

export function isExperiencePOCResponse(response: unknown): response is ExperiencePOCResponse {
  const r = response as BaseApiResponse | null;
  return r !== null && r?.pillar === 'experience' && r?.poc_proposal !== undefined;
}

export function isInsightsAnalysisResponse(response: unknown): response is InsightsAnalysisResponse {
  const r = response as BaseApiResponse | null;
  return r !== null && r?.pillar === 'insights' && r?.analysis_type !== undefined;
}

export function isOperationsAPIResponse(response: unknown): response is OperationsAPIResponse {
  const r = response as BaseApiResponse | null;
  return r !== null && r?.pillar === 'operations';
}

// --- Smart Adapter Function ---

type AdaptableResponse = 
  | ExperienceRoadmapResponse 
  | ExperiencePOCResponse 
  | InsightsAnalysisResponse 
  | OperationsAPIResponse 
  | unknown;

export function adaptResponse<T>(response: AdaptableResponse): T {
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