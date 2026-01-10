/**
 * VARKInsightsPanel Types
 * Type definitions for VARKInsightsPanel component
 */

import { FileMetadata } from '@/shared/types/file';

export interface VARKInsightsPanelProps {
  onClose?: () => void;
  className?: string;
  initialData?: any;
}

export type LearningStyle = 'tabular' | 'visual';
export type DataDepth = 'summary' | 'detailed' | 'drill-down';

export interface AnalysisHistoryEntry {
  id: string;
  timestamp: Date;
  type: 'initial_analysis' | 'iterative_analysis';
  query?: string;
  learningStyle: LearningStyle;
  dataDepth: DataDepth;
  results: any;
  summary: string;
}

export interface VARKInsightsPanelState {
  files: FileMetadata[];
  selectedFile: FileMetadata | null;
  fileLoading: boolean;
  learningStyle: LearningStyle;
  dataDepth: DataDepth;
  isAnalyzing: boolean;
  analysisResults: any;
  businessSummary: string;
  summaryLoading: boolean;
  error: string | null;
  // New state for iterative analysis
  analysisHistory: AnalysisHistoryEntry[];
  currentSessionId: string | null;
  isIterativeAnalysis: boolean;
}

export interface FileSelectorProps {
  files: FileMetadata[];
  selectedFile: FileMetadata | null;
  onFileSelect: (file: FileMetadata) => void;
  loading: boolean;
}

export interface LearningStyleSelectorProps {
  learningStyle: LearningStyle;
  onStyleChange: (style: LearningStyle) => void;
  dataDepth: DataDepth;
  onDepthChange: (depth: DataDepth) => void;
}

export interface BusinessSummaryProps {
  summary: string;
  loading: boolean;
  onRefresh: () => void;
}

export interface VARKDisplayProps {
  learningStyle: LearningStyle;
  dataDepth: DataDepth;
  analysisResults: any;
  isAnalyzing: boolean;
  onAnalysisComplete: (results: any) => void;
}

export interface SummarySectionProps {
  businessSummary: string;
  analysisResults: any;
  learningStyle: LearningStyle;
  onExport: () => void;
  onShare: () => void;
}

export interface AnalysisRequest {
  fileUuid: string;
  learningStyle: LearningStyle;
  dataDepth: DataDepth;
  sessionToken?: string;
}

export interface AnalysisResponse {
  success: boolean;
  data?: any;
  error?: string;
} 