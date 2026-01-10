// InsightsTab Types
import { LearningStyleType } from "@/shared/services/insights/types";

export interface InsightsTabProps {
  insightsData?: any;
  isLoading?: boolean;
}

export interface InsightsTabState {
  summaryText: string;
  keyInsights: string[];
  recommendations: string[];
  visualizations: any[];
  learningStyle: LearningStyleType;
  analysisHistory: any[];
  hasData: boolean;
}

export interface InsightsTabUIProps {
  summaryText: string;
  keyInsights: string[];
  recommendations: string[];
  visualizations: any[];
  learningStyle: LearningStyleType;
  analysisHistory: any[];
  hasData: boolean;
  isLoading: boolean;
}

export interface InsightsSummaryData {
  summary: string;
  key_insights: string[];
  recommendations: string[];
  visualizations?: any[];
  metadata?: {
    learning_style?: LearningStyleType;
    analysis_type?: string;
    timestamp?: string;
  };
}

export interface AnalysisHistoryEntry {
  id: string;
  timestamp: Date;
  type: 'initial_analysis' | 'iterative_analysis';
  query?: string;
  learningStyle: LearningStyleType;
  results: any;
  summary: string;
}

export interface VisualizationData {
  type: 'chart' | 'table' | 'graph' | 'diagram';
  title: string;
  data: any;
  config?: any;
  description?: string;
}

export interface KeyInsightItem {
  id: string;
  title: string;
  description: string;
  category: string;
  impact: 'low' | 'medium' | 'high';
  confidence: number; // 0-100
  actionable: boolean;
}

export interface RecommendationItem {
  id: string;
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  category: string;
  effort: 'low' | 'medium' | 'high';
  impact: 'low' | 'medium' | 'high';
  timeline: string;
} 