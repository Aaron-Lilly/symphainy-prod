/**
 * Session Boundary Provider
 * 
 * Single source of truth for session lifecycle management.
 * 
 * Architecture Principles:
 * 1. Sessions are lease-based, not guaranteed (404/401 = state transition, not error)
 * 2. Only this component calls /api/session/* endpoints
 * 3. Realtime connections follow session state (never lead it)
 * 4. Cleanup is event-driven, not component-driven
 * 
 * Pattern matches: Salesforce, Slack, Notion, GitHub, Figma
 */

"use client";

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  useRef,
} from "react";
import { ExperiencePlaneClient } from "@/shared/services/ExperiencePlaneClient";
import { getGlobalExperiencePlaneClient } from "@/shared/services/ExperiencePlaneClient";

// ============================================================================
// SESSION STATUS STATE MACHINE
// ============================================================================

export enum SessionStatus {
  Initializing = "Initializing",     // Checking existing session
  Anonymous = "Anonymous",           // Valid anonymous session
  Authenticating = "Authenticating", // Login in progress
  Active = "Active",                 // Valid authenticated session
  Invalid = "Invalid",               // 404/401 received - session doesn't exist
  Recovering = "Recovering",        // Creating new session after invalidation
}

// ============================================================================
// SESSION STATE INTERFACE
// ============================================================================

export interface SessionBoundaryState {
  status: SessionStatus;
  sessionId: string | null;
  tenantId: string | null;
  userId: string | null;
  error: string | null;
}

// ============================================================================
// CONTEXT INTERFACE
// ============================================================================

interface SessionBoundaryContextType {
  // State
  state: SessionBoundaryState;
  
  // Actions
  createAnonymousSession: () => Promise<void>;
  upgradeSession: (userData: { user_id: string; tenant_id: string; access_token: string; metadata?: Record<string, any> }) => Promise<void>;
  invalidateSession: () => void; // Explicit invalidation (e.g., logout)
  recoverSession: () => Promise<void>; // Manual recovery trigger
}

const SessionBoundaryContext = createContext<SessionBoundaryContextType | undefined>(undefined);

// ============================================================================
// HOOK
// ============================================================================

export const useSessionBoundary = (): SessionBoundaryContextType => {
  const context = useContext(SessionBoundaryContext);
  
  // SSR-safe: Return a safe default during prerendering
  if (context === undefined) {
    if (typeof window === 'undefined') {
      // Server-side: Return a minimal safe default
      return {
        state: {
          status: SessionStatus.Initializing,
          sessionId: null,
          tenantId: null,
          userId: null,
          error: null,
        },
        createAnonymousSession: async () => {},
        upgradeSession: async () => {},
        invalidateSession: () => {},
        recoverSession: async () => {},
      };
    }
    // Client-side: This is a real error
    throw new Error("useSessionBoundary must be used within SessionBoundaryProvider");
  }
  return context;
};

// ============================================================================
// PROVIDER COMPONENT
// ============================================================================

interface SessionBoundaryProviderProps {
  children: React.ReactNode;
  experiencePlaneClient?: ExperiencePlaneClient;
}

