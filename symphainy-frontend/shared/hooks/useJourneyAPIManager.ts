/**
 * useJourneyAPIManager Hook
 * 
 * React hook for JourneyAPIManager that provides access to Journey Realm API.
 * 
 * Usage:
 * ```tsx
 * const journeyAPIManager = useJourneyAPIManager();
 * const result = await journeyAPIManager.optimizeProcess(workflowId);
 * ```
 */

import { useMemo } from "react";
import { JourneyAPIManager } from "@/shared/managers/JourneyAPIManager";
import { usePlatformState } from "@/shared/state/PlatformStateProvider";

let globalJourneyAPIManager: JourneyAPIManager | null = null;

/**
 * Get or create global JourneyAPIManager instance
 */
export function getGlobalJourneyAPIManager(): JourneyAPIManager {
  if (!globalJourneyAPIManager) {
    globalJourneyAPIManager = new JourneyAPIManager();
  }
  return globalJourneyAPIManager;
}

/**
 * React hook for JourneyAPIManager
 * 
 * Provides JourneyAPIManager instance with PlatformStateProvider integration.
 * 
 * @returns JourneyAPIManager instance
 */
export function useJourneyAPIManager(): JourneyAPIManager {
  const platformState = usePlatformState();

  const journeyAPIManager = useMemo(() => {
    return new JourneyAPIManager(
      undefined, // Use global Experience Plane Client
      () => platformState // Provide getPlatformState function
    );
  }, [platformState]);

  return journeyAPIManager;
}
