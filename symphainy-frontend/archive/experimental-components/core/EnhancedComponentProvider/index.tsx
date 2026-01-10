/**
 * Enhanced Component Provider Orchestrator
 * Unified access point for enhanced component functionality
 */

// Core provider and context
export { 
  EnhancedComponentProvider, 
  useEnhancedComponentContext 
} from './core';

// Context types
export type { 
  EnhancedComponentContextValue, 
  EnhancedComponentProviderProps 
} from './context';

// Composition hooks and utilities
export {
  useContextComposition,
  useRenderProps,
  useCompoundComponent,
  createHOC,
  useComponentComposition,
  createContextProvider,
  useComponentRegistry
} from './composition-hooks'; 