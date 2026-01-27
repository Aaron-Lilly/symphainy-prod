/**
 * ParsePreview - Component for previewing parsed files
 * 
 * Handles selecting parsed files and generating previews.
 * This component is separate from FileParser which handles parsing.
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
  Loader2, 
  AlertCircle,
  Code,
  RefreshCw
} from 'lucide-react';
// ✅ PHASE 4: Session-First - Use SessionBoundary for session state
import { useSessionBoundary, SessionStatus } from '@/shared/state/SessionBoundaryProvider';
import { usePlatformState } from '@/shared/state/PlatformStateProvider';
import { useContentAPIManager } from '@/shared/managers/ContentAPIManager';
import { FileMetadata, FileStatus } from '@/shared/types/file';
import { FileSelector } from './FileSelector';
import { StructuredDataTab } from '@/components/content/tabs/StructuredDataTab';

interface ParsePreviewProps {
  selectedFile?: FileMetadata | null;
  className?: string;
}

export function ParsePreview({ 
  selectedFile: propSelectedFile, 
  className
}: ParsePreviewProps) {
  // ✅ PHASE 4: Session-First - Use SessionBoundary for session state
  const { state: sessionState } = useSessionBoundary();
  const { state, submitIntent, getExecutionStatus } = usePlatformState();
  const isAuthenticated = sessionState.status === SessionStatus.Active;
  const contentAPIManager = useContentAPIManager();
  
  const [parsedFiles, setParsedFiles] = useState<any[]>([]);
  const [selectedParsedFileId, setSelectedParsedFileId] = useState<string | null>(null);
  const [parsedFilePreview, setParsedFilePreview] = useState<any>(null);
  const [loadingParsedFiles, setLoadingParsedFiles] = useState(false);
  const [loadingPreview, setLoadingPreview] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load ALL parsed files from parsed_data_files table
  // With the backend fix, parsed_file_id now matches the actual GCS UUID, so lookups work correctly
  // ✅ PHASE 4: Migrate to intent-based API (list_files intent)
  const loadParsedFiles = useCallback(async () => {
    if (!sessionState.sessionId || !sessionState.tenantId) {
      setParsedFiles([]);
      setSelectedParsedFileId(null);
      setParsedFilePreview(null);
      return;
    }

    setLoadingParsedFiles(true);
    setError(null);
    try {
        setParsedFiles([]);
        setError('Session required to load files');
        return;
      }

      // Submit list_files intent to get all files
      const executionId = await submitIntent(
        'list_files',
        {
          // Optional: Add file_type filter if we want to filter parsed files
          // For now, get all files and filter client-side for parsed status
        }
      );

      // Wait for execution to complete
      const maxAttempts = 10;
      let attempts = 0;
      let files: any[] = [];

      while (attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 500));
        
        const status = await getExecutionStatus(executionId);
        
        if (status?.status === "completed") {
          // Extract files from execution artifacts
          const fileListArtifact = status.artifacts?.file_list;
          if (fileListArtifact?.semantic_payload?.files) {
            files = fileListArtifact.semantic_payload.files;
          }
          break;
        } else if (status?.status === "failed") {
          throw new Error(status.error || "Failed to load files");
        }
        
        attempts++;
      }

      // Filter for parsed files (files that have been parsed)
      // Note: This is a client-side filter - in the future, we could add a status filter to the intent
      const parsedFiles = files.filter((file: any) => {
        // Files are considered "parsed" if they have parsing metadata or status
        // This logic may need adjustment based on actual file structure
        return file.file_type === 'parsed' || file.status === 'parsed' || file.parsed_file_id;
      });

      setParsedFiles(parsedFiles);
      
      // Auto-select first parsed file if available and none selected
      if (parsedFiles.length > 0 && !selectedParsedFileId) {
        const firstFileId = parsedFiles[0].parsed_file_id || parsedFiles[0].file_id || parsedFiles[0].id;
        setSelectedParsedFileId(firstFileId);
      }
    } catch (error) {
      console.error('[ParsePreview] Error loading parsed files:', error);
      setParsedFiles([]);
      setError(error instanceof Error ? error.message : 'Failed to load parsed files');
    } finally {
      setLoadingParsedFiles(false);
    }
  }, [sessionState.sessionId, sessionState.tenantId, selectedParsedFileId, submitIntent, getExecutionStatus]);

  // Load parsed files on mount and when session changes
  useEffect(() => {
    loadParsedFiles();
  }, [sessionState.sessionId, loadParsedFiles]);

  // Listen for parse completion events from FileParser
  useEffect(() => {
    const handleParseComplete = () => {
      // Refresh parsed files list when a file is parsed
      loadParsedFiles();
    };

    // Listen for custom event from FileParser
    window.addEventListener('fileParsed', handleParseComplete);
    
    // Also listen for storage events (if files are updated in another tab)
    window.addEventListener('storage', (e) => {
      if (e.key === 'fileParsed') {
        handleParseComplete();
      }
    });

    return () => {
      window.removeEventListener('fileParsed', handleParseComplete);
      window.removeEventListener('storage', handleParseComplete);
    };
  }, [state.session.sessionId]);

  // Handle preview generation (manual trigger via button)
  const handleGeneratePreview = async () => {
    if (!selectedParsedFileId || !state.session.sessionId) {
      setError('Missing parsed file ID or session');
      return;
    }

    setLoadingPreview(true);
    setParsedFilePreview(null);
    setError(null);
    
    try {
      // Get parsed file preview using new ContentAPIManager
      // Note: getParsedFile method returns parsed content and preview
      const fileReference = `parsed:${state.session.tenantId}:${state.session.sessionId}:${selectedParsedFileId}`;
      const result = await contentAPIManager.getParsedFile(selectedParsedFileId, fileReference);
      
      if (result.success && result.parsed_content) {
        // Use parsed_content and preview from result
        const previewData = result.preview || result.parsed_content;
        setParsedFilePreview({
          format: 'jsonl',
          preview_grid: previewData.rows || [],
          metadata: {
            column_names: previewData.columns || [],
            rows: previewData.total_rows || 0,
            columns: previewData.total_columns || 0,
            preview_rows: previewData.preview_rows || 0,
            preview_columns: previewData.preview_columns || 0
          }
        });
      } else {
        setError(result.error || 'Failed to generate preview');
      }
    } catch (error) {
      console.error('[ParsePreview] Error generating preview:', error);
      setError(error instanceof Error ? error.message : 'Failed to generate preview');
      setParsedFilePreview(null);
    } finally {
      setLoadingPreview(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="p-6 text-center">
        <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Authentication Required</h3>
        <p className="text-gray-600">Please log in to preview parsed files.</p>
      </div>
    );
  }

  return (
    <div className={`space-y-4 ${className || ''}`} data-testid="parse-preview">
      {/* Parsed Files Selection - Show all parsed files directly */}
      <div className="space-y-2" data-testid="parsed-files-selector-wrapper">
        <div className="flex items-center justify-between">
          <label className="text-sm font-medium text-gray-700">
            Select Parsed File to Preview
          </label>
          <Button
            variant="ghost"
            size="sm"
            onClick={loadParsedFiles}
            disabled={loadingParsedFiles}
            className="h-8"
            title="Refresh parsed files list"
          >
            <RefreshCw className={`h-4 w-4 ${loadingParsedFiles ? 'animate-spin' : ''}`} />
          </Button>
        </div>
        {loadingParsedFiles ? (
          <div className="text-sm text-gray-500 py-2">Loading parsed files...</div>
        ) : (
          <Select
            value={selectedParsedFileId || undefined}
            onValueChange={(value) => {
              setSelectedParsedFileId(value);
              setParsedFilePreview(null); // Clear previous preview when selecting new file
              setError(null);
            }}
            disabled={loadingParsedFiles || parsedFiles.length === 0}
          >
            <SelectTrigger data-testid="parsed-files-selector">
              <SelectValue placeholder={parsedFiles.length > 0 ? "Choose a parsed file to preview" : "No parsed files available"} />
            </SelectTrigger>
            <SelectContent>
              {parsedFiles.length > 0 ? (
                parsedFiles.map((parsedFile) => (
                  <SelectItem 
                    key={parsedFile.parsed_file_id || parsedFile.id} 
                    value={parsedFile.parsed_file_id || parsedFile.id}
                  >
                    {parsedFile.name || parsedFile.parsed_file_id || parsedFile.id}
                    {parsedFile.created_at && ` (${new Date(parsedFile.created_at).toLocaleDateString()})`}
                  </SelectItem>
                ))
              ) : (
                <SelectItem value="no-files" disabled>No parsed files available</SelectItem>
              )}
            </SelectContent>
          </Select>
        )}
        <p className="text-xs text-gray-500">
          {parsedFiles.length > 0 
            ? "Select a parsed file to preview its data."
            : "No parsed files available yet. Parse a file in the File Parsing section first."}
        </p>
      </div>

      {/* Error Display */}
      {error && (
        <div className="text-red-600 text-sm p-3 bg-red-50 rounded-lg border border-red-200">
          <div className="flex items-center space-x-2">
            <AlertCircle className="h-4 w-4" />
            <span>{error}</span>
          </div>
        </div>
      )}

      {/* Generate Preview Button - Show when parsed file is selected */}
      {selectedParsedFileId && (
        <Button
          onClick={handleGeneratePreview}
          disabled={loadingPreview || !selectedParsedFileId}
          className="w-full"
          data-testid="generate-preview-button"
          aria-label="Generate preview for selected parsed file"
        >
          {loadingPreview ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Generating Preview...
            </>
          ) : (
            <>
              <FileText className="h-4 w-4 mr-2" />
              Generate Preview
            </>
          )}
        </Button>
      )}

      {/* Preview Display */}
      <div className="mt-4">
        {parsedFilePreview && selectedParsedFileId ? (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Preview: {parsedFiles.find(f => (f.parsed_file_id || f.id) === selectedParsedFileId)?.name || selectedParsedFileId}</span>
                <Badge variant="outline" className="flex items-center space-x-1">
                  <Code className="h-3 w-3" />
                  <span>{parsedFiles.find(f => (f.parsed_file_id || f.id) === selectedParsedFileId)?.format_type?.toUpperCase() || 'JSONL'}</span>
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loadingPreview ? (
                <div className="flex items-center justify-center p-8">
                  <Loader2 className="h-6 w-6 animate-spin mr-2" />
                  <span>Loading preview...</span>
                </div>
              ) : (
                <StructuredDataTab 
                  data={parsedFilePreview}
                  metadata={parsedFilePreview.metadata || {}}
                />
              )}
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardHeader>
              <CardTitle>Parse Preview</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="relative block w-full rounded-lg border-2 border-dashed p-12 text-center border-gray-300 min-h-[300px] flex items-center justify-center">
                <div className="text-gray-500">
                  {parsedFiles.length === 0 ? (
                    <>
                      <FileText className="mx-auto h-12 w-12 mb-2" />
                      <p className="font-medium">No parsed files available</p>
                      <p className="text-sm mt-1">Parse a file in the File Parsing section first to see it here.</p>
                    </>
                  ) : !selectedParsedFileId ? (
                    <>
                      <FileText className="mx-auto h-12 w-12 mb-2" />
                      <p className="font-medium">Select a parsed file to preview</p>
                      <p className="text-sm mt-1">Choose a parsed file from the dropdown above to preview its data</p>
                    </>
                  ) : (
                    <>
                      <FileText className="mx-auto h-12 w-12 mb-2" />
                      <p className="font-medium">Ready to generate preview</p>
                      <p className="text-sm mt-1">Click "Generate Preview" to view the parsed data</p>
                    </>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
