// Cross-Pillar Service Core
import { 
  CrossPillarDataRequest,
  CrossPillarDataResponse,
  CrossPillarCommunicationRequest,
  CrossPillarCommunicationResponse,
  CrossPillarStateSyncRequest,
  CrossPillarStateSyncResponse,
  CrossPillarValidationRequest,
  CrossPillarValidationResponse,
  CrossPillarErrorResponse,
  CrossPillarBridgeConfig,
  CrossPillarBridgeState,
  CrossPillarEvent,
  CrossPillarPerformanceMetrics,
  CrossPillarHealthCheck
} from './types';

import { getApiUrl } from '@/shared/config/api-config';

// Use centralized API config (NO hardcoded values)
const API_URL = getApiUrl();

// Error handling utilities
class CrossPillarAPIError extends Error {
  public code?: string;
  public details?: any;
  public operation: 'data_sharing' | 'communication' | 'state_sync' | 'validation';
  public sourcePillar?: string;
  public targetPillar?: string;

  constructor(
    message: string,
    operation: 'data_sharing' | 'communication' | 'state_sync' | 'validation',
    code?: string,
    details?: any,
    sourcePillar?: string,
    targetPillar?: string
  ) {
    super(message);
    this.name = 'CrossPillarAPIError';
    this.operation = operation;
    this.code = code;
    this.details = details;
    this.sourcePillar = sourcePillar;
    this.targetPillar = targetPillar;
  }
}

// Enhanced error parsing
function parseAPIError(response: Response, responseText: string, operation: 'data_sharing' | 'communication' | 'state_sync' | 'validation', sourcePillar?: string, targetPillar?: string): CrossPillarAPIError {
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
    '400': 'Invalid cross-pillar request. Please check your data and try again.',
    '401': 'Authentication required. Please log in again.',
    '403': 'Access denied. You may not have permission for cross-pillar operations.',
    '404': 'Cross-pillar service not found. The service may be temporarily unavailable.',
    '422': 'Invalid cross-pillar data format. Please ensure your data is in the correct format.',
    '500': 'Cross-pillar service error. Please try again later or contact support.',
    '502': 'Cross-pillar service temporarily unavailable. Please try again later.',
    '503': 'Cross-pillar service temporarily unavailable. Please try again later.',
    '504': 'Cross-pillar request timeout. Please try again with a smaller dataset.',
  };

  const friendlyMessage = userFriendlyMessages[errorCode] || errorMessage;

  return new CrossPillarAPIError(friendlyMessage, operation, errorCode, errorDetails, sourcePillar, targetPillar);
}

// Core Cross-Pillar API Functions
export async function shareCrossPillarData(request: CrossPillarDataRequest): Promise<CrossPillarDataResponse> {
  try {
    const response = await fetch(
      `${API_URL}/api/cross-pillar/share-data`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${request.sessionToken}`,
        },
        body: JSON.stringify({
          session_token: request.sessionToken,
          source_pillar: request.sourcePillar,
          target_pillar: request.targetPillar,
          data_type: request.dataType,
          data: request.data,
          context: request.context || {},
        }),
      },
    );

    const responseText = await response.text();
    console.log("Share cross-pillar data raw response:", responseText);

    if (!response.ok) {
      throw parseAPIError(response, responseText, 'data_sharing', request.sourcePillar, request.targetPillar);
    }

    const data = JSON.parse(responseText);
    return data;
  } catch (error) {
    if (error instanceof CrossPillarAPIError) {
      throw error;
    }
    throw new CrossPillarAPIError(
      error instanceof Error ? error.message : 'Failed to share cross-pillar data',
      'data_sharing',
      undefined,
      undefined,
      request.sourcePillar,
      request.targetPillar
    );
  }
}

export async function sendCrossPillarCommunication(request: CrossPillarCommunicationRequest): Promise<CrossPillarCommunicationResponse> {
  try {
    const response = await fetch(
      `${API_URL}/api/cross-pillar/communicate`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${request.sessionToken}`,
        },
        body: JSON.stringify({
          session_token: request.sessionToken,
          source_pillar: request.sourcePillar,
          target_pillar: request.targetPillar,
          message_type: request.messageType,
          message: request.message,
          priority: request.priority,
        }),
      },
    );

    const responseText = await response.text();
    console.log("Send cross-pillar communication raw response:", responseText);

    if (!response.ok) {
      throw parseAPIError(response, responseText, 'communication', request.sourcePillar, request.targetPillar);
    }

    const data = JSON.parse(responseText);
    return data;
  } catch (error) {
    if (error instanceof CrossPillarAPIError) {
      throw error;
    }
    throw new CrossPillarAPIError(
      error instanceof Error ? error.message : 'Failed to send cross-pillar communication',
      'communication',
      undefined,
      undefined,
      request.sourcePillar,
      request.targetPillar
    );
  }
}

