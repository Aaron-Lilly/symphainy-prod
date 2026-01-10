/**
 * Insights API Manager
 * 
 * Centralizes all Insights pillar API calls using semantic endpoints.
 * Provides a clean interface for insights analysis operations.
 */

// ============================================
// Insights API Manager Types
// ============================================

export type AnalysisType = 'quick' | 'comprehensive' | 'detailed';

export interface AnalyzeContentRequest {
  file_ids: string[];
  analysis_type?: AnalysisType;
  focus_areas?: string[];  // ["trends", "anomalies", "recommendations"]
  user_id?: string;
}

export interface AnalyzeContentResponse {
  success: boolean;
  analysis_id?: string;
  key_findings?: any[];
  recommendations?: any[];
  visualizations?: any;
  confidence_score?: number;
  message?: string;
  error?: string;
}

export interface AnalysisResultsResponse {
  success: boolean;
  analysis?: any;
  findings?: any[];
  recommendations?: any[];
  message?: string;
  error?: string;
}

export interface VisualizationsResponse {
  success: boolean;
  visualizations?: any;
  message?: string;
  error?: string;
}

// ============================================
// Insights API Manager Class
// ============================================

import { BaseAPIManager, UserContext } from './BaseAPIManager';

export class InsightsAPIManager extends BaseAPIManager {
  constructor(sessionToken: string, baseURL?: string, userContext?: UserContext) {
    super(sessionToken, baseURL, userContext);
  }

  // ============================================
  // Content Analysis
  // ============================================

  async analyzeContentForInsights(request: AnalyzeContentRequest): Promise<AnalyzeContentResponse> {
    const result = await this.post<AnalyzeContentResponse>('/api/v1/insights-pillar/analyze-content', {
      file_ids: request.file_ids,
      analysis_type: request.analysis_type || 'comprehensive',
      focus_areas: request.focus_areas,
      user_id: request.user_id
    });

    if (!result.success || !result.data) {
      return {
        success: false,
        error: result.error || 'Content analysis failed'
      };
    }

    return result.data;
  }

  // ============================================
  // Analysis Results
  // ============================================

  async getAnalysisResults(analysisId: string): Promise<AnalysisResultsResponse> {
    const result = await this.get<AnalysisResultsResponse>(`/api/v1/insights-pillar/analysis-results/${analysisId}`);

    if (!result.success || !result.data) {
      return {
        success: false,
        error: result.error || 'Failed to get analysis results'
      };
    }

    return result.data;
  }

  // ============================================
  // Visualizations
  // ============================================

  async getVisualizations(analysisId: string): Promise<VisualizationsResponse> {
    const result = await this.get<VisualizationsResponse>(`/api/v1/insights-pillar/analysis-visualizations/${analysisId}`);

    if (!result.success || !result.data) {
      return {
        success: false,
        error: result.error || 'Failed to get visualizations'
      };
    }

    return result.data;
  }
}






