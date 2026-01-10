/**
 * Utilities for Optimized Insights Panel Components
 * 
 * Helper functions for data processing, memoization, and performance optimization
 * to ensure efficient rendering and data handling.
 */

import type { 
  AGUIResponse, 
  ProcessedResponses, 
  GridData, 
  Visualization, 
  Alert, 
  AgentMessage, 
  ErrorMessage,
  SortConfig,
  FilterConfig,
  PaginationConfig,
} from './types';

// ============================================
// Data Processing Utilities
// ============================================

/**
 * Process AGUI responses and group them by type
 */
export function processAGUIResponsesStacked(responses: AGUIResponse[]): ProcessedResponses {
  const result: ProcessedResponses = {
    summary_output: [],
    data_grid_response: [],
    visual_output: [],
    agent_message: [],
    error: [],
  };

  for (const resp of responses) {
    if (resp.type && result[resp.type as keyof ProcessedResponses] !== undefined) {
      result[resp.type as keyof ProcessedResponses].push(resp);
    }
  }

  return result;
}

/**
 * Extract summary from processed responses
 */
export function extractSummary(responses: ProcessedResponses): string {
  const summaries = responses.summary_output.map(resp => resp.data?.summary || resp.data?.content || '');
  return summaries.join('\n\n').trim() || 'No summary available';
}

/**
 * Extract grid data from processed responses
 */
export function extractGridData(responses: ProcessedResponses): GridData | null {
  const gridResponses = responses.data_grid_response;
  if (gridResponses.length === 0) return null;

  // Use the most recent grid response
  const latestGrid = gridResponses[gridResponses.length - 1];
  return {
    columns: latestGrid.data?.columns || [],
    rows: latestGrid.data?.rows || [],
  };
}

/**
 * Extract visualizations from processed responses
 */
export function extractVisualizations(responses: ProcessedResponses): Visualization[] {
  return responses.visual_output.map(resp => ({
    type: resp.data?.type || 'unknown',
    title: resp.data?.title,
    description: resp.data?.description,
    data: resp.data?.data || resp.data,
    xKey: resp.data?.xKey,
    yKey: resp.data?.yKey,
    valueKey: resp.data?.valueKey,
    keys: resp.data?.keys,
    rationale: resp.data?.rationale,
    nivoChartType: resp.data?.nivoChartType,
    config: resp.data?.config,
  }));
}

/**
 * Extract alerts from processed responses
 */
export function extractAlerts(responses: ProcessedResponses): Alert[] {
  return responses.error
    .filter(resp => resp.data?.level)
    .map(resp => ({
      level: resp.data.level,
      message: resp.data.message || resp.data.content || 'Unknown error',
      recommendation: resp.data.recommendation,
      timestamp: resp.timestamp,
      id: resp.id || `alert_${resp.timestamp}`,
    }));
}

/**
 * Extract agent messages from processed responses
 */
export function extractAgentMessages(responses: ProcessedResponses): AgentMessage[] {
  return responses.agent_message.map(resp => ({
    id: resp.id || `msg_${resp.timestamp}`,
    type: resp.data?.type || 'agent',
    content: resp.data?.content || resp.data?.message || '',
    timestamp: resp.timestamp,
    metadata: resp.data?.metadata || resp.metadata,
  }));
}

/**
 * Extract error messages from processed responses
 */
export function extractErrorMessages(responses: ProcessedResponses): ErrorMessage[] {
  return responses.error
    .filter(resp => !resp.data?.level) // Exclude alerts
    .map(resp => ({
      id: resp.id || `error_${resp.timestamp}`,
      message: resp.data?.message || resp.data?.content || 'Unknown error',
      type: resp.data?.type || 'error',
      timestamp: resp.timestamp,
      details: resp.data?.details,
      stack: resp.data?.stack,
    }));
}

// ============================================
// Data Grid Utilities
// ============================================

/**
 * Sort grid data by column
 */
export function sortGridData(
  data: GridData, 
  sortConfig: SortConfig
): GridData {
  const { columnIndex, ascending } = sortConfig;
  
  if (columnIndex < 0 || columnIndex >= data.columns.length) {
    return data;
  }

  const sortedRows = [...data.rows].sort((a, b) => {
    const aVal = a[columnIndex];
    const bVal = b[columnIndex];

    if (aVal === bVal) return 0;
    if (aVal == null) return ascending ? 1 : -1;
    if (bVal == null) return ascending ? -1 : 1;

    const comparison = aVal < bVal ? -1 : 1;
    return ascending ? comparison : -comparison;
  });

  return {
    ...data,
    rows: sortedRows,
  };
}

/**
 * Filter grid data by text
 */
