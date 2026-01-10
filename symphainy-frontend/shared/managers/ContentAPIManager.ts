/**
 * Content API Manager
 * 
 * Centralizes all Content pillar API calls and operations.
 * Provides a clean interface for all content-related functionality.
 */

// ============================================
// Content API Manager Types
// ============================================

export interface ContentFile {
  id: string;
  name: string;
  type: string;
  size: number;
  uploadDate: string;
  status?: string; // File status: "uploaded", "parsed", etc.
  metadata?: any;
}

export interface UploadResponse {
  success: boolean;
  file?: ContentFile;
  error?: string;
}

export interface ProcessResponse {
  success: boolean;
  result?: any;
  error?: string;
}

// ============================================
// Content API Manager Class
// ============================================

import { BaseAPIManager, UserContext } from './BaseAPIManager';

export class ContentAPIManager extends BaseAPIManager {
  constructor(sessionToken: string, baseURL?: string, userContext?: UserContext) {
    super(sessionToken, baseURL, userContext);
  }

  // ============================================
  // File Management
  // ============================================

  async listFiles(): Promise<ContentFile[]> {
    try {
      // ✅ OPTIMAL ARCHITECTURE: Use unified dashboard-files endpoint
      // This endpoint returns files from all three tables (project_files, parsed_data_files, embedding_files)
      const result = await this.get<{ files: any[] }>('/api/v1/content-pillar/dashboard-files');

      if (!result.success || !result.data) {
        throw new Error(result.error || 'Failed to list files');
      }

      const backendFiles = result.data.files || [];
        
        // Map backend response to ContentFile format
      // Backend returns: uuid, ui_name, file_type, size, created_at, status, type ("original", "parsed", "embedded")
      // Frontend expects: id, name, type, size, uploadDate, status, metadata
      return backendFiles.map((file: any) => ({
        id: file.uuid || file.file_id || '',
        name: file.ui_name || file.original_filename || file.filename || 'Unnamed File',
        type: file.file_type || file.mime_type || '',
        size: file.size || file.size_bytes || file.file_size || 0,
        uploadDate: file.created_at || file.uploaded_at || new Date().toISOString(),
        status: file.status || (file.type === 'parsed' ? 'parsed' : file.type === 'embedded' ? 'embedded' : 'uploaded'), // Use status from backend, fallback to type
        metadata: {
          ...file,
          file_type: file.type, // Store original type ("original", "parsed", "embedded")
          mime_type: file.mime_type,
          content_type: file.content_type,
          parsed: file.type === 'parsed' || file.status === 'parsed',
          original_file_id: file.original_file_id, // For parsed/embedded files
          parsed_file_id: file.parsed_file_id // For embedded files
        }
      }));
    } catch (error) {
      console.error('Error listing files:', error);
      throw error;
    }
  }

