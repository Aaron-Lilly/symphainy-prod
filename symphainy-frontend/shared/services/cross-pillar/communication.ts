// Cross-Pillar Communication Module
import { 
  CrossPillarCommunicationRequest,
  CrossPillarCommunicationResponse,
  CrossPillarEvent
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

// Communication types and interfaces
export interface CommunicationChannel {
  id: string;
  name: string;
  type: 'direct' | 'broadcast' | 'multicast';
  sourcePillar: string;
  targetPillars: string[];
  status: 'active' | 'inactive' | 'error';
  lastMessage: string;
  messageCount: number;
}

// Detailed communication message with tracking info (extends base CommunicationMessage)
export interface DetailedCommunicationMessage {
  id: string;
  type: string;
  sourcePillar: string;
  targetPillars: string[];
  content: unknown;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  timestamp: string;
  status: 'sent' | 'delivered' | 'failed' | 'pending';
  metadata?: Record<string, unknown>;
}

export interface CommunicationConfig {
  sessionToken: string;
  channels: CommunicationChannel[];
  retryAttempts: number;
  timeout: number;
  maxMessageSize: number;
}

// Send message with retry logic
export async function sendMessageWithRetry(request: CrossPillarCommunicationRequest, retryAttempts: number = 3): Promise<CrossPillarCommunicationResponse> {
  let lastError: Error | null = null;

  for (let attempt = 1; attempt <= retryAttempts; attempt++) {
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
            attempt: attempt,
          }),
        },
      );

      const responseText = await response.text();
      console.log(`Send message attempt ${attempt} raw response:`, responseText);

      if (!response.ok) {
        throw parseAPIError(response, responseText, 'communication', request.sourcePillar, request.targetPillar);
      }

      const data = JSON.parse(responseText);
      return data;
    } catch (error) {
      lastError = error instanceof Error ? error : new Error('Unknown error');
      console.warn(`Message send attempt ${attempt} failed:`, lastError.message);
      
      if (attempt < retryAttempts) {
        // Wait before retrying (exponential backoff)
        await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000));
      }
    }
  }

  throw new CrossPillarAPIError(
    `Failed to send message after ${retryAttempts} attempts: ${lastError?.message}`,
    'communication',
    undefined,
    undefined,
    request.sourcePillar,
    request.targetPillar
  );
}

// Broadcast message to multiple pillars
export interface BroadcastRequest {
  sessionToken: string;
  sourcePillar: 'content' | 'insights' | 'operations' | 'experience';
  targetPillars: ('content' | 'insights' | 'operations' | 'experience')[];
  messageType: 'data_request' | 'state_update' | 'error_notification' | 'status_update';
  message: any;
  priority: 'low' | 'medium' | 'high' | 'urgent';
}

export interface BroadcastResult {
  results: CrossPillarCommunicationResponse[];
  summary: {
    total: number;
    successful: number;
    failed: number;
    totalDuration: number;
    avgDuration: number;
  };
}

export async function broadcastMessage(request: BroadcastRequest): Promise<BroadcastResult> {
  const startTime = Date.now();
  const results: CrossPillarCommunicationResponse[] = [];

  // Send messages to all target pillars
  const promises = request.targetPillars.map(async (targetPillar) => {
    const communicationRequest: CrossPillarCommunicationRequest = {
      sessionToken: request.sessionToken,
      sourcePillar: request.sourcePillar,
      targetPillar,
      messageType: request.messageType,
      message: request.message,
      priority: request.priority,
    };

    try {
      const result = await sendMessageWithRetry(communicationRequest);
      return result;
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        messageId: `failed-${Date.now()}-${Math.random()}`,
        timestamp: new Date().toISOString(),
      };
    }
  });

  const messageResults = await Promise.all(promises);
  results.push(...messageResults);

  const totalDuration = Date.now() - startTime;
  const successful = results.filter(r => r.success).length;
  const failed = results.filter(r => !r.success).length;

  return {
    results,
    summary: {
      total: results.length,
      successful,
      failed,
      totalDuration,
      avgDuration: totalDuration / results.length,
    },
  };
}

// Subscribe to cross-pillar events
export interface EventSubscription {
  sessionToken: string;
  pillar: string;
  eventTypes: string[];
  callback: (event: CrossPillarEvent) => void;
}

