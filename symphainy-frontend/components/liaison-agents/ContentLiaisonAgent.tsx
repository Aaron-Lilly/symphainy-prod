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

import { useAuth } from '@/shared/agui/AuthProvider';

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
  
  
  const [currentGuidance, setCurrentGuidance] = useState<ContentGuidance | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [conversationHistory, setConversationHistory] = useState<any[]>([]);
  const [userMessage, setUserMessage] = useState('');

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
        content: generateContentResponse(message),
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
    if (suggestion.includes('Upload')) {
      return 'I can help you upload files! Make sure to select the appropriate file type (PDF, DOCX, CSV, etc.) for best results. The system will automatically detect the content and prepare it for processing.';
    } else if (suggestion.includes('Parse')) {
      return 'Parsing will convert your file into a structured format that our AI can analyze. This process extracts text, identifies sections, and prepares the content for metadata extraction.';
    } else if (suggestion.includes('Extract') || suggestion.includes('metadata')) {
      return 'Metadata extraction will analyze your content to identify key themes, entities, and insights. This creates a rich understanding of your document that can be used for further analysis.';
    } else if (suggestion.includes('Proceed')) {
      return 'Great! Your content is ready for the Insights Pillar. The structured data and metadata will be used to generate business insights and recommendations.';
    }
    return 'I understand you want help with content processing. Let me guide you through the next steps.';
  };

  const generateContentResponse = (message: string): string => {
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes('upload') || lowerMessage.includes('file')) {
      return 'To upload a file, use the file uploader above. I recommend starting with a PDF or Word document. The system supports PDF, DOCX, CSV, and Excel files.';
    } else if (lowerMessage.includes('parse') || lowerMessage.includes('structure')) {
      return 'Parsing converts your file into structured data. This process identifies headings, paragraphs, tables, and other elements to create a machine-readable format.';
    } else if (lowerMessage.includes('metadata') || lowerMessage.includes('insight')) {
      return 'Metadata extraction analyzes your content to identify key themes, entities, keywords, and insights. This creates a comprehensive understanding of your document.';
    } else if (lowerMessage.includes('error') || lowerMessage.includes('problem')) {
      return 'I can help troubleshoot content processing issues. Common problems include unsupported file formats, corrupted files, or network issues. Let me know what specific error you\'re seeing.';
    } else if (lowerMessage.includes('format') || lowerMessage.includes('type')) {
      return 'Supported file formats include: PDF documents, Word documents (.docx), CSV files, Excel spreadsheets (.xlsx), and plain text files. Each format is processed differently for optimal results.';
    }
    
    return 'I\'m here to help with content processing! You can ask me about file uploads, parsing, metadata extraction, or any other content-related questions.';
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
              placeholder="Ask about content processing..."
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
    </div>
  );
};

export default ContentLiaisonAgent;






























