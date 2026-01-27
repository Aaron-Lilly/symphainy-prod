/**
 * ParsePreview - Using Semantic APIs via ContentAPIManager
 * 
 * Production-grade ParsePreview component that uses semantic APIs for file parsing and preview.
 * Includes file selection, tabbed data view, export options, and comprehensive error handling.
 */

"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { 
  FileText, 
  Play, 
  Loader2, 
  AlertCircle,
  CheckCircle,
  Clock,
  Code,
  Database,
  XCircle,
  Download
} from 'lucide-react';
// ✅ PHASE 4: Session-First - Use SessionBoundary for session state
import { useSessionBoundary, SessionStatus } from '@/shared/state/SessionBoundaryProvider';
import { usePlatformState } from '@/shared/state/PlatformStateProvider';
import { useContentAPIManager } from '@/shared/hooks/useContentAPIManager';
import { FileMetadata, FileStatus, FileType } from '@/shared/types/file';
import { toast } from 'sonner';
import { StructuredDataTab } from '@/components/content/tabs/StructuredDataTab';
import { TextDataTab } from '@/components/content/tabs/TextDataTab';
import { SOPWorkflowTab } from '@/components/content/tabs/SOPWorkflowTab';
import { FileInfoTab } from '@/components/content/tabs/FileInfoTab';
import { IssuesTab } from '@/components/content/tabs/IssuesTab';
import { ExportOptions } from '@/components/content/ExportOptions';

type ParseState = "idle" | "parsing" | "success" | "error";

interface ParseResult {
  file_id: string;
  format: string;
  chunks?: any[];
  structured_data?: any;
  metadata?: any;
  parsed_data?: any;
  preview_grid?: any[];
  text?: string;
}

interface ParsePreviewNewProps {
  selectedFile?: FileMetadata | null;
  onParseComplete?: (file: FileMetadata, parseResult: ParseResult) => void;
  onParseError?: (error: string) => void;
  className?: string;
}

// Helper to combine and deduplicate files from all pillar states
function combineAndDeduplicateFiles(pillarStates: any[]): FileMetadata[] {
  const allFiles: FileMetadata[] = [];
  
  pillarStates.forEach(state => {
    if (state?.files) {
      allFiles.push(...state.files);
    }
  });

  // Deduplicate by UUID
  const uniqueFilesMap = new Map<string, FileMetadata>();
  allFiles.forEach((file) => {
    if (!uniqueFilesMap.has(file.uuid)) {
      uniqueFilesMap.set(file.uuid, file);
    }
  });

  return Array.from(uniqueFilesMap.values())
    .filter((file: FileMetadata) => file.status === FileStatus.Uploaded)
    .sort((a, b) => {
      const dateA = new Date(a.created_at || 0).getTime();
      const dateB = new Date(b.created_at || 0).getTime();
      return dateB - dateA;
    });
}

// Get tabs for file type
function getTabsForFileType(fileType: FileType | string): Array<{ id: string; label: string }> {
  const baseTabs = [
    { id: "preview", label: "Preview" },
    { id: "file-info", label: "File Info" },
    { id: "issues", label: "Issues" },
  ];

  // Handle both enum values and string values
  const typeStr = typeof fileType === 'string' ? fileType.toLowerCase() : fileType;

  switch (typeStr) {
    case FileType.Structured:
    case 'structured':
    case 'csv':
    case 'xlsx':
    case 'xls':
      return [
        ...baseTabs,
        { id: "structured-data", label: "Structured Data" },
      ];
    case FileType.Pdf:
    case FileType.Image:
    case 'pdf':
    case 'image':
    case 'png':
    case 'jpg':
    case 'jpeg':
      return [
        ...baseTabs,
        { id: "text-data", label: "Text Data" },
      ];
    case FileType.SopWorkflow:
    case 'sop':
    case 'workflow':
    case 'sop-workflow':
      return [
        ...baseTabs,
        { id: "sop-workflow", label: "SOP/Workflow" },
      ];
    default:
      return baseTabs;
  }
}

