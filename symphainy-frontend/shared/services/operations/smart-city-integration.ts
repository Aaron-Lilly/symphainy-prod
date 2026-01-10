// Smart City Integration Module
import { 
  OperationsQueryRequest,
  OperationsConversationRequest,
  OperationsLiaisonEvent
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

// Traffic Cop Integration - Session Management
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

export async function routeOperationsSession(request: TrafficCopSessionRequest): Promise<TrafficCopSessionResponse> {
  try {
    const response = await fetch(
      `${API_URL}/api/operations/traffic-cop/route`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${request.sessionToken}`,
        },
        body: JSON.stringify({
          session_token: request.sessionToken,
          operation: request.operation,
          files: request.files || [],
          context: request.context || {},
        }),
      },
    );

    const responseText = await response.text();
    console.log("Traffic Cop routing raw response:", responseText);

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
      error instanceof Error ? error.message : 'Failed to route operations session',
      'coexistence_analysis'
    );
  }
}

// Post Office Integration - Message Delivery
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

export async function sendOperationsMessage(message: PostOfficeMessage): Promise<PostOfficeResponse> {
  try {
    const response = await fetch(
      `${API_URL}/api/operations/post-office/send`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${message.sessionToken}`,
        },
        body: JSON.stringify(message),
      },
    );

    const responseText = await response.text();
    console.log("Post Office message raw response:", responseText);

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
      error instanceof Error ? error.message : 'Failed to send operations message',
      'coexistence_analysis'
    );
  }
}

// Conductor Integration - Workflow Orchestration
export interface ConductorWorkflowRequest {
  sessionToken: string;
  workflowType: 'sop_generation' | 'workflow_generation' | 'coexistence_analysis' | 'blueprint_generation';
  inputs: any;
  priority: 'low' | 'medium' | 'high';
}

export interface ConductorWorkflowResponse {
  workflowId: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
  progress: number;
  estimatedCompletion: string;
  currentStep: string;
  results?: any;
}

export async function orchestrateOperationsWorkflow(request: ConductorWorkflowRequest): Promise<ConductorWorkflowResponse> {
  try {
    const response = await fetch(
      `${API_URL}/api/operations/conductor/orchestrate`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${request.sessionToken}`,
        },
        body: JSON.stringify({
          session_token: request.sessionToken,
          workflow_type: request.workflowType,
          inputs: request.inputs,
          priority: request.priority,
        }),
      },
    );

    const responseText = await response.text();
    console.log("Conductor orchestration raw response:", responseText);

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
      error instanceof Error ? error.message : 'Failed to orchestrate operations workflow',
      'coexistence_analysis'
    );
  }
}

// Archive Integration - State Persistence
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

export async function persistOperationsState(request: ArchiveStateRequest): Promise<ArchiveStateResponse> {
  try {
    const response = await fetch(
      `${API_URL}/api/operations/archive/persist`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${request.sessionToken}`,
        },
        body: JSON.stringify({
          session_token: request.sessionToken,
          state: request.state,
          metadata: request.metadata,
        }),
      },
    );

    const responseText = await response.text();
    console.log("Archive persistence raw response:", responseText);

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
      error instanceof Error ? error.message : 'Failed to persist operations state',
      'coexistence_analysis'
    );
  }
}

// Operations Liaison Integration
export async function processOperationsQuery(request: OperationsQueryRequest): Promise<any> {
  try {
    const response = await fetch(
      `${API_URL}/api/operations/liaison/query`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
      },
    );

    const responseText = await response.text();
    console.log("Operations liaison query raw response:", responseText);

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
      error instanceof Error ? error.message : 'Failed to process operations query',
      'coexistence_analysis'
    );
  }
}

export async function processOperationsConversation(request: OperationsConversationRequest): Promise<any> {
  try {
    const response = await fetch(
      `${API_URL}/api/operations/liaison/conversation`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
      },
    );

    const responseText = await response.text();
    console.log("Operations liaison conversation raw response:", responseText);

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
      error instanceof Error ? error.message : 'Failed to process operations conversation',
      'coexistence_analysis'
    );
  }
}

export async function getOperationsConversationContext(sessionId: string): Promise<any> {
  try {
    const response = await fetch(
      `${API_URL}/api/operations/liaison/context/${sessionId}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      },
    );

    const responseText = await response.text();
    console.log("Operations liaison context raw response:", responseText);

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
      error instanceof Error ? error.message : 'Failed to get operations conversation context',
      'coexistence_analysis'
    );
  }
}

export async function analyzeOperationsIntent(query: string): Promise<any> {
  try {
    const response = await fetch(
      `${API_URL}/api/operations/liaison/analyze-intent`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      },
    );

    const responseText = await response.text();
    console.log("Operations intent analysis raw response:", responseText);

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
      error instanceof Error ? error.message : 'Failed to analyze operations intent',
      'coexistence_analysis'
    );
  }
} 