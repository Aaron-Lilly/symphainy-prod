"use client";

import React, { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useApp } from "@/shared/agui/AppProvider";
import { useWebSocket } from "@/shared/agui/WebSocketProvider";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Bot, User, Send, AlertTriangle } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { ChatMessage } from "@/shared/types";

function Message({ msg }: { msg: ChatMessage }) {
  const isUser = msg.role === "user";
  const Icon = isUser ? User : Bot;

  return (
    <div className={`flex items-start gap-3 ${isUser ? "justify-end" : ""}`}>
      {!isUser && <Icon className="h-6 w-6 text-primary" />}
      <div
        className={`rounded-lg px-4 py-2 max-w-[80%] ${isUser ? "bg-primary text-primary-foreground" : "bg-muted"}`}
      >
        <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
      </div>
      {isUser && <Icon className="h-6 w-6 text-muted-foreground" />}
    </div>
  );
}

export default function ChatAssistant() {
  const [input, setInput] = useState("");
  const { messages, sendMessage, status, error } = useWebSocket();
  const { state: appState } = useApp();
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollAreaRef.current) {
      // Using `setTimeout` to ensure the scroll happens after the new message is rendered
      setTimeout(() => {
        if (scrollAreaRef.current) {
          scrollAreaRef.current.scrollTo({
            top: scrollAreaRef.current.scrollHeight,
            behavior: "smooth",
          });
        }
      }, 100);
    }
  }, [messages]);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() === "" || status !== "open") return;

    // The websocket provider will handle adding the session_token
    sendMessage(input);
    setInput("");
  };

  return (
    <div className="flex flex-col h-full bg-background border rounded-lg">
      <header className="p-4 border-b flex items-center justify-between">
        <h3 className="text-lg font-semibold">Chat Assistant</h3>
        <Badge variant={status === "open" ? "default" : "destructive"}>
          {status.charAt(0).toUpperCase() + status.slice(1)}
        </Badge>
      </header>

      <ScrollArea className="flex-1 p-4" ref={scrollAreaRef as any}>
        <div className="space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-muted-foreground py-12">
              <Bot className="mx-auto h-10 w-10 mb-2" />
              <p>No messages yet. Start the conversation!</p>
            </div>
          )}
          {messages.map((msg, index) => (
            <Message key={index} msg={msg} />
          ))}
        </div>
      </ScrollArea>

      {error && (
        <div className="p-2 text-sm text-destructive-foreground bg-destructive flex items-center gap-2">
          <AlertTriangle className="h-4 w-4" />
          <p>
            <strong>Error:</strong> {error}
          </p>
        </div>
      )}

      <footer className="p-4 border-t">
        <form onSubmit={handleSend} className="flex items-center gap-2">
          <Input
            type="text"
            placeholder="Ask a question..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={status !== "open"}
            className="flex-1"
          />
          <Button type="submit" disabled={status !== "open" || !input.trim()}>
            <Send className="h-4 w-4" />
          </Button>
        </form>
      </footer>
    </div>
  );
}
