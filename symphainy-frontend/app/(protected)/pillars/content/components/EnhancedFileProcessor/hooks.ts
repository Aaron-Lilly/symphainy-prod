/**
 * Enhanced File Processor Hooks
 * Custom hooks for enhanced file processing functionality
 */

import React, { useState, useCallback } from 'react';
import { 
  processFileWithMetadata, 
  getFileMetadata, 
  getFileLineage,
  EnhancedFileProcessingRequest,
  EnhancedFileProcessingResponse,
  FileMetadataResponse,
  FileLineageResponse
} from '@/lib/api/content';
import { ProcessingState, MetadataDisplay } from './types';

export function useEnhancedFileProcessor(
  file: any,
  onProcessingComplete?: (result: EnhancedFileProcessingResponse) => void,
  onError?: (error: string) => void
) {
  const [processingState, setProcessingState] = useState<ProcessingState>({
    isProcessing: false,
    isComplete: false,
    error: null,
    processingTime: 0,
    result: null
  });

  const [metadata, setMetadata] = useState<MetadataDisplay | null>(null);
  const [lineage, setLineage] = useState<any[]>([]);

  const startProcessing = useCallback(async () => {
    if (!file) return;

    setProcessingState(prev => ({
      ...prev,
      isProcessing: true,
      error: null
    }));

    try {
      // Convert file to base64 for API
      const fileData = await convertFileToBase64(file);
      
      const request: EnhancedFileProcessingRequest = {
        file_data: fileData,
        filename: file.filename,
        file_type: file.file_type,
        user_id: 'demo-user', // This would come from auth context
        options: {
          extract_tables: true,
          extract_metadata: true,
          auto_track_lineage: true
        },
        session_token: 'demo-session' // This would come from session context
      };

      const result = await processFileWithMetadata('demo-token', request); // Token from auth context
      
      setProcessingState(prev => ({
        ...prev,
        isProcessing: false,
        isComplete: true,
        processingTime: result.processing_time_seconds,
        result: result
      }));

      setMetadata(result.metadata);
      setLineage(result.lineage || []);

      if (onProcessingComplete) {
        onProcessingComplete(result);
      }

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      
      setProcessingState(prev => ({
        ...prev,
        isProcessing: false,
        error: errorMessage
      }));

      if (onError) {
        onError(errorMessage);
      }
    }
  }, [file, onProcessingComplete, onError]);

  const downloadMetadata = useCallback(() => {
    if (!metadata) return;

    const metadataJson = JSON.stringify(metadata, null, 2);
    const blob = new Blob([metadataJson], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `${file.filename}_metadata.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [metadata, file.filename]);

  const downloadFile = useCallback(() => {
    // This would download the processed file
    // Implementation depends on how files are stored and accessed
    console.log('Download file functionality would be implemented here');
  }, []);

  return {
    processingState,
    metadata,
    lineage,
    startProcessing,
    downloadMetadata,
    downloadFile
  };
}

// Helper function to convert file to base64
async function convertFileToBase64(file: any): Promise<string> {
  return new Promise((resolve, reject) => {
    // For demo purposes, we'll create a mock file data
    // In real implementation, this would read the actual file
    const mockFileData = 'mock-file-data-for-demo';
    const base64 = btoa(mockFileData);
    resolve(base64);
  });
}




