// Coexistence Analysis Module
import { 
  OperationsCoexistenceResponse,
  CoexistenceAnalysisRequest,
  CoexistenceContentRequest
} from './types';

import { getApiUrl } from '@/shared/config/api-config';

// Use centralized API config (NO hardcoded values)
const API_URL = getApiUrl();

// Error handling utilities
class OperationsAPIError extends Error {
  public code?: string;
  public details?: any;
  public operation: 'sop_to_workflow' | 'workflow_to_sop' | 'coexistence_analysis' | 'wizard_start' | 'wizard_chat' | 'wizard_publish';
  public file_uuid?: string;

  constructor(
    message: string,
    operation: 'sop_to_workflow' | 'workflow_to_sop' | 'coexistence_analysis' | 'wizard_start' | 'wizard_chat' | 'wizard_publish',
    code?: string,
    details?: any,
    file_uuid?: string
  ) {
    super(message);
    this.name = 'OperationsAPIError';
    this.operation = operation;
    this.code = code;
    this.details = details;
    this.file_uuid = file_uuid;
  }
}

// Enhanced error parsing
function parseAPIError(response: Response, responseText: string, operation: 'sop_to_workflow' | 'workflow_to_sop' | 'coexistence_analysis', file_uuid?: string): OperationsAPIError {
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
    '400': 'Invalid request. Please check your file selection and try again.',
    '401': 'Authentication required. Please log in again.',
    '403': 'Access denied. You may not have permission for this operation.',
    '404': 'File not found. The selected file may have been moved or deleted.',
    '422': 'Invalid file format. Please ensure your file is in the correct format.',
    '500': 'Server error. Please try again later or contact support.',
    '502': 'Service temporarily unavailable. Please try again later.',
    '503': 'Service temporarily unavailable. Please try again later.',
    '504': 'Request timeout. Please try again with a smaller file.',
  };

  const friendlyMessage = userFriendlyMessages[errorCode] || errorMessage;

  return new OperationsAPIError(friendlyMessage, operation, errorCode, errorDetails, file_uuid);
}

// Optimize coexistence with files
export async function optimizeCoexistence(request: CoexistenceAnalysisRequest): Promise<OperationsCoexistenceResponse> {
  try {
    const response = await fetch(
      `${API_URL}/api/operations/optimize-coexistence`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${request.sessionToken}`,
        },
        body: JSON.stringify({
          sop_input_file_uuid: request.sopInputFileUuid,
          workflow_input_file_uuid: request.workflowInputFileUuid,
          session_token: request.sessionToken,
        }),
      },
    );

    const responseText = await response.text();
    console.log("Optimize coexistence raw response:", responseText);

    if (!response.ok) {
      throw parseAPIError(response, responseText, 'coexistence_analysis');
    }

    const data = JSON.parse(responseText);
    return data;
  } catch (error) {
    if (error instanceof OperationsAPIError) {
      throw error;
    }
    throw new OperationsAPIError(
      error instanceof Error ? error.message : 'Failed to optimize coexistence',
      'coexistence_analysis'
    );
  }
}

// Optimize coexistence with content
export async function optimizeCoexistenceWithContent(request: CoexistenceContentRequest): Promise<OperationsCoexistenceResponse> {
  try {
    const response = await fetch(
      `${API_URL}/api/operations/optimize-coexistence-with-content`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${request.sessionToken}`,
        },
        body: JSON.stringify({
          sop_content: request.sopContent,
          workflow_content: request.workflowContent,
          session_token: request.sessionToken,
        }),
      },
    );

    const responseText = await response.text();
    console.log("Optimize coexistence with content raw response:", responseText);

    if (!response.ok) {
      throw parseAPIError(response, responseText, 'coexistence_analysis');
    }

    const data = JSON.parse(responseText);
    return data;
  } catch (error) {
    if (error instanceof OperationsAPIError) {
      throw error;
    }
    throw new OperationsAPIError(
      error instanceof Error ? error.message : 'Failed to optimize coexistence with content',
      'coexistence_analysis'
    );
  }
}

