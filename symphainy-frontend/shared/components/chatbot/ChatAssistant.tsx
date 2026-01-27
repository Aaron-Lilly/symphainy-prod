import React, { useState, useEffect, useRef, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Loader2, SendHorizontal, DivideCircle } from "lucide-react";

import StreamingMessage from "./StreamingMessage";
import { useRouter } from "next/navigation";
import { WorkflowStatus } from "@/components/ui/workflow-status";
import { useSessionBoundary } from "@/shared/state/SessionBoundaryProvider";
// ✅ PHASE 3: WebSocket Consolidation - Use useUnifiedAgentChat instead of direct RuntimeClient
import { useUnifiedAgentChat } from "@/shared/hooks/useUnifiedAgentChat";



export default function ChatAssistant() {
  const router = useRouter();
  const { state: sessionState } = useSessionBoundary();
  const guideSessionToken = sessionState.sessionId;
  
  // ✅ PHASE 3: WebSocket Consolidation - Use useUnifiedAgentChat instead of direct RuntimeClient
  const {
    messages: unifiedMessages,
    sendMessage: sendUnifiedMessage,
    isConnected: unifiedConnected,
    isLoading: unifiedLoading,
    error: unifiedError,
    connect: connectWebSocket,
  } = useUnifiedAgentChat({
    sessionToken: guideSessionToken,
    autoConnect: false, // Don't auto-connect - wait for user interaction
    initialAgent: 'guide',
  });

  const [message, setMessage] = useState("");
  const [isVisible, setIsVisible] = useState(true);
  const [shouldStartAnimation, setShouldStartAnimation] = useState(false);
  const [agentData, setAgentData] = useState<any>(null);
  const [pillar, setPillar] = useState<string | null>(null);
  const [workflowStatus, setWorkflowStatus] = useState<{
    workflowId: string;
    fileName: string;
    status: "processing" | "completed" | "error" | "pending";
    startedAt?: string;
    completedAt?: string;
    estimatedDuration?: number;
  } | null>(null);

  // ✅ PHASE 3: Convert unified messages to wsMessages format for display
  const wsMessages = unifiedMessages.map((msg) => ({
    type: msg.role === 'user' ? 'user' as const : msg.role === 'assistant' ? 'agent' as const : 'system' as const,
    content: msg.content,
    isStreaming: false,
    isComplete: true,
    pillar: msg.pillar,
  }));

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!guideSessionToken || message.trim() === "") return;

    // ✅ PHASE 3: Connect if not connected
    if (!unifiedConnected) {
      try {
        await connectWebSocket();
      } catch (err) {
        console.error("Failed to connect WebSocket:", err);
        return;
      }
    }

    try {
      // ✅ PHASE 3: Send message via useUnifiedAgentChat
      await sendUnifiedMessage(message, 'guide');
      setMessage("");
    } catch (err) {
      console.error("Failed to send message:", err);
    }
  };



  const toggleChat = () => {
    setIsVisible(!isVisible);
  };

  const closeChat = () => {
    setIsVisible(false);
  };

  // ✅ PHASE 3: Extract workflow information from agent messages
  const extractWorkflowInfo = useCallback((content: string) => {
    const workflowIdMatch = content.match(/🆔 Workflow ID: ([^\n]+)/);
    const fileNameMatch = content.match(/📁 File: ([^\n]+)/);
    const statusMatch = content.match(/📊 Status: ([^\n]+)/);
    
    if (workflowIdMatch && fileNameMatch) {
      const workflowId = workflowIdMatch[1].trim();
      const fileName = fileNameMatch[1].trim();
      const status = statusMatch ? statusMatch[1].trim() : "processing";
      
      // Determine if this is a workflow start message
      if (content.includes("✅ Processing") || content.includes("✅ File processing")) {
        setWorkflowStatus({
          workflowId,
          fileName,
          status: "processing" as const,
          startedAt: new Date().toISOString(),
          estimatedDuration: 30 // Default estimate
        });
      }
    }
  }, [setWorkflowStatus]);

  // ✅ PHASE 3: Extract workflow info from agent messages
  useEffect(() => {
    unifiedMessages.forEach((msg) => {
      if (msg.role === 'assistant' && msg.content) {
        extractWorkflowInfo(msg.content);
      }
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [unifiedMessages]);

  const handleStreamingComplete = (messageIndex: number) => {
    // ✅ PHASE 3: Messages are managed by useUnifiedAgentChat
    // Start animation after streaming completes
    setTimeout(() => {
      setShouldStartAnimation(true);
    }, 500); // Small delay for better UX
  };

  return (
    <>
      {/* Always visible chat tab - slides with the panel */}
      <div
        className={`fixed top-1/4 transform -translate-y-1/3 z-40 transition-all duration-300 ease-in-out ${isVisible ? "right-[360px]" : "right-0"}
        ${isVisible ? "w-1" : "w-8"}`}
      >
        <Button
          onClick={toggleChat}
          className={`h-14 rounded-l-lg rounded-r-none bg-[#007A87] hover:bg-[#006571] text-white shadow-lg transition-all duration-300 flex flex-col items-center justify-center
          aria-label="Toggle Chat Assistant`}
        >
          <span className={`${isVisible ? "" : "w-5 h-5"} pr-1`}>💬</span>
          <span className="text-xs writing-mode-vertical transform rotate-90 whitespace-nowrap origin-center" />
        </Button>
      </div>

      {/* Chat Assistant Panel */}
      <div
        className={`fixed bottom-0 right-0 h-[530px] w-[350px] bg-[#f3f6f8] border-l rounded-t-lg rounded-r-none border-[#e5eaed] flex flex-col z-50 transition-transform duration-300 ease-in-out ${
          isVisible ? "translate-x-0" : "translate-x-full"
        }`}
      >
        {/* Header without close button */}
        <div className="h-[70px] border-b  rounded-t-lg rounded-r-none border-[#e5eaed] bg-white">
          <div className="flex items-center">
            <h2 className="text-md text-gray-900  font-semibold pl-6 pt-3">
              Chat Assistant
            </h2>
          </div>

        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-3 space-y-2">
          {wsMessages.length === 0 ? (
            <div className="text-gray-500 text-sm">
              Ask me anything!
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
                  <>
                    <StreamingMessage
                      content={msg.content}
                      isComplete={msg.isComplete}
                      typingSpeed={25}
                      onComplete={() => handleStreamingComplete(idx)}
                    />
                    <div
                      className={`transition-all duration-300 ${
                        !shouldStartAnimation
                          ? "opacity-30 pointer-events-none grayscale"
                          : "opacity-100 pointer-events-auto"
                      }`}
                      aria-disabled={!shouldStartAnimation}
                    >
                      <br />
                      {/* Component removed - was causing import issues */}
                      <br />
                    </div>
                  </>
                ) : (
                  <div
                    className={`rounded-lg py-2 px-3 shadow-md max-w-[80%] ${
                      msg.type === "user"
                        ? "text-gray-800 text-sm ml-auto text-right"
                        : "text-gray-800 w-full text-center"
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

        {/* Workflow Status Display */}
        {workflowStatus && (
          <div className="p-3 border-t border-gray-200 bg-gray-50">
            <WorkflowStatus
              workflowId={workflowStatus.workflowId}
              fileName={workflowStatus.fileName}
              status={workflowStatus.status}
              startedAt={workflowStatus.startedAt}
              completedAt={workflowStatus.completedAt}
              estimatedDuration={workflowStatus.estimatedDuration}
              onRefresh={() => {
                // TODO: Implement status refresh
                console.log("Refreshing workflow status...");
              }}
            />
          </div>
        )}

        {/* Input Area */}
        <div className="h-[70px] pl-4 py-4 border-t border-[#e5eaed] bg-white">
          <form onSubmit={handleSend} className="flex">
            <Input
              type="text"
              placeholder={
                guideSessionToken ? "Type your message..." : "Loading session..."
              }
              className="border-b border-gray-400 focus:border-gray-400 focus:ring-0 text-gray-700"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              aria-label="Type your message"
              disabled={!guideSessionToken || unifiedLoading}
            />
            <Button
              type="submit"
              variant="ghost"
              className="hover:bg-transparent w-14 h-14 pb-6 px-1"
              disabled={!guideSessionToken || unifiedLoading || message.trim() === ""}
            >
              {unifiedLoading ? (
                <Loader2 className="animate-spin text-[#007A87]" />
              ) : (
                <SendHorizontal className="text-[#007A87] hover:text-[#006571]" />
              )}
            </Button>
          </form>
        </div>
      </div>
    </>
  );
}
