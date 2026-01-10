/**
 * VARKInsightsPanel Core
 * Core VARKInsightsPanel component with VARK interface
 */

import React from 'react';
import { VARKInsightsPanelProps } from './types';
import { useVARKInsightsPanel } from './hooks';
import { 
  FileSelector, 
  LearningStyleSelector, 
  BusinessSummary, 
  VARKDisplay, 
  SummarySection 
} from './components';

export function VARKInsightsPanel({ onClose, className = '', initialData }: VARKInsightsPanelProps) {
  const {
    state,
    handleFileSelect,
    handleLearningStyleChange,
    handleDataDepthChange,
    handleAnalysis,
    handleRefreshSummary,
    handleExport,
    handleShare,
  } = useVARKInsightsPanel();

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Error Display */}
      {state.error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-700 text-sm">{state.error}</p>
        </div>
      )}

      {/* File Selection */}
      <FileSelector
        files={state.files}
        selectedFile={state.selectedFile}
        onFileSelect={handleFileSelect}
        loading={state.fileLoading}
      />

      {/* VARK Display Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Learning Style Selector */}
        <LearningStyleSelector
          learningStyle={state.learningStyle}
          onStyleChange={handleLearningStyleChange}
          dataDepth={state.dataDepth}
          onDepthChange={handleDataDepthChange}
        />

        {/* Business Summary */}
        <BusinessSummary
          summary={state.businessSummary}
          loading={state.summaryLoading}
          onRefresh={handleRefreshSummary}
        />
      </div>

      {/* Analysis Display */}
      <VARKDisplay
        learningStyle={state.learningStyle}
        dataDepth={state.dataDepth}
        analysisResults={state.analysisResults}
        isAnalyzing={state.isAnalyzing || state.isIterativeAnalysis}
        onAnalysisComplete={(results) => {
          // Handle analysis completion
          console.log('Analysis completed:', results);
        }}
      />

      {/* Analysis History (if available) */}
      {state.analysisHistory.length > 1 && (
        <div className="bg-gray-50 border rounded-lg p-4">
          <h4 className="font-medium mb-3">Analysis History</h4>
          <div className="space-y-2">
            {state.analysisHistory.slice(-3).map((entry) => (
              <div key={entry.id} className="flex items-center gap-3 text-sm">
                <div className={`w-2 h-2 rounded-full ${
                  entry.type === 'initial_analysis' ? 'bg-blue-500' : 'bg-green-500'
                }`} />
                <span className="text-gray-600">
                  {entry.type === 'initial_analysis' ? 'Initial Analysis' : 'Follow-up Analysis'}
                </span>
                {entry.query && (
                  <span className="text-gray-500 italic">"{entry.query}"</span>
                )}
                <span className="text-gray-400">
                  {entry.timestamp.toLocaleTimeString()}
                </span>
              </div>
            ))}
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Use the InsightsLiaisonAgent in the chat panel to ask follow-up questions about your data.
          </p>
        </div>
      )}

      {/* Summary Section */}
      <SummarySection
        businessSummary={state.businessSummary}
        analysisResults={state.analysisResults}
        learningStyle={state.learningStyle}
        onExport={handleExport}
        onShare={handleShare}
      />

      {/* Analysis Button */}
      {state.selectedFile && !state.isAnalyzing && !state.isIterativeAnalysis && (
        <div className="text-center">
          <button
            onClick={handleAnalysis}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Analyze with {state.learningStyle === 'visual' ? 'Visual' : 'Tabular'} Style
          </button>
        </div>
      )}

      {/* Iterative Analysis Status */}
      {state.isIterativeAnalysis && (
        <div className="text-center py-4">
          <div className="inline-flex items-center gap-2 bg-blue-50 text-blue-700 px-4 py-2 rounded-lg">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-700"></div>
            <span>Processing follow-up analysis...</span>
          </div>
        </div>
      )}

      {/* InsightsLiaisonAgent Guidance */}
      {state.analysisResults && !state.isAnalyzing && !state.isIterativeAnalysis && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-medium text-blue-800 mb-2">💡 Interactive Analysis Ready</h4>
          <p className="text-sm text-blue-700">
            Use the <strong>InsightsLiaisonAgent</strong> in the chat panel to ask follow-up questions like:
          </p>
          <ul className="text-sm text-blue-600 mt-2 space-y-1">
            <li>• "Show me customers who are more than 90 days late"</li>
            <li>• "What are the trends in this data?"</li>
            <li>• "Can you drill down into the outliers?"</li>
          </ul>
        </div>
      )}
    </div>
  );
} 