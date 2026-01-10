/**
 * Business Outcomes API Manager
 * 
 * Centralizes all Business Outcomes pillar API calls using semantic endpoints.
 * Provides a clean interface for business outcomes operations.
 */

// ============================================
// Business Outcomes API Manager Types
// ============================================

export interface GenerateRoadmapRequest {
  pillar_outputs: Record<string, any>;
  roadmap_options?: any;
  user_id?: string;
}

export interface GenerateRoadmapResponse {
  success: boolean;
  roadmap_id?: string;
  roadmap?: any;
  message?: string;
  error?: string;
}

export interface GeneratePOCProposalRequest {
  pillar_outputs: Record<string, any>;
  proposal_options?: any;
  user_id?: string;
}

export interface GeneratePOCProposalResponse {
  success: boolean;
  proposal_id?: string;
  proposal?: any;
  message?: string;
  error?: string;
}

export interface PillarSummariesResponse {
  success: boolean;
  summaries?: Record<string, any>;
  message?: string;
  error?: string;
}

export interface JourneyVisualizationResponse {
  success: boolean;
  visualization?: any;
  message?: string;
  error?: string;
}

// ============================================
// Business Outcomes API Manager Class
// ============================================

import { BaseAPIManager, UserContext } from './BaseAPIManager';

export class BusinessOutcomesAPIManager extends BaseAPIManager {
  constructor(sessionToken: string, baseURL?: string, userContext?: UserContext) {
    super(sessionToken, baseURL, userContext);
  }

  // ============================================
  // Strategic Roadmap
  // ============================================

  async generateStrategicRoadmap(request: GenerateRoadmapRequest): Promise<GenerateRoadmapResponse> {
    const result = await this.post<GenerateRoadmapResponse>('/api/v1/business-outcomes-pillar/generate-strategic-roadmap', {
      pillar_outputs: request.pillar_outputs,
      roadmap_options: request.roadmap_options,
      user_id: request.user_id
    });

    if (!result.success || !result.data) {
      return {
        success: false,
        error: result.error || 'Roadmap generation failed'
      };
    }

    return result.data;
  }

  // ============================================
  // POC Proposal
  // ============================================

  async generatePOCProposal(request: GeneratePOCProposalRequest): Promise<GeneratePOCProposalResponse> {
    const result = await this.post<GeneratePOCProposalResponse>('/api/v1/business-outcomes-pillar/generate-proof-of-concept-proposal', {
      pillar_outputs: request.pillar_outputs,
      proposal_options: request.proposal_options,
      user_id: request.user_id
    });

    if (!result.success || !result.data) {
      return {
        success: false,
        error: result.error || 'POC proposal generation failed'
      };
    }

    return result.data;
  }

  // ============================================
  // Pillar Summaries
  // ============================================

  async getPillarSummaries(): Promise<PillarSummariesResponse> {
    const result = await this.get<PillarSummariesResponse>('/api/v1/business-outcomes-pillar/get-pillar-summaries');

    if (!result.success || !result.data) {
      return {
        success: false,
        error: result.error || 'Failed to get pillar summaries'
      };
    }

    return result.data;
  }

  // ============================================
  // Journey Visualization
  // ============================================

  async getJourneyVisualization(): Promise<JourneyVisualizationResponse> {
    try {
      const response = await fetch(`${this.baseURL}/api/v1/business-outcomes-pillar/get-journey-visualization`, {
        headers: {
          'Authorization': `Bearer ${this.sessionToken}`,
          'Content-Type': 'application/json',
          'X-Session-Token': this.sessionToken
        }
      });

      if (!response.ok) {
        const errorData = await response.json();
        return {
          success: false,
          error: errorData.message || errorData.error || 'Failed to get journey visualization'
        };
      }

      const data = await response.json();
      return {
        success: data.success,
        visualization: data.visualization,
        message: data.message,
        error: data.error
      };
    } catch (error) {
      console.error('Error getting journey visualization:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get journey visualization'
      };
    }
  }
}






