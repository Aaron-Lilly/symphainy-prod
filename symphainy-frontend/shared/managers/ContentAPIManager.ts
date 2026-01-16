/**
 * Content API Manager (New Architecture)
 * 
 * Content Realm API client using Experience Plane Client and Runtime-based intent submission.
 * 
 * Architecture:
 * - All operations via Experience Plane Client
 * - Intent submission to Runtime
 * - Execution tracking via PlatformStateProvider
 * 
 * Replaces direct API calls with Runtime-based intent flow.
 */

import { ExperiencePlaneClient, getGlobalExperiencePlaneClient } from "@/shared/services/ExperiencePlaneClient";
import { usePlatformState } from "@/shared/state/PlatformStateProvider";

// ============================================
// Content API Manager Types
// ============================================

export interface ContentFile {
  id: string;
  name: string;
  type: string;
  size: number;
  uploadDate: string;
  status?: string; // File status: "uploaded", "parsed", "embedded"
  metadata?: any;
}

export interface UploadResponse {
  success: boolean;
  file?: ContentFile;
  file_id?: string;
  file_reference?: string;
  error?: string;
}

export interface ParseResponse {
  success: boolean;
  parsed_file_id?: string;
  parsed_content?: any;
  preview?: any;
  error?: string;
}

export interface EmbeddingResponse {
  success: boolean;
  embedding_id?: string;
  embedding_reference?: string;
  error?: string;
}

export interface SemanticInterpretationResponse {
  success: boolean;
  interpretation?: any;
  error?: string;
}

// ============================================
// Content API Manager Class
// ============================================

export class ContentAPIManager {
  private experiencePlaneClient: ExperiencePlaneClient;
  private getPlatformState: () => ReturnType<typeof usePlatformState>;

  constructor(
    experiencePlaneClient?: ExperiencePlaneClient,
    getPlatformState?: () => ReturnType<typeof usePlatformState>
  ) {
    this.experiencePlaneClient = experiencePlaneClient || getGlobalExperiencePlaneClient();
    // Note: getPlatformState will be provided by components using the hook
    this.getPlatformState = getPlatformState || (() => {
      throw new Error("PlatformStateProvider not available. Use ContentAPIManager with usePlatformState hook.");
    });
  }

  /**
   * Upload file (ingest_file intent)
   * 
   * Flow: Experience Plane → Runtime → Content Realm
   */
  async uploadFile(
    file: File,
    copybookFile?: File,
    contentType?: string,
    fileTypeCategory?: string
  ): Promise<UploadResponse> {
    try {
      if (!file || !(file instanceof File)) {
        throw new Error("Invalid file: file must be a File object");
      }

      const platformState = this.getPlatformState();
      
      if (!platformState.state.session.sessionId || !platformState.state.session.tenantId) {
        throw new Error("Session required to upload file");
      }

      // For file upload, we still need to use FormData to send the actual file
      // The intent submission will reference the uploaded file
      // TODO: In full implementation, file upload might be a separate step before intent submission
      // For now, we'll use a hybrid approach: upload file first, then submit intent
      
      // Step 1: Upload file to Experience Plane (file storage)
      const formData = new FormData();
      formData.append('file', file);
      
      if (copybookFile) {
        if (!(copybookFile instanceof File)) {
          throw new Error("Invalid copybook file: copybookFile must be a File object");
        }
        formData.append('copybook', copybookFile);
      }
      
      if (contentType) {
        formData.append('content_type', contentType);
      }
      if (fileTypeCategory) {
        formData.append('file_type_category', fileTypeCategory);
      }

      // Upload file (this might need to go through Experience Plane file upload endpoint)
      // For MVP, we'll assume there's a file upload endpoint that returns file_id
      const { getApiEndpointUrl } = require('@/shared/config/api-config');
      const uploadURL = getApiEndpointUrl('/api/v1/content-pillar/upload-file');
      
      const uploadResponse = await fetch(uploadURL, {
        method: 'POST',
        body: formData,
      });

      if (!uploadResponse.ok) {
        const error = await uploadResponse.json().catch(() => ({ detail: 'File upload failed' }));
        throw new Error(error.detail || `File upload failed: ${uploadResponse.statusText}`);
      }

      const uploadData = await uploadResponse.json();
      const fileId = uploadData.file_id || uploadData.uuid;
      const fileReference = uploadData.file_reference || `file:${platformState.state.session.tenantId}:${platformState.state.session.sessionId}:${fileId}`;

      // Step 2: Submit ingest_file intent to Runtime
      const executionId = await platformState.submitIntent(
        "ingest_file",
        {
          file_id: fileId,
          file_reference: fileReference,
          filename: file.name,
          file_size: file.size,
          file_type: file.type,
          copybook_reference: copybookFile ? `copybook:${platformState.state.session.tenantId}:${platformState.state.session.sessionId}:${fileId}` : undefined,
          content_type: contentType,
          file_type_category: fileTypeCategory,
        },
        {
          ui_name: file.name, // User-friendly filename
          original_filename: file.name,
        }
      );

      // Track execution
      platformState.trackExecution(executionId);

      // Wait for execution to complete (or return immediately and let UI poll)
      // For MVP, we'll return immediately and let the UI track execution status
      const contentFile: ContentFile = {
        id: fileId,
        name: uploadData.ui_name || file.name,
        type: file.type,
        size: file.size,
        uploadDate: new Date().toISOString(),
        status: "uploaded",
        metadata: {
          file_id: fileId,
          file_reference: fileReference,
          execution_id: executionId,
          ...uploadData,
        },
      };

      return {
        success: true,
        file: contentFile,
        file_id: fileId,
        file_reference: fileReference,
      };
    } catch (error) {
      console.error("Error uploading file:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "File upload failed",
      };
    }
  }

