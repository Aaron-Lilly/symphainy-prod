/**
 * InsightsFileSelector Component
 * 
 * File/metadata selection with "Use Extracted Metadata" option
 * Supports both file upload and content metadata from Content Pillar
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { FileText, Database, Loader2, Lock } from 'lucide-react';
import { getAvailableContentMetadata } from '@/lib/api/insights';
import { useContentAPIManager, ContentFile } from '@/shared/managers/ContentAPIManager';
import { usePlatformState } from '@/shared/state/PlatformStateProvider';
import { ContentType } from '@/shared/types/file';

interface InsightsFileSelectorProps {
  onSourceSelected: (sourceId: string, sourceType: 'file' | 'content_metadata', contentType: 'structured' | 'unstructured') => void;
  contentType: 'structured' | 'unstructured';
  selectedSourceId?: string;
  selectedSourceType?: 'file' | 'content_metadata';
  filterDataModel?: boolean;  // ⭐ NEW: Filter to show only Data Model files
}

export function InsightsFileSelector({ 
  onSourceSelected,
  contentType,
  selectedSourceId,
  selectedSourceType = 'file',
  filterDataModel = false  // ⭐ NEW: Default to false (show all files)
}: InsightsFileSelectorProps) {
  const { state } = usePlatformState();
  const contentAPIManager = useContentAPIManager();
  const [sourceMode, setSourceMode] = useState<'file' | 'content_metadata'>(selectedSourceType);
  const [files, setFiles] = useState<ContentFile[]>([]);
  const [metadata, setMetadata] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load files when switching to file mode
  useEffect(() => {
    if (sourceMode === 'file') {
      loadFiles();
    }
  }, [sourceMode]);

  // Load content metadata when switching to metadata mode
  useEffect(() => {
    if (sourceMode === 'content_metadata') {
      loadContentMetadata();
    }
  }, [sourceMode, contentType]);

  // Load files from Content Pillar using ContentAPIManager
  const loadFiles = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Get files from PlatformStateProvider (Content realm state)
      let contentFiles = state.realm.content.files || [];
      
      // ⭐ NEW: Filter by ContentType.DATA_MODEL if filterDataModel is true
      if (filterDataModel) {
        contentFiles = contentFiles.filter((file: any) => 
          file.content_type === ContentType.DATA_MODEL || 
          file.metadata?.content_type === ContentType.DATA_MODEL ||
          file.metadata?.parsing_type === 'data_model'
        );
      }
      
      // Convert to ContentFile format
      const formattedFiles: ContentFile[] = contentFiles.map((file: any) => ({
        id: file.id || file.uuid || file.file_id,
        name: file.name || file.filename || file.ui_name || 'Unknown',
        type: file.type || file.file_type || 'unknown',
        size: file.size || 0,
        uploadDate: file.uploadDate || file.created_at || new Date().toISOString(),
        status: file.status,
        metadata: file.metadata || file
      }));
      
      setFiles(formattedFiles);
    } catch (err) {
      console.error('Error loading files:', err);
      setError('Failed to load files from Content Pillar');
      setFiles([]);
    } finally {
      setLoading(false);
    }
  };

  const loadContentMetadata = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getAvailableContentMetadata(
        undefined, // tenant_id
        contentType, // content_type filter
        50, // limit
        0 // offset
      );
      
      if (response.success) {
        setMetadata(response.content_metadata_items || []);
      } else {
        setError('Failed to load content metadata');
      }
    } catch (err) {
      console.error('Error loading content metadata:', err);
      setError('Error loading content metadata');
      setMetadata([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSourceModeChange = (mode: 'file' | 'content_metadata') => {
    setSourceMode(mode);
    // Reset selection when changing modes
    onSourceSelected('', mode, contentType);
  };

  const handleSourceSelect = (sourceId: string) => {
    onSourceSelected(sourceId, sourceMode, contentType);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          Data Source Selection
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Source Mode Toggle */}
        <div>
          <label className="text-sm font-medium mb-2 block">Source Type</label>
          <div className="grid grid-cols-2 gap-2">
            <Button
              variant={sourceMode === 'file' ? 'default' : 'outline'}
              onClick={() => handleSourceModeChange('file')}
              className="justify-start"
            >
              <FileText className="h-4 w-4 mr-2" />
              Upload File
            </Button>
            <Button
              variant={sourceMode === 'content_metadata' ? 'default' : 'outline'}
              onClick={() => handleSourceModeChange('content_metadata')}
              className="justify-start"
            >
              <Database className="h-4 w-4 mr-2" />
              Use Metadata
              <Lock className="h-3 w-3 ml-auto text-green-600" />
            </Button>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            {sourceMode === 'file' 
              ? 'Upload a new file for analysis'
              : '🔒 Use extracted metadata (data stays secure in your environment)'}
          </p>
        </div>

        {/* File Selection */}
        {sourceMode === 'file' && (
          <div>
            <label className="text-sm font-medium mb-2 block">Select File</label>
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-5 w-5 animate-spin" />
                <span className="ml-2 text-sm">Loading files...</span>
              </div>
            ) : error ? (
              <div className="text-center py-8">
                <p className="text-sm text-red-600 mb-3">{error}</p>
                <Button size="sm" variant="outline" onClick={loadFiles}>
                  Retry
                </Button>
              </div>
            ) : files.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <FileText className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                <p className="text-sm">No files available</p>
                <p className="text-xs text-gray-400 mt-1">
                  Upload files in the Content Pillar first
                </p>
              </div>
            ) : (
              <>
                <Select
                  value={selectedSourceId || ''}
                  onValueChange={handleSourceSelect}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Choose a file to analyze (from Content Pillar)" />
                  </SelectTrigger>
                  <SelectContent>
                    {files.map((file) => (
                      <SelectItem key={file.id} value={file.id}>
                        <div className="flex flex-col">
                          <span className="font-medium">{file.name}</span>
                          <span className="text-xs text-gray-500">
                            {file.type} - {(file.size / 1024 / 1024).toFixed(2)} MB
                          </span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <p className="text-xs text-gray-500 mt-2">
                  {files.length} file{files.length !== 1 ? 's' : ''} available from Content Pillar
                </p>
              </>
            )}
          </div>
        )}

        {/* Metadata Selection */}
        {sourceMode === 'content_metadata' && (
          <div>
            <label className="text-sm font-medium mb-2 block">
              Select Content Metadata
            </label>
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-5 w-5 animate-spin" />
                <span className="ml-2 text-sm">Loading metadata...</span>
              </div>
            ) : error ? (
              <div className="text-center py-8">
                <p className="text-sm text-red-600 mb-3">{error}</p>
                <Button size="sm" variant="outline" onClick={loadContentMetadata}>
                  Retry
                </Button>
              </div>
            ) : metadata.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Database className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                <p className="text-sm">No content metadata available</p>
                <p className="text-xs text-gray-400 mt-1">
                  Process files in the Content Pillar to extract metadata first
                </p>
              </div>
            ) : (
              <>
                <Select
                  value={selectedSourceId || ''}
                  onValueChange={handleSourceSelect}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Choose extracted metadata to analyze" />
                  </SelectTrigger>
                  <SelectContent>
                    {metadata.map((item) => (
                      <SelectItem key={item.content_metadata_id} value={item.content_metadata_id}>
                        <div className="flex flex-col">
                          <span className="font-medium">
                            {item.file_metadata?.file_name || 'Unknown File'}
                          </span>
                          <span className="text-xs text-gray-500">
                            {item.content_metadata?.title || 'No title'} • 
                            {item.semantic_metadata?.topics?.slice(0, 2).join(', ') || 'No topics'}
                          </span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <p className="text-xs text-gray-500 mt-2">
                  Metadata extracted: {metadata.length} item{metadata.length !== 1 ? 's' : ''} available
                </p>
              </>
            )}
          </div>
        )}

        {/* Selected Source Info */}
        {selectedSourceId && (
          <div className="bg-blue-50 p-3 rounded-lg border border-blue-200">
            <p className="text-xs font-medium text-blue-900">
              ✓ Source selected: {sourceMode === 'file' ? 'File' : 'Content Metadata'}
            </p>
            <p className="text-xs text-blue-700 mt-1">
              ID: {selectedSourceId.substring(0, 20)}...
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

