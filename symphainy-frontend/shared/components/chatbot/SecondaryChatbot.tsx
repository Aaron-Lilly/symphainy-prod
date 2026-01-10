import React, { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Loader2, SendHorizontal, DivideCircle } from "lucide-react";
import { listFiles } from "@/lib/api/fms"; // Import the working API function
import StreamingMessage from "./StreamingMessage";
import { useRouter, usePathname } from "next/navigation";
import { useAtomValue, useSetAtom } from "jotai";
import { chatbotAgentInfoAtom, mainChatbotOpenAtom } from "@/shared/atoms/chatbot-atoms";
import { getEDAAnalysis, getVisualizationAnalysis, processNaturalLanguageQuery } from "@/lib/api/insights";
import { processOperationsQuery } from "@/lib/api/operations";
import { SecondaryChatbotAgent } from "@/shared/types/secondaryChatbot";
import BusinessAnalysisDisplay from "@/components/insights/BusinessAnalysisDisplay";
import { useGlobalSession } from "@/shared/agui/GlobalSessionProvider";
import { useUnifiedAgentChat, PillarType } from "@/shared/hooks/useUnifiedAgentChat";

import { FileMetadata } from '@/shared/types/file';

/**
 * Helper function to determine pillar from route path
 */
function getPillarFromPath(pathname: string | null): PillarType | null {
  if (!pathname) return null;
  
  if (pathname.includes('/pillars/content')) return 'content';
  if (pathname.includes('/pillars/insights')) return 'insights';
  if (pathname.includes('/pillars/operation')) return 'operations';
  if (pathname.includes('/pillars/business-outcomes')) return 'business_outcomes';
  
  return null;
}

/**
 * Helper function to map agent name to pillar
 */
function getPillarFromAgent(agent: string | null): PillarType | null {
  if (!agent) return null;
  
  const agentLower = agent.toLowerCase();
  if (agentLower.includes('content')) return 'content';
  if (agentLower.includes('insight')) return 'insights';
  if (agentLower.includes('operation')) return 'operations';
  if (agentLower.includes('business') || agentLower.includes('outcome')) return 'business_outcomes';
  
  return null;
}

