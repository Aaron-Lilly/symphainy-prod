/**
 * App Providers (New Architecture)
 * 
 * Unified provider composition using SessionBoundaryProvider and PlatformStateProvider.
 * 
 * Architecture:
 * - SessionBoundaryProvider (session lifecycle - single authority)
 * - AuthProvider (authentication - uses SessionBoundaryProvider)
 * - PlatformStateProvider (execution, realm, UI state - subscribes to SessionBoundaryProvider)
 * - GuideAgentProvider (agent chat - uses UnifiedWebSocketClient)
 * - Other providers as needed
 * 
 * Provider Hierarchy:
 * SessionBoundaryProvider (session authority)
 *   └─ AuthProvider (authentication - upgrades session)
 *       └─ PlatformStateProvider (other state - subscribes to session)
 *           └─ Other providers...
 */

"use client";

import React from "react";
import { SessionBoundaryProvider } from "./SessionBoundaryProvider";
import { AGUIStateProvider } from "./AGUIStateProvider";
import { PlatformStateProvider } from "./PlatformStateProvider";
import { AuthProvider } from "../auth/AuthProvider";
import { AppProvider } from "../agui/AppProvider";
import { GuideAgentProvider } from "../agui/GuideAgentProvider";
import { ExperienceLayerProvider } from "../../lib/contexts/ExperienceLayerProvider";
import { UserContextProviderComponent } from "../../lib/contexts/UserContextProvider";

export default function AppProviders({
  children,
}: {
  children: React.ReactNode;
}) {
  // ✅ SESSION BOUNDARY PATTERN: SessionBoundaryProvider is the root
  // - Only component that calls /api/session/* endpoints
  // - Manages session lifecycle state machine
  // - All other providers subscribe to session state
  // ✅ PHASE 2.5: AGUI State Provider - session-scoped experience state
  return (
    <SessionBoundaryProvider>
      <AGUIStateProvider>
        <AuthProvider>
          <PlatformStateProvider>
            <AppProvider>
              <UserContextProviderComponent>
                <ExperienceLayerProvider>
                  <GuideAgentProvider>
                    {children}
                  </GuideAgentProvider>
                </ExperienceLayerProvider>
              </UserContextProviderComponent>
            </AppProvider>
          </PlatformStateProvider>
        </AuthProvider>
      </AGUIStateProvider>
    </SessionBoundaryProvider>
  );
}
