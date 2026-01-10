/**
 * Insights VARK Analysis
 * Specialized VARK learning style analysis functionality
 */

import { InsightsService } from './core';
import { 
  VARKInsightsRequest, 
  InsightsAnalysisResponse, 
  LearningStyleType 
} from './types';

export interface VARKAnalysisRequest {
  sessionToken: string;
  learningStyle: LearningStyleType;
  fileUuid?: string;
  userQuery?: string;
  additionalContext?: any;
}

export interface VARKAnalysisResponse {
  success: boolean;
  data: {
    visual_insights?: any;
    tabular_insights?: any;
    auditory_summary?: string;
    kinesthetic_actions?: string[];
  };
  error?: string;
}

export interface LearningStyleAdaptation {
  visual: {
    charts: any[];
    graphs: any[];
    color_scheme: string;
    layout: string;
  };
  tabular: {
    tables: any[];
    structured_data: any[];
    sort_options: string[];
    filter_options: string[];
  };
  auditory: {
    summary: string;
    key_points: string[];
    narrative: string;
  };
  kinesthetic: {
    interactive_elements: string[];
    action_items: string[];
    next_steps: string[];
  };
}

export class VARKAnalysisService {
  private insightsService: InsightsService;

  constructor(insightsService: InsightsService) {
    this.insightsService = insightsService;
  }

  async processVARKInsights(request: VARKAnalysisRequest): Promise<VARKAnalysisResponse> {
    try {
      const varkRequest: VARKInsightsRequest = {
        session_token: request.sessionToken,
        file_uuid: request.fileUuid,
        learning_style: request.learningStyle,
        user_query: request.userQuery,
        additional_context: request.additionalContext,
      };

      const response = await fetch('/api/insights/vark', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(varkRequest),
      });

      if (!response.ok) {
        throw new Error(`VARK analysis failed: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      return {
        success: false,
        data: {},
        error: error instanceof Error ? error.message : 'VARK analysis failed',
      };
    }
  }

  async getVARKInsights(
    sessionToken: string,
    learningStyle: LearningStyleType,
    fileUuid?: string,
    userQuery?: string
  ): Promise<VARKAnalysisResponse> {
    const request: VARKAnalysisRequest = {
      sessionToken,
      learningStyle,
      fileUuid,
      userQuery,
    };

    return await this.processVARKInsights(request);
  }

  async adaptContentForLearningStyle(
    content: any,
    learningStyle: LearningStyleType
  ): Promise<LearningStyleAdaptation> {
    const adaptation: LearningStyleAdaptation = {
      visual: {
        charts: [],
        graphs: [],
        color_scheme: 'default',
        layout: 'standard',
      },
      tabular: {
        tables: [],
        structured_data: [],
        sort_options: [],
        filter_options: [],
      },
      auditory: {
        summary: '',
        key_points: [],
        narrative: '',
      },
      kinesthetic: {
        interactive_elements: [],
        action_items: [],
        next_steps: [],
      },
    };

    switch (learningStyle) {
      case LearningStyleType.VISUAL:
        adaptation.visual = this.adaptForVisual(content);
        break;
      case LearningStyleType.TABULAR:
        adaptation.tabular = this.adaptForTabular(content);
        break;
    }

    // Always provide auditory summary as proxy
    adaptation.auditory = this.generateAuditorySummary(content);

    return adaptation;
  }

  private adaptForVisual(content: any): LearningStyleAdaptation['visual'] {
    // Extract visual elements from content
    const charts = content.charts || [];
    const graphs = content.graphs || [];
    
    return {
      charts,
      graphs,
      color_scheme: 'blue-green',
      layout: 'grid',
    };
  }

  private adaptForTabular(content: any): LearningStyleAdaptation['tabular'] {
    // Extract tabular elements from content
    const tables = content.tables || [];
    const structuredData = content.structured_data || [];
    
    return {
      tables,
      structured_data: structuredData,
      sort_options: ['name', 'date', 'value'],
      filter_options: ['type', 'category', 'status'],
    };
  }

  private generateAuditorySummary(content: any): LearningStyleAdaptation['auditory'] {
    // Generate auditory-friendly summary
    const summary = content.summary || 'No summary available';
    const keyPoints = content.key_points || [];
    const narrative = content.narrative || summary;

    return {
      summary,
      key_points: keyPoints,
      narrative,
    };
  }

  async generateInteractiveElements(content: any): Promise<string[]> {
    // Generate interactive elements for kinesthetic learners
    const elements: string[] = [];
    
    if (content.charts) {
      elements.push('Interactive charts with zoom and pan');
    }
    
    if (content.tables) {
      elements.push('Sortable and filterable data tables');
    }
    
    if (content.insights) {
      elements.push('Clickable insight cards with details');
    }
    
    return elements;
  }

  async generateActionItems(content: any): Promise<string[]> {
    // Generate action items from insights
    const actions: string[] = [];
    
    if (content.recommendations) {
      actions.push(...content.recommendations.map((rec: string) => `Implement: ${rec}`));
    }
    
    if (content.insights) {
      actions.push('Review key insights for decision making');
    }
    
    return actions;
  }
} 