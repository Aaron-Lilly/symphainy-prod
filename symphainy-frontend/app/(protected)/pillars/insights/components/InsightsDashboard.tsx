/**
 * InsightsDashboard New - Using Experience Layer Client
 * 
 * Enhanced InsightsDashboard component that uses the new unified Experience Layer Client
 * for insights generation and analysis.
 */

"use client";

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Brain, 
  TrendingUp, 
  Target, 
  Lightbulb, 
  BarChart3, 
  PieChart,
  Loader2, 
  AlertCircle,
  CheckCircle,
  Eye,
  Download,
  RefreshCw
} from 'lucide-react';
import { useAuth } from '@/shared/auth/AuthProvider';
import { usePlatformState } from '@/shared/state/PlatformStateProvider';
import { useInsightsOrchestrator } from "@/shared/hooks/usePillarOrchestrator";
import { toast } from 'sonner';

interface InsightData {
  insight_id: string;
  title: string;
  description: string;
  category: string;
  confidence_score: number;
  impact_level: 'high' | 'medium' | 'low';
  data_sources: string[];
  generated_at: string;
  tags: string[];
  recommendations?: string[];
  visualizations?: any[];
}

interface InsightsDashboardNewProps {
  contentData?: any;
  onInsightSelected?: (insight: InsightData) => void;
}

