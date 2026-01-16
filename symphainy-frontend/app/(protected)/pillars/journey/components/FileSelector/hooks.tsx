// FileSelector Hooks
"use client";
import React, { useMemo } from "react";
import { FileText, FileImage, FileCode, FileSpreadsheet, FileVideo, FileAudio, FileArchive, File } from "lucide-react";
import { FileType, FileMetadata } from "@/shared/types/file";
import { FileSelectorProps, FileSelectorState, FileSelectorActions, FileTypeConfigMap } from "./types";

export function useFileSelector(props: FileSelectorProps): FileSelectorState & FileSelectorActions {
  // File type configurations
  const fileTypeConfigs: FileTypeConfigMap = {
    [FileType.Document]: {
      icon: () => <FileText className="w-5 h-5" />,
      label: "Document",
      description: "Text documents and reports"
    },
    [FileType.Pdf]: {
      icon: () => <FileText className="w-5 h-5" />,
      label: "PDF",
      description: "Portable Document Format files"
    },
    [FileType.Text]: {
      icon: () => <FileText className="w-5 h-5" />,
      label: "Text",
      description: "Plain text files"
    },
    [FileType.Image]: {
      icon: () => <FileImage className="w-5 h-5" />,
      label: "Image",
      description: "Image files (PNG, JPG, etc.)"
    },
    [FileType.Structured]: {
      icon: () => <FileSpreadsheet className="w-5 h-5" />,
      label: "Structured",
      description: "Structured data files (CSV, JSON, etc.)"
    },
    [FileType.Binary]: {
      icon: () => <File className="w-5 h-5" />,
      label: "Binary",
      description: "Binary files"
    },
    [FileType.SopWorkflow]: {
      icon: () => <FileText className="w-5 h-5" />,
      label: "SOP/Workflow",
      description: "Standard Operating Procedures and Workflow files"
    },
  };

  // Filter files based on file types
  const filteredFiles = useMemo(() => {
    if (!props.fileTypes || props.fileTypes.length === 0) {
      return props.files;
    }
    return props.files.filter(file => props.fileTypes!.includes(file.file_type as FileType));
  }, [props.files, props.fileTypes]);

  // Handle file selection change
  const handleSelectionChange = (type: string, file: FileMetadata | null) => {
    props.onSelectionChange(type, file);
  };

  // Get file icon based on file type
  const getFileIcon = (fileType: FileType | string) => {
    const type = fileType as FileType;
    return fileTypeConfigs[type]?.icon() || fileTypeConfigs[FileType.Document].icon();
  };

  // Get file type label
  const getFileTypeLabel = (fileType: FileType | string) => {
    const type = fileType as FileType;
    return fileTypeConfigs[type]?.label || fileTypeConfigs[FileType.Document].label;
  };

  return {
    filteredFiles,
    handleSelectionChange,
    getFileIcon,
    getFileTypeLabel,
  };
} 