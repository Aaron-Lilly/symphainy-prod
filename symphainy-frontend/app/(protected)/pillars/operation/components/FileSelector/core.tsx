// FileSelector Core Component
"use client";
import React from "react";
import { useFileSelector } from "./hooks";
import { FileSelectorProps } from "./types";
import { FileSelectorUI } from "./components";

export function FileSelectorCore({
  files,
  selected,
  onSelectionChange,
  fileTypes,
  isLoading = false,
}: FileSelectorProps) {
  const {
    filteredFiles,
    handleSelectionChange,
    getFileIcon,
    getFileTypeLabel,
  } = useFileSelector({
    files,
    selected,
    onSelectionChange,
    fileTypes,
  });

  return (
    <FileSelectorUI
      files={filteredFiles}
      selected={selected}
      isLoading={isLoading}
      onSelectionChange={handleSelectionChange}
      getFileIcon={getFileIcon}
      getFileTypeLabel={getFileTypeLabel}
    />
  );
} 