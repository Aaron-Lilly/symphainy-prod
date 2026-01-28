/**
 * Cross-Pillar Service Types
 * 
 * Type definitions for cross-pillar communication and data sharing.
 */

export type PillarType = 'content' | 'insights' | 'operations' | 'experience';

/**
 * Cross-pillar data payload structure
 */
export interface CrossPillarDataPayload {
  dataId?: string;
  content: Record<string, unknown>;
  metadata?: Record<string, unknown>;
}

/**
 * Cross-pillar context structure
 */
export interface CrossPillarContext {
  sourceOperation?: string;
  targetOperation?: string;
  artifacts?: string[];
  parameters?: Record<string, unknown>;
}

export interface CrossPillarDataRequest {
  sessionToken: string;
  sourcePillar: PillarType;
  targetPillar: PillarType;
  dataType: string;
  data: CrossPillarDataPayload;
  context?: CrossPillarContext;
}

export interface CrossPillarDataResponse {
  success: boolean;
  data?: CrossPillarDataPayload;
  error?: string;
  sourcePillar: string;
  targetPillar: string;
  dataType: string;
  timestamp: string;
}

/**
 * Communication message structure
 */
export interface CommunicationMessage {
  type: string;
  content: string | Record<string, unknown>;
  metadata?: Record<string, unknown>;
}

export interface CrossPillarCommunicationRequest {
  sessionToken: string;
  sourcePillar: PillarType;
  targetPillar: PillarType;
  messageType: 'data_request' | 'state_update' | 'error_notification' | 'status_update';
  message: CommunicationMessage;
  priority: 'low' | 'medium' | 'high' | 'urgent';
}

/**
 * Communication response payload
 */
export interface CommunicationResponsePayload {
  acknowledgment?: boolean;
  data?: Record<string, unknown>;
  status?: string;
}

export interface CrossPillarCommunicationResponse {
  success: boolean;
  response?: CommunicationResponsePayload;
  error?: string;
  messageId: string;
  timestamp: string;
}

/**
 * Pillar state structure for sync
 */
export interface PillarState {
  currentOperation?: string;
  artifacts?: string[];
  progress?: number;
  status?: string;
  data?: Record<string, unknown>;
}

export interface CrossPillarStateSyncRequest {
  sessionToken: string;
  pillar: PillarType;
  state: PillarState;
  version: string;
  timestamp: string;
}

/**
 * State conflict structure
 */
export interface StateConflict {
  field: string;
  localValue: unknown;
  remoteValue: unknown;
  resolution?: 'local' | 'remote' | 'merge';
}

export interface CrossPillarStateSyncResponse {
  success: boolean;
  syncedState?: PillarState;
  conflicts?: StateConflict[];
  error?: string;
  version: string;
  timestamp: string;
}

/**
 * Validation rules structure
 */
export interface ValidationRules {
  requiredFields?: string[];
  typeChecks?: Record<string, string>;
  customValidators?: Array<{ field: string; rule: string }>;
}

export interface CrossPillarValidationRequest {
  sessionToken: string;
  data: CrossPillarDataPayload;
  dataType: string;
  sourcePillar: string;
  targetPillar: string;
  validationRules: ValidationRules;
}

export interface CrossPillarValidationResponse {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  suggestions: string[];
  validationScore: number; // 0-100
}

/**
 * Error details structure
 */
export interface CrossPillarErrorDetails {
  failedOperation?: string;
  attemptedData?: Record<string, unknown>;
  validationErrors?: string[];
  stackTrace?: string;
}

export interface CrossPillarErrorResponse {
  message: string;
  operation: 'data_sharing' | 'communication' | 'state_sync' | 'validation';
  code?: string;
  sourcePillar?: string;
  targetPillar?: string;
  details?: CrossPillarErrorDetails;
}

export interface CrossPillarBridgeConfig {
  sessionToken: string;
  pillars: {
    content: boolean;
    insights: boolean;
    operations: boolean;
    experience: boolean;
  };
  dataTypes: string[];
  communicationChannels: string[];
  syncInterval: number; // milliseconds
  retryAttempts: number;
  timeout: number; // milliseconds
}

export interface CrossPillarBridgeState {
  isConnected: boolean;
  activePillars: string[];
  lastSync: string;
  errors: string[];
  warnings: string[];
  performance: {
    avgResponseTime: number;
    successRate: number;
    totalRequests: number;
    failedRequests: number;
  };
}

/**
 * Event metadata structure
 */
export interface CrossPillarEventMetadata {
  operationId?: string;
  correlationId?: string;
  retryCount?: number;
  duration?: number;
}

export interface CrossPillarEvent {
  type: 'data_shared' | 'state_synced' | 'communication_sent' | 'validation_completed' | 'error_occurred';
  sessionToken: string;
  sourcePillar: string;
  targetPillar?: string;
  data?: CrossPillarDataPayload;
  timestamp: string;
  metadata?: CrossPillarEventMetadata;
}

export interface CrossPillarPerformanceMetrics {
  sessionToken: string;
  timestamp: string;
  metrics: {
    dataSharing: {
      totalRequests: number;
      successfulRequests: number;
      failedRequests: number;
      avgResponseTime: number;
    };
    communication: {
      totalMessages: number;
      deliveredMessages: number;
      failedMessages: number;
      avgDeliveryTime: number;
    };
    stateSync: {
      totalSyncs: number;
      successfulSyncs: number;
      failedSyncs: number;
      avgSyncTime: number;
    };
    validation: {
      totalValidations: number;
      passedValidations: number;
      failedValidations: number;
      avgValidationTime: number;
    };
  };
}

export interface CrossPillarHealthCheck {
  sessionToken: string;
  timestamp: string;
  status: 'healthy' | 'degraded' | 'unhealthy';
  checks: {
    dataSharing: 'healthy' | 'degraded' | 'unhealthy';
    communication: 'healthy' | 'degraded' | 'unhealthy';
    stateSync: 'healthy' | 'degraded' | 'unhealthy';
    validation: 'healthy' | 'degraded' | 'unhealthy';
  };
  details: {
    dataSharing?: string;
    communication?: string;
    stateSync?: string;
    validation?: string;
  };
} 