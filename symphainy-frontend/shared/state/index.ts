/**
 * Enhanced State Management Orchestrator
 * Provides unified access to all state management functionality
 */

// Export core functionality
export { EnhancedStateManager } from './enhanced_core';
export type { 
  StateNode, 
  StateChange, 
  StateConfig 
} from './enhanced_core';

// Export persistence
export { StatePersistence } from './persistence';
export type { 
  PersistenceConfig, 
  StorageStats 
} from './persistence';

// Export synchronization
export { StateSynchronizer } from './sync';
export type { 
  SyncConfig, 
  SyncStatus 
} from './sync';

// Export hooks
export {
  useEnhancedState,
  useStateSync,
  useStatePersistence
} from './hooks';

// Export enhanced state provider
export { EnhancedStateProvider } from './EnhancedStateProvider'; 