/**
 * Guide Agent API Manager
 * 
 * Centralizes all Guide Agent API calls using semantic endpoints.
 * Provides a clean interface for Guide Agent interactions.
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

export class GuideAgentAPIManager {
  private baseURL: string;
  private sessionToken: string;

  constructor(sessionToken: string, baseURL?: string) {
    this.sessionToken = sessionToken;
    // Use centralized API config (NO hardcoded values)
    if (baseURL) {
      this.baseURL = baseURL.replace(':8000', '').replace(/\/$/, '');
    } else {
      // Import here to avoid circular dependency issues
      const { getApiUrl } = require('@/shared/config/api-config');
      this.baseURL = getApiUrl();
    }
  }

  // ============================================
  // User Intent Analysis
  // ============================================

  async analyzeUserIntent(request: AnalyzeIntentRequest): Promise<AnalyzeIntentResponse> {
    try {
      const response = await fetch(`${this.baseURL}/api/v1/journey/guide-agent/analyze-user-intent`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.sessionToken}`,
          'Content-Type': 'application/json',
          'X-Session-Token': this.sessionToken || request.session_token || ''
        },
        body: JSON.stringify({
          message: request.message,
          user_id: request.user_id,
          context: request.context
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        return {
          success: false,
          error: errorData.message || errorData.error || 'Intent analysis failed'
        };
      }

      const data = await response.json();
      return {
        success: data.success,
        intent_analysis: data.intent_analysis,
        session_id: data.session_id,
        timestamp: data.timestamp,
        message: data.message,
        error: data.error
      };
    } catch (error) {
      console.error('Error analyzing user intent:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Intent analysis failed'
      };
    }
  }

  // ============================================
  // Journey Guidance
  // ============================================

  async getJourneyGuidance(request: JourneyGuidanceRequest): Promise<JourneyGuidanceResponse> {
    try {
      const response = await fetch(`${this.baseURL}/api/v1/journey/guide-agent/get-journey-guidance`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.sessionToken}`,
          'Content-Type': 'application/json',
          'X-Session-Token': this.sessionToken || request.session_token || ''
        },
        body: JSON.stringify({
          user_goal: request.user_goal,
          current_step: request.current_step,
          context: request.context
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        return {
          success: false,
          error: errorData.message || errorData.error || 'Journey guidance failed'
        };
      }

      const data = await response.json();
      return {
        success: data.success,
        guidance: data.guidance,
        next_steps: data.next_steps,
        session_id: data.session_id,
        message: data.message,
        error: data.error
      };
    } catch (error) {
      console.error('Error getting journey guidance:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Journey guidance failed'
      };
    }
  }

  // ============================================
  // Conversation History
  // ============================================

  async getConversationHistory(sessionId: string): Promise<ConversationHistoryResponse> {
    try {
      const response = await fetch(`${this.baseURL}/api/v1/journey/guide-agent/get-conversation-history/${sessionId}`, {
        headers: {
          'Authorization': `Bearer ${this.sessionToken}`,
          'Content-Type': 'application/json',
          'X-Session-Token': this.sessionToken
        }
      });

      if (!response.ok) {
        const errorData = await response.json();
        return {
          success: false,
          error: errorData.message || errorData.error || 'Failed to get conversation history'
        };
      }

      const data = await response.json();
      return {
        success: data.success,
        conversation_history: data.conversation_history,
        session_id: data.session_id,
        message: data.message,
        error: data.error
      };
    } catch (error) {
      console.error('Error getting conversation history:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get conversation history'
      };
    }
  }
}






