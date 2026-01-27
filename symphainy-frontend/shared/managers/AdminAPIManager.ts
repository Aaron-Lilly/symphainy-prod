/**
 * Admin API Manager
 * 
 * Centralized client for Admin Dashboard API calls (all 3 views).
 * 
 * Architecture:
 * - Direct REST API calls to Experience Plane Admin Dashboard endpoints
 * - No intent submission (Admin Dashboard is not realm-based)
 * - Access control handled by backend (Security Guard SDK)
 * 
 * Views:
 * 1. Control Room - Platform observability
 * 2. Developer View - Platform SDK documentation and tools
 * 3. Business User View - Solution composition and feature requests
 */

import { getApiEndpointUrl } from '@/shared/config/api-config';

// ============================================
// Control Room Types
// ============================================

export interface PlatformStatistics {
  total_intents: number;
  successful_intents: number;
  failed_intents: number;
  success_rate: number;
  average_execution_time: number;
  intent_type_distribution: Record<string, number>;
  active_sessions: number;
  total_sessions: number;
  realm_health: Record<string, {
    status: 'healthy' | 'degraded' | 'unhealthy';
    intent_count: number;
    response_time: number;
    error_rate: number;
  }>;
}

export interface ExecutionMetrics {
  time_range: string;
  total_executions: number;
  successful_executions: number;
  failed_executions: number;
  average_execution_time: number;
  p95_execution_time: number;
  p99_execution_time: number;
  throughput: number;
  error_rate: number;
  executions_by_type: Record<string, number>;
}

export interface RealmHealth {
  realms: Record<string, {
    status: 'healthy' | 'degraded' | 'unhealthy';
    intent_count: number;
    response_time_ms: number;
    error_rate: number;
    last_activity: string;
  }>;
  overall_health: 'healthy' | 'degraded' | 'unhealthy';
}

export interface SolutionRegistryStatus {
  total_solutions: number;
  active_solutions: number;
  inactive_solutions: number;
  solutions_by_domain: Record<string, number>;
  solution_health: Record<string, {
    status: 'active' | 'inactive' | 'error';
    execution_count: number;
    success_rate: number;
  }>;
}

export interface SystemHealth {
  runtime: {
    status: 'healthy' | 'degraded' | 'unhealthy';
    wal_health: 'healthy' | 'degraded' | 'unhealthy';
    state_surface_health: 'healthy' | 'degraded' | 'unhealthy';
  };
  infrastructure: {
    database: {
      arangodb: 'healthy' | 'degraded' | 'unhealthy';
      redis: 'healthy' | 'degraded' | 'unhealthy';
    };
    storage: {
      gcs: 'healthy' | 'degraded' | 'unhealthy';
      supabase: 'healthy' | 'degraded' | 'unhealthy';
    };
    telemetry: 'healthy' | 'degraded' | 'unhealthy';
  };
  observability: {
    opentelemetry: 'healthy' | 'degraded' | 'unhealthy';
    prometheus: 'healthy' | 'degraded' | 'unhealthy';
    tempo: 'healthy' | 'degraded' | 'unhealthy';
  };
}

// ============================================
// Developer View Types
// ============================================

export interface DocumentationSection {
  id: string;
  title: string;
  content: string;
  subsections?: DocumentationSection[];
}

export interface Documentation {
  sections: DocumentationSection[];
  architecture_overview?: {
    runtime: string;
    civic_systems: string;
    domains: string;
    foundations: string;
  };
  api_documentation?: {
    solution_sdk: string;
    realm_sdk: string;
    smart_city_sdk: string;
    experience_sdk: string;
    agentic_sdk: string;
  };
}

export interface CodeExample {
  id: string;
  title: string;
  description: string;
  category: string;
  code: string;
  language: string;
  related_patterns?: string[];
}

export interface CodeExamples {
  examples: CodeExample[];
  categories: string[];
}

export interface Pattern {
  id: string;
  title: string;
  description: string;
  category: 'realm' | 'solution' | 'agent' | 'public_works';
  example_code?: string;
  best_practices?: string[];
}

export interface Patterns {
  patterns: Pattern[];
  categories: string[];
}

export interface SolutionValidationRequest {
  solution_config: Record<string, any>;
}

export interface SolutionValidationResponse {
  valid: boolean;
  errors?: string[];
  warnings?: string[];
  preview?: {
    structure: Record<string, any>;
    estimated_complexity: 'low' | 'medium' | 'high';
  };
}

export interface FeatureRequestSubmission {
  title: string;
  description: string;
  category?: string;
  metadata?: Record<string, any>;
}

export interface FeatureRequestResponse {
  success: boolean;
  request_id?: string;
  status?: 'submitted' | 'coming_soon';
  message?: string;
}

