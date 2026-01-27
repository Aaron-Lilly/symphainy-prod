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

import { ExperiencePlaneClient, getGlobalExperiencePlaneClient, ExecutionStatus } from "@/shared/services/ExperiencePlaneClient";
import { usePlatformState } from "@/shared/state/PlatformStateProvider";
import { validateSession } from "@/shared/utils/sessionValidation";
import { getApiEndpointUrl } from "@/shared/config/api-config";

// ============================================
// Content API Manager Types
// ============================================

export interface ContentFile {
  id: string;
  name: string;
  type: string;
  size: number;
  uploadDate: string;
  status?: string; // File status: "uploaded", "parsed", "embedded", "pending"
  metadata?: any;
  boundary_contract_id?: string;  // NEW: Boundary contract ID
  materialization_pending?: boolean;  // NEW: Whether materialization is pending
}

export interface UploadResponse {
  success: boolean;
  file?: ContentFile;
  file_id?: string;
  file_reference?: string;
  boundary_contract_id?: string;  // NEW: Boundary contract ID from upload
  materialization_pending?: boolean;  // NEW: Whether materialization is pending
  error?: string;
}

export interface SaveMaterializationResponse {
  success: boolean;
  file_id?: string;
  boundary_contract_id?: string;
  materialization_id?: string;  // ✅ PHASE 2: Added materialization_id
  message?: string;
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
// Phase 3: Artifact-Centric Types
// ============================================

export interface ArtifactRecord {
  artifact_id: string;
  artifact_type: string;
  tenant_id: string;
  produced_by: {
    intent: string;
    execution_id: string;
  };
  lifecycle_state: string;
  semantic_descriptor: {
    schema?: string;
    record_count?: number;
    parser_type?: string;
    embedding_model?: string;
  };
  parent_artifacts: string[];
  materializations: Array<{
    materialization_id: string;
    storage_type: string;
    uri: string;
    format: string;
    compression?: string;
    created_at: string;
  }>;
  created_at: string;
  updated_at: string;
}

export interface ArtifactListItem {
  artifact_id: string;
  artifact_type: string;
  lifecycle_state: string;
  semantic_descriptor: {
    schema?: string;
    record_count?: number;
    parser_type?: string;
    embedding_model?: string;
  };
  created_at: string;
  updated_at: string;
}

export interface ArtifactListResponse {
  artifacts: ArtifactListItem[];
  total: number;
  limit: number;
  offset: number;
}

export interface PendingIntent {
  intent_id: string;
  intent_type: string;
  status: string;
  target_artifact_id?: string;
  context: Record<string, any>; // ingestion_profile lives here
  created_at: string;
  updated_at: string;
}

export interface PendingIntentListResponse {
  intents: PendingIntent[];
  total: number;
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
      
      // ✅ FIX ISSUE 4: Use standardized session validation
      validateSession(platformState, "upload file");

      // ✅ FIX ISSUE 3: Parameter validation before submitIntent
      if (!file) {
        throw new Error("file is required for ingest_file");
      }

      // ✅ PHASE 4: Convert file to hex-encoded bytes for ingest_file intent
      // Following CTO guidance: Upload file (goes to GCS), materialization is pending
      // User must explicitly click "Save" to persist (via save_materialization intent)
      const fileBuffer = await file.arrayBuffer();
      const fileContentHex = Array.from(new Uint8Array(fileBuffer))
        .map(b => b.toString(16).padStart(2, '0'))
        .join('');

      // ✅ PHASE 4: Submit ingest_file intent (file goes to GCS, materialization pending)
      const executionId = await platformState.submitIntent(
        "ingest_file",
        {
          ingestion_type: 'upload',
          file_content: fileContentHex,
          ui_name: file.name,
          file_type: fileTypeCategory || 'unstructured',
          mime_type: file.type,
          filename: file.name
        },
        {
          ui_name: file.name, // User-friendly filename
          original_filename: file.name,
        }
      );

      // Track execution
      platformState.trackExecution(executionId);

      // ✅ PHASE 4: Wait for execution to complete to get file_id and boundary_contract_id
      const maxAttempts = 30; // Wait up to 15 seconds (30 * 500ms)
      let attempts = 0;
      let fileId: string | undefined;
      let boundaryContractId: string | undefined;
      let materializationPending: boolean = true;
      
      while (attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 500)); // Wait 500ms
        