// Parse status indicator component
function ParseStatusIndicator({ parseState }: { parseState: ParseState }) {
  const getStatusConfig = () => {
    switch (parseState) {
      case 'success':
        return { icon: CheckCircle, color: 'text-green-600', label: 'Parse Successful' };
      case 'error':
        return { icon: AlertCircle, color: 'text-red-600', label: 'Parse Failed' };
      case 'parsing':
        return { icon: Loader2, color: 'text-blue-600', label: 'Parsing...' };
      default:
        return { icon: Clock, color: 'text-gray-600', label: 'Ready to Parse' };
    }
  };

  const { icon: Icon, color, label } = getStatusConfig();

  return (
    <div className={`flex items-center space-x-2 ${color}`}>
      {parseState === 'parsing' ? (
        <Icon className="h-5 w-5 animate-spin" />
      ) : (
        <Icon className="h-5 w-5" />
      )}
      <span className="text-sm font-medium">{label}</span>
    </div>
  );
}

export function ParsePreviewNew({ 
  selectedFile: propSelectedFile, 
  onParseComplete,
  onParseError,
  className
}: ParsePreviewNewProps) {
  // ✅ PHASE 4: Session-First - Use SessionBoundary for session state
  const { state: sessionState } = useSessionBoundary();
  const { state, getRealmState } = usePlatformState();
  const isAuthenticated = sessionState.status === SessionStatus.Active;
  const contentAPIManager = useContentAPIManager();
  
  const [selectedFileUuid, setSelectedFileUuid] = useState<string | null>(null);
  const [parseState, setParseState] = useState<ParseState>("idle");
  const [parseResult, setParseResult] = useState<ParseResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [activeTab, setActiveTab] = useState("preview");

  // Get files from realm states
  const contentFiles = state.realm.content.files || [];
  const journeyFiles = state.realm.journey.files || [];
  const insightsFiles = state.realm.insights.files || [];

  const filesToParse = combineAndDeduplicateFiles([
    { files: contentFiles },
    { files: journeyFiles },
    { files: insightsFiles },
  ]);

  const selectedFile = filesToParse.find((f) => f.uuid === selectedFileUuid) || propSelectedFile;

  // Auto-select first file if none selected
  useEffect(() => {
    if (propSelectedFile) {
      setSelectedFileUuid(propSelectedFile.uuid || propSelectedFile.file_id || null);
    } else if (filesToParse.length > 0 && !selectedFileUuid) {
      setSelectedFileUuid(filesToParse[0].uuid);
    }
    
    // Reset if selected file no longer exists
    if (selectedFileUuid && !filesToParse.some((f) => f.uuid === selectedFileUuid)) {
      setSelectedFileUuid(null);
      setParseState("idle");
    }
  }, [filesToParse, selectedFileUuid, propSelectedFile]);

  // Reset parse state when file changes
  useEffect(() => {
    if (selectedFileUuid) {
      setParseResult(null);
      setError(null);
      setParseState("idle");
      setActiveTab("preview");
    }
  }, [selectedFileUuid]);

  // Handle file parsing using semantic API
  const handleParse = useCallback(async () => {
    if (!selectedFile) {
      toast.error("No file selected");
      return;
    }

    // Validate file status
    if (selectedFile.status !== FileStatus.Uploaded) {
      toast.error("Cannot parse file with this status");
      return;
    }

    // Check if file type supports parsing
    if (selectedFile.file_type === FileType.SopWorkflow) {
      toast.error("SOP/Workflow files are processed in the Operations pillar");
      return;
    }

    setParseState("parsing");
    setError(null);
    setParseResult(null);

    try {
      const fileId = selectedFile.file_id || selectedFile.uuid;
      const fileReference = (selectedFile as any).file_reference || (selectedFile.metadata as any)?.file_reference || `file:${state.session.tenantId}:${state.session.sessionId}:${fileId}`;
      const result = await contentAPIManager.parseFile(fileId, fileReference);

      if (result.success && result.parsed_file_id) {
        const parsedData: ParseResult = {
          file_id: fileId,
          format: result.parsed_content?.format || 'json_structured',
          chunks: result.parsed_content?.chunks,
          structured_data: result.parsed_content?.structured_data,
          metadata: result.parsed_content?.metadata,
          parsed_data: result.parsed_content,
          preview_grid: result.parsed_content?.preview_grid,
          text: result.parsed_content?.text,
        };
        
        setParseResult(parsedData);
        setParseState("success");
        
        toast.success('File parsed successfully!', {
          description: `File "${selectedFile.ui_name || selectedFile.original_filename || fileId}" has been parsed.`
        });

        if (onParseComplete) {
          onParseComplete(selectedFile, parsedData);
        }
      } else {
        const errorMsg = result.error || 'Parsing failed';
        setError(errorMsg);
        setParseState("error");
        toast.error('Parsing failed', {
          description: errorMsg
        });
        
        if (onParseError) {
          onParseError(errorMsg);
        }
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Parsing failed';
      setError(errorMessage);
      setParseState("error");
      toast.error('Parsing failed', {
        description: errorMessage
      });
      
      if (onParseError) {
        onParseError(errorMessage);
      }
    }
  }, [selectedFile, state.session.sessionId, contentAPIManager, onParseComplete, onParseError]);

  const resetParse = useCallback(() => {
    setParseState("idle");
    setError(null);
    setParseResult(null);
    setActiveTab("preview");
  }, []);

  // Render tab content
  const renderTabContent = (tabId: string) => {
    if (!parseResult) return null;

    switch (tabId) {
      case "preview":
        return (
          <div className="space-y-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-medium mb-2">Data Preview</h4>
              <pre className="text-sm overflow-x-auto max-h-60">
                {JSON.stringify(parseResult.parsed_data || parseResult, null, 2)}
              </pre>
            </div>
          </div>
        );
      
      case "structured-data":
        return <StructuredDataTab data={parseResult} metadata={parseResult.metadata || {}} />;
      
      case "text-data":
        return <TextDataTab data={parseResult} metadata={parseResult.metadata || {}} />;
      
      case "sop-workflow":
        // SOPWorkflowTab needs the full FileMetadata object, not just ParseResult
        if (!selectedFile) return <div>No file selected</div>;
        return <SOPWorkflowTab file={selectedFile} metadata={parseResult.metadata || {}} />;
      
      case "file-info":
        return <FileInfoTab data={parseResult} metadata={parseResult.metadata || {}} />;
      
      case "issues":
        return <IssuesTab data={parseResult} />;
      
      default:
        return <div>Tab content not found</div>;
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="p-6 text-center">
        <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Authentication Required</h3>
        <p className="text-gray-600">Please log in to parse files.</p>
      </div>
    );
  }

  // No files available
  if (filesToParse.length === 0) {
    return (
      <div className={`space-y-4 ${className || ''}`} data-testid="content-pillar-parse-preview">
        <div className="relative block w-full rounded-lg border-2 border-dashed p-12 text-center border-gray-300 h-[185px] flex items-center justify-center">
          <div className="text-gray-500">
            <FileText className="mx-auto h-12 w-12 mb-2" />
            <p>No files available for parsing</p>
            <p className="text-sm">Upload a file first to begin parsing</p>
          </div>
        </div>
      </div>
    );
  }

  const tabs = selectedFile ? getTabsForFileType(selectedFile.file_type) : [];

  return (
    <div className={`space-y-4 ${className || ''}`} data-testid="content-pillar-parse-preview">
      {/* File Selection */}
      <div className="space-y-2">
        <label className="text-sm font-medium text-gray-700">Select File to Parse</label>
        <Select
          value={selectedFileUuid || ''}
          onValueChange={setSelectedFileUuid}
          data-testid="parse-file-selector"
        >
          <SelectTrigger>
            <SelectValue placeholder="Choose a file to parse" />
          </SelectTrigger>
          <SelectContent>
            {filesToParse.map((file) => (
              <SelectItem key={file.uuid} value={file.uuid}>
                <div className="flex flex-col">
                  <span className="font-medium">{file.ui_name || file.original_filename || file.uuid}</span>
                  <span className="text-xs text-gray-500">{file.file_type}</span>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Parse Status */}
      {parseState !== 'idle' && (
        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <ParseStatusIndicator parseState={parseState} />
          {parseState === 'success' && parseResult && (
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => setShowDetailsModal(true)}
              data-testid="view-parse-details-button"
            >
              View Details
            </Button>
          )}
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="text-red-600 text-sm p-3 bg-red-50 rounded-lg border border-red-200">
          <div className="flex items-center space-x-2">
            <AlertCircle className="h-4 w-4" />
            <span>{error}</span>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex space-x-2">
        <Button
          onClick={handleParse}
          disabled={!selectedFile || parseState === 'parsing'}
          className="flex-1"
          data-testid="parse-file-button"
          aria-label="Parse selected file"
        >
          {parseState === 'parsing' ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Parsing...
            </>
          ) : (
            <>
              <Play className="h-4 w-4 mr-2" />
              Parse File
            </>
          )}
        </Button>

        {parseState !== 'idle' && (
          <Button 
            onClick={resetParse} 
            variant="ghost" 
            size="sm"
            data-testid="reset-parse-button"
          >
            Reset
          </Button>
        )}
      </div>

      {/* Parsed Data Display with Tabs */}
      {parseState === 'success' && parseResult && selectedFile && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Parse Results</span>
              <div className="flex items-center space-x-2">
                <Badge variant="outline" className="flex items-center space-x-1">
                  {parseResult.format === 'json_structured' && <Database className="h-3 w-3" />}
                  {parseResult.format === 'json_chunks' && <FileText className="h-3 w-3" />}
                  {parseResult.format === 'parquet' && <Code className="h-3 w-3" />}
                  <span>{parseResult.format}</span>
                </Badge>
                {parseResult.chunks && (
                  <Badge variant="outline">
                    {parseResult.chunks.length} chunks
                  </Badge>
                )}
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Tab Navigation */}
            {tabs.length > 0 && (
              <div className="border-b border-gray-200">
                <nav className="-mb-px flex space-x-8">
                  {tabs.map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`py-2 px-1 border-b-2 text-sm font-medium transition-colors ${
                        activeTab === tab.id
                          ? 'border-blue-500 text-blue-600'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      }`}
                      data-testid={`parse-tab-${tab.id}`}
                    >
                      {tab.label}
                    </button>
                  ))}
                </nav>
              </div>
            )}
            
            {/* Tab Content */}
            <div className="mt-4" data-testid="parse-results-content">
              {renderTabContent(activeTab)}
            </div>

            {/* Export Options */}
            {parseResult && (
              <div className="pt-4 border-t">
                <ExportOptions 
                  data={parseResult} 
                  fileType={selectedFile.file_type} 
                  fileName={selectedFile.ui_name || selectedFile.original_filename || 'parsed_data'} 
                />
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Details Modal */}
      {showDetailsModal && parseResult && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" data-testid="parse-details-modal">
          <div className="bg-white rounded-lg p-6 max-w-4xl max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Parsed Data Details</h3>
              <Button variant="ghost" onClick={() => setShowDetailsModal(false)}>
                <XCircle className="h-5 w-5" />
              </Button>
            </div>
            
            <div className="space-y-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-medium mb-2">Data Summary</h4>
                <pre className="text-sm overflow-x-auto">
                  {JSON.stringify(parseResult, null, 2)}
                </pre>
              </div>
              
              <div className="flex justify-end space-x-2">
                <Button variant="outline" onClick={() => setShowDetailsModal(false)}>
                  Close
                </Button>
                {selectedFile && (
                  <ExportOptions 
                    data={parseResult} 
                    fileType={selectedFile.file_type} 
                    fileName={selectedFile.ui_name || 'parsed_data'} 
                  />
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
