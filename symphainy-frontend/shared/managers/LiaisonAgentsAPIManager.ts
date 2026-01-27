/**
 * Liaison Agents API Manager
 * 
 * ✅ PHASE 5.6.4: Migrated to intent-based API
 * 
 * Centralizes all Liaison Agent API calls using intent-based architecture.
 * 
 * Note: This manager now delegates to JourneyAPIManager for intent-based operations.
 * Liaison agent operations use intent-based API through Journey realm.
 */

// ============================================
// Liaison Agents API Manager Types
// ============================================

export type PillarType = 'content' | 'insights' | 'journey' | 'outcomes';

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

import { useJourneyAPIManager } from '@/shared/hooks/useJourneyAPIManager';

/**
 * ✅ PHASE 5.6.4: Liaison Agents API Manager (Migrated to Intent-Based API)
 * 
 * This manager now uses JourneyAPIManager for all operations.
 * Liaison agent operations use intent-based API through Journey realm.
 */
export class LiaisonAgentsAPIManager {
  private journeyAPIManager: ReturnType<typeof useJourneyAPIManager>;

  constructor(journeyAPIManager: ReturnType<typeof useJourneyAPIManager>) {
    this.journeyAPIManager = journeyAPIManager;
  }

  /**
   * Send message to pillar agent
   * 
   * ✅ PHASE 5.6.4: Uses JourneyAPIManager (intent-based API)
   */
  async sendMessageToPillarAgent(request: SendMessageRequest): Promise<SendMessageResponse> {
    const result = await this.journeyAPIManager.sendMessageToPillarAgent(
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
   * ✅ PHASE 5.6.4: Uses JourneyAPIManager (intent-based API)
   */
  async getPillarConversationHistory(sessionId: string, pillar: PillarType): Promise<ConversationHistoryResponse> {
    const result = await this.journeyAPIManager.getPillarConversationHistory(sessionId, pillar);

    return {
      success: result.success,
      conversation: result.conversation,
      error: result.error
    };
  }
}

// Factory function for use in components
export function useLiaisonAgentsAPIManager(): LiaisonAgentsAPIManager {
  const journeyAPIManager = useJourneyAPIManager();
  return new LiaisonAgentsAPIManager(journeyAPIManager);
}
