/**
 * AGUI State Provider
 * 
 * ✅ PHASE 2.5: AGUI Native Integration
 * 
 * Single source of truth for AGUI state (experience layer state).
 * 
 * Architecture Principles:
 * 1. AGUI state is session-scoped (cleared on session invalidation)
 * 2. AGUI state compiles to Intent (frontend compilation)
 * 3. AGUI state is experience semantics, not execution semantics
 * 4. AGUI state follows session lifecycle
 * 
 * Integration:
 * - Integrates with SessionBoundaryProvider (session-scoped)
 * - AGUI state stored in session state
 * - AGUI state cleared when session becomes Invalid
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
import { useSessionBoundary, SessionStatus } from "./SessionBoundaryProvider";
import {
  AGUIState,
  AGUIMutation,
  AGUIValidationError,
  JourneyStep,
  Artifact,
  Workflow,
  JourneyStepStatus,
} from "@/shared/types/agui";

// ============================================================================
// CONTEXT INTERFACE
// ============================================================================

interface AGUIStateContextType {
  // State
  state: AGUIState | null;
  isValid: boolean;
  validationErrors: AGUIValidationError[];
  
  // Actions
  updateState: (mutation: AGUIMutation) => void;
  setJourney: (journey: AGUIState["journey"]) => void;
  setCurrentStep: (stepId: string) => void;
  addArtifact: (artifact: Artifact, location: "inputs" | "outputs") => void;
  updateArtifact: (id: string, updates: Partial<Artifact>, location: "inputs" | "outputs") => void;
  removeArtifact: (id: string, location: "inputs" | "outputs") => void;
  addWorkflow: (workflow: Workflow) => void;
  updateWorkflow: (id: string, updates: Partial<Workflow>) => void;
  removeWorkflow: (id: string) => void;
  clearState: () => void;
  
  // Validation
  validate: () => AGUIValidationError[];
}

const AGUIStateContext = createContext<AGUIStateContextType | undefined>(undefined);

// ============================================================================
// HOOK
// ============================================================================

export const useAGUIState = (): AGUIStateContextType => {
  const context = useContext(AGUIStateContext);
  
  // SSR-safe: Return a safe default during prerendering
  if (context === undefined) {
    if (typeof window === 'undefined') {
      // Server-side: Return a minimal safe default
      return {
        state: null,
        isValid: false,
        validationErrors: [],
        updateState: () => {},
        setJourney: () => {},
        setCurrentStep: () => {},
        addArtifact: () => {},
        updateArtifact: () => {},
        removeArtifact: () => {},
        addWorkflow: () => {},
        updateWorkflow: () => {},
        removeWorkflow: () => {},
        clearState: () => {},
        validate: () => [],
      };
    }
    // Client-side: This is a real error
    throw new Error("useAGUIState must be used within AGUIStateProvider");
  }
  return context;
};

// ============================================================================
// PROVIDER
// ============================================================================

interface AGUIStateProviderProps {
  children: React.ReactNode;
}

export const AGUIStateProvider: React.FC<AGUIStateProviderProps> = ({ children }) => {
  const { state: sessionState } = useSessionBoundary();
  const [aguiState, setAguiState] = useState<AGUIState | null>(null);
  const [validationErrors, setValidationErrors] = useState<AGUIValidationError[]>([]);
  const isInitializedRef = useRef(false);

  // ✅ SESSION-SCOPED: Clear AGUI state when session becomes Invalid
  useEffect(() => {
    if (sessionState.status === SessionStatus.Invalid) {
      setAguiState(null);
      setValidationErrors([]);
      isInitializedRef.current = false;
    }
  }, [sessionState.status]);

  // ✅ SESSION-SCOPED: Initialize AGUI state when session becomes Active
  useEffect(() => {
    if (sessionState.status === SessionStatus.Active && sessionState.sessionId && !isInitializedRef.current) {
      // Initialize empty AGUI state for new session
      const initialState: AGUIState = {
        journey: {
          id: `journey_${Date.now()}`,
          name: "New Journey",
          current_step: "",
          steps: [],
        },
        inputs: {
          artifacts: [],
          parameters: {},
        },
        workflows: [],
        outputs: {
          artifacts: [],
          results: {},
        },
        metadata: {
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          session_id: sessionState.sessionId,
          tenant_id: sessionState.tenantId || undefined,
          user_id: sessionState.userId || undefined,
        },
      };
      setAguiState(initialState);
      isInitializedRef.current = true;
    }
  }, [sessionState.status, sessionState.sessionId, sessionState.tenantId, sessionState.userId]);

  // ✅ SESSION-SCOPED: Update metadata when session changes
  useEffect(() => {
    if (aguiState && sessionState.sessionId) {
      setAguiState(prev => prev ? {
        ...prev,
        metadata: {
          ...prev.metadata,
          session_id: sessionState.sessionId!,
          tenant_id: sessionState.tenantId || undefined,
          user_id: sessionState.userId || undefined,
          updated_at: new Date().toISOString(),
        },
      } : null);
    }
  }, [sessionState.sessionId, sessionState.tenantId, sessionState.userId, aguiState]);

  // Validation function
  const validate = useCallback((): AGUIValidationError[] => {
    if (!aguiState) {
      return [{ field: "state", message: "AGUI state is not initialized" }];
    }

    const errors: AGUIValidationError[] = [];

    // Validate journey
    if (!aguiState.journey.id) {
      errors.push({ field: "journey.id", message: "Journey ID is required" });
    }
    if (aguiState.journey.current_step && !aguiState.journey.steps.find(s => s.id === aguiState.journey.current_step)) {
      errors.push({ field: "journey.current_step", message: `Current step "${aguiState.journey.current_step}" not found in steps` });
    }

    // Validate current step requirements
    const currentStep = aguiState.journey.steps.find(s => s.id === aguiState.journey.current_step);
    if (currentStep?.required_artifacts) {
      for (const requiredId of currentStep.required_artifacts) {
        const hasArtifact = aguiState.inputs.artifacts.some(a => a.id === requiredId) ||
                          aguiState.outputs.artifacts.some(a => a.id === requiredId);
        if (!hasArtifact) {
          errors.push({ field: "journey.required_artifacts", message: `Required artifact "${requiredId}" not found` });
        }
      }
    }

    return errors;
  }, [aguiState]);

  // Update validation errors when state changes
  useEffect(() => {
    if (aguiState) {
      const errors = validate();
      setValidationErrors(errors);
    }
  }, [aguiState, validate]);

  // Update state with mutation
  const updateState = useCallback((mutation: AGUIMutation) => {
    setAguiState(prev => {
      if (!prev) return prev;

      const updated: AGUIState = { ...prev };

      // Apply journey mutations
      if (mutation.journey) {
        if (mutation.journey.set_step) {
          updated.journey.current_step = mutation.journey.set_step;
        }
        if (mutation.journey.add_step) {
          updated.journey.steps = [...updated.journey.steps, mutation.journey.add_step];
        }
        if (mutation.journey.update_step) {
          updated.journey.steps = updated.journey.steps.map(s =>
            s.id === mutation.journey!.update_step!.id
              ? { ...s, ...mutation.journey!.update_step!.updates }
              : s
          );
        }
        if (mutation.journey.remove_step) {
          updated.journey.steps = updated.journey.steps.filter(s => s.id !== mutation.journey!.remove_step);
          if (updated.journey.current_step === mutation.journey.remove_step) {
            updated.journey.current_step = "";
          }
        }
      }

      // Apply input mutations
      if (mutation.inputs) {
        if (mutation.inputs.add_artifact) {
          updated.inputs.artifacts = [...updated.inputs.artifacts, mutation.inputs.add_artifact];
        }
        if (mutation.inputs.update_artifact) {
          updated.inputs.artifacts = updated.inputs.artifacts.map(a =>
            a.id === mutation.inputs!.update_artifact!.id
              ? { ...a, ...mutation.inputs!.update_artifact!.updates }
              : a
          );
        }
        if (mutation.inputs.remove_artifact) {
          updated.inputs.artifacts = updated.inputs.artifacts.filter(a => a.id !== mutation.inputs!.remove_artifact);
        }
        if (mutation.inputs.set_parameter) {
          updated.inputs.parameters = {
            ...updated.inputs.parameters,
            [mutation.inputs.set_parameter.key]: mutation.inputs.set_parameter.value,
          };
        }
        if (mutation.inputs.remove_parameter) {
          const { [mutation.inputs.remove_parameter]: _, ...rest } = updated.inputs.parameters;
          updated.inputs.parameters = rest;
        }
      }

      // Apply workflow mutations
      if (mutation.workflows) {
        if (mutation.workflows.add_workflow) {
          updated.workflows = [...updated.workflows, mutation.workflows.add_workflow];
        }
        if (mutation.workflows.update_workflow) {
          updated.workflows = updated.workflows.map(w =>
            w.id === mutation.workflows!.update_workflow!.id
              ? { ...w, ...mutation.workflows!.update_workflow!.updates }
              : w
          );
        }
        if (mutation.workflows.remove_workflow) {
          updated.workflows = updated.workflows.filter(w => w.id !== mutation.workflows!.remove_workflow);
        }
      }

      // Apply output mutations
      if (mutation.outputs) {
        if (mutation.outputs.add_artifact) {
          updated.outputs.artifacts = [...updated.outputs.artifacts, mutation.outputs.add_artifact];
        }
        if (mutation.outputs.update_artifact) {
          updated.outputs.artifacts = updated.outputs.artifacts.map(a =>
            a.id === mutation.outputs!.update_artifact!.id
              ? { ...a, ...mutation.outputs!.update_artifact!.updates }
              : a
          );
        }
        if (mutation.outputs.remove_artifact) {
          updated.outputs.artifacts = updated.outputs.artifacts.filter(a => a.id !== mutation.outputs!.remove_artifact);
        }
        if (mutation.outputs.set_result) {
          updated.outputs.results = {
            ...updated.outputs.results,
            [mutation.outputs.set_result.key]: mutation.outputs.set_result.value,
          };
        }
        if (mutation.outputs.remove_result) {
          const { [mutation.outputs.remove_result]: _, ...rest } = updated.outputs.results;
          updated.outputs.results = rest;
        }
      }

      // Apply metadata mutations
      if (mutation.metadata?.update) {
        updated.metadata = {
          ...updated.metadata,
          ...mutation.metadata.update,
          updated_at: new Date().toISOString(),
        };
      }

      // Always update timestamp
      updated.metadata.updated_at = new Date().toISOString();

      return updated;
    });
  }, []);

  // Convenience methods
  const setJourney = useCallback((journey: AGUIState["journey"]) => {
    updateState({ journey: { set_step: journey.current_step } });
    // Note: Full journey replacement would need more mutation support
  }, [updateState]);

  const setCurrentStep = useCallback((stepId: string) => {
    updateState({ journey: { set_step: stepId } });
  }, [updateState]);

  const addArtifact = useCallback((artifact: Artifact, location: "inputs" | "outputs") => {
    updateState({
      [location]: { add_artifact: artifact },
    } as AGUIMutation);
  }, [updateState]);

  const updateArtifact = useCallback((id: string, updates: Partial<Artifact>, location: "inputs" | "outputs") => {
    updateState({
      [location]: { update_artifact: { id, updates } },
    } as AGUIMutation);
  }, [updateState]);

  const removeArtifact = useCallback((id: string, location: "inputs" | "outputs") => {
    updateState({
      [location]: { remove_artifact: id },
    } as AGUIMutation);
  }, [updateState]);

  const addWorkflow = useCallback((workflow: Workflow) => {
    updateState({ workflows: { add_workflow: workflow } });
  }, [updateState]);

  const updateWorkflow = useCallback((id: string, updates: Partial<Workflow>) => {
    updateState({ workflows: { update_workflow: { id, updates } } });
  }, [updateState]);

  const removeWorkflow = useCallback((id: string) => {
    updateState({ workflows: { remove_workflow: id } });
  }, [updateState]);

  const clearState = useCallback(() => {
    setAguiState(null);
    setValidationErrors([]);
    isInitializedRef.current = false;
  }, []);

  const contextValue: AGUIStateContextType = {
    state: aguiState,
    isValid: validationErrors.length === 0,
    validationErrors,
    updateState,
    setJourney,
    setCurrentStep,
    addArtifact,
    updateArtifact,
    removeArtifact,
    addWorkflow,
    updateWorkflow,
    removeWorkflow,
    clearState,
    validate,
  };

  return (
    <AGUIStateContext.Provider value={contextValue}>
      {children}
    </AGUIStateContext.Provider>
  );
};