  async uploadFile(
    file: File, 
    copybookFile?: File,
    contentType?: string,
    fileTypeCategory?: string
  ): Promise<UploadResponse> {
    try {
      // DEBUG: Verify file objects
      console.log('[ContentAPIManager] uploadFile called');
      console.log('[ContentAPIManager] file:', file);
      console.log('[ContentAPIManager] file.name:', file?.name);
      console.log('[ContentAPIManager] file.size:', file?.size);
      console.log('[ContentAPIManager] file.type:', file?.type);
      console.log('[ContentAPIManager] copybookFile:', copybookFile);
      console.log('[ContentAPIManager] copybookFile?.name:', copybookFile?.name);
      console.log('[ContentAPIManager] copybookFile?.size:', copybookFile?.size);
      
      if (!file || !(file instanceof File)) {
        console.error('[ContentAPIManager] ERROR: file is not a valid File object:', file);
        throw new Error('Invalid file: file must be a File object');
      }
      
      const formData = new FormData();
      formData.append('file', file);
      
      // Add optional copybook file for binary files
      if (copybookFile) {
        if (!(copybookFile instanceof File)) {
          console.error('[ContentAPIManager] ERROR: copybookFile is not a valid File object:', copybookFile);
          throw new Error('Invalid copybook file: copybookFile must be a File object');
        }
        formData.append('copybook', copybookFile);
      }
      
      // Add content_type and file_type_category if provided (for workflow/SOP files)
      if (contentType) {
        formData.append('content_type', contentType);
      }
      if (fileTypeCategory) {
        formData.append('file_type_category', fileTypeCategory);
      }
      
      // DEBUG: Verify FormData
      console.log('[ContentAPIManager] FormData entries:', Array.from(formData.entries()).map(([key, value]) => {
        if (value instanceof File) {
          return [key, { name: value.name, size: value.size, type: value.type }];
        }
        return [key, value];
      }));

      // Use centralized API config (NO hardcoded values)
      const { getApiEndpointUrl } = require('@/shared/config/api-config');
      const uploadURL = getApiEndpointUrl('/api/v1/content-pillar/upload-file');
      
      console.log('[ContentAPIManager] ⚠️ FILE UPLOAD: Using Traefik route (production setup)');
      console.log('[ContentAPIManager] Uploading to:', uploadURL);
      console.log('[ContentAPIManager] File size:', file.size, 'bytes');
      console.log('[ContentAPIManager] Copybook size:', copybookFile?.size || 0, 'bytes');
      console.log('[ContentAPIManager] File object:', file);
      console.log('[ContentAPIManager] File instanceof File:', file instanceof File);

      // Use direct backend URL (bypass Next.js rewrite for file uploads)
      // For FormData, use makeRequest directly (can't use post() as it JSON.stringifies)
      // Extract endpoint from full URL
      const endpoint = uploadURL.replace(this.baseURL, '');
      const result = await this.makeRequest<{
        file_id?: string;
        uuid?: string;
        ui_name?: string;
        original_filename?: string;
        file_name?: string;
        file_type?: string;
        file_extension?: string;
        file_size?: number;
        uploaded_at?: string;
        mime_type?: string;
        content_type?: string;
        file_type_category?: string;
        copybook_file_id?: string;
        success?: boolean;
        error?: string;
      }>(endpoint, {
        method: 'POST',
        body: formData,
        includeUserContext: true,
        // Don't set Content-Type - browser will set it with boundary for FormData
        headers: {} as any, // Override default headers for FormData
      });

      if (!result.success || !result.data) {
        return {
          success: false,
          error: result.error || 'Upload failed'
        };
      }

      const data = result.data;
      
      // Map semantic response to ContentFile format
      const contentFile: ContentFile = {
        id: data.file_id || data.uuid || '',
        name: data.ui_name || data.original_filename || data.file_name || '',
        type: data.file_type || data.file_extension || '',
        size: data.file_size || 0,
        uploadDate: data.uploaded_at || new Date().toISOString(),
        metadata: {
          original_filename: data.original_filename,
          file_extension: data.file_extension,
          mime_type: data.mime_type,
          content_type: data.content_type,
          file_type_category: data.file_type_category,
          copybook_file_id: data.copybook_file_id
        }
      };
      
      return {
        success: data.success,
        file: contentFile,
        error: data.error
      };
    } catch (error) {
      console.error('Error uploading file:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Upload failed'
      };
    }
  }

  async getFileMetadata(fileId: string): Promise<any> {
    const result = await this.get<{ file?: any }>(`/api/v1/content-pillar/get-file-details/${fileId}`);

    if (!result.success || !result.data) {
      throw new Error(result.error || 'Failed to get file metadata');
    }

    return result.data.file || result.data;
  }

  async deleteFile(fileId: string, fileType?: string): Promise<boolean> {
    let endpoint = `/api/v1/content-pillar/delete-file/${fileId}`;
    if (fileType) {
      endpoint += `?file_type=${fileType}`;
    }

    const result = await this.delete<{ success?: boolean }>(endpoint);

    if (!result.success) {
      console.error('[ContentAPIManager] Delete file failed:', result.error);
      return false;
    }

    return result.data?.success === true || result.success;
  }

  // ============================================
  // Content Processing
  // ============================================

  async processFile(fileId: string, copybookFileId?: string, processingOptions?: any): Promise<ProcessResponse> {
    const requestBody: any = {};
    if (copybookFileId) {
      requestBody.copybook_file_id = copybookFileId;
    }
    if (processingOptions) {
      requestBody.processing_options = processingOptions;
    }

    const result = await this.post<{
      success?: boolean;
      parse_result?: any;
      metadata?: any;
      processing_status?: string;
      parsed_file_id?: string;
      error?: string;
    }>(`/api/v1/content-pillar/process-file/${fileId}`, requestBody);

    if (!result.success || !result.data) {
      return {
        success: false,
        error: result.error || 'Processing failed'
      };
    }

    const data = result.data;
    const parseResult = data.parse_result || {};
    return {
      success: data.success ?? true,
      result: {
        parsed_data: parseResult.parsed_data || {
          format: parseResult.format || 'json_structured',
          chunks: parseResult.preview_records || [],
          structured_data: {
            tables: parseResult.preview_tables || [],
            records: parseResult.preview_records || []
          },
          preview_grid: parseResult.preview_tables?.[0]?.preview_data || [],
          text: parseResult.text_content || ''
        },
        metadata: parseResult.metadata || data.metadata,
        processing_status: data.processing_status,
        parse_result: parseResult,
        parsed_file_id: data.parsed_file_id
      },
      error: data.error
    };
  }