// ============================================
// Business User View Types
// ============================================

export interface CompositionGuide {
  steps: Array<{
    step_number: number;
    title: string;
    description: string;
    actions: string[];
  }>;
  domain_selection: {
    available_domains: string[];
    domain_descriptions: Record<string, string>;
  };
  intent_selection: {
    available_intents: Record<string, string[]>;
    intent_descriptions: Record<string, string>;
  };
}

export interface SolutionTemplate {
  id: string;
  name: string;
  description: string;
  domain: string;
  intents: string[];
  complexity: 'low' | 'medium' | 'high';
  customizable: boolean;
}

export interface SolutionTemplates {
  templates: SolutionTemplate[];
  categories: string[];
}

export interface SolutionCompositionRequest {
  solution_config: Record<string, any>;
}

export interface SolutionCompositionResponse {
  success: boolean;
  solution_id?: string;
  solution_reference?: string;
  errors?: string[];
  warnings?: string[];
}

export interface BusinessFeatureRequest {
  title: string;
  description: string;
  business_need: string;
  priority?: 'low' | 'medium' | 'high';
  metadata?: Record<string, any>;
}

export interface BusinessFeatureRequestResponse {
  success: boolean;
  request_id?: string;
  message?: string;
}

// ============================================
// Admin API Manager Class
// ============================================

import { usePlatformState } from '@/shared/state/PlatformStateProvider';
import { validateSession } from '@/shared/utils/sessionValidation';

export class AdminAPIManager {
  private getPlatformState: () => ReturnType<typeof usePlatformState>;

  constructor(getPlatformState?: () => ReturnType<typeof usePlatformState>) {
    this.getPlatformState = getPlatformState || (() => {
      throw new Error("PlatformStateProvider not available. Use AdminAPIManager with usePlatformState hook.");
    });
  }

  /**
   * Helper method to submit admin intent and wait for execution
   * 
   * ✅ PHASE 5.6.5: Intent-based API pattern for admin operations
   */
  private async _submitAdminIntent(
    intentType: string,
    parameters: Record<string, any> = {}
  ): Promise<any> {
    const platformState = this.getPlatformState();
    
    // ✅ FIX ISSUE 4: Use standardized session validation
    validateSession(platformState, `admin operation: ${intentType}`);

    // Submit intent via Experience Plane Client
    const execution = await platformState.submitIntent(intentType, parameters);

    // Wait for execution completion
    const result = await this._waitForExecution(execution, platformState);

    if (result.status === "completed" && result.artifacts) {
      return result.artifacts;
    } else {
      throw new Error(result.error || `Failed to execute ${intentType}`);
    }
  }

  /**
   * Wait for execution completion
   */
  private async _waitForExecution(
    executionId: string,
    platformState: ReturnType<typeof usePlatformState>,
    maxWaitTime: number = 60000,
    pollInterval: number = 1000
  ): Promise<any> {
    const startTime = Date.now();
    
    while (Date.now() - startTime < maxWaitTime) {
      const status = await platformState.getExecutionStatus(executionId);
      
      if (!status) {
        throw new Error("Execution not found");
      }

      if (status.status === "completed" || status.status === "failed" || status.status === "cancelled") {
        return status;
      }

      await new Promise(resolve => setTimeout(resolve, pollInterval));
    }

    throw new Error("Execution timeout");
  }

  // ============================================
  // Control Room API Methods
  // ============================================

  /**
   * Get platform statistics (admin_get_platform_statistics intent)
   * 
   * ✅ PHASE 5.6.5: Migrated to intent-based API
   */
  async getPlatformStatistics(): Promise<PlatformStatistics> {
    const artifacts = await this._submitAdminIntent('admin_get_platform_statistics');
    return artifacts.platform_statistics;
  }

  /**
   * Get execution metrics (admin_get_execution_metrics intent)
   * 
   * ✅ PHASE 5.6.5: Migrated to intent-based API
   */
  async getExecutionMetrics(timeRange: string = '1h'): Promise<ExecutionMetrics> {
    const artifacts = await this._submitAdminIntent('admin_get_execution_metrics', { time_range: timeRange });
    return artifacts.execution_metrics;
  }

  /**
   * Get realm health (admin_get_realm_health intent)
   * 
   * ✅ PHASE 5.6.5: Migrated to intent-based API
   */
  async getRealmHealth(): Promise<RealmHealth> {
    const artifacts = await this._submitAdminIntent('admin_get_realm_health');
    return artifacts.realm_health;
  }

  /**
   * Get solution registry status (admin_get_solution_registry_status intent)
   * 
   * ✅ PHASE 5.6.5: Migrated to intent-based API
   */
  async getSolutionRegistryStatus(): Promise<SolutionRegistryStatus> {
    const artifacts = await this._submitAdminIntent('admin_get_solution_registry_status');
    return artifacts.solution_registry_status;
  }

