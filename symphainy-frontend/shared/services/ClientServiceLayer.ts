/**
 * Client-Side Service Layer
 * 
 * A frontend-friendly service layer that only loads on the client side,
 * avoiding SSR issues while maintaining the sophisticated architecture.
 */

"use client";

import React, { useState, useEffect, useCallback } from 'react';

// ============================================
// Service Layer Types
// ============================================

export interface ServiceLayerConfig {
  sessionToken?: string;
  baseURL?: string;
  timeout?: number;
}

export interface ServiceLayerInstance {
  api: any;
  websocket: any;
  manager: any;
  isInitialized: boolean;
}

// ============================================
// Client Service Layer Hook
// ============================================

export function useClientServiceLayer(config?: ServiceLayerConfig) {
  const [serviceLayer, setServiceLayer] = useState<ServiceLayerInstance | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const initializeServiceLayer = useCallback(async () => {
    // Only run on client side
    if (typeof window === 'undefined') {
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      // Dynamically import the service layer components
      const [
        { APIService },
        { WebSocketService },
        { serviceLayerManager }
      ] = await Promise.all([
        import('./APIService'),
        import('./WebSocketService'),
        import('./index')
      ]);

      // Initialize the service layer
      const apiService = new APIService();
      const webSocketService = new WebSocketService();
      
      // Configure the service layer
      if (config?.sessionToken) {
        serviceLayerManager.initialize({ sessionToken: config.sessionToken });
      }

      setServiceLayer({
        api: apiService,
        websocket: webSocketService,
        manager: serviceLayerManager,
        isInitialized: true
      });

    } catch (err: any) {
      console.error('Failed to initialize service layer:', err);
      setError(err.message || 'Failed to initialize service layer');
    } finally {
      setIsLoading(false);
    }
  }, [config?.sessionToken]);

  // Initialize on mount
  useEffect(() => {
    initializeServiceLayer();
  }, [initializeServiceLayer]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (serviceLayer?.manager) {
        serviceLayer.manager.cleanup();
      }
    };
  }, [serviceLayer]);

  return {
    serviceLayer,
    isLoading,
    error,
    reinitialize: initializeServiceLayer
  };
}

// ============================================
// Service Layer Factory
// ============================================

export class ClientServiceLayerFactory {
  private static instance: ClientServiceLayerFactory | null = null;
  private serviceLayer: ServiceLayerInstance | null = null;

  static getInstance(): ClientServiceLayerFactory {
    if (!ClientServiceLayerFactory.instance) {
      ClientServiceLayerFactory.instance = new ClientServiceLayerFactory();
    }
    return ClientServiceLayerFactory.instance;
  }

  async createServiceLayer(config?: ServiceLayerConfig): Promise<ServiceLayerInstance> {
    if (this.serviceLayer && this.serviceLayer.isInitialized) {
      return this.serviceLayer;
    }

    // Only run on client side
    if (typeof window === 'undefined') {
      throw new Error('Service layer can only be created on the client side');
    }

    try {
      // Dynamically import the service layer components
      const [
        { APIService },
        { WebSocketService },
        { serviceLayerManager }
      ] = await Promise.all([
        import('./APIService'),
        import('./WebSocketService'),
        import('./index')
      ]);

      // Initialize the service layer
      const apiService = new APIService();
      const webSocketService = new WebSocketService();
      
      // Configure the service layer
      if (config?.sessionToken) {
        serviceLayerManager.initialize({ sessionToken: config.sessionToken });
      }

      this.serviceLayer = {
        api: apiService,
        websocket: webSocketService,
        manager: serviceLayerManager,
        isInitialized: true
      };

      return this.serviceLayer;

    } catch (error: any) {
      console.error('Failed to create service layer:', error);
      throw new Error(`Failed to create service layer: ${error.message}`);
    }
  }

  getServiceLayer(): ServiceLayerInstance | null {
    return this.serviceLayer;
  }

  cleanup() {
    if (this.serviceLayer?.manager) {
      this.serviceLayer.manager.cleanup();
    }
    this.serviceLayer = null;
  }
}

// ============================================
// Convenience Hook for Service Layer
// ============================================

export function useServiceLayerClient(config?: ServiceLayerConfig) {
  const { serviceLayer, isLoading, error, reinitialize } = useClientServiceLayer(config);

  const getService = useCallback((serviceName: 'api' | 'websocket' | 'manager') => {
    if (!serviceLayer) {
      throw new Error('Service layer not initialized');
    }
    return serviceLayer[serviceName];
  }, [serviceLayer]);

  return {
    api: serviceLayer?.api,
    websocket: serviceLayer?.websocket,
    manager: serviceLayer?.manager,
    isInitialized: serviceLayer?.isInitialized || false,
    isLoading,
    error,
    reinitialize,
    getService
  };
}
