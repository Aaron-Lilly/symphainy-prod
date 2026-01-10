/**
 * StructuredDataInsightsSection Component
 * 
 * Complete section for structured data insights analysis
 * Includes file/metadata selection, analysis trigger, and results display
 */

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Sparkles, AlertCircle } from 'lucide-react';
import { InsightsFileSelector } from './InsightsFileSelector';
import { InsightsSummaryDisplay } from './InsightsSummaryDisplay';
import { analyzeContentForInsights, AnalyzeContentRequest, AnalyzeContentResponse } from '@/lib/api/insights';

interface StructuredDataInsightsSectionProps {
  onAnalysisComplete?: (analysis: AnalyzeContentResponse) => void;
}

export function StructuredDataInsightsSection({ 
  onAnalysisComplete 
}: StructuredDataInsightsSectionProps) {
  const [selectedSourceId, setSelectedSourceId] = useState<string>('');
  const [selectedSourceType, setSelectedSourceType] = useState<'file' | 'content_metadata'>('file');
  const [analysisResult, setAnalysisResult] = useState<AnalyzeContentResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSourceSelected = (
    sourceId: string, 
    sourceType: 'file' | 'content_metadata',
    contentType: 'structured' | 'unstructured'
  ) => {
    setSelectedSourceId(sourceId);
    setSelectedSourceType(sourceType);
    // Clear previous results and errors
    setAnalysisResult(null);
    setError(null);
  };

  const handleAnalyze = async () => {
    if (!selectedSourceId) {
      setError('Please select a data source first');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const request: AnalyzeContentRequest = {
        source_type: selectedSourceType,
        ...(selectedSourceType === 'file' ? { file_id: selectedSourceId } : { content_metadata_id: selectedSourceId }),
        content_type: 'structured',
        analysis_options: {
          include_visualizations: true,
          include_tabular_summary: true,
          aar_specific_analysis: false
        }
      };

      const result = await analyzeContentForInsights(request);

      if (result.success) {
        setAnalysisResult(result);
        if (onAnalysisComplete) {
          onAnalysisComplete(result);
        }
      } else {
        setError(result.error || 'Analysis failed');
      }
    } catch (err) {
      console.error('Analysis error:', err);
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* File/Metadata Selection */}
      <InsightsFileSelector
        onSourceSelected={handleSourceSelected}
        contentType="structured"
        selectedSourceId={selectedSourceId}
        selectedSourceType={selectedSourceType}
      />

      {/* Analysis Trigger */}
      <div className="flex items-center gap-4">
        <Button
          onClick={handleAnalyze}
          disabled={!selectedSourceId || loading}
          size="lg"
          className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
        >
          <Sparkles className="h-5 w-5 mr-2" />
          {loading ? 'Analyzing...' : 'Analyze Content'}
        </Button>

        {selectedSourceId && !loading && (
          <span className="text-sm text-gray-600">
            Ready to analyze {selectedSourceType === 'file' ? 'file' : 'metadata'}
          </span>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-red-900">Analysis Error</p>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* Results Display */}
      <InsightsSummaryDisplay
        summary={analysisResult?.summary}
        loading={loading}
        defaultTab="text"
      />

      {/* Insights List */}
      {analysisResult?.insights && analysisResult.insights.length > 0 && !loading && (
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-purple-900 mb-4">
            Key Insights ({analysisResult.insights.length})
          </h3>
          <div className="space-y-3">
            {analysisResult.insights.map((insight) => (
              <div
                key={insight.insight_id}
                className="bg-white p-4 rounded-lg border border-purple-100"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <span className="text-xs font-medium text-purple-600 uppercase tracking-wide">
                      {insight.type}
                    </span>
                    <p className="text-sm text-gray-900 mt-1">{insight.description}</p>
                    {insight.recommendations && insight.recommendations.length > 0 && (
                      <div className="mt-2">
                        <p className="text-xs font-medium text-gray-700">Recommendations:</p>
                        <ul className="text-xs text-gray-600 mt-1 ml-4 space-y-1">
                          {insight.recommendations.map((rec, idx) => (
                            <li key={idx}>• {rec}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                  <div className="text-xs text-gray-500 ml-4">
                    {Math.round(insight.confidence * 100)}% confidence
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}








