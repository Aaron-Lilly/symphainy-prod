/**
 * Intent Submission Helper
 * 
 * Thin wrapper for intent-based API submission.
 * 
 * ⚠️ CRITICAL: This is a thin wrapper only - no semantic abstraction.
 * - Does NOT hide intent types or parameters
 * - Does NOT add retry logic (belongs in Runtime)
 * - Does NOT add business logic
 * 
 * Purpose: Reduce boilerplate, not hide architecture.
 */

import { getApiEndpointUrl } from '@/shared/config/api-config';

export interface IntentSubmitRequest {
  intent_type: string;
  tenant_id: string;
  session_id: string;
  solution_id?: string;
  parameters?: Record<string, any>;
  metadata?: Record<string, any>;
}

export interface IntentSubmitResponse {
  execution_id: string;
  intent_id: string;
  status: "accepted" | "rejected";
  tenant_id: string;
  session_id: string;
  created_at: string;
  metadata?: Record<string, any>;
}

/**
 * Submit intent to Runtime via intent-based API.
 * 
 * This is the ONLY way to trigger backend execution.
 * All operations must go through Runtime/ExecutionLifecycleManager.
 * 
 * @param request Intent submission request
 * @returns Intent submission response
 * @throws Error if submission fails (user-friendly message)
 */
export async function submitIntent(
  request: IntentSubmitRequest
): Promise<IntentSubmitResponse> {
  const url = getApiEndpointUrl('/api/intent/submit');
  
  // Get access token if available
  const accessToken = typeof window !== 'undefined' 
    ? sessionStorage.getItem("access_token") 
    : null;
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };
  
  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`;
  }
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify(request),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ 
        detail: `Failed to submit intent: ${response.statusText}` 
      }));
      
      // ✅ User-friendly error message (per CIO feedback)
      const errorMessage = errorData.detail || errorData.message || `Failed to submit intent: ${response.statusText}`;
      
      // ✅ Log migration warning in dev (per CIO feedback)
      if (process.env.NODE_ENV === 'development') {
        console.warn(`[IntentSubmission] Failed to submit intent ${request.intent_type}:`, errorMessage);
      }
      
      throw new Error(errorMessage);
    }
    
    return await response.json();
  } catch (error) {
    // ✅ User-friendly error message (per CIO feedback)
    if (error instanceof Error) {
      throw error;
    }
    
    throw new Error('Failed to submit intent: Network error or invalid response');
  }
}

/**
 * Get execution status.
 * 
 * @param executionId Execution ID from intent submission
 * @param tenantId Tenant ID
 * @returns Execution status
 */
export async function getExecutionStatus(
  executionId: string,
  tenantId: string
): Promise<any> {
  const url = getApiEndpointUrl(`/api/execution/${executionId}/status`);
  
  const accessToken = typeof window !== 'undefined' 
    ? sessionStorage.getItem("access_token") 
    : null;
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };
  
  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`;
  }
  
  const response = await fetch(url, {
    method: 'GET',
    headers,
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ 
      detail: `Failed to get execution status: ${response.statusText}` 
    }));
    throw new Error(errorData.detail || `Failed to get execution status: ${response.statusText}`);
  }
  
  return await response.json();
}
