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
  // ✅ PHASE 5: Chatbot/UI state (consolidated from Jotai atoms)
  chatbot: {
    mainChatbotOpen: boolean;
    agentInfo: {
      title: string;
      agent: string;
      file_url: string;
      additional_info: string;
    };
    chatInputFocused: boolean;
    messageComposing: boolean;
  };
  // ✅ PHASE 5: Analysis results (consolidated from Jotai atoms)
  analysisResults: {
    business: any | null;
    visualization: any | null;
    anomaly: any | null;
    eda: any | null;
  };
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
  setRealmState: (realm: "content" | "insights" | "journey" | "outcomes", key: string, value: any) => Promise<void>;
  getRealmState: (realm: "content" | "insights" | "journey" | "outcomes", key: string) => any;
  clearRealmState: (realm: "content" | "insights" | "journey" | "outcomes") => void;
  
  // UI actions
  setCurrentPillar: (pillar: "content" | "insights" | "journey" | "outcomes" | null) => void;
  setSidebarOpen: (open: boolean) => void;
  addNotification: (type: "info" | "success" | "warning" | "error", message: string) => void;
  removeNotification: (id: string) => void;
  
  // ✅ PHASE 5: Chatbot state actions (replaces Jotai atoms)
  setMainChatbotOpen: (open: boolean) => void;
  setChatbotAgentInfo: (info: { title?: string; agent?: string; file_url?: string; additional_info?: string }) => void;
  setChatInputFocused: (focused: boolean) => void;
  setMessageComposing: (composing: boolean) => void;
  
  // ✅ PHASE 5: Analysis results actions (replaces Jotai atoms)
  setAnalysisResult: (type: "business" | "visualization" | "anomaly" | "eda", result: any) => void;
  clearAnalysisResults: () => void;
  
  // ✅ PHASE 5: Derived chatbot state (computed from mainChatbotOpen)
  getShouldShowSecondaryChatbot: () => boolean;
  getPrimaryChatbotHeight: () => string;
  getSecondaryChatbotPosition: () => string;
  getPrimaryChatbotTransform: () => string;
  
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
            // ✅ PHASE 5: Chatbot/UI state initialization
            chatbot: {
              mainChatbotOpen: true,
              agentInfo: {
                title: "",
                agent: "",
                file_url: "",
                additional_info: "",
              },
              chatInputFocused: false,
              messageComposing: false,
            },
            analysisResults: {
              business: null,
              visualization: null,
              anomaly: null,
              eda: null,
            },
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
        // ✅ PHASE 5: Chatbot state actions
        setMainChatbotOpen: () => {},
        setChatbotAgentInfo: () => {},
        setChatInputFocused: () => {},
        setMessageComposing: () => {},
        // ✅ PHASE 5: Analysis results actions
        setAnalysisResult: () => {},
        clearAnalysisResults: () => {},
        // ✅ PHASE 5: Derived chatbot state
        getShouldShowSecondaryChatbot: () => false,
        getPrimaryChatbotHeight: () => 'h-[87vh]',
        getSecondaryChatbotPosition: () => 'translate-x-full opacity-0',
        getPrimaryChatbotTransform: () => 'translate-y-0',
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
      // ✅ PHASE 5: Chatbot/UI state initialization
      chatbot: {
        mainChatbotOpen: true,
        agentInfo: {
          title: "",
          agent: "",
          file_url: "",
          additional_info: "",
        },
        chatInputFocused: false,
        messageComposing: false,
      },
      analysisResults: {
        business: null,
        visualization: null,
        anomaly: null,
        eda: null,
      },
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
  // ✅ RUNTIME AUTHORITY: setRealmState persists to Runtime, Runtime is source of truth
  const setRealmState = useCallback(
    async (realm: "content" | "insights" | "journey" | "outcomes", key: string, value: any) => {
      // Update local state optimistically
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

      // ✅ RUNTIME AUTHORITY: Persist to Runtime (if session is active)
      if (sessionState.status === SessionStatus.Active && sessionState.sessionId && sessionState.tenantId) {
        try {
          // Store realm state in Runtime session state
          // Note: This would require a new API endpoint or extend existing session update
          // For now, we'll sync on next syncWithRuntime call
          // TODO: Add API endpoint to update realm state in session state
        } catch (error) {
          console.error(`Failed to persist realm state to Runtime: ${error}`);
          // Don't revert local state - let Runtime overwrite on next sync
        }
      }
    },
    [sessionState.status, sessionState.sessionId, sessionState.tenantId]
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

  // ✅ PHASE 5: Chatbot state actions (replaces Jotai atoms)
  const setMainChatbotOpen = useCallback((open: boolean) => {
    setState((prev) => ({
      ...prev,
      ui: {
        ...prev.ui,
        chatbot: { ...prev.ui.chatbot, mainChatbotOpen: open },
      },
    }));
  }, []);

  const setChatbotAgentInfo = useCallback((info: { title?: string; agent?: string; file_url?: string; additional_info?: string }) => {
    setState((prev) => ({
      ...prev,
      ui: {
        ...prev.ui,
        chatbot: {
          ...prev.ui.chatbot,
          agentInfo: { ...prev.ui.chatbot.agentInfo, ...info },
        },
      },
    }));
  }, []);

  const setChatInputFocused = useCallback((focused: boolean) => {
    setState((prev) => ({
      ...prev,
      ui: {
        ...prev.ui,
        chatbot: { ...prev.ui.chatbot, chatInputFocused: focused },
      },
    }));
  }, []);

  const setMessageComposing = useCallback((composing: boolean) => {
    setState((prev) => ({
      ...prev,
      ui: {
        ...prev.ui,
        chatbot: { ...prev.ui.chatbot, messageComposing: composing },
      },
    }));
  }, []);

  // ✅ PHASE 5: Analysis results actions (replaces Jotai atoms)
  const setAnalysisResult = useCallback((type: "business" | "visualization" | "anomaly" | "eda", result: any) => {
    setState((prev) => ({
      ...prev,
      ui: {
        ...prev.ui,
        analysisResults: { ...prev.ui.analysisResults, [type]: result },
      },
    }));
  }, []);

  const clearAnalysisResults = useCallback(() => {
    setState((prev) => ({
      ...prev,
      ui: {
        ...prev.ui,
        analysisResults: {
          business: null,
          visualization: null,
          anomaly: null,
          eda: null,
        },
      },
    }));
  }, []);

  // ✅ PHASE 5: Derived chatbot state (computed from mainChatbotOpen)
  const getShouldShowSecondaryChatbot = useCallback(() => {
    return !state.ui.chatbot.mainChatbotOpen;
  }, [state.ui.chatbot.mainChatbotOpen]);

  const getPrimaryChatbotHeight = useCallback(() => {
    return state.ui.chatbot.mainChatbotOpen ? 'h-[87vh]' : 'h-[30vh]';
  }, [state.ui.chatbot.mainChatbotOpen]);

  const getSecondaryChatbotPosition = useCallback(() => {
    return state.ui.chatbot.mainChatbotOpen
      ? 'translate-x-full opacity-0' // Hidden off-screen
      : 'translate-x-0 opacity-100'; // Visible at normal position
  }, [state.ui.chatbot.mainChatbotOpen]);

  const getPrimaryChatbotTransform = useCallback(() => {
    return state.ui.chatbot.mainChatbotOpen
      ? 'translate-y-0' // Normal position
      : 'translate-y-[20vh]'; // Slide down to make space for secondary
  }, [state.ui.chatbot.mainChatbotOpen]);

  // ✅ PHASE 5: Clear all state on session invalidation
  useEffect(() => {
    if (sessionState.status === SessionStatus.Invalid) {
      // Clear all platform state when session becomes invalid
      setState((prev) => ({
        ...prev,
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
          ...prev.ui,
          chatbot: {
            mainChatbotOpen: true, // Reset to default
            agentInfo: {
              title: "",
              agent: "",
              file_url: "",
              additional_info: "",
            },
            chatInputFocused: false,
            messageComposing: false,
          },
          analysisResults: {
            business: null,
            visualization: null,
            anomaly: null,
            eda: null,
          },
          notifications: [], // Clear notifications
        },
      }));
    }
  }, [sessionState.status]);

  // ✅ SESSION BOUNDARY PATTERN: Sync with Runtime - ONLY when session is Active
  // Sync follows session state - never leads it
  // ✅ SYNC MECHANISM: Hybrid (Event-driven push via WebSocket + Pull safety net)
  // - Primary: WebSocket provides real-time execution events (EXECUTION_STARTED, EXECUTION_COMPLETED, etc.)
  // - Safety Net: Pull every 30 seconds (catches missed events, syncs realm state)
  // - Not: Polling as primary mechanism
  const syncWithRuntime = useCallback(async () => {
    // Only sync when session is Active (authenticated and valid)
    if (sessionState.status !== SessionStatus.Active) {
      return;
    }
    
    if (!sessionState.sessionId || !sessionState.tenantId) {
      return;
    }

    try {
      // Sync active executions (only if we have a valid active session)
      for (const executionId of state.execution.activeExecutions) {
        await getExecutionStatus(executionId);
      }

      // ✅ RUNTIME AUTHORITY: Sync realm state from Runtime
      // Get session state from Runtime (includes realm state if stored there)
      try {
        const session = await client.getSession(sessionState.sessionId, sessionState.tenantId);
        
        // ✅ RUNTIME AUTHORITATIVE OVERWRITE: If Runtime has realm state, Runtime wins
        if (session.state && session.state.realm_state) {
          const runtimeRealmState = session.state.realm_state;
          
          // Check for divergence and reconcile
          setState((prev) => {
            let hasDivergence = false;
            const reconciledRealm: RealmState = { ...prev.realm };
            
            // For each realm, check if Runtime state differs
            for (const realm of ["content", "insights", "journey", "outcomes"] as const) {
              const runtimeState = runtimeRealmState[realm] || {};
              const localState = prev.realm[realm] || {};
              
              // Compare keys - if Runtime has different values, Runtime wins
              for (const key in runtimeState) {
                if (JSON.stringify(localState[key]) !== JSON.stringify(runtimeState[key])) {
                  hasDivergence = true;
                  reconciledRealm[realm] = {
                    ...localState,
                    ...runtimeState, // Runtime overwrites local
                  };
                }
              }
              
              // If Runtime has keys local doesn't have, add them
              for (const key in runtimeState) {
                if (!(key in localState)) {
                  hasDivergence = true;
                  reconciledRealm[realm] = {
                    ...localState,
                    ...runtimeState,
                  };
                }
              }
            }
            
            if (hasDivergence) {
              console.info("🔄 [PlatformState] Realm state diverged - Runtime overwrote local state");
              return {
                ...prev,
                realm: reconciledRealm,
              };
            }
            
            return prev; // No divergence, keep local state
          });
        }
      } catch (error) {
        // Session might not have realm_state yet, or API might not support it
        // This is OK - realm state sync is optional for now
        console.debug("Realm state sync not available:", error);
      }
    } catch (error) {
      console.error("Failed to sync with Runtime:", error);
      // Don't clear session state here - SessionBoundaryProvider handles that
    }
  }, [sessionState.status, sessionState.sessionId, sessionState.tenantId, state.execution.activeExecutions, getExecutionStatus, client]);

  // Periodic sync with Runtime (every 30 seconds) - ONLY if user is authenticated
  // ✅ SESSION-FIRST: Use SessionBoundaryProvider state to determine authentication
  // ✅ SESSION BOUNDARY PATTERN: Don't access sessionStorage directly - use SessionBoundaryProvider
  // Anonymous sessions exist but don't sync (no tenant_id/user_id)
  useEffect(() => {
    // ✅ SESSION BOUNDARY PATTERN: Check authentication via SessionBoundaryProvider state
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
    // ✅ PHASE 5: Chatbot state actions
    setMainChatbotOpen,
    setChatbotAgentInfo,
    setChatInputFocused,
    setMessageComposing,
    // ✅ PHASE 5: Analysis results actions
    setAnalysisResult,
    clearAnalysisResults,
    // ✅ PHASE 5: Derived chatbot state
    getShouldShowSecondaryChatbot,
    getPrimaryChatbotHeight,
    getSecondaryChatbotPosition,
    getPrimaryChatbotTransform,
    syncWithRuntime,
  };

  return (
    <PlatformStateContext.Provider value={contextValue}>
      {children}
    </PlatformStateContext.Provider>
  );
};
