/**
 * useJourneyStep Hook
 * 
 * ✅ PHASE 2.5: AGUI Native Integration
 * 
 * Returns the current journey step from AGUI state.
 * 
 * Usage:
 * ```tsx
 * const currentStep = useJourneyStep();
 * if (currentStep?.id === "parse_file") { ... }
 * ```
 */

"use client";

import { useAGUIState } from '../state/AGUIStateProvider';
import { JourneyStep } from '@/shared/types/agui';

export function useJourneyStep(): JourneyStep | null {
  const { state } = useAGUIState();
  
  if (!state || !state.journey.current_step) {
    return null;
  }
  
  return state.journey.steps.find(s => s.id === state.journey.current_step) || null;
}
