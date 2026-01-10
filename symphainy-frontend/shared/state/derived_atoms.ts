/**
 * Derived Atoms for UI State Management
 * Auto-derived atoms that update based on main state changes
 */

import { atom } from 'jotai';
import { mainChatbotOpenAtom } from './core';

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

// ============================================
// Computed state atoms
// ============================================

// Combined analysis results
export const allAnalysisResultsAtom = atom((get) => {
  // This would be computed from individual analysis result atoms
  // when we implement them in the pillar-specific modules
  return {
    business: null,
    visualization: null,
    anomaly: null,
    eda: null,
  };
});

// UI state summary
export const uiStateSummaryAtom = atom((get) => {
  const mainOpen = get(mainChatbotOpenAtom);
  const shouldShowSecondary = get(shouldShowSecondaryChatbotAtom);
  
  return {
    mainChatbotOpen: mainOpen,
    secondaryChatbotVisible: shouldShowSecondary,
    primaryHeight: get(primaryChatbotHeightAtom),
    secondaryPosition: get(secondaryChatbotPositionAtom),
    primaryTransform: get(primaryChatbotTransformAtom),
  };
});

// ============================================
// State validation atoms
// ============================================

// State consistency check
export const stateConsistencyAtom = atom((get) => {
  const mainOpen = get(mainChatbotOpenAtom);
  const shouldShowSecondary = get(shouldShowSecondaryChatbotAtom);
  
  // Validate that secondary chatbot visibility is inverse of main chatbot
  const isConsistent = mainOpen === !shouldShowSecondary;
  
  return {
    isConsistent,
    mainChatbotOpen: mainOpen,
    secondaryChatbotVisible: shouldShowSecondary,
    validationMessage: isConsistent ? 'State is consistent' : 'State inconsistency detected',
  };
}); 