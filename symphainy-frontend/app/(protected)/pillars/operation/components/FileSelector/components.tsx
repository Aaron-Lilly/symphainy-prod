// FileSelector UI Components
"use client";
import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/empty-state";
import { FileMetadata, FileType, FileStatus } from "@/shared/types/file";
import { FileSelectorUIProps } from "./types";
import { FileText } from "lucide-react";

export function FileSelectorUI({
  files,
  selected,
  isLoading,
  onSelectionChange,
  getFileIcon,
  getFileTypeLabel,
}: FileSelectorUIProps) {
  if (isLoading) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-3 text-gray-600">Loading files...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (files.length === 0) {
    return (
      <Card>
        <CardContent className="pt-6">
          <EmptyState
            icon={<FileText className="w-12 h-12 text-gray-400" />}
            title="No Files Available"
            description="Upload files to get started with operations"
          />
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {files.map((file) => {
          const isSelected = Object.values(selected).some(selectedFile => 
            selectedFile?.uuid === file.uuid
          );
          const selectionType = Object.entries(selected).find(([_, selectedFile]) => 
            selectedFile?.uuid === file.uuid
          )?.[0];

          return (
            <Card
              key={file.uuid}
              className={`cursor-pointer transition-all duration-200 hover:shadow-md ${
                isSelected 
                  ? 'border-blue-500 bg-blue-50' 
                  : 'hover:border-gray-300'
              }`}
              onClick={() => {
                if (isSelected) {
                  // Deselect if already selected
                  onSelectionChange(selectionType || 'default', null);
                } else {
                  // Select for the first available type
                  const availableTypes = Object.keys(selected).filter(type => !selected[type]);
                  if (availableTypes.length > 0) {
                    onSelectionChange(availableTypes[0], file);
                  }
                }
              }}
            >
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3 flex-1">
                    <div className="text-gray-600">
                      {getFileIcon(file.file_type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium text-gray-900 truncate">
                        {file.ui_name}
                      </h4>
                      <p className="text-sm text-gray-500 truncate">
                        {getFileTypeLabel(file.file_type)}
                      </p>
                      {file.metadata?.size && (
                        <p className="text-xs text-gray-400">
                          {(file.metadata.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="flex flex-col items-end space-y-1">
                    {isSelected && (
                      <Badge variant="secondary" className="text-xs">
                        {selectionType}
                      </Badge>
                    )}
                    <Badge 
                      variant={file.status === FileStatus.Validated ? 'default' : 'secondary'}
                      className="text-xs"
                    >
                      {file.status}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Selection Summary */}
      {Object.entries(selected).some(([_, file]) => file !== null) && (
        <Card className="border-blue-200 bg-blue-50">
          <CardHeader>
            <CardTitle className="text-blue-800">Selected Files</CardTitle>
            <CardDescription className="text-blue-700">
              Files ready for processing
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {Object.entries(selected).map(([type, file]) => {
                if (!file) return null;
                
                return (
                  <div key={type} className="flex items-center justify-between p-3 bg-white rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className="text-gray-600">
                        {getFileIcon(file.file_type)}
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{file.ui_name}</p>
                        <p className="text-sm text-gray-500 capitalize">{type}</p>
                      </div>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => onSelectionChange(type, null)}
                    >
                      Remove
                    </Button>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
} 