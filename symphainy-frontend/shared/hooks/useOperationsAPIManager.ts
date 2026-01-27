/**
 * useOperationsAPIManager Hook
 * 
 * React hook for OperationsAPIManager that provides access to Operations Realm API.
 * 
 * NAMING NOTE:
 * - Backend: "Operations Realm" (handles SOPs, workflows, process optimization)
 * - Frontend API Manager: "OperationsAPIManager"
 * - This replaces the previous "JourneyAPIManager" to align with backend naming
 * 
 * Usage:
 * ```tsx
 * const operationsAPIManager = useOperationsAPIManager();
 * const result = await operationsAPIManager.optimizeProcess(workflowId);
 * ```
 */

import { useMemo } from "react";
import { OperationsAPIManager } from "@/shared/managers/OperationsAPIManager";
import { usePlatformState } from "@/shared/state/PlatformStateProvider";

let globalOperationsAPIManager: OperationsAPIManager | null = null;

/**
 * Get or create global OperationsAPIManager instance
 */
export function getGlobalOperationsAPIManager(): OperationsAPIManager {
  if (!globalOperationsAPIManager) {
    globalOperationsAPIManager = new OperationsAPIManager();
  }
  return globalOperationsAPIManager;
}

/**
 * React hook for OperationsAPIManager
 * 
 * Provides OperationsAPIManager instance with PlatformStateProvider integration.
 * 
 * @returns OperationsAPIManager instance
 */
export function useOperationsAPIManager(): OperationsAPIManager {
  const platformState = usePlatformState();

  const operationsAPIManager = useMemo(() => {
    return new OperationsAPIManager(
      undefined, // Use global Experience Plane Client
      () => platformState // Provide getPlatformState function
    );
  }, [platformState]);

  return operationsAPIManager;
}

// Backwards compatibility aliases (deprecated - use useOperationsAPIManager)
/** @deprecated Use useOperationsAPIManager instead */
export const useJourneyAPIManager = useOperationsAPIManager;
/** @deprecated Use getGlobalOperationsAPIManager instead */
export const getGlobalJourneyAPIManager = getGlobalOperationsAPIManager;
