"use client";
import React from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { EmptyState } from "@/components/ui/empty-state";
import { ArrowLeft, FileText, Bot, Loader2, AlertTriangle } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { FileMetadata, FileType } from "@/shared/types/file";

const FILE_CATEGORIES = [
  { key: "SOP", label: "Standard Operating Procedure (SOP)" },
  { key: "workflow", label: "Workflow Document" },
];

interface FileSelectorProps {
  operationFiles: FileMetadata[];
  selected: { [type: string]: FileMetadata | null };
  onSelectionChange: (type: string, file: FileMetadata | null) => void;
  onAnalyze: () => void;
  onBack: () => void;
  isLoadingFiles: boolean;
}

// Helper function to check if a file can be used for operations
const isOperationFile = (file: FileMetadata): boolean => {
  return (
    file.file_type === FileType.Document || 
    file.file_type === FileType.Pdf ||
    file.file_type === FileType.Text ||
    file.file_type === FileType.SopWorkflow
  );
};

// Helper function to get file type display name
const getFileTypeDisplay = (fileType: FileType | string): string => {
  const type = fileType as FileType;
  switch (type) {
    case FileType.Document:
      return "Document";
    case FileType.Pdf:
      return "PDF";
    case FileType.Text:
      return "Text";
    case FileType.SopWorkflow:
      return "SOP/Workflow";
    default:
      return fileType;
  }
};

export default function FileSelector({
  operationFiles,
  selected,
  onSelectionChange,
  onAnalyze,
  onBack,
  isLoadingFiles,
}: FileSelectorProps) {
  // Filter files to only show operation-relevant files
  const availableFiles = operationFiles.filter(isOperationFile);

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-center">
          <CardTitle>Select Files for Analysis</CardTitle>
          <Button variant="outline" size="sm" onClick={onBack}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
        </div>
        <CardDescription>
          Select an SOP to generate a workflow, a workflow to generate an SOP,
          or both files to generate both outputs.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {isLoadingFiles ? (
          <div className="flex items-center justify-center p-12">
            <Loader2 className="mr-2 h-8 w-8 animate-spin" /> Loading files...
          </div>
        ) : (
          <div className="flex flex-col sm:flex-row items-end gap-4">
            {FILE_CATEGORIES.map((category) => (
              <div key={category.key} className="flex-1 w-full">
                <label
                  htmlFor={`select-${category.key}`}
                  className="text-sm font-medium mb-2 block"
                >
                  {category.label}
                </label>
                <Select
                  value={selected[category.key]?.uuid || ""}
                  onValueChange={(value) => {
                    const file = availableFiles.find((f) => f.uuid === value);
                    onSelectionChange(category.key, file || null);
                  }}
                >
                  <SelectTrigger>
                    <SelectValue
                      placeholder={`Select a ${category.key} file...`}
                    />
                  </SelectTrigger>
                  <SelectContent>
                    {availableFiles.length === 0 ? (
                      <div className="p-4 text-center text-muted-foreground">
                        <p>No operation files available</p>
                        <p className="text-xs mt-1">
                          Upload Document or PDF files in Content Pillar
                        </p>
                      </div>
                    ) : (
                      availableFiles.map((f) => (
                        <SelectItem key={f.uuid} value={f.uuid}>
                          <div className="flex items-center justify-between w-full">
                            <span className="font-medium">{f.ui_name}</span>
                            <span className="text-xs text-muted-foreground ml-2">
                              {getFileTypeDisplay(f.file_type)} • {f.status}
                            </span>
                          </div>
                        </SelectItem>
                      ))
                    )}
                  </SelectContent>
                </Select>
              </div>
            ))}
            <Button
              disabled={(!selected["SOP"] && !selected["workflow"]) || false}
              onClick={onAnalyze}
              className="w-full sm:w-auto mt-4 sm:mt-0"
            >
              {false ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Bot className="mr-2 h-4 w-4" />
                  {selected["SOP"] && selected["workflow"]
                    ? "Analyze Both Files"
                    : selected["workflow"]
                      ? "Generate Workflow"
                      : "Generate SOP"}
                </>
              )}
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
