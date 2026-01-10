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

import { useAuth } from '@/shared/agui/AuthProvider';

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
  
  const [currentGuidance, setCurrentGuidance] = useState<SolutionGuidance | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [conversationHistory, setConversationHistory] = useState<any[]>([]);
  const [userMessage, setUserMessage] = useState('');

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
        content: generateSolutionResponse(message),
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
    if (suggestion.includes('transform') || suggestion.includes('call center')) {
      return 'Excellent! Call center transformation is a great use case. I can help you create an AI-powered solution that improves customer service, reduces wait times, and provides intelligent routing. Would you like to start with an MVP or create a POC first?';
    } else if (suggestion.includes('integrate') || suggestion.includes('legacy')) {
      return 'Legacy data integration is a common challenge. I can help you create a solution that connects your existing systems with modern APIs, ensuring data consistency and real-time synchronization. This typically works well as a POC to validate the integration approach.';
    } else if (suggestion.includes('marketing') || suggestion.includes('campaign')) {
      return 'AI-powered marketing campaigns are very effective! I can help you create personalized campaigns, automated content generation, and intelligent audience targeting. This works great as an MVP to test market response.';
    } else if (suggestion.includes('validate') || suggestion.includes('concept')) {
      return 'Concept validation is perfect for a POC approach. I can help you create a proof-of-concept that demonstrates the value proposition and validates the technical feasibility before full implementation.';
    } else if (suggestion.includes('MVP')) {
      return 'MVP (Minimum Viable Product) is perfect for getting started quickly. It provides core functionality to validate your business concept and gather user feedback. Typically takes 2-4 weeks to implement.';
    } else if (suggestion.includes('POC')) {
      return 'POC (Proof of Concept) is ideal for validating specific ideas or technologies. It demonstrates feasibility and value to stakeholders. Typically takes 4-8 weeks to implement.';
    } else if (suggestion.includes('demonstration') || suggestion.includes('demo')) {
      return 'A demonstration is perfect for showcasing capabilities and generating interest. It\'s quick to build (1-2 weeks) and great for presentations and stakeholder engagement.';
    }
    return 'I understand you want help with solution discovery. Let me guide you through the process to find the right approach for your business needs.';
  };

  const generateSolutionResponse = (message: string): string => {
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes('mvp') || lowerMessage.includes('minimum viable')) {
      return 'MVP solutions are perfect for validating business concepts quickly. They provide core functionality without complex features, allowing you to test market demand and gather user feedback. I can help you define the MVP scope and implementation approach.';
    } else if (lowerMessage.includes('poc') || lowerMessage.includes('proof of concept')) {
      return 'POC solutions are ideal for validating specific ideas or technologies. They demonstrate feasibility and business value to stakeholders, helping with decision-making and risk mitigation. I can guide you through the POC development process.';
    } else if (lowerMessage.includes('demo') || lowerMessage.includes('demonstration')) {
      return 'Demo solutions are perfect for showcasing capabilities and generating interest. They\'re quick to build and great for presentations, stakeholder engagement, and concept validation. I can help you create an effective demonstration.';
    } else if (lowerMessage.includes('business outcome') || lowerMessage.includes('goal')) {
      return 'A clear business outcome is the foundation of any successful solution. I can help you define specific, measurable goals that align with your business objectives. What specific problem are you trying to solve?';
    } else if (lowerMessage.includes('solution') || lowerMessage.includes('approach')) {
      return 'I can help you choose the right solution approach based on your business outcome. Whether you need an MVP, POC, demo, or full production solution, I\'ll guide you through the decision process.';
    } else if (lowerMessage.includes('orchestrate') || lowerMessage.includes('implement')) {
      return 'Solution orchestration involves analyzing your requirements, selecting the right approach, and coordinating the implementation process. I can help you orchestrate your solution from start to finish.';
    }
    
    return 'I\'m here to help with solution discovery! You can ask me about business outcomes, solution approaches (MVP, POC, Demo), or any other solution-related questions.';
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
              placeholder="Ask about solution discovery..."
              value={userMessage}
              onChange={(e) => setUserMessage(e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
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





