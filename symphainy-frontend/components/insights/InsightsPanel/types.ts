/**
 * Types for Optimized Insights Panel Components
 * 
 * Centralized type definitions for all insights panel components
 * to ensure type safety and consistency.
 */

// ============================================
// Core Data Types
// ============================================

export interface GridData {
  columns: string[];
  rows: (string | number | boolean | null)[][];
}

export interface Visualization {
  type: string;
  title?: string;
  description?: string;
  data: any;
  xKey?: string;
  yKey?: string;
  valueKey?: string;
  keys?: string[];
  rationale?: string;
  nivoChartType?: string;
  config?: Record<string, any>;
}

export interface Alert {
  level: "info" | "warning" | "critical";
  message: string;
  recommendation?: string;
  timestamp?: number;
  id?: string;
}

export interface AgentMessage {
  id: string;
  type: "user" | "agent" | "system";
  content: string;
  timestamp: number;
  metadata?: Record<string, any>;
}

export interface ErrorMessage {
  id: string;
  message: string;
  type: "error" | "warning" | "info";
  timestamp: number;
  details?: string;
  stack?: string;
}

// ============================================
// AGUI Response Types
// ============================================

export interface AGUIResponse {
  type: string;
  data: any;
  timestamp: number;
  id?: string;
  metadata?: Record<string, any>;
}

export interface ProcessedResponses {
  summary_output: AGUIResponse[];
  data_grid_response: AGUIResponse[];
  visual_output: AGUIResponse[];
  agent_message: AGUIResponse[];
  error: AGUIResponse[];
}

// ============================================
// Panel Output Types
// ============================================

export interface InsightsPanelOutput {
  summary: string;
  grid: GridData;
  visualizations: Visualization[];
  alerts: Alert[];
  agentMessages: AgentMessage[];
  errors: ErrorMessage[];
  metadata?: Record<string, any>;
}

// ============================================
// Component Props Types
// ============================================

export interface InsightsSummaryProps {
  summary?: string;
  isLoading?: boolean;
  className?: string;
}

export interface InsightsDataGridProps {
  gridData?: GridData;
  isLoading?: boolean;
  className?: string;
  onSort?: (columnIndex: number, ascending: boolean) => void;
  onFilter?: (filter: string) => void;
}

export interface InsightsVisualizationsProps {
  visualizations?: Visualization[];
  isLoading?: boolean;
  className?: string;
  onVisualizationClick?: (visualization: Visualization) => void;
}

export interface InsightsAlertsProps {
  alerts?: Alert[];
  isLoading?: boolean;
  className?: string;
  onAlertDismiss?: (alertId: string) => void;
  onAlertAction?: (alert: Alert) => void;
}

export interface InsightsAgentMessagesProps {
  messages?: AgentMessage[];
  isLoading?: boolean;
  className?: string;
  onMessageClick?: (message: AgentMessage) => void;
  onMessageReply?: (message: AgentMessage) => void;
}

export interface InsightsErrorMessagesProps {
  errors?: ErrorMessage[];
  isLoading?: boolean;
  className?: string;
  onErrorDismiss?: (errorId: string) => void;
  onErrorRetry?: (error: ErrorMessage) => void;
}

// ============================================
// Chart Configuration Types
// ============================================

export interface ChartConfig {
  width: number;
  height: number;
  margin: {
    top: number;
    right: number;
    bottom: number;
    left: number;
  };
  colors: string[];
  theme: 'light' | 'dark';
}

export interface NivoChartProps {
  data: any;
  config: ChartConfig;
  className?: string;
}

// ============================================
// Utility Types
// ============================================

export interface SortConfig {
  columnIndex: number;
  ascending: boolean;
}

export interface FilterConfig {
  text: string;
  columns: string[];
}

export interface PaginationConfig {
  page: number;
  pageSize: number;
  total: number;
}

// ============================================
// Event Types
// ============================================

export interface InsightsPanelEvent {
  type: 'tab_change' | 'data_update' | 'error' | 'loading';
  data?: any;
  timestamp: number;
}

export interface TabChangeEvent {
  tab: string;
  previousTab?: string;
}

export interface DataUpdateEvent {
  dataType: 'summary' | 'grid' | 'visualizations' | 'alerts' | 'messages' | 'errors';
  data: any;
}

// ============================================
// State Types
// ============================================

export interface InsightsPanelState {
  activeTab: string;
  isLoading: boolean;
  error: Error | null;
  data: InsightsPanelOutput | null;
  lastUpdate: number | null;
}

export interface InsightsPanelActions {
  setActiveTab: (tab: string) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: Error | null) => void;
  setData: (data: InsightsPanelOutput | null) => void;
  updateData: (updates: Partial<InsightsPanelOutput>) => void;
}

// ============================================
// Hook Return Types
// ============================================

export interface UseInsightsPanelReturn {
  state: InsightsPanelState;
  actions: InsightsPanelActions;
  processedData: ProcessedResponses | null;
  sendAgentEvent: (event: any) => Promise<void>;
}

export interface UseInsightsDataReturn {
  data: InsightsPanelOutput | null;
  isLoading: boolean;
  error: Error | null;
  refresh: () => Promise<void>;
  update: (updates: Partial<InsightsPanelOutput>) => void;
}

// ============================================
// Configuration Types
// ============================================

export interface InsightsPanelConfig {
  maxOutputs: number;
  autoRefresh: boolean;
  refreshInterval: number;
  enableSorting: boolean;
  enableFiltering: boolean;
  enablePagination: boolean;
  pageSize: number;
  chartConfig: ChartConfig;
}

export interface TabConfig {
  value: string;
  label: string;
  icon: string;
  disabled?: boolean;
  badge?: number;
}

// ============================================
// Performance Types
// ============================================

export interface PerformanceMetrics {
  renderTime: number;
  dataLoadTime: number;
  memoryUsage: number;
  componentRenders: number;
}

export interface OptimizationConfig {
  enableMemoization: boolean;
  enableVirtualization: boolean;
  enableLazyLoading: boolean;
  debounceDelay: number;
  throttleDelay: number;
} 