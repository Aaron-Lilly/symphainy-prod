/**
 * useServiceLayerAPI Hook
 * 
 * ✅ PHASE 2: React hook that provides ServiceLayerAPI functions
 * with automatic session token management from SessionBoundaryProvider
 * 
 * Usage:
 * ```tsx
 * const { loginUser, sendAgentEvent, submitIntent } = useServiceLayerAPI();
 * await loginUser({ email, password });
 * ```
 */

"use client";

import { useCallback } from 'react';
import { useSessionBoundary } from '../state/SessionBoundaryProvider';
import { useAGUIState } from '../state/AGUIStateProvider';
import * as ServiceLayerAPI from '../services/ServiceLayerAPI';
import { AGUIMutation, AGUIState, IntentCompilationResult } from '@/shared/types/agui';

export function useServiceLayerAPI() {
  const { state: sessionState } = useSessionBoundary();
  
  // ✅ PHASE 2.5: Get AGUI state for compilation
  const { state: aguiState, updateState } = useAGUIState();
  
  // Get service layer config from SessionBoundaryProvider
  const getConfig = (): ServiceLayerAPI.ServiceLayerAPIConfig => ({
    sessionId: sessionState.sessionId,
    accessToken: typeof window !== 'undefined' ? sessionStorage.getItem('access_token') : null,
    tenantId: sessionState.tenantId,
    userId: sessionState.userId,
  });

  // ✅ PHASE 2.5: AGUI mutation function (uses AGUIStateProvider)
  const updateAGUI = useCallback((mutation: AGUIMutation) => {
    updateState(mutation);
  }, [updateState]);

  // ✅ PHASE 2.5: Compile AGUI → Intent (frontend compilation)
  const compileIntentFromAGUI = useCallback((
    state?: AGUIState,
    intentType?: string
  ): IntentCompilationResult => {
    // SSR-safe: Return empty result during SSR
    if (typeof window === 'undefined') {
      return {
        intent_type: intentType || "unknown",
        parameters: {},
        validation_errors: ["AGUI compilation not available during SSR"],
      };
    }
    const stateToCompile = state || aguiState;
    if (!stateToCompile) {
      throw new Error("AGUI state is required for intent compilation");
    }
    return ServiceLayerAPI.compileIntentFromAGUI(stateToCompile, intentType);
  }, [aguiState]);

  // ✅ PHASE 2.5: Submit Intent from AGUI state
  const submitIntentFromAGUI = useCallback(async (
    state?: AGUIState,
    intentType?: string
  ) => {
    // SSR-safe: Throw error during SSR (shouldn't be called during SSR anyway)
    if (typeof window === 'undefined') {
      throw new Error("submitIntentFromAGUI cannot be called during SSR");
    }
    const stateToCompile = state || aguiState;
    if (!stateToCompile) {
      throw new Error("AGUI state is required for intent submission");
    }
    return ServiceLayerAPI.submitIntentFromAGUI(stateToCompile, intentType, getConfig());
  }, [aguiState, getConfig]);

  // Wrap ServiceLayerAPI functions with automatic config injection
  return {
    // Authentication
    loginUser: ServiceLayerAPI.loginUser,
    registerUser: ServiceLayerAPI.registerUser,
    
    // Validation utilities (client-side)
    validateEmail: ServiceLayerAPI.validateEmail,
    validatePassword: ServiceLayerAPI.validatePassword,
    validateName: ServiceLayerAPI.validateName,
    
    // Agent
    sendAgentEvent: (event: ServiceLayerAPI.AgentEvent) => 
      ServiceLayerAPI.sendAgentEvent(event, getConfig()),
    
    // Intent & Execution
    submitIntent: (
      intentType: string,
      parameters?: Record<string, any>,
      metadata?: Record<string, any>
    ) => ServiceLayerAPI.submitIntent(intentType, parameters, metadata, getConfig()),
    
    getExecutionStatus: (executionId: string) =>
      ServiceLayerAPI.getExecutionStatus(executionId, getConfig()),
    
    // Session (should only be used by SessionBoundaryProvider)
    createAnonymousSession: ServiceLayerAPI.createAnonymousSession,
    getSession: ServiceLayerAPI.getSession,
    upgradeSession: ServiceLayerAPI.upgradeSession,
    
    // ✅ PHASE 2.5: AGUI functions (native platform language)
    updateAGUI,
    compileIntentFromAGUI,
    submitIntentFromAGUI,
  };
}
