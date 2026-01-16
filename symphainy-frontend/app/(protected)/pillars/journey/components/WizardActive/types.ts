// WizardActive Types
export interface ChatTurn {
  role: 'user' | 'agent';
  content: string;
}

export interface WizardActiveProps {
  onBack: () => void;
}

export interface WizardActiveState {
  chatHistory: ChatTurn[];
  input: string;
  setInput: (value: string) => void;
  loading: boolean;
  error: string | null;
  draftSop: any | null;
  published: boolean;
  publishedSop: any | null;
  publishedWorkflow: any | null;
  sessionToken: string;
}

export interface WizardActiveActions {
  handleSend: (e: React.FormEvent) => Promise<void>;
  handlePublish: () => Promise<void>;
  handleBack: () => void;
}

export interface WizardActiveUIProps {
  chatHistory: ChatTurn[];
  input: string;
  setInput: (value: string) => void;
  loading: boolean;
  error: string | null;
  draftSop: any | null;
  published: boolean;
  publishedSop: any | null;
  publishedWorkflow: any | null;
  onSend: (e: React.FormEvent) => Promise<void>;
  onPublish: () => Promise<void>;
  onBack: () => void;
}

export interface WizardChatRequest {
  sessionToken: string;
  userMessage: string;
}

export interface WizardChatResponse {
  agent_response: string;
  draft_sop?: any;
  session_token: string;
  status: 'success' | 'error';
  message?: string;
}

export interface WizardPublishRequest {
  sessionToken: string;
}

export interface WizardPublishResponse {
  sop: any;
  workflow: any;
  session_token: string;
  status: 'success' | 'error';
  message?: string;
} 