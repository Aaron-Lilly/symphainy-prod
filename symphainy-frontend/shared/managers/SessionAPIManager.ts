/**
 * Session API Manager
 * 
 * ✅ PHASE 5.6.2: Migrated to intent-based API where possible
 * 
 * Centralizes all Session API calls.
 * 
 * Note: Session creation uses direct API call (no session exists yet),
 * but other operations use intent-based API for consistency.
 */

// ============================================
// Session API Manager Types
// ============================================

export interface CreateSessionRequest {
  user_id?: string;
  session_type?: string;
  context?: any;
}

export interface CreateSessionResponse {
  success: boolean;
  session_id?: string;
  session_token?: string;
  user_id?: string;
  created_at?: string;
  message?: string;
  error?: string;
}

export interface SessionDetailsResponse {
  success: boolean;
  session?: any;
  message?: string;
  error?: string;
}

export interface SessionStateResponse {
  success: boolean;
  session_state?: any;
  orchestrator_states?: any;
  message?: string;
  error?: string;
}

// ============================================
// Session API Manager Class
// ============================================

import { usePlatformState } from '@/shared/state/PlatformStateProvider';
import { validateSession } from '@/shared/utils/sessionValidation';
import { getApiEndpointUrl } from '@/shared/config/api-config';

export class SessionAPIManager {
  private getPlatformState: () => ReturnType<typeof usePlatformState>;

  constructor(getPlatformState?: () => ReturnType<typeof usePlatformState>) {
    this.getPlatformState = getPlatformState || (() => {
      throw new Error("PlatformStateProvider not available. Use SessionAPIManager with usePlatformState hook.");
    });
  }

  // ============================================
  // Session Creation (Direct API - No Session Yet)
  // ============================================

  /**
   * Create user session
   * 
   * ⚠️ NOTE: Uses direct API call because no session exists yet.
   * This is the only exception to intent-based architecture.
   * 
   * After session creation, all other operations use intent-based API.
   */
  async createUserSession(request: CreateSessionRequest = {}): Promise<CreateSessionResponse> {
    try {
      const url = getApiEndpointUrl('/api/v1/session/create-user-session');
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: request.user_id,
          session_type: request.session_type || 'mvp',
          context: request.context
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: 'Session creation failed' }));
        return {
          success: false,
          error: errorData.message || errorData.error || 'Session creation failed'
        };
      }

      const data = await response.json();
      
      return {
        success: data.success !== false,
        session_id: data.session_id,
        session_token: data.session_token,
        user_id: data.user_id,
        created_at: data.created_at,
        message: data.message,
        error: data.error
      };
    } catch (error) {
      console.error('[SessionAPIManager] Error creating session:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Session creation failed'
      };
    }
  }

  // ============================================
  // Session Operations (Intent-Based API)
  // ============================================

  /**
   * Get session details (get_session_details intent)
   * 
   * ✅ PHASE 5.6.2: Migrated to intent-based API
   * 
   * Flow: Experience Plane → Runtime → Session Realm
   */
  async getSessionDetails(sessionId: string): Promise<SessionDetailsResponse> {
    try {
      const platformState = this.getPlatformState();
      
      // ✅ FIX ISSUE 4: Use standardized session validation
      validateSession(platformState, "get session details");

      // ✅ FIX ISSUE 3: Parameter validation before submitIntent
      if (!sessionId) {
        throw new Error("session_id is required for get_session_details");
      }

      // Submit intent via Experience Plane Client
      const execution = await platformState.submitIntent(
        "get_session_details",
        {
          session_id: sessionId
        }
      );

      // Wait for execution completion
      const result = await this._waitForExecution(execution, platformState);

      if (result.status === "completed" && result.artifacts?.session_details) {
        return {
          success: true,
          session: result.artifacts.session_details
        };
      } else {
        throw new Error(result.error || "Failed to get session details");
      }
    } catch (error) {
      console.error('[SessionAPIManager] Error getting session details:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Get session state (get_session_state intent)
   * 
   * ✅ PHASE 5.6.2: Migrated to intent-based API
   * 
   * Flow: Experience Plane → Runtime → Session Realm
   */
  async getSessionState(sessionId: string): Promise<SessionStateResponse> {
    try {
      const platformState = this.getPlatformState();
      
      // ✅ FIX ISSUE 4: Use standardized session validation
      validateSession(platformState, "get session state");

      // ✅ FIX ISSUE 3: Parameter validation before submitIntent
      if (!sessionId) {
        throw new Error("session_id is required for get_session_state");
      }

      // Submit intent via Experience Plane Client
      const execution = await platformState.submitIntent(
        "get_session_state",
        {
          session_id: sessionId
        }
      );

      // Wait for execution completion
      const result = await this._waitForExecution(execution, platformState);

      if (result.status === "completed" && result.artifacts?.session_state) {
        return {
          success: true,
          session_state: result.artifacts.session_state.session_state,
          orchestrator_states: result.artifacts.session_state.orchestrator_states
        };
      } else {
        throw new Error(result.error || "Failed to get session state");
      }
    } catch (error) {
      console.error('[SessionAPIManager] Error getting session state:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Wait for execution completion
   * 
   * Polls execution status until completion or failure
   */
  private async _waitForExecution(
    executionId: string,
    platformState: ReturnType<typeof usePlatformState>,
    maxWaitTime: number = 60000, // 60 seconds
    pollInterval: number = 1000 // 1 second
  ): Promise<any> {
    const startTime = Date.now();
    
    while (Date.now() - startTime < maxWaitTime) {
      const status = await platformState.getExecutionStatus(executionId);
      
      if (!status) {
        throw new Error("Execution not found");
      }

      if (status.status === "completed" || status.status === "failed" || status.status === "cancelled") {
        return status;
      }

      // Wait before next poll
      await new Promise(resolve => setTimeout(resolve, pollInterval));
    }

    throw new Error("Execution timeout");
  }
}

// Factory function for use in components
export function useSessionAPIManager(): SessionAPIManager {
  const platformState = usePlatformState();
  
  return new SessionAPIManager(() => platformState);
}