export interface EventSubscriptionResult {
  subscriptionId: string;
  status: 'active' | 'inactive' | 'error';
  eventTypes: string[];
  lastEvent: string;
}

export async function subscribeToEvents(subscription: EventSubscription): Promise<EventSubscriptionResult> {
  try {
    const response = await fetch(
      `${API_URL}/api/cross-pillar/subscribe`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${subscription.sessionToken}`,
        },
        body: JSON.stringify({
          session_token: subscription.sessionToken,
          pillar: subscription.pillar,
          event_types: subscription.eventTypes,
        }),
      },
    );

    const responseText = await response.text();
    console.log("Subscribe to events raw response:", responseText);

    if (!response.ok) {
      throw parseAPIError(response, responseText, 'communication', subscription.pillar);
    }

    const data = JSON.parse(responseText);
    
    // Set up WebSocket connection for real-time events
    setupEventWebSocket(subscription, data.subscription_id);
    
    return data;
  } catch (error) {
    if (error instanceof CrossPillarAPIError) {
      throw error;
    }
    throw new CrossPillarAPIError(
      error instanceof Error ? error.message : 'Failed to subscribe to events',
      'communication',
      undefined,
      undefined,
      subscription.pillar
    );
  }
}

// Set up WebSocket connection for real-time events
function setupEventWebSocket(subscription: EventSubscription, subscriptionId: string) {
  const wsUrl = `${API_URL.replace('http', 'ws')}/api/cross-pillar/events/${subscriptionId}`;
  
  try {
    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      console.log(`WebSocket connected for subscription ${subscriptionId}`);
    };
    
    ws.onmessage = (event) => {
      try {
        const crossPillarEvent: CrossPillarEvent = JSON.parse(event.data);
        subscription.callback(crossPillarEvent);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };
    
    ws.onerror = (error) => {
      console.error(`WebSocket error for subscription ${subscriptionId}:`, error);
    };
    
    ws.onclose = () => {
      console.log(`WebSocket disconnected for subscription ${subscriptionId}`);
    };
    
    // Store WebSocket connection for cleanup
    (window as any).crossPillarWebSockets = (window as any).crossPillarWebSockets || {};
    (window as any).crossPillarWebSockets[subscriptionId] = ws;
  } catch (error) {
    console.error('Failed to set up WebSocket connection:', error);
  }
}

// Unsubscribe from events
export async function unsubscribeFromEvents(sessionToken: string, subscriptionId: string): Promise<{ success: boolean }> {
  try {
    const response = await fetch(
      `${API_URL}/api/cross-pillar/unsubscribe`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${sessionToken}`,
        },
        body: JSON.stringify({
          session_token: sessionToken,
          subscription_id: subscriptionId,
        }),
      },
    );

    const responseText = await response.text();
    console.log("Unsubscribe from events raw response:", responseText);

    if (!response.ok) {
      throw parseAPIError(response, responseText, 'communication');
    }

    // Close WebSocket connection
    if ((window as any).crossPillarWebSockets?.[subscriptionId]) {
      (window as any).crossPillarWebSockets[subscriptionId].close();
      delete (window as any).crossPillarWebSockets[subscriptionId];
    }

    const data = JSON.parse(responseText);
    return data;
  } catch (error) {
    if (error instanceof CrossPillarAPIError) {
      throw error;
    }
    throw new CrossPillarAPIError(
      error instanceof Error ? error.message : 'Failed to unsubscribe from events',
      'communication'
    );
  }
}

// Get communication channels
export async function getCommunicationChannels(sessionToken: string): Promise<CommunicationChannel[]> {
  try {
    const response = await fetch(
      `${API_URL}/api/cross-pillar/channels?session_token=${encodeURIComponent(sessionToken)}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${sessionToken}`,
        },
      },
    );

    const responseText = await response.text();
    console.log("Get communication channels raw response:", responseText);

    if (!response.ok) {
      throw parseAPIError(response, responseText, 'communication');
    }

    const data = JSON.parse(responseText);
    return data.channels || [];
  } catch (error) {
    if (error instanceof CrossPillarAPIError) {
      throw error;
    }
    throw new CrossPillarAPIError(
      error instanceof Error ? error.message : 'Failed to get communication channels',
      'communication'
    );
  }
} 