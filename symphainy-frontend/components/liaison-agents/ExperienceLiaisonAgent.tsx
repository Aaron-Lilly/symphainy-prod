/**
 * Experience Liaison Agent
 * 
 * Specialized agent for the Experience Pillar that provides guidance on roadmap generation,
 * POC proposal creation, strategic planning, and business outcomes synthesis.
 */

"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Map, 
  Rocket, 
  Target, 
  CheckCircle, 
  AlertCircle, 
  Lightbulb,
  Bot,
  User,
  SendHorizontal,
  Loader2,
  Compass,
  Zap,
  TrendingUp
} from 'lucide-react';
// Removed deprecated ExperienceLayerProvider import
import { useAuth } from '@/shared/auth/AuthProvider';

// ============================================================================
// COMPONENT INTERFACES
// ============================================================================

interface ExperienceLiaisonAgentProps {
  pillarOutputs?: any;
  roadmap?: any;
  pocProposal?: any;
  onAggregateOutputs?: () => void;
  onGenerateRoadmap?: () => void;
  onGeneratePOC?: () => void;
  className?: string;
}

interface ExperienceGuidance {
  step: 'aggregate' | 'roadmap' | 'poc' | 'complete';
  message: string;
  suggestions: string[];
  nextAction?: string;
}

// ============================================================================
// EXPERIENCE LIAISON AGENT COMPONENT
// ============================================================================

