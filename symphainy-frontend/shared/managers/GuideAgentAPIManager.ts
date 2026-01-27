/**
 * Guide Agent API Manager
 * 
 * ✅ PHASE 5.6.3: Migrated to intent-based API
 * 
 * Centralizes all Guide Agent API calls using intent-based architecture.
 * 
 * Note: This manager now delegates to JourneyAPIManager for intent-based operations.
 * Guide agent operations are part of the Journey realm.
 */

// ============================================
// Guide Agent API Manager Types
// ============================================

export interface AnalyzeIntentRequest {
  message: string;
  user_id?: string;
  session_token?: string;
  context?: any;
}

export interface AnalyzeIntentResponse {
  success: boolean;
  intent_analysis?: any;
  session_id?: string;
  timestamp?: string;
  message?: string;
  error?: string;
}

export interface JourneyGuidanceRequest {
  user_goal: string;
  current_step?: string;
  context?: any;
  session_token?: string;
}

export interface JourneyGuidanceResponse {
  success: boolean;
  guidance?: any;
  next_steps?: string[];
  session_id?: string;
  message?: string;
  error?: string;
}

export interface ConversationHistoryResponse {
  success: boolean;
  conversation_history?: any[];
  session_id?: string;
  message?: string;
  error?: string;
}

// ============================================
// Guide Agent API Manager Class
// ============================================

import { useJourneyAPIManager } from '@/shared/hooks/useJourneyAPIManager';

/**
 * ✅ PHASE 5.6.3: Guide Agent API Manager (Migrated to Intent-Based API)
 * 
 * This manager now uses JourneyAPIManager for all operations.
 * Guide agent operations are part of the Journey realm and use intent-based API.
 */
export class GuideAgentAPIManager {
  private journeyAPIManager: ReturnType<typeof useJourneyAPIManager>;

  constructor(journeyAPIManager: ReturnType<typeof useJourneyAPIManager>) {
    this.journeyAPIManager = journeyAPIManager;
  }

  /**
   * Analyze user intent
   * 
   * ✅ PHASE 5.6.3: Uses JourneyAPIManager (intent-based API)
   */
  async analyzeUserIntent(request: AnalyzeIntentRequest): Promise<AnalyzeIntentResponse> {
    const result = await this.journeyAPIManager.analyzeUserIntent(
      request.message,
      request.context
    );

    return {
      success: result.success,
      intent_analysis: result.intent_analysis,
      error: result.error
    };
  }

  /**
   * Get journey guidance
   * 
   * ✅ PHASE 5.6.3: Uses JourneyAPIManager (intent-based API)
   */
  async getJourneyGuidance(request: JourneyGuidanceRequest): Promise<JourneyGuidanceResponse> {
    const result = await this.journeyAPIManager.getJourneyGuidance(
      request.user_goal,
      request.current_step,
      request.context
    );

    return {
      success: result.success,
      guidance: result.guidance,
      next_steps: result.next_steps,
      error: result.error
    };
  }

  /**
   * Get conversation history
   * 
   * ✅ PHASE 5.6.3: Uses JourneyAPIManager (intent-based API)
   */
  async getConversationHistory(sessionId: string): Promise<ConversationHistoryResponse> {
    const result = await this.journeyAPIManager.getConversationHistory(sessionId);

    return {
      success: result.success,
      conversation_history: result.conversation_history,
      error: result.error
    };
  }
}

// Factory function for use in components
export function useGuideAgentAPIManager(): GuideAgentAPIManager {
  const journeyAPIManager = useJourneyAPIManager();
  return new GuideAgentAPIManager(journeyAPIManager);
}
