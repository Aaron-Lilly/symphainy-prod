/**
 * ⚠️ PHASE 1: ProviderComposer is DEPRECATED
 * 
 * This component used old providers that have been archived.
 * Use `shared/state/AppProviders.tsx` instead, which uses the new architecture:
 * - SessionBoundaryProvider (session authority)
 * - AuthProvider (authentication)
 * - PlatformStateProvider (platform state)
 * - GuideAgentProvider (agent chat)
 * 
 * This file is kept for reference but should not be used in new code.
 */

"use client";

import React from "react";
// ✅ PHASE 1: All old providers archived - use AppProviders from shared/state/AppProviders.tsx instead
// import { SessionProvider, useSession } from "./SessionProvider";
// import { AppProvider } from "./AppProvider";
// import { WebSocketProvider } from "./WebSocketProvider";
// import { GlobalSessionProvider } from "./GlobalSessionProvider";
// import { AGUIEventProvider } from "./AGUIEventProvider";

/**
 * ⚠️ DEPRECATED: Use AppProviders from shared/state/AppProviders.tsx instead
 * 
 * This component is no longer functional as it depends on archived providers.
 * All new code should use the consolidated AppProviders.
 */
export const ProviderComposer: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  console.warn("⚠️ ProviderComposer is deprecated. Use AppProviders from '@/shared/state/AppProviders' instead.");
  // Return children directly - actual providers are in AppProviders
  return <>{children}</>;
};
