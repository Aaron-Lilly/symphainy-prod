/**
 * useInsightsAPIManager Hook
 * 
 * React hook for InsightsAPIManager that provides access to Insights Realm API.
 * 
 * Usage:
 * ```tsx
 * const insightsAPIManager = useInsightsAPIManager();
 * const result = await insightsAPIManager.assessDataQuality(parsedFileId, sourceFileId, parserType);
 * ```
 */

import { useMemo } from "react";
import { InsightsAPIManager } from "@/shared/managers/InsightsAPIManager";
import { usePlatformState } from "@/shared/state/PlatformStateProvider";

let globalInsightsAPIManager: InsightsAPIManager | null = null;

/**
 * Get or create global InsightsAPIManager instance
 */
export function getGlobalInsightsAPIManager(): InsightsAPIManager {
  if (!globalInsightsAPIManager) {
    globalInsightsAPIManager = new InsightsAPIManager();
  }
  return globalInsightsAPIManager;
}

/**
 * React hook for InsightsAPIManager
 * 
 * Provides InsightsAPIManager instance with PlatformStateProvider integration.
 * 
 * @returns InsightsAPIManager instance
 */
export function useInsightsAPIManager(): InsightsAPIManager {
  const platformState = usePlatformState();

  const insightsAPIManager = useMemo(() => {
    return new InsightsAPIManager(
      undefined, // Use global Experience Plane Client
      () => platformState // Provide getPlatformState function
    );
  }, [platformState]);

  return insightsAPIManager;
}
