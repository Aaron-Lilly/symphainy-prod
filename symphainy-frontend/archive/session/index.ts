/**
 * Session Management Orchestrator
 * Provides unified access to all session management functionality
 */

// Export core functionality
export { SessionManager } from './core';
export type { SessionState, SessionActions } from './core';

// Export Smart City integration
export { SmartCitySessionIntegration } from './smart_city_integration';
export type { 
  TrafficCop, 
  Archive, 
  Conductor 
} from './smart_city_integration';

// Export types
export type {
  SessionContextType,
  SessionStatus,
  PillarState,
  SessionData,
  SessionMetadata,
  SmartCitySessionData,
  SessionValidationResult,
  SessionCreationOptions
} from './types';

// Export hooks
export {
  useSessionStatus,
  usePillarState,
  useSessionLifecycle
} from './hooks';

export {
  useSessionPersistence,
  useSmartCitySession
} from './hooks_persistence';

// ✅ PHASE 1: GlobalSessionProvider archived - use SessionBoundaryProvider instead
// export { GlobalSessionProvider, useGlobalSession } from './GlobalSessionProvider';
// Migration: Use SessionBoundaryProvider from '@/shared/state/SessionBoundaryProvider' 