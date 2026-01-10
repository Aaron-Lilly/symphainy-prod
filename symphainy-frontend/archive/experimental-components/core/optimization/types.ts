/**
 * Optimization Types
 * Type definitions for component optimization
 */

export interface OptimizationConfig {
  enableMemoization: boolean;
  enableCallbackOptimization: boolean;
  enableRefOptimization: boolean;
  enableTransitionOptimization: boolean;
  enableVirtualization: boolean;
  memoizationDepth: number;
}

export interface VirtualizationConfig {
  itemHeight: number;
  containerHeight: number;
  overscan: number;
  enableDynamicHeight: boolean;
} 