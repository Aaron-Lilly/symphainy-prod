/**
 * Unified Service Layer
 * 
 * Single authoritative service layer for the platform.
 * Combines best of SimpleServiceLayer and ClientServiceLayer.
 * 
 * Architecture:
 * - Client-side only (SSR-safe)
 * - React hook-based API
 * - Uses RuntimeClient for Runtime Foundation WebSocket
 * - Uses BaseAPIManager pattern for API calls
 * - Provides unified interface for all services
 */

"use client";

import { useState, useEffect, useCallback, useRef } from 'react';
import { RuntimeClient } from './RuntimeClient';
import { BaseAPIManager, UserContext } from '../managers/BaseAPIManager';

// ============================================
// Service Layer Types
// ============================================

export interface UnifiedServiceLayerConfig {
  sessionToken?: string;
  baseURL?: string;
  userContext?: UserContext;
  autoConnectWebSocket?: boolean;
}

export interface UnifiedServiceLayerInstance {
  api: BaseAPIManager;
  runtimeClient: RuntimeClient | null;
  isInitialized: boolean;
  sessionToken?: string;
  userContext?: UserContext;
}

// ============================================
// Unified Service Layer Hook
// ============================================

export function useUnifiedServiceLayer(
  config?: UnifiedServiceLayerConfig
): {
  serviceLayer: UnifiedServiceLayerInstance | null;
  isLoading: boolean;
  error: string | null;
  reinitialize: () => Promise<void>;
} {
  const [serviceLayer, setServiceLayer] = useState<UnifiedServiceLayerInstance | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const runtimeClientRef = useRef<RuntimeClient | null>(null);

  const initializeServiceLayer = useCallback(async () => {
    // Only run on client side
    if (typeof window === 'undefined') {
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      if (!config?.sessionToken) {
        setServiceLayer(null);
        setIsLoading(false);
        return;
      }

      // Create API manager (using BaseAPIManager pattern)
      // Note: In practice, you'd use specific managers (ContentAPIManager, etc.)
      // This is a placeholder - actual managers extend BaseAPIManager
      // Use ContentAPIManager as a concrete implementation
      const { ContentAPIManager } = await import('../managers/ContentAPIManager');
      const apiManager = new ContentAPIManager(
        config.sessionToken,
        config.baseURL,
        config.userContext
      );

      // Create Runtime Client if auto-connect is enabled
      let runtimeClient: RuntimeClient | null = null;
      if (config.autoConnectWebSocket !== false && config.baseURL) {
        runtimeClient = new RuntimeClient({
          baseUrl: config.baseURL,
          sessionToken: config.sessionToken,
          autoReconnect: true,
        });
        runtimeClientRef.current = runtimeClient;
        // Connect
        await runtimeClient.connect();
      }

      setServiceLayer({
        api: apiManager,
        runtimeClient,
        isInitialized: true,
        sessionToken: config.sessionToken,
        userContext: config.userContext,
      });
    } catch (err: any) {
      console.error('Failed to initialize unified service layer:', err);
      setError(err.message || 'Failed to initialize service layer');
    } finally {
      setIsLoading(false);
    }
  }, [config?.sessionToken, config?.baseURL, config?.userContext, config?.autoConnectWebSocket]);

  // Initialize on mount
  useEffect(() => {
    initializeServiceLayer();
  }, [initializeServiceLayer]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (runtimeClientRef.current) {
        runtimeClientRef.current.disconnect();
        runtimeClientRef.current = null;
      }
    };
  }, []);

  return {
    serviceLayer,
    isLoading,
    error,
    reinitialize: initializeServiceLayer,
  };
}

// ============================================
// Unified Service Layer Factory
// ============================================

export class UnifiedServiceLayerFactory {
  private static instance: UnifiedServiceLayerFactory | null = null;
  private serviceLayer: UnifiedServiceLayerInstance | null = null;

  static getInstance(): UnifiedServiceLayerFactory {
    if (!UnifiedServiceLayerFactory.instance) {
      UnifiedServiceLayerFactory.instance = new UnifiedServiceLayerFactory();
    }
    return UnifiedServiceLayerFactory.instance;
  }

  async createServiceLayer(
    config: UnifiedServiceLayerConfig
  ): Promise<UnifiedServiceLayerInstance> {
    if (this.serviceLayer && this.serviceLayer.isInitialized) {
      // Update if session token changed
      if (config.sessionToken && this.serviceLayer.sessionToken !== config.sessionToken) {
        this.serviceLayer.api.setSessionToken(config.sessionToken);
        this.serviceLayer.sessionToken = config.sessionToken;
      }
      // Update user context if provided
      if (config.userContext) {
        this.serviceLayer.api.setUserContext(config.userContext);
        this.serviceLayer.userContext = config.userContext;
      }
      return this.serviceLayer;
    }

    // Only run on client side
    if (typeof window === 'undefined') {
      throw new Error('Service layer can only be created on the client side');
    }

    if (!config.sessionToken) {
      throw new Error('Session token is required');
    }

    try {
      // Create API manager (using ContentAPIManager as concrete implementation)
      const { ContentAPIManager } = await import('../managers/ContentAPIManager');
      const apiManager = new ContentAPIManager(
        config.sessionToken,
        config.baseURL,
        config.userContext
      );

      // Create Runtime Client if auto-connect is enabled
      let runtimeClient: RuntimeClient | null = null;
      if (config.autoConnectWebSocket !== false && config.baseURL) {
        runtimeClient = new RuntimeClient({
          baseUrl: config.baseURL,
          sessionToken: config.sessionToken,
          autoReconnect: true,
        });
        // Connect
        await runtimeClient.connect();
      }

      this.serviceLayer = {
        api: apiManager,
        runtimeClient,
        isInitialized: true,
        sessionToken: config.sessionToken,
        userContext: config.userContext,
      };

      return this.serviceLayer;
    } catch (error: any) {
      console.error('Failed to create unified service layer:', error);
      throw new Error(`Failed to create service layer: ${error.message}`);
    }
  }

  getServiceLayer(): UnifiedServiceLayerInstance | null {
    return this.serviceLayer;
  }

  cleanup() {
    if (this.serviceLayer?.runtimeClient) {
      this.serviceLayer.runtimeClient.disconnect();
    }
    this.serviceLayer = null;
  }
}

// ============================================
// Convenience Exports
// ============================================

export const unifiedServiceLayerFactory = UnifiedServiceLayerFactory.getInstance();