        const status = await platformState.getExecutionStatus(executionId);
        
        if (status?.status === "completed") {
          // Extract file_id and boundary_contract_id from execution artifacts
          const fileArtifact = status.artifacts?.file;
          if (fileArtifact?.semantic_payload) {
            fileId = fileArtifact.semantic_payload.file_id;
            boundaryContractId = fileArtifact.semantic_payload.boundary_contract_id;
            materializationPending = fileArtifact.semantic_payload.materialization_pending === true;
          }
          break;
        } else if (status?.status === "failed") {
          throw new Error(status.error || "File upload execution failed");
        }
        
        attempts++;
      }

      // ✅ PHASE 4: Validate we got file_id and boundary_contract_id
      if (!fileId || !boundaryContractId) {
        throw new Error("Upload completed but file_id or boundary_contract_id not found in execution result");
      }

      const fileReference = `file:${platformState.state.session.tenantId}:${platformState.state.session.sessionId}:${fileId}`;

      const contentFile: ContentFile = {
        id: fileId,
        name: file.name,
        type: file.type,
        size: file.size,
        uploadDate: new Date().toISOString(),
        status: materializationPending ? "pending" : "uploaded",  // ✅ Materialization is pending until user clicks "Save"
        metadata: {
          file_id: fileId,
          file_reference: fileReference,
          execution_id: executionId,
          boundary_contract_id: boundaryContractId,
          materialization_pending: materializationPending,
        },
      };

      return {
        success: true,
        file: contentFile,
        file_id: fileId,
        file_reference: fileReference,
        boundary_contract_id: boundaryContractId,
        materialization_pending: materializationPending,  // ✅ Key: Materialization is pending
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
   * Save materialization (save_materialization intent)
   * 
   * Explicitly save (materialize) a file that was uploaded.
   * This is the second phase of the two-phase materialization flow.
   * 
   * Flow: Experience Plane → Runtime → Content Realm (via submitIntent)
   */
  async saveMaterialization(
    boundaryContractId: string,
    fileId: string
  ): Promise<SaveMaterializationResponse> {
    try {
      const platformState = this.getPlatformState();
      
      // ✅ PHASE 2: Use standardized session validation
      validateSession(platformState, "save materialization");

      // ✅ PHASE 2: Parameter validation before submitIntent
      if (!boundaryContractId || !fileId) {
        throw new Error("boundary_contract_id and file_id are required for save_materialization");
      }

      // ✅ PHASE 2: Migrate to intent-based API (submitIntent)
      const executionId = await platformState.submitIntent(
        "save_materialization",
        {
          file_id: fileId,
          boundary_contract_id: boundaryContractId,
        }
      );

      // Track execution
      platformState.trackExecution(executionId);

      // ✅ PHASE 2: Wait for execution to complete to get materialization_id
      const maxAttempts = 30; // Wait up to 15 seconds (30 * 500ms)
      let attempts = 0;
      let materializationId: string | undefined;
      let success: boolean = false;
      
      while (attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 500)); // Wait 500ms
        
        const status = await platformState.getExecutionStatus(executionId);
        
        if (status?.status === "completed") {
          // Extract materialization_id from execution artifacts
          const materializationArtifact = status.artifacts?.materialization;
          if (materializationArtifact?.semantic_payload) {
            materializationId = materializationArtifact.semantic_payload.materialization_id;
            success = materializationArtifact.semantic_payload.success === true;
          } else if (status.artifacts?.file?.semantic_payload) {
            // Fallback: check if file artifact has materialization info
            const filePayload = status.artifacts.file.semantic_payload;
            materializationId = filePayload.materialization_id;
            success = filePayload.materialization_pending === false;
          } else {
            // If no artifact structure, assume success if execution completed
            success = true;
          }
          break;
        } else if (status?.status === "failed") {
          throw new Error(status.error || "Save materialization execution failed");
        }
        
        attempts++;
      }

      if (attempts >= maxAttempts) {
        throw new Error("Timeout waiting for save materialization to complete");
      }

      return {
        success: success,
        file_id: fileId,
        boundary_contract_id: boundaryContractId,
        materialization_id: materializationId,
        message: success ? "File saved successfully" : "Save materialization completed with warnings",
      };
    } catch (error) {
      console.error("Error saving materialization:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Save materialization failed",
      };
    }
  }

  /**
   * List files
   * 
   * Flow: Query via Runtime intent (list_files) - returns only saved files (workspace-scoped)
   */
  async listFiles(): Promise<ContentFile[]> {
    try {
      const platformState = this.getPlatformState();
      
      // ✅ FIX ISSUE 4: Use standardized session validation
      validateSession(platformState, "list files");

      // Submit list_files intent to Runtime
      const executionId = await platformState.submitIntent(
        "list_files",
        {
          tenant_id: platformState.state.session.tenantId,
          session_id: platformState.state.session.sessionId,
        }
      );

      // Track execution
      platformState.trackExecution(executionId);

      // Wait for execution to complete
      const maxAttempts = 10;
      let attempts = 0;
      
      while (attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 500));
        
        const status = await platformState.getExecutionStatus(executionId);
        
        if (status?.status === "completed") {
          // Extract files from execution artifacts
          const fileListArtifact = status.artifacts?.file_list;
          if (fileListArtifact?.semantic_payload?.files) {
            const backendFiles = fileListArtifact.semantic_payload.files;
            
            // Map backend response to ContentFile format
            return backendFiles.map((file: any) => ({
              id: file.file_id || file.uuid || '',
              name: file.file_name || file.ui_name || 'Unnamed File',
              type: file.file_type || file.mime_type || '',
              size: file.file_size || 0,
              uploadDate: file.created_at || new Date().toISOString(),
              status: file.materialization_pending ? 'pending' : (file.status || 'uploaded'),
              boundary_contract_id: file.boundary_contract_id,
              materialization_pending: file.materialization_pending === true,
              metadata: {
                ...file,
                file_type: file.file_type,
                mime_type: file.mime_type,
                boundary_contract_id: file.boundary_contract_id,
                materialization_pending: file.materialization_pending,
              },
            }));
          }
          // If no files in response, return empty array
          return [];
        } else if (status?.status === "failed") {
          throw new Error(status.error || "Failed to list files");
        }
        
        attempts++;
      }

      throw new Error("Timeout waiting for file list");
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
      
      // ✅ FIX ISSUE 4: Use standardized session validation
      validateSession(platformState, "parse file");

      // ✅ PHASE 2: Parameter validation before submitIntent
      if (!fileId) {
        throw new Error("file_id is required for parse_content");
      }
      if (!fileReference) {
        throw new Error("file_reference is required for parse_content");
      }

      // Check if file has content_type === DATA_MODEL and set parsing_type accordingly
      const files = platformState.state.realm.content.files || [];
      const file = files.find((f: any) => (f.uuid === fileId || f.file_id === fileId));
      const finalParseOptions = { ...parseOptions };
      
      if (file?.content_type === "data_model") {
        finalParseOptions.parsing_type = "data_model";
      }

      // Submit parse_content intent
      const executionId = await platformState.submitIntent(
        "parse_content",
        {
          file_id: fileId,
          file_reference: fileReference,
          copybook_reference: copybookReference,
          parse_options: finalParseOptions,
          parsing_type: finalParseOptions.parsing_type, // Also pass as top-level parameter for backend
        }
      );

      // Track execution
      platformState.trackExecution(executionId);

      // ✅ PHASE 2: Wait for execution to complete to get parsed_file_id
      const maxAttempts = 30; // Wait up to 15 seconds (30 * 500ms)
      let attempts = 0;
      let parsedFileId: string | undefined;
      let parsedFileReference: string | undefined;
      
      while (attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 500)); // Wait 500ms
        
        const status = await platformState.getExecutionStatus(executionId);
        
        if (status?.status === "completed") {
          // Extract parsed_file_id from execution artifacts
          const parsedFileArtifact = status.artifacts?.parsed_file;
          if (parsedFileArtifact?.semantic_payload) {
            parsedFileId = parsedFileArtifact.semantic_payload.parsed_file_id || fileId;
            parsedFileReference = parsedFileArtifact.semantic_payload.parsed_file_reference;
          } else {
            // Fallback: use fileId if no artifact structure
            parsedFileId = fileId;
          }
          break;
        } else if (status?.status === "failed") {
          throw new Error(status.error || "File parsing execution failed");
        }
        
        attempts++;
      }

      if (attempts >= maxAttempts) {
        throw new Error("Timeout waiting for file parsing to complete");
      }

      if (!parsedFileId) {
        throw new Error("Parsing completed but parsed_file_id not found in execution result");
      }

      return {
        success: true,
        parsed_file_id: parsedFileId,
        parsed_content: parsedFileReference ? { parsed_file_reference: parsedFileReference } : undefined,
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
      
      // ✅ FIX ISSUE 4: Use standardized session validation
      validateSession(platformState, "extract embeddings");

      // ✅ PHASE 2: Parameter validation before submitIntent
      if (!parsedFileId) {
        throw new Error("parsed_file_id is required for extract_embeddings");
      }
      if (!parsedFileReference) {
        throw new Error("parsed_file_reference is required for extract_embeddings");
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

      // ✅ PHASE 2: Wait for execution to complete to get embedding_id
      const maxAttempts = 30; // Wait up to 15 seconds (30 * 500ms)
      let attempts = 0;
      let embeddingId: string | undefined;
      let embeddingReference: string | undefined;
      
      while (attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 500)); // Wait 500ms
        
        const status = await platformState.getExecutionStatus(executionId);
        
        if (status?.status === "completed") {
          // Extract embedding_id from execution artifacts
          const embeddingArtifact = status.artifacts?.embeddings;
          if (embeddingArtifact?.semantic_payload) {
            embeddingId = embeddingArtifact.semantic_payload.embeddings_id;
            embeddingReference = embeddingArtifact.semantic_payload.embedding_reference || parsedFileReference;
          } else {
            // Fallback: use parsedFileReference if no artifact structure
            embeddingReference = parsedFileReference;
          }
          break;
        } else if (status?.status === "failed") {
          throw new Error(status.error || "Embedding extraction execution failed");
        }
        
        attempts++;
      }

      if (attempts >= maxAttempts) {
        throw new Error("Timeout waiting for embedding extraction to complete");
      }

      return {
        success: true,
        embedding_id: embeddingId,
        embedding_reference: embeddingReference || parsedFileReference,
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
      
      // ✅ PHASE 2: Use standardized session validation
      validateSession(platformState, "get parsed file");

      // ✅ PHASE 2: Parameter validation before submitIntent
      if (!fileId) {
        throw new Error("file_id is required for get_parsed_file");
      }
      if (!fileReference) {
        throw new Error("file_reference is required for get_parsed_file");
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
      
      // ✅ FIX ISSUE 4: Use standardized session validation
      validateSession(platformState, "get semantic interpretation");

      // ✅ FIX ISSUE 3: Parameter validation before submitIntent
      if (!fileId) {
        throw new Error("file_id is required for get_semantic_interpretation");
      }
      if (!fileReference) {
        throw new Error("file_reference is required for get_semantic_interpretation");
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

  /**
   * Wait for execution completion
   * 
   * Polls execution status until completion or failure
   * 
   * ✅ PHASE 5.5: Added for save_materialization intent-based flow
   */
  private async _waitForExecution(
    executionId: string,
    platformState: ReturnType<typeof usePlatformState>,
    maxWaitTime: number = 60000, // 60 seconds
    pollInterval: number = 1000 // 1 second
  ): Promise<ExecutionStatus> {
    const startTime = Date.now();
    
    while (Date.now() - startTime < maxWaitTime) {
      const status = await platformState.getExecutionStatus(executionId);
      
      if (!status) {
        throw new Error("Execution not found");
      }

      if (status.status === "completed" || status.status === "failed" || status.status === "cancelled") {
        return status;
      }

      // Wait before next poll
      await new Promise(resolve => setTimeout(resolve, pollInterval));
    }

    throw new Error("Execution timeout");
  }

  // ============================================
  // Phase 3: Artifact-Centric Methods
  // ============================================

  /**
   * Resolve artifact (authoritative resolution via State Surface)
   * 
   * Flow: Direct API call to Runtime → State Surface → Artifact Registry
   * 
   * This is the single source of truth for artifact resolution.
   * Returns full artifact record with materializations and lineage.
   */
  async resolveArtifact(
    artifactId: string,
    artifactType: string,
    tenantId: string
  ): Promise<ArtifactRecord> {
    try {
      const platformState = this.getPlatformState();
      validateSession(platformState, "resolve artifact");

      const url = getApiEndpointUrl('/api/artifact/resolve');
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          artifact_id: artifactId,
          artifact_type: artifactType,
          tenant_id: tenantId,
        }),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Failed to resolve artifact' }));
        throw new Error(error.detail || `Failed to resolve artifact: ${response.statusText}`);
      }

      const data = await response.json();
      return data.artifact;
    } catch (error) {
      console.error("Error resolving artifact:", error);
      throw error;
    }
  }

  /**
   * List artifacts (discovery/indexing via Supabase)
   * 
   * Flow: Direct API call to Runtime → RegistryAbstraction → artifact_index
   * 
   * Returns artifact metadata (not content) filtered by:
   * - artifact_type
   * - lifecycle_state (default: READY)
   * - eligible_for (next intent that needs this artifact)
   * 
   * For actual artifact content, use resolveArtifact().
   */
  async listArtifacts(filters: {
    tenantId: string;
    artifactType?: string;
    lifecycleState?: string;
    eligibleFor?: string; // Next intent that needs this artifact
    limit?: number;
    offset?: number;
  }): Promise<ArtifactListResponse> {
    try {
      const platformState = this.getPlatformState();
      validateSession(platformState, "list artifacts");

      const url = getApiEndpointUrl('/api/artifact/list');
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tenant_id: filters.tenantId,
          artifact_type: filters.artifactType,
          lifecycle_state: filters.lifecycleState || 'READY',
          eligible_for: filters.eligibleFor,
          limit: filters.limit || 100,
          offset: filters.offset || 0,
        }),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Failed to list artifacts' }));
        throw new Error(error.detail || `Failed to list artifacts: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error("Error listing artifacts:", error);
      throw error;
    }
  }

  /**
   * Get pending intents (for UI display)
   * 
   * Flow: Direct API call to Runtime → RegistryAbstraction → intent_executions
   * 
   * Used to show "files with pending parse intents" and similar UI features.
   * Returns pending intents with context (ingestion_profile lives here).
   */
  async getPendingIntents(filters: {
    tenantId: string;
    targetArtifactId?: string;
    intentType?: string;
  }): Promise<PendingIntentListResponse> {
    try {
      const platformState = this.getPlatformState();
      validateSession(platformState, "get pending intents");

      const url = getApiEndpointUrl('/api/intent/pending/list');
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tenant_id: filters.tenantId,
          target_artifact_id: filters.targetArtifactId,
          intent_type: filters.intentType,
        }),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Failed to list pending intents' }));
        throw new Error(error.detail || `Failed to list pending intents: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error("Error getting pending intents:", error);
      throw error;
    }
  }

  /**
   * Create pending intent (where ingestion_profile lives)
   * 
   * Flow: Direct API call to Runtime → RegistryAbstraction → intent_executions
   * 
   * This enables resumable workflows - user can upload file, select ingestion_profile,
   * and resume parsing later (even in a different session).
   * 
   * The ingestion_profile is stored in the intent context, not on the artifact.
   */
  async createPendingIntent(
    intentType: string,
    targetArtifactId: string,
    context: {
      ingestion_profile?: string;
      parse_options?: Record<string, any>;
      [key: string]: any;
    },
    tenantId: string,
    userId?: string,
    sessionId?: string
  ): Promise<{ intentId: string; status: string }> {
    try {
      const platformState = this.getPlatformState();
      validateSession(platformState, "create pending intent");

      const url = getApiEndpointUrl('/api/intent/pending/create');
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          intent_type: intentType,
          target_artifact_id: targetArtifactId,
          context: context, // ingestion_profile lives here
          tenant_id: tenantId,
          user_id: userId || platformState.state.session.userId,
          session_id: sessionId || platformState.state.session.sessionId,
        }),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Failed to create pending intent' }));
        throw new Error(error.detail || `Failed to create pending intent: ${response.statusText}`);
      }

      const data = await response.json();
      return {
        intentId: data.intent_id,
        status: data.status,
      };
    } catch (error) {
      console.error("Error creating pending intent:", error);
      throw error;
    }
  }

  // ============================================
  // Journey-Based Methods (compose_journey pattern)
  // ============================================

  /**
   * Upload and materialize file using compose_journey pattern
   * 
   * This is an alternative to calling uploadFile() + saveMaterialization() separately.
   * Uses the compose_journey intent to execute the complete FileUploadMaterialization journey.
   * 
   * Flow: submitIntent("compose_journey") → Runtime → ContentSolution → FileUploadMaterializationJourney
   */
  async uploadAndMaterializeJourney(
    file: File,
    contentType?: string,
    fileType?: string
  ): Promise<UploadResponse> {
    try {
      const platformState = this.getPlatformState();
      validateSession(platformState, "upload and materialize journey");

      // Convert file to base64
      const fileBuffer = await file.arrayBuffer();
      const fileContentBase64 = btoa(String.fromCharCode(...new Uint8Array(fileBuffer)));

      // Submit compose_journey intent for file_upload_materialization journey
      const executionId = await platformState.submitIntent(
        "compose_journey",
        {
          journey_id: "file_upload_materialization",
          journey_params: {
            file_content: fileContentBase64,
            file_name: file.name,
            content_type: contentType || "unstructured",
            file_type: fileType || this._inferFileType(file.name),
            auto_save: true, // Complete journey in one step
          },
        }
      );

      // Track execution
      platformState.trackExecution(executionId);

      // Wait for journey completion
      const maxAttempts = 30;
      let attempts = 0;

      while (attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 500));
        const status = await platformState.getExecutionStatus(executionId);

        if (status?.status === "completed") {
          const fileArtifact = status.artifacts?.file;
          const semanticPayload = fileArtifact?.semantic_payload || {};

          return {
            success: true,
            file_id: semanticPayload.artifact_id,
            boundary_contract_id: semanticPayload.boundary_contract_id,
            materialization_pending: false,
            file: {
              id: semanticPayload.artifact_id || "",
              name: file.name,
              type: file.type,
              size: file.size,
              uploadDate: new Date().toISOString(),
              status: "uploaded",
            },
          };
        } else if (status?.status === "failed") {
          throw new Error(status.error || "Journey execution failed");
        }
        attempts++;
      }

      throw new Error("Timeout waiting for journey completion");
    } catch (error) {
      console.error("Error in uploadAndMaterializeJourney:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Journey failed",
      };
    }
  }

  /**
   * Parse file using compose_journey pattern
   * 
   * Uses the FileParsingJourney to parse content and save parsed artifact.
   */
  async parseFileJourney(
    artifactId: string,
    pendingJourneyId?: string
  ): Promise<ParseResponse> {
    try {
      const platformState = this.getPlatformState();
      validateSession(platformState, "parse file journey");

      const executionId = await platformState.submitIntent(
        "compose_journey",
        {
          journey_id: "file_parsing",
          journey_params: {
            artifact_id: artifactId,
            pending_journey_id: pendingJourneyId,
            auto_save: true,
          },
        }
      );

      platformState.trackExecution(executionId);

      const maxAttempts = 30;
      let attempts = 0;

      while (attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 500));
        const status = await platformState.getExecutionStatus(executionId);

        if (status?.status === "completed") {
          const parsedArtifact = status.artifacts?.parsed_content;
          return {
            success: true,
            parsed_file_id: parsedArtifact?.semantic_payload?.parsed_artifact_id,
            parsed_content: parsedArtifact,
          };
        } else if (status?.status === "failed") {
          throw new Error(status.error || "Parsing journey failed");
        }
        attempts++;
      }

      throw new Error("Timeout waiting for parsing journey");
    } catch (error) {
      console.error("Error in parseFileJourney:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Parsing journey failed",
      };
    }
  }

  /**
   * List available journeys in the Content Solution
   */
  async listContentJourneys(): Promise<{ journeys: Array<{ journey_id: string; journey_name: string }> }> {
    try {
      const platformState = this.getPlatformState();
      validateSession(platformState, "list content journeys");

      // For now, return static list (could be fetched from backend)
      return {
        journeys: [
          { journey_id: "file_upload_materialization", journey_name: "File Upload & Materialization" },
          { journey_id: "file_parsing", journey_name: "File Parsing" },
          { journey_id: "deterministic_embedding", journey_name: "Deterministic Embedding Creation" },
          { journey_id: "file_management", journey_name: "File Management" },
        ],
      };
    } catch (error) {
      console.error("Error listing journeys:", error);
      throw error;
    }
  }

  /**
   * Helper: Infer file type from filename
   */
  private _inferFileType(filename: string): string {
    const ext = filename.split('.').pop()?.toLowerCase() || "";
    const typeMap: Record<string, string> = {
      pdf: "pdf",
      csv: "csv",
      json: "json",
      xml: "xml",
      txt: "txt",
      xlsx: "xlsx",
      xls: "xls",
      doc: "doc",
      docx: "docx",
    };
    return typeMap[ext] || "unknown";
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
