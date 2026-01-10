/**
 * DataGrid Utilities
 * Utility functions for DataGrid component
 */

import { ProcessedData, SortConfig, FilterConfig } from './types';

export function processData(data: any[][], columns?: string[]): ProcessedData {
  if (!data || data.length === 0) {
    return { columnHeaders: [], dataRows: [] };
  }

  // Check if data is array of objects (for backward compatibility)
  if (typeof data[0] === 'object' && !Array.isArray(data[0])) {
    // Object data - extract column headers from first object
    const firstRow = data[0];
    const extractedColumns = columns || Object.keys(firstRow);
    const processedRows = data.map(row => 
      extractedColumns.map(col => {
        const value = row[col];
        // Handle different data types properly
        if (value === null || value === undefined) {
          return '';
        } else if (typeof value === 'boolean') {
          return value.toString();
        } else {
          return String(value);
        }
      })
    );
    
    return {
      columnHeaders: extractedColumns,
      dataRows: processedRows
    };
  } else {
    // Array data - use provided columns or first row as headers
    const extractedColumns = columns || (data.length > 0 ? data[0] : []);
    const processedRows = columns ? data : (data.length > 1 ? data.slice(1) : []);
    
    return {
      columnHeaders: extractedColumns,
      dataRows: processedRows
    };
  }
}

export function applySorting(data: any[][], sortConfig: SortConfig | null): any[][] {
  if (!sortConfig || sortConfig.column >= data[0]?.length) {
    return data;
  }

  return [...data].sort((a, b) => {
    const aVal = String(a[sortConfig.column] || '');
    const bVal = String(b[sortConfig.column] || '');
    const comparison = aVal.localeCompare(bVal);
    return sortConfig.direction === 'asc' ? comparison : -comparison;
  });
}

export function applyFiltering(data: any[][], filterConfig: FilterConfig): any[][] {
  if (!filterConfig.text) {
    return data;
  }

  const searchText = filterConfig.caseSensitive 
    ? filterConfig.text 
    : filterConfig.text.toLowerCase();

  return data.filter(row => 
    row.some(cell => {
      const cellText = filterConfig.caseSensitive 
        ? String(cell) 
        : String(cell).toLowerCase();
      return cellText.includes(searchText);
    })
  );
}

export function limitRows(data: any[][], maxRows: number): any[][] {
  return data.slice(0, maxRows);
}

export function formatCellValue(value: any): string {
  if (value === null || value === undefined) {
    return '';
  }
  
  if (typeof value === 'boolean') {
    return value.toString();
  }
  
  if (typeof value === 'number') {
    return value.toString();
  }
  
  if (typeof value === 'string') {
    return value;
  }
  
  if (typeof value === 'object') {
    return JSON.stringify(value);
  }
  
  return String(value);
}

export function validateCellValue(value: any): boolean {
  // Add validation logic here if needed
  return value !== null && value !== undefined;
}

export function generateCellId(rowIndex: number, colIndex: number): string {
  return `cell-${rowIndex}-${colIndex}`;
}

export function parseCellId(cellId: string): { rowIndex: number; colIndex: number } | null {
  const match = cellId.match(/^cell-(\d+)-(\d+)$/);
  if (match) {
    return {
      rowIndex: parseInt(match[1]),
      colIndex: parseInt(match[2])
    };
  }
  return null;
} 