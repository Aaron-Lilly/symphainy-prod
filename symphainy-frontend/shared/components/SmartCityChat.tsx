/**
 * Smart City Chat Component
 * React component for Smart City chat system integration
 */

import React, { useState, useEffect, useRef } from 'react';
import { smartCityWebSocketClient } from '../services/SmartCityWebSocketClient';
import { 
  ChatResponse, 
  WorkflowResponse, 
  ErrorResponse, 
  AgentType, 
  PillarType,
  isErrorResponse,
  isChatResponse,
  isWorkflowResponse
} from '../types/smart-city-api';

interface SmartCityChatProps {
  sessionToken: string;
  onMessage?: (response: ChatResponse | WorkflowResponse | ErrorResponse) => void;
  onAgentChange?: (agent: AgentType) => void;
  onPillarChange?: (pillar: PillarType) => void;
  className?: string;
}

interface ChatMessage {
  id: string;
  content: string;
  agent: AgentType;
  timestamp: string;
  isUser: boolean;
  pillar?: PillarType;
  pillarTransition?: boolean;
}

export const SmartCityChat: React.FC<SmartCityChatProps> = ({
  sessionToken,
  onMessage,
  onAgentChange,
  onPillarChange,
  className = ''
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [currentAgent, setCurrentAgent] = useState<AgentType | null>(null);
  const [currentPillar, setCurrentPillar] = useState<PillarType | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Connect to WebSocket
  useEffect(() => {
    const connectToChat = async () => {
      try {
        await smartCityWebSocketClient.connect();
        setIsConnected(true);
        
        // Send initial greeting
        await sendMessage('hello');
      } catch (error) {
        console.error('Failed to connect to Smart City chat:', error);
        setIsConnected(false);
      }
    };

    connectToChat();

    // Set up event listeners
    smartCityWebSocketClient.onConnect(() => {
      setIsConnected(true);
    });

    smartCityWebSocketClient.onDisconnect(() => {
      setIsConnected(false);
    });

    smartCityWebSocketClient.onError((error) => {
      console.error('Smart City WebSocket error:', error);
      setIsConnected(false);
    });

    smartCityWebSocketClient.onMessage((response) => {
      handleMessage(response);
    });

    // Cleanup
    return () => {
      smartCityWebSocketClient.disconnect();
    };
  }, [sessionToken]);

  const handleMessage = (response: ChatResponse | WorkflowResponse | ErrorResponse) => {
    if (isErrorResponse(response)) {
      // Handle error
      const errorMessage: ChatMessage = {
        id: Date.now().toString(),
        content: `Error: ${response.error}`,
        agent: 'guide' as AgentType,
        timestamp: new Date().toISOString(),
        isUser: false
      };
      setMessages(prev => [...prev, errorMessage]);
      setIsLoading(false);
      onMessage?.(response);
      return;
    }

    if (isChatResponse(response)) {
      // Handle chat response
      const chatMessage: ChatMessage = {
        id: Date.now().toString(),
        content: response.message,
        agent: response.agent || 'guide' as AgentType,
        timestamp: new Date().toISOString(),
        isUser: false,
        pillar: response.pillar,
        pillarTransition: false
      };
      
      setMessages(prev => [...prev, chatMessage]);
      setIsLoading(false);
      
      // Update current agent and pillar
      if (response.agent && response.agent !== currentAgent) {
        setCurrentAgent(response.agent);
        onAgentChange?.(response.agent);
      }
      
      if (response.pillar && response.pillar !== currentPillar) {
        setCurrentPillar(response.pillar);
        onPillarChange?.(response.pillar);
      }
      
      onMessage?.(response);
      return;
    }

    if (isWorkflowResponse(response)) {
      // Handle workflow response
      const workflowMessage: ChatMessage = {
        id: Date.now().toString(),
        content: `Workflow ${response.workflow_id}: ${response.status}`,
        agent: response.agent || 'guide' as AgentType,
        timestamp: new Date().toISOString(),
        isUser: false
      };
      
      setMessages(prev => [...prev, workflowMessage]);
      setIsLoading(false);
      onMessage?.(response);
      return;
    }
  };

  const sendMessage = async (message: string) => {
    if (!message.trim() || !isConnected || isLoading) return;

    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content: message,
      agent: 'guide' as AgentType,
      timestamp: new Date().toISOString(),
      isUser: true
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      await smartCityWebSocketClient.sendMessage(message, sessionToken);
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: ChatMessage = {
        id: Date.now().toString(),
        content: 'Sorry, I encountered an error. Please try again.',
        agent: 'guide' as AgentType,
        timestamp: new Date().toISOString(),
        isUser: false
      };
      setMessages(prev => [...prev, errorMessage]);
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(inputMessage);
  };

  const getAgentDisplayName = (agent: AgentType): string => {
    switch (agent) {
      case 'guide':
        return 'Guide Agent';
      case 'specialist':
        return 'Specialist';
      case 'liaison':
        return 'Liaison';
      case 'analyst':
        return 'Analyst';
      case 'orchestrator':
        return 'Orchestrator';
      default:
        return 'Agent';
    }
  };

  const getPillarDisplayName = (pillar: PillarType): string => {
    switch (pillar) {
      case 'content':
        return 'Content';
      case 'insights':
        return 'Insights';
      case 'operations':
        return 'Operations';
      case 'business-outcomes':
        return 'Business Outcomes';
      default:
        return 'Unknown';
    }
  };

  return (
    <div className={`smart-city-chat ${className}`}>
      {/* Connection Status */}
      <div className="connection-status">
        <div className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
          {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
        </div>
        {currentAgent && (
          <div className="current-agent">
            Agent: {getAgentDisplayName(currentAgent)}
          </div>
        )}
        {currentPillar && (
          <div className="current-pillar">
            Pillar: {getPillarDisplayName(currentPillar)}
          </div>
        )}
      </div>

      {/* Messages */}
      <div className="messages-container">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`message ${message.isUser ? 'user-message' : 'agent-message'}`}
          >
            <div className="message-header">
              <span className="agent-name">
                {message.isUser ? 'You' : getAgentDisplayName(message.agent)}
              </span>
              {message.pillar && !message.isUser && (
                <span className="pillar-badge">
                  {getPillarDisplayName(message.pillar)}
                </span>
              )}
              {message.pillarTransition && (
                <span className="transition-badge">
                  🔄 Transition
                </span>
              )}
              <span className="timestamp">
                {new Date(message.timestamp).toLocaleTimeString()}
              </span>
            </div>
            <div className="message-content">
              {message.content}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="message agent-message">
            <div className="message-content">
              <div className="loading-indicator">
                <span>●</span>
                <span>●</span>
                <span>●</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="input-form">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Ask me anything or select a file to analyze..."
          disabled={!isConnected || isLoading}
          className="message-input"
        />
        <button
          type="submit"
          disabled={!isConnected || isLoading || !inputMessage.trim()}
          className="send-button"
        >
          Send
        </button>
      </form>
    </div>
  );
};

export default SmartCityChat; 