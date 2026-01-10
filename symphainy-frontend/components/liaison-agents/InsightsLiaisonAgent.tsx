/**
 * Insights Liaison Agent
 * 
 * Specialized agent for the Insights Pillar that provides guidance on data analysis,
 * visualization, business insights generation, and recommendations.
 */

"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  BarChart3, 
  TrendingUp, 
  Brain, 
  CheckCircle, 
  AlertCircle, 
  Lightbulb,
  Bot,
  User,
  SendHorizontal,
  Loader2,
  Eye,
  Target
} from 'lucide-react';

import { useAuth } from '@/shared/agui/AuthProvider';

// ============================================================================
// COMPONENT INTERFACES
// ============================================================================

interface InsightsLiaisonAgentProps {
  contentData?: any;
  analysisResult?: any;
  visualization?: any;
  insightsSummary?: any;
  onAnalyze?: (fileIds: string[]) => void;
  onGenerateSummary?: () => void;
  className?: string;
}

interface InsightsGuidance {
  step: 'select_files' | 'analyze' | 'visualize' | 'summarize' | 'complete';
  message: string;
  suggestions: string[];
  nextAction?: string;
}

// ============================================================================
// INSIGHTS LIAISON AGENT COMPONENT
// ============================================================================

export const InsightsLiaisonAgent: React.FC<InsightsLiaisonAgentProps> = ({
  contentData,
  analysisResult,
  visualization,
  insightsSummary,
  onAnalyze,
  onGenerateSummary,
  className = ''
}) => {
  const { user } = useAuth();
  
  
  const [currentGuidance, setCurrentGuidance] = useState<InsightsGuidance | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [conversationHistory, setConversationHistory] = useState<any[]>([]);
  const [userMessage, setUserMessage] = useState('');

  // ============================================================================
  // GUIDANCE LOGIC
  // ============================================================================

  useEffect(() => {
    const analyzeInsightsState = () => {
      if (!contentData || !contentData.files || contentData.files.length === 0) {
        setCurrentGuidance({
          step: 'select_files',
          message: 'Welcome to the Insights Pillar! I\'m here to help you analyze your business data and generate actionable insights. First, let\'s select the files you want to analyze.',
          suggestions: [
            'Select files from Content Pillar',
            'Choose analysis type',
            'Configure visualization preferences',
            'Set analysis parameters'
          ],
          nextAction: 'select_files'
        });
      } else if (contentData && !analysisResult) {
        setCurrentGuidance({
          step: 'analyze',
          message: `Great! You have ${contentData.files.length} file(s) ready for analysis. Let's run a comprehensive business analysis to extract insights.`,
          suggestions: [
            'Run comprehensive analysis',
            'Quick analysis for overview',
            'Detailed analysis with deep insights',
            'Custom analysis configuration'
          ],
          nextAction: 'analyze_data'
        });
      } else if (analysisResult && !visualization) {
        setCurrentGuidance({
          step: 'visualize',
          message: 'Excellent! Your analysis is complete. Now let\'s create visualizations to help you understand the insights better.',
          suggestions: [
            'Generate data visualizations',
            'Create interactive charts',
            'Build dashboard views',
            'Export visualization data'
          ],
          nextAction: 'create_visualizations'
        });
      } else if (visualization && !insightsSummary) {
        setCurrentGuidance({
          step: 'summarize',
          message: 'Perfect! Your visualizations are ready. Now let\'s generate a comprehensive insights summary with actionable recommendations.',
          suggestions: [
            'Generate insights summary',
            'Create executive summary',
            'Identify key recommendations',
            'Prepare for operations pillar'
          ],
          nextAction: 'generate_summary'
        });
      } else if (insightsSummary) {
        setCurrentGuidance({
          step: 'complete',
          message: 'Outstanding! Your insights analysis is complete. You now have comprehensive business insights and recommendations ready for implementation.',
          suggestions: [
            'Proceed to Operations Pillar',
            'Export insights report',
            'Share insights with team',
            'Create action plan'
          ],
          nextAction: 'proceed_to_operations'
        });
      }
    };

    analyzeInsightsState();
  }, [contentData, analysisResult, visualization, insightsSummary]);

  // ============================================================================
  // EVENT HANDLERS
  // ============================================================================

  const handleSuggestionClick = async (suggestion: string) => {
    setIsAnalyzing(true);
    
    // Add user message to conversation
    const userMsg = {
      id: Date.now().toString(),
      type: 'user',
      content: suggestion,
      timestamp: new Date()
    };
    setConversationHistory(prev => [...prev, userMsg]);

    // Simulate AI response
    setTimeout(() => {
      const aiResponse = {
        id: (Date.now() + 1).toString(),
        type: 'agent',
        content: getSuggestionResponse(suggestion),
        timestamp: new Date()
      };
      setConversationHistory(prev => [...prev, aiResponse]);
      setIsAnalyzing(false);
    }, 1000);
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userMessage.trim()) return;

    const message = userMessage.trim();
    setUserMessage('');

    // Add user message
    const userMsg = {
      id: Date.now().toString(),
      type: 'user',
      content: message,
      timestamp: new Date()
    };
    setConversationHistory(prev => [...prev, userMsg]);

    // Generate AI response
    setIsAnalyzing(true);
    setTimeout(() => {
      const aiResponse = {
        id: (Date.now() + 1).toString(),
        type: 'agent',
        content: generateInsightsResponse(message),
        timestamp: new Date()
      };
      setConversationHistory(prev => [...prev, aiResponse]);
      setIsAnalyzing(false);
    }, 1500);
  };

  // ============================================================================
  // HELPER FUNCTIONS
  // ============================================================================

  const getSuggestionResponse = (suggestion: string): string => {
    if (suggestion.includes('Select files') || suggestion.includes('Choose')) {
      return 'I can help you select the right files for analysis. Look for files that contain relevant business data, such as reports, spreadsheets, or documents with key metrics.';
    } else if (suggestion.includes('analysis') || suggestion.includes('Analyze')) {
      return 'Analysis will examine your data for patterns, trends, and insights. I recommend starting with a comprehensive analysis to get the full picture, then drilling down into specific areas.';
    } else if (suggestion.includes('visualization') || suggestion.includes('charts')) {
      return 'Visualizations help you understand your data better. I can help you choose the right chart types based on your data and create interactive dashboards for deeper exploration.';
    } else if (suggestion.includes('summary') || suggestion.includes('recommendations')) {
      return 'The insights summary will synthesize all your analysis into actionable recommendations. This creates a clear path forward for implementing the insights in your operations.';
    } else if (suggestion.includes('Proceed') || suggestion.includes('operations')) {
      return 'Great! Your insights are ready for the Operations Pillar. The analysis results and recommendations will be used to create workflows and SOPs for implementation.';
    }
    return 'I understand you want help with insights analysis. Let me guide you through the next steps.';
  };

  const generateInsightsResponse = (message: string): string => {
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes('analysis') || lowerMessage.includes('analyze')) {
      return 'I can help you choose the right analysis approach. Comprehensive analysis gives you the full picture, quick analysis provides an overview, and detailed analysis dives deep into specific areas.';
    } else if (lowerMessage.includes('visualization') || lowerMessage.includes('chart')) {
      return 'For visualizations, I recommend starting with bar charts for comparisons, line charts for trends, and pie charts for proportions. Interactive dashboards let you explore the data dynamically.';
    } else if (lowerMessage.includes('insight') || lowerMessage.includes('pattern')) {
      return 'Insights are the key findings from your data analysis. Look for trends, anomalies, correlations, and opportunities. I can help you interpret what the data is telling you.';
    } else if (lowerMessage.includes('recommendation') || lowerMessage.includes('action')) {
      return 'Recommendations are actionable steps based on your insights. They should be specific, measurable, and tied to business outcomes. I can help you prioritize and implement them.';
    } else if (lowerMessage.includes('metric') || lowerMessage.includes('kpi')) {
      return 'Key metrics and KPIs are essential for measuring business performance. I can help you identify the most important metrics for your business and track them over time.';
    } else if (lowerMessage.includes('trend') || lowerMessage.includes('forecast')) {
      return 'Trend analysis helps you understand how your business is changing over time. I can help you identify patterns and make predictions about future performance.';
    }
    
    return 'I\'m here to help with insights analysis! You can ask me about data analysis, visualizations, business insights, recommendations, or any other insights-related questions.';
  };

  // ============================================================================
  // RENDER HELPERS
  // ============================================================================

  const renderMessage = (message: any) => {
    const isUser = message.type === 'user';
    
    return (
      <div key={message.id} className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-3`}>
        <div className={`flex items-start space-x-2 max-w-[80%] ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
          <div className={`flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center ${
            isUser ? 'bg-blue-500' : 'bg-purple-500'
          }`}>
            {isUser ? (
              <User className="w-3 h-3 text-white" />
            ) : (
              <Bot className="w-3 h-3 text-white" />
            )}
          </div>
          <div className={`rounded-lg px-3 py-2 text-sm ${
            isUser 
              ? 'bg-blue-500 text-white' 
              : 'bg-gray-100 text-gray-800'
          }`}>
            {message.content}
          </div>
        </div>
      </div>
    );
  };

  const renderCurrentGuidance = () => {
    if (!currentGuidance) return null;

    return (
      <Card className="border-purple-200 bg-purple-50">
        <CardHeader className="pb-3">
          <CardTitle className="text-purple-800 flex items-center space-x-2">
            <Lightbulb className="w-4 h-4" />
            <span>Insights Guidance</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm text-purple-700">{currentGuidance.message}</p>
          
          <div>
            <h4 className="font-medium text-purple-800 mb-2">Suggested Actions:</h4>
            <div className="space-y-2">
              {currentGuidance.suggestions.map((suggestion, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="w-full text-left justify-start text-purple-700 border-purple-300 hover:bg-purple-100"
                >
                  {suggestion}
                </Button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    );
  };

  // ============================================================================
  // MAIN RENDER
  // ============================================================================

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Current Guidance */}
      {renderCurrentGuidance()}

      {/* Chat Interface */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-gray-800 flex items-center space-x-2">
            <Bot className="w-4 h-4" />
            <span>Insights Liaison Agent</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Conversation History */}
          {conversationHistory.length > 0 && (
            <div className="max-h-60 overflow-y-auto space-y-2">
              {conversationHistory.map(renderMessage)}
              {isAnalyzing && (
                <div className="flex justify-start">
                  <div className="flex items-center space-x-2 bg-gray-100 rounded-lg px-3 py-2">
                    <Loader2 className="w-3 h-3 animate-spin text-gray-400" />
                    <span className="text-xs text-gray-600">AI is thinking...</span>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Input Form */}
          <form onSubmit={handleSendMessage} className="flex space-x-2">
            <input
              type="text"
              placeholder="Ask about insights analysis..."
              value={userMessage}
              onChange={(e) => setUserMessage(e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
            <Button
              type="submit"
              size="sm"
              disabled={!userMessage.trim() || isAnalyzing}
            >
              {isAnalyzing ? (
                <Loader2 className="w-3 h-3 animate-spin" />
              ) : (
                <SendHorizontal className="w-3 h-3" />
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Status Indicators */}
      <div className="grid grid-cols-4 gap-2">
        <div className={`p-2 rounded-lg text-center text-xs ${
          contentData ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
        }`}>
          <Eye className="w-4 h-4 mx-auto mb-1" />
          Files Selected
        </div>
        <div className={`p-2 rounded-lg text-center text-xs ${
          analysisResult ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
        }`}>
          <BarChart3 className="w-4 h-4 mx-auto mb-1" />
          Analysis Complete
        </div>
        <div className={`p-2 rounded-lg text-center text-xs ${
          visualization ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
        }`}>
          <TrendingUp className="w-4 h-4 mx-auto mb-1" />
          Visualizations Ready
        </div>
        <div className={`p-2 rounded-lg text-center text-xs ${
          insightsSummary ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
        }`}>
          <Brain className="w-4 h-4 mx-auto mb-1" />
          Summary Generated
        </div>
      </div>
    </div>
  );
};

export default InsightsLiaisonAgent;






























