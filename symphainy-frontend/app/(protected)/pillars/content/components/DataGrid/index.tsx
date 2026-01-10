/**
 * DataGrid Orchestrator
 * Unified access point for DataGrid functionality
 */

// Main component
export { DataGrid } from './core';

// Sub-components
export { DataTable, FilterBar, DataGridHeader } from './components';

// Types
export type {
  DataGridProps,
  DataGridState,
  ProcessedData,
  SortConfig,
  FilterConfig,
  CellEditRequest,
  DataGridColumn
} from './types';

// Utilities
export { 
  processData,
  applySorting,
  applyFiltering,
  limitRows,
  formatCellValue,
  validateCellValue,
  generateCellId,
  parseCellId
} from './utils';

// Hooks
export { useDataGrid } from './hooks'; 