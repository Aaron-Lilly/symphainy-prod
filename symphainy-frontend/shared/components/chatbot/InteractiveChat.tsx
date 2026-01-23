/**
 * Interactive Chat Component
 * 
 * Contains all the interactive chat functionality with the new agent architecture.
 * This component is dynamically loaded to avoid SSR issues.
 */

"use client";

import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Loader2, SendHorizontal } from "lucide-react";
import StreamingMessage from "./StreamingMessage";
import { useRouter } from "next/navigation";
import { useAtomValue, useSetAtom } from "jotai";
import { chatbotAgentInfoAtom, mainChatbotOpenAtom } from "@/shared/atoms/chatbot-atoms";
import { useAuth } from "@/shared/auth/AuthProvider";
import { usePlatformState } from "@/shared/state/PlatformStateProvider";
import { useUnifiedAgentChat } from "@/shared/hooks/useUnifiedAgentChat";

export default function InteractiveChat() {
  const router = useRouter();
  const { isAuthenticated, sessionToken } = useAuth();
  const { state } = usePlatformState();
  
  // Get session token - prefer auth token (for backward compatibility), fallback to session ID
  const guideSessionToken = sessionToken || state.session.sessionId;
  
  const mainChatbotOpen = useAtomValue(mainChatbotOpenAtom);
  const setMainChatbotOpen = useSetAtom(mainChatbotOpenAtom);
  const [message, setMessage] = useState("");
  const [wsMessages, setWsMessages] = useState<
    {
      type: "user" | "agent" | "system";
      content: string;
      isStreaming?: boolean;
      isComplete?: boolean;
      pillar?: string;
    }[]
  >([]);
  const [loading, setLoading] = useState(false);
  const [isVisible, setIsVisible] = useState(true);
  const [shouldStartAnimation, setShouldStartAnimation] = useState(false);
  const [agentData, setAgentData] = useState<any>(null);
  const [pillar, setPillar] = useState<string | null>(null);

  // ✅ STRICT Safety check: Only use websocket if authenticated and have valid session token
  // Additional check: ensure token is substantial (not just a few characters)
  const shouldConnect = isAuthenticated && 
    !!guideSessionToken && 
    typeof guideSessionToken === 'string' && 
    guideSessionToken.trim() !== '' && 
    guideSessionToken !== 'token_placeholder' &&
    guideSessionToken.length > 10; // Ensure token is substantial
  
  // Use unified agent chat hook for real backend communication - only if authenticated
  // ✅ Option B: Defer connection until user interaction (don't auto-connect)
  const {
    messages: unifiedMessages,
    isConnected: unifiedConnected,
    sendMessage: sendUnifiedMessage,
    isLoading: unifiedLoading,
    error: unifiedError,
    connect: connectWebSocket
  } = useUnifiedAgentChat({
    sessionToken: shouldConnect ? guideSessionToken : undefined,
    autoConnect: false, // ✅ Don't auto-connect - wait for user interaction
    initialAgent: 'guide',
    onMessage: (msg) => {
      // Add agent response to chat when received from WebSocket
      setWsMessages((prev) => [
        ...prev,
        { 
          type: "agent", 
          content: msg.content || "No response", 
          isComplete: true,
          pillar: msg.pillar
        },
      ]);
    },
    onError: (error) => {
      console.error('[InteractiveChat] WebSocket error:', error);
      setWsMessages((prev) => [
        ...prev,
        { 
          type: "agent", 
          content: `Error: ${error}`, 
          isComplete: true 
        },
      ]);
    }
  });

  // Sync unified messages to local state
  useEffect(() => {
    // Filter for guide agent messages
    const guideMessages = unifiedMessages.filter(msg => msg.agent_type === 'guide');
    
    // Update local messages with new unified messages
    if (guideMessages.length > 0) {
      const newMessages = guideMessages.map(msg => ({
        type: msg.role === 'user' ? 'user' as const : 'agent' as const,
        content: msg.content,
        isComplete: true,
        pillar: msg.pillar
      }));
      
      // Only add messages we don't already have
      setWsMessages(prev => {
        const existingContents = new Set(prev.map(m => m.content));
        const toAdd = newMessages.filter(m => !existingContents.has(m.content));
        return [...prev, ...toAdd];
      });
    }
  }, [unifiedMessages]);

  // ✅ Connect WebSocket when chat panel is opened (lazy connection)
  useEffect(() => {
    // Connect when main chatbot is opened and we're ready
    if (shouldConnect && !unifiedConnected && !unifiedLoading && guideSessionToken && mainChatbotOpen) {
      console.log('[InteractiveChat] Connecting WebSocket - chat panel opened');
      connectWebSocket().catch(err => {
        console.error('[InteractiveChat] Failed to connect:', err);
      });
    }
  }, [shouldConnect, unifiedConnected, unifiedLoading, guideSessionToken, mainChatbotOpen, connectWebSocket]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // ✅ Connect if not already connected (lazy connection on first message)
    if (shouldConnect && !unifiedConnected && !unifiedLoading && guideSessionToken) {
      console.log('[InteractiveChat] Connecting WebSocket before sending message');
      try {
        await connectWebSocket();
        // Wait a moment for connection to establish
        await new Promise(resolve => setTimeout(resolve, 200));
      } catch (err) {
        console.error('[InteractiveChat] Failed to connect WebSocket:', err);
        setWsMessages((prev) => [
          ...prev,
          { 
            type: "agent", 
            content: `Error: Failed to connect to chat service. Please try again.`, 
            isComplete: true 
          },
        ]);
        return;
      }
    }
    
    // ✅ Safety check: Don't send if not authenticated or not connected
    if (!message.trim() || !shouldConnect || !guideSessionToken || !unifiedConnected) {
      if (!shouldConnect) {
        console.warn("Cannot send message: not authenticated");
      } else if (!unifiedConnected) {
        console.error("Unified agent chat is not connected - connection may still be establishing");
        setWsMessages((prev) => [
          ...prev,
          { 
            type: "agent", 
            content: `Connecting to chat service... Please wait a moment and try again.`, 
            isComplete: true 
          },
        ]);
      }
      return;
    }

    setLoading(true);

    try {
      // Add user message to chat
      setWsMessages((prev) => [
        ...prev,
        { type: "user", content: message, isComplete: true },
      ]);

      // Send message via unified WebSocket
      await sendUnifiedMessage(message, 'guide');
      setMessage("");
      console.log(`✅ Message sent to guide agent via unified websocket`);
    } catch (error: any) {
      console.error("❌ Failed to send message to guide agent:", error);
      setWsMessages((prev) => [
        ...prev,
        { 
          type: "agent", 
          content: `Error: ${error.message || "Failed to send message"}`, 
          isComplete: true 
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleStreamingComplete = (messageIndex: number) => {
    setWsMessages((prev) =>
      prev.map((msg, idx) =>
        idx === messageIndex ? { ...msg, isComplete: true } : msg
      )
    );
  };

  // Show loading state if WebSocket is connecting
  if (unifiedLoading && !unifiedConnected) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-2" />
          <p className="text-sm text-gray-500">Connecting to chat service...</p>
        </div>
      </div>
    );
  }

  // Show error state if WebSocket connection failed
  if (unifiedError && !unifiedConnected) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <p className="text-sm text-red-500 mb-2">Chat connection failed</p>
          <p className="text-xs text-gray-500">{unifiedError}</p>
          <Button 
            onClick={() => connectWebSocket()} 
            className="mt-2"
            size="sm"
          >
            Retry Connection
          </Button>
        </div>
      </div>
    );
  }

  return (
    <>
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {wsMessages.length === 0 ? (
          <div className="text-gray-500 text-xs">
            Ask me anything! I'm here to help guide you through your business transformation.
          </div>
        ) : (
          wsMessages.map((msg, idx) => (
            <div 
              key={idx} 
              data-testid={`guide-agent-message-${msg.type}`}
              data-message-id={idx}
              className="flex flex-col gap-1"
            >
              <p
                className={`text-xs text-gray-500 pr-2 ${msg.type === "user" ? "text-right" : "text-left"}`}
              >
                {msg.type === "user"
                  ? "you"
                  : msg.type === "system"
                    ? "system"
                    : "agent"}
              </p>

              {/* Render agent messages with streaming effect */}
              {msg.type === "agent" ? (
                <StreamingMessage
                  content={msg.content}
                  isComplete={msg.isComplete}
                  typingSpeed={25}
                  onComplete={() => handleStreamingComplete(idx)}
                />
              ) : (
                <div
                  className={`rounded-lg py-2 px-3 text-sm shadow-md max-w-[80%] ${
                    msg.type === "user"
                      ? "text-gray-800 ml-auto text-left"
                      : "text-gray-800 w-full text-left"
                  }`}
                >
                  <>
                    {/* Replace newlines with <br> tags for proper formatting */}
                    {msg.content.split("\n").map((line, lineIdx) => (
                      <React.Fragment key={lineIdx}>
                        {line}
                        {lineIdx < msg.content.split("\n").length - 1 && (
                          <br />
                        )}
                      </React.Fragment>
                    ))}
                  </>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Input Area */}
      <div 
        data-testid="guide-agent-input-container"
        className="border-t border-[#e5eaed] p-3 bg-white"
      >
        <form onSubmit={handleSend} className="flex gap-2">
          <Input
            data-testid="send-message-to-guide-agent"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Ask me anything..."
            className="flex-1 text-sm"
            disabled={loading || !unifiedConnected}
            aria-label="Send message to Guide Agent"
          />
          <Button
            data-testid="submit-message-to-guide-agent"
            type="submit"
            size="sm"
            disabled={loading || !message.trim() || !unifiedConnected}
            className="px-3"
            aria-label="Submit message to Guide Agent"
          >
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <SendHorizontal className="h-4 w-4" />
            )}
          </Button>
        </form>
        {!unifiedConnected && shouldConnect && (
          <p className="text-xs text-yellow-500 mt-1">
            {unifiedLoading ? "Connecting to chat service..." : "Click to connect to chat service"}
          </p>
        )}
        {unifiedError && (
          <p className="text-xs text-red-500 mt-1">{unifiedError}</p>
        )}
      </div>
    </>
  );
}
