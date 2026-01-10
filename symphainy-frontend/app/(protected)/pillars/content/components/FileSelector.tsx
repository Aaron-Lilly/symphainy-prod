/**
 * FileSelector - Reusable file selection component
 * 
 * Single source of truth for file selection across the Content Pillar.
 * Uses the same file loading logic as FileDashboard with filtering capabilities.
 */

"use client";

import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useAuth } from '@/shared/agui/AuthProvider';
import { useGlobalSession } from '@/shared/agui/GlobalSessionProvider';
import { ContentAPIManager } from '@/shared/managers/ContentAPIManager';
import { FileMetadata, FileStatus } from '@/shared/types/file';

interface FileSelectorProps {
  value?: string; // Selected file ID
  onValueChange?: (fileId: string, file: FileMetadata | null) => void;
  filterStatus?: FileStatus[]; // Filter by status (e.g., [FileStatus.Uploaded])
  showOnlyParsed?: boolean; // Show only parsed files
  placeholder?: string;
  className?: string;
  disabled?: boolean;
  dataTestId?: string;
}

export function FileSelector({
  value,
  onValueChange,
  filterStatus,
  showOnlyParsed = false,
  placeholder = "Choose a file",
  className,
  disabled = false,
  dataTestId = "file-selector",
}: FileSelectorProps) {
  const { isAuthenticated } = useAuth();
  const { guideSessionToken, getPillarState, setPillarState } = useGlobalSession();
  
  const [files, setFiles] = useState<FileMetadata[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load files from backend using semantic API (same logic as FileDashboard)
  const loadFiles = useCallback(async () => {
    if (!isAuthenticated) return;

    setLoading(true);
    setError(null);

    try {
      const sessionToken = guideSessionToken || 'debug-token';
      const apiManager = new ContentAPIManager(sessionToken);
      
      const contentFiles = await apiManager.listFiles();
      
      // Map ContentFile to FileMetadata format
      // Map status string to FileStatus enum
      const mapStatus = (statusStr?: string): FileStatus => {
        if (!statusStr) return FileStatus.Uploaded;
        const statusLower = statusStr.toLowerCase();
        if (statusLower === 'parsed') return FileStatus.Parsed;
        if (statusLower === 'validated') return FileStatus.Validated;
        if (statusLower === 'parsing') return FileStatus.Parsing;
        return FileStatus.Uploaded; // Default to Uploaded
      };

      let mappedFiles: FileMetadata[] = contentFiles.map((cf) => ({
        uuid: cf.id,
        file_id: cf.id,
        ui_name: cf.name,
        original_filename: cf.name,
        file_type: cf.type as any,
        mime_type: cf.metadata?.mime_type || '',
        file_size: cf.size,
        status: mapStatus(cf.status), // Use actual status from API
        metadata: cf.metadata || {},
        created_at: cf.uploadDate,
        updated_at: cf.uploadDate,
        upload_timestamp: cf.uploadDate,
        original_path: cf.id, // Use ID as path for now
        deleted: false,
      }));
      
      // Apply filters
      if (filterStatus && filterStatus.length > 0) {
        mappedFiles = mappedFiles.filter(file => 
          filterStatus.includes(file.status)
        );
      }
      
      if (showOnlyParsed) {
        // Show only files that have been parsed (have parsed_path or status is Parsed)
        mappedFiles = mappedFiles.filter(file => 
          file.status === FileStatus.Parsed || 
          file.parsed_path || 
          (file.metadata?.parsed === true)
        );
      }
      
      // Sort by creation date (newest first)
      mappedFiles.sort((a, b) => {
        const dateA = new Date(a.created_at || 0).getTime();
        const dateB = new Date(b.created_at || 0).getTime();
        return dateB - dateA;
      });
      
      setFiles(mappedFiles);
      
      // Update global state for other components to use
      await setPillarState('data', { files: mappedFiles });
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load files';
      setError(errorMessage);
      console.error('FileSelector: Failed to load files', errorMessage);
      
      // Fallback to global state if available
      const dataState = getPillarState('data');
      if (dataState?.files) {
        let fallbackFiles = dataState.files;
        
        // Apply same filters to fallback
        if (filterStatus && filterStatus.length > 0) {
          fallbackFiles = fallbackFiles.filter((file: FileMetadata) => 
            filterStatus.includes(file.status)
          );
        }
        
        if (showOnlyParsed) {
          fallbackFiles = fallbackFiles.filter((file: FileMetadata) => 
            file.status === FileStatus.Parsed || 
            file.parsed_path || 
            (file.metadata?.parsed === true)
          );
        }
        
        setFiles(fallbackFiles);
      }
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated, guideSessionToken, filterStatus, showOnlyParsed, getPillarState, setPillarState]);

  // Load files ONLY once on component mount (when authenticated)
  // Use ref to track if we've already loaded to prevent multiple calls
  const hasLoadedRef = useRef(false);
  useEffect(() => {
    // Only load if authenticated AND we haven't loaded yet
    if (isAuthenticated && !hasLoadedRef.current) {
      hasLoadedRef.current = true;
      loadFiles();
    }
    // Reset ref if user logs out (so it can load again on next login)
    if (!isAuthenticated) {
      hasLoadedRef.current = false;
    }
  }, [isAuthenticated]); // Only depend on isAuthenticated, not loadFiles

  // Initialize from global state
  useEffect(() => {
    const dataState = getPillarState('data');
    if (dataState?.files && Array.isArray(dataState.files) && dataState.files.length > 0) {
      let stateFiles = dataState.files;
      
      // Apply filters
      if (filterStatus && filterStatus.length > 0) {
        stateFiles = stateFiles.filter((file: FileMetadata) => 
          filterStatus.includes(file.status)
        );
      }
      
      if (showOnlyParsed) {
        stateFiles = stateFiles.filter((file: FileMetadata) => 
          file.status === FileStatus.Parsed || 
          file.parsed_path || 
          (file.metadata?.parsed === true)
        );
      }
      
      setFiles(stateFiles);
    }
  }, [getPillarState, filterStatus, showOnlyParsed]);

  // Handle file selection
  const handleValueChange = (fileId: string) => {
    const selectedFile = files.find(f => f.file_id === fileId || f.uuid === fileId) || null;
    onValueChange?.(fileId, selectedFile);
  };

  return (
    <div data-testid={dataTestId}>
      <Select
        value={value || ""}
        onValueChange={handleValueChange}
        disabled={disabled || loading}
      >
        <SelectTrigger className={className}>
          <SelectValue placeholder={loading ? "Loading files..." : placeholder} />
        </SelectTrigger>
      <SelectContent>
        {error ? (
          <SelectItem value="error" disabled>
            Error loading files
          </SelectItem>
        ) : files.length === 0 ? (
          <SelectItem value="no-files" disabled>
            No files available
          </SelectItem>
        ) : (
          files.map((file) => {
            const fileId = file.file_id || file.uuid;
            return (
              <SelectItem key={fileId} value={fileId}>
                <div className="flex flex-col">
                  <span className="font-medium">{file.ui_name || file.original_filename || fileId}</span>
                  <span className="text-xs text-gray-500">
                    {file.file_type?.toUpperCase() || 'FILE'} • {file.file_size ? `${(file.file_size / 1024 / 1024).toFixed(1)} MB` : ''}
                  </span>
                </div>
              </SelectItem>
            );
          })
        )}
      </SelectContent>
    </Select>
    </div>
  );
}

