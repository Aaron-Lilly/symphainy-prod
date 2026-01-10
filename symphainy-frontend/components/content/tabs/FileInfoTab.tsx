"use client";

import React from "react";

interface FileInfoTabProps {
  data: any;
  metadata: any;
}

export const FileInfoTab: React.FC<FileInfoTabProps> = ({ 
  data, 
  metadata 
}) => {
  return (
    <div className="space-y-4">
      <div className="bg-white border rounded p-3">
        <h4 className="font-semibold mb-3">File Information</h4>
        <div className="grid grid-cols-2 gap-4 text-sm">
          {metadata && (
            <>
              {metadata.rows && (
                <div>
                  <span className="font-medium">Rows:</span> {metadata.rows}
                </div>
              )}
              {metadata.columns && (
                <div>
                  <span className="font-medium">Columns:</span> {metadata.columns}
                </div>
              )}
              {metadata.pages && (
                <div>
                  <span className="font-medium">Pages:</span> {metadata.pages}
                </div>
              )}
              {metadata.file_size && (
                <div>
                  <span className="font-medium">File Size:</span> {metadata.file_size}
                </div>
              )}
              {metadata.column_names && (
                <div className="col-span-2">
                  <div className="font-medium mb-2">Columns:</div>
                  <div className="text-xs text-gray-600 bg-gray-50 p-2 rounded">
                    {metadata.column_names.join(", ")}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
      
      {data && data.metadata && (
        <div className="bg-white border rounded p-3">
          <h4 className="font-semibold mb-3">Parsing Details</h4>
          <div className="text-sm space-y-2">
            {Object.entries(data.metadata).map(([key, value]) => (
              <div key={key} className="flex justify-between">
                <span className="font-medium">{key}:</span>
                <span className="text-gray-600">{String(value)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}; 