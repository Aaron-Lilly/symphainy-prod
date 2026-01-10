/**
 * Insights Business Analysis
 * Specialized business analysis functionality for insights service
 */

import { InsightsService } from './core';
import { 
  BusinessSummaryRequest, 
  InsightsSummaryResponse,
  InsightsAnalysisResponse 
} from './types';

export interface BusinessAnalysisRequest {
  sessionToken: string;
  fileUuid?: string;
  analysisResults?: any;
  userInsights?: string[];
  includeRecommendations?: boolean;
}

export interface BusinessAnalysisResponse {
  success: boolean;
  data: {
    business_summary: string;
    key_insights: string[];
    recommendations: string[];
    risk_assessment: string[];
    opportunities: string[];
    next_steps: string[];
  };
  error?: string;
}

export interface BusinessInsights {
  summary: string;
  key_findings: string[];
  business_impact: string[];
  recommendations: string[];
  risk_factors: string[];
  opportunities: string[];
  action_items: string[];
}

export class BusinessAnalysisService {
  private insightsService: InsightsService;

  constructor(insightsService: InsightsService) {
    this.insightsService = insightsService;
  }

  async generateBusinessSummary(request: BusinessAnalysisRequest): Promise<BusinessAnalysisResponse> {
    try {
      const businessRequest: BusinessSummaryRequest = {
        session_token: request.sessionToken,
        file_uuid: request.fileUuid,
        analysis_results: request.analysisResults,
        user_insights: request.userInsights,
        include_recommendations: request.includeRecommendations,
      };

      const response = await fetch('/api/insights/business-summary', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(businessRequest),
      });

      if (!response.ok) {
        throw new Error(`Business summary generation failed: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      return {
        success: false,
        data: {
          business_summary: '',
          key_insights: [],
          recommendations: [],
          risk_assessment: [],
          opportunities: [],
          next_steps: [],
        },
        error: error instanceof Error ? error.message : 'Business summary generation failed',
      };
    }
  }

  async getBusinessSummary(
    sessionToken: string,
    fileUuid?: string,
    analysisResults?: any,
    userInsights?: string[]
  ): Promise<BusinessAnalysisResponse> {
    const request: BusinessAnalysisRequest = {
      sessionToken,
      fileUuid,
      analysisResults,
      userInsights,
      includeRecommendations: true,
    };

    return await this.generateBusinessSummary(request);
  }

  async analyzeBusinessImpact(analysisResults: any): Promise<BusinessInsights> {
    const insights: BusinessInsights = {
      summary: '',
      key_findings: [],
      business_impact: [],
      recommendations: [],
      risk_factors: [],
      opportunities: [],
      action_items: [],
    };

    // Extract key findings from analysis results
    if (analysisResults.insights) {
      insights.key_findings = analysisResults.insights.map((insight: any) => insight.description);
    }

    // Generate business impact assessment
    if (analysisResults.metrics) {
      insights.business_impact = this.assessBusinessImpact(analysisResults.metrics);
    }

    // Generate recommendations
    if (analysisResults.patterns) {
      insights.recommendations = this.generateRecommendations(analysisResults.patterns);
    }

    // Assess risks
    insights.risk_factors = this.assessRisks(analysisResults);

    // Identify opportunities
    insights.opportunities = this.identifyOpportunities(analysisResults);

    // Generate action items
    insights.action_items = this.generateActionItems(insights);

    // Generate summary
    insights.summary = this.generateSummary(insights);

    return insights;
  }

  private assessBusinessImpact(metrics: any): string[] {
    const impacts: string[] = [];
    
    if (metrics.revenue_impact) {
      impacts.push(`Revenue impact: ${metrics.revenue_impact}`);
    }
    
    if (metrics.cost_savings) {
      impacts.push(`Potential cost savings: ${metrics.cost_savings}`);
    }
    
    if (metrics.efficiency_gains) {
      impacts.push(`Efficiency improvements: ${metrics.efficiency_gains}`);
    }
    
    return impacts;
  }

  private generateRecommendations(patterns: any): string[] {
    const recommendations: string[] = [];
    
    if (patterns.trends) {
      recommendations.push('Monitor identified trends for strategic planning');
    }
    
    if (patterns.anomalies) {
      recommendations.push('Investigate anomalies for process improvements');
    }
    
    if (patterns.correlations) {
      recommendations.push('Leverage correlations for predictive modeling');
    }
    
    return recommendations;
  }

  private assessRisks(analysisResults: any): string[] {
    const risks: string[] = [];
    
    if (analysisResults.data_quality?.issues) {
      risks.push('Data quality issues may affect decision accuracy');
    }
    
    if (analysisResults.outliers?.count > 0) {
      risks.push('Outliers detected - investigate for data integrity');
    }
    
    if (analysisResults.missing_data?.percentage > 10) {
      risks.push('Significant missing data may impact analysis reliability');
    }
    
    return risks;
  }

  private identifyOpportunities(analysisResults: any): string[] {
    const opportunities: string[] = [];
    
    if (analysisResults.growth_patterns) {
      opportunities.push('Growth patterns identified for expansion planning');
    }
    
    if (analysisResults.optimization_areas) {
      opportunities.push('Optimization opportunities detected in key areas');
    }
    
    if (analysisResults.market_insights) {
      opportunities.push('Market insights available for competitive advantage');
    }
    
    return opportunities;
  }

  private generateActionItems(insights: BusinessInsights): string[] {
    const actions: string[] = [];
    
    // Prioritize recommendations
    insights.recommendations.slice(0, 3).forEach(rec => {
      actions.push(`Implement: ${rec}`);
    });
    
    // Address risks
    insights.risk_factors.slice(0, 2).forEach(risk => {
      actions.push(`Mitigate: ${risk}`);
    });
    
    // Pursue opportunities
    insights.opportunities.slice(0, 2).forEach(opp => {
      actions.push(`Pursue: ${opp}`);
    });
    
    return actions;
  }

  private generateSummary(insights: BusinessInsights): string {
    const keyPoints = insights.key_findings.slice(0, 3).join(', ');
    const impact = insights.business_impact.slice(0, 2).join(', ');
    
    return `Analysis reveals ${insights.key_findings.length} key findings with ${impact}. 
    ${insights.recommendations.length} recommendations identified for implementation. 
    ${insights.risk_factors.length} risks require attention while ${insights.opportunities.length} 
    opportunities present growth potential.`;
  }

  async exportBusinessSummary(insights: BusinessInsights, format: 'pdf' | 'docx' | 'json' = 'json'): Promise<string> {
    // Generate export content based on format
    switch (format) {
      case 'pdf':
        return this.generatePDFExport(insights);
      case 'docx':
        return this.generateDOCXExport(insights);
      case 'json':
      default:
        return JSON.stringify(insights, null, 2);
    }
  }

  private generatePDFExport(insights: BusinessInsights): string {
    // Mock PDF generation - in real implementation, use a PDF library
    return `PDF export for business insights (${insights.key_findings.length} findings)`;
  }

  private generateDOCXExport(insights: BusinessInsights): string {
    // Mock DOCX generation - in real implementation, use a DOCX library
    return `DOCX export for business insights (${insights.key_findings.length} findings)`;
  }
} 