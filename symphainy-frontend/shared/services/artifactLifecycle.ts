/**
 * Artifact Lifecycle Management
 * 
 * ✅ PHASE 5.3: Purpose-Bound Outcomes Lifecycle
 * 
 * Manages artifact lifecycle states and transitions:
 * - Creation: Artifact has purpose, scope, owner
 * - Transition: Only valid transitions allowed
 * - Visibility: Lifecycle state visible in UI
 * - Authority: Runtime enforces transitions
 * - Persistence: Lifecycle survives reload
 */

export type LifecycleState = 'draft' | 'active' | 'archived';

export interface ArtifactLifecycle {
  lifecycle_state: LifecycleState;
  status?: LifecycleState; // For UI compatibility
  purpose: string;
  scope: string;
  owner: string;
  createdAt: string;
  updatedAt?: string;
  transitionHistory?: Array<{
    from: LifecycleState;
    to: LifecycleState;
    timestamp: string;
    reason?: string;
  }>;
}

/**
 * Valid lifecycle state transitions
 */
const VALID_TRANSITIONS: Record<LifecycleState, LifecycleState[]> = {
  draft: ['active', 'archived'],
  active: ['archived'],
  archived: [], // Archived is terminal
};

/**
 * ✅ PHASE 5.3: Validate lifecycle state transition
 * 
 * Testable Guarantee: Only valid transitions allowed
 */
export function validateLifecycleTransition(
  currentState: LifecycleState,
  targetState: LifecycleState
): { valid: boolean; error?: string } {
  const allowedTransitions = VALID_TRANSITIONS[currentState];
  
  if (!allowedTransitions.includes(targetState)) {
    return {
      valid: false,
      error: `Invalid transition from ${currentState} to ${targetState}. Allowed transitions: ${allowedTransitions.join(', ')}`
    };
  }
  
  return { valid: true };
}

/**
 * ✅ PHASE 5.3: Create artifact with lifecycle
 * 
 * Testable Guarantee: Artifact has purpose, scope, owner
 */
export function createArtifactWithLifecycle(
  artifactData: any,
  purpose: string,
  scope: string,
  owner: string
): ArtifactLifecycle & { artifact: any } {
  return {
    ...artifactData,
    lifecycle_state: 'draft',
    status: 'draft', // For UI compatibility
    purpose,
    scope,
    owner,
    createdAt: new Date().toISOString(),
    transitionHistory: [{
      from: 'draft',
      to: 'draft',
      timestamp: new Date().toISOString(),
      reason: 'Initial creation'
    }]
  };
}

/**
 * ✅ PHASE 5.3: Transition artifact lifecycle state
 * 
 * Testable Guarantee: Runtime enforces transitions (this is a frontend helper,
 * actual enforcement happens in Runtime via intent)
 */
export function transitionArtifactLifecycle(
  artifact: ArtifactLifecycle,
  targetState: LifecycleState,
  reason?: string
): { success: boolean; artifact?: ArtifactLifecycle; error?: string } {
  const validation = validateLifecycleTransition(artifact.lifecycle_state, targetState);
  
  if (!validation.valid) {
    return {
      success: false,
      error: validation.error
    };
  }
  
  const transitionHistory = artifact.transitionHistory || [];
  transitionHistory.push({
    from: artifact.lifecycle_state,
    to: targetState,
    timestamp: new Date().toISOString(),
    reason
  });
  
  return {
    success: true,
    artifact: {
      ...artifact,
      lifecycle_state: targetState,
      status: targetState, // For UI compatibility
      updatedAt: new Date().toISOString(),
      transitionHistory
    }
  };
}

/**
 * ✅ PHASE 5.3: Ensure artifact has lifecycle (helper for artifact creation)
 */
export function ensureArtifactLifecycle(
  artifact: any,
  defaultPurpose: string,
  defaultScope: string,
  owner: string
): ArtifactLifecycle & { artifact: any } {
  // If artifact already has lifecycle, return as-is
  if (artifact.lifecycle_state && artifact.purpose && artifact.scope && artifact.owner) {
    return artifact;
  }
  
  // Otherwise, create lifecycle
  return createArtifactWithLifecycle(
    artifact,
    artifact.purpose || defaultPurpose,
    artifact.scope || defaultScope,
    artifact.owner || owner
  );
}
