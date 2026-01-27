/**
 * ✅ PHASE 5: Chatbot State Hook
 * 
 * Convenience hook for accessing chatbot state from PlatformStateProvider.
 * Replaces direct Jotai atom usage.
 * 
 * Usage:
 * ```tsx
 * const { 
 *   mainChatbotOpen, 
 *   setMainChatbotOpen,
 *   agentInfo,
 *   setAgentInfo,
 *   shouldShowSecondary,
 *   primaryHeight,
 *   secondaryPosition,
 *   primaryTransform
 * } = useChatbotState();
 * ```
 */

import { usePlatformState } from '../state/PlatformStateProvider';

export function useChatbotState() {
  const { state, setMainChatbotOpen, setChatbotAgentInfo, getShouldShowSecondaryChatbot, getPrimaryChatbotHeight, getSecondaryChatbotPosition, getPrimaryChatbotTransform } = usePlatformState();

  return {
    // State
    mainChatbotOpen: state.ui.chatbot.mainChatbotOpen,
    agentInfo: state.ui.chatbot.agentInfo,
    chatInputFocused: state.ui.chatbot.chatInputFocused,
    messageComposing: state.ui.chatbot.messageComposing,
    
    // Actions
    setMainChatbotOpen,
    setAgentInfo: setChatbotAgentInfo,
    setChatInputFocused: (focused: boolean) => {
      // Will be added to provider if needed
      console.warn('setChatInputFocused not yet implemented in provider');
    },
    setMessageComposing: (composing: boolean) => {
      // Will be added to provider if needed
      console.warn('setMessageComposing not yet implemented in provider');
    },
    
    // Derived state
    shouldShowSecondary: getShouldShowSecondaryChatbot(),
    primaryHeight: getPrimaryChatbotHeight(),
    secondaryPosition: getSecondaryChatbotPosition(),
    primaryTransform: getPrimaryChatbotTransform(),
  };
}
