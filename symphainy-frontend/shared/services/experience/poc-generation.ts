// POC Generation Module
import { 
  ExperiencePOCResponse,
  ExperienceDocumentResponse,
  POCGenerationRequest,
  DocumentGenerationRequest
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

// Generate POC proposal
export async function generatePOCProposal(request: POCGenerationRequest): Promise<ExperiencePOCResponse> {
  try {
    const response = await fetch(
      `${API_URL}/api/experience/generate-poc-proposal`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${request.sessionToken}`,
        },
        body: JSON.stringify({
          session_token: request.sessionToken,
          roadmap_data: request.roadmapData,
          insights_data: request.insightsData,
          operations_data: request.operationsData,
          requirements: request.requirements,
        }),
      },
    );

    const responseText = await response.text();
    console.log("Generate POC proposal raw response:", responseText);

    if (!response.ok) {
      throw parseAPIError(response, responseText, 'poc_generation');
    }

    const data = JSON.parse(responseText);
    return data;
  } catch (error) {
    if (error instanceof ExperienceAPIError) {
      throw error;
    }
    throw new ExperienceAPIError(
      error instanceof Error ? error.message : 'Failed to generate POC proposal',
      'poc_generation'
    );
  }
}

// Generate POC document
export async function generatePOCDocument(request: DocumentGenerationRequest): Promise<ExperienceDocumentResponse> {
  try {
    const response = await fetch(
      `${API_URL}/api/experience/generate-poc-document`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${request.sessionToken}`,
        },
        body: JSON.stringify({
          session_token: request.sessionToken,
          document_type: request.documentType,
          data: request.data,
          format: request.format,
        }),
      },
    );

    const responseText = await response.text();
    console.log("Generate POC document raw response:", responseText);

    if (!response.ok) {
      throw parseAPIError(response, responseText, 'document_generation');
    }

    const data = JSON.parse(responseText);
    return data;
  } catch (error) {
    if (error instanceof ExperienceAPIError) {
      throw error;
    }
    throw new ExperienceAPIError(
      error instanceof Error ? error.message : 'Failed to generate POC document',
      'document_generation'
    );
  }
}

// POC types and interfaces
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

export async function validatePOC(pocData: any, sessionToken: string): Promise<POCValidationResult> {
  try {
    const response = await fetch(
      `${API_URL}/api/experience/validate-poc`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${sessionToken}`,
        },
        body: JSON.stringify({
          poc_data: pocData,
          session_token: sessionToken,
        }),
      },
    );

    const responseText = await response.text();
    console.log("POC validation raw response:", responseText);

    if (!response.ok) {
      throw parseAPIError(response, responseText, 'poc_generation');
    }

    const data = JSON.parse(responseText);
    return data;
  } catch (error) {
    if (error instanceof ExperienceAPIError) {
      throw error;
    }
    throw new ExperienceAPIError(
      error instanceof Error ? error.message : 'Failed to validate POC',
      'poc_generation'
    );
  }
}

// POC optimization
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

export async function optimizePOC(request: POCOptimizationRequest): Promise<POCOptimizationResult> {
  try {
    const response = await fetch(
      `${API_URL}/api/experience/optimize-poc`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${request.sessionToken}`,
        },
        body: JSON.stringify({
          poc_data: request.pocData,
          optimization_type: request.optimizationType,
          constraints: request.constraints,
          session_token: request.sessionToken,
        }),
      },
    );

    const responseText = await response.text();
    console.log("POC optimization raw response:", responseText);

    if (!response.ok) {
      throw parseAPIError(response, responseText, 'poc_generation');
    }

    const data = JSON.parse(responseText);
    return data;
  } catch (error) {
    if (error instanceof ExperienceAPIError) {
      throw error;
    }
    throw new ExperienceAPIError(
      error instanceof Error ? error.message : 'Failed to optimize POC',
      'poc_generation'
    );
  }
} 