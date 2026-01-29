/**
 * Experience Service Types
 * 
 * Properly typed interfaces for the Experience pillar services.
 * Aligned with backend contracts and runtime-contracts.ts definitions.
 */

import { 
  RoadmapData, 
  RoadmapPhaseData, 
  RoadmapMilestoneData,
  POCProposal,
  DocumentResponseData 
} from '../../types/responses';

// =============================================================================
// Session Types
// =============================================================================

export interface ExperienceSessionResponse {
  session_id: string;
  status: string;
  message: string;
  data?: ExperienceSessionData;
}

export interface ExperienceSessionData {
  created_at: string;
  last_activity: string;
  current_phase: string;
  artifacts_generated: string[];
}

// =============================================================================
// Roadmap Types
// =============================================================================

export interface ExperienceRoadmapResponse {
  roadmap: RoadmapData;
  timeline: RoadmapPhaseData[];
  milestones: RoadmapMilestoneData[];
  recommendations: string[];
  session_token: string;
  status: 'success' | 'error';
  message?: string;
}

// =============================================================================
// POC Types
// =============================================================================

export interface ExperiencePOCResponse {
  poc_proposal: POCProposal;
  requirements: string[];
  timeline: string;
  resources: string[];
  session_token: string;
  status: 'success' | 'error';
  message?: string;
}

// =============================================================================
// Document Types
// =============================================================================

export interface ExperienceDocumentResponse {
  document: DocumentResponseData;
  format: string;
  content: string;
  session_token: string;
  status: 'success' | 'error';
  message?: string;
}

// =============================================================================
// Error Types
// =============================================================================

export interface ExperienceErrorResponse {
  message: string;
  operation: 'roadmap_generation' | 'poc_generation' | 'document_generation' | 'session_management';
  code?: string;
  details?: Record<string, unknown>;
}

// =============================================================================
// Source File Types
// =============================================================================

export interface SourceFile {
  uuid: string;
  filename: string;
  file_type: string;
  file_size: number;
  upload_date: string;
  status: string;
  metadata?: SourceFileMetadata;
}

export interface SourceFileMetadata {
  content_type?: string;
  row_count?: number;
  column_count?: number;
  parsed?: boolean;
  analysis_status?: string;
}

// =============================================================================
// Context Types
// =============================================================================

export interface AdditionalContext {
  id: string;
  type: string;
  content: string | Record<string, unknown>;
  priority: 'low' | 'medium' | 'high';
  timestamp: string;
}

export interface AdditionalContextRequest {
  session_token: string;
  context_type: string;
  context_data: Record<string, unknown>;
  priority: 'low' | 'medium' | 'high';
}

// =============================================================================
// Session State Types
// =============================================================================

export interface InsightsData {
  analysis_results: Record<string, unknown>;
  visualizations?: string[];
  summary?: string;
}

export interface OperationsData {
  workflows: string[];
  sops: string[];
  coexistence_analysis?: Record<string, unknown>;
}

export interface ExperienceSessionState {
  session_id: string;
  status: 'active' | 'inactive' | 'error';
  source_files: SourceFile[];
  additional_context: AdditionalContext[];
  insights_data?: InsightsData;
  operations_data?: OperationsData;
  roadmap_data?: RoadmapData;
  poc_data?: POCProposal;
}

// =============================================================================
// Request Types
// =============================================================================

export interface RoadmapGenerationRequest {
  sessionToken: string;
  sourceFiles: SourceFile[];
  insightsData?: InsightsData;
  operationsData?: OperationsData;
  additionalContext?: AdditionalContext[];
}

export interface POCGenerationRequest {
  sessionToken: string;
  roadmapData?: RoadmapData;
  insightsData?: InsightsData;
  operationsData?: OperationsData;
  requirements?: string[];
}

export interface DocumentGenerationRequest {
  sessionToken: string;
  documentType: 'roadmap' | 'poc' | 'summary';
  data: RoadmapData | POCProposal | Record<string, unknown>;
  format: 'pdf' | 'docx' | 'markdown';
}

// =============================================================================
// Liaison Event Types
// =============================================================================

export interface ExperienceLiaisonEventData {
  context_type?: string;
  roadmap_type?: string;
  poc_requirements?: string[];
  additional_files?: SourceFile[];
}

export interface ExperienceLiaisonEvent {
  type: 'experience_context_request' | 'experience_roadmap_request' | 'experience_poc_request';
  session_token: string;
  agent_type: 'experience_liaison';
  pillar: 'experience';
  data: ExperienceLiaisonEventData;
}

// =============================================================================
// Cross-Pillar Types
// =============================================================================

export interface CrossPillarDataRequest {
  sessionToken: string;
  pillar: 'content' | 'insights' | 'operations';
  dataType: string;
  context?: Record<string, unknown>;
}

export interface CrossPillarDataResponse {
  success: boolean;
  data?: InsightsData | OperationsData | SourceFile[];
  error?: string;
  pillar: string;
  dataType: string;
}

// =============================================================================
// Output Types
// =============================================================================

export interface ExperienceOutput {
  id: string;
  type: 'roadmap' | 'poc' | 'summary';
  format: string;
  content: string | Record<string, unknown>;
  generated_at: string;
  visualization_url?: string;
}

export interface ExperienceOutputsRequest {
  sessionToken: string;
  outputType: 'roadmap' | 'poc' | 'summary' | 'all';
  format?: string;
  includeVisualizations?: boolean;
}

