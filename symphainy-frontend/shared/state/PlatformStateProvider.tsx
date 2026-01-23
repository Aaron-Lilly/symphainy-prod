/**
 * Platform State Provider
 * 
 * Unified state management provider that consolidates:
 * - Session state (synced with Runtime)
 * - Execution state (from Runtime)
 * - Realm state (from State Surface)
 * - UI state (local)
 * 
 * Replaces:
 * - GlobalSessionProvider
 * - SessionProvider
 * - AppProvider
 * - AGUIEventProvider (event handling)
 * 
 * Architecture:
 * - Single source of truth for platform state
 * - Syncs with Runtime via Experience Plane Client
 * - No context errors (proper provider hierarchy)
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
import { ExperiencePlaneClient, ExecutionStatus } from "@/shared/services/ExperiencePlaneClient";
import { getGlobalExperiencePlaneClient } from "@/shared/services/ExperiencePlaneClient";
import { useSessionBoundary, SessionStatus } from "./SessionBoundaryProvider";

// State interfaces
export interface SessionState {
  sessionId: string | null;
  tenantId: string | null;
  userId: string | null;
  session: null; // ✅ SESSION BOUNDARY PATTERN: Session object not stored here - use SessionBoundaryProvider
  isLoading: boolean;
  error: string | null;
}

export interface ExecutionState {
  executions: Map<string, ExecutionStatus>;
  activeExecutions: string[];
  isLoading: boolean;
  error: string | null;
}

export interface RealmState {
  content: Record<string, any>;
  insights: Record<string, any>;
  journey: Record<string, any>;
  outcomes: Record<string, any>;
}

export interface UIState {
  currentPillar: "content" | "insights" | "journey" | "outcomes" | null;
  sidebarOpen: boolean;
  notifications: Array<{
    id: string;
    type: "info" | "success" | "warning" | "error";
    message: string;
    timestamp: Date;
  }>;
}

export interface PlatformState {
  session: SessionState;
  execution: ExecutionState;
  realm: RealmState;
  ui: UIState;
}

// Context
interface PlatformStateContextType {
  // State
  state: PlatformState;
  
  // ✅ SESSION BOUNDARY PATTERN: Session management removed - use SessionBoundaryProvider instead
  // Session actions removed - subscribe to SessionBoundaryProvider for session state
  
  // Execution actions
  submitIntent: (
    intentType: string,
    parameters?: Record<string, any>,
    metadata?: Record<string, any>
  ) => Promise<string>;
  getExecutionStatus: (executionId: string) => Promise<ExecutionStatus | null>;
  trackExecution: (executionId: string) => void;
  untrackExecution: (executionId: string) => void;
  
  // Realm state actions
  setRealmState: (realm: "content" | "insights" | "journey" | "outcomes", key: string, value: any) => void;
  getRealmState: (realm: "content" | "insights" | "journey" | "outcomes", key: string) => any;
  clearRealmState: (realm: "content" | "insights" | "journey" | "outcomes") => void;
  
  // UI actions
  setCurrentPillar: (pillar: "content" | "insights" | "journey" | "outcomes" | null) => void;
  setSidebarOpen: (open: boolean) => void;
  addNotification: (type: "info" | "success" | "warning" | "error", message: string) => void;
  removeNotification: (id: string) => void;
  
  // Sync actions
  syncWithRuntime: () => Promise<void>;
}

const PlatformStateContext = createContext<PlatformStateContextType | undefined>(undefined);

export const usePlatformState = (): PlatformStateContextType => {
  const context = useContext(PlatformStateContext);
  
  // SSR-safe: Return a safe default during prerendering
  if (context === undefined) {
    if (typeof window === 'undefined') {
      // Server-side: Return a minimal safe default
      return {
        state: {
          session: {
            sessionId: null,
            tenantId: null,
            userId: null,
            session: null,
            isLoading: false,
            error: null,
          },
          execution: {
            executions: new Map(),
            activeExecutions: [],
            isLoading: false,
            error: null,
          },
          realm: {
            content: {},
            insights: {},
            journey: {},
            outcomes: {},
          },
          ui: {
            currentPillar: null,
            sidebarOpen: false,
            notifications: [],
          },
        },
        submitIntent: async () => "",
        getExecutionStatus: async () => null,
        trackExecution: () => {},
        untrackExecution: () => {},
        setRealmState: () => {},
        getRealmState: () => ({}),
        clearRealmState: () => {},
        setCurrentPillar: () => {},
        setSidebarOpen: () => {},
        addNotification: () => {},
        removeNotification: () => {},
        syncWithRuntime: async () => {},
      };
    }
    // Client-side: This is a real error
    throw new Error("usePlatformState must be used within PlatformStateProvider");
  }
  return context;
};

interface PlatformStateProviderProps {
  children: React.ReactNode;
  experiencePlaneClient?: ExperiencePlaneClient;
}

export const PlatformStateProvider: React.FC<PlatformStateProviderProps> = ({
  children,
  experiencePlaneClient,
}) => {
  const client = experiencePlaneClient || getGlobalExperiencePlaneClient();
  const syncIntervalRef = useRef<NodeJS.Timeout | null>(null);
  
  // ✅ SESSION BOUNDARY PATTERN: Subscribe to SessionBoundaryProvider for session state
  const { state: sessionState } = useSessionBoundary();
  
  // ✅ BEST PRACTICE: Check access_token directly (set by AuthProvider) to determine authentication
  // This prevents circular dependency (AuthProvider uses usePlatformState)
  // Pattern: AuthProvider sets access_token → PlatformStateProvider checks it → loads session if authenticated
  // This is similar to how NextAuth and Auth0 work - session provider checks token, not auth state
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authChecked, setAuthChecked] = useState(false);
  
  // Check authentication status by looking for access_token (set by AuthProvider)
  // Wait a small delay to let AuthProvider initialize first
  useEffect(() => {
    const checkAuth = () => {
      const accessToken = typeof window !== 'undefined' ? sessionStorage.getItem("access_token") : null;
      setIsAuthenticated(!!accessToken);
      setAuthChecked(true);
    };
    
    // Small delay to let AuthProvider initialize and set access_token
    const timer = setTimeout(checkAuth, 100);
    return () => clearTimeout(timer);
  }, []);
  
  // Also listen for storage changes (when AuthProvider sets/removes access_token)
  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'access_token') {
        setIsAuthenticated(!!e.newValue);
      }
    };
    
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  // ✅ SESSION BOUNDARY PATTERN: No cleanup code here
  // SessionBoundaryProvider handles all session lifecycle management

  // ✅ SESSION BOUNDARY PATTERN: Sync session state from SessionBoundaryProvider
  // Session state is managed by SessionBoundaryProvider - we just mirror it here for backward compatibility
  useEffect(() => {
    setState((prev) => ({
      ...prev,
      session: {
        sessionId: sessionState.sessionId,
        tenantId: sessionState.tenantId,
        userId: sessionState.userId,
        session: null, // We don't store full session object here anymore
        isLoading: sessionState.status === SessionStatus.Initializing || sessionState.status === SessionStatus.Recovering,
        error: sessionState.error,
      },
    }));
  }, [sessionState]);

  // Initialize state
  const [state, setState] = useState<PlatformState>({
    session: {
      sessionId: sessionState.sessionId,
      tenantId: sessionState.tenantId,
      userId: sessionState.userId,
      session: null,
      isLoading: sessionState.status === SessionStatus.Initializing || sessionState.status === SessionStatus.Recovering,
      error: sessionState.error,
    },
    execution: {
      executions: new Map(),
      activeExecutions: [],
      isLoading: false,
      error: null,
    },
    realm: {
      content: {},
      insights: {},
      journey: {},
      outcomes: {},
    },
    ui: {
      currentPillar: null,
      sidebarOpen: false,
      notifications: [],
    },
  });

  // ✅ SESSION BOUNDARY PATTERN: Session management removed
  // All session operations are handled by SessionBoundaryProvider
  // No session methods here - components should use useSessionBoundary() instead

  // ✅ SESSION BOUNDARY PATTERN: Session initialization removed
  // SessionBoundaryProvider handles all session lifecycle management

  // Execution actions
  const submitIntent = useCallback(
    async (
      intentType: string,
      parameters?: Record<string, any>,
      metadata?: Record<string, any>
    ): Promise<string> => {
      // ✅ SESSION BOUNDARY PATTERN: Use session state from SessionBoundaryProvider
      if (!sessionState.sessionId || !sessionState.tenantId) {
        throw new Error("Active session required to submit intent");
      }

      setState((prev) => ({
        ...prev,
        execution: { ...prev.execution, isLoading: true, error: null },
      }));

      try {
        const response = await client.submitIntent({
          intent_type: intentType,
          tenant_id: sessionState.tenantId!,
          session_id: sessionState.sessionId,
          parameters,
          metadata,
        });

        const executionStatus: ExecutionStatus = {
          execution_id: response.execution_id,
          status: "pending",
          intent_id: response.intent_id,
          tenant_id: sessionState.tenantId!,
          session_id: sessionState.sessionId,
          started_at: response.created_at,
        };

        setState((prev) => {
          const executions = new Map(prev.execution.executions);
          executions.set(response.execution_id, executionStatus);
          return {
            ...prev,
            execution: {
              ...prev.execution,
              executions,
              activeExecutions: [...prev.execution.activeExecutions, response.execution_id],
              isLoading: false,
              error: null,
            },
          };
        });

        // Track execution updates
        trackExecution(response.execution_id);

        return response.execution_id;
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : "Failed to submit intent";
        setState((prev) => ({
          ...prev,
          execution: { ...prev.execution, isLoading: false, error: errorMessage },
        }));
        throw error;
      }
    },
    [client, sessionState.sessionId, sessionState.tenantId]
  );

  const getExecutionStatus = useCallback(
    async (executionId: string): Promise<ExecutionStatus | null> => {
      // ✅ SESSION BOUNDARY PATTERN: Use session state from SessionBoundaryProvider
      if (!sessionState.tenantId) {
        throw new Error("Active session required to get execution status");
      }

      try {
        const status = await client.getExecutionStatus(executionId, sessionState.tenantId);
        setState((prev) => {
          const executions = new Map(prev.execution.executions);
          executions.set(executionId, status);
          return {
            ...prev,
            execution: {
              ...prev.execution,
              executions,
            },
          };
        });
        return status;
      } catch (error) {
        console.error("Failed to get execution status:", error);
        return null;
      }
    },
    [client, sessionState.tenantId]
  );

  const trackExecution = useCallback((executionId: string) => {
    // Subscribe to execution updates via WebSocket
    client.streamExecution(
      executionId,
      (status) => {
        setState((prev) => {
          const executions = new Map(prev.execution.executions);
          executions.set(executionId, status);
          
          // Update active executions list
          let activeExecutions = [...prev.execution.activeExecutions];
          if (status.status === "completed" || status.status === "failed" || status.status === "cancelled") {
            activeExecutions = activeExecutions.filter((id) => id !== executionId);
          } else if (!activeExecutions.includes(executionId)) {
            activeExecutions.push(executionId);
          }

          return {
            ...prev,
            execution: {
              ...prev.execution,
              executions,
              activeExecutions,
            },
          };
        });
      },
      (error) => {
        console.error("Execution streaming error:", error);
      }
    );
  }, [client]);

  const untrackExecution = useCallback((executionId: string) => {
    setState((prev) => {
      const activeExecutions = prev.execution.activeExecutions.filter((id) => id !== executionId);
      return {
        ...prev,
        execution: {
          ...prev.execution,
          activeExecutions,
        },
      };
    });
  }, []);

  // Realm state actions
  const setRealmState = useCallback(
    (realm: "content" | "insights" | "journey" | "outcomes", key: string, value: any) => {
      setState((prev) => ({
        ...prev,
        realm: {
          ...prev.realm,
          [realm]: {
            ...prev.realm[realm],
            [key]: value,
          },
        },
      }));
    },
    []
  );

  const getRealmState = useCallback(
    (realm: "content" | "insights" | "journey" | "outcomes", key: string) => {
      return state.realm[realm][key];
    },
    [state.realm]
  );

  const clearRealmState = useCallback((realm: "content" | "insights" | "journey" | "outcomes") => {
    setState((prev) => ({
      ...prev,
      realm: {
        ...prev.realm,
        [realm]: {},
      },
    }));
  }, []);

  // UI actions
  const setCurrentPillar = useCallback((pillar: "content" | "insights" | "journey" | "outcomes" | null) => {
    setState((prev) => ({
      ...prev,
      ui: { ...prev.ui, currentPillar: pillar },
    }));
  }, []);

  const setSidebarOpen = useCallback((open: boolean) => {
    setState((prev) => ({
      ...prev,
      ui: { ...prev.ui, sidebarOpen: open },
    }));
  }, []);

  const addNotification = useCallback(
    (type: "info" | "success" | "warning" | "error", message: string) => {
      const notification = {
        id: `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        type,
        message,
        timestamp: new Date(),
      };
      setState((prev) => ({
        ...prev,
        ui: {
          ...prev.ui,
          notifications: [...prev.ui.notifications, notification],
        },
      }));
    },
    []
  );

  const removeNotification = useCallback((id: string) => {
    setState((prev) => ({
      ...prev,
      ui: {
        ...prev.ui,
        notifications: prev.ui.notifications.filter((n) => n.id !== id),
      },
    }));
  }, []);

  // ✅ SESSION BOUNDARY PATTERN: Sync with Runtime - ONLY when session is Active
  // Sync follows session state - never leads it
  const syncWithRuntime = useCallback(async () => {
    // Only sync when session is Active (authenticated and valid)
    if (sessionState.status !== SessionStatus.Active) {
      return;
    }
    
    if (!sessionState.sessionId) {
      return;
    }

    try {
      // Sync active executions (only if we have a valid active session)
      for (const executionId of state.execution.activeExecutions) {
        await getExecutionStatus(executionId);
      }
    } catch (error) {
      console.error("Failed to sync with Runtime:", error);
      // Don't clear session state here - SessionBoundaryProvider handles that
    }
  }, [sessionState.status, sessionState.sessionId, state.execution.activeExecutions, getExecutionStatus]);

  // Periodic sync with Runtime (every 30 seconds) - ONLY if user is authenticated
  // ✅ SESSION-FIRST: Check access_token to determine authentication
  // Anonymous sessions exist but don't sync (no tenant_id/user_id)
  useEffect(() => {
    // Check if user is authenticated (has access_token)
    const accessToken = typeof window !== 'undefined' ? sessionStorage.getItem("access_token") : null;
    
    // Only sync if authenticated AND session has tenant_id (not anonymous)
    if (sessionState.status === SessionStatus.Active && sessionState.sessionId && sessionState.tenantId) {
      syncIntervalRef.current = setInterval(() => {
        syncWithRuntime();
      }, 30000);
    } else {
      // Clear interval if no session, not authenticated, or anonymous session
      if (syncIntervalRef.current) {
        clearInterval(syncIntervalRef.current);
        syncIntervalRef.current = null;
      }
    }

    return () => {
      if (syncIntervalRef.current) {
        clearInterval(syncIntervalRef.current);
      }
    };
  }, [sessionState.status, sessionState.sessionId, sessionState.tenantId, syncWithRuntime]);

  const contextValue: PlatformStateContextType = {
    state,
    submitIntent,
    getExecutionStatus,
    trackExecution,
    untrackExecution,
    setRealmState,
    getRealmState,
    clearRealmState,
    setCurrentPillar,
    setSidebarOpen,
    addNotification,
    removeNotification,
    syncWithRuntime,
  };

  return (
    <PlatformStateContext.Provider value={contextValue}>
      {children}
    </PlatformStateContext.Provider>
  );
};
