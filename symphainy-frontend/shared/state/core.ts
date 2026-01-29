/**
 * Core State Management
 * Handles core state management logic for the application
 */

import { atom } from 'jotai';

// ============================================
// Type Definitions
// ============================================

/**
 * Agent information structure for chatbot
 */
export interface AgentInfo {
  title: string;
  agent: string;
  file_url: string;
  additional_info: string;
}

/**
 * Business analysis result structure
 */
export interface BusinessAnalysisResult {
  summary?: string;
  key_findings?: string[];
  recommendations?: string[];
  metrics?: Record<string, number>;
  timestamp?: string;
}

/**
 * Visualization result structure
 */
export interface VisualizationResult {
  type: string;
  config: Record<string, unknown>;
  data?: unknown[];
  title?: string;
}

/**
 * Anomaly detection result structure
 */
export interface AnomalyDetectionResult {
  anomalies?: Array<{
    id: string;
    field: string;
    value: unknown;
    severity: 'low' | 'medium' | 'high';
    description: string;
  }>;
  summary?: string;
  confidence?: number;
}

/**
 * EDA analysis result structure
 */
export interface EDAAnalysisResult {
  statistics?: Record<string, number>;
  distributions?: Record<string, unknown[]>;
  correlations?: Array<{ field1: string; field2: string; correlation: number }>;
  summary?: string;
}

/**
 * Combined analysis results type
 */
export type AnalysisResult = 
  | BusinessAnalysisResult 
  | VisualizationResult 
  | AnomalyDetectionResult 
  | EDAAnalysisResult;

// ============================================
// Core State Atoms - Single source of truth
// ============================================

// Main chatbot state
export const mainChatbotOpenAtom = atom(true);

// Chatbot agent information
export const chatbotAgentInfoAtom = atom<AgentInfo>({
  title: "",
  agent: "",
  file_url: "",
  additional_info: "",
});

// UI state atoms
export const chatInputFocusedAtom = atom(false);
export const messageComposingAtom = atom(false);

// Analysis results atoms for cross-component communication
export const businessAnalysisResultAtom = atom<BusinessAnalysisResult | null>(null);
export const visualizationResultAtom = atom<VisualizationResult | null>(null);
export const anomalyDetectionResultAtom = atom<AnomalyDetectionResult | null>(null);
export const edaAnalysisResultAtom = atom<EDAAnalysisResult | null>(null);

// ============================================
// State Management Utilities
// ============================================

export interface StateManager {
  getMainChatbotState(): boolean;
  setMainChatbotState(open: boolean): void;
  getAgentInfo(): AgentInfo;
  setAgentInfo(info: Partial<AgentInfo>): void;
  getAnalysisResults(): Record<string, AnalysisResult | null>;
  setAnalysisResult(type: string, result: AnalysisResult | null): void;
  resetAnalysisResults(): void;
}

export class ApplicationStateManager implements StateManager {
  private mainChatbotOpen: boolean = true;
  private agentInfo: AgentInfo = {
    title: "",
    agent: "",
    file_url: "",
    additional_info: "",
  };
  private analysisResults: Record<string, AnalysisResult | null> = {};

  getMainChatbotState(): boolean {
    return this.mainChatbotOpen;
  }

  setMainChatbotState(open: boolean): void {
    this.mainChatbotOpen = open;
  }

  getAgentInfo(): AgentInfo {
    return { ...this.agentInfo };
  }

  setAgentInfo(info: Partial<AgentInfo>): void {
    this.agentInfo = { ...this.agentInfo, ...info };
  }

  getAnalysisResults(): Record<string, AnalysisResult | null> {
    return { ...this.analysisResults };
  }

  setAnalysisResult(type: string, result: AnalysisResult | null): void {
    this.analysisResults[type] = result;
  }

  resetAnalysisResults(): void {
    this.analysisResults = {};
  }
} 