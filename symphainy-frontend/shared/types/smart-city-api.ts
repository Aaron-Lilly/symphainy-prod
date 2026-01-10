/**
 * Smart City API Types
 * Type definitions for Smart City chat and workflow responses
 */

// Export types as both type and value for compatibility
export type AgentType = 'guide' | 'liaison' | 'specialist' | 'analyst' | 'orchestrator';
export type PillarType = 'content' | 'insights' | 'operations' | 'business-outcomes';

// Also export as const enums for runtime use
export const AgentType = {
  GUIDE: 'guide',
  LIAISON: 'liaison',
  SPECIALIST: 'specialist',
  ANALYST: 'analyst',
  ORCHESTRATOR: 'orchestrator'
} as const;

export const PillarType = {
  CONTENT: 'content',
  INSIGHTS: 'insights',
  OPERATIONS: 'operations',
  BUSINESS_OUTCOMES: 'business-outcomes'
} as const;

export interface ChatResponse {
  type: 'chat';
  message: string;
  agent: AgentType;
  pillar?: PillarType;
  metadata?: {
    intent?: string;
    confidence?: number;
    suggested_actions?: string[];
  };
}

export interface WorkflowResponse {
  type: 'workflow';
  workflow_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  result?: any;
  agent: AgentType;
  pillar?: PillarType;
}

export interface ErrorResponse {
  type: 'error';
  error: string;
  code?: string;
  details?: any;
}

export type SmartCityResponse = ChatResponse | WorkflowResponse | ErrorResponse;

export function isChatResponse(response: SmartCityResponse): response is ChatResponse {
  return response.type === 'chat';
}

export function isWorkflowResponse(response: SmartCityResponse): response is WorkflowResponse {
  return response.type === 'workflow';
}

export function isErrorResponse(response: SmartCityResponse): response is ErrorResponse {
  return response.type === 'error';
}

// Additional types for archived files
export interface WebSocketMessage {
  type: string;
  data?: any;
}

export interface ChatMessage {
  id: string;
  content: string;
  agent: AgentType;
  timestamp: string;
}

export interface WorkflowRequest {
  workflow_type: string;
  parameters?: any;
}

export interface WebSocketResponse {
  type: string;
  data?: any;
}

export interface SmartCityWebSocketClient {
  connect(): void;
  disconnect(): void;
  sendMessage(message: string): void;
}

export function createChatMessage(content: string, agent: AgentType): ChatMessage {
  return {
    id: `msg_${Date.now()}`,
    content,
    agent,
    timestamp: new Date().toISOString()
  };
}

export function createWorkflowRequest(workflowType: string, parameters?: any): WorkflowRequest {
  return {
    workflow_type: workflowType,
    parameters
  };
}
