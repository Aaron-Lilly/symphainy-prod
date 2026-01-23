/**
 * FileDashboard - Using Semantic APIs via ContentAPIManager
 * 
 * Complete FileDashboard component that uses semantic APIs for file management.
 * Displays files in a table format with statistics, deletion, and expandable view.
 */

"use client";

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  File, 
  Trash2, 
  Loader2, 
  AlertCircle,
  CheckCircle,
  Clock,
  Database,
  RefreshCw,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { useAuth } from '@/shared/auth/AuthProvider';
import { usePlatformState } from '@/shared/state/PlatformStateProvider';
import { useContentAPIManager } from '@/shared/managers/ContentAPIManager';
import { toast } from 'sonner';
import { FileMetadata, FileStatus, ContentType } from '@/shared/types/file';

interface FileStats {
  total: number;
  uploaded: number;
  parsed: number;
  embedded?: number; // New field for embedding files count
  validated: number;
  rejected: number;
  deleted: number;
}

interface FileDashboardNewProps {
  onFileSelected?: (file: FileMetadata) => void;
  onFileParsed?: (file: FileMetadata, parseResult: any) => void;
  onFileDeleted?: (fileId: string) => void;
  onEnhancedProcessing?: (file: FileMetadata) => void;
  className?: string;
}

