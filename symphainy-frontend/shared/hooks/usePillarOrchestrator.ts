/**
 * Pillar Orchestrator Hook
 * 
 * Provides easy access to pillar orchestrators with proper initialization
 * and cleanup. Works with the beautiful service layer architecture.
 */

"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { PillarOrchestrator, PillarOrchestratorFactory } from '../orchestrators/PillarOrchestrator';

// ============================================
// Hook Interface
// ============================================

export interface UsePillarOrchestratorReturn {
  orchestrator: PillarOrchestrator | null;
  isInitialized: boolean;
  isLoading: boolean;
  error: string | null;
  executeOperation: (operation: string, data: any) => Promise<any>;
  getPillarData: () => Promise<any>;
  reinitialize: () => Promise<void>;
}

// ============================================
// Pillar Orchestrator Hook
// ============================================

export function usePillarOrchestrator(
  pillarName: string,
  sessionToken: string
): UsePillarOrchestratorReturn {
  const [orchestrator, setOrchestrator] = useState<PillarOrchestrator | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const initializeOrchestrator = useCallback(async () => {
    if (!sessionToken || !pillarName) {
      return;
    }

    // Only run on client side
    if (typeof window === 'undefined') {
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      // Create pillar orchestrator
      const pillarOrchestrator = PillarOrchestratorFactory.createOrchestrator(pillarName, sessionToken);
      
      // Initialize the orchestrator
      await pillarOrchestrator.initialize();

      setOrchestrator(pillarOrchestrator);
      setIsInitialized(true);

    } catch (err: any) {
      console.error(`Failed to initialize ${pillarName} orchestrator:`, err);
      setError(err.message || `Failed to initialize ${pillarName} orchestrator`);
    } finally {
      setIsLoading(false);
    }
  }, [pillarName, sessionToken]);

  const executeOperation = useCallback(async (operation: string, data: any) => {
    if (!orchestrator || !isInitialized) {
      throw new Error(`${pillarName} orchestrator not initialized`);
    }

    try {
      return await orchestrator.processPillarOperation(operation, data);
    } catch (err: any) {
      console.error(`Error executing ${pillarName} operation ${operation}:`, err);
      throw err;
    }
  }, [orchestrator, isInitialized, pillarName]);

  const getPillarData = useCallback(async () => {
    if (!orchestrator || !isInitialized) {
      throw new Error(`${pillarName} orchestrator not initialized`);
    }

    try {
      return await orchestrator.getPillarData();
    } catch (err: any) {
      console.error(`Error getting ${pillarName} data:`, err);
      throw err;
    }
  }, [orchestrator, isInitialized, pillarName]);

  const reinitialize = useCallback(async () => {
    if (orchestrator) {
      await orchestrator.cleanup();
    }
    setOrchestrator(null);
    setIsInitialized(false);
    await initializeOrchestrator();
  }, [orchestrator, initializeOrchestrator]);

  // Initialize on mount or when dependencies change
  useEffect(() => {
    initializeOrchestrator();
  }, [initializeOrchestrator]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (orchestrator) {
        orchestrator.cleanup().catch(console.error);
      }
    };
  }, [orchestrator]);

  return {
    orchestrator,
    isInitialized,
    isLoading,
    error,
    executeOperation,
    getPillarData,
    reinitialize
  };
}

// ============================================
// Convenience Hooks for Each Pillar
// ============================================

export function useContentOrchestrator(sessionToken: string) {
  return usePillarOrchestrator('content', sessionToken);
}

export function useInsightsOrchestrator(sessionToken: string) {
  return usePillarOrchestrator('insights', sessionToken);
}

export function useOperationsOrchestrator(sessionToken: string) {
  return usePillarOrchestrator('operations', sessionToken);
}

export function useExperienceOrchestrator(sessionToken: string) {
  return usePillarOrchestrator('experience', sessionToken);
}
