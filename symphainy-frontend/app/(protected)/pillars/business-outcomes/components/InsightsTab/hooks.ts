// InsightsTab Hooks
"use client";
import React, { useMemo } from "react";
import { LearningStyleType } from "@/shared/services/insights/types";
import { InsightsTabProps, InsightsTabState, InsightsSummaryData, AnalysisHistoryEntry, VisualizationData, KeyInsightItem, RecommendationItem } from "./types";

export function useInsightsTab(props: InsightsTabProps): InsightsTabState {
  // Extract and process insights data
  const insightsSummary = useMemo((): InsightsSummaryData | null => {
    if (!props.insightsData) return null;
    
    // Handle different data structures
    if (props.insightsData.summary) {
      return {
        summary: props.insightsData.summary,
        key_insights: props.insightsData.key_insights || [],
        recommendations: props.insightsData.recommendations || [],
        visualizations: props.insightsData.visualizations || [],
        metadata: props.insightsData.metadata || {},
      };
    }
    
    if (props.insightsData.summary_text) {
      return {
        summary: props.insightsData.summary_text,
        key_insights: props.insightsData.insights_summary?.key_insights || [],
        recommendations: props.insightsData.recommendations || [],
        visualizations: props.insightsData.visualizations || [],
        metadata: {
          learning_style: props.insightsData.learning_style || LearningStyleType.VISUAL,
          analysis_type: props.insightsData.analysis_type,
          timestamp: props.insightsData.timestamp,
        },
      };
    }
    
    // Fallback for legacy format
    return {
      summary: props.insightsData.summary_text || "No summary available",
      key_insights: props.insightsData.insights_summary?.key_insights || [],
      recommendations: props.insightsData.recommendations || [],
      visualizations: props.insightsData.visualizations || [],
      metadata: {
        learning_style: LearningStyleType.VISUAL,
        analysis_type: "legacy",
        timestamp: new Date().toISOString(),
      },
    };
  }, [props.insightsData]);

  // Extract summary text
  const summaryText = useMemo(() => {
    return insightsSummary?.summary || "No insights summary available";
  }, [insightsSummary]);

  // Extract key insights
  const keyInsights = useMemo((): string[] => {
    if (!insightsSummary?.key_insights) return [];
    
    return insightsSummary.key_insights.map((insight: any, index: number) => {
      if (typeof insight === 'string') {
        return insight;
      }
      if (insight.name || insight.title) {
        return insight.name || insight.title;
      }
      return `Insight ${index + 1}`;
    });
  }, [insightsSummary]);

  // Extract recommendations
  const recommendations = useMemo((): string[] => {
    if (!insightsSummary?.recommendations) return [];
    
    return insightsSummary.recommendations.map((rec: any, index: number) => {
      if (typeof rec === 'string') {
        return rec;
      }
      if (rec.title || rec.description) {
        return rec.title || rec.description;
      }
      return `Recommendation ${index + 1}`;
    });
  }, [insightsSummary]);

  // Extract visualizations
  const visualizations = useMemo((): VisualizationData[] => {
    if (!insightsSummary?.visualizations) return [];
    
    return insightsSummary.visualizations.map((viz: any, index: number) => ({
      type: viz.type || 'chart',
      title: viz.title || `Visualization ${index + 1}`,
      data: viz.data || viz,
      config: viz.config || {},
      description: viz.description || '',
    }));
  }, [insightsSummary]);

  // Determine learning style
  const learningStyle = useMemo((): LearningStyleType => {
    return insightsSummary?.metadata?.learning_style || LearningStyleType.VISUAL;
  }, [insightsSummary]);

  // Extract analysis history
  const analysisHistory = useMemo((): AnalysisHistoryEntry[] => {
    if (!props.insightsData?.analysis_history) return [];
    
    return props.insightsData.analysis_history.map((entry: any) => ({
      id: entry.id || Math.random().toString(36).slice(2),
      timestamp: new Date(entry.timestamp || Date.now()),
      type: entry.type || 'initial_analysis',
      query: entry.query,
      learningStyle: entry.learning_style || LearningStyleType.VISUAL,
      results: entry.results || {},
      summary: entry.summary || '',
    }));
  }, [props.insightsData]);

  // Check if we have data
  const hasData = useMemo(() => {
    return !!(
      insightsSummary?.summary ||
      insightsSummary?.key_insights?.length > 0 ||
      insightsSummary?.recommendations?.length > 0 ||
      insightsSummary?.visualizations?.length > 0
    );
  }, [insightsSummary]);

  return {
    summaryText,
    keyInsights,
    recommendations,
    visualizations,
    learningStyle,
    analysisHistory,
    hasData,
  };
} 