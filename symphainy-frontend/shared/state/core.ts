/**
 * Core State Management
 * Handles core state management logic for the application
 */

import { atom } from 'jotai';

// ============================================
// Core State Atoms - Single source of truth
// ============================================

// Main chatbot state
export const mainChatbotOpenAtom = atom(true);

// Chatbot agent information
export const chatbotAgentInfoAtom = atom({
  title: "",
  agent: "",
  file_url: "",
  additional_info: "",
});

// UI state atoms
export const chatInputFocusedAtom = atom(false);
export const messageComposingAtom = atom(false);

// Analysis results atoms for cross-component communication
export const businessAnalysisResultAtom = atom<any>(null);
export const visualizationResultAtom = atom<any>(null);
export const anomalyDetectionResultAtom = atom<any>(null);
export const edaAnalysisResultAtom = atom<any>(null);

// ============================================
// State Management Utilities
// ============================================

export interface StateManager {
  getMainChatbotState(): boolean;
  setMainChatbotState(open: boolean): void;
  getAgentInfo(): any;
  setAgentInfo(info: any): void;
  getAnalysisResults(): Record<string, any>;
  setAnalysisResult(type: string, result: any): void;
  resetAnalysisResults(): void;
}

export class ApplicationStateManager implements StateManager {
  private mainChatbotOpen: boolean = true;
  private agentInfo: any = {
    title: "",
    agent: "",
    file_url: "",
    additional_info: "",
  };
  private analysisResults: Record<string, any> = {};

  getMainChatbotState(): boolean {
    return this.mainChatbotOpen;
  }

  setMainChatbotState(open: boolean): void {
    this.mainChatbotOpen = open;
  }

  getAgentInfo(): any {
    return { ...this.agentInfo };
  }

  setAgentInfo(info: any): void {
    this.agentInfo = { ...this.agentInfo, ...info };
  }

  getAnalysisResults(): Record<string, any> {
    return { ...this.analysisResults };
  }

  setAnalysisResult(type: string, result: any): void {
    this.analysisResults[type] = result;
  }

  resetAnalysisResults(): void {
    this.analysisResults = {};
  }
} 