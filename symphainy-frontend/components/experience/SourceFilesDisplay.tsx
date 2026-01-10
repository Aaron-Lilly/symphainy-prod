import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { FileText, AlertTriangle, CheckCircle } from "lucide-react";
import { type SourceFile } from "@/lib/api/experience";

interface SourceFilesDisplayProps {
  sourceFiles: SourceFile[];
  title?: string;
  description?: string;
}

export default function SourceFilesDisplay({ 
  sourceFiles, 
  title = "Source Files", 
  description = "Original files from Insights and Operations pillar sessions" 
}: SourceFilesDisplayProps) {
  if (sourceFiles.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
          <CardDescription>{description}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No source files available</p>
            <p className="text-sm text-gray-400 mt-2">
              Complete Insights and Operations pillar analysis first
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <FileText className="h-5 w-5" />
          <span>{title}</span>
          <span className="text-sm text-gray-500">({sourceFiles.length})</span>
        </CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {sourceFiles.map((file) => (
            <div key={file.uuid} className="p-4 border rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-2 flex-1">
                  {file.error ? (
                    <AlertTriangle className="h-4 w-4 text-red-500 flex-shrink-0" />
                  ) : (
                    <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                  )}
                  <div className="min-w-0 flex-1">
                    <div className="font-medium text-sm text-gray-900 truncate">
                      {file.filename}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {file.file_type} • {formatFileSize(file.file_size)}
                    </div>
                    {file.uploaded_at && (
                      <div className="text-xs text-gray-400 mt-1">
                        {new Date(file.uploaded_at).toLocaleDateString()}
                      </div>
                    )}
                  </div>
                </div>
              </div>
              
              {file.error && (
                <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-700">
                  <div className="font-medium">Error:</div>
                  <div>{file.error}</div>
                </div>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return "0 B";
  
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
}