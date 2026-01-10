/**
 * Lifecycle Orchestrator
 * Unified access point for lifecycle functionality
 */

// Types
export type {
  LifecycleState,
  LifecycleConfig,
  LifecycleEvents
} from './types';

// Core lifecycle hooks
export {
  useLifecycle,
  useComponentMount,
  useComponentVisibility,
  useComponentActivity
} from './core';

// Enhancement features
export {
  AdvancedErrorBoundary,
  usePerformanceMonitoring,
  useLazyLoading,
  useCaching,
  useDeepMemo,
  useOptimizedCallback,
  useVirtualization,
  useRenderOptimization
} from './enhancement'; 