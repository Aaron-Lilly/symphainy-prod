/**
 * useUnifiedAgentChat Hook
 * 
 * Unified React hook for all agent communications (Guide + Liaison).
 * Uses single WebSocket connection with message routing.
 * 
 * Phase 5: Unified WebSocket Architecture
 * 
 * Features:
 * - Single WebSocket connection per user
 * - Message routing based on agent_type and pillar
 * - Conversation context management
 * - Agent switching without reconnection
 * - AGUI component support
 */

import { useState, useEffect, useCallback, useRef } from 'react';
// ✅ PHASE 3: WebSocket Consolidation - Check SessionStatus before connecting
import { useSessionBoundary, SessionStatus } from '@/shared/state/SessionBoundaryProvider';
import { RuntimeClient, RuntimeEventType } from '@/shared/services/RuntimeClient';
import { getRuntimeWebSocketUrl, getApiUrl } from '@/shared/config/api-config';

export type AgentType = 'guide' | 'liaison';
export type PillarType = 'content' | 'insights' | 'operations' | 'business_outcomes';

export interface UnifiedChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  agent_type: AgentType;
  pillar?: PillarType;
  conversation_id?: string;
  metadata?: {
    data?: any; // AGUI components, analysis results, etc.
    visualization?: any; // Visualization components
    intent?: any;
    [key: string]: any;
  };
}

export interface UseUnifiedAgentChatReturn {
  // State
  messages: UnifiedChatMessage[];
  isConnected: boolean;
  isLoading: boolean;
  error: string | null;
  currentAgent: AgentType | null;
  currentPillar: PillarType | null;
  conversationId: string | null;
  
  // Actions
  sendMessage: (message: string, agentType?: AgentType, pillar?: PillarType) => Promise<void>;
  switchAgent: (agentType: AgentType, pillar?: PillarType) => void;
  clearMessages: (conversationId?: string) => void;
  connect: () => Promise<void>;
  disconnect: () => void;
  
  // Conversation management
  getConversationMessages: (conversationId: string) => UnifiedChatMessage[];
  setConversationId: (conversationId: string) => void;
}

export interface UseUnifiedAgentChatOptions {
  sessionToken?: string;
  autoConnect?: boolean;
  initialAgent?: AgentType;
  initialPillar?: PillarType;
  onMessage?: (message: UnifiedChatMessage) => void;
  onError?: (error: string) => void;
  onAgentSwitch?: (agentType: AgentType, pillar?: PillarType) => void;
}

