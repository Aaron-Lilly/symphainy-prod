"use client";

import React, {
  createContext,
  useContext,
  useState,
  useRef,
  useCallback,
  ReactNode,
} from "react";
import { ChatMessage } from "@/shared/types";

type WebSocketStatus = "connecting" | "open" | "closing" | "closed" | "error";

interface WebSocketContextType {
  messages: ChatMessage[];
  status: WebSocketStatus;
  error: string | null;
  isConnected: boolean;
  connect: (url: string) => void;
  disconnect: () => void;
  sendMessage: (content: string) => void;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(
  undefined,
);

export const WebSocketProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const socketRef = useRef<WebSocket | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [status, setStatus] = useState<WebSocketStatus>("closed");
  const [error, setError] = useState<string | null>(null);

  const disconnect = useCallback(() => {
    if (socketRef.current) {
      setStatus("closing");
      socketRef.current.close();
      socketRef.current = null;
      setMessages([]);
    }
  }, []);

  const connect = useCallback(
    (url: string) => {
      // Disconnect any existing connection before starting a new one
      if (socketRef.current) {
        disconnect();
      }

      setStatus("connecting");
      setError(null);
      setMessages([]); // Clear previous messages

      const socket = new WebSocket(url);
      socketRef.current = socket;

      socket.onopen = () => {
        console.log("[WebSocketProvider] Connection established");
        setStatus("open");
      };

      socket.onmessage = (event) => {
        try {
          const receivedMessage = JSON.parse(event.data);
          // Assuming server sends messages in ChatMessage format
          setMessages((prev) => [...prev, receivedMessage]);
        } catch (e) {
          // If it's not a JSON object, treat as a simple text message from assistant
          const fallbackMessage: ChatMessage = {
            role: "assistant",
            content: event.data,
          };
          setMessages((prev) => [...prev, fallbackMessage]);
          console.warn(
            "[WebSocketProvider] Received non-JSON message:",
            event.data,
          );
        }
      };

      socket.onerror = (err) => {
        console.error("[WebSocketProvider] WebSocket error:", err);
        setError(
          "A WebSocket connection error occurred. Check the console for details.",
        );
        setStatus("error");
      };

      socket.onclose = () => {
        console.log("[WebSocketProvider] Connection closed");
        setStatus("closed");
        socketRef.current = null;
      };
    },
    [disconnect],
  );

  const sendMessage = useCallback((content: string) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const userMessage: ChatMessage = { role: "user", content };
      // Add user message to state immediately for responsiveness
      setMessages((prev) => [...prev, userMessage]);

      // Send the message to the server
      socketRef.current.send(JSON.stringify({ type: "user_message", content }));
    } else {
      console.error(
        "[WebSocketProvider] Cannot send message, socket not open.",
      );
      setError("Cannot send message. The connection is not open.");
    }
  }, []);

  const value = React.useMemo(
    () => ({
      messages,
      status,
      error,
      isConnected: status === "open",
      connect,
      disconnect,
      sendMessage,
    }),
    [messages, status, error, connect, disconnect, sendMessage],
  );

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (context === undefined) {
    throw new Error("useWebSocket must be used within a WebSocketProvider");
  }
  return context;
};