export default function SecondaryChatbot() {
  const agentInfo = useAtomValue(chatbotAgentInfoAtom);
  const setMainChatbotOpen = useSetAtom(mainChatbotOpenAtom);
  const { guideSessionToken } = useGlobalSession();
  const router = useRouter();
  const pathname = usePathname();

    // Determine current pillar from route or agent info
    const currentPillar = getPillarFromPath(pathname) || getPillarFromAgent(agentInfo.agent) || 'content'; // Default to content
    
    // ✅ Safety check: Only connect if authenticated and have valid session token
    const shouldConnect = guideSessionToken && 
      typeof guideSessionToken === 'string' && 
      guideSessionToken.trim() !== '' && 
      guideSessionToken !== 'token_placeholder' &&
      guideSessionToken.length > 10;
    
    // Use useUnifiedAgentChat hook (Phase 5: Unified WebSocket Architecture)
    // ✅ Option B: Defer connection until user interaction
    const {
      messages: unifiedMessages,
      sendMessage: sendUnifiedMessage,
      isConnected: unifiedConnected,
      isLoading: unifiedLoading,
      error: unifiedError,
      currentAgent,
      currentPillar: activePillar,
      switchAgent,
      clearMessages: clearUnifiedMessages,
      connect: connectWebSocket
    } = useUnifiedAgentChat({
      sessionToken: shouldConnect ? guideSessionToken : undefined,
      autoConnect: false, // ✅ Don't auto-connect - wait for user interaction
      initialAgent: 'liaison',
      initialPillar: currentPillar,
      onMessage: (message) => {
        console.log("Unified agent message received:", message);
      },
      onError: (error) => {
        console.error("Unified agent chat error:", error);
      },
      onAgentSwitch: (agentType, pillar) => {
        console.log(`Agent switched to ${agentType}${pillar ? ` (${pillar})` : ''}`);
      }
    });
    
    // Switch to liaison agent with current pillar when pillar changes
    useEffect(() => {
      if (currentPillar && (activePillar !== currentPillar || currentAgent !== 'liaison')) {
        switchAgent('liaison', currentPillar);
      }
    }, [currentPillar, activePillar, currentAgent, switchAgent]);

    const [message, setMessage] = useState("");
    const [loading, setLoading] = useState(false);
    const [files, setFiles] = useState<FileMetadata[]>([]);
    const [selectedFile, setSelectedFile] = useState<FileMetadata | null>(null);
    const [showFileSelector, setShowFileSelector] = useState(false);
    const [isVisible, setIsVisible] = useState(true);
    const [shouldStartAnimation, setShouldStartAnimation] = useState(false);
    const [agentData, setAgentData] = useState<any>(null);
    const [pillar, setPillar] = useState<string | null>(null);
    


    // Fetch files from content pillar
    useEffect(() => {
      async function fetchContentFiles() {
        try {
          // No user ID available yet; pass undefined to get all files (see backend docs)
          const userId = undefined;
          const fileList = await listFiles(userId);
          setFiles(fileList);
          console.log("Files fetched successfully:", fileList.length);
        } catch (error) {
          console.error("Failed to fetch files:", error);
          setFiles([]);
        }
      }
  
      fetchContentFiles();
    }, []);
  
    // Filter messages for current agent/pillar and convert to wsMessages format for display
    const wsMessages = unifiedMessages
      .filter(msg => 
        msg.agent_type === 'liaison' && 
        (msg.pillar === currentPillar || !msg.pillar)
      )
      .map((msg) => ({
        type: msg.role === 'user' ? 'user' as const : msg.role === 'assistant' ? 'agent' as const : 'system' as const,
        content: msg.content,
        isStreaming: false,
        isComplete: true,
        pillar: msg.pillar || currentPillar
      }));

    // Update loading state from unified chat
    useEffect(() => {
      setLoading(unifiedLoading);
    }, [unifiedLoading]);

    // Handle unified chat errors
    useEffect(() => {
      if (unifiedError) {
        console.error("Unified agent chat error:", unifiedError);
      }
    }, [unifiedError]);
  
    // ✅ Connect WebSocket when user first interacts (lazy connection)
    const mainChatbotOpen = useAtomValue(mainChatbotOpenAtom);
    useEffect(() => {
      // Connect when main chatbot is opened and we're ready
      if (shouldConnect && !unifiedConnected && !unifiedLoading && guideSessionToken && mainChatbotOpen) {
        console.log('[SecondaryChatbot] Connecting WebSocket - chat panel opened');
        connectWebSocket().catch(err => {
          console.error('[SecondaryChatbot] Failed to connect:', err);
        });
      }
    }, [shouldConnect, unifiedConnected, unifiedLoading, guideSessionToken, mainChatbotOpen, connectWebSocket]);

    const handleSend = async (e: React.FormEvent) => {
      e.preventDefault();
      
      // ✅ Connect if not already connected (lazy connection on first message)
      if (shouldConnect && !unifiedConnected && !unifiedLoading && guideSessionToken) {
        console.log('[SecondaryChatbot] Connecting WebSocket before sending message');
        await connectWebSocket();
        // Wait a moment for connection to establish
        await new Promise(resolve => setTimeout(resolve, 200));
      }
      
      if (!guideSessionToken || message.trim() === "" || !unifiedConnected) {
        if (!unifiedConnected) {
          console.error("Unified agent chat is not connected - connection may still be establishing");
        }
        return;
      }

      setLoading(true);

      try {
        // Send message via useUnifiedAgentChat hook (Phase 5: Unified WebSocket Architecture)
        await sendUnifiedMessage(message, 'liaison', currentPillar);
        setMessage("");
        console.log(`✅ Message sent to ${currentPillar} liaison agent via unified websocket`);
      } catch (error) {
        console.error("❌ Failed to send message to liaison agent:", error);
        setLoading(false);
      }
    };
  
    const handleFileSelect = (file: FileMetadata) => {
      setSelectedFile(file);
      setShowFileSelector(false);
      // File selection is handled via selectedFile state
      // User can now ask questions about the selected file
      console.log(`File selected: ${file.ui_name}`);
    };
  
    const toggleFileSelector = () => {
      const newValue = !showFileSelector;
      console.log(
        "Toggling file selector:",
        newValue,
        "Files available:",
        files.length,
      );
      setShowFileSelector(newValue);
    };
  
    const handleStreamingComplete = (messageIndex: number) => {
      // Streaming completion is handled by useUnifiedAgentChat hook
      // This function is kept for compatibility but does nothing
      console.log(`Streaming complete for message ${messageIndex}`);
  
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
        <div
        className={`w-full h-full bg-[#f3f6f8] rounded-lg shadow-md border border-[#e5eaed] flex flex-col`}
      >
        {/* Header */}
        <div className="h-[3rem] border-b rounded-lg border-[#e5eaed] bg-white">
          <div className="flex items-center">
            <h2 className="text-md text-gray-900 font-semibold pl-6 pt-3">
              <span className="gradient-chatbot">{agentInfo.title} Agent</span>
            </h2>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-3 space-y-2">
          { wsMessages.length === 0 ? (
            <div className="text-gray-500 text-xs">
              {selectedFile
                ? `Ask questions about "${selectedFile.ui_name}"`
                : "Ask me anything or select a file to analyze"}
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
        <div className="h-[3rem] pl-4 py-2 border-t border-[#e5eaed] bg-white">
          <form onSubmit={handleSend} className="flex">
            <Input
              type="text"
              placeholder={
                guideSessionToken ? "Type your message..." : "Loading session..."
              }
              className="h-[2rem] border-b border-gray-400 focus:border-gray-400 focus:ring-0 text-gray-700"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              aria-label="Type your message"
              disabled={!guideSessionToken || loading}
            />
            <Button
              type="submit"
              variant="ghost"
              className="hover:bg-transparent w-12 h-12 pb-6 px-1"
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
    )
}   