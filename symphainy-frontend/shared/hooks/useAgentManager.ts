/**
 * Agent Manager Hook
 * 
 * Provides easy access to the new agent architecture with proper initialization
 * and cleanup. Manages WebSocket connections and agent routing.
 */

"use client";

import { useState, useEffect, useCallback } from 'react';
import type { 
  IWebSocketManager, 
  AgentRouter, 
  AgentResponse, 
  AdditionalMessageContext,
  FileContext 
} from '../managers/AgentRouter';
import type { ContentAPIManager } from '../managers/ContentAPIManager';
import type { OperationsAPIManager } from '../managers/OperationsAPIManager';

// ============================================
// Hook Interface
// ============================================

/**
 * Context update payload for agent manager
 */
export interface AgentContextUpdate {
  currentPillar?: string;
  fileContext?: FileContext;
  sessionToken?: string;
}

export interface UseAgentManagerReturn {
  // WebSocket and Agent Management
  webSocketManager: IWebSocketManager | null;
  agentRouter: AgentRouter | null;
  isConnected: boolean;
  isLoading: boolean;
  error: string | null;

  // API Managers
  contentAPI: ContentAPIManager | null;
  operationsAPI: OperationsAPIManager | null;

  // Agent Methods
  sendToGuideAgent: (message: string, context?: AdditionalMessageContext) => Promise<AgentResponse>;
  sendToContentAgent: (message: string, context?: AdditionalMessageContext) => Promise<AgentResponse>;
  sendToInsightsAgent: (message: string, context?: AdditionalMessageContext) => Promise<AgentResponse>;
  sendToOperationsAgent: (message: string, context?: AdditionalMessageContext) => Promise<AgentResponse>;
  sendToExperienceAgent: (message: string, context?: AdditionalMessageContext) => Promise<AgentResponse>;

  // Utility Methods
  reconnect: () => Promise<void>;
  updateContext: (context: AgentContextUpdate) => void;
}

// ============================================
// Extended WebSocket Manager interface for cleanup
// ============================================

interface WebSocketManagerWithCleanup extends IWebSocketManager {
  _unsubscribe?: () => void;
}

// ============================================
// Agent Manager Hook
// ============================================

export function useAgentManager(
  sessionToken: string,
  currentPillar?: string,
  fileContext?: FileContext
): UseAgentManagerReturn {
  const [webSocketManager, setWebSocketManager] = useState<WebSocketManagerWithCleanup | null>(null);
  const [agentRouter, setAgentRouter] = useState<AgentRouter | null>(null);
  const [contentAPI, setContentAPI] = useState<ContentAPIManager | null>(null);
  const [operationsAPI, setOperationsAPI] = useState<OperationsAPIManager | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const initializeManagers = useCallback(async () => {
    if (!sessionToken) {
      return;
    }

    // Only run on client side
    if (typeof window === 'undefined') {
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      // Dynamically import managers to avoid SSR issues
      const [
        { WebSocketManager },
        { AgentRouter: AgentRouterClass },
        { ContentAPIManager: ContentAPIManagerClass },
        { OperationsAPIManager: OperationsAPIManagerClass }
      ] = await Promise.all([
        import('../managers/WebSocketManager'),
        import('../managers/AgentRouter'),
        import('../managers/ContentAPIManager'),
        import('../managers/OperationsAPIManager')
      ]);

      // Create WebSocket manager
      const wsManager = new WebSocketManager() as WebSocketManagerWithCleanup;
      await wsManager.connect(sessionToken);

      // Create agent router
      const router = new AgentRouterClass(wsManager, {
        sessionToken,
        currentPillar,
        fileContext
      });

      // Create API managers
      // Note: These managers now require ExperiencePlaneClient and getPlatformState
      // This hook should be refactored to use the hook pattern (useContentAPIManager, etc.)
      const contentAPIManager = new ContentAPIManagerClass();
      const operationsAPIManager = new OperationsAPIManagerClass();

      // Set up connection monitoring
      const unsubscribe = wsManager.onConnectionChange((connected: boolean) => {
        setIsConnected(connected);
      });

      setWebSocketManager(wsManager);
      setAgentRouter(router);
      setContentAPI(contentAPIManager);
      setOperationsAPI(operationsAPIManager);
      setIsConnected(wsManager.isConnected());

      // Store unsubscribe function for cleanup
      wsManager._unsubscribe = unsubscribe;

    } catch (err) {
      console.error('Failed to initialize agent managers:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to initialize agent managers';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [sessionToken, currentPillar, fileContext]);

  const sendToGuideAgent = useCallback(async (message: string, context?: AdditionalMessageContext): Promise<AgentResponse> => {
    if (!agentRouter) {
      throw new Error('Agent router not initialized');
    }
    return agentRouter.routeMessage('guide', message, context);
  }, [agentRouter]);

  const sendToContentAgent = useCallback(async (message: string, context?: AdditionalMessageContext): Promise<AgentResponse> => {
    if (!agentRouter) {
      throw new Error('Agent router not initialized');
    }
    return agentRouter.routeMessage('content', message, context);
  }, [agentRouter]);

  const sendToInsightsAgent = useCallback(async (message: string, context?: AdditionalMessageContext): Promise<AgentResponse> => {
    if (!agentRouter) {
      throw new Error('Agent router not initialized');
    }
    return agentRouter.routeMessage('insights', message, context);
  }, [agentRouter]);

  const sendToOperationsAgent = useCallback(async (message: string, context?: AdditionalMessageContext): Promise<AgentResponse> => {
    if (!agentRouter) {
      throw new Error('Agent router not initialized');
    }
    return agentRouter.routeMessage('operations', message, context);
  }, [agentRouter]);

  const sendToExperienceAgent = useCallback(async (message: string, context?: AdditionalMessageContext): Promise<AgentResponse> => {
    if (!agentRouter) {
      throw new Error('Agent router not initialized');
    }
    return agentRouter.routeMessage('experience', message, context);
  }, [agentRouter]);

  const reconnect = useCallback(async () => {
    if (webSocketManager && sessionToken) {
      try {
        await webSocketManager.connect(sessionToken);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Reconnection failed';
        setError(errorMessage);
      }
    }
  }, [webSocketManager, sessionToken]);

  const updateContext = useCallback((newContext: AgentContextUpdate) => {
    if (agentRouter) {
      agentRouter.updateContext(newContext);
    }
  }, [agentRouter]);

  // Initialize on mount or when dependencies change
  useEffect(() => {
    initializeManagers();
  }, [initializeManagers]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (webSocketManager) {
        // Clean up connection monitoring
        if (webSocketManager._unsubscribe) {
          webSocketManager._unsubscribe();
        }
        webSocketManager.disconnect();
      }
    };
  }, [webSocketManager]);

  return {
    webSocketManager,
    agentRouter,
    isConnected,
    isLoading,
    error,
    contentAPI,
    operationsAPI,
    sendToGuideAgent,
    sendToContentAgent,
    sendToInsightsAgent,
    sendToOperationsAgent,
    sendToExperienceAgent,
    reconnect,
    updateContext
  };
}