export function FileDashboard({ 
  onFileSelected, 
  onFileParsed, 
  onFileDeleted,
  onEnhancedProcessing,
  className
}: FileDashboardNewProps) {
  const { isAuthenticated, user } = useAuth();
  const { state, setRealmState } = usePlatformState();
  const contentAPIManager = useContentAPIManager();
  
  const [files, setFiles] = useState<FileMetadata[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [processingFiles, setProcessingFiles] = useState<Set<string>>(new Set());
  const [showAll, setShowAll] = useState(false);
  const [deleting, setDeleting] = useState<string | null>(null);

  // Initialize from realm state first (before loading from API)
  useEffect(() => {
    const contentFiles = state.realm.content.files;
    if (contentFiles && Array.isArray(contentFiles) && contentFiles.length > 0) {
      setFiles(contentFiles);
      setShowAll(contentFiles.length <= 5);
    }
  }, [state.realm.content.files]);

  // Load files from backend using semantic API
  const loadFiles = useCallback(async () => {
    if (!isAuthenticated) return;

    setLoading(true);
    setError(null);

    try {
      // Load files using new ContentAPIManager (Runtime-based)
      const contentFiles = await contentAPIManager.listFiles();
      
      // Map ContentFile to FileMetadata format
      // Map status string to FileStatus enum (same logic as FileSelector)
      const mapStatus = (statusStr?: string): FileStatus => {
        if (!statusStr) return FileStatus.Uploaded;
        const statusLower = statusStr.toLowerCase();
        if (statusLower === 'parsed') return FileStatus.Parsed;
        if (statusLower === 'validated') return FileStatus.Validated;
        if (statusLower === 'embedded') return FileStatus.Validated; // Map "embedded" to Validated for UI
        if (statusLower === 'parsing') return FileStatus.Parsing;
        return FileStatus.Uploaded; // Default to Uploaded
      };

      const mappedFiles: FileMetadata[] = contentFiles.map((cf) => ({
        uuid: cf.id,
        file_id: cf.id,
        ui_name: cf.name,
        original_filename: cf.name,
        original_path: cf.metadata?.original_path || '',
        file_type: cf.type as any,
        mime_type: cf.metadata?.mime_type || '',
        file_size: cf.size,
        status: mapStatus(cf.status), // Use actual status from API
        metadata: cf.metadata || {},
        created_at: cf.uploadDate,
        updated_at: cf.uploadDate,
        upload_timestamp: cf.uploadDate,
        deleted: false,
        // NEW: Materialization fields
        boundary_contract_id: cf.boundary_contract_id || cf.metadata?.boundary_contract_id,
        materialization_pending: cf.materialization_pending !== false && (cf.status === 'pending' || cf.metadata?.materialization_pending === true),
      }));
      
      // Sort by creation date (newest first)
      mappedFiles.sort((a, b) => {
        const dateA = new Date(a.created_at || 0).getTime();
        const dateB = new Date(b.created_at || 0).getTime();
        return dateB - dateA;
      });
      
      setFiles(mappedFiles);
      setShowAll(mappedFiles.length <= 5);
      
      // Update realm state (Content realm)
      setRealmState('content', 'files', mappedFiles);
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load files';
      setError(errorMessage);
      toast.error('Failed to load files', {
        description: errorMessage
      });
      
      // Fallback to platform state if available
      // Note: Files are now managed via PlatformStateProvider
      // This fallback is for legacy compatibility
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated, contentAPIManager, state.realm.content.files, setRealmState]);

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
  }, [isAuthenticated, loadFiles]);

  // Listen for file update events (e.g., when a file is parsed)
  useEffect(() => {
    const handleFileUpdated = () => {
      console.log('[FileDashboard] File updated event received, refreshing file list...');
      loadFiles();
    };

    window.addEventListener('fileUpdated', handleFileUpdated);
    window.addEventListener('fileParsed', handleFileUpdated);

    return () => {
      window.removeEventListener('fileUpdated', handleFileUpdated);
      window.removeEventListener('fileParsed', handleFileUpdated);
    };
  }, [loadFiles]);

  // Delete file using semantic API
  const handleDeleteFile = useCallback(async (file: FileMetadata) => {
    if (!confirm(`Are you sure you want to delete "${file.ui_name || file.original_filename || file.uuid}"?`)) {
      return;
    }

    const fileId = file.file_id || file.uuid;
    setDeleting(fileId);
    setProcessingFiles(prev => new Set(prev).add(fileId));
    
    try {
      // Delete file using new ContentAPIManager (Runtime-based)
      // Note: deleteFile method may need to be added to new ContentAPIManager
      // For now, we'll use the existing endpoint pattern
      const fileType = file.metadata?.file_type || 
                       (file.status === FileStatus.Parsed ? 'parsed' : 
                        (file.status === FileStatus.Validated && file.metadata?.parsed_file_id ? 'embedded' : 'original'));
      
      // TODO: Add deleteFile method to new ContentAPIManager
      // For MVP, we'll use direct API call or add to ContentAPIManager
      const { getApiEndpointUrl } = require('@/shared/config/api-config');
      const deleteURL = getApiEndpointUrl(`/api/v1/content-pillar/delete-file/${fileId}${fileType ? `?file_type=${fileType}` : ''}`);
      
      const response = await fetch(deleteURL, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
      });
      
      const success = response.ok;

      if (success) {
        const updatedFiles = files.filter(f => (f.file_id || f.uuid) !== fileId);
        setFiles(updatedFiles);
        
        // Update realm state (Content realm)
        setRealmState('content', 'files', updatedFiles);
        
        toast.success('File deleted successfully!', {
          description: `File "${file.ui_name || file.original_filename || file.uuid}" has been deleted.`
        });
        
        if (onFileDeleted) {
          onFileDeleted(fileId);
        }
      } else {
        toast.error('Delete failed', {
          description: 'An error occurred during deletion'
        });
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Delete failed';
      toast.error('Delete failed', {
        description: errorMessage
      });
    } finally {
      setDeleting(null);
      setProcessingFiles(prev => {
        const newSet = new Set(prev);
        newSet.delete(fileId);
        return newSet;
      });
    }
  }, [onFileDeleted, contentAPIManager, files, setRealmState]);

  // Format file size
  const formatFileSize = (bytes: number): string => {
    if (!bytes || bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Format timestamp
  const formatTimestamp = (timestamp: string): string => {
    if (!timestamp) return 'N/A';
    return new Date(timestamp).toLocaleString();
  };

  // Get status badge
  const getStatusBadge = (file: FileMetadata) => {
    const status = file.status || FileStatus.Uploaded;
    const isProcessing = processingFiles.has(file.file_id || file.uuid);
    const isPending = file.materialization_pending === true;
    
    if (isProcessing) {
      return (
        <Badge variant="outline" className="text-xs">
          <Loader2 className="h-3 w-3 mr-1 animate-spin" />
          Processing
        </Badge>
      );
    }
    
    // Show "Pending" badge if materialization is pending
    if (isPending) {
      return (
        <Badge variant="outline" className="text-xs bg-amber-50 text-amber-700 border-amber-200">
          <Clock className="h-3 w-3 mr-1" />
          Pending Save
        </Badge>
      );
    }
    
    switch (status) {
      case FileStatus.Parsed:
        return <Badge variant="outline" className="text-xs bg-green-50 text-green-700 border-green-200">Parsed</Badge>;
      case FileStatus.Validated:
        return <Badge variant="outline" className="text-xs bg-purple-50 text-purple-700 border-purple-200">Validated</Badge>;
      case FileStatus.Parsing:
        return <Badge variant="outline" className="text-xs bg-yellow-50 text-yellow-700 border-yellow-200">Parsing</Badge>;
      case FileStatus.Uploaded:
      default:
        return <Badge variant="outline" className="text-xs bg-blue-50 text-blue-700 border-blue-200">
          <CheckCircle className="h-3 w-3 mr-1" />
          Saved
        </Badge>;
    }
  };

  // Fetch file statistics from backend (includes uploaded, parsed, embedded counts)
  const [stats, setStats] = useState<FileStats>({
    total: 0,
    uploaded: 0,
    parsed: 0,
    validated: 0,
    rejected: 0,
    deleted: 0,
  });
  const [loadingStats, setLoadingStats] = useState(false);

  useEffect(() => {
    const fetchStats = async () => {
      if (!state.session.sessionId) return;
      
      setLoadingStats(true);
      try {
        // Calculate statistics from files array
        const parsedFiles = state.realm.content.parsedFiles || [];
        setStats({
          total: files.length,
          uploaded: files.filter(f => f.status === FileStatus.Uploaded || f.status === FileStatus.Parsed || f.status === FileStatus.Validated).length,
          parsed: parsedFiles.length,
          embedded: parsedFiles.filter(f => (f as any).embeddings && (f as any).embeddings.length > 0).length,
          validated: files.filter(f => f.status === FileStatus.Validated).length,
          rejected: files.filter(f => f.rejection_reason && f.rejection_reason.length > 0).length,
          deleted: files.filter(f => f.deleted).length,
        });
      } catch (error) {
        console.error('Failed to fetch file statistics:', error);
        // Fallback to calculating from files array
        setStats({
          total: files.length,
          uploaded: files.filter(f => f.status === FileStatus.Uploaded).length,
          parsed: files.filter(f => f.status === FileStatus.Parsed).length,
          validated: files.filter(f => f.status === FileStatus.Validated).length,
          rejected: files.filter(f => f.rejection_reason && f.rejection_reason.length > 0).length,
          deleted: files.filter(f => f.deleted).length,
        });
      } finally {
        setLoadingStats(false);
      }
    };

    fetchStats();
  }, [state.session.sessionId, files.length]); // Re-fetch when session or file count changes
  // Show 5 most recent files by default, or all if showAll is true
  const displayFiles = showAll ? files : files.slice(0, 5);

  if (!isAuthenticated) {
    return (
      <div className="p-6 text-center">
        <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Authentication Required</h3>
        <p className="text-gray-600">Please log in to view your files.</p>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className || ''}`} data-testid="content-pillar-file-dashboard">
      {/* Header with Stats and Refresh */}
      <div className="flex justify-between items-center">
        {/* File Stats Card */}
        <Card className="flex-1 max-w-md">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center space-x-2 text-sm">
              <Database className="h-4 w-4" />
              <span>File Statistics</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-4 gap-2 text-xs">
              <div>
                <div className="font-semibold text-gray-900">{loadingStats ? '...' : stats.total}</div>
                <div className="text-gray-500">Total</div>
              </div>
              <div>
                <div className="font-semibold text-blue-600">{loadingStats ? '...' : stats.uploaded}</div>
                <div className="text-gray-500">Uploaded</div>
              </div>
              <div>
                <div className="font-semibold text-green-600">{loadingStats ? '...' : stats.parsed}</div>
                <div className="text-gray-500">Parsed</div>
              </div>
              <div>
                <div className="font-semibold text-indigo-600">{loadingStats ? '...' : (stats.embedded || 0)}</div>
                <div className="text-gray-500">Embedded</div>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Button 
          onClick={loadFiles} 
          disabled={loading}
          variant="outline"
          size="sm"
          data-testid="refresh-files-button"
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="flex items-center space-x-2 p-3 bg-red-50 border border-red-200 rounded-md">
          <AlertCircle className="h-4 w-4 text-red-500" />
          <span className="text-sm text-red-700">{error}</span>
        </div>
      )}

      {/* Files Table */}
      {loading && files.length === 0 ? (
        <div className="flex items-center justify-center p-8">
          <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
          <span className="ml-2 text-gray-600">Loading files...</span>
        </div>
      ) : files.length === 0 ? (
        <div className="text-center p-8">
          <File className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No files uploaded</h3>
          <p className="text-gray-600">Upload your first file to get started.</p>
        </div>
      ) : (
        <Card>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">File Name</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Type</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Size</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Uploaded</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Status</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-700 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {displayFiles.map((file) => {
                    const fileId = file.file_id || file.uuid;
                    const isDeleting = deleting === fileId;
                    const isProcessing = processingFiles.has(fileId);
                    
                    return (
                      <tr 
                        key={fileId} 
                        className="hover:bg-gray-50 transition-colors"
                        data-testid={`file-list-item-${fileId}`}
                      >
                        <td className="px-4 py-3 whitespace-nowrap">
                          <div className="flex items-center">
                            <File className="h-4 w-4 text-gray-400 mr-2" />
                            <div className="flex flex-col">
                              <div className="flex items-center gap-2">
                                <span className="text-sm font-medium text-gray-900">
                                  {file.ui_name || file.original_filename || file.uuid}
                                </span>
                                {file.content_type === ContentType.DATA_MODEL && (
                                  <Badge variant="outline" className="text-xs bg-purple-50 text-purple-700 border-purple-200">
                                    📊 Data Model
                                  </Badge>
                                )}
                              </div>
                              {file.original_filename && file.original_filename !== file.ui_name && (
                                <span className="text-xs text-gray-500">
                                  {file.original_filename}
                                </span>
                              )}
                            </div>
                          </div>
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <div className="flex flex-col">
                            <span className="text-sm text-gray-900">
                              {file.file_type?.toUpperCase() || 'N/A'}
                            </span>
                            {file.mime_type && (
                              <span className="text-xs text-gray-500">
                                {file.mime_type.split('/')[1]}
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                          {file.file_size ? formatFileSize(file.file_size) : 'N/A'}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                          {file.created_at ? formatTimestamp(file.created_at) : 'N/A'}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          {getStatusBadge(file)}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-right">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleDeleteFile(file)}
                            disabled={isProcessing || isDeleting}
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                            data-testid={`delete-file-${fileId}`}
                            aria-label={`Delete file ${file.ui_name || file.uuid}`}
                          >
                            {isDeleting ? (
                              <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                              <Trash2 className="h-4 w-4" />
                            )}
                          </Button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
      
      {/* Show All / Show Less Button */}
      {files.length > 5 && (
        <div className="text-center">
          <Button 
            variant="outline" 
            onClick={() => setShowAll(!showAll)}
            data-testid="toggle-show-all-files"
            className="flex items-center space-x-2"
          >
            {showAll ? (
              <>
                <ChevronUp className="h-4 w-4" />
                <span>Show Less</span>
              </>
            ) : (
              <>
                <ChevronDown className="h-4 w-4" />
                <span>Show All ({files.length} files)</span>
              </>
            )}
          </Button>
        </div>
      )}

      {/* User Info */}
      <div className="text-xs text-gray-500 text-center">
        Files for: {user?.name} ({user?.email})
      </div>
    </div>
  );
}
