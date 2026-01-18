/**
 * App Providers (New Architecture)
 * 
 * Unified provider composition using PlatformStateProvider.
 * Replaces the old AppProviders with consolidated state management.
 * 
 * Architecture:
 * - PlatformStateProvider (unified state)
 * - AuthProvider (authentication - will be updated in Phase 1.4)
 * - GuideAgentProvider (agent chat - uses UnifiedWebSocketClient)
 * - Other providers as needed
 */

"use client";

import React from "react";
import { PlatformStateProvider } from "./PlatformStateProvider";
import { AuthProvider } from "../auth/AuthProvider";
import { GuideAgentProvider } from "../agui/GuideAgentProvider";

export default function AppProviders({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <PlatformStateProvider>
      <AuthProvider>
        <GuideAgentProvider>
          {children}
        </GuideAgentProvider>
      </AuthProvider>
    </PlatformStateProvider>
  );
}