export function InsightsDashboard({ contentData, onInsightSelected }: InsightsDashboardNewProps) {
  const { isAuthenticated, user, sessionToken } = useAuth();
  const { state } = usePlatformState();
  
  // Get session token - prefer auth token (for backward compatibility), fallback to session ID
  const guideSessionToken = sessionToken || state.session.sessionId;
  
  const { 
    orchestrator, 
    isInitialized: orchestratorInitialized, 
    isLoading: orchestratorLoading, 
    error: orchestratorError,
    executeOperation
  } = useInsightsOrchestrator(guideSessionToken || "");
  
  const [insights, setInsights] = useState<InsightData[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedInsight, setSelectedInsight] = useState<InsightData | null>(null);
  const [generationProgress, setGenerationProgress] = useState(0);

  // Generate insights when content data is available
  useEffect(() => {
    if (contentData && isAuthenticated) {
      handleGenerateInsights();
    }
  }, [contentData, isAuthenticated]);

  // Handle insights generation
  const handleGenerateInsights = async () => {
    if (!contentData || !isAuthenticated) return;

    setIsGenerating(true);
    setError(null);
    setGenerationProgress(0);

    try {
      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setGenerationProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 15;
        });
      }, 300);

              // Dynamically import InsightsService
              const { InsightsService } = await import('@/shared/services/insights');
              const insightsService = new InsightsService(guideSessionToken);
      const response = await insightsService.getBusinessAnalysis(
        contentData.files?.[0]?.file_url || "",
        {
          session_id: "session_123", // TODO: Use real session ID
          include_recommendations: true,
          include_visualizations: true,
          confidence_threshold: 0.7
        },
        guideSessionToken
      );

      clearInterval(progressInterval);
      setGenerationProgress(100);

      if (response.success && response.data) {
        setInsights(response.data);
        
        toast.success('Insights generated successfully!', {
          description: `Generated ${response.data.length} insights from your content.`
        });
      } else {
        setError(response.error || 'Insights generation failed');
        toast.error('Insights generation failed', {
          description: response.error || 'An error occurred during insights generation'
        });
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Insights generation failed';
      setError(errorMessage);
      toast.error('Insights generation failed', {
        description: errorMessage
      });
    } finally {
      setIsGenerating(false);
      setGenerationProgress(0);
    }
  };

  // Handle insight selection
  const handleInsightClick = (insight: InsightData) => {
    setSelectedInsight(insight);
    if (onInsightSelected) {
      onInsightSelected(insight);
    }
  };

  // Get impact level color
  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high':
        return 'text-red-600 bg-red-100';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100';
      case 'low':
        return 'text-green-600 bg-green-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  // Get confidence score color
  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (!isAuthenticated) {
    return (
      <div className="p-6 text-center">
        <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Authentication Required</h3>
        <p className="text-gray-600">Please log in to generate insights.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Insights Dashboard</h2>
          <p className="text-gray-600">AI-powered insights from your content</p>
        </div>
        <Button
          onClick={handleGenerateInsights}
          disabled={isGenerating || !contentData}
          variant="outline"
        >
          {isGenerating ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <RefreshCw className="h-4 w-4 mr-2" />
              Regenerate Insights
            </>
          )}
        </Button>
      </div>

      {/* Generation Progress */}
      {isGenerating && (
        <Card>
          <CardContent className="p-6">
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <Brain className="h-6 w-6 text-blue-500" />
                <div>
                  <div className="font-medium text-gray-900">Generating Insights</div>
                  <div className="text-sm text-gray-600">Analyzing your content...</div>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span>Progress</span>
                  <span>{generationProgress}%</span>
                </div>
                <Progress value={generationProgress} className="w-full" />
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Insights Grid */}
      {insights.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {insights.map((insight) => (
            <Card 
              key={insight.insight_id}
              className={`cursor-pointer transition-all hover:shadow-lg ${
                selectedInsight?.insight_id === insight.insight_id ? 'ring-2 ring-blue-500' : ''
              }`}
              onClick={() => handleInsightClick(insight)}
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <CardTitle className="text-lg">{insight.title}</CardTitle>
                  <Badge className={getImpactColor(insight.impact_level)}>
                    {insight.impact_level}
                  </Badge>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge variant="outline">{insight.category}</Badge>
                  <span className={`text-sm font-medium ${getConfidenceColor(insight.confidence_score)}`}>
                    {Math.round(insight.confidence_score * 100)}% confidence
                  </span>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700 mb-4">{insight.description}</p>
                
                {/* Tags */}
                {insight.tags && insight.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-4">
                    {insight.tags.slice(0, 3).map((tag, index) => (
                      <Badge key={index} variant="secondary" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                    {insight.tags.length > 3 && (
                      <Badge variant="secondary" className="text-xs">
                        +{insight.tags.length - 3} more
                      </Badge>
                    )}
                  </div>
                )}

                {/* Data Sources */}
                <div className="text-xs text-gray-500">
                  Sources: {insight.data_sources.join(', ')}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Selected Insight Details */}
      {selectedInsight && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Eye className="h-5 w-5" />
              <span>Insight Details</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Basic Info */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <div className="text-sm font-medium text-gray-700">Category</div>
                <Badge variant="outline">{selectedInsight.category}</Badge>
              </div>
              <div>
                <div className="text-sm font-medium text-gray-700">Impact Level</div>
                <Badge className={getImpactColor(selectedInsight.impact_level)}>
                  {selectedInsight.impact_level}
                </Badge>
              </div>
              <div>
                <div className="text-sm font-medium text-gray-700">Confidence</div>
                <div className={`font-medium ${getConfidenceColor(selectedInsight.confidence_score)}`}>
                  {Math.round(selectedInsight.confidence_score * 100)}%
                </div>
              </div>
            </div>

            {/* Description */}
            <div>
              <div className="text-sm font-medium text-gray-700 mb-2">Description</div>
              <p className="text-gray-900">{selectedInsight.description}</p>
            </div>

            {/* Recommendations */}
            {selectedInsight.recommendations && selectedInsight.recommendations.length > 0 && (
              <div>
                <div className="text-sm font-medium text-gray-700 mb-3">Recommendations</div>
                <div className="space-y-2">
                  {selectedInsight.recommendations.map((recommendation, index) => (
                    <div key={index} className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                      <Lightbulb className="h-4 w-4 text-blue-500 mt-0.5 flex-shrink-0" />
                      <p className="text-sm text-gray-700">{recommendation}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Tags */}
            {selectedInsight.tags && selectedInsight.tags.length > 0 && (
              <div>
                <div className="text-sm font-medium text-gray-700 mb-2">Tags</div>
                <div className="flex flex-wrap gap-2">
                  {selectedInsight.tags.map((tag, index) => (
                    <Badge key={index} variant="secondary">
                      {tag}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Data Sources */}
            <div>
              <div className="text-sm font-medium text-gray-700 mb-2">Data Sources</div>
              <div className="flex flex-wrap gap-2">
                {selectedInsight.data_sources.map((source, index) => (
                  <Badge key={index} variant="outline">
                    {source}
                  </Badge>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error Display */}
      {error && (
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2 text-red-600">
              <AlertCircle className="h-4 w-4" />
              <span className="text-sm">{error}</span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* No Content Data */}
      {!contentData && !isGenerating && (
        <Card>
          <CardContent className="p-6 text-center">
            <Brain className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Content Data</h3>
            <p className="text-gray-600">Process content in the Data Pillar to generate insights.</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
