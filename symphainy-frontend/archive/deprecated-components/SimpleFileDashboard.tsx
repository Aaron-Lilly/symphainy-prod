"use client";
import React, { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
// ✅ PHASE 2: Use service layer hook instead of direct API calls
import { useContentAPI, SimpleFileData } from "@/shared/hooks/useContentAPI";
import { useSessionBoundary } from "@/shared/state/SessionBoundaryProvider";
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
import { RefreshCw, FileText, FileImage, FileSpreadsheet, ChevronDown, ChevronUp } from "lucide-react";
import { toast } from "sonner";

export default function SimpleFileDashboard() {
  // ✅ PHASE 1: Migrated to SessionBoundaryProvider
  // ✅ PHASE 2: Use service layer hook
  const { state: sessionState } = useSessionBoundary();
  const { listContentFiles } = useContentAPI();
  const [files, setFiles] = useState<SimpleFileData[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAll, setShowAll] = useState(false);

  // ✅ PHASE 2: Use service layer hook - no need to pass token manually
  // ✅ PHASE 6: Use { data, error } pattern
  const loadFiles = async () => {
    setIsLoading(true);
    setError(null);

    // Service layer hook automatically gets token from SessionBoundaryProvider
    const result = await listContentFiles();
    if (result.error) {
      const errorMessage = result.error.message || "Failed to load files";
      setError(errorMessage);
      toast.error(errorMessage);
    } else if (result.data) {
      setFiles(result.data);
      toast.success(`Loaded ${result.data.length} files`);
    } else {
      setFiles([]);
    }
    setIsLoading(false);
  };

  useEffect(() => {
    loadFiles();
  }, [listContentFiles]);

  const getFileIcon = (fileType: string) => {
    switch (fileType.toLowerCase()) {
      case 'pdf':
        return <FileText className="h-4 w-4" />;
      case 'csv':
      case 'xlsx':
        return <FileSpreadsheet className="h-4 w-4" />;
      case 'jpg':
      case 'jpeg':
      case 'png':
        return <FileImage className="h-4 w-4" />;
      default:
        return <FileText className="h-4 w-4" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
      'uploaded': 'default',
      'parsed': 'secondary',
      'validated': 'outline',
      'error': 'destructive',
    };

    return (
      <Badge variant={statusMap[status.toLowerCase()] || 'default'}>
        {status}
      </Badge>
    );
  };

  const formatFileSize = (metadata: any) => {
    if (!metadata || !metadata.size) return 'Unknown';
    const bytes = metadata.size;
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  // Determine which files to show
  const displayFiles = showAll ? files : files.slice(0, 5);
  const hasMoreFiles = files.length > 5;

  if (error) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">Files</h3>
          <Button onClick={loadFiles} disabled={isLoading} size="sm">
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Retry
          </Button>
        </div>
        <div className="text-red-600 bg-red-50 p-4 rounded-md">
          Error: {error}
        </div>
      </div>
    );
  }

  if (files.length === 0 && !isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">Files</h3>
          <Button onClick={loadFiles} disabled={isLoading} size="sm">
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
        <EmptyState
          icon={<FileText className="h-8 w-8" />}
          title="No files found"
          description="Upload some files to get started"
        />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Files ({files.length})</h3>
        <Button onClick={loadFiles} disabled={isLoading} size="sm">
          <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      <div className="border rounded-md">
        <Table>
          <TableHeader>
            <TableRow key="header">
              <TableHead>File</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Size</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Uploaded</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {displayFiles.map((file) => (
              <TableRow key={file.id || file.file_id}>
                <TableCell className="flex items-center space-x-2">
                  {getFileIcon(file.file_type)}
                  <span className="font-medium">{file.ui_name}</span>
                </TableCell>
                <TableCell>
                  <Badge variant="outline">{file.file_type}</Badge>
                </TableCell>
                <TableCell>{formatFileSize(file.metadata)}</TableCell>
                <TableCell>{getStatusBadge(file.status)}</TableCell>
                <TableCell>{formatDate(file.created_at)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {hasMoreFiles && (
        <div className="flex justify-center">
          <Button
            variant="outline"
            onClick={() => setShowAll(!showAll)}
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
    </div>
  );
} 