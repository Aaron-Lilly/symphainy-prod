/**
 * AGUI (Agentic Graphical User Interface) Types
 * 
 * ✅ PHASE 2.5: AGUI Native Integration
 * 
 * AGUI is the native interaction model for the platform.
 * It represents experience state (journey, artifacts, workflows) that compiles to Intent.
 * 
 * Architecture:
 * - AGUI is experience semantics (frontend)
 * - Intent is execution semantics (backend)
 * - Frontend compiles AGUI → Intent
 * - Backend validates and executes Intent
 */

// ============================================================================
// CORE AGUI TYPES
// ============================================================================

/**
 * Artifact - Represents a piece of data/work in the journey
 */
export interface Artifact {
  id: string;
  type: string; // e.g., "file", "code", "document", "workflow"
  name: string;
  state: ArtifactState;
  metadata?: Record<string, any>;
  created_at?: string;
  updated_at?: string;
}

/**
 * Artifact State - Lifecycle state of an artifact
 */
export enum ArtifactState {
  Ephemeral = "ephemeral",           // Temporary, not persisted
  WorkingMaterial = "working_material", // In progress
  RecordOfFact = "record_of_fact",   // Completed, persisted
  PurposeBoundOutcome = "purpose_bound_outcome", // Delivered
  PlatformDNA = "platform_dna",     // Canonical, reusable
}

/**
 * Journey Step - A step in the journey
 */
export interface JourneyStep {
  id: string;
  name: string;
  description?: string;
  status: JourneyStepStatus;
  allowed_next_steps?: string[]; // IDs of allowed next steps
  required_artifacts?: string[]; // IDs of required artifacts
  metadata?: Record<string, any>;
}

/**
 * Journey Step Status
 */
export enum JourneyStepStatus {
  Pending = "pending",
  Active = "active",
  Completed = "completed",
  Skipped = "skipped",
  Blocked = "blocked",
}

/**
 * Workflow - A workflow definition
 */
export interface Workflow {
  id: string;
  name: string;
  description?: string;
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  state: WorkflowState;
  metadata?: Record<string, any>;
}

/**
 * Workflow Node
 */
export interface WorkflowNode {
  id: string;
  type: string; // e.g., "task", "decision", "parallel"
  label: string;
  data?: Record<string, any>;
  position?: { x: number; y: number };
}

/**
 * Workflow Edge
 */
export interface WorkflowEdge {
  id: string;
  source: string; // Node ID
  target: string; // Node ID
  label?: string;
  condition?: string;
}

/**
 * Workflow State
 */
export enum WorkflowState {
  Draft = "draft",
  Active = "active",
  Completed = "completed",
  Paused = "paused",
  Cancelled = "cancelled",
}

// ============================================================================
// AGUI STATE
// ============================================================================

/**
 * AGUI State - Complete state of the experience layer
 */
export interface AGUIState {
  journey: {
    id: string;
    name: string;
    current_step: string; // Step ID
    steps: JourneyStep[];
  };
  inputs: {
    artifacts: Artifact[];
    parameters: Record<string, any>;
  };
  workflows: Workflow[];
  outputs: {
    artifacts: Artifact[];
    results: Record<string, any>;
  };
  metadata: {
    created_at: string;
    updated_at: string;
    session_id: string;
    tenant_id?: string;
    user_id?: string;
  };
}

// ============================================================================
// AGUI MUTATIONS
// ============================================================================

/**
 * AGUI Mutation - A change to AGUI state
 */
export interface AGUIMutation {
  // Journey mutations
  journey?: {
    set_step?: string; // Step ID
    add_step?: JourneyStep;
    update_step?: { id: string; updates: Partial<JourneyStep> };
    remove_step?: string; // Step ID
  };
  
  // Input mutations
  inputs?: {
    add_artifact?: Artifact;
    update_artifact?: { id: string; updates: Partial<Artifact> };
    remove_artifact?: string; // Artifact ID
    set_parameter?: { key: string; value: any };
    remove_parameter?: string; // Parameter key
  };
  
  // Workflow mutations
  workflows?: {
    add_workflow?: Workflow;
    update_workflow?: { id: string; updates: Partial<Workflow> };
    remove_workflow?: string; // Workflow ID
  };
  
  // Output mutations
  outputs?: {
    add_artifact?: Artifact;
    update_artifact?: { id: string; updates: Partial<Artifact> };
    remove_artifact?: string; // Artifact ID
    set_result?: { key: string; value: any };
    remove_result?: string; // Result key
  };
  
  // Metadata mutations
  metadata?: {
    update?: Record<string, any>;
  };
}

// ============================================================================
// INTENT COMPILATION
// ============================================================================

/**
 * Intent Compilation Result
 */
export interface IntentCompilationResult {
  intent_type: string;
  parameters: Record<string, any>;
  metadata?: Record<string, any>;
  validation_errors?: string[];
}

/**
 * AGUI Validation Error
 */
export interface AGUIValidationError {
  field: string;
  message: string;
  code?: string;
}
