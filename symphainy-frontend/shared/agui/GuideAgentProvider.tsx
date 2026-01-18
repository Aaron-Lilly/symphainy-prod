/**
 * Guide Agent Provider - Sophisticated Architecture
 * 
 * Provides the Guide Agent functionality using the new sophisticated architecture.
 * Integrates with GlobalSessionProvider, AuthProvider, and WebSocketService.
 */

"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useAuth } from '../auth/AuthProvider';
import { usePlatformState } from '../state/PlatformStateProvider';
import { RuntimeClient, RuntimeEventType } from '@/shared/services/RuntimeClient';
import { getRuntimeWebSocketUrl, getApiUrl } from '@/shared/config/api-config';

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
}

// ============================================================================
// GUIDE AGENT CONTEXT
// ============================================================================

const GuideAgentContext = createContext<GuideAgentContextType | undefined>(undefined);

// ============================================================================
// GUIDE AGENT PROVIDER
// ============================================================================

export const GuideAgentProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { isAuthenticated, user } = useAuth();
  const { state: platformState } = usePlatformState();
  const sessionToken = platformState.session.sessionId;
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

  // Initialize Guide Agent
  const initializeGuideAgent = async () => {
    if (!isAuthenticated || !sessionToken) {
      return;
    }

    try {
      setAgentState(prev => ({ ...prev, isLoading: true, error: null }));

      // Create Runtime Client if not exists
      if (!runtimeClient) {
        const baseUrl = getApiUrl();
        const client = new RuntimeClient({
          baseUrl,
          sessionToken: sessionToken,
          autoReconnect: true,
        });
        setRuntimeClient(client);

        // Subscribe to AGENT_RESPONSE events
        client.on(RuntimeEventType.AGENT_RESPONSE, (data: any) => {
          console.log("Received Guide Agent response:", data);
          
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
            }
          };

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

  // Initialize RuntimeClient
  useEffect(() => {
    if (typeof window !== 'undefined' && isAuthenticated && sessionToken) {
      const baseUrl = getApiUrl();
      const client = new RuntimeClient({
        baseUrl,
        sessionToken: sessionToken,
        autoReconnect: true,
      });
      setRuntimeClient(client);

      // Cleanup on unmount
      return () => {
        client.disconnect();
      };
    }
  }, [isAuthenticated, sessionToken]);

  // Initialize when authenticated and WebSocket client is ready
  useEffect(() => {
    if (isAuthenticated && sessionToken && runtimeClient && !agentState.isInitialized) {
      initializeGuideAgent();
    }
  }, [isAuthenticated, sessionToken, runtimeClient, agentState.isInitialized]);

  const contextValue: GuideAgentContextType = {
    state: agentState,
    sendMessage,
    clearConversation,
    getGuidance,
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
