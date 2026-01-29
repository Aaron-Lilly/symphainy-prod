import React, { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  Send, 
  Sparkles, 
  BarChart3, 
  TrendingUp, 
  Database, 
  FileText,
  Lightbulb,
  MessageSquare,
  History,
  Download,
  Share2
} from 'lucide-react';
import { useSessionBoundary } from '@/shared/state/SessionBoundaryProvider';
// ✅ PHASE 2: Use service layer hook instead of direct API calls
import { useInsightsAPI } from '@/shared/hooks/useInsightsAPI';
import VisualizationDisplay from './VisualizationDisplay';
import { QuerySuggestions } from './QuerySuggestions';
import InsightsSummaryDisplay from './InsightsSummaryDisplay';
import SecondaryChatbot from '@/shared/components/chatbot/SecondaryChatbot';

interface ConversationalInsightsPanelProps {
  onClose?: () => void;
  className?: string;
}

interface QueryResult {
  query_id: string;
  visualization_type: string;
  agent_selected: string;
  confidence_score: number;
  parameters: any;
  visualization_url?: string;
  insights?: string;
}

interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  suggestions?: string[];
  visualization_url?: string;
}

export function ConversationalInsightsPanel({ onClose, className = '' }: ConversationalInsightsPanelProps) {
  // ✅ PHASE 1: Migrated to SessionBoundaryProvider
  // ✅ PHASE 2: Use service layer hook
  const { state: sessionState } = useSessionBoundary();
  const { processNaturalLanguageQuery, processChatMessage } = useInsightsAPI();
  
  // State management
  const [query, setQuery] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [queryResults, setQueryResults] = useState<QueryResult[]>([]);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [activeTab, setActiveTab] = useState('query');
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);

  // Example queries for suggestions
  const exampleQueries = [
    "Show me a histogram of customer ages",
    "What are the top 10 products by sales?",
    "Are there any outliers in the revenue data?",
    "Compare sales performance by region",
    "What's the correlation between price and demand?",
    "Show me trends over time for monthly revenue"
  ];

  // ✅ PHASE 2: Use service layer hook - no need to pass session_id manually
  const handleQuerySubmit = useCallback(async () => {
    if (!query.trim()) return;

    setIsProcessing(true);
    setError(null);

    // ✅ PHASE 6: Use { data, error } pattern
    const result = await processNaturalLanguageQuery({
      query: query.trim(),
      file_url: selectedFile || undefined,
      context: {
        previous_queries: queryResults.map(q => q.query_id),
        chat_history: chatMessages.length
      }
    });

    if (result.error) {
      setError(result.error.message || 'Failed to process query');
      setIsProcessing(false);
      return;
    }

    if (result.data) {
      const data = result.data as any;
      // Handle both old format (with status) and new format
      if (data.status === 'success' || data.visualization_type) {
        const newResult: QueryResult = {
          ...(data.data || data),
          insights: `Generated ${(data.data || data).visualization_type} visualization using ${(data.data || data).agent_selected} with ${Math.round(((data.data || data).confidence_score || 0) * 100)}% confidence.`
        };

        setQueryResults(prev => [newResult, ...prev]);
        setQuery('');

        // Add to chat history
        const userMessage: ChatMessage = {
          id: Date.now().toString(),
          type: 'user',
          content: query.trim(),
          timestamp: new Date()
        };

        const assistantMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          type: 'assistant',
          content: newResult.insights || 'Analysis completed successfully.',
          timestamp: new Date(),
          visualization_url: newResult.visualization_url,
          suggestions: [
            "Can you show me more details about this?",
            "What other visualizations would be helpful?",
            "Are there any patterns or trends I should know about?"
          ]
        };

        setChatMessages(prev => [...prev, userMessage, assistantMessage]);
      } else {
        setError('Failed to process query - invalid response');
      }
    }
    setIsProcessing(false);
  }, [query, selectedFile, queryResults, chatMessages, processNaturalLanguageQuery]);

  // ✅ PHASE 2: Use service layer hook - no need to check guideSessionToken
  const handleChatMessage = useCallback(async (message: string) => {
    if (!message.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: message,
      timestamp: new Date()
    };

    setChatMessages(prev => [...prev, userMessage]);

    // ✅ PHASE 6: Use { data, error } pattern
    // ✅ PHASE 2: Use service layer hook - no need to pass session_id manually
    const result = await processChatMessage({
      message: message,
      context: {
        query_history: queryResults.map(q => q.query_id),
        chat_history: chatMessages.length
      }
    });

    if (result.error) {
      setError(result.error.message || 'Failed to process message');
      return;
    }

    if (result.data) {
      const data = result.data as any;
      // Handle both old format (with status) and new format
      if (data.status === 'success' || data.response || data.message) {
        const resultData = data.data || data;
        const assistantMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          type: 'assistant',
          content: resultData.response || resultData.message || 'Response received',
          timestamp: new Date(),
          suggestions: resultData.suggestions,
          visualization_url: resultData.visualization_url
        };

        setChatMessages(prev => [...prev, assistantMessage]);
      } else {
        setError('Failed to process message - invalid response');
      }
    }
  }, [queryResults, chatMessages, processChatMessage]);

  const handleExampleQuery = useCallback((exampleQuery: string) => {
    setQuery(exampleQuery);
  }, []);

  const handleKeyPress = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleQuerySubmit();
    }
  }, [handleQuerySubmit]);

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center gap-3">
          <Sparkles className="h-6 w-6 text-purple-600" />
          <div>
            <h2 className="text-xl font-semibold">Conversational Insights</h2>
            <p className="text-sm text-gray-600">Ask questions about your data in natural language</p>
          </div>
        </div>
        {onClose && (
          <Button variant="ghost" size="sm" onClick={onClose}>
            Close
          </Button>
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 flex">
        {/* Left Panel - Query Interface */}
        <div className="w-1/2 border-r flex flex-col">
          {/* Query Input */}
          <div className="p-4 border-b">
            <div className="flex gap-2">
              <Input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask a question about your data..."
                className="flex-1"
                disabled={isProcessing}
              />
              <Button 
                onClick={handleQuerySubmit}
                disabled={isProcessing || !query.trim()}
                size="sm"
              >
                {isProcessing ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
              </Button>
            </div>
            
            {/* Example Queries */}
            <QuerySuggestions 
              suggestions={exampleQueries}
              onSuggestionClick={handleExampleQuery}
              className="mt-3"
            />
          </div>

          {/* Query Results */}
          <ScrollArea className="flex-1 p-4">
            <div className="space-y-4">
              {queryResults.map((result) => (
                <Card key={result.query_id} className="border-l-4 border-l-purple-500">
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-sm font-medium">
                        {result.visualization_type}
                      </CardTitle>
                      <div className="flex items-center gap-2">
                        <Badge variant="secondary" className="text-xs">
                          {result.agent_selected}
                        </Badge>
                        <Badge variant="outline" className="text-xs">
                          {Math.round(result.confidence_score * 100)}% confidence
                        </Badge>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="pt-0">
                    {result.visualization_url && (
                      <VisualizationDisplay 
                        title="Visualization"
                        description="Data visualization"
                        data={result}
                      />
                    )}
                    <p className="text-sm text-gray-600">{result.insights}</p>
                  </CardContent>
                </Card>
              ))}
              
              {queryResults.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <Lightbulb className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Start by asking a question about your data</p>
                  <p className="text-sm">Try one of the example queries above</p>
                </div>
              )}
            </div>
          </ScrollArea>
        </div>

        {/* Right Panel - Chat Interface */}
        <div className="w-1/2 flex flex-col">
          <SecondaryChatbot />
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="p-4 bg-red-50 border-t border-red-200">
          <p className="text-red-700 text-sm">{error}</p>
        </div>
      )}
    </div>
  );
} 