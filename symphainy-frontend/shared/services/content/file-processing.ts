/**
 * Content File Processing
 * Specialized file processing functionality for content service
 */

import { SimpleFileData, ParseFileResponse } from './types';

export interface FileUploadRequest {
  file: File;
  userId?: string;
  sessionToken?: string;
  metadata?: any;
}

export interface FileUploadResponse {
  file_id: string;
  status: string;
  message: string;
  file_data: SimpleFileData;
}

export interface FileFormatMapping {
  inputFormat: string;
  outputFormat: 'parquet' | 'json_structured' | 'json_chunks';
  mappingRules: any;
}

export class FileProcessingService {
  private contentService: any;

  constructor(contentService: any) {
    this.contentService = contentService;
  }

  /**
   * Upload file - uses intent-based API pattern.
   * 
   * ✅ PHASE 4: Migrated to intent-based API
   * - Uses ingest_file intent
   * - File goes to GCS, materialization is pending
   * - User must explicitly save to persist
   */
  async uploadFile(request: FileUploadRequest): Promise<FileUploadResponse> {
    // ✅ PHASE 4: Convert file to hex-encoded bytes for ingest_file intent
    const fileBuffer = await request.file.arrayBuffer();
    const fileContentHex = Array.from(new Uint8Array(fileBuffer))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');

    // ✅ PHASE 4: Get session state
    const sessionId = typeof window !== 'undefined' ? sessionStorage.getItem('session_id') : null;
    const tenantId = typeof window !== 'undefined' ? sessionStorage.getItem('tenant_id') : null;

    if (!sessionId || !tenantId) {
      throw new Error("Session required to upload file");
    }

    // ✅ PHASE 4: Submit ingest_file intent via intent-based API
    const response = await fetch('/api/intent/submit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': typeof window !== 'undefined' ? `Bearer ${sessionStorage.getItem('access_token') || ''}` : ''
      },
      body: JSON.stringify({
        intent_type: 'ingest_file',
        tenant_id: tenantId,
        session_id: sessionId,
        parameters: {
          ingestion_type: 'upload',
          file_content: fileContentHex,
          ui_name: request.file.name,
          file_type: request.metadata?.file_type || 'unstructured',
          mime_type: request.file.type,
          filename: request.file.name,
          user_id: request.userId
        },
        metadata: request.metadata
      })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'File upload failed' }));
      throw new Error(errorData.detail || `File upload failed: ${response.status} ${response.statusText}`);
    }

    const result = await response.json();
    
    // Extract file_id and boundary_contract_id from execution result
    // Note: May need to poll execution status to get full result
    return {
      file_id: result.execution_id, // Temporary - will be updated when execution completes
      status: 'pending',
      message: 'File upload initiated. Materialization is pending.',
      file_data: {
        file_id: result.execution_id,
        status: 'pending',
        materialization_pending: true
      } as any
    };
  }

  async parseMainframeFile(fileId: string, copybookData?: string): Promise<ParseFileResponse> {
    const parseRequest = {
      file_id: fileId,
      parse_type: 'mainframe',
      copybook_data: copybookData,
    };

    return await this.contentService.parseFile(parseRequest);
  }

  async convertToAIFriendlyFormat(
    fileId: string, 
    targetFormat: 'parquet' | 'json_structured' | 'json_chunks',
    mappingRules?: any
  ): Promise<ParseFileResponse> {
    const parseRequest = {
      file_id: fileId,
      parse_type: 'format_conversion',
      target_format: targetFormat,
      mapping_rules: mappingRules,
    };

    return await this.contentService.parseFile(parseRequest);
  }

  detectFileType(file: File): string {
    const extension = file.name.split('.').pop()?.toLowerCase();
    const mimeType = file.type;

    // Mainframe file detection
    if (extension === 'cpy' || extension === 'cbl') {
      return 'mainframe_copybook';
    }
    
    if (extension === 'bin' || mimeType.includes('application/octet-stream')) {
      return 'mainframe_binary';
    }

    // Standard file types
    switch (extension) {
      case 'csv':
        return 'csv';
      case 'json':
        return 'json';
      case 'xlsx':
      case 'xls':
        return 'excel';
      case 'pdf':
        return 'pdf';
      case 'docx':
      case 'doc':
        return 'word';
      case 'txt':
        return 'text';
      default:
        return 'unknown';
    }
  }

  getRecommendedFormat(fileType: string): 'parquet' | 'json_structured' | 'json_chunks' {
    switch (fileType) {
      case 'csv':
      case 'excel':
        return 'parquet';
      case 'json':
        return 'json_structured';
      case 'pdf':
      case 'word':
      case 'text':
        return 'json_chunks';
      case 'mainframe_copybook':
      case 'mainframe_binary':
        return 'json_structured';
      default:
        return 'json_chunks';
    }
  }

  async validateFile(file: File): Promise<{ valid: boolean; errors: string[] }> {
    const errors: string[] = [];
    const maxSize = 100 * 1024 * 1024; // 100MB

    if (file.size > maxSize) {
      errors.push('File size exceeds 100MB limit');
    }

    const allowedTypes = [
      'text/csv',
      'application/json',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/vnd.ms-excel',
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/msword',
      'text/plain',
      'application/octet-stream', // For mainframe files
    ];

    if (!allowedTypes.includes(file.type) && !file.name.match(/\.(cpy|cbl|bin)$/i)) {
      errors.push('File type not supported');
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }
} 