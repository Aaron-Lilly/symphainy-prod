/**
 * useOutcomesAPIManager Hook
 * 
 * React hook for OutcomesAPIManager that provides access to Outcomes Realm API.
 * 
 * Usage:
 * ```tsx
 * const outcomesAPIManager = useOutcomesAPIManager();
 * const result = await outcomesAPIManager.generateRoadmap(goals);
 * ```
 */

import { useMemo } from "react";
import { OutcomesAPIManager } from "@/shared/managers/OutcomesAPIManager";
import { usePlatformState } from "@/shared/state/PlatformStateProvider";

let globalOutcomesAPIManager: OutcomesAPIManager | null = null;

/**
 * Get or create global OutcomesAPIManager instance
 */
export function getGlobalOutcomesAPIManager(): OutcomesAPIManager {
  if (!globalOutcomesAPIManager) {
    globalOutcomesAPIManager = new OutcomesAPIManager();
  }
  return globalOutcomesAPIManager;
}

/**
 * React hook for OutcomesAPIManager
 * 
 * Provides OutcomesAPIManager instance with PlatformStateProvider integration.
 * 
 * @returns OutcomesAPIManager instance
 */
export function useOutcomesAPIManager(): OutcomesAPIManager {
  const platformState = usePlatformState();

  const outcomesAPIManager = useMemo(() => {
    return new OutcomesAPIManager(
      undefined, // Use global Experience Plane Client
      () => platformState // Provide getPlatformState function
    );
  }, [platformState]);

  return outcomesAPIManager;
}
