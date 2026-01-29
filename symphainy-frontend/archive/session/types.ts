/**
 * Session Management Types
 * TypeScript interfaces and types for session management
 */

export interface SessionState {
  guideSessionToken: string | null;
  pillarStates: Record<string, any>;
}

export interface SessionActions {
  setGuideSessionToken: (token: string) => Promise<void>;
  getPillarState: (pillar: string) => any;
  setPillarState: (pillar: string, state: any) => Promise<void>;
  resetAllState: () => Promise<void>;
  startNewSession: () => Promise<string>;
}

export interface SessionContextType {
  guideSessionToken: string | null;
  setGuideSessionToken: (token: string) => Promise<void>;
  getPillarState: (pillar: string) => any;
  setPillarState: (pillar: string, state: any) => Promise<void>;
  resetAllState: () => Promise<void>;
  sessionStatus: SessionStatus;
  isSessionValid: boolean;
}

export type SessionStatus = 
  | 'no_session'
  | 'creating'
  | 'active'
  | 'validating'
  | 'error'
  | 'expired';

export interface PillarState {
  [key: string]: any;
}

export interface SessionData {
  sessionToken: string;
  createdAt: string;
  lastAccessed: string;
  pillarStates: Record<string, PillarState>;
  metadata: SessionMetadata;
}

export interface SessionMetadata {
  userAgent?: string;
  ipAddress?: string;
  deviceType?: string;
  sessionDuration?: number;
}

// Smart City specific types
export interface SmartCitySessionData extends SessionData {
  trafficCopId?: string;
  archiveId?: string;
  conductorId?: string;
  workflowStatus?: string;
}

export interface SessionValidationResult {
  isValid: boolean;
  reason?: string;
  sessionData?: SmartCitySessionData;
}

export interface SessionCreationOptions {
  metadata?: SessionMetadata;
  initialPillarStates?: Record<string, PillarState>;
  smartCityIntegration?: boolean;
} 