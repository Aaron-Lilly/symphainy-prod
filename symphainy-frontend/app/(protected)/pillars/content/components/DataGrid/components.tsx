/**
 * DataGrid Components
 * Sub-components for DataGrid functionality
 */

import React from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';
import { ProcessedData } from './types';
import { formatCellValue, generateCellId } from './utils';

interface DataTableProps {
  data: any[][];
  columnHeaders: string[];
  sortable: boolean;
  onSort: (columnIndex: number) => void;
  sortColumn: number | null;
  sortDirection: 'asc' | 'desc';
  onCellEdit: (rowIndex: number, colIndex: number, value: any) => void;
  editingCell: string | null;
  onStartEdit: (cellId: string) => void;
  onStopEdit: () => void;
}

export function DataTable({
  data,
  columnHeaders,
  sortable,
  onSort,
  sortColumn,
  sortDirection,
  onCellEdit,
  editingCell,
  onStartEdit,
  onStopEdit,
}: DataTableProps) {
  const getSortIcon = (columnIndex: number) => {
    if (sortColumn !== columnIndex) {
      return <ArrowUpDown className="h-4 w-4" />;
    }
    return sortDirection === 'asc' ? <ArrowUp className="h-4 w-4" /> : <ArrowDown className="h-4 w-4" />;
  };

  const handleCellClick = (rowIndex: number, colIndex: number) => {
    const cellId = generateCellId(rowIndex, colIndex);
    onStartEdit(cellId);
  };

  const handleCellChange = (rowIndex: number, colIndex: number, value: string) => {
    onCellEdit(rowIndex, colIndex, value);
  };

  const handleCellBlur = () => {
    onStopEdit();
  };

  const handleCellKeyDown = (e: React.KeyboardEvent, rowIndex: number, colIndex: number) => {
    if (e.key === 'Enter') {
      onStopEdit();
    } else if (e.key === 'Escape') {
      onStopEdit();
    }
  };

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            {columnHeaders.map((header, index) => (
              <th
                key={index}
                className={`px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider ${
                  sortable ? 'cursor-pointer hover:bg-gray-100' : ''
                }`}
                onClick={() => sortable && onSort(index)}
              >
                <div className="flex items-center space-x-1">
                  <span>{header}</span>
                  {sortable && getSortIcon(index)}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {data.map((row, rowIndex) => (
            <tr key={rowIndex} className="hover:bg-gray-50">
              {row.map((cell, colIndex) => {
                const cellId = generateCellId(rowIndex, colIndex);
                const isEditing = editingCell === cellId;
                
                return (
                  <td key={colIndex} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {isEditing ? (
                      <input
                        type="text"
                        value={formatCellValue(cell)}
                        onChange={(e) => handleCellChange(rowIndex, colIndex, e.target.value)}
                        onBlur={handleCellBlur}
                        onKeyDown={(e) => handleCellKeyDown(e, rowIndex, colIndex)}
                        className="w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        autoFocus
                      />
                    ) : (
                      <div
                        onClick={() => handleCellClick(rowIndex, colIndex)}
                        className="cursor-pointer hover:bg-gray-100 px-2 py-1 rounded"
                      >
                        {formatCellValue(cell)}
                      </div>
                    )}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

interface FilterBarProps {
  filterText: string;
  onFilterChange: (text: string) => void;
  onReset: () => void;
}

export function FilterBar({ filterText, onFilterChange, onReset }: FilterBarProps) {
  return (
    <div className="flex items-center space-x-2 mb-4">
      <Input
        type="text"
        placeholder="Filter data..."
        value={filterText}
        onChange={(e) => onFilterChange(e.target.value)}
        className="max-w-sm"
      />
      {filterText && (
        <Button variant="outline" size="sm" onClick={onReset}>
          Clear
        </Button>
      )}
    </div>
  );
}

interface DataGridHeaderProps {
  title?: string;
  totalRows: number;
  filteredRows: number;
  onResetAll: () => void;
}

export function DataGridHeader({ title, totalRows, filteredRows, onResetAll }: DataGridHeaderProps) {
  return (
    <div className="flex justify-between items-center mb-4">
      <div>
        {title && <h3 className="text-lg font-medium">{title}</h3>}
        <p className="text-sm text-gray-500">
          Showing {filteredRows} of {totalRows} rows
        </p>
      </div>
      <Button variant="outline" size="sm" onClick={onResetAll}>
        Reset All
      </Button>
    </div>
  );
} 