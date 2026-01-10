// Smart City Integration Module
import { 
  ExperienceLiaisonEvent,
  CrossPillarDataRequest,
  CrossPillarDataResponse
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

export async function routeExperienceSession(request: TrafficCopSessionRequest): Promise<TrafficCopSessionResponse> {
  try {
    const response = await fetch(
      `${API_URL}/api/experience/traffic-cop/route`,
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
      throw parseAPIError(response, responseText, 'session_management');
    }

    const data = JSON.parse(responseText);
    return data;
  } catch (error) {
    if (error instanceof ExperienceAPIError) {
      throw error;
    }
    throw new ExperienceAPIError(
      error instanceof Error ? error.message : 'Failed to route experience session',
      'session_management'
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

export async function sendExperienceMessage(message: PostOfficeMessage): Promise<PostOfficeResponse> {
  try {
    const response = await fetch(
      `${API_URL}/api/experience/post-office/send`,
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
      throw parseAPIError(response, responseText, 'session_management');
    }

    const data = JSON.parse(responseText);
    return data;
  } catch (error) {
    if (error instanceof ExperienceAPIError) {
      throw error;
    }
    throw new ExperienceAPIError(
      error instanceof Error ? error.message : 'Failed to send experience message',
      'session_management'
    );
  }
}

// Conductor Integration - Experience Orchestration
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

export async function orchestrateExperience(request: ConductorExperienceRequest): Promise<ConductorExperienceResponse> {
  try {
    const response = await fetch(
      `${API_URL}/api/experience/conductor/orchestrate`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${request.sessionToken}`,
        },
        body: JSON.stringify({
          session_token: request.sessionToken,
          experience_type: request.experienceType,
          inputs: request.inputs,
          priority: request.priority,
        }),
      },
    );

    const responseText = await response.text();
    console.log("Conductor orchestration raw response:", responseText);

    if (!response.ok) {
      throw parseAPIError(response, responseText, 'session_management');
    }

    const data = JSON.parse(responseText);
    return data;
  } catch (error) {
    if (error instanceof ExperienceAPIError) {
      throw error;
    }
    throw new ExperienceAPIError(
      error instanceof Error ? error.message : 'Failed to orchestrate experience',
      'session_management'
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

export async function persistExperienceState(request: ArchiveStateRequest): Promise<ArchiveStateResponse> {
  try {
    const response = await fetch(
      `${API_URL}/api/experience/archive/persist`,
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
      throw parseAPIError(response, responseText, 'session_management');
    }

    const data = JSON.parse(responseText);
    return data;
  } catch (error) {
    if (error instanceof ExperienceAPIError) {
      throw error;
    }
    throw new ExperienceAPIError(
      error instanceof Error ? error.message : 'Failed to persist experience state',
      'session_management'
    );
  }
}

// Cross-Pillar Data Integration
export async function getCrossPillarData(request: CrossPillarDataRequest): Promise<CrossPillarDataResponse> {
  try {
    const response = await fetch(
      `${API_URL}/api/experience/cross-pillar/data`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${request.sessionToken}`,
        },
        body: JSON.stringify({
          session_token: request.sessionToken,
          pillar: request.pillar,
          data_type: request.dataType,
          context: request.context || {},
        }),
      },
    );

    const responseText = await response.text();
    console.log("Cross-pillar data raw response:", responseText);

    if (!response.ok) {
      throw parseAPIError(response, responseText, 'session_management');
    }

    const data = JSON.parse(responseText);
    return data;
  } catch (error) {
    if (error instanceof ExperienceAPIError) {
      throw error;
    }
    throw new ExperienceAPIError(
      error instanceof Error ? error.message : 'Failed to get cross-pillar data',
      'session_management'
    );
  }
}

// Experience Liaison Integration
export async function processExperienceLiaisonRequest(event: ExperienceLiaisonEvent): Promise<any> {
  try {
    const response = await fetch(
      `${API_URL}/api/experience/liaison/process`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(event),
      },
    );

    const responseText = await response.text();
    console.log("Experience liaison request raw response:", responseText);

    if (!response.ok) {
      throw parseAPIError(response, responseText, 'session_management');
    }

    const data = JSON.parse(responseText);
    return data;
  } catch (error) {
    if (error instanceof ExperienceAPIError) {
      throw error;
    }
    throw new ExperienceAPIError(
      error instanceof Error ? error.message : 'Failed to process experience liaison request',
      'session_management'
    );
  }
} 