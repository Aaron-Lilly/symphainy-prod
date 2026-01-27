/**
 * Enhanced Global Session Provider
 * Uses micro-modular session management with Smart City integration
 */

"use client";
import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { SessionManager } from './core';
import { SessionContextType, SessionStatus } from './types';
import { useSessionStatus } from './hooks';

const GlobalSessionContext = createContext<SessionContextType | undefined>(undefined);

export const GlobalSessionProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [sessionManager] = useState(() => new SessionManager());
  const { status, isSessionValid } = useSessionStatus();

  // Hydrate from localStorage on mount
  useEffect(() => {
    console.log("[GlobalSessionProvider] useEffect running");
    const storedToken = localStorage.getItem("guideSessionToken");
    const storedPillars = localStorage.getItem("pillarStates");
    
    console.log("[GlobalSessionProvider] storedToken:", storedToken);
    
    if (storedToken) {
      sessionManager.setGuideSessionToken(storedToken);
      console.log("[GlobalSessionProvider] set guideSessionToken from localStorage:", storedToken);
    } else {
      // Start a new session if none exists
      console.log("[GlobalSessionProvider] No token found, starting new session");
      sessionManager.startNewSession()
        .then((token) => {
          localStorage.setItem("guideSessionToken", token);
          console.log("[GlobalSessionProvider] New session token set:", token);
        })
        .catch((err) => {
          console.error("[GlobalSessionProvider] Failed to start session:", err);
        });
    }
    
    if (storedPillars) {
      const pillarStates = JSON.parse(storedPillars);
      Object.entries(pillarStates).forEach(([pillar, state]) => {
        sessionManager.setPillarState(pillar, state);
      });
      console.log("[GlobalSessionProvider] set pillarStates from localStorage:", storedPillars);
    }
  }, [sessionManager]);

  // Persist to localStorage on change
  useEffect(() => {
    const unsubscribe = sessionManager.subscribe((state) => {
      if (state.guideSessionToken) {
        localStorage.setItem("guideSessionToken", state.guideSessionToken);
      } else {
        localStorage.removeItem("guideSessionToken");
      }
      localStorage.setItem("pillarStates", JSON.stringify(state.pillarStates));
    });

    return unsubscribe;
  }, [sessionManager]);

  const value: SessionContextType = {
    guideSessionToken: sessionManager.getState().guideSessionToken,
    setGuideSessionToken: sessionManager.setGuideSessionToken.bind(sessionManager),
    getPillarState: sessionManager.getPillarState.bind(sessionManager),
    setPillarState: sessionManager.setPillarState.bind(sessionManager),
    resetAllState: sessionManager.resetAllState.bind(sessionManager),
    sessionStatus: status,
    isSessionValid,
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