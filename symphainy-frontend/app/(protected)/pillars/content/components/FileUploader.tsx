/**
 * FileUploader - Using Semantic APIs via ContentAPIManager
 * 
 * Complete FileUploader component that uses semantic APIs for file upload.
 * Supports all file types including Mainframe files with copybook support.
 */

"use client";

import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { UploadCloud, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { useAuth } from '@/shared/agui/AuthProvider';
import { useGlobalSession } from '@/shared/agui/GlobalSessionProvider';
import { ContentAPIManager } from '@/shared/managers/ContentAPIManager';
import { ContentType, FileTypeCategory, FILE_TYPE_CONFIGS, FileType } from '@/shared/types/file';
import { toast } from 'sonner';

// Content Type options (primary selection)
const CONTENT_TYPE_OPTIONS = [
  {
    type: ContentType.STRUCTURED,
    label: 'Structured Data',
    description: 'Tabular data, spreadsheets, binary files with copybooks, machine-readable formats'
  },
  {
    type: ContentType.UNSTRUCTURED,
    label: 'Unstructured Documents',
    description: 'Text documents, PDFs, images, rich text formats, SOP/Workflow files'
  },
  {
    type: ContentType.HYBRID,
    label: 'Hybrid Content',
    description: 'Documents with embedded structured data, complex formats requiring special handling'
  },
  {
    type: ContentType.WORKFLOW_SOP,
    label: 'Workflow & SOP Documentation',
    description: 'Workflow diagrams and Standard Operating Procedure documents (processed in Operations Pillar)'
  }
];

interface UploadState {
  step: 'content_type' | 'file_category' | 'upload';
  contentType: ContentType | null;
  fileCategory: FileTypeCategory | null;
  selectedFile: File | null;
  copybookFile: File | null;
  uploading: boolean;
  error: string | null;
  success: boolean;
  processingStatus: string | null;
  workflowId: string | null;
}

interface FileUploaderProps {
  onFileUploaded?: (fileId: string) => void;
  onUploadError?: (error: string) => void;
  className?: string;
}

export function FileUploader({ 
  onFileUploaded, 
  onUploadError,
  className 
}: FileUploaderProps = {}) {
  const { isAuthenticated, user } = useAuth();
  const { guideSessionToken, getPillarState, setPillarState } = useGlobalSession();
  
  
  const [uploadState, setUploadState] = useState<UploadState>({
    step: 'content_type',
    contentType: null,
    fileCategory: null,
    selectedFile: null,
    copybookFile: null,
    uploading: false,
    error: null,
    success: false,
    processingStatus: null,
    workflowId: null,
  });

  // Get available file categories for selected content type
  const getAvailableFileCategories = useCallback((contentType: ContentType | null) => {
    if (!contentType) return [];
    return FILE_TYPE_CONFIGS.filter(config => config.contentType === contentType);
  }, []);

  // Get selected file type config
  const selectedFileTypeConfig = useCallback(() => {
    if (!uploadState.contentType || !uploadState.fileCategory) return null;
    return FILE_TYPE_CONFIGS.find(
      config => config.contentType === uploadState.contentType && config.category === uploadState.fileCategory
    );
  }, [uploadState.contentType, uploadState.fileCategory]);

  // Get accept object for dropzone based on file type config
  const getAcceptObject = useCallback(() => {
    const config = selectedFileTypeConfig();
    if (!config) return undefined;
    
    // Build MIME type map from config
    const acceptObject: Record<string, string[]> = {};
    config.mimeTypes.forEach((mimeType, index) => {
      const extension = config.extensions[index]?.replace('.', '');
      if (extension) {
        if (!acceptObject[mimeType]) {
          acceptObject[mimeType] = [];
        }
        acceptObject[mimeType].push(`.${extension}`);
      }
    });
    
    return acceptObject;
  }, [selectedFileTypeConfig]);

  // Handle file drop
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      setUploadState(prev => ({ 
        ...prev, 
        selectedFile: file,
        error: null,
        success: false
      }));
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: getAcceptObject(),
    multiple: false,
    disabled: uploadState.step !== 'upload' || !isAuthenticated,
  });

  // Handle content type selection
  const handleContentTypeChange = useCallback((value: string) => {
    const contentType = value as ContentType;
    setUploadState(prev => ({
      ...prev,
      step: 'file_category',
      contentType,
      fileCategory: null,
      selectedFile: null,
      copybookFile: null,
      error: null,
      success: false,
    }));
  }, []);

  // Handle file category selection
  const handleFileCategoryChange = useCallback((value: string) => {
    const fileCategory = value as FileTypeCategory;
    setUploadState(prev => ({
      ...prev,
      step: 'upload',
      fileCategory,
      selectedFile: null,
      copybookFile: null,
      error: null,
      success: false,
    }));
  }, []);

  // Handle back button
  const handleBack = useCallback(() => {
    setUploadState(prev => {
      if (prev.step === 'file_category') {
        return {
          ...prev,
          step: 'content_type',
          contentType: null,
          fileCategory: null,
        };
      } else if (prev.step === 'upload') {
        return {
          ...prev,
          step: 'file_category',
          fileCategory: null,
          selectedFile: null,
          copybookFile: null,
        };
      }
      return prev;
    });
  }, []);

  // Handle copybook file selection (for Mainframe/Binary files)
  const handleCopybookChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setUploadState(prev => ({ ...prev, copybookFile: e.target.files![0] }));
    }
  }, []);

  // Handle file upload
  const handleUpload = useCallback(async () => {
    const config = selectedFileTypeConfig();
    if (!uploadState.selectedFile || !config || !isAuthenticated) {
      setUploadState(prev => ({ ...prev, error: 'Please select a file type and file' }));
      return;
    }

    // Validate copybook file for Binary files
    if (config.requiresCopybook && !uploadState.copybookFile) {
      setUploadState(prev => ({ ...prev, error: 'Please upload a copybook file for Mainframe data' }));
      return;
    }

    setUploadState(prev => ({ ...prev, uploading: true, error: null, processingStatus: 'Uploading file...' }));

    try {
      const sessionToken = guideSessionToken || 'debug-token';
      const apiManager = new ContentAPIManager(sessionToken);
      
      // Upload file using semantic API
      const result = await apiManager.uploadFile(
        uploadState.selectedFile,
        uploadState.copybookFile || undefined,
        uploadState.contentType || undefined,  // ⭐ Pass content_type
        uploadState.fileCategory || undefined  // ⭐ Pass file_type_category
      );

      if (result.success && result.file) {
        setUploadState(prev => ({ 
          ...prev, 
          uploading: false, 
          success: true,
          error: null,
          processingStatus: 'File uploaded successfully! Processing started...',
          workflowId: result.file?.id || null
        }));
        
        // Update pillar states
        const config = selectedFileTypeConfig();
        const currentDataState = getPillarState('data') || { files: [] };
        const uploadedFile = {
          uuid: result.file.id,
          ui_name: result.file.name,
          file_type: config?.category || 'unknown',
          content_type: uploadState.contentType || undefined,
          file_type_category: uploadState.fileCategory || undefined,
          mime_type: uploadState.selectedFile.type,
          original_path: result.file.name,
          status: 'uploaded',
          metadata: {
            ...(result.file.metadata || {}),
            content_type: uploadState.contentType,
            file_type_category: uploadState.fileCategory,
            processing_pillar: config?.processingPillar,
          },
          created_at: result.file.uploadDate,
          updated_at: result.file.uploadDate,
        };
        
        const updatedFiles = [...(currentDataState.files || []), uploadedFile];
        await setPillarState('data', { ...currentDataState, files: updatedFiles });
        
        // Add to parsing queue
        const currentParsingState = getPillarState('parsing') || { files: [] };
        const updatedParsingFiles = [...(currentParsingState.files || []), uploadedFile];
        await setPillarState('parsing', { ...currentParsingState, files: updatedParsingFiles });
        
        // If SOP/Workflow (processing_pillar is operations_pillar), also add to operations pillar
        if (config?.processingPillar === 'operations_pillar') {
          const currentOperationsState = getPillarState('operations') || { files: [] };
          const updatedOperationFiles = [...(currentOperationsState.files || []), uploadedFile];
          await setPillarState('operations', { ...currentOperationsState, files: updatedOperationFiles });
          
          toast.info('File uploaded to Content Pillar', {
            description: 'This file will be parsed in Operations Pillar'
          });
        }
        
        toast.success('File uploaded successfully!', {
          description: `File "${uploadState.selectedFile.name}" has been uploaded and is ready for processing.`
        });
        
        // Call callback
        if (onFileUploaded) {
          onFileUploaded(result.file.id);
        }
        
        // Reset form after successful upload
        setTimeout(() => {
          setUploadState({
            step: 'content_type',
            contentType: null,
            fileCategory: null,
            selectedFile: null,
            copybookFile: null,
            uploading: false,
            error: null,
            success: false,
            processingStatus: null,
            workflowId: null,
          });
        }, 3000);
        
      } else {
        const errorMsg = result.error || 'Upload failed';
        setUploadState(prev => ({ 
          ...prev, 
          uploading: false, 
          error: errorMsg,
          processingStatus: null
        }));
        
        toast.error('Upload failed', {
          description: errorMsg
        });
        
        if (onUploadError) {
          onUploadError(errorMsg);
        }
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Upload failed';
      setUploadState(prev => ({ 
        ...prev, 
        uploading: false, 
        error: errorMessage,
        processingStatus: null
      }));
      
      toast.error('Upload failed', {
        description: errorMessage
      });
      
      if (onUploadError) {
        onUploadError(errorMessage);
      }
    }
  }, [uploadState, isAuthenticated, guideSessionToken, getPillarState, setPillarState, onFileUploaded, onUploadError, selectedFileTypeConfig]);

  // Format file size
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (!isAuthenticated) {
    return (
      <div className="p-6 text-center">
        <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Authentication Required</h3>
        <p className="text-gray-600">Please log in to upload files.</p>
      </div>
    );
  }

  const config = selectedFileTypeConfig();
  const availableCategories = getAvailableFileCategories(uploadState.contentType);

  return (
    <div className={`space-y-4 ${className || ''}`} data-testid="content-pillar-file-upload-area">
      {/* Step 1: Content Type Selection */}
      {uploadState.step === 'content_type' && (
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">Content Type</label>
          <Select 
            onValueChange={handleContentTypeChange} 
            value={uploadState.contentType || ''}
          >
            <SelectTrigger data-testid="content-type-selector">
              <SelectValue placeholder="Select content type" />
            </SelectTrigger>
            <SelectContent>
              {CONTENT_TYPE_OPTIONS.map((option) => (
                <SelectItem key={option.type} value={option.type}>
                  <div>
                    <div className="font-medium">{option.label}</div>
                    <div className="text-xs text-gray-500">{option.description}</div>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      )}

      {/* Step 2: File Category Selection */}
      {uploadState.step === 'file_category' && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-gray-700">File Category</label>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={handleBack}
              className="text-xs"
            >
              ← Back
            </Button>
          </div>
          <Select 
            onValueChange={handleFileCategoryChange} 
            value={uploadState.fileCategory || ''}
          >
            <SelectTrigger data-testid="file-category-selector">
              <SelectValue placeholder="Select file category" />
            </SelectTrigger>
            <SelectContent>
              {availableCategories.map((category) => (
                <SelectItem key={category.category} value={category.category}>
                  <div>
                    <div className="font-medium flex items-center gap-2">
                      {category.icon && <span>{category.icon}</span>}
                      {category.label}
                    </div>
                    <div className="text-xs text-gray-500">
                      {category.extensions.join(', ')}
                    </div>
                    {category.description && (
                      <div className="text-xs text-gray-400 mt-1">{category.description}</div>
                    )}
                    {category.requiresCopybook && (
                      <div className="text-xs text-amber-600 mt-1">⚠️ Requires copybook file</div>
                    )}
                    {category.processingPillar && (
                      <div className="text-xs text-blue-600 mt-1">
                        ℹ️ Parsed in {category.processingPillar === 'operations_pillar' ? 'Operations' : 'Content'} Pillar
                      </div>
                    )}
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      )}

      {/* Step 3: File Upload */}
      {uploadState.step === 'upload' && (
        <>
          <div className="flex items-center justify-between mb-2">
            <div>
              <h3 className="text-sm font-medium text-gray-700">
                {config?.label || 'File Upload'}
              </h3>
              {config && (
                <p className="text-xs text-gray-500 mt-1">
                  {config.extensions.join(', ')} files
                </p>
              )}
            </div>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={handleBack}
              className="text-xs"
            >
              ← Back
            </Button>
          </div>

          {/* File Drop Zone */}
          <div
            {...getRootProps()}
            className={`
              border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors
              ${isDragActive 
                ? 'border-blue-400 bg-blue-50' 
                : uploadState.selectedFile 
                  ? 'border-green-400 bg-green-50' 
                  : 'border-gray-300 hover:border-gray-400'
              }
            `}
            data-testid="file-upload-dropzone"
          >
            <input 
              {...getInputProps()} 
              data-testid="select-files-to-upload"
              aria-label="Select files to upload"
            />
            
            {uploadState.selectedFile ? (
              <div className="space-y-2">
                <CheckCircle className="h-8 w-8 text-green-500 mx-auto" />
                <div className="font-medium text-green-700">{uploadState.selectedFile.name}</div>
                <div className="text-sm text-green-600">
                  {formatFileSize(uploadState.selectedFile.size)}
                </div>
                <div className="text-xs text-gray-500">
                  Click to select a different file
                </div>
              </div>
            ) : (
              <div className="space-y-2">
                <UploadCloud className="h-8 w-8 text-gray-400 mx-auto" />
                <div className="font-medium text-gray-700">
                  {isDragActive ? 'Drop the file here' : 'Drag & drop a file here'}
                </div>
                <div className="text-sm text-gray-500">
                  or click to select a file
                </div>
                {config && (
                  <div className="text-xs text-gray-400">
                    {config.extensions.join(', ')} files only
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Copybook File Upload (for Binary files) */}
          {config?.requiresCopybook && (
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">Copybook File (Required)</label>
          <input
            type="file"
            accept=".cpy,.cbl,.txt"
            onChange={handleCopybookChange}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            data-testid="select-copybook-file"
            aria-label="Select copybook file"
          />
          {uploadState.copybookFile && (
            <div className="text-sm text-green-600">
              Selected: {uploadState.copybookFile.name}
            </div>
          )}
        </div>
      )}

          {/* Upload Button */}
          {uploadState.selectedFile && config && (
            <Button 
              onClick={handleUpload}
              disabled={uploadState.uploading || (config.requiresCopybook && !uploadState.copybookFile)}
              className="w-full"
              data-testid="complete-file-upload"
              aria-label="Complete file upload"
            >
              {uploadState.uploading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Uploading...
                </>
              ) : (
                <>
                  <UploadCloud className="h-4 w-4 mr-2" />
                  Upload File
                </>
              )}
            </Button>
          )}
        </>
      )}

      {/* Processing Status */}
      {uploadState.processingStatus && (
        <div className="flex items-center space-x-2 p-3 bg-blue-50 border border-blue-200 rounded-md">
          <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
          <span className="text-sm text-blue-800">{uploadState.processingStatus}</span>
          {uploadState.workflowId && (
            <span className="text-xs text-blue-600">(Workflow: {uploadState.workflowId})</span>
          )}
        </div>
      )}

      {/* Error Display */}
      {uploadState.error && (
        <div className="flex items-center space-x-2 p-3 bg-red-50 border border-red-200 rounded-md">
          <AlertCircle className="h-4 w-4 text-red-500" />
          <span className="text-sm text-red-700">{uploadState.error}</span>
        </div>
      )}

      {/* Success Display */}
      {uploadState.success && (
        <div className="flex items-center space-x-2 p-3 bg-green-50 border border-green-200 rounded-md">
          <CheckCircle className="h-4 w-4 text-green-500" />
          <span className="text-sm text-green-700">File uploaded successfully!</span>
        </div>
      )}

      {/* User Info */}
      <div className="text-xs text-gray-500 text-center">
        Uploading as: {user?.name} ({user?.email})
      </div>
    </div>
  );
}
