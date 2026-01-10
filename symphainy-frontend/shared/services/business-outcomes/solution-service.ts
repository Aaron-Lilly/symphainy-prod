/**
 * Business Outcomes Solution Service
 * 
 * Service layer for Business Outcomes Solution Orchestrator endpoints.
 * Follows the same pattern as Operations Solution Service.
 * 
 * Endpoints:
 * - GET /api/v1/business-outcomes-solution/pillar-summaries?session_id=...
 * - POST /api/v1/business-outcomes-solution/roadmap
 * - POST /api/v1/business-outcomes-solution/poc-proposal
 */

import { getApiEndpointUrl } from '@/shared/config/api-config';

// Use centralized API config (NO hardcoded values)
const API_BASE = getApiEndpointUrl('/api/v1/business-outcomes-solution');

// Helper to create standardized authenticated headers
const getAuthHeaders = (token?: string, sessionToken?: string) => {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  
  if (sessionToken) {
    headers["X-Session-Token"] = sessionToken;
  }
  
  return headers;
};

export interface PillarSummariesResponse {
  success: boolean;
  summaries: {
    content?: any;
    insights?: any;
    operations?: any;
  };
  solution_context?: any;
  workflow_id?: string;
  error?: string;
}

export interface RoadmapGenerationRequest {
  pillarSummaries?: any;
  sessionId?: string;
  roadmapOptions?: any;
  userId?: string;
  sessionToken?: string;
}

export interface RoadmapGenerationResponse {
  success: boolean;
  roadmap_id?: string;
  roadmap?: any;
  agent_reasoning?: string;
  generated_at?: string;
  error?: string;
}

export interface POCProposalRequest {
  pillarSummaries?: any;
  sessionId?: string;
  pocOptions?: any;
  userId?: string;
  sessionToken?: string;
}

export interface POCProposalResponse {
  success: boolean;
  poc_id?: string;
  poc_proposal?: any;
  financial_metrics?: any;
  agent_reasoning?: string;
  generated_at?: string;
  error?: string;
}

export class BusinessOutcomesSolutionService {
  private token?: string;

  constructor(token?: string) {
    this.token = token || (typeof window !== 'undefined' ? localStorage.getItem('auth_token') || undefined : undefined);
  }

  /**
   * Get pillar summaries
   */
  async getPillarSummaries(
    sessionId: string,
    sessionToken?: string
  ): Promise<PillarSummariesResponse> {
    const res = await fetch(`${API_BASE}/pillar-summaries?session_id=${encodeURIComponent(sessionId)}`, {
      method: "GET",
      headers: getAuthHeaders(this.token, sessionToken),
    });
    
    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(`Failed to get pillar summaries: ${res.status} ${res.statusText} - ${errorText}`);
    }
    
    return await res.json();
  }

  /**
   * Generate strategic roadmap
   */
  async generateRoadmap(
    request: RoadmapGenerationRequest
  ): Promise<RoadmapGenerationResponse> {
    const res = await fetch(`${API_BASE}/roadmap`, {
      method: "POST",
      headers: getAuthHeaders(this.token, request.sessionToken),
      body: JSON.stringify({
        pillar_summaries: request.pillarSummaries,
        session_id: request.sessionId,
        roadmap_options: request.roadmapOptions,
        user_context: {
          user_id: request.userId,
          session_id: request.sessionId,
          session_token: request.sessionToken
        }
      }),
    });
    
    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(`Failed to generate roadmap: ${res.status} ${res.statusText} - ${errorText}`);
    }
    
    return await res.json();
  }

  /**
   * Generate POC proposal
   */
  async generatePOCProposal(
    request: POCProposalRequest
  ): Promise<POCProposalResponse> {
    const res = await fetch(`${API_BASE}/poc-proposal`, {
      method: "POST",
      headers: getAuthHeaders(this.token, request.sessionToken),
      body: JSON.stringify({
        pillar_summaries: request.pillarSummaries,
        session_id: request.sessionId,
        poc_options: request.pocOptions,
        user_context: {
          user_id: request.userId,
          session_id: request.sessionId,
          session_token: request.sessionToken
        }
      }),
    });
    
    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(`Failed to generate POC proposal: ${res.status} ${res.statusText} - ${errorText}`);
    }
    
    return await res.json();
  }
}

// Export singleton instance
export const businessOutcomesSolutionService = new BusinessOutcomesSolutionService();