// Coexistence analysis types
export interface CoexistenceAnalysisResult {
  compatibility: number; // 0-100
  conflicts: string[];
  synergies: string[];
  recommendations: string[];
  riskAssessment: {
    low: string[];
    medium: string[];
    high: string[];
  };
  optimizationOpportunities: string[];
}

export async function analyzeCoexistence(sopData: any, workflowData: any, token: string): Promise<CoexistenceAnalysisResult> {
  try {
    const response = await fetch(
      `${API_URL}/api/operations/analyze-coexistence`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          sop_data: sopData,
          workflow_data: workflowData,
          session_token: token,
        }),
      },
    );

    const responseText = await response.text();
    console.log("Coexistence analysis raw response:", responseText);

    if (!response.ok) {
      throw parseAPIError(response, responseText, 'coexistence_analysis');
    }

    const data = JSON.parse(responseText);
    return data;
  } catch (error) {
    if (error instanceof OperationsAPIError) {
      throw error;
    }
    throw new OperationsAPIError(
      error instanceof Error ? error.message : 'Failed to analyze coexistence',
      'coexistence_analysis'
    );
  }
}

// Blueprint generation
export interface BlueprintGenerationRequest {
  sopData: any;
  workflowData: any;
  analysisResult: CoexistenceAnalysisResult;
  sessionToken: string;
}

export interface BlueprintGenerationResult {
  blueprint: any;
  futureStateSop: any;
  futureStateWorkflow: any;
  implementationPlan: string[];
  timeline: {
    phase: string;
    duration: string;
    tasks: string[];
  }[];
  successMetrics: string[];
}

export async function generateBlueprint(request: BlueprintGenerationRequest): Promise<BlueprintGenerationResult> {
  try {
    const response = await fetch(
      `${API_URL}/api/operations/generate-blueprint`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${request.sessionToken}`,
        },
        body: JSON.stringify({
          sop_data: request.sopData,
          workflow_data: request.workflowData,
          analysis_result: request.analysisResult,
          session_token: request.sessionToken,
        }),
      },
    );

    const responseText = await response.text();
    console.log("Blueprint generation raw response:", responseText);

    if (!response.ok) {
      throw parseAPIError(response, responseText, 'coexistence_analysis');
    }

    const data = JSON.parse(responseText);
    return data;
  } catch (error) {
    if (error instanceof OperationsAPIError) {
      throw error;
    }
    throw new OperationsAPIError(
      error instanceof Error ? error.message : 'Failed to generate blueprint',
      'coexistence_analysis'
    );
  }
}

// Coexistence evaluation
export interface CoexistenceEvaluationRequest {
  currentState: {
    sop: any;
    workflow: any;
  };
  targetState: {
    sop: any;
    workflow: any;
  };
  sessionToken: string;
}

export interface CoexistenceEvaluationResult {
  feasibility: number; // 0-100
  effort: 'low' | 'medium' | 'high';
  timeline: string;
  risks: string[];
  benefits: string[];
  prerequisites: string[];
  alternatives: string[];
}

export async function evaluateCoexistence(request: CoexistenceEvaluationRequest): Promise<CoexistenceEvaluationResult> {
  try {
    const response = await fetch(
      `${API_URL}/api/operations/evaluate-coexistence`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${request.sessionToken}`,
        },
        body: JSON.stringify({
          current_state: request.currentState,
          target_state: request.targetState,
          session_token: request.sessionToken,
        }),
      },
    );

    const responseText = await response.text();
    console.log("Coexistence evaluation raw response:", responseText);

    if (!response.ok) {
      throw parseAPIError(response, responseText, 'coexistence_analysis');
    }

    const data = JSON.parse(responseText);
    return data;
  } catch (error) {
    if (error instanceof OperationsAPIError) {
      throw error;
    }
    throw new OperationsAPIError(
      error instanceof Error ? error.message : 'Failed to evaluate coexistence',
      'coexistence_analysis'
    );
  }
} 