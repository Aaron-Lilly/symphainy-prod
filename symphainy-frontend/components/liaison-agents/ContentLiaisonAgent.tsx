/**
 * Content Liaison Agent
 * 
 * Specialized agent for the Content Pillar that provides guidance on file upload,
 * parsing, metadata extraction, and content management workflows.
 */

"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Lightbulb,
  Bot,
  User,
  SendHorizontal,
  Loader2
} from 'lucide-react';

import { useAuth } from '@/shared/auth/AuthProvider';
import { usePlatformState } from '@/shared/state/PlatformStateProvider';
import { useUnifiedAgentChat } from '@/shared/hooks/useUnifiedAgentChat';

// ============================================================================
// COMPONENT INTERFACES
// ============================================================================

interface ContentLiaisonAgentProps {
  selectedFile?: any;
  parseResult?: any;
  metadata?: any;
  onFileUpload?: (file: File, fileType: string) => void;
  onParseFile?: (fileId: string) => void;
  onExtractMetadata?: (fileId: string) => void;
  className?: string;
}

interface ContentGuidance {
  step: 'upload' | 'parse' | 'metadata' | 'complete';
  message: string;
  suggestions: string[];
  nextAction?: string;
}

// ============================================================================
// CONTENT LIAISON AGENT COMPONENT
// ============================================================================

export const ContentLiaisonAgent: React.FC<ContentLiaisonAgentProps> = ({
  selectedFile,
  parseResult,
  metadata,
  onFileUpload,
  onParseFile,
  onExtractMetadata,
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
    initialPillar: 'content'
  });
  
  const [currentGuidance, setCurrentGuidance] = useState<ContentGuidance | null>(null);
  const [userMessage, setUserMessage] = useState('');
  
  // Switch to liaison agent on mount
  useEffect(() => {
    switchAgent('liaison', 'content');
  }, [switchAgent]);

  // ============================================================================
  // GUIDANCE LOGIC
  // ============================================================================

  useEffect(() => {
    const analyzeContentState = () => {
      if (!selectedFile && !parseResult && !metadata) {
        setCurrentGuidance({
          step: 'upload',
          message: 'Welcome to the Content Pillar! I\'m here to help you upload and process your business files. Let\'s start by uploading a file.',
          suggestions: [
            'Upload a PDF document',
            'Upload a Word document',
            'Upload a CSV file',
            'Upload an Excel spreadsheet'
          ],
          nextAction: 'upload_file'
        });
      } else if (selectedFile && !parseResult && !metadata) {
        setCurrentGuidance({
          step: 'parse',
          message: `Great! You've uploaded "${selectedFile.ui_name}". Now let's parse it to extract structured data.`,
          suggestions: [
            'Parse the file into structured format',
            'Extract text content',
            'Analyze document structure',
            'Prepare for metadata extraction'
          ],
          nextAction: 'parse_file'
        });
      } else if (selectedFile && parseResult && !metadata) {
        setCurrentGuidance({
          step: 'metadata',
          message: 'Excellent! Your file has been parsed successfully. Now let\'s extract metadata and insights from the content.',
          suggestions: [
            'Extract metadata and insights',
            'Analyze content keywords',
            'Identify key entities',
            'Generate content summary'
          ],
          nextAction: 'extract_metadata'
        });
      } else if (selectedFile && parseResult && metadata) {
        setCurrentGuidance({
          step: 'complete',
          message: 'Perfect! Your content processing is complete. You now have structured data and insights ready for analysis.',
          suggestions: [
            'Proceed to Insights Pillar',
            'Upload additional files',
            'Review extracted metadata',
            'Export processed data'
          ],
          nextAction: 'proceed_to_insights'
        });
      }
    };

    analyzeContentState();
  }, [selectedFile, parseResult, metadata]);

  // ============================================================================
  // EVENT HANDLERS
  // ============================================================================

  const handleSuggestionClick = async (suggestion: string) => {
    // Send suggestion as message to real-time chat
    try {
      await sendMessage(suggestion, 'liaison', 'content');
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
      await sendMessage(message, 'liaison', 'content');
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
            <span>Content Guidance</span>
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
            <span>Content Liaison Agent</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Connection Status */}
          {!isConnected && (
            <Alert>
              <AlertDescription className="text-xs">
                {chatError ? `Connection error: ${chatError}` : 'Connecting to Content Liaison Agent...'}
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
              Ask me about content processing, file uploads, parsing, or metadata extraction!
            </div>
          )}

          {/* Input Form */}
          <form onSubmit={handleSendMessage} className="flex space-x-2">
            <input
              type="text"
              placeholder="Ask about content processing..."
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
    </div>
  );
};

export default ContentLiaisonAgent;






























