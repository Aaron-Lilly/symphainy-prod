/**
 * Service Layer API
 * 
 * ✅ PHASE 2: Unified API interface for all service layer calls
 * 
 * This module provides a single entry point for all API calls through the service layer.
 * All components should use these functions instead of direct fetch/axios calls.
 * 
 * Architecture:
 * - Uses SessionBoundaryProvider for session tokens
 * - Uses ExperiencePlaneClient for Experience Plane API calls
 * - Consistent error handling
 * - All calls go through service layer
 */

"use client";

import { ExperiencePlaneClient } from './ExperiencePlaneClient';
import { getApiUrl, getApiEndpointUrl } from '@/shared/config/api-config';

// ============================================
// Service Layer API Interface
// ============================================

export interface ServiceLayerAPIConfig {
  sessionId?: string | null;
  accessToken?: string | null;
  tenantId?: string | null;
  userId?: string | null;
}

/**
 * Get ExperiencePlaneClient instance
 * 
 * Note: This should eventually get session tokens from SessionBoundaryProvider
 * For now, it accepts them as parameters to avoid circular dependencies
 */
function getExperiencePlaneClient(): ExperiencePlaneClient {
  return new ExperiencePlaneClient();
}

// ============================================
// Session API
// ============================================

/**
 * Create anonymous session
 * 
 * ✅ PHASE 2: Should only be called by SessionBoundaryProvider
 * Components should NOT call this directly
 */
export async function createAnonymousSession(): Promise<{
  session_id: string;
  tenant_id?: string | null;
  user_id?: string | null;
  created_at?: string;
}> {
  const client = getExperiencePlaneClient();
  return client.createSession({
    tenant_id: '', // Anonymous session
    user_id: '', // Anonymous session
  });
}

/**
 * Get session by ID
 * 
 * ✅ PHASE 2: Should only be called by SessionBoundaryProvider
 * Components should NOT call this directly
 */
export async function getSession(
  sessionId: string,
  tenantId?: string
): Promise<{
  session_id: string;
  tenant_id: string | null;
  user_id: string | null;
  created_at: string;
  metadata?: Record<string, any>;
}> {
  const client = getExperiencePlaneClient();
  return client.getSession(sessionId, tenantId);
}

/**
 * Upgrade session with user identity
 * 
 * ✅ PHASE 2: Should only be called by SessionBoundaryProvider
 * Components should NOT call this directly
 */
export async function upgradeSession(
  sessionId: string,
  userId: string,
  tenantId: string,
  accessToken: string,
  metadata?: Record<string, any>
): Promise<{
  session_id: string;
  tenant_id: string;
  user_id: string;
  created_at: string;
  metadata?: Record<string, any>;
}> {
  // TODO: Implement upgrade session endpoint
  // For now, this is handled by SessionBoundaryProvider
  throw new Error('upgradeSession should be called through SessionBoundaryProvider');
}

// ============================================
// Authentication API
// ============================================

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  name: string;
  email: string;
  password: string;
}

export interface AuthResponse {
  success: boolean;
  user?: {
    id: string;
    email: string;
    name: string;
    avatar_url?: string;
    permissions?: string[];
    tenant_id?: string;
  };
  token?: string;
  refresh_token?: string;
  message: string;
}

/**
 * Login user
 * 
 * ✅ PHASE 2: Use this instead of direct fetch in AuthProvider
 */
export async function loginUser(credentials: LoginRequest): Promise<AuthResponse> {
  const url = getApiEndpointUrl('/api/auth/login');
  
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(credentials),
  });

  if (!response.ok) {
    const errorText = await response.text();
    return {
      success: false,
      message: errorText || 'Login failed. Please check your credentials.',
    };
  }

  const data = await response.json();
  return {
    success: true,
    user: data.user,
    token: data.access_token,
    refresh_token: data.refresh_token,
    message: data.message || 'Login successful',
  };
}

/**
 * Register user
 * 
 * ✅ PHASE 2: Use this instead of direct fetch in AuthProvider
 */
export async function registerUser(credentials: RegisterRequest): Promise<AuthResponse> {
  const url = getApiEndpointUrl('/api/auth/register');
  
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(credentials),
  });

  if (!response.ok) {
    const errorText = await response.text();
    return {
      success: false,
      message: errorText || 'Registration failed. Please try again.',
    };
  }

  const data = await response.json();
  return {
    success: true,
    user: data.user,
    token: data.access_token,
    refresh_token: data.refresh_token,
    message: data.message || 'Registration successful',
  };
}

// ============================================
// Agent API
// ============================================

