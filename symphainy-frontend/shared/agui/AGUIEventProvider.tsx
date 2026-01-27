"use client";
import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
} from "react";

// --- Types ---
export interface AGUIEvent {
  type: string;
  session_token: string;
  [key: string]: any;
}

export interface AGUIResponse {
  type: string;
  [key: string]: any;
}

interface AGUIEventContextType {
  sessionToken: string | null;
  setSessionToken: (token: string) => void;
  events: AGUIResponse[];
  sendEvent: (event: AGUIEvent) => Promise<AGUIResponse[]>;
  addEvent: (event: AGUIResponse) => void;
}

const AGUIEventContext = createContext<AGUIEventContextType | undefined>(
  undefined,
);

// --- Provider ---
export const AGUIEventProvider: React.FC<{
  children: React.ReactNode;
  sessionToken: string | null;
}> = ({ children, sessionToken }) => {
  const [events, setEvents] = useState<AGUIResponse[]>([]);

  // Add a new event to the state
  const addEvent = useCallback((event: AGUIResponse) => {
    setEvents((prev) => [...prev, event]);
  }, []);

  // ✅ PHASE 2: Use ServiceLayerAPI instead of direct fetch
  const sendEvent = useCallback(
    async (event: AGUIEvent): Promise<AGUIResponse[]> => {
      const { sendAgentEvent } = await import('@/shared/services/ServiceLayerAPI');
      const responses = await sendAgentEvent(event, {
        sessionId: sessionToken,
      });
      // Add responses to events state
      if (Array.isArray(responses) && responses.length > 0) {
        setEvents((prev) => [...prev, ...responses]);
      }
      return responses;
    },
    [sessionToken],
  );

  React.useEffect(() => {
    console.log("AGUIEventProvider sessionToken:", sessionToken);
  }, [sessionToken]);

  // Context value
  const value: AGUIEventContextType = {
    sessionToken,
    setSessionToken: () => {}, // No-op, sessionToken is now managed by GlobalSessionProvider
    events,
    sendEvent,
    addEvent,
  };

  return (
    <AGUIEventContext.Provider value={value}>
      {children}
    </AGUIEventContext.Provider>
  );
};

// --- Hook for easy access ---
export function useAGUIEvent() {
  const ctx = useContext(AGUIEventContext);
  if (!ctx)
    throw new Error("useAGUIEvent must be used within AGUIEventProvider");
  return ctx;
}
