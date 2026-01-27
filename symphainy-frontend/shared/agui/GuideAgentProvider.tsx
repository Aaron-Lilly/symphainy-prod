/**
 * Guide Agent Provider - Sophisticated Architecture
 * 
 * Provides the Guide Agent functionality using the new sophisticated architecture.
 * Integrates with GlobalSessionProvider, AuthProvider, and WebSocketService.
 */

"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useAuth } from '../auth/AuthProvider';
import { useSessionBoundary, SessionStatus } from '../state/SessionBoundaryProvider';
// ✅ PHASE 2.5: AGUI Native Integration - Guide Agent proposes AGUI mutations
import { useAGUIState } from '../state/AGUIStateProvider';
import { useServiceLayerAPI } from '../hooks/useServiceLayerAPI';
import { RuntimeClient, RuntimeEventType } from '@/shared/services/RuntimeClient';
import { getRuntimeWebSocketUrl, getApiUrl } from '@/shared/config/api-config';
import { AGUIMutation } from '@/shared/types/agui';

// ============================================================================
// GUIDE AGENT TYPES
// ============================================================================

export interface ConversationMessage {
  id: string;
  type: 'user' | 'agent' | 'system';
  content: string;
  timestamp: Date;
  metadata?: {
    intent?: string;
    pillar?: string;
    confidence?: number;
    suggested_actions?: string[];
    // ✅ PHASE 2.5: AGUI mutation info
    has_agui_mutation?: boolean;
    reasoning?: string;
  };
}

export interface GuidanceResponse {
  success: boolean;
  guidance?: {
    intent_analysis: {
      primary_intent: string;
      confidence: number;
      related_intents: string[];
    };
    recommended_actions: string[];
    suggested_data_types: string[];
    pillar_routing: string;
    next_steps: string[];
    conversation_context: any;
  };
  // ✅ PHASE 2.5: Agent proposes AGUI mutations (doesn't execute)
  agui_mutation?: AGUIMutation;
  reasoning?: string; // Why this mutation
  error?: string;
}

export interface GuideAgentState {
  isInitialized: boolean;
  isConnected: boolean;
  currentGuidance: GuidanceResponse | null;
  conversationHistory: ConversationMessage[];
  isLoading: boolean;
  error: string | null;
  conversationId: string | null; // Track conversation ID
}

export interface JourneyRequest {
  business_outcome: string;
  journey_type: string;
}

export interface JourneyResponse {
  success: boolean;
  journey_id?: string;
  business_outcome: string;
  journey_type: string;
  status: string;
  current_step: string;
  guide_agent_prompt: string;
  next_steps: string[];
  journey_metadata: {
    created_at: string;
    tenant_id: string;
    user_id: string;
  };
  error?: string;
}

export interface SolutionRequest {
  business_outcome: string;
  solution_intent: string;
}

export interface SolutionResponse {
  success: boolean;
  solution_id?: string;
  business_outcome: string;
  solution_intent: string;
  status: string;
  current_step: string;
  guide_agent_prompt: string;
  next_steps: string[];
  solution_metadata: {
    created_at: string;
    tenant_id: string;
    user_id: string;
  };
  error?: string;
}

export interface GuideAgentContextType {
  state: GuideAgentState;
  sendMessage: (message: string) => Promise<GuidanceResponse>;
  clearConversation: () => void;
  getGuidance: (intent: string) => Promise<GuidanceResponse>;
  createJourney: (request: JourneyRequest) => Promise<JourneyResponse>;
  createSolution: (request: SolutionRequest) => Promise<SolutionResponse>;
  initializeGuideAgent: () => Promise<void>;
  // ✅ PHASE 2.5: Submit intent from current AGUI state
  submitIntentFromCurrentAGUI: (intentType?: string) => Promise<void>;
}

// ============================================================================
// GUIDE AGENT CONTEXT
// ============================================================================

const GuideAgentContext = createContext<GuideAgentContextType | undefined>(undefined);

// ============================================================================
// GUIDE AGENT PROVIDER
// ============================================================================

