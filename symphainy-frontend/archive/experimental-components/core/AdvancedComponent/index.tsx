/**
 * Advanced Component Orchestrator
 * Unified access point for advanced component functionality
 */

// Types
export type {
  ComponentConfig,
  ComponentState,
  PerformanceMetrics
} from './types';

// Core component
export { AdvancedComponent } from './core';

// Error boundary
export { AdvancedErrorBoundary } from './error-boundary';

// Performance features
export {
  usePerformanceMonitoring,
  useLazyLoading,
  useCaching,
  useMemoization,
  withAdvancedFeatures
} from './performance'; 