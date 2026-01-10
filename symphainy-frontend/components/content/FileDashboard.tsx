"use client";
import React, { useEffect, useState, useCallback } from "react";
import { FileMetadata, FileStatus, FileType } from "@/shared/types/file";
import { Button } from "@/components/ui/button";
import { listFiles, deleteFile } from "@/lib/api/fms";
import { useGlobalSession } from "@/shared/agui/GlobalSessionProvider";
import { EmptyState } from "@/components/ui/empty-state";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { RefreshCw, Trash2, Database } from "lucide-react";
import { toast } from "sonner";

// DEVELOPMENT ONLY: Mock data for local development and testing
// This should never be used in production API calls
const mockFiles: FileMetadata[] = [
  {
    uuid: "1",
    user_id: "user1",
    ui_name: "data1.csv",
    file_type: FileType.Structured,
    mime_type: "text/csv",
    original_path: "/uploads/data1.csv",
    parsed_path: "",
    status: FileStatus.Uploaded,
    metadata: { size: 12345 },
    insights: {},
    rejection_reason: "",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    deleted: false,
  },
  {
    uuid: "2",
    user_id: "user1",
    ui_name: "report.pdf",
    file_type: FileType.Pdf,
    mime_type: "application/pdf",
    original_path: "/uploads/report.pdf",
    parsed_path: "",
    status: FileStatus.Parsed,
    metadata: { size: 67890 },
    insights: {},
    rejection_reason: "",
    created_at: new Date(Date.now() - 86400000).toISOString(),
    updated_at: new Date(Date.now() - 86400000).toISOString(),
    deleted: false,
  },
  {
    uuid: "3",
    user_id: "user1",
    ui_name: "image.jpg",
    file_type: FileType.Binary,
    mime_type: "image/jpeg",
    original_path: "/uploads/image.jpg",
    parsed_path: "",
    status: FileStatus.Validated,
    metadata: { size: 234567 },
    insights: {},
    rejection_reason: "",
    created_at: new Date(Date.now() - 172800000).toISOString(),
    updated_at: new Date(Date.now() - 172800000).toISOString(),
    deleted: false,
  },
];

