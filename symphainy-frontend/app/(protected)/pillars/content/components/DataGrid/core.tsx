/**
 * DataGrid Core
 * Core DataGrid component with data display interface
 */

import React from 'react';
import { DataGridProps } from './types';
import { useDataGrid } from './hooks';
import { DataTable, FilterBar, DataGridHeader } from './components';

export function DataGrid({ 
  data, 
  columns, 
  sortable = false, 
  filterable = false, 
  maxRows = 100,
  onEdit = null,
  className 
}: DataGridProps) {
  const {
    state,
    processedData,
    displayData,
    handleSort,
    handleFilter,
    handleCellEdit,
    startCellEdit,
    stopCellEdit,
    resetSorting,
    resetFiltering,
    resetAll,
  } = useDataGrid(data, columns, sortable, filterable, maxRows);

  const handleCellEditWithCallback = (rowIndex: number, colIndex: number, value: any) => {
    handleCellEdit(rowIndex, colIndex, value);
    if (onEdit) {
      onEdit(rowIndex, colIndex, value);
    }
  };

  const handleResetAll = () => {
    resetAll();
  };

  return (
    <div className={`space-y-4 ${className || ''}`}>
      {/* Header */}
      <DataGridHeader
        title="Data Grid"
        totalRows={processedData.dataRows.length}
        filteredRows={displayData.length}
        onResetAll={handleResetAll}
      />

      {/* Filter Bar */}
      {filterable && (
        <FilterBar
          filterText={state.filterText}
          onFilterChange={handleFilter}
          onReset={resetFiltering}
        />
      )}

      {/* Data Table */}
      <DataTable
        data={displayData}
        columnHeaders={processedData.columnHeaders}
        sortable={sortable}
        onSort={handleSort}
        sortColumn={state.sortColumn}
        sortDirection={state.sortDirection}
        onCellEdit={handleCellEditWithCallback}
        editingCell={state.editingCell}
        onStartEdit={startCellEdit}
        onStopEdit={stopCellEdit}
      />

      {/* Empty State */}
      {displayData.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          {state.filterText ? 'No data matches your filter criteria.' : 'No data available.'}
        </div>
      )}
    </div>
  );
} 