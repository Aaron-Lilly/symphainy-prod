/**
 * useAGUIMutation Hook
 * 
 * ✅ PHASE 2.5: AGUI Native Integration
 * 
 * Provides convenient methods for mutating AGUI state.
 * 
 * Usage:
 * ```tsx
 * const { updateState, addArtifact, setCurrentStep } = useAGUIMutation();
 * await addArtifact(newArtifact, "inputs");
 * await setCurrentStep("next_step");
 * ```
 */

"use client";

import { useCallback } from 'react';
import { useAGUIState } from '../state/AGUIStateProvider';
import { AGUIMutation, Artifact, Workflow } from '@/shared/types/agui';

export function useAGUIMutation() {
  const {
    updateState,
    setCurrentStep,
    addArtifact,
    updateArtifact,
    removeArtifact,
    addWorkflow,
    updateWorkflow,
    removeWorkflow,
  } = useAGUIState();

  // Convenience wrapper that returns mutation for chaining
  const mutate = useCallback((mutation: AGUIMutation) => {
    updateState(mutation);
  }, [updateState]);

  return {
    // Direct mutation
    mutate,
    updateState,
    
    // Journey mutations
    setCurrentStep,
    
    // Artifact mutations
    addArtifact,
    updateArtifact,
    removeArtifact,
    
    // Workflow mutations
    addWorkflow,
    updateWorkflow,
    removeWorkflow,
  };
}
