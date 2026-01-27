"use client";
import React, { createContext, useContext, useState, useEffect } from "react";
import { startGlobalSession } from "@/lib/api/global";

interface SessionContextType {
  sessionToken: string | null;
  isLoading: boolean;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

export const SessionProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [sessionToken, setSessionToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    const initializeSession = async () => {
      setIsLoading(true);
      const storedToken = localStorage.getItem("sessionToken");

      if (storedToken) {
        if (isMounted) {
          setSessionToken(storedToken);
        }
      } else {
        try {
          const res = await startGlobalSession();
          if (isMounted) {
            setSessionToken(res.session_token);
            localStorage.setItem("sessionToken", res.session_token);
          }
        } catch (err) {
          console.error(
            "[SessionProvider] Failed to start global session:",
            err,
          );
        }
      }
      if (isMounted) {
        setIsLoading(false);
      }
    };

    initializeSession();

    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    if (sessionToken) {
      localStorage.setItem("sessionToken", sessionToken);
    }
  }, [sessionToken]);

  const value = React.useMemo(
    () => ({
      sessionToken,
      isLoading,
    }),
    [sessionToken, isLoading],
  );

  return (
    <SessionContext.Provider value={value}>{children}</SessionContext.Provider>
  );
};

export function useSession() {
  const context = useContext(SessionContext);
  if (context === undefined) {
    throw new Error("useSession must be used within a SessionProvider");
  }
  return context;
}
