/**
 * Agent Manager Hook
 * 
 * Provides easy access to the new agent architecture with proper initialization
 * and cleanup. Manages WebSocket connections and agent routing.
 */

"use client";

import React, { useState, useEffect, useCallback } from 'react';
// All manager imports are now dynamic to avoid SSR issues

// ============================================
// Hook Interface
// ============================================

export interface UseAgentManagerReturn {
  // WebSocket and Agent Management
  webSocketManager: any | null;
  agentRouter: any | null;
  isConnected: boolean;
  isLoading: boolean;
  error: string | null;

  // API Managers
  contentAPI: any | null;
  operationsAPI: any | null;

  // Agent Methods
  sendToGuideAgent: (message: string, context?: any) => Promise<any>;
  sendToContentAgent: (message: string, context?: any) => Promise<any>;
  sendToInsightsAgent: (message: string, context?: any) => Promise<any>;
  sendToOperationsAgent: (message: string, context?: any) => Promise<any>;
  sendToExperienceAgent: (message: string, context?: any) => Promise<any>;

  // Utility Methods
  reconnect: () => Promise<void>;
  updateContext: (context: any) => void;
}

// ============================================
// Agent Manager Hook
// ============================================

export function useAgentManager(
  sessionToken: string,
  currentPillar?: string,
  fileContext?: any
): UseAgentManagerReturn {
  const [webSocketManager, setWebSocketManager] = useState<any | null>(null);
  const [agentRouter, setAgentRouter] = useState<any | null>(null);
  const [contentAPI, setContentAPI] = useState<any | null>(null);
  const [operationsAPI, setOperationsAPI] = useState<any | null>(null);
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
        { AgentRouter },
        { ContentAPIManager },
        { OperationsAPIManager }
      ] = await Promise.all([
        import('../managers/WebSocketManager'),
        import('../managers/AgentRouter'),
        import('../managers/ContentAPIManager'),
        import('../managers/OperationsAPIManager')
      ]);

      // Create WebSocket manager
      const wsManager = new WebSocketManager();
      await wsManager.connect(sessionToken);

      // Create agent router
      const router = new AgentRouter(wsManager, {
        sessionToken,
        currentPillar,
        fileContext
      });

      // Create API managers
      // Note: These managers now require ExperiencePlaneClient and getPlatformState
      // This hook should be refactored to use the hook pattern (useContentAPIManager, etc.)
      const contentAPIManager = new ContentAPIManager();
      const operationsAPIManager = new OperationsAPIManager();

      // Set up connection monitoring
      const unsubscribe = wsManager.onConnectionChange((connected) => {
        setIsConnected(connected);
      });

      setWebSocketManager(wsManager);
      setAgentRouter(router);
      setContentAPI(contentAPIManager);
      setOperationsAPI(operationsAPIManager);
      setIsConnected(wsManager.isConnected());

      // Store unsubscribe function for cleanup
      (wsManager as any)._unsubscribe = unsubscribe;

    } catch (err: any) {
      console.error('Failed to initialize agent managers:', err);
      setError(err.message || 'Failed to initialize agent managers');
    } finally {
      setIsLoading(false);
    }
  }, [sessionToken, currentPillar, fileContext]);

  const sendToGuideAgent = useCallback(async (message: string, context?: any) => {
    if (!agentRouter) {
      throw new Error('Agent router not initialized');
    }
    return agentRouter.routeMessage('guide', message, context);
  }, [agentRouter]);

  const sendToContentAgent = useCallback(async (message: string, context?: any) => {
    if (!agentRouter) {
      throw new Error('Agent router not initialized');
    }
    return agentRouter.routeMessage('content', message, context);
  }, [agentRouter]);

  const sendToInsightsAgent = useCallback(async (message: string, context?: any) => {
    if (!agentRouter) {
      throw new Error('Agent router not initialized');
    }
    return agentRouter.routeMessage('insights', message, context);
  }, [agentRouter]);

  const sendToOperationsAgent = useCallback(async (message: string, context?: any) => {
    if (!agentRouter) {
      throw new Error('Agent router not initialized');
    }
    return agentRouter.routeMessage('operations', message, context);
  }, [agentRouter]);

  const sendToExperienceAgent = useCallback(async (message: string, context?: any) => {
    if (!agentRouter) {
      throw new Error('Agent router not initialized');
    }
    return agentRouter.routeMessage('experience', message, context);
  }, [agentRouter]);

  const reconnect = useCallback(async () => {
    if (webSocketManager && sessionToken) {
      try {
        await webSocketManager.connect(sessionToken);
      } catch (err: any) {
        setError(err.message || 'Reconnection failed');
      }
    }
  }, [webSocketManager, sessionToken]);

  const updateContext = useCallback((newContext: any) => {
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
        if ((webSocketManager as any)._unsubscribe) {
          (webSocketManager as any)._unsubscribe();
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
