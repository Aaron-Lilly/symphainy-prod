import React, { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Loader2, SendHorizontal, DivideCircle } from "lucide-react";

import StreamingMessage from "./StreamingMessage";
import { useRouter } from "next/navigation";
import { WorkflowStatus } from "@/components/ui/workflow-status";
import { useGlobalSession } from "@/shared/agui/GlobalSessionProvider";
import { RuntimeClient, RuntimeEventType } from "@/shared/services/RuntimeClient";
import { getApiUrl } from "@/shared/config/api-config";



export default function ChatAssistant() {
  const router = useRouter();
  const { guideSessionToken } = useGlobalSession();
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
  const runtimeClientRef = useRef<RuntimeClient | null>(null);
  const [loading, setLoading] = useState(false);
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



  // Initialize Runtime Client
  useEffect(() => {
    if (!guideSessionToken) return;

    const baseUrl = getApiUrl();
    const client = new RuntimeClient({
      baseUrl,
      sessionToken: guideSessionToken,
      autoReconnect: true,
    });
    runtimeClientRef.current = client;

    // Subscribe to AGENT_RESPONSE events
    client.on(RuntimeEventType.AGENT_RESPONSE, (data: any) => {
      setWsMessages((prev) => [
        ...prev,
        {
          type: "agent",
          content: data.message || data.content || 'Response received',
          isStreaming: true,
          isComplete: false,
        },
      ]);
    });

    // Connect
    client.connect().then(() => {
      console.log("✅ Runtime Client connected");
    }).catch((err) => {
      console.error("❌ Runtime Client connection error", err);
    });

    return () => {
      client.disconnect();
    };
  }, [guideSessionToken]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!guideSessionToken || message.trim() === "" || !runtimeClientRef.current) return;

    setLoading(true);

    // Add user message to UI
    setWsMessages((prev) => [
      ...prev,
      { type: "user", content: message, isComplete: true },
    ]);
    setMessage("");

    try {
      // Send intent to Runtime Foundation
      runtimeClientRef.current.submitIntent({
        intent: message,
        agent_type: 'guide',
        metadata: {}
      });

      // Reset loading state after a short delay (simulating send time)
      setTimeout(() => {
        setLoading(false);
        // Simulate agent response with streaming (until real responses come through)
        simulateAgentResponse();
      }, 1000);
    } catch (err) {
      console.error("Failed to send message:", err);
      setLoading(false);
    }
  };



  const toggleChat = () => {
    setIsVisible(!isVisible);
  };

  const closeChat = () => {
    setIsVisible(false);
  };

  // Simulate agent response with streaming (dummy data for now)
  const simulateAgentResponse = () => {
    // Reset animation state for new response
    setShouldStartAnimation(false);

    const dummyResponses = [
      "I understand your query. Let me analyze the data you've provided and generate insights based on the patterns I can identify.",
      "Based on my analysis, I can see several interesting trends in your dataset. The data shows clear correlations between different variables that might be useful for your business decisions.",
      "Here are the key findings:\n\n1. Data quality appears to be high with minimal missing values\n2. There are clear seasonal patterns in the metrics\n3. Several outliers that may need investigation\n\nWould you like me to dive deeper into any of these areas?",
      "I've processed your request and here's what I found. The analysis reveals some compelling insights that could help guide your next steps in the project.",
    ];

    const randomResponse =
      dummyResponses[Math.floor(Math.random() * dummyResponses.length)];

    // Add streaming message
    setWsMessages((prev) => [
      ...prev,
      {
        type: "agent",
        content: randomResponse,
        isStreaming: true,
        isComplete: false,
      },
    ]);

    // Extract workflow info if this is a workflow response
    extractWorkflowInfo(randomResponse);
  };

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

  // Extract workflow information from agent messages
  const extractWorkflowInfo = (content: string) => {
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