export const SessionBoundaryProvider: React.FC<SessionBoundaryProviderProps> = ({
  children,
  experiencePlaneClient,
}) => {
  const client = experiencePlaneClient || getGlobalExperiencePlaneClient();
  const isMountedRef = useRef(true);
  const recoveryInProgressRef = useRef(false);

  const [state, setState] = useState<SessionBoundaryState>({
    status: SessionStatus.Initializing,
    sessionId: null,
    tenantId: null,
    userId: null,
    error: null,
  });

  // ============================================================================
  // STATE TRANSITIONS (Internal)
  // ============================================================================

  const transitionTo = useCallback((newStatus: SessionStatus, updates?: Partial<SessionBoundaryState>) => {
    if (!isMountedRef.current) return;
    
    setState((prev) => {
      const newState = {
        ...prev,
        status: newStatus,
        ...updates,
      };
      
      // Log state transitions (not errors)
      if (newStatus === SessionStatus.Invalid) {
        console.info("🔄 [SessionBoundary] Session invalidated - transitioning to recovery");
      } else if (newStatus === SessionStatus.Recovering) {
        console.info("🔄 [SessionBoundary] Recovering session...");
      } else if (newStatus === SessionStatus.Anonymous) {
        console.info("✅ [SessionBoundary] Anonymous session established");
      } else if (newStatus === SessionStatus.Active) {
        console.info("✅ [SessionBoundary] Authenticated session active");
      }
      
      return newState;
    });
  }, []);

  // ============================================================================
  // SESSION OPERATIONS (ONLY place that calls /api/session/*)
  // ============================================================================

  /**
   * Create anonymous session
   * Called during initialization or recovery
   */
  const createAnonymousSession = useCallback(async (): Promise<void> => {
    if (!isMountedRef.current) return;
    
    try {
      transitionTo(SessionStatus.Recovering);
      
      const response = await client.createAnonymousSession();
      
      if (!isMountedRef.current) return;
      
      // Store session_id in sessionStorage (only thing we store)
      if (typeof window !== 'undefined') {
        sessionStorage.setItem("session_id", response.session_id);
        // Don't store tenant_id or user_id for anonymous sessions
      }
      
      transitionTo(SessionStatus.Anonymous, {
        sessionId: response.session_id,
        tenantId: null,
        userId: null,
        error: null,
      });
    } catch (error) {
      if (!isMountedRef.current) return;
      
      const errorMessage = error instanceof Error ? error.message : "Failed to create anonymous session";
      console.error("❌ [SessionBoundary] Failed to create anonymous session:", error);
      
      transitionTo(SessionStatus.Invalid, {
        error: errorMessage,
      });
    }
  }, [client, transitionTo]);

  /**
   * Upgrade anonymous session to authenticated
   * Called by AuthProvider after successful login
   */
  const upgradeSession = useCallback(async (
    userData: { user_id: string; tenant_id: string; access_token: string; metadata?: Record<string, any> }
  ): Promise<void> => {
    if (!isMountedRef.current || !state.sessionId) {
      console.warn("⚠️ [SessionBoundary] Cannot upgrade: no existing session");
      return;
    }
    
    try {
      transitionTo(SessionStatus.Authenticating);
      
      const session = await client.upgradeSession(state.sessionId, {
        user_id: userData.user_id,
        tenant_id: userData.tenant_id,
        access_token: userData.access_token,
        metadata: userData.metadata,
      });
      
      if (!isMountedRef.current) return;
      
      // Store tenant_id and user_id in sessionStorage
      if (typeof window !== 'undefined') {
        sessionStorage.setItem("tenant_id", userData.tenant_id);
        sessionStorage.setItem("user_id", userData.user_id);
        sessionStorage.setItem("access_token", userData.access_token);
      }
      
      transitionTo(SessionStatus.Active, {
        sessionId: session.session_id,
        tenantId: session.tenant_id || null,
        userId: session.user_id || null,
        error: null,
      });
    } catch (error) {
      if (!isMountedRef.current) return;
      
      const errorMessage = error instanceof Error ? error.message : "Failed to upgrade session";
      console.error("❌ [SessionBoundary] Failed to upgrade session:", error);
      
      // On upgrade failure, invalidate and recover
      transitionTo(SessionStatus.Invalid, {
        error: errorMessage,
      });
      
      // Auto-recover to anonymous session
      await recoverSession();
    }
  }, [client, state.sessionId, transitionTo]);

  /**
   * Invalidate session (e.g., on logout)
   */
  const invalidateSession = useCallback(() => {
    if (!isMountedRef.current) return;
    
    // Clear storage
    if (typeof window !== 'undefined') {
      sessionStorage.removeItem("session_id");
      sessionStorage.removeItem("tenant_id");
      sessionStorage.removeItem("user_id");
      sessionStorage.removeItem("access_token");
    }
    
    transitionTo(SessionStatus.Invalid, {
      sessionId: null,
      tenantId: null,
      userId: null,
      error: null,
    });
  }, [transitionTo]);

  /**
   * Recover from invalid session
   * Creates new anonymous session
   */
  const recoverSession = useCallback(async (): Promise<void> => {
    if (recoveryInProgressRef.current) {
      return; // Already recovering
    }
    
    recoveryInProgressRef.current = true;
    
    try {
      await createAnonymousSession();
    } finally {
      recoveryInProgressRef.current = false;
    }
  }, [createAnonymousSession]);

  // ============================================================================
  // INITIALIZATION: Check existing session on mount
  // ============================================================================

  useEffect(() => {
    isMountedRef.current = true;
    
    const initializeSession = async () => {
      if (typeof window === 'undefined') {
        return;
      }
      
      try {
        // Check for existing session_id
        const existingSessionId = sessionStorage.getItem("session_id");
        const existingTenantId = sessionStorage.getItem("tenant_id");
        const existingUserId = sessionStorage.getItem("user_id");
        const accessToken = sessionStorage.getItem("access_token");
        
        if (existingSessionId) {
          // Try to load existing session
          try {
            const session = await client.getSession(existingSessionId, existingTenantId || undefined);
            
            if (!isMountedRef.current) return;
            
            if (session) {
              // Session exists and is valid
              if (accessToken && session.tenant_id && session.user_id) {
                // Authenticated session
                transitionTo(SessionStatus.Active, {
                  sessionId: session.session_id,
                  tenantId: session.tenant_id || null,
                  userId: session.user_id || null,
                  error: null,
                });
              } else {
                // Anonymous session
                transitionTo(SessionStatus.Anonymous, {
                  sessionId: session.session_id,
                  tenantId: null,
                  userId: null,
                  error: null,
                });
              }
              return; // Successfully loaded
            }
          } catch (error) {
            if (!isMountedRef.current) return;
            
            // 404/401 = Session doesn't exist (state transition, not error)
            const is404 = error instanceof Error && (
              error.message.includes("not found") ||
              error.message.includes("404") ||
              (error.message.includes("Session") && error.message.includes("not found")) ||
              ((error as any).status === 404)
            );
            
            const is401 = error instanceof Error && (
              error.message.includes("401") ||
              error.message.includes("unauthorized") ||
              ((error as any).status === 401)
            );
            
            if (is404 || is401) {
              // This is a state transition, not an error
              console.info("ℹ️ [SessionBoundary] Existing session invalid (404/401) - will recover");
              transitionTo(SessionStatus.Invalid);
              
              // Auto-recover to anonymous session
              await recoverSession();
              return;
            }
            
            // Other errors (network, etc.) - log but don't treat as session invalidation
            console.error("❌ [SessionBoundary] Error loading session:", error);
            transitionTo(SessionStatus.Invalid, {
              error: error instanceof Error ? error.message : "Failed to load session",
            });
            
            // Still try to recover
            await recoverSession();
            return;
          }
        }
        
        // No existing session - create anonymous session
        if (!isMountedRef.current) return;
        await createAnonymousSession();
      } catch (error) {
        if (!isMountedRef.current) return;
        
        console.error("❌ [SessionBoundary] Failed to initialize session:", error);
        transitionTo(SessionStatus.Invalid, {
          error: error instanceof Error ? error.message : "Failed to initialize session",
        });
        
        // Try to recover
        await recoverSession();
      }
    };
    
    initializeSession();
    
    return () => {
      isMountedRef.current = false;
    };
  }, [client, createAnonymousSession, recoverSession, transitionTo]);

  // ============================================================================
  // CONTEXT VALUE
  // ============================================================================

  const contextValue: SessionBoundaryContextType = {
    state,
    createAnonymousSession,
    upgradeSession,
    invalidateSession,
    recoverSession,
  };

  return (
    <SessionBoundaryContext.Provider value={contextValue}>
      {children}
    </SessionBoundaryContext.Provider>
  );
};
