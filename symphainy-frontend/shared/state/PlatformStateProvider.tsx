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
import { ExperiencePlaneClient, Session, ExecutionStatus } from "@/shared/services/ExperiencePlaneClient";
import { getGlobalExperiencePlaneClient } from "@/shared/services/ExperiencePlaneClient";

// State interfaces
export interface SessionState {
  sessionId: string | null;
  tenantId: string | null;
  userId: string | null;
  session: Session | null;
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
  
  // Session actions
  createSession: (tenantId: string, userId: string, metadata?: Record<string, any>) => Promise<string>;
  getSession: (sessionId: string) => Promise<Session | null>;
  setSession: (session: Session) => void;
  clearSession: () => void;
  
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
  if (!context) {
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

  // Initialize state
  const [state, setState] = useState<PlatformState>({
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
  });

  // Session actions
  const createSession = useCallback(
    async (tenantId: string, userId: string, metadata?: Record<string, any>): Promise<string> => {
      setState((prev) => ({
        ...prev,
        session: { ...prev.session, isLoading: true, error: null },
      }));

      try {
        const response = await client.createSession({
          tenant_id: tenantId,
          user_id: userId,
          metadata,
        });

        setState((prev) => ({
          ...prev,
          session: {
            sessionId: response.session_id,
            tenantId: response.tenant_id,
            userId: response.user_id,
            session: {
              session_id: response.session_id,
              tenant_id: response.tenant_id,
              user_id: response.user_id,
              created_at: response.created_at,
              metadata: response.metadata,
            },
            isLoading: false,
            error: null,
          },
        }));

        // Store in localStorage for persistence
        localStorage.setItem("session_id", response.session_id);
        localStorage.setItem("tenant_id", response.tenant_id);
        localStorage.setItem("user_id", response.user_id);

        return response.session_id;
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : "Failed to create session";
        setState((prev) => ({
          ...prev,
          session: { ...prev.session, isLoading: false, error: errorMessage },
        }));
        throw error;
      }
    },
    [client]
  );

  const getSession = useCallback(
    async (sessionId: string): Promise<Session | null> => {
      if (!state.session.tenantId) {
        throw new Error("Tenant ID required to get session");
      }

      try {
        const session = await client.getSession(sessionId, state.session.tenantId);
        setState((prev) => ({
          ...prev,
          session: { ...prev.session, session },
        }));
        return session;
      } catch (error) {
        console.error("Failed to get session:", error);
        return null;
      }
    },
    [client, state.session.tenantId]
  );

  const setSession = useCallback((session: Session) => {
    setState((prev) => ({
      ...prev,
      session: {
        sessionId: session.session_id,
        tenantId: session.tenant_id,
        userId: session.user_id,
        session,
        isLoading: false,
        error: null,
      },
    }));
  }, []);

  const clearSession = useCallback(() => {
    setState((prev) => ({
      ...prev,
      session: {
        sessionId: null,
        tenantId: null,
        userId: null,
        session: null,
        isLoading: false,
        error: null,
      },
    }));
    localStorage.removeItem("session_id");
    localStorage.removeItem("tenant_id");
    localStorage.removeItem("user_id");
  }, []);

  // Execution actions
  const submitIntent = useCallback(
    async (
      intentType: string,
      parameters?: Record<string, any>,
      metadata?: Record<string, any>
    ): Promise<string> => {
      if (!state.session.sessionId || !state.session.tenantId) {
        throw new Error("Session required to submit intent");
      }

      setState((prev) => ({
        ...prev,
        execution: { ...prev.execution, isLoading: true, error: null },
      }));

      try {
        const response = await client.submitIntent({
          intent_type: intentType,
          tenant_id: state.session.tenantId,
          session_id: state.session.sessionId,
          parameters,
          metadata,
        });

        const executionStatus: ExecutionStatus = {
          execution_id: response.execution_id,
          status: "pending",
          intent_id: response.intent_id,
          tenant_id: state.session.tenantId,
          session_id: state.session.sessionId,
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
    [client, state.session.sessionId, state.session.tenantId]
  );

  const getExecutionStatus = useCallback(
    async (executionId: string): Promise<ExecutionStatus | null> => {
      if (!state.session.tenantId) {
        throw new Error("Tenant ID required to get execution status");
      }

      try {
        const status = await client.getExecutionStatus(executionId, state.session.tenantId);
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
    [client, state.session.tenantId]
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

  // Sync with Runtime
  const syncWithRuntime = useCallback(async () => {
    if (!state.session.sessionId || !state.session.tenantId) {
      return;
    }

    try {
      // Sync session
      const session = await getSession(state.session.sessionId);
      if (session) {
        setSession(session);
      }

      // Sync active executions
      for (const executionId of state.execution.activeExecutions) {
        await getExecutionStatus(executionId);
      }
    } catch (error) {
      console.error("Failed to sync with Runtime:", error);
    }
  }, [state.session.sessionId, state.session.tenantId, state.execution.activeExecutions, getSession, setSession, getExecutionStatus]);

  // Hydrate from localStorage on mount
  useEffect(() => {
    const sessionId = localStorage.getItem("session_id");
    const tenantId = localStorage.getItem("tenant_id");
    const userId = localStorage.getItem("user_id");

    if (sessionId && tenantId && userId) {
      setState((prev) => ({
        ...prev,
        session: {
          ...prev.session,
          sessionId,
          tenantId,
          userId,
        },
      }));

      // Load session details
      client.getSession(sessionId, tenantId).then((session) => {
        if (session) {
          setSession(session);
        }
      }).catch((error) => {
        console.error("Failed to load session:", error);
      });
    }
  }, [client, setSession]);

  // Periodic sync with Runtime (every 30 seconds)
  useEffect(() => {
    if (state.session.sessionId) {
      syncIntervalRef.current = setInterval(() => {
        syncWithRuntime();
      }, 30000);
    }

    return () => {
      if (syncIntervalRef.current) {
        clearInterval(syncIntervalRef.current);
      }
    };
  }, [state.session.sessionId, syncWithRuntime]);

  const contextValue: PlatformStateContextType = {
    state,
    createSession,
    getSession,
    setSession,
    clearSession,
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
