/**
 * useContentAPIManager Hook
 * 
 * React hook for ContentAPIManager that provides access to Content Realm API.
 * 
 * Usage:
 * ```tsx
 * const contentAPIManager = useContentAPIManager();
 * const result = await contentAPIManager.uploadFile(file);
 * ```
 */

import { useMemo } from "react";
import { ContentAPIManager } from "@/shared/managers/ContentAPIManager";
import { usePlatformState } from "@/shared/state/PlatformStateProvider";

let globalContentAPIManager: ContentAPIManager | null = null;

/**
 * Get or create global ContentAPIManager instance
 */
export function getGlobalContentAPIManager(): ContentAPIManager {
  if (!globalContentAPIManager) {
    globalContentAPIManager = new ContentAPIManager();
  }
  return globalContentAPIManager;
}

/**
 * React hook for ContentAPIManager
 * 
 * Provides ContentAPIManager instance with PlatformStateProvider integration.
 * 
 * @returns ContentAPIManager instance
 */
export function useContentAPIManager(): ContentAPIManager {
  const platformState = usePlatformState();

  const contentAPIManager = useMemo(() => {
    return new ContentAPIManager(
      undefined, // Use global Experience Plane Client
      () => platformState // Provide getPlatformState function
    );
  }, [platformState]);

  return contentAPIManager;
}
