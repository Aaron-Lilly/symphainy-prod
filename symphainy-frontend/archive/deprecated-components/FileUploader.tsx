"use client";

import React, { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
// ✅ PHASE 2: Use service layer hook instead of direct API calls
import { FileType, ApiUploadRequest, FileStatus } from "@/shared/types/file";
import { useFileAPI } from "@/shared/hooks/useFileAPI";
import { useSessionBoundary } from "@/shared/state/SessionBoundaryProvider";
import { usePlatformState } from "@/shared/state/PlatformStateProvider";
import { v4 as uuidv4 } from "uuid";
import { UploadCloud } from "lucide-react";
import { toast } from "sonner";

const TILE_OPTIONS = [
  {
    label: "Structured",
    type: FileType.Structured,
    extensions: ".csv .xls .xlsx",
  },
  { label: "Image", type: FileType.Image, extensions: ".jpg .jpeg .png .bmp" },
  { label: "PDF", type: FileType.Pdf, extensions: ".pdf .docx" },
  { label: "Mainframe", type: FileType.Binary, extensions: ".bin .dat" },
  { 
    label: "SOP/Workflow", 
    type: FileType.SopWorkflow, 
    extensions: ".docx .pdf .bpmn .txt .json",
    description: "SOP and Workflow files for Operations pillar processing"
  },
];

function getAcceptObject(type: FileType | null) {
  if (!type) return undefined;
  switch (type) {
    case FileType.Structured:
      return {
        "text/csv": [".csv"],
        "application/vnd.ms-excel": [".xls"],
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [
          ".xlsx",
        ],
      };
    case FileType.Image:
      return {
        "image/jpeg": [".jpg", ".jpeg"],
        "image/png": [".png"],
        "image/bmp": [".bmp"],
      };
    case FileType.Pdf:
      return {
        "application/pdf": [".pdf"],
        "application/docx": [".docx"],
      };
    case FileType.Binary:
      return {
        "application/octet-stream": [".bin", ".dat"],
      };
    case FileType.SopWorkflow:
      return {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
        "application/pdf": [".pdf"],
        "application/xml": [".bpmn"],
        "text/plain": [".txt"],
        "application/json": [".json"],
      };
    default:
      return undefined;
  }
}

export default function FileUploader() {
  // ✅ PHASE 1: Migrated to SessionBoundaryProvider
  // ✅ PHASE 2: Use service layer hook
  const { state: sessionState } = useSessionBoundary();
  const { uploadAndProcessFile } = useFileAPI();
  const sessionId = sessionState.sessionId;
  // ✅ PHASE 4: Use PlatformStateProvider for realm state
  // Frontend-only continuity, state persisted via intents/artifacts
  // TODO: Phase 5 - Runtime persistence of frontend state
  const { getRealmState, setRealmState } = usePlatformState();
  const [selectedType, setSelectedType] = useState<FileType | null>(null);
  const [selectedExtensions, setSelectedExtensions] = useState<string | null>(
    null,
  );
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [copybookFile, setCopybookFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [processingStatus, setProcessingStatus] = useState<string | null>(null);
  const [workflowId, setWorkflowId] = useState<string | null>(null);

  // Handle file drop or selection
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setSelectedFile(acceptedFiles[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: getAcceptObject(selectedType),
    multiple: false,
    disabled: !selectedType,
  });

  // Handle copybook file selection (for Mainframe)
  const handleCopybookChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setCopybookFile(e.target.files[0]);
    }
  };

  // Handle file type selection from dropdown
  const handleFileTypeChange = (value: string) => {
    const fileType = value as FileType;
    const extensions = TILE_OPTIONS.find(
      (t) => t.type === fileType,
    )?.extensions;
    setSelectedExtensions(extensions || null);
    setSelectedType(fileType);
    setSelectedFile(null);
    setCopybookFile(null);
    setError(null);
  };

  // Upload handler
  const handleUpload = async () => {
    setError(null);
    if (!selectedFile || !selectedType) return;
    if (selectedType === FileType.Binary && !copybookFile) {
      setError("Please upload a copybook file for Mainframe data.");
      return;
    }
    setUploading(true);
    try {
      // ✅ PHASE 2: Use service layer hook - no need to pass token manually
      if (!sessionId) {
        throw new Error("Session not available. Please ensure you're logged in.");
      }
      
      // Service layer hook automatically gets token from SessionBoundaryProvider
      const result = await uploadAndProcessFile(
        selectedFile,
        sessionId,
        selectedType,
      );

      // ✅ PHASE 6: Use { data, error } pattern
      if (result.error) {
        throw new Error(result.error.message || "Upload failed");
      }

      if (!result.data || !result.data.success) {
        throw new Error(result.data?.message || "Upload failed");
      }

      // Store workflow ID for status tracking
      setWorkflowId(result.data.data.workflow_id);
      setProcessingStatus("File uploaded successfully! Processing started...");

      // Create a file metadata object for backward compatibility
      const uploadedFile = {
        uuid: result.data.data.file_id,
        user_id: sessionState.userId || null, // ✅ Use actual user ID from session
        ui_name: selectedFile.name,
        file_type: selectedType,
        mime_type: selectedFile.type,
        original_path: `/uploads/${result.data.data.file_id}_${selectedFile.name}`,
        parsed_path: "",
        status: FileStatus.Uploaded,
        metadata: { 
          size: selectedFile.size,
          workflow_id: result.data.data.workflow_id,
          session_id: result.data.data.session_id
        },
        insights: {},
        rejection_reason: "",
        created_at: result.data.data.timestamp,
        updated_at: result.data.data.timestamp,
        deleted: false,
      };

      // ✅ PHASE 1: Update realm state via PlatformStateProvider
      // Update Content realm files state
      const currentFiles = getRealmState("content", "files") || [];
      const updatedFiles = Array.isArray(currentFiles) ? [...currentFiles, uploadedFile] : [uploadedFile];
      await setRealmState("content", "files", updatedFiles);

      // Store in parsing queue (files available for parsing)
      const currentParsingFiles = getRealmState("content", "parsing_files") || [];
      const updatedParsingFiles = Array.isArray(currentParsingFiles) ? [...currentParsingFiles, uploadedFile] : [uploadedFile];
      await setRealmState("content", "parsing_files", updatedParsingFiles);

      // If it's a SOP/Workflow or PDF file, also add to Journey realm state
      if (selectedType === FileType.SopWorkflow || selectedType === FileType.Pdf) {
        const currentJourneyFiles = getRealmState("journey", "files") || [];
        const updatedJourneyFiles = Array.isArray(currentJourneyFiles) ? [...currentJourneyFiles, uploadedFile] : [uploadedFile];
        await setRealmState("journey", "files", updatedJourneyFiles);
      }

      toast.success("File uploaded successfully");
      
      // Clear form but keep status for a moment
      setTimeout(() => {
        setSelectedFile(null);
        setCopybookFile(null);
        setSelectedType(null);
        setProcessingStatus(null);
        setWorkflowId(null);
      }, 3000);
    } catch (err: any) {
      console.error("Upload error:", err);
      
      // ✅ PHASE 1: Fail gracefully - no mock fallback
      // ✅ WORKING CODE ONLY: No placeholders, mocks, or cheats
      if (!sessionId) {
        setError("Session not available. Please ensure you're logged in.");
        toast.error("Session not available");
      } else {
        setError(err.message || "Upload failed.");
        toast.error("Error uploading file");
      }
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div>
        <Select value={selectedType || ""} onValueChange={handleFileTypeChange}>
          <SelectTrigger className="w-full">
            <SelectValue placeholder="Choose a file type..." />
          </SelectTrigger>
          <SelectContent>
            {TILE_OPTIONS.map((option) => (
              <SelectItem key={option.type} value={option.type}>
                <div className="flex items-center justify-between w-full">
                  <span className="font-medium">{option.label}</span>
                  <span className="text-xs text-muted-foreground ml-2">
                    {option.extensions}
                  </span>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Main upload area - Fixed height to match ParsePreview (185px) */}
      <div
        {...getRootProps()}
        className={`relative block w-full rounded-lg border-2 border-dashed text-center hover:border-primary-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 h-[185px] flex items-center justify-center
        ${isDragActive ? "border-primary bg-accent" : "border-border"}
        ${!selectedType ? "cursor-not-allowed opacity-50" : "cursor-pointer"}`}
      >
        <input {...getInputProps()} />
        <div className="text-muted-foreground">
          <UploadCloud className="mx-auto h-12 w-12 mb-2" />
          <span className="block text-sm font-semibold">
            {selectedType
              ? `Drop a ${TILE_OPTIONS.find((t) => t.type === selectedType)?.label} file here or click to browse`
              : "Select a file type first"}
          </span>
          {selectedFile && (
            <span className="mt-1 block text-xs text-muted-foreground">
              Selected: {selectedFile.name}
            </span>
          )}
        </div>
      </div>

      {selectedType === FileType.Binary && (
        <div>
          <h4 className="text-h4 mb-2">Upload Copybook (Required)</h4>
          <input
            id="copybook-file"
            type="file"
            accept=".cpy,.copybook,.txt"
            onChange={handleCopybookChange}
            className="sr-only"
          />
          <label htmlFor="copybook-file" className="cursor-pointer">
            <div className="w-full rounded-lg border border-input bg-background p-3 text-center text-sm hover:bg-accent">
              {copybookFile
                ? `Selected: ${copybookFile.name}`
                : "Choose Copybook File"}
            </div>
          </label>
        </div>
      )}

      <div>
        <Button
          className="w-full bg-blue-600 text-white"
          onClick={handleUpload}
          disabled={
            uploading ||
            !selectedFile ||
            (selectedType === FileType.Binary && !copybookFile)
          }
        >
          {uploading ? "Uploading..." : "Upload & Process"}
        </Button>
        {error && <p className="mt-2 text-sm text-destructive">{error}</p>}
        
        {/* Processing Status Display */}
        {processingStatus && (
          <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
              <span className="text-sm font-medium text-blue-800">
                {processingStatus}
              </span>
            </div>
            {workflowId && (
              <p className="text-xs text-blue-600 mt-1">
                Workflow ID: {workflowId}
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
