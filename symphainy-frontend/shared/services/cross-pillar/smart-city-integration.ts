// Smart City Integration Module
import { 
  CrossPillarEvent,
  CrossPillarPerformanceMetrics,
  CrossPillarHealthCheck
} from './types';

// EC2 default: http://35.215.64.103:8000 (accessible from outside EC2)
// Option C: Override via NEXT_PUBLIC_API_URL environment variable
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

// Traffic Cop Integration - Cross-Pillar Routing
export interface TrafficCopRoutingRequest {
  sessionToken: string;
  sourcePillar: string;
  targetPillar: string;
  operation: string;
  data?: any;
  priority: 'low' | 'medium' | 'high' | 'urgent';
}

export interface TrafficCopRoutingResponse {
  routeId: string;
  status: 'approved' | 'pending' | 'rejected' | 'rerouted';
  route: {
    path: string[];
    estimatedTime: number;
    cost: number;
    reliability: number;
  };
  restrictions: string[];
  alternatives: string[];
}

export async function routeCrossPillarRequest(request: TrafficCopRoutingRequest): Promise<TrafficCopRoutingResponse> {
  try {
    const response = await fetch(
      `${API_URL}/api/cross-pillar/traffic-cop/route`,
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
          operation: request.operation,
          data: request.data,
          priority: request.priority,
        }),
      },
    );

    const responseText = await response.text();
    console.log("Traffic Cop routing raw response:", responseText);

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
      error instanceof Error ? error.message : 'Failed to route cross-pillar request',
      'data_sharing',
      undefined,
      undefined,
      request.sourcePillar,
      request.targetPillar
    );
  }
}

// Post Office Integration - Cross-Pillar Message Delivery
export interface PostOfficeMessage {
  type: string;
  sessionToken: string;
  sourcePillar: string;
  targetPillar: string;
  data: any;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  timestamp: string;
  metadata?: any;
}

export interface PostOfficeResponse {
  messageId: string;
  status: 'queued' | 'delivered' | 'failed' | 'pending';
  recipient: string;
  timestamp: string;
  deliveryTime?: number;
}

export async function sendCrossPillarMessage(message: PostOfficeMessage): Promise<PostOfficeResponse> {
  try {
    const response = await fetch(
      `${API_URL}/api/cross-pillar/post-office/send`,
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
      throw parseAPIError(response, responseText, 'communication', message.sourcePillar, message.targetPillar);
    }

    const data = JSON.parse(responseText);
    return data;
  } catch (error) {
    if (error instanceof CrossPillarAPIError) {
      throw error;
    }
    throw new CrossPillarAPIError(
      error instanceof Error ? error.message : 'Failed to send cross-pillar message',
      'communication',
      undefined,
      undefined,
      message.sourcePillar,
      message.targetPillar
    );
  }
}

// Conductor Integration - Cross-Pillar Orchestration
export interface ConductorOrchestrationRequest {
  sessionToken: string;
  workflowType: 'data_sharing' | 'communication' | 'state_sync' | 'validation' | 'comprehensive';
  sourcePillar: string;
  targetPillar: string;
  inputs: any;
  priority: 'low' | 'medium' | 'high';
}

export interface ConductorOrchestrationResponse {
  workflowId: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
  progress: number;
  estimatedCompletion: string;
  currentStep: string;
  results?: any;
}

export async function orchestrateCrossPillarWorkflow(request: ConductorOrchestrationRequest): Promise<ConductorOrchestrationResponse> {
  try {
    const response = await fetch(
      `${API_URL}/api/cross-pillar/conductor/orchestrate`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${request.sessionToken}`,
        },
        body: JSON.stringify({
          session_token: request.sessionToken,
          workflow_type: request.workflowType,
          source_pillar: request.sourcePillar,
          target_pillar: request.targetPillar,
          inputs: request.inputs,
          priority: request.priority,
        }),
      },
    );

    const responseText = await response.text();
    console.log("Conductor orchestration raw response:", responseText);

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
      error instanceof Error ? error.message : 'Failed to orchestrate cross-pillar workflow',
      'data_sharing',
      undefined,
      undefined,
      request.sourcePillar,
      request.targetPillar
    );
  }
}

// Archive Integration - Cross-Pillar State Persistence
export interface ArchiveStateRequest {
  sessionToken: string;
  pillar: string;
  state: any;
  metadata: {
    operation: string;
    timestamp: string;
    userId: string;
    version: string;
    crossPillar: boolean;
  };
}

export interface ArchiveStateResponse {
  stateId: string;
  status: 'saved' | 'failed';
  timestamp: string;
  version: string;
  crossPillarReferences?: string[];
}

export async function persistCrossPillarState(request: ArchiveStateRequest): Promise<ArchiveStateResponse> {
  try {
    const response = await fetch(
      `${API_URL}/api/cross-pillar/archive/persist`,
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
          metadata: request.metadata,
        }),
      },
    );

    const responseText = await response.text();
    console.log("Archive persistence raw response:", responseText);

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
      error instanceof Error ? error.message : 'Failed to persist cross-pillar state',
      'state_sync',
      undefined,
      undefined,
      request.pillar
    );
  }
}

// Performance monitoring
export async function getCrossPillarPerformanceMetrics(sessionToken: string): Promise<CrossPillarPerformanceMetrics> {
  try {
    const response = await fetch(
      `${API_URL}/api/cross-pillar/performance?session_token=${encodeURIComponent(sessionToken)}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${sessionToken}`,
        },
      },
    );

    const responseText = await response.text();
    console.log("Get performance metrics raw response:", responseText);

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
      error instanceof Error ? error.message : 'Failed to get performance metrics',
      'data_sharing'
    );
  }
}

// Health check
export async function getCrossPillarHealthCheck(sessionToken: string): Promise<CrossPillarHealthCheck> {
  try {
    const response = await fetch(
      `${API_URL}/api/cross-pillar/health?session_token=${encodeURIComponent(sessionToken)}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${sessionToken}`,
        },
      },
    );

    const responseText = await response.text();
    console.log("Get health check raw response:", responseText);

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
      error instanceof Error ? error.message : 'Failed to get health check',
      'data_sharing'
    );
  }
}

// Event emission
export async function emitCrossPillarEvent(event: CrossPillarEvent): Promise<{ success: boolean; eventId: string }> {
  try {
    const response = await fetch(
      `${API_URL}/api/cross-pillar/events/emit`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(event),
      },
    );

    const responseText = await response.text();
    console.log("Emit cross-pillar event raw response:", responseText);

    if (!response.ok) {
      throw parseAPIError(response, responseText, 'communication', event.sourcePillar, event.targetPillar);
    }

    const data = JSON.parse(responseText);
    return data;
  } catch (error) {
    if (error instanceof CrossPillarAPIError) {
      throw error;
    }
    throw new CrossPillarAPIError(
      error instanceof Error ? error.message : 'Failed to emit cross-pillar event',
      'communication',
      undefined,
      undefined,
      event.sourcePillar,
      event.targetPillar
    );
  }
} 