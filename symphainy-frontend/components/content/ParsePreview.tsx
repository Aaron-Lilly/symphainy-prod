"use client";

import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import {
  FileMetadata,
  FileStatus,
} from "@/shared/types/file";
// ✅ PHASE 2: Use service layer hook instead of direct API calls
import { useFileAPI } from "@/shared/hooks/useFileAPI";
import { useSessionBoundary } from "@/shared/state/SessionBoundaryProvider";
import { usePlatformState } from "@/shared/state/PlatformStateProvider";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { CheckCircle, FileText, XCircle } from "lucide-react";
import { Loader } from "@/components/ui/loader";
import { toast } from "sonner";
import { FileType } from "@/shared/types/file";
import { StructuredDataTab } from "./tabs/StructuredDataTab";
import { TextDataTab } from "./tabs/TextDataTab";
import { SOPWorkflowTab } from "./tabs/SOPWorkflowTab";
import { FileInfoTab } from "./tabs/FileInfoTab";
import { IssuesTab } from "./tabs/IssuesTab";
import { ExportOptions } from "./ExportOptions";

type ParseState = "idle" | "parsing" | "success" | "error";

export default function ParsePreview() {
  // ✅ PHASE 1: Migrated to SessionBoundaryProvider
  // ✅ PHASE 2: Use service layer hook
  const { state: sessionState } = useSessionBoundary();
  const { parseFile } = useFileAPI();
  // ✅ PHASE 1: Migrated to PlatformStateProvider - use realm state
  const { getRealmState } = usePlatformState();

  const [selectedFileUuid, setSelectedFileUuid] = useState<string | null>(null);
  const [parseState, setParseState] = useState<ParseState>("idle");
  const [error, setError] = useState<string | null>(null);
  const [isApproving, setIsApproving] = useState(false);
  const [parsedData, setParsedData] = useState<any>(null); // NEW: Store parsed data
  const [showDetailsModal, setShowDetailsModal] = useState(false); // NEW: Modal state
  const [activeTab, setActiveTab] = useState("preview"); // NEW: Tab state

  // ✅ PHASE 1: Get files from all realm states to find uploaded files
  const parsingFiles = getRealmState("content", "parsing_files") || [];
  const contentFiles = getRealmState("content", "files") || [];
  const insightsFiles = getRealmState("insights", "files") || [];
  const journeyFiles = getRealmState("journey", "files") || [];

  // ✅ PHASE 1: Combine all files and deduplicate by UUID
  const allFiles = [
    ...(Array.isArray(parsingFiles) ? parsingFiles : []),
    ...(Array.isArray(contentFiles) ? contentFiles : []),
    ...(Array.isArray(insightsFiles) ? insightsFiles : []),
    ...(Array.isArray(journeyFiles) ? journeyFiles : []),
  ];

  const uniqueFilesMap = new Map();
  allFiles.forEach((file) => {
    if (!uniqueFilesMap.has(file.uuid)) {
      uniqueFilesMap.set(file.uuid, file);
    }
  });

  const filesToParse = Array.from(uniqueFilesMap.values())
    .filter((file: FileMetadata) => file.status === FileStatus.Uploaded)
    .sort((a, b) => {
      // Sort by created_at (most recent first)
      const dateA = new Date(a.created_at || 0).getTime();
      const dateB = new Date(b.created_at || 0).getTime();
      return dateB - dateA;
    });

  // Auto-select the first file if none is selected
  useEffect(() => {
    if (filesToParse.length > 0 && !selectedFileUuid) {
      setSelectedFileUuid(filesToParse[0].uuid);
    }
    // Reset if selected file no longer exists
    if (
      selectedFileUuid &&
      !filesToParse.some((f) => f.uuid === selectedFileUuid)
    ) {
      setSelectedFileUuid(null);
      setParseState("idle");
    }
  }, [filesToParse, selectedFileUuid]);

  const selectedFile = filesToParse.find((f) => f.uuid === selectedFileUuid);

  const handleParse = async () => {
    if (!selectedFile) {
      toast.error("No file selected");
      return;
    }

    // Check if file status allows parsing
    if (selectedFile.status !== FileStatus.Uploaded) {
      toast.error("Cannot parse file with this status");
      return;
    }

    // Check if file type supports parsing (SOP/Workflow files are not parsed in Content pillar)
    if (selectedFile.file_type === FileType.SopWorkflow) {
      toast.error("SOP/Workflow files are processed in the Operations pillar");
      return;
    }

    setParseState("parsing");
    setError(null);
    setParsedData(null); // Clear previous parsed data

    try {
      // ✅ PHASE 2: Use service layer hook - no need to pass token manually
      const result = await parseFile(selectedFile.uuid);
      
      // Store the parsed data from cloud function
      setParsedData(result);
      setParseState("success");
    } catch (e: any) {
      setError(e.message || "Parse failed.");
      setParseState("error");
      toast.error("Error parsing file");
      console.error("Parse error:", e);
    }
  };

  // Approve/reject functionality removed - no longer needed

  const resetParse = () => {
    setParseState("idle");
    setError(null);
  };

  // No files available
  if (filesToParse.length === 0) {
    return (
      <div className="space-y-4">
        <div className="relative block w-full rounded-lg border-2 border-dashed p-12 text-center border-border h-[185px] flex items-center justify-center">
          <div className="text-muted-foreground">
            <FileText className="mx-auto h-12 w-12 mb-2" />
            <p>No files available for parsing</p>
            <p className="text-sm">Upload a file first to begin parsing</p>
          </div>
        </div>
      </div>
    );
  }

  // NEW: Modal component for detailed view
  const ParsedDataModal = ({ data, onClose }: { data: any; onClose: () => void }) => {
    if (!data) return null;
    
    return (
      <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg w-full max-w-4xl h-[80vh] flex flex-col">
          {/* Header */}
          <div className="flex justify-between items-center p-4 border-b">
            <h2 className="text-lg font-semibold">Parsed Data Details</h2>
            <Button onClick={onClose} variant="ghost" size="sm">
              ✕
            </Button>
          </div>
          
          {/* Content */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {/* Data Grid */}
            {data.preview_grid && data.preview_grid.length > 0 && (
              <div className="bg-white border rounded p-3">
                <h4 className="font-semibold mb-2">Data Preview</h4>
                <div className="overflow-x-auto">
                  <table className="min-w-full border">
                    <thead>
                      <tr>
                        {data.preview_grid[0]?.map((col: string, idx: number) => (
                          <th key={idx} className="border px-2 py-1 bg-gray-50 text-left text-sm">
                            {col}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {data.preview_grid.slice(1, 20).map((row: any[], rowIdx: number) => (
                        <tr key={rowIdx}>
                          {row.map((cell: any, cellIdx: number) => (
                            <td key={cellIdx} className="border px-2 py-1 text-sm">
                              {cell}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Showing first 20 rows of {data.preview_grid.length - 1} total rows
                </p>
              </div>
            )}
            
            {/* Text Content */}
            {data.text && (
              <div className="bg-white border rounded p-3">
                <h4 className="font-semibold mb-2">Extracted Text</h4>
                <div className="max-h-64 overflow-y-auto text-sm font-mono bg-gray-50 p-3 rounded">
                  {data.text}
                </div>
              </div>
            )}
            
            {/* Metadata */}
            {data.metadata && (
              <div className="bg-white border rounded p-3">
                <h4 className="font-semibold mb-2">File Information</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  {data.metadata.rows && (
                    <div>Rows: {data.metadata.rows}</div>
                  )}
                  {data.metadata.columns && (
                    <div>Columns: {data.metadata.columns}</div>
                  )}
                  {data.metadata.pages && (
                    <div>Pages: {data.metadata.pages}</div>
                  )}
                  {data.metadata.column_names && (
                    <div className="col-span-2">
                      <div className="font-medium">Columns:</div>
                      <div className="text-xs text-gray-600">
                        {data.metadata.column_names.join(", ")}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
          
          {/* Footer */}
          <div className="flex justify-end gap-3 p-4 border-t">
            <Button onClick={onClose} variant="outline">
              Close
            </Button>
            {/* Approve/reject buttons removed - no longer needed */}
          </div>
        </div>
      </div>
    );
  };

  // NEW: Tabbed interface component
  const TabbedParsedData = ({ data, fileType }: { data: any; fileType: FileType }) => {
    // Dynamic tabs based on file type
    const getTabs = () => {
      const baseTabs = [
        { id: "preview", label: "Preview", icon: "📊" },
        { id: "info", label: "Info", icon: "ℹ️" },
        { id: "issues", label: "Issues", icon: "⚠️" },
      ];
      
      if (fileType === FileType.SopWorkflow) {
        return [
          { id: "operations", label: "Operations", icon: "⚙️" },
          ...baseTabs
        ];
      }
      
      if (data.text) {
        baseTabs.splice(1, 0, { id: "text", label: "Text", icon: "📝" });
      }
      
      return baseTabs;
    };
    
    const tabs = getTabs();

    return (
      <div className="w-full h-full flex flex-col">
        {/* Header */}
        <div className="text-center space-y-2 mb-4">
          <CheckCircle className="mx-auto h-8 w-8 text-green-600" />
          <h3 className="text-lg font-semibold">Parsing Complete!</h3>
          <p className="text-sm text-muted-foreground">
            {selectedFile?.ui_name} has been successfully parsed
          </p>
        </div>
        
        {/* Tabs */}
        <div className="flex border-b mb-4">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? "border-blue-500 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              <span>{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>
        
        {/* Tab Content */}
        <div className="flex-1 overflow-y-auto">
          {activeTab === "preview" && (
            <StructuredDataTab data={data} metadata={data.metadata} />
          )}
          
          {activeTab === "text" && data.text && (
            <TextDataTab data={data} metadata={data.metadata} />
          )}
          
          {activeTab === "operations" && fileType === FileType.SopWorkflow && (
            <SOPWorkflowTab file={selectedFile} metadata={data.metadata} />
          )}
          
          {activeTab === "info" && (
            <FileInfoTab data={data} metadata={data.metadata} />
          )}
          
          {activeTab === "issues" && (
            <IssuesTab data={data} />
          )}
        </div>
        
        {/* Action Buttons */}
        <div className="flex gap-3 justify-center pt-4 border-t">
          <ExportOptions data={data} fileType={fileType} fileName={selectedFile?.ui_name || ''} />
          {/* Approve/reject buttons removed - no longer needed */}
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-4">
      {parseState !== "success" && (
        <div>
          <Select
            value={selectedFileUuid || ""}
            onValueChange={(value) => {
              setSelectedFileUuid(value);
              setParseState("idle");
              setError(null);
            }}
            disabled={parseState === "parsing" || isApproving}
          >
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Select a file to parse..." />
            </SelectTrigger>
            <SelectContent className="max-h-60 overflow-y-auto">
              {filesToParse.map((file) => (
                <SelectItem key={file.uuid} value={file.uuid}>
                  <div className="flex items-center justify-between w-full">
                    <span className="font-medium">{file.ui_name}</span>
                    <span className="text-xs text-muted-foreground ml-2">
                      {file.file_type}
                    </span>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      )}

      {/* Main Content Area - Fixed height to match upload component */}
      <div className="relative block w-full rounded-lg border-2 border-dashed p-12 text-center border-border h-full flex items-center justify-center">
        {/* Parsing State */}
        {parseState === "parsing" && (
          <div className="text-center space-y-2">
            <Loader size="xl" className="mx-auto" />
            <h3 className="text-lg font-semibold">Parsing File...</h3>
            <p className="text-sm text-muted-foreground">
              Processing {selectedFile?.ui_name}
            </p>
          </div>
        )}

        {/* Success State */}
        {parseState === "success" && (
          <TabbedParsedData data={parsedData} fileType={selectedFile?.file_type || FileType.Structured} />
        )}

        {/* Error State */}
        {parseState === "error" && (
          <div className="text-center space-y-3">
            <XCircle className="mx-auto h-8 w-8 text-red-500" />
            <h3 className="text-base font-semibold">Parsing Failed</h3>
            <Button onClick={resetParse} variant="outline">
              Try Again
            </Button>
          </div>
        )}

        {/* Idle State - Empty dashed border area like upload */}
        {parseState === "idle" && (
          <div className="text-muted-foreground">
            <FileText className="mx-auto h-12 w-12 mb-2" />
            <span className="text-sm font-semibold">
              Ready to parse selected file
            </span>
          </div>
        )}
      </div>

      {/* Parse Button - Hidden during success state */}
      {parseState !== "success" && (
        <div>
          <Button
            onClick={handleParse}
            disabled={
              !selectedFileUuid || parseState === "parsing" || isApproving
            }
            className="w-full bg-blue-600 text-white"
          >
            Parse Selected File
          </Button>
        </div>
      )}

      {/* Modal for detailed parsed data */}
      {showDetailsModal && parsedData && (
        <ParsedDataModal data={parsedData} onClose={() => setShowDetailsModal(false)} />
      )}
    </div>
  );
}
