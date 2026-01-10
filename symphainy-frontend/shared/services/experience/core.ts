// Experience Service Core
import { 
  ExperienceSessionResponse,
  ExperienceRoadmapResponse,
  ExperiencePOCResponse,
  ExperienceDocumentResponse,
  ExperienceErrorResponse,
  SourceFile,
  AdditionalContextRequest,
  ExperienceSessionState,
  RoadmapGenerationRequest,
  POCGenerationRequest,
  DocumentGenerationRequest,
  ExperienceOutputsRequest,
  ExperienceOutputsResponse
} from './types';

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

// Core Experience API Functions
export async function getExperienceSession(sessionToken: string): Promise<ExperienceSessionResponse> {
  try {
    const response = await fetch(
      `${API_URL}/api/experience/session?session_token=${encodeURIComponent(sessionToken)}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${sessionToken}`,
        },
      },
    );

    const responseText = await response.text();
    console.log("Get experience session raw response:", responseText);

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
      error instanceof Error ? error.message : 'Failed to get experience session',
      'session_management'
    );
  }
}

export async function createExperienceSession(sessionToken: string): Promise<ExperienceSessionResponse> {
  try {
    const response = await fetch(
      `${API_URL}/api/experience/session`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${sessionToken}`,
        },
        body: JSON.stringify({
          session_token: sessionToken,
        }),
      },
    );

    const responseText = await response.text();
    console.log("Create experience session raw response:", responseText);

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
      error instanceof Error ? error.message : 'Failed to create experience session',
      'session_management'
    );
  }
}

export async function getExperienceSessionState(sessionToken: string): Promise<ExperienceSessionState> {
  try {
    const response = await fetch(
      `${API_URL}/api/experience/session/state?session_token=${encodeURIComponent(sessionToken)}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${sessionToken}`,
        },
      },
    );

    const responseText = await response.text();
    console.log("Get experience session state raw response:", responseText);

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
      error instanceof Error ? error.message : 'Failed to get experience session state',
      'session_management'
    );
  }
}

export async function storeAdditionalContext(request: AdditionalContextRequest): Promise<{ success: boolean; message: string }> {
  try {
    const response = await fetch(
      `${API_URL}/api/experience/context`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${request.session_token}`,
        },
        body: JSON.stringify({
          session_token: request.session_token,
          context_type: request.context_type,
          context_data: request.context_data,
          priority: request.priority,
        }),
      },
    );

    const responseText = await response.text();
    console.log("Store additional context raw response:", responseText);

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
      error instanceof Error ? error.message : 'Failed to store additional context',
      'session_management'
    );
  }
}

export async function generateExperienceOutputs(request: ExperienceOutputsRequest): Promise<ExperienceOutputsResponse> {
  try {
    const response = await fetch(
      `${API_URL}/api/experience/outputs`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${request.sessionToken}`,
        },
        body: JSON.stringify({
          session_token: request.sessionToken,
          output_type: request.outputType,
          format: request.format,
          include_visualizations: request.includeVisualizations,
        }),
      },
    );

    const responseText = await response.text();
    console.log("Generate experience outputs raw response:", responseText);

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
      error instanceof Error ? error.message : 'Failed to generate experience outputs',
      'roadmap_generation'
    );
  }
}

export async function getSourceFiles(sessionToken: string): Promise<SourceFile[]> {
  try {
    const response = await fetch(
      `${API_URL}/api/experience/source-files?session_token=${encodeURIComponent(sessionToken)}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${sessionToken}`,
        },
      },
    );

    const responseText = await response.text();
    console.log("Get source files raw response:", responseText);

    if (!response.ok) {
      throw parseAPIError(response, responseText, 'session_management');
    }

    const data = JSON.parse(responseText);
    return data.files || [];
  } catch (error) {
    if (error instanceof ExperienceAPIError) {
      throw error;
    }
    throw new ExperienceAPIError(
      error instanceof Error ? error.message : 'Failed to get source files',
      'session_management'
    );
  }
} 