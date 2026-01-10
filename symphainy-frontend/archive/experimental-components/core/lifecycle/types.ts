/**
 * Lifecycle Types
 * Type definitions for component lifecycle management
 */

export interface LifecycleState {
  isMounted: boolean;
  isVisible: boolean;
  isActive: boolean;
  mountTime: number;
  lastActivity: number;
  renderCount: number;
}

export interface LifecycleConfig {
  enableVisibilityTracking: boolean;
  enableActivityTracking: boolean;
  enableAutoCleanup: boolean;
  cleanupTimeout: number;
  visibilityThreshold: number;
}

export interface LifecycleEvents {
  onMount?: () => void;
  onUnmount?: () => void;
  onVisibilityChange?: (isVisible: boolean) => void;
  onActivityChange?: (isActive: boolean) => void;
  onCleanup?: () => void;
} 