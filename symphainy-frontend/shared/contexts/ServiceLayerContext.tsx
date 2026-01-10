/**
 * Service Layer Context
 * 
 * A React Context-based service layer that only initializes on the client side,
 * providing a clean separation between server and client rendering.
 */

"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

// ============================================
// Service Layer Context Types
// ============================================

export interface ServiceLayerContextType {
  api: any;
  websocket: any;
  manager: any;
  isInitialized: boolean;
  isLoading: boolean;
  error: string | null;
  initialize: (config: { sessionToken: string }) => Promise<void>;
  cleanup: () => void;
}

// ============================================
// Service Layer Context
// ============================================

const ServiceLayerContext = createContext<ServiceLayerContextType | undefined>(undefined);

// ============================================
// Service Layer Provider
// ============================================

export const ServiceLayerProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [api, setApi] = useState<any>(null);
  const [websocket, setWebsocket] = useState<any>(null);
  const [manager, setManager] = useState<any>(null);
  const [isInitialized, setIsInitialized] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const initialize = async (config: { sessionToken: string }) => {
    // Only run on client side
    if (typeof window === 'undefined') {
      console.log('ServiceLayerContext: Skipping initialization on server side');
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      // Dynamically import service layer components
      const [
        { APIService },
        { WebSocketService },
        { serviceLayerManager }
      ] = await Promise.all([
        import('../services/APIService'),
        import('../services/WebSocketService'),
        import('../services/index')
      ]);

      // Create service instances
      const apiService = new APIService();
      const webSocketService = new WebSocketService();

      // Initialize the manager
      serviceLayerManager.initialize(config);

      // Set the services
      setApi(apiService);
      setWebsocket(webSocketService);
      setManager(serviceLayerManager);
      setIsInitialized(true);

    } catch (err: any) {
      console.error('Failed to initialize service layer:', err);
      setError(err.message || 'Failed to initialize service layer');
    } finally {
      setIsLoading(false);
    }
  };

  const cleanup = () => {
    if (manager) {
      manager.cleanup();
    }
    setApi(null);
    setWebsocket(null);
    setManager(null);
    setIsInitialized(false);
    setError(null);
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      cleanup();
    };
  }, []);

  const contextValue: ServiceLayerContextType = {
    api,
    websocket,
    manager,
    isInitialized,
    isLoading,
    error,
    initialize,
    cleanup
  };

  return (
    <ServiceLayerContext.Provider value={contextValue}>
      {children}
    </ServiceLayerContext.Provider>
  );
};

// ============================================
// Service Layer Hook
// ============================================

export const useServiceLayerContext = (): ServiceLayerContextType => {
  const context = useContext(ServiceLayerContext);
  if (context === undefined) {
    throw new Error('useServiceLayerContext must be used within a ServiceLayerProvider');
  }
  return context;
};
