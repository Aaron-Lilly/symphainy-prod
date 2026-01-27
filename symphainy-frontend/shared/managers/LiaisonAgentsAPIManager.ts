/**
 * Liaison Agents API Manager
 * 
 * Centralizes all Liaison Agent API calls using intent-based architecture.
 * 
 * Note: This manager delegates to OperationsAPIManager for intent-based operations.
 * Liaison agent operations use intent-based API through Operations realm.
 */

// ============================================
// Liaison Agents API Manager Types
// ============================================

export type PillarType = 'content' | 'insights' | 'operations' | 'outcomes';

export interface SendMessageRequest {
  message: string;
  pillar: PillarType;
  session_id?: string;
  conversation_id?: string;
  user_id?: string;
  session_token?: string;
}

export interface SendMessageResponse {
  success: boolean;
  response?: any;
  session_id?: string;
  pillar?: string;
  timestamp?: string;
  message?: string;
  error?: string;
}

export interface ConversationHistoryResponse {
  success: boolean;
  conversation?: any;
  message?: string;
  error?: string;
}

// ============================================
// Liaison Agents API Manager Class
// ============================================

import { useOperationsAPIManager } from '@/shared/hooks/useOperationsAPIManager';

/**
 * Liaison Agents API Manager (Intent-Based API)
 * 
 * This manager uses OperationsAPIManager for all operations.
 * Liaison agent operations use intent-based API through Operations realm.
 */
export class LiaisonAgentsAPIManager {
  private operationsAPIManager: ReturnType<typeof useOperationsAPIManager>;

  constructor(operationsAPIManager: ReturnType<typeof useOperationsAPIManager>) {
    this.operationsAPIManager = operationsAPIManager;
  }

  /**
   * Send message to pillar agent
   * 
   * Uses OperationsAPIManager (intent-based API)
   */
  async sendMessageToPillarAgent(request: SendMessageRequest): Promise<SendMessageResponse> {
    const result = await this.operationsAPIManager.sendMessageToPillarAgent(
      request.message,
      request.pillar,
      request.conversation_id,
      { session_id: request.session_id, user_id: request.user_id }
    );

    return {
      success: result.success,
      response: result.response,
      error: result.error
    };
  }

  /**
   * Get pillar conversation history
   * 
   * Uses OperationsAPIManager (intent-based API)
   */
  async getPillarConversationHistory(sessionId: string, pillar: PillarType): Promise<ConversationHistoryResponse> {
    const result = await this.operationsAPIManager.getPillarConversationHistory(sessionId, pillar);

    return {
      success: result.success,
      conversation: result.conversation,
      error: result.error
    };
  }
}

// Factory function for use in components
export function useLiaisonAgentsAPIManager(): LiaisonAgentsAPIManager {
  const operationsAPIManager = useOperationsAPIManager();
  return new LiaisonAgentsAPIManager(operationsAPIManager);
}
