/**
 * Guide Agent Chat Component
 * 
 * Intelligent chat interface for the Guide Agent that provides goal analysis,
 * pillar routing, and cross-dimensional guidance throughout the MVP journey.
 */

"use client";

import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  SendHorizontal, 
  Loader2, 
  Bot, 
  User, 
  Lightbulb, 
  Navigation, 
  Target,
  MessageCircle,
  RefreshCw,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import { useGuideAgent } from '@/shared/agui/GuideAgentProvider';
import { useRouter } from 'next/navigation';

// ============================================================================
// COMPONENT INTERFACES
// ============================================================================

interface GuideAgentChatProps {
  onGoalAnalysis?: (goals: string, suggestedData: string[]) => void;
  onPillarRouting?: (pillar: string) => void;
  className?: string;
  showSuggestions?: boolean;
  maxHeight?: string;
}

// ============================================================================
// GUIDE AGENT CHAT COMPONENT
// ============================================================================

export const GuideAgentChat: React.FC<GuideAgentChatProps> = ({
  onGoalAnalysis,
  onPillarRouting,
  className = '',
  showSuggestions = true,
  maxHeight = 'h-[500px]'
}) => {
  const router = useRouter();
  const {
    state,
    sendMessage,
    clearConversation,
    getGuidance,
    initializeGuideAgent
  } = useGuideAgent();

  const {
    isInitialized,
    isConnected,
    currentGuidance,
    conversationHistory,
    isLoading,
    error
  } = state;

  const [message, setMessage] = useState('');
  const [showQuickActions, setShowQuickActions] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversationHistory]);

  // Handle pillar routing when guidance is received
  useEffect(() => {
    if (currentGuidance?.guidance?.pillar_routing && onPillarRouting) {
      onPillarRouting(currentGuidance.guidance.pillar_routing);
    }
  }, [currentGuidance, onPillarRouting]);

  // ============================================================================
  // EVENT HANDLERS
  // ============================================================================

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim() || isLoading) return;

    const userMessage = message.trim();
    setMessage('');

    try {
      // Send message to Guide Agent
      const response = await sendMessage(userMessage);

      // Handle goal analysis callback
      if (response.success && response.guidance && onGoalAnalysis) {
        onGoalAnalysis(userMessage, response.guidance.suggested_data_types);
      }
    } catch (error) {
      console.error('Failed to send message to Guide Agent:', error);
    }
  };

  const handleQuickAction = async (action: string) => {
    setShowQuickActions(false);
    try {
      await sendMessage(action);
    } catch (error) {
      console.error('Failed to send quick action to Guide Agent:', error);
    }
  };

  const handlePillarNavigation = async (pillar: string) => {
    try {
      const response = await sendMessage(`Navigate to ${pillar} pillar`);
      
      if (response.success && response.guidance?.pillar_routing) {
        router.push(`/pillars/${response.guidance.pillar_routing}`);
      }
    } catch (error) {
      console.error('Failed to navigate to pillar:', error);
    }
  };

  const handleRestartConversation = () => {
    clearConversation();
    setShowQuickActions(true);
  };

  // ============================================================================
  // QUICK ACTIONS
  // ============================================================================

  const quickActions = [
    {
      id: 'upload_files',
      label: 'Upload Files',
      description: 'Upload and process business documents',
      icon: '📁',
      action: 'I want to upload and analyze my business files'
    },
    {
      id: 'analyze_data',
      label: 'Analyze Data',
      description: 'Get insights from your data',
      icon: '📊',
      action: 'I want to analyze my business data for insights'
    },
    {
      id: 'create_workflows',
      label: 'Create Workflows',
      description: 'Build operational processes',
      icon: '⚙️',
      action: 'I want to create workflows and SOPs'
    },
    {
      id: 'generate_roadmap',
      label: 'Generate Roadmap',
      description: 'Create strategic roadmaps',
      icon: '🗺️',
      action: 'I want to generate a strategic roadmap'
    }
  ];

  // ============================================================================
  // RENDER HELPERS
  // ============================================================================

  const renderMessage = (message: any, index: number) => {
    const isUser = message.type === 'user';
    const isSystem = message.type === 'system';

    return (
      <div key={message.id || index} className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
        <div className={`flex items-start space-x-2 max-w-[80%] ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
          {/* Avatar */}
          <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
            isUser ? 'bg-blue-500' : isSystem ? 'bg-gray-500' : 'bg-green-500'
          }`}>
            {isUser ? (
              <User className="w-4 h-4 text-white" />
            ) : isSystem ? (
              <AlertCircle className="w-4 h-4 text-white" />
            ) : (
              <Bot className="w-4 h-4 text-white" />
            )}
          </div>

          {/* Message Content */}
          <div className={`rounded-lg px-4 py-2 ${
            isUser 
              ? 'bg-blue-500 text-white' 
              : isSystem 
                ? 'bg-gray-100 text-gray-800' 
                : 'bg-white border border-gray-200 text-gray-800'
          }`}>
            <p className="text-sm whitespace-pre-wrap">{message.content}</p>
            
            {/* Message Metadata */}
            {message.metadata && (
              <div className="mt-2 space-y-1">
                {message.metadata.intent && (
                  <Badge variant="outline" className="text-xs">
                    Intent: {message.metadata.intent}
                  </Badge>
                )}
                {message.metadata.confidence && (
                  <Badge variant="outline" className="text-xs ml-1">
                    Confidence: {Math.round(message.metadata.confidence * 100)}%
                  </Badge>
                )}
                {message.metadata.suggested_actions && message.metadata.suggested_actions.length > 0 && (
                  <div className="mt-2">
                    <p className="text-xs font-medium mb-1">Suggested Actions:</p>
                    <div className="flex flex-wrap gap-1">
                      {message.metadata.suggested_actions.map((action: string, idx: number) => (
                        <Badge key={idx} variant="secondary" className="text-xs">
                          {action.replace(/_/g, ' ')}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  const renderQuickActions = () => {
    if (!showQuickActions || conversationHistory.length > 0) return null;

    return (
      <div className="space-y-4">
        <div className="text-center">
          <h3 className="text-lg font-semibold text-gray-800 mb-2">What would you like to do?</h3>
          <p className="text-sm text-gray-600">Choose an option to get started, or ask me anything!</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {quickActions.map((action) => (
            <Card 
              key={action.id} 
              className="cursor-pointer hover:shadow-md transition-shadow border border-gray-200"
              onClick={() => handleQuickAction(action.action)}
            >
              <CardContent className="p-4">
                <div className="flex items-center space-x-3">
                  <span className="text-2xl">{action.icon}</span>
                  <div>
                    <h4 className="font-medium text-gray-800">{action.label}</h4>
                    <p className="text-sm text-gray-600">{action.description}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  };

  const renderCurrentGuidance = () => {
    if (!currentGuidance?.guidance) return null;

    const guidance = currentGuidance.guidance;

    return (
      <Card className="border-green-200 bg-green-50">
        <CardHeader className="pb-3">
          <CardTitle className="text-green-800 flex items-center space-x-2">
            <Lightbulb className="w-5 h-5" />
            <span>AI Guidance</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {/* Intent Analysis */}
          <div>
            <h4 className="font-medium text-green-800 mb-2">Intent Analysis</h4>
            <div className="space-y-2">
              <Badge variant="outline" className="text-green-700">
                {guidance.intent_analysis.primary_intent}
              </Badge>
              <p className="text-sm text-green-700">
                Confidence: {Math.round(guidance.intent_analysis.confidence * 100)}%
              </p>
            </div>
          </div>

          {/* Recommended Actions */}
          {guidance.recommended_actions.length > 0 && (
            <div>
              <h4 className="font-medium text-green-800 mb-2">Recommended Actions</h4>
              <ul className="space-y-1">
                {guidance.recommended_actions.map((action, index) => (
                  <li key={index} className="text-sm text-green-700 flex items-center space-x-2">
                    <CheckCircle className="w-3 h-3" />
                    <span>{action}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Pillar Routing */}
          {guidance.pillar_routing && (
            <div>
              <h4 className="font-medium text-green-800 mb-2">Suggested Navigation</h4>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePillarNavigation(guidance.pillar_routing)}
                className="text-green-700 border-green-300 hover:bg-green-100"
              >
                <Navigation className="w-4 h-4 mr-2" />
                Go to {guidance.pillar_routing} Pillar
              </Button>
            </div>
          )}

          {/* Suggested Data Types */}
          {guidance.suggested_data_types.length > 0 && (
            <div>
              <h4 className="font-medium text-green-800 mb-2">Suggested Data Types</h4>
              <div className="flex flex-wrap gap-1">
                {guidance.suggested_data_types.map((type, index) => (
                  <Badge key={index} variant="secondary" className="text-xs">
                    {type}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    );
  };

  // ============================================================================
  // MAIN RENDER
  // ============================================================================

  return (
    <div className={`bg-white rounded-lg border border-gray-200 flex flex-col ${className}`}>
      {/* Header */}
      <div className="border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
              <Bot className="w-4 h-4 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-800">AI Guide Agent</h3>
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-xs text-gray-600">
                  {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleRestartConversation}
              className="text-xs"
            >
              <RefreshCw className="w-3 h-3 mr-1" />
              Restart
            </Button>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <Alert className="m-4 border-red-200 bg-red-50">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription className="text-red-800">{error}</AlertDescription>
        </Alert>
      )}

      {/* Messages Area */}
      <div className={`flex-1 overflow-y-auto p-4 ${maxHeight}`}>
        {!isInitialized ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <Loader2 className="w-8 h-8 animate-spin text-gray-400 mx-auto mb-2" />
              <p className="text-sm text-gray-600">Initializing Guide Agent...</p>
            </div>
          </div>
        ) : conversationHistory.length === 0 ? (
          renderQuickActions()
        ) : (
          <div className="space-y-4">
            {conversationHistory.map((message, index) => renderMessage(message, index))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="flex items-center space-x-2 bg-gray-100 rounded-lg px-4 py-2">
                  <Loader2 className="w-4 h-4 animate-spin text-gray-400" />
                  <span className="text-sm text-gray-600">AI is thinking...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Current Guidance */}
      {currentGuidance?.guidance && (
        <div className="border-t border-gray-200 p-4">
          {renderCurrentGuidance()}
        </div>
      )}

      {/* Input Area */}
      <div className="border-t border-gray-200 p-4">
        <form onSubmit={handleSendMessage} className="flex space-x-2">
          <Input
            type="text"
            placeholder={isInitialized ? "Ask me anything or describe your goals..." : "Initializing..."}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            disabled={!isInitialized || isLoading}
            className="flex-1"
          />
          <Button
            type="submit"
            disabled={!isInitialized || isLoading || !message.trim()}
            className="px-4"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <SendHorizontal className="w-4 h-4" />
            )}
          </Button>
        </form>
      </div>
    </div>
  );
};

export default GuideAgentChat;

