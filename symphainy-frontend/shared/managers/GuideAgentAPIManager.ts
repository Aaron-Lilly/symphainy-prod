/**
 * Guide Agent API Manager
 * 
 * Centralizes all Guide Agent API calls using intent-based architecture.
 * 
 * Note: This manager delegates to OperationsAPIManager for intent-based operations.
 * Guide agent operations are part of the Operations realm.
 * 
 * NAMING NOTE: "journey guidance" refers to user journey (platform concept),
 * not the old "Journey Realm" which is now called "Operations Realm".
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

import { useOperationsAPIManager } from '@/shared/hooks/useOperationsAPIManager';

/**
 * Guide Agent API Manager (Intent-Based API)
 * 
 * This manager uses OperationsAPIManager for all operations.
 * Guide agent operations are part of the Operations realm and use intent-based API.
 */
export class GuideAgentAPIManager {
  private operationsAPIManager: ReturnType<typeof useOperationsAPIManager>;

  constructor(operationsAPIManager: ReturnType<typeof useOperationsAPIManager>) {
    this.operationsAPIManager = operationsAPIManager;
  }

  /**
   * Analyze user intent
   * 
   * Uses OperationsAPIManager (intent-based API)
   */
  async analyzeUserIntent(request: AnalyzeIntentRequest): Promise<AnalyzeIntentResponse> {
    const result = await this.operationsAPIManager.analyzeUserIntent(
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
   * Get journey guidance (user journey through pillars)
   * 
   * NOTE: "journey" here refers to user journey (platform concept),
   * not the old realm name which is now "Operations Realm".
   * 
   * Uses OperationsAPIManager (intent-based API)
   */
  async getJourneyGuidance(request: JourneyGuidanceRequest): Promise<JourneyGuidanceResponse> {
    const result = await this.operationsAPIManager.getJourneyGuidance(
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
   * Uses OperationsAPIManager (intent-based API)
   */
  async getConversationHistory(sessionId: string): Promise<ConversationHistoryResponse> {
    const result = await this.operationsAPIManager.getConversationHistory(sessionId);

    return {
      success: result.success,
      conversation_history: result.conversation_history,
      error: result.error
    };
  }
}

// Factory function for use in components
export function useGuideAgentAPIManager(): GuideAgentAPIManager {
  const operationsAPIManager = useOperationsAPIManager();
  return new GuideAgentAPIManager(operationsAPIManager);
}
