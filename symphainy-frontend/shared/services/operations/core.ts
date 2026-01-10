// Operations Service Core
import { 
  OperationsSessionResponse,
  OperationsWorkflowResponse,
  OperationsCoexistenceResponse,
  OperationsWizardResponse,
  WorkflowGenerationRequest,
  SopGenerationRequest,
  CoexistenceAnalysisRequest,
  CoexistenceContentRequest,
  WizardRequest,
  BlueprintSaveRequest,
  OperationsQueryRequest,
  OperationsConversationRequest
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

// Core Operations API Functions
export async function getSessionElements(sessionToken: string): Promise<OperationsSessionResponse> {
  try {
    const response = await fetch(
      `${API_URL}/api/operations/session/elements?session_token=${encodeURIComponent(sessionToken)}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${sessionToken}`,
        },
      },
    );

    const responseText = await response.text();
    console.log("Get session elements raw response:", responseText);

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
      error instanceof Error ? error.message : 'Failed to get session elements',
      'sop_to_workflow'
    );
  }
}

export async function clearSessionElements(sessionToken: string): Promise<{ success: boolean; message: string }> {
  try {
    const response = await fetch(
      `${API_URL}/api/operations/session/elements`,
      {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${sessionToken}`,
        },
      },
    );

    const responseText = await response.text();
    console.log("Clear session elements raw response:", responseText);

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
      error instanceof Error ? error.message : 'Failed to clear session elements',
      'sop_to_workflow'
    );
  }
}

export async function generateWorkflowFromSop(request: WorkflowGenerationRequest): Promise<OperationsWorkflowResponse> {
  try {
    const response = await fetch(
      `${API_URL}/api/operations/generate-workflow-from-sop`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${request.sessionToken}`,
        },
        body: JSON.stringify({
          sop_file_uuid: request.sopFileUuid,
          session_token: request.sessionToken,
        }),
      },
    );

    const responseText = await response.text();
    console.log("Generate workflow from SOP raw response:", responseText);

    if (!response.ok) {
      throw parseAPIError(response, responseText, 'sop_to_workflow', request.sopFileUuid);
    }

    const data = JSON.parse(responseText);
    return data;
  } catch (error) {
    if (error instanceof OperationsAPIError) {
      throw error;
    }
    throw new OperationsAPIError(
      error instanceof Error ? error.message : 'Failed to generate workflow from SOP',
      'sop_to_workflow',
      undefined,
      undefined,
      request.sopFileUuid
    );
  }
}

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

export async function saveBlueprint(request: BlueprintSaveRequest): Promise<{ blueprint_id: string }> {
  try {
    const response = await fetch(
      `${API_URL}/api/operations/save-blueprint`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          blueprint: request.blueprint,
          user_id: request.userId,
        }),
      },
    );

    const responseText = await response.text();
    console.log("Save blueprint raw response:", responseText);

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
      error instanceof Error ? error.message : 'Failed to save blueprint',
      'coexistence_analysis'
    );
  }
} 