export const GuideAgentProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  // ✅ PHASE 4: Session-First - Use SessionBoundary for session state (user still from AuthProvider for now)
  const { state: sessionState } = useSessionBoundary();
  const { user } = useAuth(); // Keep user from AuthProvider for now (may refactor later)
  const isAuthenticated = sessionState.status === SessionStatus.Active;
  // ✅ PHASE 2.5: AGUI Native Integration - Guide Agent proposes AGUI mutations
  const { state: aguiState, updateState: updateAGUIState } = useAGUIState();
  const { submitIntentFromAGUI } = useServiceLayerAPI();
  const sessionToken = sessionState.sessionId;
  const [runtimeClient, setRuntimeClient] = useState<RuntimeClient | null>(null);

  const [agentState, setAgentState] = useState<GuideAgentState>({
    isInitialized: false,
    isConnected: false,
    currentGuidance: null,
    conversationHistory: [],
    isLoading: false,
    error: null,
    conversationId: null,
  });

  // ✅ SESSION BOUNDARY PATTERN: Only initialize when session is Active
  const initializeGuideAgent = async () => {
    // Only connect when session is Active (authenticated and valid)
    if (sessionState.status !== SessionStatus.Active || !sessionToken) {
      // Disconnect if session becomes invalid
      if (runtimeClient) {
        runtimeClient.disconnect();
        setRuntimeClient(null);
        setAgentState(prev => ({
          ...prev,
          isConnected: false,
          isInitialized: false,
          error: sessionState.status === SessionStatus.Invalid 
            ? "Session invalid - reconnecting..." 
            : null,
        }));
      }
      return;
    }

    try {
      setAgentState(prev => ({ ...prev, isLoading: true, error: null }));

      // Create Runtime Client if not exists
      if (!runtimeClient) {
        const baseUrl = getApiUrl();
        // Get both access_token and session_id from storage
        const accessToken = typeof window !== 'undefined' ? sessionStorage.getItem("access_token") : null;
        const sessionId = sessionToken; // sessionToken is actually session_id from PlatformState
        
        if (!accessToken || !sessionId) {
          console.warn("Missing access_token or session_id, cannot create RuntimeClient");
          return;
        }
        
        const client = new RuntimeClient({
          baseUrl,
          accessToken: accessToken,
          sessionId: sessionId,
          autoReconnect: true,
        });
        setRuntimeClient(client);

        // ✅ PHASE 2.5: Subscribe to AGENT_RESPONSE events - Agent proposes AGUI mutations
        client.on(RuntimeEventType.AGENT_RESPONSE, async (data: any) => {
          console.log("Received Guide Agent response:", data);
          
          // ✅ PHASE 2.5: Extract AGUI mutation from agent response (if present)
          const aguiMutation: AGUIMutation | undefined = data.agui_mutation || data.aguiMutation;
          const reasoning: string | undefined = data.reasoning || data.explanation;
          
          // Convert backend response to GuidanceResponse format
          const guidanceResponse: GuidanceResponse = {
            success: true,
            guidance: {
              intent_analysis: data.intent || { primary_intent: 'general', confidence: 0.8, related_intents: [] },
              recommended_actions: [data.message || data.content],
              suggested_data_types: [],
              pillar_routing: data.intent?.target_domain || '',
              next_steps: [],
              conversation_context: data.guidance_response || {}
            },
            // ✅ PHASE 2.5: Include AGUI mutation in response
            agui_mutation: aguiMutation,
            reasoning: reasoning,
          };

          // ✅ PHASE 2.5: Apply AGUI mutation if present (agent proposes, frontend applies)
          if (aguiMutation) {
            try {
              console.log("✅ [GuideAgent] Applying AGUI mutation proposed by agent:", aguiMutation);
              updateAGUIState(aguiMutation);
              
              // ✅ PHASE 2.5: After applying mutation, compile and submit intent if needed
              // (This is optional - some mutations might not require immediate intent submission)
              // The component can decide when to submit based on the mutation type
              // Note: aguiState will be updated after mutation, so we need to wait for next render
              // For now, we'll let components handle intent submission explicitly
              // Auto-submit can be added later if needed via a callback pattern
            } catch (error) {
              console.error("❌ [GuideAgent] Failed to apply AGUI mutation:", error);
              // Continue with response even if mutation fails
            }
          }

          setAgentState(prev => ({
            ...prev,
            currentGuidance: guidanceResponse,
            isConnected: true,
            isLoading: false,
            error: null,
          }));

          // Add agent response to conversation history
          const agentMessage: ConversationMessage = {
            id: `agent-${Date.now()}`,
            type: 'agent',
            content: data.message || data.content || 'Response received',
            timestamp: new Date(),
            metadata: {
              intent: data.intent?.primary_intent,
              pillar: data.intent?.target_domain,
              confidence: data.intent?.confidence,
              suggested_actions: [data.message || data.content],
              // ✅ PHASE 2.5: Include AGUI mutation info in metadata
              has_agui_mutation: !!aguiMutation,
              reasoning: reasoning,
            }
          };

          setAgentState(prev => ({
            ...prev,
            conversationHistory: [...prev.conversationHistory, agentMessage]
          }));
        });

        // Subscribe to EXECUTION_FAILED events (errors)
        client.on(RuntimeEventType.EXECUTION_FAILED, (data: any) => {
          setAgentState(prev => ({
            ...prev,
            error: data.error || data.message || 'Error from Guide Agent',
            isLoading: false,
          }));
        });

        // Set up connection handler
        client.onConnect(() => {
          setAgentState(prev => ({
            ...prev,
            isInitialized: true,
            isConnected: true,
            isLoading: false,
            error: null,
          }));
        });

        // Set up error handler
        client.onError((err: Error) => {
          setAgentState(prev => ({
            ...prev,
            error: err.message || "Failed to initialize Guide Agent",
            isLoading: false,
            isConnected: false,
          }));
        });
      }

      // Connect
      await runtimeClient.connect();

    } catch (error: any) {
      console.error("Failed to initialize Guide Agent:", error);
      setAgentState(prev => ({
        ...prev,
        error: error.message || "Failed to initialize Guide Agent",
        isLoading: false,
        isConnected: false,
      }));
    }
  };

  // Send message to Guide Agent
  const sendMessage = async (message: string): Promise<GuidanceResponse> => {
    if (!runtimeClient || !sessionToken) {
      throw new Error("Guide Agent not initialized");
    }

    try {
      setAgentState(prev => ({ ...prev, isLoading: true, error: null }));

      // Add user message to conversation history
      const userMessage: ConversationMessage = {
        id: `user-${Date.now()}`,
        type: 'user',
        content: message,
        timestamp: new Date(),
      };

      setAgentState(prev => ({
        ...prev,
        conversationHistory: [...prev.conversationHistory, userMessage]
      }));

      if (!runtimeClient.isConnected()) {
        throw new Error("Guide Agent connection not connected");
      }

      // Generate conversation ID if not set
      const activeConversationId = agentState.conversationId || `guide_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      if (!agentState.conversationId) {
        setAgentState(prev => ({ ...prev, conversationId: activeConversationId }));
      }

      // Send intent to Runtime Foundation
      runtimeClient.submitIntent({
        intent: message,
        session_id: activeConversationId,
        agent_type: 'guide',
        metadata: {
          conversation_id: activeConversationId
        }
      });

      // Return a promise that resolves when we get the response
      return new Promise((resolve, reject) => {
        const timeout = setTimeout(() => {
          reject(new Error("Guide Agent response timeout"));
        }, 30000);

        // Listen for the response (this will be handled by the event handler above)
        const checkForResponse = () => {
          if (agentState.currentGuidance) {
            clearTimeout(timeout);
            resolve(agentState.currentGuidance);
          } else if (agentState.error) {
            clearTimeout(timeout);
            reject(new Error(agentState.error));
          } else {
            setTimeout(checkForResponse, 100);
          }
        };
        
        checkForResponse();
      });

    } catch (error: any) {
      setAgentState(prev => ({
        ...prev,
        error: error.message || "Failed to send message to Guide Agent",
        isLoading: false,
      }));
      throw error;
    }
  };

  // Get guidance for specific intent
  const getGuidance = async (intent: string): Promise<GuidanceResponse> => {
    return sendMessage(`I need guidance for: ${intent}`);
  };

  // Create solution (calls backend Solution Manager via Solution-Driven Architecture)
  const createSolution = async (request: SolutionRequest): Promise<SolutionResponse> => {
    try {
      setAgentState(prev => ({ ...prev, isLoading: true, error: null }));

      // Call Solution Manager API endpoint (Solution-Driven Architecture)
      const response = await fetch('/api/v1/solution/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(sessionToken && { 'Authorization': `Bearer ${sessionToken}` }),
        },
        body: JSON.stringify({
          solution_type: request.solution_intent || 'mvp',
          requirements: {
            business_outcome: request.business_outcome,
            user_id: user?.id || 'anonymous',
            tenant_id: user?.tenant_id || 'default',
          }
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Transform Solution Manager response to SolutionResponse format
      const solutionResponse: SolutionResponse = {
        success: data.success || false,
        solution_id: data.solution_id || data.result?.solution_id,
        business_outcome: request.business_outcome,
        solution_intent: request.solution_intent || 'mvp',
        status: data.design_status || data.status || 'created',
        current_step: data.current_step || 'initialization',
        guide_agent_prompt: data.guide_agent_prompt || 'Solution created successfully. Let\'s begin your journey!',
        next_steps: data.next_steps || data.journey?.next_steps || ['Begin solution implementation'],
        solution_metadata: {
          created_at: data.created_at || new Date().toISOString(),
          tenant_id: user?.tenant_id || 'default',
          user_id: user?.id || 'anonymous',
        },
        error: data.error,
      };
      
      if (solutionResponse.success) {
        setAgentState(prev => ({
          ...prev,
          isLoading: false,
          error: null,
        }));
      } else {
        setAgentState(prev => ({
          ...prev,
          error: solutionResponse.error || "Failed to create solution",
          isLoading: false,
        }));
      }

      return solutionResponse;

    } catch (error: any) {
      setAgentState(prev => ({
        ...prev,
        error: error.message || "Failed to create solution",
        isLoading: false,
      }));
      throw error;
    }
  };

  // Clear conversation history
  const clearConversation = () => {
    setAgentState(prev => ({
      ...prev,
      conversationHistory: [],
      currentGuidance: null,
      error: null,
    }));
  };

  // ✅ PHASE 2.5: Submit intent from current AGUI state (after agent proposes mutation)
  const submitIntentFromCurrentAGUI = async (intentType?: string) => {
    try {
      if (!aguiState) {
        throw new Error("AGUI state is not available");
      }
      // submitIntentFromAGUI from useServiceLayerAPI takes (state?: AGUIState, intentType?: string)
      // If state is undefined, it uses the current aguiState from the hook
      await submitIntentFromAGUI(aguiState, intentType);
    } catch (error) {
      console.error("❌ [GuideAgent] Failed to submit intent from AGUI:", error);
      throw error;
    }
  };

  // Initialize RuntimeClient
  useEffect(() => {
    // ✅ PHASE 4: Session-First - Use SessionStatus === Active
    if (typeof window !== 'undefined' && sessionState.status === SessionStatus.Active && sessionToken) {
      const baseUrl = getApiUrl();
      // Get both access_token and session_id from storage
      const accessToken = typeof window !== 'undefined' ? sessionStorage.getItem("access_token") : null;
      // ✅ SESSION BOUNDARY PATTERN: Only create client when session is Active
      if (sessionState.status !== SessionStatus.Active || !sessionToken) {
        return;
      }

      const sessionId = sessionToken;
      
      if (!accessToken || !sessionId) {
        console.warn("Missing access_token or session_id, cannot create RuntimeClient");
        return;
      }
      
      const client = new RuntimeClient({
        baseUrl,
        accessToken: accessToken,
        sessionId: sessionId,
        autoReconnect: true, // Still allow reconnect for network errors (not 403/401)
      });
      setRuntimeClient(client);

      // Cleanup on unmount
      return () => {
        client.disconnect();
      };
    }
  }, [sessionState.status, sessionToken]);

  // ✅ SESSION BOUNDARY PATTERN: Initialize when session is Active and WebSocket client is ready
  useEffect(() => {
    if (sessionState.status === SessionStatus.Active && sessionToken && runtimeClient && !agentState.isInitialized) {
      initializeGuideAgent();
    }
  }, [sessionState.status, sessionToken, runtimeClient, agentState.isInitialized]);

  const contextValue: GuideAgentContextType = {
    state: agentState,
    sendMessage,
    clearConversation,
    getGuidance,
    // ✅ PHASE 2.5: Submit intent from current AGUI state
    submitIntentFromCurrentAGUI,
    createJourney: async (request: JourneyRequest): Promise<JourneyResponse> => {
      // For now, return a mock response
      // TODO: Implement actual journey creation
      return {
        success: true,
        journey_id: `journey_${Date.now()}`,
        business_outcome: request.business_outcome,
        journey_type: request.journey_type,
        status: "created",
        current_step: "initialization",
        guide_agent_prompt: "Journey created successfully",
        next_steps: ["Begin journey implementation"],
        journey_metadata: {
          created_at: new Date().toISOString(),
          tenant_id: user?.tenant_id || "default",
          user_id: user?.id || "default"
        }
      };
    },
    createSolution,
    initializeGuideAgent,
  };

  return (
    <GuideAgentContext.Provider value={contextValue}>
      {children}
    </GuideAgentContext.Provider>
  );
};

// ============================================================================
// GUIDE AGENT HOOK
// ============================================================================

export const useGuideAgent = (): GuideAgentContextType => {
  const context = useContext(GuideAgentContext);
  if (context === undefined) {
    throw new Error('useGuideAgent must be used within a GuideAgentProvider');
  }
  return context;
};
