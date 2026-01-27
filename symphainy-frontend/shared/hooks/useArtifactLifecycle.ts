/**
 * useArtifactLifecycle Hook
 * 
 * ✅ PHASE 5.3: Purpose-Bound Outcomes Lifecycle Management
 * 
 * Provides lifecycle management for artifacts:
 * - Transition lifecycle states
 * - Validate transitions
 * - Ensure Runtime authority (transitions go through Runtime)
 */

import { useCallback } from 'react';
import { usePlatformState } from '@/shared/state/PlatformStateProvider';
import { 
  LifecycleState, 
  validateLifecycleTransition, 
  transitionArtifactLifecycle 
} from '@/shared/services/artifactLifecycle';

interface UseArtifactLifecycleOptions {
  realm: 'outcomes' | 'journey';
  artifactType: 'blueprint' | 'poc' | 'roadmap' | 'sop' | 'workflow';
  artifactId: string;
}

/**
 * ✅ PHASE 5.3: Hook for artifact lifecycle management
 * 
 * Testable Guarantees:
 * - Authority: Runtime enforces transitions (via intent)
 * - Visibility: Lifecycle state visible in UI
 * - Persistence: Lifecycle survives reload (via Runtime state)
 */
export function useArtifactLifecycle({ realm, artifactType, artifactId }: UseArtifactLifecycleOptions) {
  const { state, submitIntent, getExecutionStatus } = usePlatformState();

  /**
   * ✅ PHASE 5.3: Transition artifact lifecycle state
   * 
   * Testable Guarantee: Runtime enforces transitions
   * - Frontend validates transition is allowed
   * - Runtime enforces via intent (transition_artifact_lifecycle)
   */
  const transitionLifecycle = useCallback(async (
    targetState: LifecycleState,
    reason?: string
  ): Promise<{ success: boolean; error?: string }> => {
    try {
      // Get current artifact from realm state
      const realmStateKey = artifactType === 'blueprint' ? 'blueprints' :
                           artifactType === 'poc' ? 'pocProposals' :
                           artifactType === 'roadmap' ? 'roadmaps' :
                           'artifacts';
      
      const artifacts = state.realm[realm][realmStateKey] || {};
      const artifact = artifacts[artifactId];
      
      if (!artifact) {
        return { success: false, error: 'Artifact not found' };
      }

      // Validate transition (frontend validation)
      const validation = validateLifecycleTransition(
        artifact.lifecycle_state || 'draft',
        targetState
      );

      if (!validation.valid) {
        return { success: false, error: validation.error };
      }

      // ✅ PHASE 5.3: Runtime enforces transition via intent
      // Submit transition intent to Runtime
      const execution = await submitIntent(
        'transition_artifact_lifecycle',
        {
          artifact_id: artifactId,
          artifact_type: artifactType,
          current_state: artifact.lifecycle_state || 'draft',
          target_state: targetState,
          reason
        }
      );

      // Wait for execution (Runtime validates and enforces)
      // TODO: Implement execution waiting logic
      
      return { success: true };
    } catch (error) {
      console.error('[useArtifactLifecycle] Error transitioning lifecycle:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to transition lifecycle'
      };
    }
  }, [realm, artifactType, artifactId, state, submitIntent, getExecutionStatus]);

  /**
   * Get current lifecycle state
   */
  const getLifecycleState = useCallback((): LifecycleState | null => {
    const realmStateKey = artifactType === 'blueprint' ? 'blueprints' :
                         artifactType === 'poc' ? 'pocProposals' :
                         artifactType === 'roadmap' ? 'roadmaps' :
                         'artifacts';
    
    const artifacts = state.realm[realm][realmStateKey] || {};
    const artifact = artifacts[artifactId];
    
    return artifact?.lifecycle_state || artifact?.status || null;
  }, [realm, artifactType, artifactId, state]);

  return {
    transitionLifecycle,
    getLifecycleState,
    currentState: getLifecycleState()
  };
}