export interface ExperienceOutputsResponse {
  outputs: ExperienceOutput[];
  session_token: string;
  status: 'success' | 'error';
  message?: string;
}

// =============================================================================
// Smart City Integration Types
// =============================================================================

export interface TrafficCopSessionRequest {
  sessionToken: string;
  operation: string;
  files?: SourceFile[];
  context?: Record<string, unknown>;
}

export interface TrafficCopSessionResponse {
  sessionId: string;
  status: 'active' | 'pending' | 'completed' | 'failed';
  routing: {
    nextStep: string;
    requiredFiles: string[];
    optionalFiles: string[];
  };
  metadata: {
    operation: string;
    timestamp: string;
    userId: string;
  };
}

export interface PostOfficeMessageData {
  content?: string;
  artifacts?: string[];
  parameters?: Record<string, unknown>;
}

export interface PostOfficeMessage {
  type: string;
  sessionToken: string;
  agentType: string;
  pillar: string;
  data: PostOfficeMessageData;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  timestamp: string;
}

export interface PostOfficeResponse {
  messageId: string;
  status: 'delivered' | 'pending' | 'failed';
  recipient: string;
  timestamp: string;
}

export interface ConductorExperienceInputs {
  source_files?: SourceFile[];
  insights_data?: InsightsData;
  operations_data?: OperationsData;
  roadmap_data?: RoadmapData;
  poc_data?: POCProposal;
  requirements?: string[];
}

export interface ConductorExperienceRequest {
  sessionToken: string;
  experienceType: 'roadmap_generation' | 'poc_generation' | 'document_generation' | 'cross_pillar_integration';
  inputs: ConductorExperienceInputs;
  priority: 'low' | 'medium' | 'high';
}

export interface ConductorExperienceResults {
  roadmap?: RoadmapData;
  poc?: POCProposal;
  document?: DocumentResponseData;
  artifacts?: string[];
}

export interface ConductorExperienceResponse {
  experienceId: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
  progress: number;
  estimatedCompletion: string;
  currentStep: string;
  results?: ConductorExperienceResults;
}

export interface ArchiveStateRequest {
  sessionToken: string;
  state: ExperienceSessionState;
  metadata: {
    operation: string;
    timestamp: string;
    userId: string;
    version: string;
  };
}

export interface ArchiveStateResponse {
  stateId: string;
  status: 'saved' | 'failed';
  timestamp: string;
  version: string;
}

// Roadmap Types
export interface RoadmapMilestone {
  id: string;
  title: string;
  description: string;
  targetDate: string;
  status: 'pending' | 'in_progress' | 'completed' | 'delayed';
  dependencies: string[];
  resources: string[];
  deliverables: string[];
}

export interface RoadmapPhase {
  id: string;
  name: string;
  description: string;
  startDate: string;
  endDate: string;
  milestones: RoadmapMilestone[];
  objectives: string[];
  successCriteria: string[];
}

export interface RoadmapTimeline {
  phases: RoadmapPhase[];
  totalDuration: string;
  criticalPath: string[];
  riskFactors: string[];
  mitigationStrategies: string[];
}

export interface RoadmapValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  suggestions: string[];
  completeness: number; // 0-100
  feasibility: number; // 0-100
  timeline: number; // 0-100
}

export interface OptimizationConstraints {
  max_timeline_weeks?: number;
  max_resources?: number;
  max_cost?: number;
  required_milestones?: string[];
  fixed_phases?: string[];
}

export interface RoadmapOptimizationRequest {
  roadmapData: RoadmapTimeline;
  optimizationType: 'timeline' | 'resources' | 'risk' | 'cost';
  constraints: OptimizationConstraints;
  sessionToken: string;
}

export interface RoadmapOptimizationResult {
  optimizedRoadmap: RoadmapTimeline;
  improvements: string[];
  metrics: {
    before: {
      timeline: number;
      resources: number;
      risk: number;
      cost: number;
    };
    after: {
      timeline: number;
      resources: number;
      risk: number;
      cost: number;
    };
  };
}

// POC Types
export interface POCRequirement {
  id: string;
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  category: 'functional' | 'non-functional' | 'technical' | 'business';
  acceptanceCriteria: string[];
  dependencies: string[];
}

export interface POCResource {
  id: string;
  name: string;
  type: 'human' | 'technical' | 'financial' | 'infrastructure';
  description: string;
  cost: number;
  availability: string;
  skills: string[];
}

export interface POCTimeline {
  phases: {
    id: string;
    name: string;
    duration: string;
    startDate: string;
    endDate: string;
    deliverables: string[];
    milestones: string[];
  }[];
  totalDuration: string;
  criticalPath: string[];
  dependencies: string[];
}

export interface POCValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  suggestions: string[];
  feasibility: number; // 0-100
  completeness: number; // 0-100
  riskLevel: 'low' | 'medium' | 'high';
}

export interface POCOptimizationConstraints {
  max_cost?: number;
  max_duration_weeks?: number;
  max_resources?: number;
  required_requirements?: string[];
  available_skills?: string[];
}

export interface POCOptimizationRequest {
  pocData: POCTimeline;
  optimizationType: 'cost' | 'timeline' | 'resources' | 'risk';
  constraints: POCOptimizationConstraints;
  sessionToken: string;
}

export interface POCOptimizationResult {
  optimizedPOC: POCTimeline;
  improvements: string[];
  metrics: {
    before: {
      cost: number;
      timeline: string;
      resources: number;
      risk: number;
    };
    after: {
      cost: number;
      timeline: string;
      resources: number;
      risk: number;
    };
  };
} 