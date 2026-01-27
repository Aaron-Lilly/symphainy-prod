import React, { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Loader2, SendHorizontal, DivideCircle } from "lucide-react";
import StreamingMessage from "./StreamingMessage";
import { useRouter } from "next/navigation";
// ✅ PHASE 5: Use PlatformStateProvider instead of Jotai atoms
import { usePlatformState } from "@/shared/state/PlatformStateProvider";
import { SecondaryChatbotAgent } from "@/shared/types/secondaryChatbot";
import BusinessAnalysisDisplay from "@/components/insights/BusinessAnalysisDisplay";
import { useSessionBoundary } from "@/shared/state/SessionBoundaryProvider";
// import { useAgentManager } from "@/shared/hooks/useAgentManager";

// FileMetadata import removed - file functionality moved to pillars

export default function PrimaryChatbot() {
  const router = useRouter();
  const { state: sessionState } = useSessionBoundary();
  const guideSessionToken = sessionState.sessionId;
  // Temporarily disabled new architecture
  // const { 
  //   webSocketManager, 
  //   agentRouter, 
  //   isConnected, 
  //   isLoading: agentLoading, 
  //   error: agentError,
  //   contentAPI,
  //   sendToGuideAgent,
  //   sendToContentAgent,
  //   sendToInsightsAgent,
  //   sendToOperationsAgent,
  //   sendToExperienceAgent
  // } = useAgentManager(guideSessionToken || "", "general");
  // ✅ PHASE 5: Use PlatformStateProvider instead of Jotai atoms
  const { state, setMainChatbotOpen } = usePlatformState();
  const mainChatbotOpen = state.ui.chatbot.mainChatbotOpen;
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
  // No need for websocketRef with new architecture
  const [loading, setLoading] = useState(false);
  // File upload functionality removed - handled by pillars
  const [isVisible, setIsVisible] = useState(true);
  const [shouldStartAnimation, setShouldStartAnimation] = useState(false);
  const [agentData, setAgentData] = useState<any>(null);
  const [pillar, setPillar] = useState<string | null>(null);

  // No need for old service layer loading - useAgentManager handles this

  // Temporarily disabled - will restore with new architecture
  // useEffect(() => {
  //   async function fetchContentFiles() {
  //     try {
  //       if (!contentAPI) return;
  //       
  //       const fileList = await contentAPI.listFiles();
  //       setFiles(fileList as unknown as FileMetadata[]);
  //       console.log("Files fetched successfully:", fileList.length);
  //     } catch (error) {
  //       console.error("Failed to fetch files:", error);
  //       setFiles([]);
  //     }
  //   }

  //   if (contentAPI) {
  //     fetchContentFiles();
  //   }
  // }, [contentAPI]);

  // WebSocket connection is handled by useAgentManager
  // No need for manual connection management

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;

    setLoading(true);

    // Temporarily disabled - will restore with new architecture
    setWsMessages((prev) => [
      ...prev,
      { type: "user", content: message, isComplete: true },
    ]);

    setWsMessages((prev) => [
      ...prev,
      {
        type: "agent", 
        content: "New architecture temporarily disabled for testing", 
        isComplete: true 
      },
    ]);

    setMessage("");
    setLoading(false);
  };

  // File selection functionality removed - handled by pillars

  const handleStreamingComplete = (messageIndex: number) => {
    setWsMessages((prev) =>
      prev.map((msg, idx) =>
        idx === messageIndex
          ? { ...msg, isStreaming: false, isComplete: true }
          : msg,
      ),
    );

    // Start animation after streaming completes
    setTimeout(() => {
      setShouldStartAnimation(true);
    }, 500); // Small delay for better UX
  };

  useEffect(() => {
    if (pillar) {
      console.log("Pillar received, navigating to:", pillar);
      router.push(`/pillars/${pillar}`);
    }
  }, [pillar]);

  // Trigger animation when agentData is available
  useEffect(() => {
    if (agentData) {
      console.log("Agent data received, starting animation in 1 second...");
      setTimeout(() => {
        setShouldStartAnimation(true);
      }, 1000); // Give time for the component to render
    }
  }, [agentData]);

  return (
    <>
      {/* Chat Assistant Panel - Always Visible */}
      <div
        className={`w-full h-full bg-[#f3f6f8] border-l rounded-t-lg rounded-r-none border-[#e5eaed] flex flex-col`}
      >
        {/* Header */}
        <div className="h-[4.5rem] border-b rounded-t-lg rounded-r-none border-[#e5eaed] bg-white">
          <div className="flex items-center justify-between">
            <h2 className="text-md text-gray-900 font-semibold pl-6 pt-3">
              <span className="gradient-chatbot">Chat Assistant</span>
            </h2>
            <div className="pr-4 pt-3">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setMainChatbotOpen(!mainChatbotOpen)}
                className="text-xs"
              >
                {mainChatbotOpen ? "Switch to Specialist" : "Switch to Guide"}
              </Button>
            </div>
          </div>
          {/* File selector removed - file uploads handled by pillars */}
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-3 space-y-2">
          {wsMessages.length === 0 ? (
            <div className="text-gray-500 text-xs">
              Ask me anything! I'm here to help guide you through your business transformation.
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
                  // {/* <div className="mt-2">
                  //   {agentData === null ? (
                  //     <></>
                  //     // <div className="bg-gray-50 rounded-lg border border-gray-200 py-8 flex items-center justify-center">
                  //     //   <div className="flex flex-col items-center gap-2">
                  //     //     <LoadingDots size="md" />
                  //     //     <span className="text-xs text-gray-500">Preparing workflow diagram...</span>
                  //     //   </div>
                  //     // </div>
                  //   ) : (
                  //     <>
                  //   {/* {msg.content.split("\n").map((line, lineIdx) => (
                  //     <React.Fragment key={lineIdx}>
                  //       {line}
                  //       {lineIdx < msg.content.split("\n").length - 1 && (
                  //         <br />
                  //       )}
                  //     </React.Fragment>
                  //   ))} */}
                  // // //     <Component shouldStart={shouldStartAnimation} agentData={agentData} />
                  // //   )}
                  // // </div>
                  // // )
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
        <div className="h-[4.5rem] pl-4 py-4 border-t border-[#e5eaed] bg-white">
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
              disabled={!guideSessionToken || loading}
            />
            <Button
              type="submit"
              variant="ghost"
              className="hover:bg-transparent w-14 h-14 pb-6 px-1"
              disabled={!guideSessionToken || loading || message.trim() === ""}
            >
              {loading ? (
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