export function filterGridData(
  data: GridData, 
  filterConfig: FilterConfig
): GridData {
  const { text, columns } = filterConfig;
  
  if (!text.trim()) {
    return data;
  }

  const searchText = text.toLowerCase();
  const columnIndices = columns.length > 0 
    ? columns.map(col => data.columns.indexOf(col)).filter(i => i !== -1)
    : data.columns.map((_, i) => i);

  const filteredRows = data.rows.filter(row =>
    columnIndices.some(colIndex => {
      const cellValue = row[colIndex];
      return cellValue != null && 
             String(cellValue).toLowerCase().includes(searchText);
    })
  );

  return {
    ...data,
    rows: filteredRows,
  };
}

/**
 * Paginate grid data
 */
export function paginateGridData(
  data: GridData, 
  paginationConfig: PaginationConfig
): { data: GridData; total: number } {
  const { page, pageSize } = paginationConfig;
  const startIndex = (page - 1) * pageSize;
  const endIndex = startIndex + pageSize;

  return {
    data: {
      ...data,
      rows: data.rows.slice(startIndex, endIndex),
    },
    total: data.rows.length,
  };
}

// ============================================
// Performance Optimization Utilities
// ============================================

/**
 * Debounce function for performance optimization
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
}

/**
 * Throttle function for performance optimization
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let lastCall = 0;
  
  return (...args: Parameters<T>) => {
    const now = Date.now();
    if (now - lastCall >= delay) {
      lastCall = now;
      func(...args);
    }
  };
}

/**
 * Memoize expensive calculations
 */
export function memoize<T extends (...args: any[]) => any>(
  func: T,
  keyGenerator?: (...args: Parameters<T>) => string
): T {
  const cache = new Map<string, ReturnType<T>>();
  
  return ((...args: Parameters<T>) => {
    const key = keyGenerator 
      ? keyGenerator(...args)
      : JSON.stringify(args);
    
    if (cache.has(key)) {
      return cache.get(key);
    }
    
    const result = func(...args);
    cache.set(key, result);
    return result;
  }) as T;
}

/**
 * Check if data has changed for memoization
 */
export function hasDataChanged<T>(oldData: T, newData: T): boolean {
  if (oldData === newData) return false;
  if (!oldData || !newData) return true;
  
  return JSON.stringify(oldData) !== JSON.stringify(newData);
}

// ============================================
// Chart Utilities
// ============================================

/**
 * Get chart type from visualization
 */
export function getChartType(visualization: Visualization): string {
  return visualization.nivoChartType || visualization.type || 'bar';
}

/**
 * Validate chart data
 */
export function validateChartData(data: any): boolean {
  if (!data || typeof data !== 'object') return false;
  
  // Check if data has required properties for charts
  if (Array.isArray(data)) {
    return data.length > 0 && data.every(item => typeof item === 'object');
  }
  
  return true;
}

/**
 * Transform data for Nivo charts
 */
export function transformDataForNivo(
  data: any, 
  xKey?: string, 
  yKey?: string
): any[] {
  if (!Array.isArray(data)) return [];
  
  if (xKey && yKey) {
    return data.map(item => ({
      x: item[xKey],
      y: item[yKey],
      ...item,
    }));
  }
  
  return data;
}

// ============================================
// Formatting Utilities
// ============================================

/**
 * Format timestamp for display
 */
export function formatTimestamp(timestamp: number): string {
  return new Date(timestamp).toLocaleString();
}

/**
 * Format file size
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Truncate text with ellipsis
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

// ============================================
// Validation Utilities
// ============================================

/**
 * Validate grid data structure
 */
export function validateGridData(data: any): data is GridData {
  return (
    data &&
    typeof data === 'object' &&
    Array.isArray(data.columns) &&
    Array.isArray(data.rows) &&
    data.columns.every((col: any) => typeof col === 'string') &&
    data.rows.every((row: any) => Array.isArray(row))
  );
}

/**
 * Validate visualization data
 */
export function validateVisualization(data: any): data is Visualization {
  return (
    data &&
    typeof data === 'object' &&
    typeof data.type === 'string' &&
    data.data !== undefined
  );
}

/**
 * Validate alert data
 */
export function validateAlert(data: any): data is Alert {
  return (
    data &&
    typeof data === 'object' &&
    ['info', 'warning', 'critical'].includes(data.level) &&
    typeof data.message === 'string'
  );
}

// ============================================
// Error Handling Utilities
// ============================================

/**
 * Create error message from various error types
 */
export function createErrorMessage(error: any): string {
  if (typeof error === 'string') return error;
  if (error?.message) return error.message;
  if (error?.toString) return error.toString();
  return 'Unknown error occurred';
}

/**
 * Get error severity level
 */
export function getErrorSeverity(error: any): 'low' | 'medium' | 'high' | 'critical' {
  if (error?.level) return error.level;
  if (error?.severity) return error.severity;
  
  const message = createErrorMessage(error).toLowerCase();
  
  if (message.includes('critical') || message.includes('fatal')) return 'critical';
  if (message.includes('error') || message.includes('failed')) return 'high';
  if (message.includes('warning') || message.includes('caution')) return 'medium';
  
  return 'low';
} 