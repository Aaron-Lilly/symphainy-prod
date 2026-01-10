"use client";

import React, { useState, useMemo } from "react";
import { Button } from "@/components/ui/button";

interface DataGridProps {
  data: any[][];
  columns?: string[];
  sortable?: boolean;
  filterable?: boolean;
  maxRows?: number;
  onEdit?: ((rowIndex: number, colIndex: number, value: any) => void) | null;
}

export const DataGrid: React.FC<DataGridProps> = ({ 
  data, 
  columns, 
  sortable = false, 
  filterable = false, 
  maxRows = 100,
  onEdit = null 
}) => {
  const [sortColumn, setSortColumn] = useState<number | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [filterText, setFilterText] = useState('');
  const [editableData, setEditableData] = useState(data);
  const [editingCell, setEditingCell] = useState<string | null>(null);
  
  // Process data and extract column headers
  const { columnHeaders, dataRows } = useMemo(() => {
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
  }, [data, columns]);
  
  const processedData = useMemo(() => {
    let result = [...dataRows];
    
    // Apply filtering
    if (filterable && filterText) {
      result = result.filter(row => 
        row.some(cell => 
          String(cell).toLowerCase().includes(filterText.toLowerCase())
        )
      );
    }
    
    // Apply sorting
    if (sortable && sortColumn !== null && sortColumn < result[0]?.length) {
      result.sort((a, b) => {
        const aVal = String(a[sortColumn] || '');
        const bVal = String(b[sortColumn] || '');
        const comparison = aVal.localeCompare(bVal);
        return sortDirection === 'asc' ? comparison : -comparison;
      });
    }
    
    return result.slice(0, maxRows);
  }, [dataRows, filterText, sortColumn, sortDirection, maxRows, filterable, sortable]);
  
  const handleCellEdit = (rowIndex: number, colIndex: number, value: any) => {
    const newData = [...editableData];
    if (columns) {
      // If we have separate columns, update the data array
      newData[rowIndex][colIndex] = value;
    } else {
      // If columns are in the first row, update data starting from index 1
      newData[rowIndex + 1][colIndex] = value;
    }
    setEditableData(newData);
    
    if (onEdit) {
      onEdit(rowIndex, colIndex, value);
    }
  };
  
  if (!data || data.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No data available
      </div>
    );
  }
  
  // Ensure columnHeaders is always an array
  const safeColumnHeaders = Array.isArray(columnHeaders) ? columnHeaders : [];
  
  return (
    <div className="space-y-3">
      {/* Controls */}
      {(filterable || sortable) && (
        <div className="flex gap-3">
          {filterable && (
            <input
              type="text"
              placeholder="Filter data..."
              value={filterText}
              onChange={(e) => setFilterText(e.target.value)}
              className="px-3 py-1 border rounded text-sm"
            />
          )}
          {sortable && safeColumnHeaders.length > 0 && (
            <select
              value={sortColumn !== null ? sortColumn : ""}
              onChange={(e) => setSortColumn(e.target.value ? parseInt(e.target.value) : null)}
              className="px-3 py-1 border rounded text-sm"
            >
              <option value="">No sorting</option>
              {safeColumnHeaders.map((col, idx) => (
                <option key={idx} value={idx}>{col}</option>
              ))}
            </select>
          )}
        </div>
      )}
      
      {/* Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full border">
          <thead>
            <tr>
              {safeColumnHeaders.map((col, idx) => (
                <th 
                  key={idx} 
                  className="border px-2 py-1 bg-gray-50 text-left text-sm cursor-pointer hover:bg-gray-100"
                  onClick={() => {
                    if (sortable) {
                      if (sortColumn === idx) {
                        setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
                      } else {
                        setSortColumn(idx);
                        setSortDirection('asc');
                      }
                    }
                  }}
                >
                  <div className="flex items-center gap-1">
                    {col}
                    {sortable && sortColumn === idx && (
                      <span>{sortDirection === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {processedData.map((row, rowIdx) => (
              <tr key={rowIdx}>
                {row.map((cell, cellIdx) => (
                  <td key={cellIdx} className="border px-2 py-1 text-sm">
                    {onEdit && editingCell === `${rowIdx}-${cellIdx}` ? (
                      <input
                        type="text"
                        value={cell || ''}
                        onChange={(e) => {
                          handleCellEdit(rowIdx, cellIdx, e.target.value);
                        }}
                        onBlur={() => setEditingCell(null)}
                        className="w-full px-1 py-0 border-none focus:outline-none"
                        autoFocus
                      />
                    ) : (
                      <div 
                        onClick={() => onEdit && setEditingCell(`${rowIdx}-${cellIdx}`)}
                        className={onEdit ? "cursor-pointer hover:bg-gray-50 px-1 py-0" : ""}
                      >
                        {cell}
                      </div>
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {/* Pagination Info */}
      {dataRows.length > maxRows && (
        <p className="text-xs text-gray-500">
          Showing {processedData.length} of {dataRows.length} rows
        </p>
      )}
    </div>
  );
}; 