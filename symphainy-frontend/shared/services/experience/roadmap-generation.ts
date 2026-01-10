// Roadmap Generation Module
import { 
  ExperienceRoadmapResponse,
  RoadmapGenerationRequest,
  SourceFile
} from './types';

// EC2 default: http://35.215.64.103:8000 (accessible from outside EC2)
// Option C: Override via NEXT_PUBLIC_API_URL environment variable
import { getApiUrl } from '@/shared/config/api-config';

// Use centralized API config (NO hardcoded values)
const API_URL = getApiUrl();

// Error handling utilities
class ExperienceAPIError extends Error {
  public code?: string;
  public details?: any;
  public operation: 'roadmap_generation' | 'poc_generation' | 'document_generation' | 'session_management';

  constructor(
    message: string,
    operation: 'roadmap_generation' | 'poc_generation' | 'document_generation' | 'session_management',
    code?: string,
    details?: any
  ) {
    super(message);
    this.name = 'ExperienceAPIError';
    this.operation = operation;
    this.code = code;
    this.details = details;
  }
}

// Enhanced error parsing
function parseAPIError(response: Response, responseText: string, operation: 'roadmap_generation' | 'poc_generation' | 'document_generation' | 'session_management'): ExperienceAPIError {
  let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
  let errorCode = response.status.toString();
  let errorDetails = null;

  try {
    const errorJson = JSON.parse(responseText);
    errorMessage = errorJson.detail || errorJson.message || errorJson.error || errorMessage;
    errorCode = errorJson.code || errorCode;
    errorDetails = errorJson;
  } catch {
    // Response is not JSON, use as-is
    errorMessage = responseText || errorMessage;
  }

  // Provide user-friendly error messages
  const userFriendlyMessages: Record<string, string> = {
    '400': 'Invalid request. Please check your input and try again.',
    '401': 'Authentication required. Please log in again.',
    '403': 'Access denied. You may not have permission for this operation.',
    '404': 'Resource not found. The requested data may have been moved or deleted.',
    '422': 'Invalid data format. Please ensure your data is in the correct format.',
    '500': 'Server error. Please try again later or contact support.',
    '502': 'Service temporarily unavailable. Please try again later.',
    '503': 'Service temporarily unavailable. Please try again later.',
    '504': 'Request timeout. Please try again with a smaller dataset.',
  };

  const friendlyMessage = userFriendlyMessages[errorCode] || errorMessage;

  return new ExperienceAPIError(friendlyMessage, operation, errorCode, errorDetails);
}

// Analyze file for roadmap generation
export async function analyzeFileForRoadmap(fileUuid: string, sessionToken: string): Promise<ExperienceRoadmapResponse> {
  try {
    const response = await fetch(
      `${API_URL}/api/experience/analyze-file-for-roadmap`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${sessionToken}`,
        },
        body: JSON.stringify({
          file_uuid: fileUuid,
          session_token: sessionToken,
        }),
      },
    );

    const responseText = await response.text();
    console.log("Analyze file for roadmap raw response:", responseText);

    if (!response.ok) {
      throw parseAPIError(response, responseText, 'roadmap_generation');
    }

    const data = JSON.parse(responseText);
    return data;
  } catch (error) {
    if (error instanceof ExperienceAPIError) {
      throw error;
    }
    throw new ExperienceAPIError(
      error instanceof Error ? error.message : 'Failed to analyze file for roadmap',
      'roadmap_generation'
    );
  }
}

// Generate roadmap from multiple sources
export async function generateRoadmap(request: RoadmapGenerationRequest): Promise<ExperienceRoadmapResponse> {
  try {
    const response = await fetch(
      `${API_URL}/api/experience/generate-roadmap`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${request.sessionToken}`,
        },
        body: JSON.stringify({
          session_token: request.sessionToken,
          source_files: request.sourceFiles,
          insights_data: request.insightsData,
          operations_data: request.operationsData,
          additional_context: request.additionalContext,
        }),
      },
    );

    const responseText = await response.text();
    console.log("Generate roadmap raw response:", responseText);

    if (!response.ok) {
      throw parseAPIError(response, responseText, 'roadmap_generation');
    }

    const data = JSON.parse(responseText);
    return data;
  } catch (error) {
    if (error instanceof ExperienceAPIError) {
      throw error;
    }
    throw new ExperienceAPIError(
      error instanceof Error ? error.message : 'Failed to generate roadmap',
      'roadmap_generation'
    );
  }
}

// Roadmap types and interfaces
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

export async function validateRoadmap(roadmapData: any, sessionToken: string): Promise<RoadmapValidationResult> {
  try {
    const response = await fetch(
      `${API_URL}/api/experience/validate-roadmap`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${sessionToken}`,
        },
        body: JSON.stringify({
          roadmap_data: roadmapData,
          session_token: sessionToken,
        }),
      },
    );

    const responseText = await response.text();
    console.log("Roadmap validation raw response:", responseText);

    if (!response.ok) {
      throw parseAPIError(response, responseText, 'roadmap_generation');
    }

    const data = JSON.parse(responseText);
    return data;
  } catch (error) {
    if (error instanceof ExperienceAPIError) {
      throw error;
    }
    throw new ExperienceAPIError(
      error instanceof Error ? error.message : 'Failed to validate roadmap',
      'roadmap_generation'
    );
  }
}

// Roadmap optimization
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

export async function optimizeRoadmap(request: RoadmapOptimizationRequest): Promise<RoadmapOptimizationResult> {
  try {
    const response = await fetch(
      `${API_URL}/api/experience/optimize-roadmap`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${request.sessionToken}`,
        },
        body: JSON.stringify({
          roadmap_data: request.roadmapData,
          optimization_type: request.optimizationType,
          constraints: request.constraints,
          session_token: request.sessionToken,
        }),
      },
    );

    const responseText = await response.text();
    console.log("Roadmap optimization raw response:", responseText);

    if (!response.ok) {
      throw parseAPIError(response, responseText, 'roadmap_generation');
    }

    const data = JSON.parse(responseText);
    return data;
  } catch (error) {
    if (error instanceof ExperienceAPIError) {
      throw error;
    }
    throw new ExperienceAPIError(
      error instanceof Error ? error.message : 'Failed to optimize roadmap',
      'roadmap_generation'
    );
  }
} 