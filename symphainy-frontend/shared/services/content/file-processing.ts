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

  async uploadFile(request: FileUploadRequest): Promise<FileUploadResponse> {
    const formData = new FormData();
    formData.append('file', request.file);
    
    if (request.userId) {
      formData.append('user_id', request.userId);
    }
    
    if (request.sessionToken) {
      formData.append('session_token', request.sessionToken);
    }
    
    if (request.metadata) {
      formData.append('metadata', JSON.stringify(request.metadata));
    }

    const sessionToken = request.sessionToken || (typeof window !== 'undefined' ? sessionStorage.getItem('session_token') : '') || '';
    
    const response = await fetch('/api/v1/business_enablement/content/upload-file', {
      method: 'POST',
      headers: {
        'X-Session-Token': sessionToken
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`File upload failed: ${response.status} ${response.statusText}`);
    }

    return await response.json();
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