/**
 * Session Validation Utility
 * 
 * ✅ FIX ISSUE 4: Standardized session validation helper
 * 
 * Provides consistent session validation across all API managers.
 */

import { usePlatformState } from "@/shared/state/PlatformStateProvider";

/**
 * Validate session for an operation
 * 
 * @param platformState - Platform state from usePlatformState
 * @param operation - Operation name for error message
 * @throws Error if session is invalid
 */
export function validateSession(
  platformState: ReturnType<typeof usePlatformState>,
  operation: string
): void {
  if (!platformState.state.session.sessionId || !platformState.state.session.tenantId) {
    throw new Error(`Session required for ${operation}`);
  }
}

/**
 * Get session validation helper for API managers
 * 
 * @param getPlatformState - Function to get platform state
 * @returns Validation function
 */
export function createSessionValidator(
  getPlatformState: () => ReturnType<typeof usePlatformState>
) {
  return (operation: string): void => {
    const platformState = getPlatformState();
    validateSession(platformState, operation);
  };
}
