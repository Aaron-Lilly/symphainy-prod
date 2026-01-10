// SOP Generation Module
import { 
  OperationsWorkflowResponse,
  SopGenerationRequest
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

// Generate SOP from workflow
export async function generateSopFromWorkflow(request: SopGenerationRequest): Promise<OperationsWorkflowResponse> {
  try {
    const response = await fetch(
      `${API_URL}/api/operations/generate-sop-from-workflow`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${request.sessionToken}`,
        },
        body: JSON.stringify({
          workflow_file_uuid: request.workflowFileUuid,
          session_token: request.sessionToken,
        }),
      },
    );

    const responseText = await response.text();
    console.log("Generate SOP from workflow raw response:", responseText);

    if (!response.ok) {
      throw parseAPIError(response, responseText, 'workflow_to_sop', request.workflowFileUuid);
    }

    const data = JSON.parse(responseText);
    return data;
  } catch (error) {
    if (error instanceof OperationsAPIError) {
      throw error;
    }
    throw new OperationsAPIError(
      error instanceof Error ? error.message : 'Failed to generate SOP from workflow',
      'workflow_to_sop',
      undefined,
      undefined,
      request.workflowFileUuid
    );
  }
}

// SOP validation
export interface SopValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  suggestions: string[];
  completeness: number; // 0-100
  clarity: number; // 0-100
  compliance: number; // 0-100
}

export async function validateSop(sopData: any, token: string): Promise<SopValidationResult> {
  try {
    const response = await fetch(
      `${API_URL}/api/operations/validate-sop`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          sop_data: sopData,
          session_token: token,
        }),
      },
    );

    const responseText = await response.text();
    console.log("SOP validation raw response:", responseText);

    if (!response.ok) {
      throw parseAPIError(response, responseText, 'workflow_to_sop');
    }

    const data = JSON.parse(responseText);
    return data;
  } catch (error) {
    if (error instanceof OperationsAPIError) {
      throw error;
    }
    throw new OperationsAPIError(
      error instanceof Error ? error.message : 'Failed to validate SOP',
      'workflow_to_sop'
    );
  }
}

// SOP optimization
export interface SopOptimizationRequest {
  sopData: any;
  optimizationType: 'clarity' | 'completeness' | 'compliance' | 'efficiency';
  sessionToken: string;
}

export interface SopOptimizationResult {
  optimizedSop: any;
  improvements: string[];
  metrics: {
    before: {
      clarity: number;
      completeness: number;
      compliance: number;
      efficiency: number;
    };
    after: {
      clarity: number;
      completeness: number;
      compliance: number;
      efficiency: number;
    };
  };
}

export async function optimizeSop(request: SopOptimizationRequest): Promise<SopOptimizationResult> {
  try {
    const response = await fetch(
      `${API_URL}/api/operations/optimize-sop`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${request.sessionToken}`,
        },
        body: JSON.stringify({
          sop_data: request.sopData,
          optimization_type: request.optimizationType,
          session_token: request.sessionToken,
        }),
      },
    );

    const responseText = await response.text();
    console.log("SOP optimization raw response:", responseText);

    if (!response.ok) {
      throw parseAPIError(response, responseText, 'workflow_to_sop');
    }

    const data = JSON.parse(responseText);
    return data;
  } catch (error) {
    if (error instanceof OperationsAPIError) {
      throw error;
    }
    throw new OperationsAPIError(
      error instanceof Error ? error.message : 'Failed to optimize SOP',
      'workflow_to_sop'
    );
  }
}

// SOP template generation
export interface SopTemplateRequest {
  processType: string;
  industry: string;
  complexity: 'simple' | 'moderate' | 'complex';
  sessionToken: string;
}

export interface SopTemplateResult {
  template: any;
  placeholders: string[];
  guidance: string[];
}

export async function generateSopTemplate(request: SopTemplateRequest): Promise<SopTemplateResult> {
  try {
    const response = await fetch(
      `${API_URL}/api/operations/generate-sop-template`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${request.sessionToken}`,
        },
        body: JSON.stringify({
          process_type: request.processType,
          industry: request.industry,
          complexity: request.complexity,
          session_token: request.sessionToken,
        }),
      },
    );

    const responseText = await response.text();
    console.log("SOP template generation raw response:", responseText);

    if (!response.ok) {
      throw parseAPIError(response, responseText, 'workflow_to_sop');
    }

    const data = JSON.parse(responseText);
    return data;
  } catch (error) {
    if (error instanceof OperationsAPIError) {
      throw error;
    }
    throw new OperationsAPIError(
      error instanceof Error ? error.message : 'Failed to generate SOP template',
      'workflow_to_sop'
    );
  }
} 