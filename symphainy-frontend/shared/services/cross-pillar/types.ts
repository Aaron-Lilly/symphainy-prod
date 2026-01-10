// Cross-Pillar Service Types
export interface CrossPillarDataRequest {
  sessionToken: string;
  sourcePillar: 'content' | 'insights' | 'operations' | 'experience';
  targetPillar: 'content' | 'insights' | 'operations' | 'experience';
  dataType: string;
  data: any;
  context?: any;
}

export interface CrossPillarDataResponse {
  success: boolean;
  data?: any;
  error?: string;
  sourcePillar: string;
  targetPillar: string;
  dataType: string;
  timestamp: string;
}

export interface CrossPillarCommunicationRequest {
  sessionToken: string;
  sourcePillar: 'content' | 'insights' | 'operations' | 'experience';
  targetPillar: 'content' | 'insights' | 'operations' | 'experience';
  messageType: 'data_request' | 'state_update' | 'error_notification' | 'status_update';
  message: any;
  priority: 'low' | 'medium' | 'high' | 'urgent';
}

export interface CrossPillarCommunicationResponse {
  success: boolean;
  response?: any;
  error?: string;
  messageId: string;
  timestamp: string;
}

export interface CrossPillarStateSyncRequest {
  sessionToken: string;
  pillar: 'content' | 'insights' | 'operations' | 'experience';
  state: any;
  version: string;
  timestamp: string;
}

export interface CrossPillarStateSyncResponse {
  success: boolean;
  syncedState?: any;
  conflicts?: any[];
  error?: string;
  version: string;
  timestamp: string;
}

export interface CrossPillarValidationRequest {
  sessionToken: string;
  data: any;
  dataType: string;
  sourcePillar: string;
  targetPillar: string;
  validationRules: any;
}

export interface CrossPillarValidationResponse {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  suggestions: string[];
  validationScore: number; // 0-100
}

export interface CrossPillarErrorResponse {
  message: string;
  operation: 'data_sharing' | 'communication' | 'state_sync' | 'validation';
  code?: string;
  sourcePillar?: string;
  targetPillar?: string;
  details?: any;
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

export interface CrossPillarEvent {
  type: 'data_shared' | 'state_synced' | 'communication_sent' | 'validation_completed' | 'error_occurred';
  sessionToken: string;
  sourcePillar: string;
  targetPillar?: string;
  data?: any;
  timestamp: string;
  metadata?: any;
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