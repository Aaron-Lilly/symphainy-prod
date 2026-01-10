/**
 * DataGrid Hooks
 * Custom hooks for DataGrid component
 */

import React, { useState, useMemo } from 'react';
import { DataGridState, ProcessedData, SortConfig, FilterConfig } from './types';
import { processData, applySorting, applyFiltering, limitRows } from './utils';

export function useDataGrid(
  data: any[][],
  columns?: string[],
  sortable: boolean = false,
  filterable: boolean = false,
  maxRows: number = 100
) {
  const [state, setState] = useState<DataGridState>({
    sortColumn: null,
    sortDirection: 'asc',
    filterText: '',
    editableData: data,
    editingCell: null,
  });

  // Process data and extract column headers
  const processedData: ProcessedData = useMemo(() => {
    return processData(data, columns);
  }, [data, columns]);

  // Apply sorting, filtering, and row limiting
  const displayData = useMemo(() => {
    let result = [...processedData.dataRows];
    
    // Apply filtering
    if (filterable && state.filterText) {
      const filterConfig: FilterConfig = {
        text: state.filterText,
        caseSensitive: false,
      };
      result = applyFiltering(result, filterConfig);
    }
    
    // Apply sorting
    if (sortable && state.sortColumn !== null) {
      const sortConfig: SortConfig = {
        column: state.sortColumn,
        direction: state.sortDirection,
      };
      result = applySorting(result, sortConfig);
    }
    
    // Apply row limiting
    result = limitRows(result, maxRows);
    
    return result;
  }, [processedData.dataRows, state.filterText, state.sortColumn, state.sortDirection, filterable, sortable, maxRows]);

  const handleSort = (columnIndex: number) => {
    if (!sortable) return;

    setState(prev => ({
      ...prev,
      sortColumn: prev.sortColumn === columnIndex ? prev.sortColumn : columnIndex,
      sortDirection: prev.sortColumn === columnIndex && prev.sortDirection === 'asc' ? 'desc' : 'asc',
    }));
  };

  const handleFilter = (text: string) => {
    if (!filterable) return;

    setState(prev => ({
      ...prev,
      filterText: text,
    }));
  };

  const handleCellEdit = (rowIndex: number, colIndex: number, value: any) => {
    const newData = [...state.editableData];
    if (columns) {
      // If we have separate columns, update the data array
      newData[rowIndex][colIndex] = value;
    } else {
      // If first row is headers, update the data array (skip header row)
      newData[rowIndex + 1][colIndex] = value;
    }
    
    setState(prev => ({
      ...prev,
      editableData: newData,
    }));
  };

  const startCellEdit = (cellId: string) => {
    setState(prev => ({
      ...prev,
      editingCell: cellId,
    }));
  };

  const stopCellEdit = () => {
    setState(prev => ({
      ...prev,
      editingCell: null,
    }));
  };

  const resetSorting = () => {
    setState(prev => ({
      ...prev,
      sortColumn: null,
      sortDirection: 'asc',
    }));
  };

  const resetFiltering = () => {
    setState(prev => ({
      ...prev,
      filterText: '',
    }));
  };

  const resetAll = () => {
    setState({
      sortColumn: null,
      sortDirection: 'asc',
      filterText: '',
      editableData: data,
      editingCell: null,
    });
  };

  return {
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
  };
} 