"use client";

import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { UploadCloud, File, CheckCircle, AlertCircle, Loader2, Info } from 'lucide-react';
import { ContentType, FileTypeCategory, FILE_TYPE_CONFIGS, FileMetadata } from '@/shared/types/file';
import { useAuth } from '@/shared/auth/AuthProvider';
// ✅ PHASE 4: Session-First - Use SessionBoundary for session state
import { useSessionBoundary, SessionStatus } from '@/shared/state/SessionBoundaryProvider';
import { usePlatformState } from '@/shared/state/PlatformStateProvider';
import { toast } from 'sonner';

interface UploadState {
  step: "content_type" | "file_category" | "upload" | "saved";
  contentType: ContentType | null;
  fileCategory: FileTypeCategory | null;
  selectedFile: File | null;
  copybookFile: File | null;
  uploading: boolean;
  saving: boolean;  // ✅ NEW: Saving state
  error: string | null;
  success: boolean;
  file_id: string | null;  // ✅ NEW: Store file_id from upload
  boundary_contract_id: string | null;  // ✅ NEW: Store boundary_contract_id from upload
  materialization_pending: boolean;  // ✅ NEW: Track if materialization is pending
}

export function ContentPillarUpload() {
  const { isAuthenticated, user } = useAuth();
  // ✅ PHASE 4: Use SessionBoundary for session state
  const { state: sessionState } = useSessionBoundary();
  // ✅ PHASE 4: Use PlatformState for intent submission
  const platformState = usePlatformState();
  const [uploadState, setUploadState] = useState<UploadState>({
    step: "content_type",
    contentType: null,
    fileCategory: null,
    selectedFile: null,
    copybookFile: null,
    uploading: false,
    saving: false,  // ✅ NEW
    error: null,
    success: false,
    file_id: null,  // ✅ NEW
    boundary_contract_id: null,  // ✅ NEW
    materialization_pending: false,  // ✅ NEW
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

  // ✅ PHASE 4: Handle upload - uploads file but materialization is pending
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

    // ✅ PHASE 4: Validate session
    if (!sessionState.sessionId || !sessionState.tenantId) {
      setUploadState(prev => ({
        ...prev,
        error: "Session required to upload file. Please refresh the page."
      }));
      toast.error("Session required", { description: "Please refresh the page and try again." });
      return;
    }

    setUploadState(prev => ({ ...prev, uploading: true, error: null }));

    try {
      // ✅ PHASE 4: Convert file to hex-encoded bytes for ingest_file intent
      const fileBuffer = await uploadState.selectedFile.arrayBuffer();
      const fileContentHex = Array.from(new Uint8Array(fileBuffer))
        .map(b => b.toString(16).padStart(2, '0'))
        .join('');

      // ✅ PHASE 4: Submit ingest_file intent (file goes to GCS, materialization pending)
      const executionId = await platformState.submitIntent(
        'ingest_file',
        {
          ingestion_type: 'upload',
          file_content: fileContentHex,
          ui_name: uploadState.selectedFile.name,
          file_type: selectedConfig.contentType === ContentType.STRUCTURED 
            ? 'structured' 
            : selectedConfig.contentType === ContentType.UNSTRUCTURED
            ? 'unstructured'
            : 'unstructured', // Default fallback
          mime_type: uploadState.selectedFile.type,
          filename: uploadState.selectedFile.name
        }
      );

      // Track execution to get result
      platformState.trackExecution(executionId);

      // Wait for execution to complete to get file_id and boundary_contract_id
      let file_id: string | null = null;
      let boundary_contract_id: string | null = null;
      const maxAttempts = 30;
      let attempts = 0;

      while (attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 500));
        
        const status = await platformState.getExecutionStatus(executionId);
        
        if (status?.status === "completed") {
          // Extract file_id and boundary_contract_id from execution artifacts
          const fileArtifact = status.artifacts?.file as { semantic_payload?: { file_id?: string; boundary_contract_id?: string } } | undefined;
          if (fileArtifact?.semantic_payload) {
            file_id = fileArtifact.semantic_payload.file_id;
            boundary_contract_id = fileArtifact.semantic_payload.boundary_contract_id;
          }
          break;
        } else if (status?.status === "failed") {
          throw new Error(status.error || "File upload execution failed");
        }
        
        attempts++;
      }

      if (!file_id || !boundary_contract_id) {
        throw new Error("Upload completed but file_id or boundary_contract_id not found");
      }

      // ✅ PHASE 4: File is uploaded but materialization is pending (not saved yet)
      setUploadState(prev => ({
        ...prev,
        uploading: false,
        success: true,
        file_id,
        boundary_contract_id,
        materialization_pending: true  // ✅ Key: Materialization is pending, user must click "Save"
      }));

      // ✅ PHASE 4: Show notification - file is uploaded but not saved
      toast.info("File uploaded", {
        description: "Click 'Save' to make it available for parsing"
      });

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

  // ✅ PHASE 4: Handle save - user explicitly opts in to persistence
  const handleSave = async () => {
    if (!uploadState.file_id || !uploadState.boundary_contract_id) {
      setUploadState(prev => ({
        ...prev,
        error: "File must be uploaded before saving"
      }));
      return;
    }

    // ✅ PHASE 4: Validate session
    if (!sessionState.sessionId || !sessionState.tenantId) {
      setUploadState(prev => ({
        ...prev,
        error: "Session required to save file"
      }));
      return;
    }

    setUploadState(prev => ({ ...prev, saving: true, error: null }));

    try {
      // ✅ PHASE 4: Submit save_materialization intent (authorizes materialization, registers in Supabase)
      const executionId = await platformState.submitIntent(
        'save_materialization',
        {
          boundary_contract_id: uploadState.boundary_contract_id,
          file_id: uploadState.file_id
        }
      );

      // Track execution
      platformState.trackExecution(executionId);

      // Wait for execution to complete
      const maxAttempts = 10;
      let attempts = 0;

      while (attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 500));
        
        const status = await platformState.getExecutionStatus(executionId);
        
        if (status?.status === "completed") {
          // ✅ File is now saved and available for parsing
          setUploadState(prev => ({
            ...prev,
            saving: false,
            materialization_pending: false,  // ✅ Materialization authorized
            step: "saved"  // ✅ Move to "saved" state
          }));

          toast.success("File saved successfully!", {
            description: "File is now available for parsing"
          });
          return;
        } else if (status?.status === "failed") {
          throw new Error(status.error || "Save materialization failed");
        }
        
        attempts++;
      }

      throw new Error("Timeout waiting for save to complete");
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Save failed";
      setUploadState(prev => ({
        ...prev,
        saving: false,
        error: errorMessage
      }));
      toast.error("Save failed", { description: errorMessage });
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

        {/* Upload button - only show if file not uploaded yet */}
        {!uploadState.file_id && (
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
        )}

        {/* ✅ PHASE 4: Save button - only show after upload, when materialization is pending */}
        {uploadState.file_id && uploadState.materialization_pending && (
          <div className="space-y-2">
            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                File uploaded successfully. Click "Save" to make it available for parsing.
              </AlertDescription>
            </Alert>
            <Button
              data-testid="save-file-materialization"
              onClick={handleSave}
              disabled={uploadState.saving}
              className="w-full"
              aria-label="Save file to make it available for parsing"
            >
              {uploadState.saving ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Save File
                </>
              )}
            </Button>
          </div>
        )}

        {/* ✅ PHASE 4: Saved state - file is saved and available */}
        {uploadState.file_id && !uploadState.materialization_pending && uploadState.step === "saved" && (
          <Alert variant="default" className="border-green-200 bg-green-50">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800">
              File saved successfully! It is now available for parsing.
            </AlertDescription>
          </Alert>
        )}

        {/* Error display */}
        {uploadState.error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{uploadState.error}</AlertDescription>
          </Alert>
        )}

        {/* Back button - only show if not saved */}
        {uploadState.step !== "saved" && (
          <Button
            variant="outline"
            onClick={() => setUploadState(prev => ({
              ...prev,
              step: "file_category",
              fileCategory: null,
              selectedFile: null,
              copybookFile: null,
              file_id: null,
              boundary_contract_id: null,
              materialization_pending: false
            }))}
            className="w-full"
          >
            ← Back
          </Button>
        )}

        {/* ✅ PHASE 4: Reset button - show after file is saved */}
        {uploadState.step === "saved" && (
          <Button
            variant="outline"
            onClick={() => setUploadState({
              step: "content_type",
              contentType: null,
              fileCategory: null,
              selectedFile: null,
              copybookFile: null,
              uploading: false,
              saving: false,
              error: null,
              success: false,
              file_id: null,
              boundary_contract_id: null,
              materialization_pending: false
            })}
            className="w-full"
          >
            Upload Another File
          </Button>
        )}
      </CardContent>
    </Card>
  );
}