  async extractMetadata(fileId: string): Promise<ProcessResponse> {
    const result = await this.post<{ metadata?: any }>(`/api/content/${fileId}/metadata`);

    if (!result.success || !result.data) {
      return {
        success: false,
        error: result.error || 'Metadata extraction failed'
      };
    }

    return {
      success: true,
      result: result.data.metadata
    };
  }

  // ============================================
  // Content Analysis
  // ============================================

  async analyzeContent(fileId: string, analysisType: string): Promise<ProcessResponse> {
    const result = await this.post<{ analysis?: any }>(`/api/content/${fileId}/analyze`, { analysisType });

    if (!result.success || !result.data) {
      return {
        success: false,
        error: result.error || 'Analysis failed'
      };
    }

    return {
      success: true,
      result: result.data.analysis
    };
  }

  // ============================================
  // Content Search
  // ============================================

  async searchContent(query: string, filters?: any): Promise<ContentFile[]> {
    const result = await this.post<{ results?: ContentFile[] }>('/api/content/search', { query, filters });

    if (!result.success || !result.data) {
      throw new Error(result.error || 'Search failed');
    }

    return result.data.results || [];
  }

  // ============================================
  // Content Health
  // ============================================

  async getHealthStatus(): Promise<any> {
    const result = await this.get<any>('/api/content/health');

    if (!result.success || !result.data) {
      throw new Error(result.error || 'Health check failed');
    }

    return result.data;
  }

  // ============================================
  // Parsed File Management
  // ============================================

  async listParsedFiles(fileId?: string): Promise<any[]> {
    let endpoint = '/api/v1/content-pillar/list-parsed-files';
    if (fileId) {
      endpoint += `?file_id=${fileId}`;
    }

    const result = await this.get<{ parsed_files?: any[] }>(endpoint);

    if (!result.success || !result.data) {
      throw new Error(result.error || 'Failed to list parsed files');
    }

    return result.data.parsed_files || [];
  }

  async previewParsedFile(parsedFileId: string, maxRows: number = 20, maxColumns: number = 20): Promise<any> {
    const endpoint = `/api/v1/content-pillar/preview-parsed-file/${parsedFileId}?max_rows=${maxRows}&max_columns=${maxColumns}`;
    
    const result = await this.get<any>(endpoint);

    if (!result.success || !result.data) {
      throw new Error(result.error || 'Failed to preview parsed file');
    }

    return result.data;
  }

  // ============================================
  // Semantic Layer (Embeddings) Management
  // ============================================

  /**
   * List all embeddings for a file (or all for user)
   * 
   * Returns embeddings grouped by content_id with metadata.
   */
  async listEmbeddings(fileId?: string): Promise<{
    success: boolean;
    embeddings: Array<{
      file_id: string;
      content_id: string;
      embeddings_count: number;
      columns: Array<{
        column_name: string;
        data_type: string;
        semantic_meaning: string;
        semantic_id?: string;
      }>;
      created_at?: string;
    }>;
    count: number;
    error?: string;
  }> {
    let endpoint = '/api/v1/content-pillar/list-embeddings';
    if (fileId) {
      endpoint += `?file_id=${fileId}`;
    }

    const result = await this.get<{
      success?: boolean;
      embeddings?: any[];
      count?: number;
      error?: string;
    }>(endpoint);

    if (!result.success || !result.data) {
      throw new Error(result.error || 'Failed to list embeddings');
    }

    return {
      success: result.data.success !== false,
      embeddings: result.data.embeddings || [],
      count: result.data.count || 0,
      error: result.data.error
    };
  }

  /**
   * Preview semantic layer (embeddings + metadata) for a given content_id
   * 
   * Reconstructs a preview from the stored embeddings and their metadata.
   */
  async previewEmbeddings(contentId: string, maxColumns: number = 20): Promise<{
    success: boolean;
    content_id: string;
    file_id?: string;
    columns: Array<{
      column_name: string;
      data_type: string;
      semantic_meaning: string;
      semantic_id?: string;
      sample_values: string[];
      column_position: number;
      row_count: number;
      semantic_model_recommendation?: any;
    }>;
    structure: {
      column_count: number;
      row_count: number;
      semantic_insights_summary?: string[];
    };
    error?: string;
  }> {
    const endpoint = `/api/v1/content-pillar/preview-embeddings/${contentId}?max_columns=${maxColumns}`;
    
    const result = await this.get<{
      success?: boolean;
      content_id?: string;
      file_id?: string;
      columns?: any[];
      structure?: any;
      error?: string;
    }>(endpoint);

    if (!result.success || !result.data) {
      throw new Error(result.error || 'Failed to preview embeddings');
    }

    const data = result.data;
    return {
      success: data.success !== false,
      content_id: data.content_id || contentId,
      file_id: data.file_id,
      columns: data.columns || [],
      structure: data.structure || {
        column_count: data.columns?.length || 0,
        row_count: data.structure?.row_count || 0
      },
      error: data.error
    };
  }
}





