export const ExperienceLiaisonAgent: React.FC<ExperienceLiaisonAgentProps> = ({
  pillarOutputs,
  roadmap,
  pocProposal,
  onAggregateOutputs,
  onGenerateRoadmap,
  onGeneratePOC,
  className = ''
}) => {
  const { user } = useAuth();
  // Removed deprecated experiencePillar usage
  
  const [currentGuidance, setCurrentGuidance] = useState<ExperienceGuidance | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [conversationHistory, setConversationHistory] = useState<any[]>([]);
  const [userMessage, setUserMessage] = useState('');

  // ============================================================================
  // GUIDANCE LOGIC
  // ============================================================================

  useEffect(() => {
    const analyzeExperienceState = () => {
      if (!pillarOutputs) {
        setCurrentGuidance({
          step: 'aggregate',
          message: 'Welcome to the Experience Pillar! I\'m here to help you synthesize insights from all pillars and create strategic roadmaps and POC proposals. Let\'s start by aggregating outputs from your previous pillar work.',
          suggestions: [
            'Aggregate pillar outputs',
            'Review content analysis results',
            'Synthesize insights findings',
            'Consolidate operations blueprints'
          ],
          nextAction: 'aggregate_outputs'
        });
      } else if (pillarOutputs && !roadmap) {
        setCurrentGuidance({
          step: 'roadmap',
          message: 'Excellent! You have aggregated outputs from all pillars. Now let\'s create a strategic roadmap that synthesizes your insights into actionable business outcomes.',
          suggestions: [
            'Generate strategic roadmap',
            'Create implementation timeline',
            'Define success metrics',
            'Identify resource requirements'
          ],
          nextAction: 'generate_roadmap'
        });
      } else if (roadmap && !pocProposal) {
        setCurrentGuidance({
          step: 'poc',
          message: 'Perfect! Your strategic roadmap is ready. Now let\'s create a POC (Proof of Concept) proposal that demonstrates the value and feasibility of your strategic plan.',
          suggestions: [
            'Generate POC proposal',
            'Define POC scope and objectives',
            'Create success metrics',
            'Plan resource allocation'
          ],
          nextAction: 'generate_poc'
        });
      } else if (pocProposal) {
        setCurrentGuidance({
          step: 'complete',
          message: 'Outstanding! Your experience journey is complete. You now have a comprehensive strategic roadmap and POC proposal ready for implementation and stakeholder presentation.',
          suggestions: [
            'Export complete package',
            'Create executive summary',
            'Schedule stakeholder review',
            'Begin implementation planning'
          ],
          nextAction: 'export_package'
        });
      }
    };

    analyzeExperienceState();
  }, [pillarOutputs, roadmap, pocProposal]);

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
        content: generateExperienceResponse(message),
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
    if (suggestion.includes('Aggregate') || suggestion.includes('Synthesize')) {
      return 'I can help you aggregate outputs from all pillars. This involves combining insights from content analysis, business insights, and operations optimization into a unified view of your business opportunities.';
    } else if (suggestion.includes('roadmap') || suggestion.includes('strategic')) {
      return 'Strategic roadmaps translate insights into actionable plans. I can help you create timelines, define milestones, identify dependencies, and establish success metrics for your business transformation.';
    } else if (suggestion.includes('POC') || suggestion.includes('proposal')) {
      return 'POC proposals demonstrate the value and feasibility of your strategic plan. I can help you define scope, set objectives, create success metrics, and plan resource allocation for your proof of concept.';
    } else if (suggestion.includes('Export') || suggestion.includes('package')) {
      return 'I can help you create a comprehensive package that includes your roadmap, POC proposal, and supporting documentation. This makes it easy to present to stakeholders and begin implementation.';
    }
    return 'I understand you want help with strategic planning and business outcomes. Let me guide you through the next steps.';
  };

  const generateExperienceResponse = (message: string): string => {
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes('roadmap') || lowerMessage.includes('strategic')) {
      return 'Strategic roadmaps should include clear phases, milestones, timelines, and success metrics. I can help you create a roadmap that balances ambition with feasibility and provides clear value at each stage.';
    } else if (lowerMessage.includes('poc') || lowerMessage.includes('proof of concept')) {
      return 'POC proposals should clearly define objectives, scope, success criteria, and resource requirements. I can help you create a compelling proposal that demonstrates value and feasibility to stakeholders.';
    } else if (lowerMessage.includes('business outcome') || lowerMessage.includes('value')) {
      return 'Business outcomes should be measurable and tied to strategic objectives. I can help you identify key performance indicators, success metrics, and value propositions that demonstrate ROI.';
    } else if (lowerMessage.includes('implementation') || lowerMessage.includes('execution')) {
      return 'Successful implementation requires careful planning, resource allocation, and change management. I can help you create implementation plans that ensure smooth execution and adoption.';
    } else if (lowerMessage.includes('stakeholder') || lowerMessage.includes('presentation')) {
      return 'Stakeholder communication is crucial for buy-in and support. I can help you create compelling presentations and documentation that clearly communicate value and next steps.';
    } else if (lowerMessage.includes('risk') || lowerMessage.includes('challenge')) {
      return 'Risk management is essential for successful implementation. I can help you identify potential risks, mitigation strategies, and contingency plans to ensure project success.';
    }
    
    return 'I\'m here to help with strategic planning and business outcomes! You can ask me about roadmaps, POC proposals, implementation planning, or any other experience-related questions.';
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
            isUser ? 'bg-blue-500' : 'bg-indigo-500'
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
      <Card className="border-indigo-200 bg-indigo-50">
        <CardHeader className="pb-3">
          <CardTitle className="text-indigo-800 flex items-center space-x-2">
            <Lightbulb className="w-4 h-4" />
            <span>Experience Guidance</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm text-indigo-700">{currentGuidance.message}</p>
          
          <div>
            <h4 className="font-medium text-indigo-800 mb-2">Suggested Actions:</h4>
            <div className="space-y-2">
              {currentGuidance.suggestions.map((suggestion, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="w-full text-left justify-start text-indigo-700 border-indigo-300 hover:bg-indigo-100"
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
            <span>Experience Liaison Agent</span>
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
              placeholder="Ask about strategic planning..."
              value={userMessage}
              onChange={(e) => setUserMessage(e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
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
      <div className="grid grid-cols-3 gap-2">
        <div className={`p-2 rounded-lg text-center text-xs ${
          pillarOutputs ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
        }`}>
          <Compass className="w-4 h-4 mx-auto mb-1" />
          Outputs Aggregated
        </div>
        <div className={`p-2 rounded-lg text-center text-xs ${
          roadmap ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
        }`}>
          <Map className="w-4 h-4 mx-auto mb-1" />
          Roadmap Generated
        </div>
        <div className={`p-2 rounded-lg text-center text-xs ${
          pocProposal ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
        }`}>
          <Rocket className="w-4 h-4 mx-auto mb-1" />
          POC Proposal Ready
        </div>
      </div>
    </div>
  );
};

export default ExperienceLiaisonAgent;


