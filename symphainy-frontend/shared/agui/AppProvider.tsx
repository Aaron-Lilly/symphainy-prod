"use client";
import React, { createContext, useContext, useReducer, ReactNode } from "react";
import { FileMetadata } from "@/shared/types/file";
import { ChatMessage } from "@/shared/types";

// 1. Define the state shape
export interface AppState {
  files: FileMetadata[];
  isLoadingFiles: boolean;
  activePillar: "operations" | "insights" | "experience" | null;
  selectedFile: string | null;
  pillars: {
    operations: any;
    insights: any;
    experience: any;
  };
  chat: {
    wizardSessionId?: string | null;
    initialMessage?: string | null;
    chatSessionId?: string | null;
    isGuideActive?: boolean;
  };
}

// 2. Define initial state
const initialState: AppState = {
  files: [],
  isLoadingFiles: true,
  activePillar: null,
  selectedFile: null,
  pillars: {
    operations: null,
    insights: null,
    experience: null,
  },
  chat: {
    wizardSessionId: null,
    initialMessage: null,
    chatSessionId: null,
    isGuideActive: false,
  },
};

// 3. Define actions
export type AppAction =
  | { type: "SET_FILES"; payload: FileMetadata[] }
  | { type: "SET_LOADING_FILES"; payload: boolean }
  | { type: "ADD_FILE"; payload: FileMetadata }
  | { type: "REMOVE_FILE"; payload: string } // payload is file uuid
  | {
      type: "SET_PILLAR_STATE";
      payload: { pillar: keyof AppState["pillars"]; state: any };
    }
  | { type: "SET_ACTIVE_PILLAR"; payload: AppState["activePillar"] }
  | { type: "SET_SELECTED_FILE"; payload: string | null }
  | { type: "START_GUIDED_EXPERIENCE" }
  | { type: "SET_CHAT_STATE"; payload: Partial<AppState["chat"]> };

// 4. Create the reducer function
const appReducer = (state: AppState, action: AppAction): AppState => {
  switch (action.type) {
    case "SET_FILES":
      return { ...state, files: action.payload, isLoadingFiles: false };
    case "SET_LOADING_FILES":
      return { ...state, isLoadingFiles: action.payload };
    case "ADD_FILE":
      return { ...state, files: [...state.files, action.payload] };
    case "REMOVE_FILE":
      return {
        ...state,
        files: state.files.filter((file) => file.uuid !== action.payload),
      };
    case "SET_PILLAR_STATE":
      return {
        ...state,
        pillars: {
          ...state.pillars,
          [action.payload.pillar]: action.payload.state,
        },
      };
    case "SET_ACTIVE_PILLAR":
      return { ...state, activePillar: action.payload };
    case "SET_SELECTED_FILE":
      return { ...state, selectedFile: action.payload };
    case "START_GUIDED_EXPERIENCE":
      return {
        ...state,
        activePillar: "experience",
        chat: { ...state.chat, isGuideActive: true },
      };
    case "SET_CHAT_STATE":
      return {
        ...state,
        chat: {
          ...state.chat,
          ...action.payload,
        },
      };
    default:
      return state;
  }
};

// 5. Create the context and provider
interface AppContextType {
  state: AppState;
  dispatch: React.Dispatch<AppAction>;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [state, dispatch] = useReducer(appReducer, initialState);

  const value = React.useMemo(() => ({ state, dispatch }), [state, dispatch]);

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};

// 6. Create the custom hook
export const useApp = () => {
  const context = useContext(AppContext);
  if (context === undefined) {
    // During SSR, return a default context instead of throwing
    if (typeof window === 'undefined') {
      return {
        state: initialState,
        dispatch: () => {}, // No-op dispatch for SSR
      };
    }
    throw new Error("useApp must be used within an AppProvider");
  }
  return context;
};
