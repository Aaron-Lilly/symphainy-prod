"use client";

import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { UploadCloud, File, CheckCircle, AlertCircle, Loader2, Info } from 'lucide-react';
import { ContentType, FileTypeCategory, FILE_TYPE_CONFIGS, FileMetadata } from '@/shared/types/file';
import { useAuth } from '@/shared/agui/AuthProvider';
import { toast } from 'sonner';

interface UploadState {
  step: "content_type" | "file_category" | "upload";
  contentType: ContentType | null;
  fileCategory: FileTypeCategory | null;
  selectedFile: File | null;
  copybookFile: File | null;
  uploading: boolean;
  error: string | null;
  success: boolean;
}

export function ContentPillarUpload() {
  const { isAuthenticated, user } = useAuth();
  const [uploadState, setUploadState] = useState<UploadState>({
    step: "content_type",
    contentType: null,
    fileCategory: null,
    selectedFile: null,
    copybookFile: null,
    uploading: false,
    error: null,
    success: false,
  });

  // Get available file categories for selected content type
  const availableCategories = uploadState.contentType
    ? FILE_TYPE_CONFIGS.filter(config => config.contentType === uploadState.contentType)
    : [];

  // Get selected file type config
  const selectedConfig = uploadState.fileCategory
    ? FILE_TYPE_CONFIGS.find(config => config.category === uploadState.fileCategory)
    : null;

  // Handle content type selection
  const handleContentTypeSelect = (contentType: ContentType) => {
    setUploadState(prev => ({
      ...prev,
      contentType,
      step: "file_category",
      fileCategory: null,
      selectedFile: null,
      copybookFile: null,
      error: null
    }));
  };

  // Handle file category selection
  const handleFileCategorySelect = (category: FileTypeCategory) => {
    setUploadState(prev => ({
      ...prev,
      fileCategory: category,
      step: "upload",
      selectedFile: null,
      copybookFile: null,
      error: null
    }));
  };

  // Handle file drop
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setUploadState(prev => ({
        ...prev,
        selectedFile: acceptedFiles[0],
        error: null
      }));
    }
  }, []);

  // Handle copybook file selection
  const handleCopybookChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setUploadState(prev => ({
        ...prev,
        copybookFile: e.target.files![0],
        error: null
      }));
    }
  };

  // Get accept object for dropzone
  const getAcceptObject = () => {
    if (!selectedConfig) return undefined;
    
    const accept: Record<string, string[]> = {};
    selectedConfig.mimeTypes.forEach(mimeType => {
      accept[mimeType] = selectedConfig.extensions;
    });
    return accept;
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: getAcceptObject(),
    multiple: false,
    disabled: !selectedConfig || !isAuthenticated,
  });

  // Handle upload
  const handleUpload = async () => {
    if (!uploadState.selectedFile || !selectedConfig) return;
    
    // Validate binary file has copybook
    if (selectedConfig.requiresCopybook && !uploadState.copybookFile) {
      setUploadState(prev => ({
        ...prev,
        error: "Please upload a copybook file for binary files."
      }));
      return;
    }

    setUploadState(prev => ({ ...prev, uploading: true, error: null }));

    try {
      // Use semantic API endpoint
      const formData = new FormData();
      formData.append("file", uploadState.selectedFile);
      formData.append("user_id", user?.id || "anonymous");
      
      // Add copybook if required
      if (uploadState.copybookFile) {
        formData.append("copybook", uploadState.copybookFile);
      }

      const sessionToken = sessionStorage.getItem("session_token") || "";
      const response = await fetch("/api/v1/business_enablement/content/upload-file", {
        method: "POST",
        body: formData,
        headers: {
          "X-Session-Token": sessionToken
        }
      });

      const result = await response.json();

      if (result.success) {
        setUploadState(prev => ({
          ...prev,
          uploading: false,
          success: true
        }));

        // Show notification for SOP/Workflow
        if (selectedConfig.processingPillar === "operations_pillar") {
          toast.info("File uploaded to Content Pillar", {
            description: "This file will be parsed in Operations Pillar"
          });
        } else {
          toast.success("File uploaded successfully!", {
            description: `File ID: ${result.file_id}`
          });
        }

        // Reset after delay
        setTimeout(() => {
          setUploadState({
            step: "content_type",
            contentType: null,
            fileCategory: null,
            selectedFile: null,
            copybookFile: null,
            uploading: false,
            error: null,
            success: false,
          });
        }, 2000);
      } else {
        throw new Error(result.error || "Upload failed");
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Upload failed";
      setUploadState(prev => ({
        ...prev,
        uploading: false,
        error: errorMessage
      }));
      toast.error("Upload failed", { description: errorMessage });
    }
  };

  // Render content type selection
  if (uploadState.step === "content_type") {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Upload File</CardTitle>
          <CardDescription>
            What type of content are you uploading?
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <button
            onClick={() => handleContentTypeSelect(ContentType.STRUCTURED)}
            className="w-full p-4 text-left border rounded-lg hover:bg-accent transition-colors"
          >
            <div className="flex items-center space-x-3">
              <span className="text-2xl">📊</span>
              <div>
                <div className="font-medium">Structured Data</div>
                <div className="text-sm text-muted-foreground">
                  Tabular data, spreadsheets, binary files
                </div>
              </div>
            </div>
          </button>

          <button
            onClick={() => handleContentTypeSelect(ContentType.UNSTRUCTURED)}
            className="w-full p-4 text-left border rounded-lg hover:bg-accent transition-colors"
          >
            <div className="flex items-center space-x-3">
              <span className="text-2xl">📄</span>
              <div>
                <div className="font-medium">Unstructured Documents</div>
                <div className="text-sm text-muted-foreground">
                  Text, PDFs, images, documents
                </div>
              </div>
            </div>
          </button>

          <button
            onClick={() => handleContentTypeSelect(ContentType.HYBRID)}
            className="w-full p-4 text-left border rounded-lg hover:bg-accent transition-colors"
          >
            <div className="flex items-center space-x-3">
              <span className="text-2xl">🔄</span>
              <div>
                <div className="font-medium">Hybrid Content</div>
                <div className="text-sm text-muted-foreground">
                  Complex documents with mixed content
                </div>
              </div>
            </div>
          </button>
        </CardContent>
      </Card>
    );
  }

  // Render file category selection
  if (uploadState.step === "file_category") {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Select File Type</CardTitle>
          <CardDescription>
            Choose the specific file type category
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {availableCategories.map(config => (
            <button
              key={config.category}
              onClick={() => handleFileCategorySelect(config.category)}
              className="w-full p-4 text-left border rounded-lg hover:bg-accent transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <span className="text-2xl">{config.icon}</span>
                  <div>
                    <div className="font-medium flex items-center space-x-2">
                      <span>{config.label}</span>
                      {config.requiresCopybook && (
                        <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
                          ⚠️ Copybook Required
                        </span>
                      )}
                      {config.processingPillar && (
                        <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                          ℹ️ Parsed in {config.processingPillar === "operations_pillar" ? "Operations" : "Content"}
                        </span>
                      )}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {config.extensions.join(", ")}
                    </div>
                    {config.description && (
                      <div className="text-xs text-muted-foreground mt-1">
                        {config.description}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </button>
          ))}

          <Button
            variant="outline"
            onClick={() => setUploadState(prev => ({ ...prev, step: "content_type", contentType: null }))}
            className="w-full mt-4"
          >
            ← Back
          </Button>
        </CardContent>
      </Card>
    );
  }

  // Render upload area
  return (
    <Card>
      <CardHeader>
        <CardTitle>Upload {selectedConfig?.label}</CardTitle>
        <CardDescription>
          {selectedConfig?.extensions.join(", ")} files
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Main file upload */}
        <div
          data-testid="content-pillar-file-upload-area"
          {...getRootProps()}
          className={`
            border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors
            ${isDragActive ? 'border-blue-400 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
          `}
        >
          <div data-testid="file-upload-dropzone">
            <input 
              data-testid="select-files-to-upload"
              {...getInputProps()} 
              aria-label="Select files to upload"
            />
          {uploadState.selectedFile ? (
            <div className="space-y-2">
              <CheckCircle className="h-8 w-8 text-green-500 mx-auto" />
              <div className="font-medium text-green-700">{uploadState.selectedFile.name}</div>
              <div className="text-sm text-green-600">
                {(uploadState.selectedFile.size / 1024).toFixed(2)} KB
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
            </div>
          )}
          </div>
        </div>

        {/* Copybook upload (for binary files) */}
        {selectedConfig?.requiresCopybook && (
          <div className="space-y-2">
            <label className="text-sm font-medium">Copybook File (Required) ⚠️</label>
            <input
              type="file"
              accept=".cpy,.copybook,.txt"
              onChange={handleCopybookChange}
              className="block w-full text-sm text-gray-500
                file:mr-4 file:py-2 file:px-4
                file:rounded-full file:border-0
                file:text-sm file:font-semibold
                file:bg-blue-50 file:text-blue-700
                hover:file:bg-blue-100"
            />
            {uploadState.copybookFile && (
              <div className="text-sm text-green-600">
                ✓ Selected: {uploadState.copybookFile.name}
              </div>
            )}
          </div>
        )}

        {/* SOP/Workflow notification */}
        {selectedConfig?.processingPillar === "operations_pillar" && (
          <Alert>
            <Info className="h-4 w-4" />
            <AlertDescription>
              This file will be uploaded to Content Pillar but parsed in Operations Pillar.
            </AlertDescription>
          </Alert>
        )}

        {/* Upload button */}
        <Button
          data-testid="complete-file-upload"
          onClick={handleUpload}
          disabled={uploadState.uploading || !uploadState.selectedFile || (selectedConfig?.requiresCopybook && !uploadState.copybookFile)}
          className="w-full"
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

        {/* Error display */}
        {uploadState.error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{uploadState.error}</AlertDescription>
          </Alert>
        )}

        {/* Back button */}
        <Button
          variant="outline"
          onClick={() => setUploadState(prev => ({
            ...prev,
            step: "file_category",
            fileCategory: null,
            selectedFile: null,
            copybookFile: null
          }))}
          className="w-full"
        >
          ← Back
        </Button>
      </CardContent>
    </Card>
  );
}

