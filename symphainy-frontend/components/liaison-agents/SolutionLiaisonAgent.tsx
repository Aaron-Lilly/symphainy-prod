/**
 * Solution Liaison Agent
 * 
 * Specialized agent for the Solution realm that provides guidance on solution discovery,
 * business outcome analysis, and solution orchestration workflows.
 */

"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Target, 
  Lightbulb, 
  CheckCircle, 
  AlertCircle, 
  Bot,
  User,
  SendHorizontal,
  Loader2,
  Rocket,
  Zap,
  Eye
} from 'lucide-react';

import { useAuth } from '@/shared/auth/AuthProvider';
import { usePlatformState } from '@/shared/state/PlatformStateProvider';
import { useUnifiedAgentChat } from '@/shared/hooks/useUnifiedAgentChat';

// ============================================================================
// COMPONENT INTERFACES
// ============================================================================

interface SolutionLiaisonAgentProps {
  businessOutcome?: string;
  solutionIntent?: string;
  onSolutionCreated?: (solution: any) => void;
  className?: string;
}

interface SolutionGuidance {
  step: 'discovery' | 'analysis' | 'orchestration' | 'implementation';
  message: string;
  suggestions: string[];
  nextAction?: string;
}

// ============================================================================
// SOLUTION LIAISON AGENT COMPONENT
// ============================================================================

export const SolutionLiaisonAgent: React.FC<SolutionLiaisonAgentProps> = ({
  businessOutcome,
  solutionIntent,
  onSolutionCreated,
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
    initialPillar: 'business_outcomes'
  });
  
  const [currentGuidance, setCurrentGuidance] = useState<SolutionGuidance | null>(null);
  const [userMessage, setUserMessage] = useState('');
  
  // Switch to liaison agent on mount
  useEffect(() => {
    switchAgent('liaison', 'business_outcomes');
  }, [switchAgent]);

  // ============================================================================
  // GUIDANCE LOGIC
  // ============================================================================

  useEffect(() => {
    const analyzeSolutionState = () => {
      if (!businessOutcome) {
        setCurrentGuidance({
          step: 'discovery',
          message: 'Welcome to the Solution Discovery! I\'m here to help you define your business outcome and discover the right solution approach. Let\'s start by understanding what you want to achieve.',
          suggestions: [
            'I want to transform my call center operations',
            'I need to integrate legacy data systems',
            'I want to create an AI-powered marketing campaign',
            'I need to validate a new business concept'
          ],
          nextAction: 'define_business_outcome'
        });
      } else if (businessOutcome && !solutionIntent) {
        setCurrentGuidance({
          step: 'analysis',
          message: `Great! You've defined your business outcome: "${businessOutcome}". Now let's determine the best solution approach for your needs.`,
          suggestions: [
            'Start with an MVP (Minimum Viable Product)',
            'Create a POC (Proof of Concept) to validate the idea',
            'Build a demonstration to showcase capabilities',
            'Develop a full production solution'
          ],
          nextAction: 'select_solution_intent'
        });
      } else if (businessOutcome && solutionIntent) {
        setCurrentGuidance({
          step: 'orchestration',
          message: 'Perfect! Now I\'ll orchestrate your solution. This involves analyzing your requirements, selecting the right approach, and setting up the implementation process.',
          suggestions: [
            'Orchestrate the solution now',
            'Review the solution approach',
            'Modify the business outcome',
            'Change the solution intent'
          ],
          nextAction: 'orchestrate_solution'
        });
      }
    };

    analyzeSolutionState();
  }, [businessOutcome, solutionIntent]);

  // ============================================================================
  // EVENT HANDLERS
  // ============================================================================

  const handleSuggestionClick = async (suggestion: string) => {
    // Send suggestion as message to real-time chat
    try {
      await sendMessage(suggestion, 'liaison', 'business_outcomes');
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
      await sendMessage(message, 'liaison', 'business_outcomes');
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
            isUser ? 'bg-blue-500' : 'bg-green-500'
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
      <Card className="border-blue-200 bg-blue-50">
        <CardHeader className="pb-3">
          <CardTitle className="text-blue-800 flex items-center space-x-2">
            <Lightbulb className="w-4 h-4" />
            <span>Solution Guidance</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm text-blue-700">{currentGuidance.message}</p>
          
          <div>
            <h4 className="font-medium text-blue-800 mb-2">Suggested Actions:</h4>
            <div className="space-y-2">
              {currentGuidance.suggestions.map((suggestion, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="w-full text-left justify-start text-blue-700 border-blue-300 hover:bg-blue-100"
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
            <span>Solution Liaison Agent</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Connection Status */}
          {!isConnected && (
            <Alert>
              <AlertDescription className="text-xs">
                {chatError ? `Connection error: ${chatError}` : 'Connecting to Outcomes Liaison Agent...'}
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
              Ask me about business outcomes, solution discovery, MVPs, POCs, or strategic planning!
            </div>
          )}

          {/* Input Form */}
          <form onSubmit={handleSendMessage} className="flex space-x-2">
            <input
              type="text"
              placeholder="Ask about solution discovery..."
              value={userMessage}
              onChange={(e) => setUserMessage(e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
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
      <div className="grid grid-cols-3 gap-2">
        <div className={`p-2 rounded-lg text-center text-xs ${
          businessOutcome ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
        }`}>
          <Target className="w-4 h-4 mx-auto mb-1" />
          Business Outcome
        </div>
        <div className={`p-2 rounded-lg text-center text-xs ${
          solutionIntent ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
        }`}>
          <Rocket className="w-4 h-4 mx-auto mb-1" />
          Solution Intent
        </div>
        <div className={`p-2 rounded-lg text-center text-xs ${
          businessOutcome && solutionIntent ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
        }`}>
          <Zap className="w-4 h-4 mx-auto mb-1" />
          Ready to Orchestrate
        </div>
      </div>
    </div>
  );
};

export default SolutionLiaisonAgent;





