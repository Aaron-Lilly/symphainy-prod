"use client";

import React, { useState, useEffect, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  MessageCircle, 
  Send, 
  Bot, 
  User, 
  Loader, 
  AlertTriangle,
  Lightbulb,
  Settings
} from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";

interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: string;
  agent?: "guide" | "specialist";
}

interface DualAgentChatProps {
  sessionToken?: string;
  onContextUpdate?: (context: any) => void;
}

export default function DualAgentChat({ sessionToken, onContextUpdate }: DualAgentChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeAgent, setActiveAgent] = useState<"guide" | "specialist">("guide");
  const [isConnected, setIsConnected] = useState(false);
  const [websocket, setWebsocket] = useState<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Initialize WebSocket connection
  useEffect(() => {
    if (!sessionToken) return;

    const wsUrl = activeAgent === "guide" 
      ? `ws://localhost/ws?session_token=${sessionToken || ''}&channel=guide`
      : `ws://localhost/ws?session_token=${sessionToken || ''}&channel=specialist`;

    const ws = new WebSocket(wsUrl);
    setWebsocket(ws);

    ws.onopen = () => {
      console.log(`Connected to ${activeAgent} WebSocket`);
      setIsConnected(true);
      setError(null);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.type === "agent_message") {
          const newMessage: ChatMessage = {
            id: Date.now().toString(),
            role: "assistant",
            content: data.data.response || "No response received",
            timestamp: new Date().toISOString(),
            agent: activeAgent
          };
          
          setMessages(prev => [...prev, newMessage]);
          
          // Update context if provided
          if (data.data.context && onContextUpdate) {
            onContextUpdate(data.data.context);
          }
        } else if (data.type === "error") {
          setError(data.message || "An error occurred");
        }
      } catch (e) {
        console.error("Error parsing WebSocket message:", e);
        setError("Failed to parse server response");
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      setError("WebSocket connection error");
      setIsConnected(false);
    };

    ws.onclose = () => {
      console.log("WebSocket connection closed");
      setIsConnected(false);
    };

    return () => {
      ws.close();
    };
  }, [activeAgent, sessionToken, onContextUpdate]);

  const sendMessage = async () => {
    if (!inputMessage.trim() || !websocket || !isConnected) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content: inputMessage,
      timestamp: new Date().toISOString(),
      agent: activeAgent
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage("");
    setIsLoading(true);
    setError(null);

    try {
      const messageData = {
        user_id: sessionToken || "anonymous",
        message: inputMessage,
        session_token: sessionToken,
        additional_info: ""
      };

      websocket.send(JSON.stringify(messageData));
    } catch (error) {
      console.error("Error sending message:", error);
      setError("Failed to send message");
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const switchAgent = (agent: "guide" | "specialist") => {
    setActiveAgent(agent);
    setMessages([]); // Clear messages when switching agents
  };

  const getAgentInfo = (agent: "guide" | "specialist") => {
    return agent === "guide" 
      ? {
          name: "Experience Guide",
          description: "Friendly guide for business planning and strategy",
          icon: <Lightbulb className="h-4 w-4" />
        }
      : {
          name: "Experience Specialist", 
          description: "Technical expert for implementation details",
          icon: <Settings className="h-4 w-4" />
        };
  };

  const currentAgentInfo = getAgentInfo(activeAgent);

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center space-x-2">
            <MessageCircle className="h-5 w-5" />
            <span>AI Guidance</span>
          </CardTitle>
          <div className="flex space-x-2">
            <Button
              variant={activeAgent === "guide" ? "default" : "outline"}
              size="sm"
              onClick={() => switchAgent("guide")}
              className="flex items-center space-x-1"
            >
              <Lightbulb className="h-3 w-3" />
              <span>Guide</span>
            </Button>
            <Button
              variant={activeAgent === "specialist" ? "default" : "outline"}
              size="sm"
              onClick={() => switchAgent("specialist")}
              className="flex items-center space-x-1"
            >
              <Settings className="h-3 w-3" />
              <span>Specialist</span>
            </Button>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          {currentAgentInfo.icon}
          <div>
            <p className="text-sm font-medium">{currentAgentInfo.name}</p>
            <p className="text-xs text-muted-foreground">{currentAgentInfo.description}</p>
          </div>
          <Badge variant={isConnected ? "default" : "secondary"} className="ml-auto">
            {isConnected ? "Connected" : "Disconnected"}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col space-y-4">
        {/* Messages Area */}
        <ScrollArea className="flex-1 border rounded-lg p-4 min-h-[300px]">
          <div className="space-y-4">
            {messages.length === 0 ? (
              <div className="text-center text-muted-foreground py-8">
                <MessageCircle className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p>Start a conversation with the {currentAgentInfo.name}</p>
                <p className="text-xs mt-1">
                  {activeAgent === "guide" 
                    ? "Ask about business objectives, planning, or strategy"
                    : "Ask about technical implementation, architecture, or requirements"
                  }
                </p>
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg p-3 ${
                      message.role === "user"
                        ? "bg-blue-500 text-white"
                        : "bg-gray-100 text-gray-900"
                    }`}
                  >
                    <div className="flex items-center space-x-2 mb-1">
                      {message.role === "user" ? (
                        <User className="h-3 w-3" />
                      ) : (
                        <Bot className="h-3 w-3" />
                      )}
                      <span className="text-xs opacity-70">
                        {message.agent === "guide" ? "Guide" : "Specialist"}
                      </span>
                    </div>
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                    <p className="text-xs opacity-70 mt-1">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))
            )}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 rounded-lg p-3">
                  <div className="flex items-center space-x-2">
                    <Loader className="h-4 w-4 animate-spin" />
                    <span className="text-sm">Thinking...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </ScrollArea>

        {/* Error Display */}
        {error && (
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Input Area */}
        <div className="flex space-x-2">
          <Input
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={`Message the ${currentAgentInfo.name}...`}
            disabled={!isConnected || isLoading}
            className="flex-1"
          />
          <Button
            onClick={sendMessage}
            disabled={!inputMessage.trim() || !isConnected || isLoading}
            size="icon"
          >
            {isLoading ? (
              <Loader className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
} 