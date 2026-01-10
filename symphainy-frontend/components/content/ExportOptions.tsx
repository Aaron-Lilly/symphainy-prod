"use client";

import React from "react";
import { Button } from "@/components/ui/button";
import { FileType } from "@/shared/types/file";
import { toast } from "sonner";

interface ExportOptionsProps {
  data: any;
  fileType: FileType | string;
  fileName: string;
}

export const ExportOptions: React.FC<ExportOptionsProps> = ({ 
  data, 
  fileType, 
  fileName 
}) => {
  const handleExport = async (format: string) => {
    try {
      switch (format) {
        case 'csv':
          await exportToCSV(data.preview_grid, fileName);
          break;
        case 'excel':
          await exportToExcel(data.preview_grid, fileName);
          break;
        case 'json':
          await exportToJSON(data, fileName);
          break;
        case 'text':
          await exportToText(data.text, fileName);
          break;
        default:
          throw new Error(`Unsupported export format: ${format}`);
      }
      toast.success(`Exported as ${format.toUpperCase()}`);
    } catch (error: any) {
      console.error('Export error:', error);
      toast.error(`Export failed: ${error.message}`);
    }
  };
  
  return (
    <div className="flex gap-2">
      {data.preview_grid && data.preview_grid.length > 0 && (
        <>
          <Button onClick={() => handleExport('csv')} variant="outline" size="sm">
            Export CSV
          </Button>
          <Button onClick={() => handleExport('excel')} variant="outline" size="sm">
            Export Excel
          </Button>
          <Button onClick={() => handleExport('json')} variant="outline" size="sm">
            Export JSON
          </Button>
        </>
      )}
      {data.text && (
        <Button onClick={() => handleExport('text')} variant="outline" size="sm">
          Export Text
        </Button>
      )}
    </div>
  );
};

// Export utility functions
const exportToCSV = async (data: any[][], fileName: string) => {
  if (!data || data.length === 0) {
    throw new Error('No data to export');
  }
  
  const csvContent = data.map(row => 
    row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(',')
  ).join('\n');
  
  downloadFile(csvContent, `${fileName}.csv`, 'text/csv');
};

const exportToExcel = async (data: any[][], fileName: string) => {
  if (!data || data.length === 0) {
    throw new Error('No data to export');
  }
  
  // For now, we'll export as CSV with .xlsx extension
  // In a real implementation, you'd use a library like xlsx
  const csvContent = data.map(row => 
    row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(',')
  ).join('\n');
  
  downloadFile(csvContent, `${fileName}.xlsx`, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
};

const exportToJSON = async (data: any, fileName: string) => {
  const jsonContent = JSON.stringify(data, null, 2);
  downloadFile(jsonContent, `${fileName}.json`, 'application/json');
};

const exportToText = async (text: string, fileName: string) => {
  if (!text) {
    throw new Error('No text to export');
  }
  
  downloadFile(text, `${fileName}.txt`, 'text/plain');
};

const downloadFile = (content: string, fileName: string, mimeType: string) => {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = fileName;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}; 