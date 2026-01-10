"use client";

import React from "react";
import { SessionProvider, useSession } from "./SessionProvider";
import { AppProvider } from "./AppProvider";
import { WebSocketProvider } from "./WebSocketProvider";
import { GlobalSessionProvider } from "./GlobalSessionProvider";
import { AGUIEventProvider } from "./AGUIEventProvider";

/**
 * This helper component is necessary because the WebSocketProvider
 * needs access to the sessionToken provided by the SessionProvider.
 * By placing it as a child, we ensure useSession() is called within
 * the SessionProvider's context.
 */
const WebSocketEnabler: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const { sessionToken, isLoading } = useSession();

  // We only render the WebSocketProvider once we have a token.
  // We can also show a global loading state for the whole app here if desired.
  if (isLoading) {
    return null; // Or a global loading spinner
  }

  return <WebSocketProvider>{children}</WebSocketProvider>;
};

/**
 * ProviderComposer composes all the core application providers into a single,
 * clean component to be used in the root layout. This pattern ensures
 * providers are nested in the correct order and keeps the main layout file clean.
 */
export const ProviderComposer: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  return (
    <GlobalSessionProvider>
      <SessionProvider>
        <AppProvider>
          <WebSocketEnabler>{children}</WebSocketEnabler>
        </AppProvider>
      </SessionProvider>
    </GlobalSessionProvider>
  );
};
