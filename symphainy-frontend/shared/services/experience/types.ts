// Experience Service Types
export interface ExperienceSessionResponse {
  session_id: string;
  status: string;
  message: string;
  data?: any;
}

export interface ExperienceRoadmapResponse {
  roadmap: any;
  timeline: any[];
  milestones: any[];
  recommendations: string[];
  session_token: string;
  status: 'success' | 'error';
  message?: string;
}

export interface ExperiencePOCResponse {
  poc_proposal: any;
  requirements: string[];
  timeline: string;
  resources: string[];
  session_token: string;
  status: 'success' | 'error';
  message?: string;
}

export interface ExperienceDocumentResponse {
  document: any;
  format: string;
  content: string;
  session_token: string;
  status: 'success' | 'error';
  message?: string;
}

export interface ExperienceErrorResponse {
  message: string;
  operation: 'roadmap_generation' | 'poc_generation' | 'document_generation' | 'session_management';
  code?: string;
  details?: any;
}

export interface SourceFile {
  uuid: string;
  filename: string;
  file_type: string;
  file_size: number;
  upload_date: string;
  status: string;
  metadata?: any;
}

export interface AdditionalContextRequest {
  session_token: string;
  context_type: string;
  context_data: any;
  priority: 'low' | 'medium' | 'high';
}

export interface ExperienceSessionState {
  session_id: string;
  status: 'active' | 'inactive' | 'error';
  source_files: SourceFile[];
  additional_context: any[];
  insights_data?: any;
  operations_data?: any;
  roadmap_data?: any;
  poc_data?: any;
}

export interface RoadmapGenerationRequest {
  sessionToken: string;
  sourceFiles: SourceFile[];
  insightsData?: any;
  operationsData?: any;
  additionalContext?: any;
}

export interface POCGenerationRequest {
  sessionToken: string;
  roadmapData?: any;
  insightsData?: any;
  operationsData?: any;
  requirements?: string[];
}

export interface DocumentGenerationRequest {
  sessionToken: string;
  documentType: 'roadmap' | 'poc' | 'summary';
  data: any;
  format: 'pdf' | 'docx' | 'markdown';
}

export interface ExperienceLiaisonEvent {
  type: 'experience_context_request' | 'experience_roadmap_request' | 'experience_poc_request';
  session_token: string;
  agent_type: 'experience_liaison';
  pillar: 'experience';
  data: {
    context_type?: string;
    roadmap_type?: string;
    poc_requirements?: string[];
    additional_files?: any[];
  };
}

export interface CrossPillarDataRequest {
  sessionToken: string;
  pillar: 'content' | 'insights' | 'operations';
  dataType: string;
  context?: any;
}

export interface CrossPillarDataResponse {
  success: boolean;
  data?: any;
  error?: string;
  pillar: string;
  dataType: string;
}

export interface ExperienceOutputsRequest {
  sessionToken: string;
  outputType: 'roadmap' | 'poc' | 'summary' | 'all';
  format?: string;
  includeVisualizations?: boolean;
}

export interface ExperienceOutputsResponse {
  outputs: any[];
  session_token: string;
  status: 'success' | 'error';
  message?: string;
}

// Smart City Integration Types
export interface TrafficCopSessionRequest {
  sessionToken: string;
  operation: string;
  files?: any[];
  context?: any;
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

export interface PostOfficeMessage {
  type: string;
  sessionToken: string;
  agentType: string;
  pillar: string;
  data: any;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  timestamp: string;
}

export interface PostOfficeResponse {
  messageId: string;
  status: 'delivered' | 'pending' | 'failed';
  recipient: string;
  timestamp: string;
}

export interface ConductorExperienceRequest {
  sessionToken: string;
  experienceType: 'roadmap_generation' | 'poc_generation' | 'document_generation' | 'cross_pillar_integration';
  inputs: any;
  priority: 'low' | 'medium' | 'high';
}

export interface ConductorExperienceResponse {
  experienceId: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
  progress: number;
  estimatedCompletion: string;
  currentStep: string;
  results?: any;
}

export interface ArchiveStateRequest {
  sessionToken: string;
  state: any;
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

export interface RoadmapOptimizationRequest {
  roadmapData: any;
  optimizationType: 'timeline' | 'resources' | 'risk' | 'cost';
  constraints: any;
  sessionToken: string;
}

export interface RoadmapOptimizationResult {
  optimizedRoadmap: any;
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

export interface POCOptimizationRequest {
  pocData: any;
  optimizationType: 'cost' | 'timeline' | 'resources' | 'risk';
  constraints: any;
  sessionToken: string;
}

export interface POCOptimizationResult {
  optimizedPOC: any;
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