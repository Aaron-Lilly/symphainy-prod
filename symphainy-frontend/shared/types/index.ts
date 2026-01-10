// FileMetadata is now imported from canonical types
import { FileMetadata } from './file';
export type { FileMetadata };

export interface AppState {
  files: FileMetadata[];
  isLoadingFiles: boolean;
  messages: ChatMessage[];
  activePillar: "operations" | "insights" | "experience" | null;
  selectedFile: string | null;
  chat: {
    // ... existing code ...
  };
}

export interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
  type?: "message" | "agent_response" | "user_message";
}

export interface CardData {
  id: string;
  text: string;
  x: number;
  y: number;
}

export interface ConnectionData {
  cards: CardData[];
  connections: Array<{
    source: string;
    destination: string;
  }>;
}
