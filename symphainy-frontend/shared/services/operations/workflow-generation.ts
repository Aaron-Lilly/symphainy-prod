// Workflow Generation Module
import { 
  OperationsWorkflowResponse,
  WorkflowGenerationRequest,
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

// SOP to Workflow conversion
export async function sopToWorkflow(fileUuid: string, token: string): Promise<OperationsWorkflowResponse> {
  try {
    const response = await fetch(
      `${API_URL}/api/operations/sop-to-workflow`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          file_uuid: fileUuid,
          session_token: token,
        }),
      },
    );

    const responseText = await response.text();
    console.log("SOP to workflow raw response:", responseText);

    if (!response.ok) {
      throw parseAPIError(response, responseText, 'sop_to_workflow', fileUuid);
    }

    const data = JSON.parse(responseText);
    return data;
  } catch (error) {
    if (error instanceof OperationsAPIError) {
      throw error;
    }
    throw new OperationsAPIError(
      error instanceof Error ? error.message : 'Failed to convert SOP to workflow',
      'sop_to_workflow',
      undefined,
      undefined,
      fileUuid
    );
  }
}

// Workflow to SOP conversion
export async function workflowToSop(fileUuid: string, token: string): Promise<OperationsWorkflowResponse> {
  try {
    const response = await fetch(
      `${API_URL}/api/operations/workflow-to-sop`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          file_uuid: fileUuid,
          session_token: token,
        }),
      },
    );

    const responseText = await response.text();
    console.log("Workflow to SOP raw response:", responseText);

    if (!response.ok) {
      throw parseAPIError(response, responseText, 'workflow_to_sop', fileUuid);
    }

    const data = JSON.parse(responseText);
    return data;
  } catch (error) {
    if (error instanceof OperationsAPIError) {
      throw error;
    }
    throw new OperationsAPIError(
      error instanceof Error ? error.message : 'Failed to convert workflow to SOP',
      'workflow_to_sop',
      undefined,
      undefined,
      fileUuid
    );
  }
}

// Workflow status tracking
export interface WorkflowStatus {
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress?: number;
  message?: string;
  result?: any;
}

export async function getWorkflowStatus(workflowId: string, token: string): Promise<WorkflowStatus> {
  try {
    const response = await fetch(
      `${API_URL}/api/operations/workflow-status/${workflowId}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      },
    );

    const responseText = await response.text();
    console.log("Workflow status raw response:", responseText);

    if (!response.ok) {
      throw parseAPIError(response, responseText, 'sop_to_workflow');
    }

    const data = JSON.parse(responseText);
    return data;
  } catch (error) {
    if (error instanceof OperationsAPIError) {
      throw error;
    }
    throw new OperationsAPIError(
      error instanceof Error ? error.message : 'Failed to get workflow status',
      'sop_to_workflow'
    );
  }
}

// Workflow validation
export interface WorkflowValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  suggestions: string[];
}

export async function validateWorkflow(workflowData: any, token: string): Promise<WorkflowValidationResult> {
  try {
    const response = await fetch(
      `${API_URL}/api/operations/validate-workflow`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          workflow_data: workflowData,
          session_token: token,
        }),
      },
    );

    const responseText = await response.text();
    console.log("Workflow validation raw response:", responseText);

    if (!response.ok) {
      throw parseAPIError(response, responseText, 'sop_to_workflow');
    }

    const data = JSON.parse(responseText);
    return data;
  } catch (error) {
    if (error instanceof OperationsAPIError) {
      throw error;
    }
    throw new OperationsAPIError(
      error instanceof Error ? error.message : 'Failed to validate workflow',
      'sop_to_workflow'
    );
  }
} 