// Cross-Pillar Service Orchestrator
export * from './types';
export * from './communication';
export * from './smart-city-integration';

// Explicit exports from core and data-sharing to avoid conflicts
export {
  shareCrossPillarData,
  sendCrossPillarCommunication,
  syncCrossPillarState,
  validateCrossPillarData,
  getCrossPillarBridgeState
} from './core';

export {
  shareDataWithValidation,
  batchShareData
} from './data-sharing';

// Main CrossPillarService class for unified access
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

import {
  shareCrossPillarData,
  sendCrossPillarCommunication,
  syncCrossPillarState,
  validateCrossPillarData,
  getCrossPillarBridgeState
} from './core';

import {
  shareDataWithValidation,
  batchShareData
} from './data-sharing';

import {
  sendMessageWithRetry,
  broadcastMessage,
  subscribeToEvents,
  unsubscribeFromEvents,
  getCommunicationChannels
} from './communication';

import {
  routeCrossPillarRequest,
  sendCrossPillarMessage,
  orchestrateCrossPillarWorkflow,
  persistCrossPillarState,
  getCrossPillarPerformanceMetrics,
  getCrossPillarHealthCheck,
  emitCrossPillarEvent
} from './smart-city-integration';

export class CrossPillarService {
  // Core Data Sharing
  static async shareData(request: CrossPillarDataRequest): Promise<CrossPillarDataResponse> {
    return shareCrossPillarData(request);
  }

  static async shareDataWithValidation(request: CrossPillarDataRequest): Promise<any> {
    return shareDataWithValidation(request);
  }

  static async batchShareData(request: any): Promise<any> {
    return batchShareData(request);
  }

  // Communication
  static async sendCommunication(request: CrossPillarCommunicationRequest): Promise<CrossPillarCommunicationResponse> {
    return sendCrossPillarCommunication(request);
  }

  static async sendMessageWithRetry(request: CrossPillarCommunicationRequest, retryAttempts: number = 3): Promise<CrossPillarCommunicationResponse> {
    return sendMessageWithRetry(request, retryAttempts);
  }

  static async broadcastMessage(request: any): Promise<any> {
    return broadcastMessage(request);
  }

  static async subscribeToEvents(subscription: any): Promise<any> {
    return subscribeToEvents(subscription);
  }

  static async unsubscribeFromEvents(sessionToken: string, subscriptionId: string): Promise<{ success: boolean }> {
    return unsubscribeFromEvents(sessionToken, subscriptionId);
  }

  static async getCommunicationChannels(sessionToken: string): Promise<any[]> {
    return getCommunicationChannels(sessionToken);
  }

  // State Synchronization
  static async syncState(request: CrossPillarStateSyncRequest): Promise<CrossPillarStateSyncResponse> {
    return syncCrossPillarState(request);
  }

  // Validation
  static async validateData(request: CrossPillarValidationRequest): Promise<CrossPillarValidationResponse> {
    return validateCrossPillarData(request);
  }

  // Bridge State
  static async getBridgeState(sessionToken: string): Promise<CrossPillarBridgeState> {
    return getCrossPillarBridgeState(sessionToken);
  }

  // Smart City Integration - Placeholder methods
  static async routeRequest(request: any): Promise<any> {
    return routeCrossPillarRequest(request);
  }

  static async sendMessage(message: any): Promise<any> {
    return sendCrossPillarMessage(message);
  }

  static async orchestrateWorkflow(request: any): Promise<any> {
    return orchestrateCrossPillarWorkflow(request);
  }

  static async persistState(request: any): Promise<any> {
    return persistCrossPillarState(request);
  }

  // Performance and Health
  static async getPerformanceMetrics(sessionToken: string): Promise<CrossPillarPerformanceMetrics> {
    return getCrossPillarPerformanceMetrics(sessionToken);
  }

  static async getHealthCheck(sessionToken: string): Promise<CrossPillarHealthCheck> {
    return getCrossPillarHealthCheck(sessionToken);
  }

  // Events
  static async emitEvent(event: CrossPillarEvent): Promise<{ success: boolean; eventId: string }> {
    return emitCrossPillarEvent(event);
  }

  // Utility Methods
  static async comprehensiveCrossPillarOperation(
    sessionToken: string,
    sourcePillar: string,
    targetPillar: string,
    operation: 'data_sharing' | 'communication' | 'state_sync' | 'validation' | 'comprehensive',
    data?: any
  ): Promise<any> {
    // Route the request through Traffic Cop
    const routingResponse = await this.routeRequest({
      sessionToken,
      sourcePillar,
      targetPillar,
      operation,
      data,
      priority: 'medium',
    });

    if (routingResponse.status === 'rejected') {
      throw new Error(`Cross-pillar operation rejected: ${routingResponse.restrictions.join(', ')}`);
    }

    // Orchestrate the workflow through Conductor
    const orchestrationResponse = await this.orchestrateWorkflow({
      sessionToken,
      workflowType: operation,
      sourcePillar,
      targetPillar,
      inputs: { data, route: routingResponse.route },
      priority: 'medium',
    });

    return orchestrationResponse;
  }

  static async monitorCrossPillarHealth(sessionToken: string): Promise<{
    health: CrossPillarHealthCheck;
    performance: CrossPillarPerformanceMetrics;
    bridgeState: CrossPillarBridgeState;
  }> {
    const [health, performance, bridgeState] = await Promise.all([
      this.getHealthCheck(sessionToken),
      this.getPerformanceMetrics(sessionToken),
      this.getBridgeState(sessionToken),
    ]);

    return { health, performance, bridgeState };
  }
}

// Default export for convenience
export default CrossPillarService; 