export interface AgentEvent {
  type: string;
  session_token: string;
  agent_type?: string;
  pillar?: string;
  [key: string]: any;
}

export interface AgentResponse {
  type: string;
  [key: string]: any;
}

/**
 * Send agent event
 * 
 * ✅ PHASE 2: Use this instead of direct fetch in AGUIEventProvider
 */
export async function sendAgentEvent(
  event: AgentEvent,
  config?: ServiceLayerAPIConfig
): Promise<AgentResponse[]> {
  const url = getApiEndpointUrl('/global/agent');
  
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      session_token: config?.sessionId || event.session_token,
      agent_type: event.agent_type || 'GuideAgent',
      pillar: event.pillar,
      event,
    }),
  });

  if (!response.ok) {
    throw new Error(await response.text());
  }

  const data = await response.json();
  // Assume data.result is the array of responses
  if (Array.isArray(data.result)) {
    return data.result;
  }
  return [];
}

// ============================================
// Intent & Execution API
// ============================================

/**
 * Submit intent for execution
 * 
 * ✅ PHASE 2: Use this instead of direct ExperiencePlaneClient calls
 */
export async function submitIntent(
  intentType: string,
  parameters?: Record<string, any>,
  metadata?: Record<string, any>,
  config?: ServiceLayerAPIConfig
): Promise<{
  execution_id: string;
  intent_id: string;
  status?: string;
  created_at?: string;
}> {
  if (!config?.sessionId || !config?.tenantId) {
    throw new Error('Session ID and tenant ID are required to submit intent');
  }

  const client = getExperiencePlaneClient();
  return client.submitIntent({
    intent_type: intentType,
    tenant_id: config.tenantId,
    session_id: config.sessionId,
    parameters,
    metadata,
  });
}

/**
 * Get execution status
 * 
 * ✅ PHASE 2: Use this instead of direct ExperiencePlaneClient calls
 */
export async function getExecutionStatus(
  executionId: string,
  config?: ServiceLayerAPIConfig
): Promise<{
  execution_id: string;
  status: string;
  intent_id?: string;
  error?: string;
  artifacts?: Record<string, unknown>;
}> {
  if (!config?.tenantId) {
    throw new Error('Tenant ID is required to get execution status');
  }

  const client = getExperiencePlaneClient();
  return client.getExecutionStatus(executionId, config.tenantId);
}

// ============================================
// AGUI → Intent Compilation (Frontend)
// ============================================

/**
 * ✅ PHASE 2.5: AGUI Native Integration
 * 
 * Frontend owns experience semantics (AGUI → Intent compilation).
 * Backend owns execution semantics (Intent validation → Execution).
 */

import type { AGUIState, IntentCompilationResult, AGUIMutation } from '@/shared/types/agui';

// Re-export for useServiceLayerAPI hook
export type { IntentCompilationResult };

/**
 * Compile AGUI state to Intent
 * 
 * ✅ PHASE 2.5: Frontend compilation of AGUI → Intent
 * 
 * This function compiles AGUI state (experience semantics) into an Intent
 * (execution semantics) that the backend can validate and execute.
 * 
 * The Intent must be fully self-contained (all parameters, all references resolved).
 */
export function compileIntentFromAGUI(
  aguiState: AGUIState,
  intentType?: string
): IntentCompilationResult {
  // Validate AGUI state
  if (!aguiState.journey.id) {
    return {
      intent_type: intentType || "unknown",
      parameters: {},
      validation_errors: ["AGUI state missing journey ID"],
    };
  }

  // Determine intent type from journey/step if not provided
  const resolvedIntentType = intentType || 
    aguiState.journey.steps.find(s => s.id === aguiState.journey.current_step)?.name ||
    aguiState.journey.name ||
    "generic_intent";

  // Compile AGUI state to Intent parameters
  const parameters: Record<string, any> = {
    // Journey context
    journey_id: aguiState.journey.id,
    current_step: aguiState.journey.current_step,
    
    // Input artifacts (fully resolved)
    input_artifacts: aguiState.inputs.artifacts.map(a => ({
      id: a.id,
      type: a.type,
      name: a.name,
      state: a.state,
      metadata: a.metadata || {},
    })),
    
    // Input parameters
    input_parameters: aguiState.inputs.parameters,
    
    // Workflows (if any)
    workflows: aguiState.workflows.map(w => ({
      id: w.id,
      name: w.name,
      state: w.state,
      nodes: w.nodes,
      edges: w.edges,
    })),
  };

  // Add output artifacts if journey is complete
  if (aguiState.outputs.artifacts.length > 0) {
    parameters.output_artifacts = aguiState.outputs.artifacts.map(a => ({
      id: a.id,
      type: a.type,
      name: a.name,
      state: a.state,
      metadata: a.metadata || {},
    }));
  }

  // Add output results if any
  if (Object.keys(aguiState.outputs.results).length > 0) {
    parameters.output_results = aguiState.outputs.results;
  }

  // Metadata
  const metadata: Record<string, any> = {
    agui_journey_id: aguiState.journey.id,
    agui_journey_name: aguiState.journey.name,
    compiled_at: new Date().toISOString(),
    ...aguiState.metadata,
  };

  return {
    intent_type: resolvedIntentType,
    parameters,
    metadata,
  };
}

