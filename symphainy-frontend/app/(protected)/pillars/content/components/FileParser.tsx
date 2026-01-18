/**
 * FileParser - Component for parsing files
 * 
 * Handles file selection, copybook selection, and parsing.
 * After successful parsing, files are saved and status is updated to "parsed".
 */

"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { 
  FileText, 
  Play, 
  Loader2, 
  AlertCircle,
  CheckCircle,
  Clock
} from 'lucide-react';
import { useAuth } from '@/shared/auth/AuthProvider';
import { usePlatformState } from '@/shared/state/PlatformStateProvider';
import { useContentAPIManager } from '@/shared/managers/ContentAPIManager';
import { FileMetadata, FileStatus, FileType } from '@/shared/types/file';
import { toast } from 'sonner';
import { FileSelector } from './FileSelector';

type ParseState = "idle" | "parsing" | "success" | "error";

interface FileParserProps {
  selectedFile?: FileMetadata | null;
  onParseComplete?: (file: FileMetadata, parseResult: any) => void;
  onParseError?: (error: string) => void;
  className?: string;
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

export function FileParser({ 
  selectedFile: propSelectedFile, 
  onParseComplete,
  onParseError,
  className
}: FileParserProps) {
  const { isAuthenticated } = useAuth();
  const { state } = usePlatformState();
  const contentAPIManager = useContentAPIManager();
  
  const [selectedFileUuid, setSelectedFileUuid] = useState<string | null>(null);
  const [selectedFileFromSelector, setSelectedFileFromSelector] = useState<FileMetadata | null>(null);
  const [selectedCopybookFileId, setSelectedCopybookFileId] = useState<string>('');
  const [parseState, setParseState] = useState<ParseState>("idle");
  const [error, setError] = useState<string | null>(null);

  // Use FileSelector as single source of truth - show only uploaded files (not parsed yet)
  const selectedFile = selectedFileFromSelector || propSelectedFile;

  // Sync with propSelectedFile from parent
  useEffect(() => {
    if (propSelectedFile) {
      const fileId = propSelectedFile.uuid || propSelectedFile.file_id;
      if (fileId) {
        setSelectedFileUuid(fileId);
        setSelectedFileFromSelector(propSelectedFile);
      }
    }
  }, [propSelectedFile]);

  // Handle file selection from FileSelector
  const handleFileSelected = (fileId: string, file: FileMetadata | null) => {
    setSelectedFileUuid(fileId);
    setSelectedFileFromSelector(file);
    // Reset parse state when file changes
    setParseState("idle");
    setError(null);
    setSelectedCopybookFileId(''); // Reset copybook selection when file changes
  };

  // Check if file is binary and might need a copybook
  const isBinaryFile = useCallback((file: FileMetadata): boolean => {
    if (!file) return false;
    
    const extension = file.file_extension?.toLowerCase() || 
                     file.original_filename?.split('.').pop()?.toLowerCase() || 
                     file.ui_name?.split('.').pop()?.toLowerCase() ||
                     (file.file_type && file.file_type.toLowerCase() === 'bin' ? 'bin' : '') ||
                     '';
    
    const fileTypeLower = file.file_type?.toLowerCase() || '';
    const isBinaryType = fileTypeLower === 'bin' || fileTypeLower === 'binary';
    
    const binaryExtensions = ['.bin', '.dat', '.ebcdic', '.mainframe', '.cobol', 'bin', 'dat', 'ebcdic', 'mainframe', 'cobol'];
    const isBinaryExtension = binaryExtensions.some(ext => {
      const extClean = ext.startsWith('.') ? ext.substring(1) : ext;
      return extension === ext || extension === extClean || extension === `.${extClean}`;
    });
    
    return isBinaryType || isBinaryExtension;
  }, []);

  // Reset parse state when file changes
  useEffect(() => {
    if (selectedFileUuid && selectedFile) {
      setError(null);
      setParseState("idle");
      // Reset copybook selection when file changes (unless it's still a binary file)
      if (!isBinaryFile(selectedFile)) {
        setSelectedCopybookFileId('');
      }
    }
  }, [selectedFileUuid, selectedFile, isBinaryFile]);

  // Handle file parsing using semantic API
  const handleParse = useCallback(async () => {
    if (!selectedFile) {
      toast.error("No file selected");
      return;
    }

    // Validate file status - only parse files that are uploaded (not already parsed)
    if (selectedFile.status !== FileStatus.Uploaded) {
      toast.error("Cannot parse file with this status. Please select an uploaded file.");
      return;
    }

    // Check if file type supports parsing
    if (selectedFile.file_type === FileType.SopWorkflow) {
      toast.error("SOP/Workflow files are processed in the Operations pillar");
      return;
    }

    // Validate copybook for binary files
    if (isBinaryFile(selectedFile) && !selectedCopybookFileId) {
      toast.error('Copybook required', {
        description: 'Please select a copybook file to parse this binary file.'
      });
      return;
    }

    setParseState("parsing");
    setError(null);

    try {
      const fileId = selectedFile.file_id || selectedFile.uuid;
      const fileReference = selectedFile.metadata?.file_reference || `file:${state.session.tenantId}:${state.session.sessionId}:${fileId}`;
      const copybookReference = selectedCopybookFileId ? `copybook:${state.session.tenantId}:${state.session.sessionId}:${selectedCopybookFileId}` : undefined;
      
      // Parse file using new ContentAPIManager (Runtime-based intent submission)
      const result = await contentAPIManager.parseFile(
        fileId,
        fileReference,
        copybookReference
      );

      if (result.success && result.parsed_file_id) {
        const parsedFileId = result.parsed_file_id;
        
        if (parsedFileId) {
          // File was parsed and stored successfully
          setParseState("success");
          toast.success('File parsed successfully!', {
            description: `File "${selectedFile.ui_name || selectedFile.original_filename || fileId}" has been parsed and saved.`
          });
          
          // Dispatch custom event to notify ParsePreview and FileDashboard to refresh
          window.dispatchEvent(new CustomEvent('fileParsed', { 
            detail: { fileId, parsedFileId } 
          }));
          
          // Also dispatch a more general file update event
          window.dispatchEvent(new CustomEvent('fileUpdated', { 
            detail: { fileId, action: 'parsed' } 
          }));
          
          if (onParseComplete) {
            onParseComplete(selectedFile, result);
          }
        } else {
          // No parsed_file_id - storage failed
          setParseState("error");
          setError("Parsing completed but file storage failed. Please check backend logs.");
          toast.error('Parsing completed but storage failed', {
            description: 'The file was parsed but could not be stored. Please try again or check backend logs.'
          });
          
          if (onParseError) {
            onParseError("Parsing completed but file storage failed");
          }
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
  }, [selectedFile, selectedCopybookFileId, isBinaryFile, state.session, contentAPIManager, onParseComplete, onParseError]);

  if (!isAuthenticated) {
    return (
      <div className="p-6 text-center">
        <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Authentication Required</h3>
        <p className="text-gray-600">Please log in to parse files.</p>
      </div>
    );
  }

  return (
    <div className={`space-y-4 ${className || ''}`} data-testid="file-parser">
      {/* File Selection */}
      <div className="space-y-2">
        <label className="text-sm font-medium text-gray-700">Select File to Parse</label>
        <FileSelector
          value={selectedFileUuid || undefined}
          onValueChange={handleFileSelected}
          filterStatus={[FileStatus.Uploaded]} // Only show uploaded files (not parsed yet)
          placeholder="Choose a file to parse"
          dataTestId="parse-file-selector"
        />
        <p className="text-xs text-gray-500">
          Select an uploaded file to parse. Files that have already been parsed will not appear here.
        </p>
      </div>

      {/* Copybook Selection */}
      {selectedFile && isBinaryFile(selectedFile) && (
        <div className="space-y-2" data-testid="copybook-selector-wrapper">
          <label className="text-sm font-medium text-gray-700">
            Copybook File <span className="text-red-500">*</span>
          </label>
          <FileSelector
            value={selectedCopybookFileId || undefined}
            onValueChange={(fileId, file) => {
              setSelectedCopybookFileId(fileId);
            }}
            filterStatus={[FileStatus.Uploaded]}
            placeholder="Select a copybook file (.cpy, .cob, .cbl)"
            dataTestId="copybook-file-selector"
          />
          <p className="text-xs text-gray-500">
            Required: Select a copybook file to define the structure of the binary file.
          </p>
        </div>
      )}

      {/* Parse Status */}
      {parseState !== 'idle' && (
        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <ParseStatusIndicator parseState={parseState} />
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

      {/* Parse Button */}
      <Button
        onClick={handleParse}
        disabled={!selectedFile || parseState === 'parsing'}
        className="w-full"
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

      {/* Success Message */}
      {parseState === 'success' && (
        <div className="p-4 bg-green-50 rounded-lg border border-green-200">
          <div className="flex items-center space-x-2 text-green-800">
            <CheckCircle className="h-5 w-5" />
            <div>
              <p className="font-medium">File parsed successfully!</p>
              <p className="text-sm mt-1">The file has been parsed and saved. You can now preview it in the Preview section.</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

