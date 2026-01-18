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

import { useAuth } from '@/shared/auth/AuthProvider';
import { usePlatformState } from '@/shared/state/PlatformStateProvider';
import { useUnifiedAgentChat } from '@/shared/hooks/useUnifiedAgentChat';

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
  const { state } = usePlatformState();
  
  // Use real-time chat hook for liaison agent
  const {
    messages,
    isConnected,
    isLoading: isChatLoading,
    error: chatError,
    sendMessage,
    switchAgent
  } = useUnifiedAgentChat({
    sessionToken: state.session.sessionId || undefined,
    autoConnect: true,
    initialAgent: 'liaison',
    initialPillar: 'insights'
  });
  
  const [currentGuidance, setCurrentGuidance] = useState<InsightsGuidance | null>(null);
  const [userMessage, setUserMessage] = useState('');
  
  // Switch to liaison agent on mount
  useEffect(() => {
    switchAgent('liaison', 'insights');
  }, [switchAgent]);

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
    // Send suggestion as message to real-time chat
    try {
      await sendMessage(suggestion, 'liaison', 'insights');
    } catch (error) {
      console.error('Failed to send suggestion:', error);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userMessage.trim() || isChatLoading) return;

    const message = userMessage.trim();
    setUserMessage('');

    // Send message via real-time chat
    try {
      await sendMessage(message, 'liaison', 'insights');
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  // ============================================================================
  // HELPER FUNCTIONS
  // ============================================================================

  // Helper functions removed - now handled by real-time agent

  // ============================================================================
  // RENDER HELPERS
  // ============================================================================

  const renderMessage = (message: any) => {
    const isUser = message.role === 'user';
    
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
          {/* Connection Status */}
          {!isConnected && (
            <Alert>
              <AlertDescription className="text-xs">
                {chatError ? `Connection error: ${chatError}` : 'Connecting to Insights Liaison Agent...'}
              </AlertDescription>
            </Alert>
          )}
          
          {/* Conversation History */}
          {messages.length > 0 && (
            <div className="max-h-60 overflow-y-auto space-y-2">
              {messages.map(renderMessage)}
              {isChatLoading && (
                <div className="flex justify-start">
                  <div className="flex items-center space-x-2 bg-gray-100 rounded-lg px-3 py-2">
                    <Loader2 className="w-3 h-3 animate-spin text-gray-400" />
                    <span className="text-xs text-gray-600">AI is thinking...</span>
                  </div>
                </div>
              )}
            </div>
          )}
          
          {messages.length === 0 && isConnected && (
            <div className="text-center text-sm text-gray-500 py-4">
              Ask me about data analysis, visualizations, business insights, or recommendations!
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
              disabled={!userMessage.trim() || isChatLoading || !isConnected}
            >
              {isChatLoading ? (
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






























