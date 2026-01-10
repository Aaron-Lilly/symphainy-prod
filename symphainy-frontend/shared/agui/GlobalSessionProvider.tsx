"use client";
import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
} from "react";
import { SessionAPIManager } from "@/shared/managers/SessionAPIManager";
import { config } from "@/lib/config";

interface GlobalSessionContextType {
  guideSessionToken: string | null;
  setGuideSessionToken: (token: string) => Promise<void>;
  getPillarState: (pillar: string) => any;
  setPillarState: (pillar: string, state: any) => Promise<void>;
  resetAllState: () => Promise<void>;
}

const GlobalSessionContext = createContext<GlobalSessionContextType | undefined>(
  undefined,
);

export const GlobalSessionProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  // Debug: Log when GlobalSessionProvider function is called (before hooks)
  console.log('[GlobalSessionProvider] Component function called');
  if (typeof window !== 'undefined') {
    (window as any).__GLOBAL_SESSION_PROVIDER_FUNCTION_CALLED__ = true;
  }
  
  // Hooks must be called unconditionally
  const [guideSessionToken, setGuideSessionTokenState] = useState<
    string | null
  >(null);
  const [pillarStates, setPillarStates] = useState<Record<string, any>>({});
  
  // Debug: Log when GlobalSessionProvider mounts (after hooks)
  console.log('[GlobalSessionProvider] Component mounted (after hooks)');
  if (typeof window !== 'undefined') {
    (window as any).__GLOBAL_SESSION_PROVIDER_MOUNTED__ = true;
    (window as any).__GLOBAL_SESSION_PROVIDER_MOUNT_TIME__ = Date.now();
  }

  // Hydrate from localStorage on mount
  // ✅ SIMPLIFIED: Single source of truth - use auth_token as guideSessionToken
  // This eliminates confusion and race conditions
  useEffect(() => {
    console.log("[GlobalSessionProvider] useEffect running");
    const authToken = localStorage.getItem("auth_token");
    const storedPillars = localStorage.getItem("pillarStates");
    
    console.log("[GlobalSessionProvider] authToken:", !!authToken);
    
    // ✅ SINGLE SOURCE OF TRUTH: Use auth_token as guideSessionToken
    // If no auth token, guideSessionToken remains null (user not authenticated)
    if (authToken && authToken !== 'token_placeholder' && authToken.trim() !== '') {
      setGuideSessionTokenState(authToken);
      console.log(
        "[GlobalSessionProvider] Using auth_token as guideSessionToken (single source of truth)",
      );
    } else {
      // No auth token = not authenticated = no guideSessionToken
      setGuideSessionTokenState(null);
      console.log(
        "[GlobalSessionProvider] No auth token - guideSessionToken remains null (user not authenticated)",
      );
    }
    
    if (storedPillars) {
      setPillarStates(JSON.parse(storedPillars));
      console.log(
        "[GlobalSessionProvider] set pillarStates from localStorage:",
        storedPillars,
      );
    }
  }, []);

  // ✅ Listen for auth token changes and sync guideSessionToken
  // This ensures guideSessionToken always matches auth_token (single source of truth)
  useEffect(() => {
    const syncAuthToken = () => {
      const authToken = localStorage.getItem("auth_token");
      
      if (authToken && authToken !== 'token_placeholder' && authToken.trim() !== '') {
        // Auth token exists and is valid
        if (authToken !== guideSessionToken) {
          console.log("[GlobalSessionProvider] Auth token changed, syncing guideSessionToken");
          setGuideSessionTokenState(authToken);
        }
      } else {
        // Auth token removed or invalid
        if (guideSessionToken) {
          console.log("[GlobalSessionProvider] Auth token removed, clearing guideSessionToken");
          setGuideSessionTokenState(null);
        }
      }
    };

    // Listen for storage events (cross-tab sync)
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'auth_token') {
        syncAuthToken();
      }
    };

    // Also check on mount and when guideSessionToken changes (same-tab sync)
    syncAuthToken();

    window.addEventListener('storage', handleStorageChange);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, [guideSessionToken]);

  // Persist to localStorage on change
  useEffect(() => {
    if (guideSessionToken) {
      localStorage.setItem("guideSessionToken", guideSessionToken);
    } else {
      localStorage.removeItem("guideSessionToken");
    }
    localStorage.setItem("pillarStates", JSON.stringify(pillarStates));
  }, [guideSessionToken, pillarStates]);

  // Async-friendly API
  const setGuideSessionToken = useCallback(async (token: string) => {
    setGuideSessionTokenState(token);
    // TODO: In future, persist to backend
  }, []);

  const getPillarState = useCallback(
    (pillar: string) => {
      return pillarStates[pillar] || null;
    },
    [pillarStates],
  );

  const setPillarState = useCallback(async (pillar: string, state: any) => {
    setPillarStates((prev) => ({ ...prev, [pillar]: state }));
    // TODO: In future, persist to backend
  }, []);

  const resetAllState = useCallback(async () => {
    setGuideSessionTokenState(null);
    setPillarStates({});
    localStorage.removeItem("guideSessionToken");
    localStorage.removeItem("pillarStates");
    // TODO: In future, reset on backend
  }, []);

  const value: GlobalSessionContextType = {
    guideSessionToken,
    setGuideSessionToken,
    getPillarState,
    setPillarState,
    resetAllState,
  };

  return (
    <GlobalSessionContext.Provider value={value}>
      {children}
    </GlobalSessionContext.Provider>
  );
};

export function useGlobalSession() {
  const ctx = useContext(GlobalSessionContext);
  if (!ctx) throw new Error('useGlobalSession must be used within GlobalSessionProvider');
  return ctx;
}
