import { atom } from 'jotai';

// ============================================
// Chatbot State Atoms - Simplified single source of truth
// ============================================

// 🎯 SINGLE SOURCE OF TRUTH - Only atom you need to use/set
export const mainChatbotOpenAtom = atom(true);
export const chatbotAgentInfoAtom = atom({
    title: "",
    agent: "",
    file_url: "",
    additional_info: "",
});

// ============================================
// Auto-derived atoms - Update automatically when mainChatbotOpenAtom changes
// ============================================

// Secondary chatbot visibility (auto-derived)
export const shouldShowSecondaryChatbotAtom = atom((get) => {
  return !get(mainChatbotOpenAtom);
});

// Primary chatbot height (auto-derived)
export const primaryChatbotHeightAtom = atom((get) => {
  const mainOpen = get(mainChatbotOpenAtom);
  return mainOpen ? 'h-[87vh]' : 'h-[30vh]';
});

// Secondary chatbot position (auto-derived)
export const secondaryChatbotPositionAtom = atom((get) => {
  const mainOpen = get(mainChatbotOpenAtom);
  
  if (mainOpen) {
    return 'translate-x-full opacity-0'; // Hidden off-screen
  } else {
    return 'translate-x-0 opacity-100'; // Visible at normal position
  }
});

// Primary chatbot transform (auto-derived)
export const primaryChatbotTransformAtom = atom((get) => {
  const mainOpen = get(mainChatbotOpenAtom);
  
  if (mainOpen) {
    return 'translate-y-0'; // Normal position
  } else {
    return 'translate-y-[20vh]'; // Slide down to make space for secondary
  }
});

// Additional UI state atoms (optional)
export const chatInputFocusedAtom = atom(false);
export const messageComposingAtom = atom(false);

// ============================================
// Analysis Results Atoms - Shared between chatbot and page components
// ============================================

// Shared analysis results atoms for cross-component communication
export const businessAnalysisResultAtom = atom<any>(null);
export const visualizationResultAtom = atom<any>(null);
export const anomalyDetectionResultAtom = atom<any>(null);
export const edaAnalysisResultAtom = atom<any>(null);
