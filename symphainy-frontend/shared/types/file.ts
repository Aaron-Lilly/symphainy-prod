// Content Type (Primary - aligns with backend)
export enum ContentType {
  STRUCTURED = "structured",
  UNSTRUCTURED = "unstructured",
  HYBRID = "hybrid",
  WORKFLOW_SOP = "workflow_sop",  // ⭐ NEW: Workflow & SOP Documentation
  DATA_MODEL = "data_model"  // ⭐ NEW: Target Data Model (JSON Schema, YAML)
}

// File Type Category (Secondary)
export enum FileTypeCategory {
  // Structured
  SPREADSHEET = "spreadsheet",
  BINARY = "binary",
  DATA_FORMAT = "data_format",
  DATA_MODEL = "data_model",  // Data model schemas (JSON Schema, YAML)
  
  // Unstructured
  DOCUMENT = "document",
  PDF = "pdf",
  IMAGE = "image",
  SOP_WORKFLOW = "sop_workflow",  // Legacy - kept for backward compatibility
  
  // Workflow/SOP (NEW)
  WORKFLOW = "workflow",  // ⭐ NEW: Workflow files (.bpmn, .json, .drawio)
  SOP = "sop",  // ⭐ NEW: SOP documents (.docx, .pdf, .txt, .md)
  
  // Hybrid
  COMPLEX_DOCUMENT = "complex_document"
}

// File Type Configuration
export interface FileTypeConfig {
  contentType: ContentType;
  category: FileTypeCategory;
  label: string;
  extensions: string[];
  mimeTypes: string[];
  requiresCopybook?: boolean;
  processingPillar?: "content_pillar" | "operations_pillar" | "journey_pillar";
  parsingType?: string;  // ⭐ NEW: Special parsing type (e.g., "data_model")
  description?: string;
  icon?: string;
}

