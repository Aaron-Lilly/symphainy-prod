/**
 * VARKInsightsPanel Orchestrator
 * Unified access point for VARKInsightsPanel functionality
 */

// Main component
export { VARKInsightsPanel } from './core';

// Sub-components
export { 
  FileSelector, 
  LearningStyleSelector, 
  BusinessSummary, 
  VARKDisplay, 
  SummarySection 
} from './components';

// Types
export type {
  VARKInsightsPanelProps,
  VARKInsightsPanelState,
  FileSelectorProps,
  LearningStyleSelectorProps,
  BusinessSummaryProps,
  VARKDisplayProps,
  SummarySectionProps,
  AnalysisRequest,
  AnalysisResponse,
  LearningStyle,
  DataDepth
} from './types';

// Utilities
export { 
  filterParsedFiles,
  getLearningStyleLabel,
  getLearningStyleIcon,
  getDataDepthLabel,
  getDataDepthDescription,
  validateAnalysisRequest,
  formatAnalysisResults,
  generateBusinessSummary,
  exportAnalysisResults
} from './utils';

// Hooks
export { useVARKInsightsPanel } from './hooks'; 