  /**
   * Get system health (admin_get_system_health intent)
   * 
   * ✅ PHASE 5.6.5: Migrated to intent-based API
   */
  async getSystemHealth(): Promise<SystemHealth> {
    const artifacts = await this._submitAdminIntent('admin_get_system_health');
    return artifacts.system_health;
  }

  // ============================================
  // Developer View API Methods
  // ============================================

  /**
   * Get Platform SDK documentation (admin_get_documentation intent)
   * 
   * ✅ PHASE 5.6.5: Migrated to intent-based API
   */
  async getDocumentation(section?: string): Promise<Documentation> {
    const artifacts = await this._submitAdminIntent('admin_get_documentation', { section });
    return artifacts.documentation;
  }

  /**
   * Get code examples (admin_get_code_examples intent)
   * 
   * ✅ PHASE 5.6.5: Migrated to intent-based API
   */
  async getCodeExamples(category?: string): Promise<CodeExamples> {
    const artifacts = await this._submitAdminIntent('admin_get_code_examples', { category });
    return artifacts.code_examples;
  }

  /**
   * Get patterns and best practices (admin_get_patterns intent)
   * 
   * ✅ PHASE 5.6.5: Migrated to intent-based API
   */
  async getPatterns(): Promise<Patterns> {
    const artifacts = await this._submitAdminIntent('admin_get_patterns');
    return artifacts.patterns;
  }

  /**
   * Validate solution configuration (admin_validate_solution intent)
   * 
   * ✅ PHASE 5.6.5: Migrated to intent-based API
   */
  async validateSolution(request: SolutionValidationRequest): Promise<SolutionValidationResponse> {
    const artifacts = await this._submitAdminIntent('admin_validate_solution', request);
    return artifacts.solution_validation;
  }

  /**
   * Preview solution structure (admin_preview_solution intent)
   * 
   * ✅ PHASE 5.6.5: Migrated to intent-based API
   */
  async previewSolution(request: SolutionValidationRequest): Promise<SolutionValidationResponse> {
    const artifacts = await this._submitAdminIntent('admin_preview_solution', request);
    return artifacts.solution_preview;
  }

  /**
   * Submit feature request (admin_submit_feature_request intent)
   * 
   * ✅ PHASE 5.6.5: Migrated to intent-based API
   */
  async submitFeatureRequest(request: FeatureRequestSubmission): Promise<FeatureRequestResponse> {
    const artifacts = await this._submitAdminIntent('admin_submit_feature_request', request);
    return artifacts.feature_request;
  }

  // ============================================
  // Business User View API Methods
  // ============================================

  /**
   * Get solution composition guide (admin_get_composition_guide intent)
   * 
   * ✅ PHASE 5.6.5: Migrated to intent-based API
   */
  async getCompositionGuide(): Promise<CompositionGuide> {
    const artifacts = await this._submitAdminIntent('admin_get_composition_guide');
    return artifacts.composition_guide;
  }

  /**
   * Get solution templates (admin_get_solution_templates intent)
   * 
   * ✅ PHASE 5.6.5: Migrated to intent-based API
   */
  async getSolutionTemplates(): Promise<SolutionTemplates> {
    const artifacts = await this._submitAdminIntent('admin_get_solution_templates');
    return artifacts.solution_templates;
  }

  /**
   * Compose solution (admin_compose_solution intent)
   * 
   * ✅ PHASE 5.6.5: Migrated to intent-based API
   */
  async composeSolution(request: SolutionCompositionRequest): Promise<SolutionCompositionResponse> {
    const artifacts = await this._submitAdminIntent('admin_compose_solution', request);
    return artifacts.solution_composition;
  }

  /**
   * Register composed solution (admin_register_solution intent)
   * 
   * ✅ PHASE 5.6.5: Migrated to intent-based API
   */
  async registerSolution(request: SolutionCompositionRequest): Promise<SolutionCompositionResponse> {
    const artifacts = await this._submitAdminIntent('admin_register_solution', request);
    return artifacts.solution_registration;
  }

  /**
   * Submit business feature request (admin_submit_business_feature_request intent)
   * 
   * ✅ PHASE 5.6.5: Migrated to intent-based API
   */
  async submitBusinessFeatureRequest(request: BusinessFeatureRequest): Promise<BusinessFeatureRequestResponse> {
    const artifacts = await this._submitAdminIntent('admin_submit_business_feature_request', request);
    return artifacts.business_feature_request;
  }
}

// Factory function for use in components
export function useAdminAPIManager(): AdminAPIManager {
  const platformState = usePlatformState();
  return new AdminAPIManager(() => platformState);
}
