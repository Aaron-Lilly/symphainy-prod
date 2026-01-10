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

  // Send an AG-UI event to the backend (HTTP POST for now)
  const sendEvent = useCallback(
    async (event: AGUIEvent): Promise<AGUIResponse[]> => {
      // Use new /global/agent endpoint
      const resp = await fetch("/global/agent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_token: sessionToken,
          agent_type: event.agent_type || "GuideAgent", // Default to GuideAgent if not specified
          pillar: event.pillar || undefined,
          event,
        }),
      });
      if (!resp.ok) throw new Error(await resp.text());
      const data = await resp.json();
      // Assume data.result is the array of responses (adjust as needed)
      if (Array.isArray(data.result)) {
        setEvents((prev) => [...prev, ...data.result]);
        return data.result;
      }
      return [];
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