export function useUnifiedAgentChat(
  options: UseUnifiedAgentChatOptions = {}
): UseUnifiedAgentChatReturn {
  const {
    sessionToken,
    autoConnect = true,
    initialAgent = 'guide',
    initialPillar,
    onMessage,
    onError,
    onAgentSwitch
  } = options;

  const [messages, setMessages] = useState<UnifiedChatMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentAgent, setCurrentAgent] = useState<AgentType | null>(initialAgent);
  const [currentPillar, setCurrentPillar] = useState<PillarType | null>(initialPillar || null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  
  // ✅ PHASE 3: Get session state from SessionBoundaryProvider
  const { state: sessionState } = useSessionBoundary();
  const effectiveSessionToken = sessionToken || sessionState.sessionId;
  
  const runtimeClientRef = useRef<RuntimeClient | null>(null);

  // Generate conversation ID
  const generateConversationId = useCallback((agentType: AgentType, pillar?: PillarType): string => {
    const pillarPart = pillar ? `_${pillar}` : '';
    return `${agentType}${pillarPart}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }, []);

  // ✅ PHASE 3: WebSocket Consolidation - Only connect when SessionStatus === Active
  useEffect(() => {
    // Disconnect when session becomes Invalid
    if (sessionState.status === SessionStatus.Invalid && runtimeClientRef.current) {
      console.log("🔄 [useUnifiedAgentChat] Session invalid, disconnecting WebSocket");
      runtimeClientRef.current.disconnect();
      runtimeClientRef.current = null;
      setIsConnected(false);
      setError(null);
    }
  }, [sessionState.status]);

  // Connect to unified WebSocket
  const connect = useCallback(async () => {
    // ✅ PHASE 3: WebSocket Consolidation - Only connect when SessionStatus === Active
    if (!sessionState || sessionState.status !== SessionStatus.Active) {
      setError(`Cannot connect: Session status is ${sessionState?.status || 'unknown'}`);
      return;
    }

    // ✅ Safety check: Don't connect if sessionToken is missing, empty, or invalid
    const tokenToUse = effectiveSessionToken;
    if (!tokenToUse || typeof tokenToUse !== 'string' || tokenToUse.trim() === '' || tokenToUse === 'token_placeholder') {
      setError("Session token required");
      return;
    }

    // Check if already connected
    if (runtimeClientRef.current?.isConnected()) {
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      // Create or reuse RuntimeClient
      if (!runtimeClientRef.current) {
        const baseUrl = getApiUrl();
        // Get both access_token and session_id from storage
        const accessToken = typeof window !== 'undefined' ? sessionStorage.getItem("access_token") : null;
        const sessionId = tokenToUse; // tokenToUse is actually session_id
        
        if (!accessToken || !sessionId) {
          console.warn("Missing access_token or session_id, cannot create RuntimeClient");
          return;
        }
        
        runtimeClientRef.current = new RuntimeClient({
          baseUrl,
          accessToken: accessToken,
          sessionId: sessionId,
          autoReconnect: autoConnect,
        });

        // Subscribe to AGENT_RESPONSE events (chat responses)
        runtimeClientRef.current.on(RuntimeEventType.AGENT_RESPONSE, (data: any) => {
          const assistantMessage: UnifiedChatMessage = {
            id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            role: 'assistant',
            content: data.message || data.content || 'Response received',
            timestamp: new Date(),
            agent_type: data.agent_type || currentAgent || 'guide',
            pillar: data.pillar || currentPillar || undefined,
            conversation_id: data.conversation_id || conversationId || undefined,
            metadata: {
              data: data.data,
              ...data
            }
          };

          setMessages(prev => [...prev, assistantMessage]);
          
          // Update conversation ID if provided
          if (data.conversation_id && data.conversation_id !== conversationId) {
            setConversationId(data.conversation_id);
          }
          
          if (onMessage) {
            onMessage(assistantMessage);
          }
        });

        // Subscribe to EXECUTION_FAILED events (errors)
        runtimeClientRef.current.on(RuntimeEventType.EXECUTION_FAILED, (data: any) => {
          const errorMsg = data.error || data.message || 'Error from agent';
          setError(errorMsg);
          if (onError) {
            onError(errorMsg);
          }
        });

        // Set up error handler
        runtimeClientRef.current.onError((err: Error) => {
          setError(err.message);
          setIsConnected(false);
          setIsLoading(false);
          if (onError) {
            onError(err.message);
          }
        });

        // Set up connection handler
        runtimeClientRef.current.onConnect(() => {
          console.log('✅ Unified Agent Runtime Client connected');
          setIsConnected(true);
          setIsLoading(false);
          
          // Generate initial conversation ID if not set
          if (!conversationId && currentAgent) {
            const newConversationId = generateConversationId(currentAgent, currentPillar || undefined);
            setConversationId(newConversationId);
          }
        });

        // Set up disconnection handler
        runtimeClientRef.current.onDisconnect(() => {
          setIsConnected(false);
          setIsLoading(false);
        });
      }

      // Connect
      await runtimeClientRef.current.connect();
    } catch (err: any) {
      setError(err.message || 'Failed to connect to Unified Agent WebSocket');
      setIsLoading(false);
      setIsConnected(false);
      if (onError) {
        onError(err.message || 'Failed to connect to Unified Agent WebSocket');
      }
    }
  }, [sessionState.status, effectiveSessionToken, conversationId, currentAgent, currentPillar, onMessage, onError, generateConversationId, autoConnect]);

  // Disconnect from Runtime Client
  const disconnect = useCallback(() => {
    if (runtimeClientRef.current) {
      runtimeClientRef.current.disconnect();
      runtimeClientRef.current = null;
    }
    
    setIsConnected(false);
  }, []);

  // Send message to agent
  const sendMessage = useCallback(async (
    message: string,
    agentType: AgentType = currentAgent || 'guide',
    pillar?: PillarType
  ) => {
    if (!runtimeClientRef.current || !runtimeClientRef.current.isConnected()) {
      throw new Error("Not connected to Runtime Client");
    }

    if (!message.trim()) {
      return;
    }

    try {
      // Update current agent/pillar if different
      if (agentType !== currentAgent || (pillar && pillar !== currentPillar)) {
        setCurrentAgent(agentType);
        if (pillar) {
          setCurrentPillar(pillar);
        }
        
        // Generate new conversation ID for new agent/pillar
        const newConversationId = generateConversationId(agentType, pillar);
        setConversationId(newConversationId);
        
        if (onAgentSwitch) {
          onAgentSwitch(agentType, pillar);
        }
      }

      // Use current conversation ID or generate one
      const activeConversationId = conversationId || generateConversationId(agentType, pillar || currentPillar || undefined);
      if (!conversationId) {
        setConversationId(activeConversationId);
      }

      // Add user message to local state immediately
      const userMessage: UnifiedChatMessage = {
        id: `user-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        role: 'user',
        content: message,
        timestamp: new Date(),
        agent_type: agentType,
        pillar: pillar || currentPillar || undefined,
        conversation_id: activeConversationId
      };

      setMessages(prev => [...prev, userMessage]);

      // Send intent to Runtime Foundation
      runtimeClientRef.current.submitIntent({
        intent: message,
        session_id: activeConversationId,
        agent_type: agentType === 'guide' ? 'guide' : 'liaison',
        metadata: {
          pillar: pillar || currentPillar || undefined,
          conversation_id: activeConversationId
        }
      });
    } catch (err: any) {
      setError(err.message || 'Failed to send message');
      throw err;
    }
  }, [currentAgent, currentPillar, conversationId, generateConversationId, onAgentSwitch]);

  // Switch agent without reconnecting
  const switchAgent = useCallback((agentType: AgentType, pillar?: PillarType) => {
    setCurrentAgent(agentType);
    if (pillar) {
      setCurrentPillar(pillar);
    } else if (agentType === 'guide') {
      // Guide agent doesn't have a pillar
      setCurrentPillar(null);
    }

    // Generate new conversation ID for new agent/pillar
    const newConversationId = generateConversationId(agentType, pillar);
    setConversationId(newConversationId);

    if (onAgentSwitch) {
      onAgentSwitch(agentType, pillar);
    }
  }, [generateConversationId, onAgentSwitch]);

  // Clear messages (optionally for specific conversation)
  const clearMessages = useCallback((targetConversationId?: string) => {
    if (targetConversationId) {
      setMessages(prev => prev.filter(msg => msg.conversation_id !== targetConversationId));
    } else {
      setMessages([]);
    }
  }, []);

  // Get messages for specific conversation
  const getConversationMessages = useCallback((targetConversationId: string): UnifiedChatMessage[] => {
    return messages.filter(msg => msg.conversation_id === targetConversationId);
  }, [messages]);

  // Auto-connect on mount if enabled
  useEffect(() => {
    // ✅ CRITICAL: Only connect if autoConnect is explicitly true
    if (!autoConnect) {
      if (runtimeClientRef.current) {
        disconnect();
      }
      return;
    }
    
    // ✅ Safety check: Only connect if sessionToken is valid
    const isValidToken = sessionToken && 
      typeof sessionToken === 'string' && 
      sessionToken.trim() !== '' && 
      sessionToken !== 'token_placeholder' &&
      sessionToken.length > 10;
    
    if (isValidToken) {
      // Add small delay to ensure token is fully validated and ready
      const connectTimer = setTimeout(() => {
        connect();
      }, 150);
      
      return () => {
        clearTimeout(connectTimer);
        disconnect();
      };
    } else {
      if (runtimeClientRef.current) {
        disconnect();
      }
    }

    return () => {
      disconnect();
    };
  }, [autoConnect, sessionState.status, effectiveSessionToken, connect, disconnect]);

  return {
    // State
    messages,
    isConnected,
    isLoading,
    error,
    currentAgent,
    currentPillar,
    conversationId,
    
    // Actions
    sendMessage,
    switchAgent,
    clearMessages,
    connect,
    disconnect,
    
    // Conversation management
    getConversationMessages,
    setConversationId
  };
}