/**
 * Update AGUI state
 * 
 * ✅ PHASE 2.5: Primary way to mutate platform state
 * 
 * This function updates AGUI state. The mutation is applied immediately.
 * To submit an intent, use `submitIntentFromAGUI()` after updating.
 */
export function updateAGUI(mutation: AGUIMutation): void {
  // This is a placeholder - actual implementation will be in the hook
  // that uses AGUIStateProvider
  throw new Error("updateAGUI must be called from useServiceLayerAPI hook (which has access to AGUIStateProvider)");
}

/**
 * Submit Intent compiled from AGUI state
 * 
 * ✅ PHASE 2.5: Compile AGUI → Intent and submit
 * 
 * This function:
 * 1. Compiles AGUI state to Intent (frontend compilation)
 * 2. Validates the compiled Intent
 * 3. Submits the Intent to the backend
 * 
 * The backend validates Intent shape only (not AGUI).
 */
export async function submitIntentFromAGUI(
  aguiState: AGUIState,
  intentType?: string,
  config?: ServiceLayerAPIConfig
): Promise<{
  execution_id: string;
  intent_id: string;
  status?: string;
  created_at?: string;
}> {
  // Compile AGUI → Intent (frontend compilation)
  const compilation = compileIntentFromAGUI(aguiState, intentType);
  
  // Check for validation errors
  if (compilation.validation_errors && compilation.validation_errors.length > 0) {
    throw new Error(`AGUI compilation failed: ${compilation.validation_errors.join(', ')}`);
  }

  // Submit compiled Intent
  return submitIntent(
    compilation.intent_type,
    compilation.parameters,
    compilation.metadata,
    config
  );
}

// ============================================
// Validation Utilities (Client-Side)
// ============================================

/**
 * Validate email format (client-side validation)
 * 
 * ✅ PHASE 2: Client-side validation utility
 */
export function validateEmail(email: string): { isValid: boolean; message?: string } {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!email || email.trim() === '') {
    return { isValid: false, message: 'Email is required' };
  }
  if (!emailRegex.test(email)) {
    return { isValid: false, message: 'Please enter a valid email address' };
  }
  return { isValid: true };
}

/**
 * Validate password (client-side validation)
 * 
 * ✅ PHASE 2: Client-side validation utility
 */
export function validatePassword(password: string): { isValid: boolean; message?: string } {
  if (!password) {
    return { isValid: false, message: 'Password is required' };
  }
  if (password.length < 8) {
    return { isValid: false, message: 'Password must be at least 8 characters' };
  }
  return { isValid: true };
}

/**
 * Validate name (client-side validation)
 * 
 * ✅ PHASE 2: Client-side validation utility
 */
export function validateName(name: string): { isValid: boolean; message?: string } {
  if (!name || name.trim().length === 0) {
    return { isValid: false, message: 'Name is required' };
  }
  if (name.trim().length > 50) {
    return { isValid: false, message: 'Name must be less than 50 characters' };
  }
  return { isValid: true };
}

// ============================================
// Helper: Get Service Layer Config from SessionBoundaryProvider
// ============================================

/**
 * Get service layer config from SessionBoundaryProvider
 * 
 * This helper should be used by hooks that need to make API calls
 * It gets the current session state from SessionBoundaryProvider
 */
export function getServiceLayerConfig(): ServiceLayerAPIConfig {
  // This will be called from hooks that have access to SessionBoundaryProvider
  // For now, fallback to sessionStorage (will be replaced in hooks)
  if (typeof window === 'undefined') {
    return {};
  }

  return {
    sessionId: sessionStorage.getItem('session_id'),
    accessToken: sessionStorage.getItem('access_token'),
    tenantId: sessionStorage.getItem('tenant_id'),
    userId: sessionStorage.getItem('user_id'),
  };
}