  /**
   * List files
   * 
   * Flow: Query State Surface via Runtime (or use existing endpoint for MVP)
   */
  async listFiles(): Promise<ContentFile[]> {
    try {
      // For MVP, we'll use the existing endpoint
      // In full implementation, this would query State Surface via Runtime
      const { getApiEndpointUrl } = require('@/shared/config/api-config');
      const url = getApiEndpointUrl('/api/v1/content-pillar/dashboard-files');
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to list files: ${response.statusText}`);
      }

      const data = await response.json();
      const backendFiles = data.files || [];

      // Map backend response to ContentFile format
      return backendFiles.map((file: any) => ({
        id: file.uuid || file.file_id || '',
        name: file.ui_name || file.original_filename || file.filename || 'Unnamed File',
        type: file.file_type || file.mime_type || '',
        size: file.size || file.size_bytes || file.file_size || 0,
        uploadDate: file.created_at || file.uploaded_at || new Date().toISOString(),
        status: file.status || (file.type === 'parsed' ? 'parsed' : file.type === 'embedded' ? 'embedded' : 'uploaded'),
        metadata: {
          ...file,
          file_type: file.type,
          mime_type: file.mime_type,
          content_type: file.content_type,
          parsed: file.type === 'parsed' || file.status === 'parsed',
          original_file_id: file.original_file_id,
          parsed_file_id: file.parsed_file_id,
        },
      }));
    } catch (error) {
      console.error("Error listing files:", error);
      throw error;
    }
  }

  /**
   * Parse file (parse_content intent)
   * 
   * Flow: Experience Plane → Runtime → Content Realm
   */
  async parseFile(
    fileId: string,
    fileReference: string,
    copybookReference?: string,
    parseOptions?: Record<string, any>
  ): Promise<ParseResponse> {
    try {
      const platformState = this.getPlatformState();
      
      if (!platformState.state.session.sessionId || !platformState.state.session.tenantId) {
        throw new Error("Session required to parse file");
      }

      // Submit parse_content intent
      const executionId = await platformState.submitIntent(
        "parse_content",
        {
          file_id: fileId,
          file_reference: fileReference,
          copybook_reference: copybookReference,
          parse_options: parseOptions || {},
        }
      );

      // Track execution
      platformState.trackExecution(executionId);

      // Return execution ID - UI will track execution status
      return {
        success: true,
        parsed_file_id: fileId, // Will be updated when execution completes
      };
    } catch (error) {
      console.error("Error parsing file:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "File parsing failed",
      };
    }
  }

  /**
   * Extract embeddings (extract_embeddings intent)
   * 
   * Flow: Experience Plane → Runtime → Content Realm
   */
  async extractEmbeddings(
    parsedFileId: string,
    parsedFileReference: string
  ): Promise<EmbeddingResponse> {
    try {
      const platformState = this.getPlatformState();
      
      if (!platformState.state.session.sessionId || !platformState.state.session.tenantId) {
        throw new Error("Session required to extract embeddings");
      }

      // Submit extract_embeddings intent
      const executionId = await platformState.submitIntent(
        "extract_embeddings",
        {
          parsed_file_id: parsedFileId,
          parsed_file_reference: parsedFileReference,
        }
      );

      // Track execution
      platformState.trackExecution(executionId);

      return {
        success: true,
        embedding_reference: parsedFileReference, // Will be updated when execution completes
      };
    } catch (error) {
      console.error("Error extracting embeddings:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Embedding extraction failed",
      };
    }
  }

  /**
   * Get parsed file (get_parsed_file intent)
   * 
   * Flow: Experience Plane → Runtime → Content Realm
   */
  async getParsedFile(fileId: string, fileReference: string): Promise<ParseResponse> {
    try {
      const platformState = this.getPlatformState();
      
      if (!platformState.state.session.sessionId || !platformState.state.session.tenantId) {
        throw new Error("Session required to get parsed file");
      }

      // Submit get_parsed_file intent
      const executionId = await platformState.submitIntent(
        "get_parsed_file",
        {
          file_id: fileId,
          file_reference: fileReference,
        }
      );

      // Track execution
      platformState.trackExecution(executionId);

      // Wait for execution and get result
      // For MVP, we'll poll execution status
      // In full implementation, this would use WebSocket streaming
      const maxAttempts = 10;
      let attempts = 0;
      
      while (attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 500)); // Wait 500ms
        
        const status = await platformState.getExecutionStatus(executionId);
        
        if (status?.status === "completed") {
          return {
            success: true,
            parsed_file_id: fileId,
            parsed_content: status.artifacts?.parsed_content,
            preview: status.artifacts?.preview,
          };
        } else if (status?.status === "failed") {
          throw new Error(status.error || "Failed to get parsed file");
        }
        
        attempts++;
      }

      throw new Error("Timeout waiting for parsed file");
    } catch (error) {
      console.error("Error getting parsed file:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Failed to get parsed file",
      };
    }
  }

  /**
   * Get semantic interpretation (get_semantic_interpretation intent)
   * 
   * Flow: Experience Plane → Runtime → Content Realm
   */
  async getSemanticInterpretation(
    fileId: string,
    fileReference: string
  ): Promise<SemanticInterpretationResponse> {
    try {
      const platformState = this.getPlatformState();
      
      if (!platformState.state.session.sessionId || !platformState.state.session.tenantId) {
        throw new Error("Session required to get semantic interpretation");
      }

      // Submit get_semantic_interpretation intent
      const executionId = await platformState.submitIntent(
        "get_semantic_interpretation",
        {
          file_id: fileId,
          file_reference: fileReference,
        }
      );

      // Track execution
      platformState.trackExecution(executionId);

      // Wait for execution and get result
      const maxAttempts = 10;
      let attempts = 0;
      
      while (attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 500));
        
        const status = await platformState.getExecutionStatus(executionId);
        
        if (status?.status === "completed") {
          return {
            success: true,
            interpretation: status.artifacts?.interpretation,
          };
        } else if (status?.status === "failed") {
          throw new Error(status.error || "Failed to get semantic interpretation");
        }
        
        attempts++;
      }

      throw new Error("Timeout waiting for semantic interpretation");
    } catch (error) {
      console.error("Error getting semantic interpretation:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Failed to get semantic interpretation",
      };
    }
  }
}

// Factory function for use in components
export function useContentAPIManager(): ContentAPIManager {
  const platformState = usePlatformState();
  
  return new ContentAPIManager(
    undefined, // Use global client
    () => platformState // Provide getPlatformState function
  );
}
