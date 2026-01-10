"use client";

import React from "react";
import { Button } from "@/components/ui/button";
import { DataGrid } from "./DataGrid";

interface FullDatasetModalProps {
  data: any;
  onClose: () => void;
}

export const FullDatasetModal: React.FC<FullDatasetModalProps> = ({ 
  data, 
  onClose 
}) => {
  if (!data || !data.preview_grid) {
    return null;
  }
  
  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg w-full max-w-6xl h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex justify-between items-center p-4 border-b">
          <h2 className="text-lg font-semibold">Full Dataset View</h2>
          <Button onClick={onClose} variant="ghost" size="sm">
            ✕
          </Button>
        </div>
        
        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">
          <DataGrid 
            data={data.preview_grid}
            columns={data.metadata?.column_names}
            sortable={true}
            filterable={true}
            maxRows={1000}
          />
        </div>
        
        {/* Footer */}
        <div className="flex justify-end gap-3 p-4 border-t">
          <Button onClick={onClose} variant="outline">
            Close
          </Button>
        </div>
      </div>
    </div>
  );
}; 