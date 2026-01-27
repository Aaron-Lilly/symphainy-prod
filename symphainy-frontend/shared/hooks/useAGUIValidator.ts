/**
 * useAGUIValidator Hook
 * 
 * ✅ PHASE 2.5: AGUI Native Integration
 * 
 * Validates AGUI state and returns validation errors.
 * 
 * Usage:
 * ```tsx
 * const { isValid, errors } = useAGUIValidator();
 * if (!isValid) { console.error(errors); }
 * ```
 */

"use client";

import { useAGUIState } from '../state/AGUIStateProvider';
import { AGUIValidationError } from '@/shared/types/agui';

export function useAGUIValidator(): {
  isValid: boolean;
  errors: AGUIValidationError[];
  validate: () => AGUIValidationError[];
} {
  const { state, isValid, validationErrors, validate } = useAGUIState();
  
  return {
    isValid: state !== null && isValid,
    errors: validationErrors,
    validate,
  };
}
