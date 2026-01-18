/**
 * Operations Liaison Agent
 * 
 * Specialized agent for the Operations Pillar that provides guidance on SOP generation,
 * workflow creation, coexistence analysis, and process optimization.
 */

"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Settings, 
  Workflow, 
  FileCheck, 
  CheckCircle, 
  AlertCircle, 
  Lightbulb,
  Bot,
  User,
  SendHorizontal,
  Loader2,
  Cog,
  GitBranch,
  Target
} from 'lucide-react';
import { useAuth } from '@/shared/auth/AuthProvider';
import { usePlatformState } from '@/shared/state/PlatformStateProvider';
import { useUnifiedAgentChat } from '@/shared/hooks/useUnifiedAgentChat';

// ============================================================================
// COMPONENT INTERFACES
// ============================================================================

interface OperationsLiaisonAgentProps {
  selectedFiles?: any[];
  sopResult?: any;
  workflowResult?: any;
  coexistenceBlueprint?: any;
  onGenerateSOP?: (fileIds: string[]) => void;
  onCreateWorkflow?: (fileIds: string[]) => void;
  onAnalyzeCoexistence?: () => void;
  className?: string;
}

interface OperationsGuidance {
  step: 'select_files' | 'generate_sop' | 'create_workflow' | 'analyze_coexistence' | 'complete';
  message: string;
  suggestions: string[];
  nextAction?: string;
}

// ============================================================================
// OPERATIONS LIAISON AGENT COMPONENT
// ============================================================================

export const OperationsLiaisonAgent: React.FC<OperationsLiaisonAgentProps> = ({
  selectedFiles = [],
  sopResult,
  workflowResult,
  coexistenceBlueprint,
  onGenerateSOP,
  onCreateWorkflow,
  onAnalyzeCoexistence,
  className = ''
}) => {
  const { user } = useAuth();
  const { state } = usePlatformState();
  
  // Use real-time chat hook for liaison agent
  // Note: Using 'operations' as pillar type (may need to update to 'journey' if backend changes)
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
    initialPillar: 'operations'
  });
  
  const [currentGuidance, setCurrentGuidance] = useState<OperationsGuidance | null>(null);
  const [userMessage, setUserMessage] = useState('');
  
  // Switch to liaison agent on mount
  useEffect(() => {
    switchAgent('liaison', 'operations');
  }, [switchAgent]);

  // ============================================================================
  // GUIDANCE LOGIC
  // ============================================================================

  useEffect(() => {
    const analyzeOperationsState = () => {
      if (selectedFiles.length === 0) {
        setCurrentGuidance({
          step: 'select_files',
          message: 'Welcome to the Operations Pillar! I\'m here to help you create SOPs, workflows, and optimize your business processes. Let\'s start by selecting the files you want to work with.',
          suggestions: [
            'Select SOP documents',
            'Choose workflow files',
            'Upload process documents',
            'Import existing procedures'
          ],
          nextAction: 'select_files'
        });
      } else if (selectedFiles.length > 0 && !sopResult && !workflowResult) {
        setCurrentGuidance({
          step: 'generate_sop',
          message: `Great! You have ${selectedFiles.length} file(s) selected. Now let's generate SOPs and workflows from your documents. I recommend starting with SOP generation.`,
          suggestions: [
            'Generate comprehensive SOP',
            'Create quick SOP overview',
            'Build detailed procedures',
            'Customize SOP templates'
          ],
          nextAction: 'generate_sop'
        });
      } else if (sopResult && !workflowResult) {
        setCurrentGuidance({
          step: 'create_workflow',
          message: 'Excellent! Your SOP has been generated. Now let\'s create a workflow that implements these procedures in a structured, actionable format.',
          suggestions: [
            'Create BPMN workflow',
            'Build simple workflow',
            'Generate detailed process flow',
            'Design automation workflow'
          ],
          nextAction: 'create_workflow'
        });
      } else if (sopResult && workflowResult && !coexistenceBlueprint) {
        setCurrentGuidance({
          step: 'analyze_coexistence',
          message: 'Perfect! You now have both SOP and workflow. Let\'s analyze how they work together and create a coexistence blueprint for optimal implementation.',
          suggestions: [
            'Analyze SOP-workflow coexistence',
            'Create implementation blueprint',
            'Identify optimization opportunities',
            'Generate future state design'
          ],
          nextAction: 'analyze_coexistence'
        });
      } else if (coexistenceBlueprint) {
        setCurrentGuidance({
          step: 'complete',
          message: 'Outstanding! Your operations optimization is complete. You now have SOPs, workflows, and a coexistence blueprint ready for implementation.',
          suggestions: [
            'Proceed to Experience Pillar',
            'Export operations package',
            'Create implementation plan',
            'Schedule team training'
          ],
          nextAction: 'proceed_to_experience'
        });
      }
    };

    analyzeOperationsState();
  }, [selectedFiles, sopResult, workflowResult, coexistenceBlueprint]);

  // ============================================================================
  // EVENT HANDLERS
  // ============================================================================

  const handleSuggestionClick = async (suggestion: string) => {
    // Send suggestion as message to real-time chat
    try {
      await sendMessage(suggestion, 'liaison', 'operations');
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
      await sendMessage(message, 'liaison', 'operations');
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
            isUser ? 'bg-blue-500' : 'bg-orange-500'
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
      <Card className="border-orange-200 bg-orange-50">
        <CardHeader className="pb-3">
          <CardTitle className="text-orange-800 flex items-center space-x-2">
            <Lightbulb className="w-4 h-4" />
            <span>Operations Guidance</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm text-orange-700">{currentGuidance.message}</p>
          
          <div>
            <h4 className="font-medium text-orange-800 mb-2">Suggested Actions:</h4>
            <div className="space-y-2">
              {currentGuidance.suggestions.map((suggestion, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="w-full text-left justify-start text-orange-700 border-orange-300 hover:bg-orange-100"
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
            <span>Journey Liaison Agent</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Connection Status */}
          {!isConnected && (
            <Alert>
              <AlertDescription className="text-xs">
                {chatError ? `Connection error: ${chatError}` : 'Connecting to Journey Liaison Agent...'}
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
              Ask me about SOPs, workflows, process optimization, or automation!
            </div>
          )}

          {/* Input Form */}
          <form onSubmit={handleSendMessage} className="flex space-x-2">
            <input
              type="text"
              placeholder="Ask about operations optimization..."
              value={userMessage}
              onChange={(e) => setUserMessage(e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
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
          selectedFiles.length > 0 ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
        }`}>
          <FileCheck className="w-4 h-4 mx-auto mb-1" />
          Files Selected
        </div>
        <div className={`p-2 rounded-lg text-center text-xs ${
          sopResult ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
        }`}>
          <Settings className="w-4 h-4 mx-auto mb-1" />
          SOP Generated
        </div>
        <div className={`p-2 rounded-lg text-center text-xs ${
          workflowResult ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
        }`}>
          <GitBranch className="w-4 h-4 mx-auto mb-1" />
          Workflow Created
        </div>
        <div className={`p-2 rounded-lg text-center text-xs ${
          coexistenceBlueprint ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
        }`}>
          <Target className="w-4 h-4 mx-auto mb-1" />
          Blueprint Ready
        </div>
      </div>
    </div>
  );
};

export default OperationsLiaisonAgent;


