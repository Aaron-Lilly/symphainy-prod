"use client";
import React from "react";
import { AGUIEventProvider } from "./AGUIEventProvider";
import { AuthProvider } from "./AuthProvider";
import { GuideAgentProvider } from "./GuideAgentProvider";
import { AppProvider } from "./AppProvider";
import { UserContextProviderComponent } from "../../lib/contexts/UserContextProvider";
import { ExperienceLayerProvider } from "../../lib/contexts/ExperienceLayerProvider";
// ServiceLayerProvider will be dynamically imported when needed
import {
  GlobalSessionProvider,
  useGlobalSession,
} from "./GlobalSessionProvider";

export default function AppProviders({
  children,
}: {
  children: React.ReactNode;
}) {
  // Debug: Log when AppProviders mounts
  console.log('[AppProviders] Component function called');
  if (typeof window !== 'undefined') {
    (window as any).__APP_PROVIDERS_MOUNTED__ = true;
    (window as any).__APP_PROVIDERS_MOUNT_TIME__ = Date.now();
  }
  
  return (
    <GlobalSessionProvider>
      <AuthProvider>
        <AppProvider>
          <UserContextProviderComponent>
            <ExperienceLayerProvider>
              <GuideAgentProvider>
                <AppProvidersInner>{children}</AppProvidersInner>
              </GuideAgentProvider>
            </ExperienceLayerProvider>
          </UserContextProviderComponent>
        </AppProvider>
      </AuthProvider>
    </GlobalSessionProvider>
  );
}

function AppProvidersInner({ children }: { children: React.ReactNode }) {
  const { guideSessionToken } = useGlobalSession();

  return (
    <AGUIEventProvider sessionToken={guideSessionToken}>
      {children}
    </AGUIEventProvider>
  );
}
