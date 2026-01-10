/**
 * DataGrid Types
 * Type definitions for DataGrid component
 */

export interface DataGridProps {
  data: any[][];
  columns?: string[];
  sortable?: boolean;
  filterable?: boolean;
  maxRows?: number;
  onEdit?: ((rowIndex: number, colIndex: number, value: any) => void) | null;
  className?: string;
}

export interface DataGridState {
  sortColumn: number | null;
  sortDirection: 'asc' | 'desc';
  filterText: string;
  editableData: any[][];
  editingCell: string | null;
}

export interface ProcessedData {
  columnHeaders: string[];
  dataRows: any[][];
}

export interface SortConfig {
  column: number;
  direction: 'asc' | 'desc';
}

export interface FilterConfig {
  text: string;
  caseSensitive: boolean;
}

export interface CellEditRequest {
  rowIndex: number;
  colIndex: number;
  value: any;
  originalValue: any;
}

export interface DataGridColumn {
  key: string;
  label: string;
  sortable?: boolean;
  filterable?: boolean;
  width?: string;
  align?: 'left' | 'center' | 'right';
} 