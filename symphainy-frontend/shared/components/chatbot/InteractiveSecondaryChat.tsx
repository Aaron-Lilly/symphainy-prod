/**
 * Interactive Secondary Chat Component
 * 
 * Contains all the interactive secondary chat functionality for liaison agents.
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
import { SecondaryChatbotAgent } from "@/shared/types/secondaryChatbot";
import BusinessAnalysisDisplay from "@/components/insights/BusinessAnalysisDisplay";
import { useUnifiedAgentChat, PillarType } from "@/shared/hooks/useUnifiedAgentChat";

export default function InteractiveSecondaryChat() {
  const agentInfo = useAtomValue(chatbotAgentInfoAtom);
  const setMainChatbotOpen = useSetAtom(mainChatbotOpenAtom);
  const mainChatbotOpen = useAtomValue(mainChatbotOpenAtom);
  const { isAuthenticated, sessionToken } = useAuth();
  const { state } = usePlatformState();
  
  // Get session token - prefer auth token (for backward compatibility), fallback to session ID
  const guideSessionToken = sessionToken || state.session.sessionId;
  const router = useRouter();
  
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

  // Determine current pillar from agent info
  const currentPillar = agentInfo.agent || "general";
  const agentType = currentPillar === "general" ? "guide" : currentPillar;
  
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
    connect: connectWebSocket
  } = useUnifiedAgentChat({
    sessionToken: shouldConnect ? guideSessionToken : undefined,
    autoConnect: false, // ✅ Don't auto-connect - wait for user interaction
    initialAgent: 'liaison',
    initialPillar: (currentPillar !== "general" ? currentPillar : undefined) as PillarType | undefined,
    onMessage: (msg) => {
      // Add agent response to chat when received from WebSocket
      setWsMessages((prev) => [
        ...prev,
        { 
          type: "agent", 
          content: msg.content || "No response", 
          isComplete: true,
          pillar: msg.pillar || currentPillar
        },
      ]);
    },
    onError: (error) => {
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
    // Filter for liaison agent messages from current pillar
    const liaisonMessages = unifiedMessages.filter(msg => 
      msg.agent_type === 'liaison' && 
      (msg.pillar === currentPillar || !msg.pillar)
    );
    
    // Update local messages with new unified messages
    if (liaisonMessages.length > 0) {
      const newMessages = liaisonMessages.map(msg => ({
        type: msg.role === 'user' ? 'user' as const : 'agent' as const,
        content: msg.content,
        isComplete: true,
        pillar: msg.pillar || currentPillar
      }));
      
      // Only add messages we don't already have
      setWsMessages(prev => {
        const existingContents = new Set(prev.map(m => m.content));
        const toAdd = newMessages.filter(m => !existingContents.has(m.content));
        return [...prev, ...toAdd];
      });
    }
  }, [unifiedMessages, currentPillar]);

  // ✅ Connect WebSocket when chat panel is opened (lazy connection)
  useEffect(() => {
    // Connect when main chatbot is opened and we're ready
    if (shouldConnect && !unifiedConnected && !unifiedLoading && guideSessionToken && mainChatbotOpen) {
      console.log('[InteractiveSecondaryChat] Connecting WebSocket - chat panel opened');
      connectWebSocket().catch(err => {
        console.error('[InteractiveSecondaryChat] Failed to connect:', err);
      });
    }
  }, [shouldConnect, unifiedConnected, unifiedLoading, guideSessionToken, mainChatbotOpen, connectWebSocket]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // ✅ Connect if not already connected (lazy connection on first message)
    if (shouldConnect && !unifiedConnected && !unifiedLoading && guideSessionToken) {
      console.log('[InteractiveSecondaryChat] Connecting WebSocket before sending message');
      await connectWebSocket();
      // Wait a moment for connection to establish
      await new Promise(resolve => setTimeout(resolve, 200));
    }
    
    // ✅ Safety check: Don't send if not authenticated or not connected
    if (!message.trim() || !shouldConnect || !guideSessionToken || !unifiedConnected) {
      if (!shouldConnect) {
        console.warn("Cannot send message: not authenticated");
      } else if (!unifiedConnected) {
        console.error("Unified agent chat is not connected - connection may still be establishing");
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
      await sendUnifiedMessage(message, 'liaison', (currentPillar !== "general" ? currentPillar : undefined) as PillarType | undefined);
      setMessage("");
      console.log(`✅ Message sent to ${currentPillar} liaison agent via unified websocket`);
    } catch (error: any) {
      console.error("❌ Failed to send message to liaison agent:", error);
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

  return (
    <>
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {wsMessages.length === 0 ? (
          <div className="text-gray-500 text-xs">
            {agentInfo.title ? 
              `Ask ${agentInfo.title} anything! I'm here to help with ${currentPillar} pillar tasks.` :
              "Ask me anything! I'm your specialist assistant."
            }
          </div>
        ) : (
          wsMessages.map((msg, idx) => (
            <div key={idx} className="flex flex-col gap-1">
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
      <div className="border-t border-[#e5eaed] p-3 bg-white">
        <form onSubmit={handleSend} className="flex gap-2">
          <Input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder={`Ask ${agentInfo.title || 'specialist'} anything...`}
            className="flex-1 text-sm"
            disabled={loading}
          />
          <Button
            type="submit"
            size="sm"
            disabled={loading || !message.trim()}
            className="px-3"
          >
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <SendHorizontal className="h-4 w-4" />
            )}
          </Button>
        </form>
      </div>
    </>
  );
}