export default function FileDashboard() {
  const { getPillarState, setPillarState, guideSessionToken } =
    useGlobalSession();
  const [files, setFiles] = useState<FileMetadata[]>([]);
  const [deleting, setDeleting] = useState<string | null>(null);
  const [isLoadingFiles, setIsLoadingFiles] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAll, setShowAll] = useState(false);
  const [initialized, setInitialized] = useState(false);

  // Initialize from global state only once
  useEffect(() => {
    if (!initialized) {
      const currentState = getPillarState("data");
      if (currentState?.files && Array.isArray(currentState.files) && currentState.files.length > 0) {
        setFiles(currentState.files);
        setShowAll(currentState.files.length <= 5);
      }
      if (currentState?.deleting) {
        setDeleting(currentState.deleting);
      }
      setInitialized(true);
    }
  }, [initialized, getPillarState]);

  // Only sync back to global state when files actually change, not on every render
  useEffect(() => {
    if (initialized) {
      setPillarState("data", { files, deleting });
    }
  }, [files, deleting, initialized, setPillarState]);

  const fetchFiles = useCallback(async () => {
    setIsLoadingFiles(true);
    setError(null);
    try {
      const token = guideSessionToken || "debug-token";

      if (guideSessionToken) {
        // Use real API when token is available
        const fileList = await listFiles(token);
        const safeFileList = Array.isArray(fileList) ? fileList : [];
        setFiles(safeFileList);
        setShowAll(safeFileList.length <= 5);
      } else {
        // Use mock data for development
        setFiles(mockFiles.slice(0, 5));
        setShowAll(mockFiles.length <= 5);
      }
    } catch (error) {
      console.error("Failed to fetch files:", error);
      setError(
        "Failed to fetch files. Please check your connection and try again.",
      );
      toast.error("Error loading files");
      // Fallback to mock data
      setFiles(mockFiles.slice(0, 5));
    } finally {
      setIsLoadingFiles(false);
    }
  }, [guideSessionToken]);

  // Only fetch files if we haven't initialized or if files are empty after initialization
  useEffect(() => {
    const fileCount = Array.isArray(files) ? files.length : 0;
    if (initialized && fileCount === 0 && !isLoadingFiles) {
      fetchFiles();
    }
  }, [initialized, files.length, isLoadingFiles, fetchFiles]);

  const handleDelete = async (uuid: string) => {
    try {
      const token = guideSessionToken || "debug-token";

      if (guideSessionToken) {
        // Use real API when token is available
        await deleteFile(uuid, token);
      }

      // Update local state - this will automatically sync to global state via useEffect
      const currentFiles = Array.isArray(files) ? files : [];
      const updatedFiles = currentFiles.filter((file) => file.uuid !== uuid);
      setFiles(updatedFiles);

      setDeleting(null);
      toast.success("File deleted successfully");
    } catch (error) {
      console.error("Failed to delete file:", error);
      toast.error("Error deleting file");
    }
  };

  const getStatusVariant = (
    status: FileStatus,
  ): "default" | "secondary" | "destructive" | "outline" => {
    switch (status) {
      // Note: FileStatus.Approved doesn't exist in the enum anymore
      case FileStatus.Validated:
      case FileStatus.Parsed:
        return "default";
      // Note: FileStatus.Rejected doesn't exist in the enum anymore
      case FileStatus.Parsing:
        return "secondary";
      case FileStatus.Uploaded:
        return "outline";
      default:
        return "outline";
    }
  };

  // Sort files by creation date (newest first)
  // Ensure files is always an array before spreading
  const fileArray = Array.isArray(files) ? files : [];
  const sortedFiles = [...fileArray].sort((a, b) => {
    const dateA = new Date(a.created_at).getTime();
    const dateB = new Date(b.created_at).getTime();
    return dateB - dateA; // Descending order (newest first)
  });

  const displayedFiles = showAll ? sortedFiles : sortedFiles.slice(0, 5);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          {Array.isArray(files) ? files.length : 0} file(s) uploaded.
        </p>
        <Button
          variant="outline"
          size="sm"
          onClick={fetchFiles}
          disabled={isLoadingFiles}
          aria-label="Refresh file list"
        >
          <RefreshCw
            className={`h-4 w-4 text-gray-500 ${isLoadingFiles ? "animate-spin" : ""}`}
            style={isLoadingFiles ? { animationDuration: "1s" } : {}}
          />
        </Button>
      </div>

      {error && (
        <div className="p-4 m-4 text-center text-red-600 bg-red-50 border border-red-200 rounded-lg">
          <p>{error}</p>
        </div>
      )}

      {isLoadingFiles && (Array.isArray(files) ? files.length : 0) === 0 ? (
        <div className="text-base text-sm text-gray-700 text-center p-8 text-muted-foreground">
          loading files...
        </div>
      ) : !isLoadingFiles && (Array.isArray(files) ? files.length : 0) === 0 && !error ? (
        <div className="p-4" data-testid="empty-state">
          <EmptyState
            icon={<Database className="h-10 w-10" />}
            title="No Data Files Found"
            description="Get started by uploading your first data file. Once uploaded, your files will appear here."
          />
        </div>
      ) : (
        !error && (
          <div className="border rounded-lg overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Filename</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Size</TableHead>
                  <TableHead>Upload Date</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody data-testid="file-list">
                {displayedFiles.map((file) => (
                  <TableRow key={file.uuid}>
                    <TableCell className="font-medium">
                      {file.ui_name}
                    </TableCell>
                    <TableCell>{file.file_type}</TableCell>
                    <TableCell>
                      {file.metadata?.size
                        ? `${(file.metadata.size / 1024).toFixed(2)} KB`
                        : "-"}
                    </TableCell>
                    <TableCell>
                      {new Date(file.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={getStatusVariant(file.status)}
                        className="w-20 justify-center"
                      >
                        {file.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => setDeleting(file.uuid)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            {(Array.isArray(files) ? files.length : 0) > 5 && (
              <div className="p-2 text-center border-t">
                <Button
                  variant="link"
                  size="sm"
                  onClick={() => setShowAll(!showAll)}
                >
                  {showAll ? "Show Less" : `Show all ${Array.isArray(files) ? files.length : 0} files`}
                </Button>
              </div>
            )}
          </div>
        )
      )}

      {/* Confirmation Modal */}
      {deleting && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>Confirm Deletion</CardTitle>
              <CardDescription>
                Are you sure you want to delete this file? This action cannot be
                undone.
              </CardDescription>
            </CardHeader>
            <CardContent className="flex justify-end gap-4">
              <Button onClick={() => setDeleting(null)} variant="outline">
                Cancel
              </Button>
              <Button
                onClick={() => handleDelete(deleting)}
                variant="destructive"
              >
                Confirm Delete
              </Button>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
