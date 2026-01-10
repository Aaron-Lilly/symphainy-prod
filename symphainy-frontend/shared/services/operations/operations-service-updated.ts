// Updated Operations Service - Complete Implementation
// This service integrates with the new Operations Pillar backend endpoints

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

// Enhanced error handling
class OperationsAPIError extends Error {
  public code?: string;
  public details?: any;
  public operation: 'sop_to_workflow' | 'workflow_to_sop' | 'coexistence_analysis' | 'wizard_start' | 'wizard_chat' | 'wizard_publish' | 'conversation' | 'coexistence_blueprint';
  public file_uuid?: string;

  constructor(
    message: string,
    operation: 'sop_to_workflow' | 'workflow_to_sop' | 'coexistence_analysis' | 'wizard_start' | 'wizard_chat' | 'wizard_publish' | 'conversation' | 'coexistence_blueprint',
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
function parseAPIError(response: Response, responseText: string, operation: string, file_uuid?: string): OperationsAPIError {
  let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
  let errorCode = response.status.toString();
  let errorDetails = null;

  try {
    const errorJson = JSON.parse(responseText);
    errorMessage = errorJson.detail || errorJson.message || errorJson.error || errorMessage;
    errorCode = errorJson.code || errorCode;
    errorDetails = errorJson;
  } catch {
    errorMessage = responseText || errorMessage;
  }

  const userFriendlyMessages: Record<string, string> = {
    '400': 'Invalid request. Please check your input and try again.',
    '401': 'Authentication required. Please log in again.',
    '403': 'Access denied. You may not have permission for this operation.',
    '404': 'Service not found. The requested operation may not be available.',
    '422': 'Invalid data format. Please ensure your data is in the correct format.',
    '500': 'Server error. Please try again later or contact support.',
    '502': 'Service temporarily unavailable. Please try again later.',
    '503': 'Service temporarily unavailable. Please try again later.',
    '504': 'Request timeout. Please try again with smaller data.',
  };

  const friendlyMessage = userFriendlyMessages[errorCode] || errorMessage;

  return new OperationsAPIError(friendlyMessage, operation as any, errorCode, errorDetails, file_uuid);
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

// NEW: Real Conversion Functions
export async function convertSopToWorkflowReal(sopData: any, token: string): Promise<OperationsWorkflowResponse> {
  try {
    const response = await fetch(
      `${API_URL}/api/operations/convert-sop-to-workflow-real`,
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
    console.log("SOP to workflow real conversion raw response:", responseText);

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
      error instanceof Error ? error.message : 'Failed to convert SOP to workflow',
      'sop_to_workflow'
    );
  }
}

export async function convertWorkflowToSopReal(workflowData: any, token: string): Promise<OperationsWorkflowResponse> {
  try {
    const response = await fetch(
      `${API_URL}/api/operations/convert-workflow-to-sop-real`,
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
    console.log("Workflow to SOP real conversion raw response:", responseText);

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
      error instanceof Error ? error.message : 'Failed to convert workflow to SOP',
      'workflow_to_sop'
    );
  }
}

// NEW: DOCX Extraction Function
export async function extractSopFromDocx(file: File, token: string): Promise<OperationsWorkflowResponse> {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(
      `${API_URL}/api/operations/extract-sop-from-docx`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      },
    );

    const responseText = await response.text();
    console.log("DOCX extraction raw response:", responseText);

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
      error instanceof Error ? error.message : 'Failed to extract SOP from DOCX',
      'sop_to_workflow'
    );
  }
}

// NEW: CoexistenceEvaluator Bypass Function
export async function createCoexistenceBlueprintDirectly(
  userRequirements: any, 
  conversationId: string, 
  token: string
): Promise<OperationsCoexistenceResponse> {
  try {
    const response = await fetch(
      `${API_URL}/api/operations/create-coexistence-blueprint-directly`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          user_requirements: userRequirements,
          conversation_id: conversationId,
          session_token: token,
        }),
      },
    );

    const responseText = await response.text();
    console.log("Coexistence blueprint creation raw response:", responseText);

    if (!response.ok) {
      throw parseAPIError(response, responseText, 'coexistence_blueprint');
    }

    const data = JSON.parse(responseText);
    return data;
  } catch (error) {
    if (error instanceof OperationsAPIError) {
      throw error;
    }
    throw new OperationsAPIError(
      error instanceof Error ? error.message : 'Failed to create coexistence blueprint',
      'coexistence_blueprint'
    );
  }
}

// NEW: Operations Conversation Function
export async function processOperationsConversation(
  message: string, 
  conversationId: string, 
  token: string
): Promise<OperationsCoexistenceResponse> {
  try {
    const response = await fetch(
      `${API_URL}/api/operations/conversation`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: message,
          conversation_id: conversationId,
          session_token: token,
        }),
      },
    );

    const responseText = await response.text();
    console.log("Operations conversation raw response:", responseText);

    if (!response.ok) {
      throw parseAPIError(response, responseText, 'conversation');
    }

    const data = JSON.parse(responseText);
    return data;
  } catch (error) {
    if (error instanceof OperationsAPIError) {
      throw error;
    }
    throw new OperationsAPIError(
      error instanceof Error ? error.message : 'Failed to process conversation',
      'conversation'
    );
  }
}

// Legacy functions (keeping for backward compatibility)
export async function generateWorkflowFromSop(request: WorkflowGenerationRequest): Promise<OperationsWorkflowResponse> {
  // Map to new real conversion function
  return convertSopToWorkflowReal(request.sopFileUuid, request.sessionToken);
}

export async function generateSopFromWorkflow(request: SopGenerationRequest): Promise<OperationsWorkflowResponse> {
  // Map to new real conversion function
  return convertWorkflowToSopReal(request.workflowFileUuid, request.sessionToken);
}

export async function sopToWorkflow(fileUuid: string, token: string): Promise<OperationsWorkflowResponse> {
  // This would need to be updated to work with file UUIDs
  // For now, return a placeholder response
  return {
    workflow: null,
    sop: null,
    session_token: token,
    status: 'error',
    message: "File UUID conversion not yet implemented"
  };
}

export async function workflowToSop(fileUuid: string, token: string): Promise<OperationsWorkflowResponse> {
  // This would need to be updated to work with file UUIDs
  // For now, return a placeholder response
  return {
    workflow: null,
    sop: null,
    session_token: token,
    status: 'error',
    message: "File UUID conversion not yet implemented"
  };
}

// Health check function
export async function checkOperationsHealth(): Promise<any> {
  try {
    const response = await fetch(`${API_URL}/api/operations/health`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    const responseText = await response.text();
    
    if (!response.ok) {
      throw parseAPIError(response, responseText, 'sop_to_workflow');
    }

    return JSON.parse(responseText);
  } catch (error) {
    if (error instanceof OperationsAPIError) {
      throw error;
    }
    throw new OperationsAPIError(
      error instanceof Error ? error.message : 'Failed to check operations health',
      'sop_to_workflow'
    );
  }
}

// Export all functions
export {
  OperationsAPIError,
  parseAPIError
};



