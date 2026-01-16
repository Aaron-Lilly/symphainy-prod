// FileSelector Types
import { FileMetadata, FileType } from "@/shared/types/file";

export interface FileSelectorProps {
  files: FileMetadata[];
  selected: {
    [type: string]: FileMetadata | null;
  };
  onSelectionChange: (type: string, file: FileMetadata | null) => void;
  fileTypes?: FileType[];
  isLoading?: boolean;
}

export interface FileSelectorState {
  filteredFiles: FileMetadata[];
}

export interface FileSelectorActions {
  handleSelectionChange: (type: string, file: FileMetadata | null) => void;
  getFileIcon: (fileType: FileType | string) => React.ReactNode;
  getFileTypeLabel: (fileType: FileType | string) => string;
}

export interface FileSelectorUIProps {
  files: FileMetadata[];
  selected: {
    [type: string]: FileMetadata | null;
  };
  isLoading: boolean;
  onSelectionChange: (type: string, file: FileMetadata | null) => void;
  getFileIcon: (fileType: FileType | string) => React.ReactNode;
  getFileTypeLabel: (fileType: FileType | string) => string;
}

export interface FileTypeConfig {
  icon: () => React.ReactNode;
  label: string;
  description: string;
}

export type FileTypeConfigMap = Record<FileType, FileTypeConfig>; 