// File Type Configurations
export const FILE_TYPE_CONFIGS: FileTypeConfig[] = [
  // Structured Data
  {
    contentType: ContentType.STRUCTURED,
    category: FileTypeCategory.SPREADSHEET,
    label: "Spreadsheet",
    extensions: [".csv", ".xlsx", ".xls", ".parquet"],
    mimeTypes: [
      "text/csv",
      "application/vnd.ms-excel",
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      "application/parquet"
    ],
    icon: "📈"
  },
  {
    contentType: ContentType.STRUCTURED,
    category: FileTypeCategory.BINARY,
    label: "Binary File",
    extensions: [".bin", ".dat"],
    mimeTypes: ["application/octet-stream"],
    requiresCopybook: true,
    description: "Requires copybook file for parsing",
    icon: "💾"
  },
  {
    contentType: ContentType.STRUCTURED,
    category: FileTypeCategory.DATA_FORMAT,
    label: "Data Format",
    extensions: [".json", ".xml", ".yaml"],
    mimeTypes: [
      "application/json",
      "application/xml",
      "application/yaml"
    ],
    icon: "📋"
  },
  
  // Unstructured Documents
  {
    contentType: ContentType.UNSTRUCTURED,
    category: FileTypeCategory.DOCUMENT,
    label: "Document",
    extensions: [".docx", ".doc", ".txt", ".md", ".rtf"],
    mimeTypes: [
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "application/msword",
      "text/plain",
      "text/markdown",
      "application/rtf"
    ],
    icon: "📝"
  },
  {
    contentType: ContentType.UNSTRUCTURED,
    category: FileTypeCategory.PDF,
    label: "PDF",
    extensions: [".pdf"],
    mimeTypes: ["application/pdf"],
    icon: "📑"
  },
  {
    contentType: ContentType.UNSTRUCTURED,
    category: FileTypeCategory.IMAGE,
    label: "Image",
    extensions: [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
    mimeTypes: [
      "image/jpeg",
      "image/png",
      "image/gif",
      "image/bmp",
      "image/svg+xml"
    ],
    icon: "🖼️"
  },
  {
    contentType: ContentType.UNSTRUCTURED,
    category: FileTypeCategory.SOP_WORKFLOW,
    label: "SOP/Workflow",
    extensions: [".docx", ".pdf", ".bpmn", ".txt", ".json"],
    mimeTypes: [
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "application/pdf",
      "application/xml",
      "text/plain",
      "application/json"
    ],
    processingPillar: "operations_pillar",
    description: "Uploaded in Content Pillar, parsed in Operations Pillar",
    icon: "⚙️"
  },
  
  // ⭐ NEW: Workflow & SOP Documentation (separate categories)
  {
    contentType: ContentType.WORKFLOW_SOP,
    category: FileTypeCategory.WORKFLOW,
    label: "Workflow File",
    extensions: [".bpmn", ".json", ".drawio"],
    mimeTypes: [
      "application/xml",  // BPMN
      "application/json",
      "application/x-drawio"
    ],
    processingPillar: "operations_pillar",
    description: "Workflow diagram files (BPMN, JSON, Draw.io)",
    icon: "🔄"
  },
  {
    contentType: ContentType.WORKFLOW_SOP,
    category: FileTypeCategory.SOP,
    label: "SOP Document",
    extensions: [".docx", ".pdf", ".txt", ".md"],
    mimeTypes: [
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "application/pdf",
      "text/plain",
      "text/markdown"
    ],
    processingPillar: "operations_pillar",
    description: "Standard Operating Procedure documents",
    icon: "📋"
  },
  
  // Hybrid Content
  {
    contentType: ContentType.HYBRID,
    category: FileTypeCategory.COMPLEX_DOCUMENT,
    label: "Complex Document",
    extensions: [".docx", ".pdf"],
    mimeTypes: [
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "application/pdf"
    ],
    description: "Documents with embedded structured data",
    icon: "🔀"
  },
  
  // ⭐ NEW: Data Model (Target Data Model Schemas)
  {
    contentType: ContentType.DATA_MODEL,
    category: FileTypeCategory.DATA_MODEL,
    label: "Data Model",
    extensions: [".json", ".yaml", ".yml"],
    mimeTypes: [
      "application/json",
      "application/yaml",
      "text/yaml"
    ],
    parsingType: "data_model",  // Special parsing type for target schemas
    description: "Target data model schemas (JSON Schema, YAML). Used for source-to-target matching in Insights pillar.",
    icon: "📊"
  }
];

// Legacy FileType enum (kept for backward compatibility)
export enum FileType {
  Structured = "structured",
  Binary = "binary",
  Image = "image",
  Pdf = "pdf",
  Text = "text",
  Document = "document",
  SopWorkflow = "sop_workflow",
}

export enum FileStatus {
  Uploaded = "uploaded",
  Parsing = "parsing",
  Parsed = "parsed",
  Validated = "validated",
}

export enum LinkType {
  ParsedFrom = "parsed_from",
  VariantOf = "variant_of",
  AlternateFormat = "alternate_format",
}

export enum AuthorType {
  Agent = "agent",
  Human = "human",
}

/**
 * Additional metadata for file records
 */
export interface FileMetadataExtra {
  parsing_status?: string;
  parsing_type?: string;
  schema_detected?: boolean;
  row_count?: number;
  column_count?: number;
  custom_fields?: Record<string, unknown>;
}

/**
 * Insights derived from file analysis
 */
export interface FileInsights {
  summary?: string;
  key_findings?: string[];
  data_quality_score?: number;
  analysis_type?: string;
  visualizations?: Array<{ type: string; config: Record<string, unknown> }>;
}

// File metadata type (matches FileMetadataResponse)
export interface FileMetadata {
  uuid: string;
  file_id?: string;  // Alias for uuid
  user_id?: string | null;
  team_id?: string;
  ui_name: string;  // User-friendly name
  original_filename?: string;  // Full original filename
  file_extension?: string;  // Extension with dot
  file_type: string;  // Extension without dot (legacy compatibility with FileType enum)
  content_type?: ContentType;  // structured/unstructured/hybrid
  file_type_category?: FileTypeCategory;  // document/spreadsheet/etc.
  mime_type?: string;
  file_size?: number;  // File size in bytes
  upload_timestamp?: string;  // Upload timestamp
  original_path: string;
  parsed_path?: string;
  status: FileStatus;
  metadata?: FileMetadataExtra;
  insights?: FileInsights;
  rejection_reason?: string;
  created_at: string;
  updated_at: string;
  deleted: boolean;
  boundary_contract_id?: string;  // NEW: Boundary contract ID for materialization
  materialization_pending?: boolean;  // NEW: Whether materialization is pending (needs save)
}

// API Upload request type (for backend communication)
export interface ApiUploadRequest {
  ui_name: string;
  file_type: FileType;
  mime_type?: string;
  original_path: string;
  metadata?: FileMetadataExtra;
}

// Component Upload request type (for UI state management)
export interface ComponentUploadRequest {
  file: File;
  fileType: FileType;
  copybookFile?: File;
  sessionToken?: string;
  userId?: string;
}

// File upload state type (for component state management)
export interface FileUploadState {
  file: File;
  fileType: FileType;
  copybookFile?: File;
  sessionToken?: string;
  userId?: string;
}

// Approve/reject request types removed - no longer needed
