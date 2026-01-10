import React, { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ArrowRight, SendHorizontal, DivideCircle } from "lucide-react";
import { Loader } from "@/components/ui/loader";
import Component from "@/components/ui/animated-card-connections-latest";
import StreamingMessage from "./StreamingMessage";

export default function ChatAssistant() {
  const [message, setMessage] = useState("");
  const [wsMessages, setWsMessages] = useState<
    {
      type: "user" | "agent" | "system";
      content: string;
      isStreaming?: boolean;
      isComplete?: boolean;
    }[]
  >([]);
  const websocketRef = useRef<WebSocket | null>(null);
  const sessionToken = "debug-token";
  const [loading, setLoading] = useState(false);
  const [shouldStartAnimation, setShouldStartAnimation] = useState(false);

  // Open websocket connection
  useEffect(() => {
    if (!sessionToken) return;

    // Use centralized API config (NO hardcoded values)
    const { getWebSocketUrl } = require('@/shared/config/api-config');
    const wsBaseURL = getWebSocketUrl(sessionToken).replace(/\?.*$/, ''); // Remove token param for base URL
    const tokenParam = sessionToken ? `?session_token=${encodeURIComponent(sessionToken)}` : '';
    // NEW: Single WebSocket endpoint via Post Office Gateway
    const wsUrl = `${wsBaseURL}/ws${tokenParam}`;
    
    const ws = new WebSocket(wsUrl);
    websocketRef.current = ws;

    ws.onopen = () => {
      console.log("✅ WebSocket connected");
    };

    ws.onmessage = (event) => {
      // For now, using dummy simulation, but this is where real streaming would be handled
      setWsMessages((prev) => [
        ...prev,
        {
          type: "agent",
          content: event.data,
          isStreaming: true,
          isComplete: false,
        },
      ]);
    };

    ws.onclose = () => {
      console.log("❌ WebSocket disconnected");
    };

    ws.onerror = (err) => {
      console.error("WebSocket error", err);
    };

    return () => {
      ws.close();
    };
  }, [sessionToken]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!sessionToken || message.trim() === "" || !websocketRef.current) return;

    setLoading(true);

    websocketRef.current.send(message);
    setWsMessages((prev) => [
      ...prev,
      { type: "user", content: message, isComplete: true },
    ]);
    setMessage("");

    // Reset loading state after a short delay (simulating send time)
    setTimeout(() => {
      setLoading(false);
      // Simulate agent response with streaming
      simulateAgentResponse();
    }, 1000);
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

  return (
    <>
      {/* Fixed Chat Assistant Panel - Always Visible */}
      <div className="fixed bottom-0 right-0 h-[540px] w-[360px] bg-white border-l border-gray-200 rounded-t-lg rounded-r-none shadow-xl flex flex-col z-50">
        {/* Header without close button */}
        <div className="h-[60px] border-b border-gray-200 rounded-tl-lg bg-white shadow-sm">
          <div className="flex items-center">
            <h2 className="text-lg text-gray-900 font-semibold pl-5 py-3">
              <span className="gradient-chatbot">Chat Assistant</span>
            </h2>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-3 space-y-2 bg-gray-50">
          {wsMessages.length === 0 ? (
            <div className="text-chatbot">
              Ask me anything about your data and projects
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
                      <Component shouldStart={shouldStartAnimation} />
                      <br />
                    </div>
                  </>
                ) : (
                  <div
                    className={`rounded-lg py-2 px-3 shadow-md border text-chatbot ${
                      msg.type === "user"
                        ? "ml-auto text-right bg-gray-100 max-w-[80%]"
                        : "w-full text-left bg-gray-50 max-w-full"
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
        <div className="h-[70px] pl-4 py-4 border-t border-gray-200 bg-white shadow-sm">
          <form onSubmit={handleSend} className="flex">
            <Input
              type="text"
              placeholder={
                sessionToken ? "Type your message..." : "Loading session..."
              }
              className="border border-gray-300 text-chatbot bg-white"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              aria-label="Type your message"
              disabled={!sessionToken || loading}
            />
            <Button
              type="submit"
              variant="ghost"
              className="hover:bg-gray-50 w-14 h-14 pb-6 px-1 transition-colors"
              disabled={!sessionToken || loading || message.trim() === ""}
            >
              {loading ? (
                <Loader size="sm" />
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