export async function syncCrossPillarState(request: CrossPillarStateSyncRequest): Promise<CrossPillarStateSyncResponse> {
  try {
    const response = await fetch(
      `${API_URL}/api/cross-pillar/sync-state`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${request.sessionToken}`,
        },
        body: JSON.stringify({
          session_token: request.sessionToken,
          pillar: request.pillar,
          state: request.state,
          version: request.version,
          timestamp: request.timestamp,
        }),
      },
    );

    const responseText = await response.text();
    console.log("Sync cross-pillar state raw response:", responseText);

    if (!response.ok) {
      throw parseAPIError(response, responseText, 'state_sync', request.pillar);
    }

    const data = JSON.parse(responseText);
    return data;
  } catch (error) {
    if (error instanceof CrossPillarAPIError) {
      throw error;
    }
    throw new CrossPillarAPIError(
      error instanceof Error ? error.message : 'Failed to sync cross-pillar state',
      'state_sync',
      undefined,
      undefined,
      request.pillar
    );
  }
}

export async function validateCrossPillarData(request: CrossPillarValidationRequest): Promise<CrossPillarValidationResponse> {
  try {
    const response = await fetch(
      `${API_URL}/api/cross-pillar/validate`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${request.sessionToken}`,
        },
        body: JSON.stringify({
          session_token: request.sessionToken,
          data: request.data,
          data_type: request.dataType,
          source_pillar: request.sourcePillar,
          target_pillar: request.targetPillar,
          validation_rules: request.validationRules,
        }),
      },
    );

    const responseText = await response.text();
    console.log("Validate cross-pillar data raw response:", responseText);

    if (!response.ok) {
      throw parseAPIError(response, responseText, 'validation', request.sourcePillar, request.targetPillar);
    }

    const data = JSON.parse(responseText);
    return data;
  } catch (error) {
    if (error instanceof CrossPillarAPIError) {
      throw error;
    }
    throw new CrossPillarAPIError(
      error instanceof Error ? error.message : 'Failed to validate cross-pillar data',
      'validation',
      undefined,
      undefined,
      request.sourcePillar,
      request.targetPillar
    );
  }
}

export async function getCrossPillarBridgeState(sessionToken: string): Promise<CrossPillarBridgeState> {
  try {
    const response = await fetch(
      `${API_URL}/api/cross-pillar/bridge-state?session_token=${encodeURIComponent(sessionToken)}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${sessionToken}`,
        },
      },
    );

    const responseText = await response.text();
    console.log("Get cross-pillar bridge state raw response:", responseText);

    if (!response.ok) {
      throw parseAPIError(response, responseText, 'data_sharing');
    }

    const data = JSON.parse(responseText);
    return data;
  } catch (error) {
    if (error instanceof CrossPillarAPIError) {
      throw error;
    }
    throw new CrossPillarAPIError(
      error instanceof Error ? error.message : 'Failed to get cross-pillar bridge state',
      'data_sharing'
    );
  }
} 