/**
 * Liaison Agents API Manager
 * 
 * Centralizes all Liaison Agent API calls using semantic endpoints.
 * Provides a clean interface for pillar-specific agent interactions.
 */

// ============================================
// Liaison Agents API Manager Types
// ============================================

export type PillarType = 'content' | 'insights' | 'operations' | 'business-outcomes';

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

export class LiaisonAgentsAPIManager {
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
  // Send Message to Pillar Agent
  // ============================================

  async sendMessageToPillarAgent(request: SendMessageRequest): Promise<SendMessageResponse> {
    try {
      const response = await fetch(`${this.baseURL}/api/v1/liaison-agents/send-message-to-pillar-agent`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.sessionToken}`,
          'Content-Type': 'application/json',
          'X-Session-Token': this.sessionToken || request.session_token || ''
        },
        body: JSON.stringify({
          message: request.message,
          pillar: request.pillar,
          session_id: request.session_id,
          conversation_id: request.conversation_id,
          user_id: request.user_id
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        return {
          success: false,
          error: errorData.message || errorData.error || 'Failed to send message'
        };
      }

      const data = await response.json();
      return {
        success: data.success,
        response: data.response,
        session_id: data.session_id,
        pillar: data.pillar,
        timestamp: data.timestamp,
        message: data.message,
        error: data.error
      };
    } catch (error) {
      console.error('Error sending message to pillar agent:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to send message'
      };
    }
  }

  // ============================================
  // Get Conversation History
  // ============================================

  async getPillarConversationHistory(sessionId: string, pillar: PillarType): Promise<ConversationHistoryResponse> {
    try {
      const response = await fetch(`${this.baseURL}/api/v1/liaison-agents/get-pillar-conversation-history/${sessionId}/${pillar}`, {
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
        conversation: data.conversation,
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






