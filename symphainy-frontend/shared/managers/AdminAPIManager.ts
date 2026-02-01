/**
 * Admin API Manager
 * 
 * Centralized client for Admin Dashboard API calls (all 3 views).
 * 
 * Architecture (Post-Modernization):
 * - Direct REST API calls to Admin Dashboard endpoints
 * - Backend handles intent submission to Control Tower capability
 * - Passes session_id and tenant_id as query parameters
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

/**
 * Admin API Manager - REST-based client for Admin Dashboard
 * 
 * Post-Modernization Pattern:
 * - Frontend calls REST endpoints directly
 * - Backend handles intent submission to Control Tower
 * - session_id and tenant_id passed as query parameters
 */
export class AdminAPIManager {
  private sessionId: string | null = null;
  private tenantId: string | null = null;

  constructor(sessionId?: string, tenantId?: string) {
    this.sessionId = sessionId || null;
    this.tenantId = tenantId || null;
  }

  /**
   * Update session and tenant context
   */
  setContext(sessionId: string, tenantId: string): void {
    this.sessionId = sessionId;
    this.tenantId = tenantId;
  }

  /**
   * Build URL with query parameters including session_id and tenant_id
   */
  private buildUrl(endpoint: string, params: Record<string, any> = {}): string {
    const url = new URL(getApiEndpointUrl(endpoint));
    
    // Add session_id and tenant_id if available
    if (this.sessionId) {
      url.searchParams.set('session_id', this.sessionId);
    }
    if (this.tenantId) {
      url.searchParams.set('tenant_id', this.tenantId);
    }
    
    // Add additional parameters
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        url.searchParams.set(key, String(value));
      }
    });
    
    return url.toString();
  }

  /**
   * Make GET request to admin API
   */
  private async get<T>(endpoint: string, params: Record<string, any> = {}): Promise<T> {
    const url = this.buildUrl(endpoint, params);
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Request failed: ${response.statusText}`);
    }
    
    return response.json();
  }

  /**
   * Make POST request to admin API
   */
  private async post<T>(endpoint: string, data: any, params: Record<string, any> = {}): Promise<T> {
    const url = this.buildUrl(endpoint, params);
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Request failed: ${response.statusText}`);
    }
    
    return response.json();
  }

  // ============================================
  // Control Room API Methods
  // ============================================

  /**
   * Get platform statistics
   * 
   * Backend: GET /api/admin/control-room/statistics
   */
  async getPlatformStatistics(): Promise<PlatformStatistics> {
    return this.get<PlatformStatistics>('/api/admin/control-room/statistics');
  }

  /**
   * Get execution metrics
   * 
   * Backend: GET /api/admin/control-room/execution-metrics
   */
  async getExecutionMetrics(timeRange: string = '1h'): Promise<ExecutionMetrics> {
    return this.get<ExecutionMetrics>('/api/admin/control-room/execution-metrics', {
      time_range: timeRange
    });
  }

  /**
   * Get realm health
   * 
   * Backend: GET /api/admin/control-room/realm-health
   */
  async getRealmHealth(): Promise<RealmHealth> {
    return this.get<RealmHealth>('/api/admin/control-room/realm-health');
  }

  /**
   * Get solution registry status
   * 
   * Backend: GET /api/admin/control-room/solution-registry
   */
  async getSolutionRegistryStatus(): Promise<SolutionRegistryStatus> {
    return this.get<SolutionRegistryStatus>('/api/admin/control-room/solution-registry');
  }

  /**
   * Get system health
   * 
   * Backend: GET /api/admin/control-room/system-health
   */
  async getSystemHealth(): Promise<SystemHealth> {
    return this.get<SystemHealth>('/api/admin/control-room/system-health');
  }

  // ============================================
  // Developer View API Methods
  // ============================================

  /**
   * Get Platform SDK documentation
   * 
   * Backend: GET /api/admin/developer/documentation
   */
  async getDocumentation(section?: string): Promise<Documentation> {
    return this.get<Documentation>('/api/admin/developer/documentation', 
      section ? { section } : {}
    );
  }

  /**
   * Get code examples
   * 
   * Backend: GET /api/admin/developer/code-examples
   */
  async getCodeExamples(category?: string): Promise<CodeExamples> {
    return this.get<CodeExamples>('/api/admin/developer/code-examples',
      category ? { category } : {}
    );
  }

  /**
   * Get patterns and best practices
   * 
   * Backend: GET /api/admin/developer/patterns
   */
  async getPatterns(): Promise<Patterns> {
    return this.get<Patterns>('/api/admin/developer/patterns');
  }

  /**
   * Validate solution configuration (Solution Builder Playground)
   * 
   * Backend: POST /api/admin/developer/validate-solution
   */
  async validateSolution(request: SolutionValidationRequest): Promise<SolutionValidationResponse> {
    return this.post<SolutionValidationResponse>(
      '/api/admin/developer/validate-solution',
      request.solution_config
    );
  }

  /**
   * Preview solution structure (Solution Builder Playground)
   * 
   * Backend: POST /api/admin/developer/preview-solution
   */
  async previewSolution(request: SolutionValidationRequest): Promise<SolutionValidationResponse> {
    return this.post<SolutionValidationResponse>(
      '/api/admin/developer/preview-solution',
      request.solution_config
    );
  }

  /**
   * Submit feature request (Developer)
   * 
   * Backend: POST /api/admin/developer/submit-feature-request
   */
  async submitFeatureRequest(request: FeatureRequestSubmission): Promise<FeatureRequestResponse> {
    return this.post<FeatureRequestResponse>(
      '/api/admin/developer/submit-feature-request',
      request
    );
  }

  // ============================================
  // Business User View API Methods
  // ============================================

  /**
   * Get solution composition guide
   * 
   * Backend: GET /api/admin/business/composition-guide
   */
  async getCompositionGuide(): Promise<CompositionGuide> {
    return this.get<CompositionGuide>('/api/admin/business/composition-guide');
  }

  /**
   * Get solution templates
   * 
   * Backend: GET /api/admin/business/templates
   */
  async getSolutionTemplates(): Promise<SolutionTemplates> {
    return this.get<SolutionTemplates>('/api/admin/business/templates');
  }

  /**
   * Compose solution (advanced builder)
   * 
   * Backend: POST /api/admin/business/compose
   */
  async composeSolution(request: SolutionCompositionRequest): Promise<SolutionCompositionResponse> {
    return this.post<SolutionCompositionResponse>(
      '/api/admin/business/compose',
      request.solution_config
    );
  }

  /**
   * Create solution from template
   * 
   * Backend: POST /api/admin/business/create-from-template
   */
  async createFromTemplate(templateId: string, customizations?: Record<string, any>): Promise<SolutionCompositionResponse> {
    return this.post<SolutionCompositionResponse>(
      '/api/admin/business/create-from-template',
      { template_id: templateId, customizations }
    );
  }

  /**
   * List registered solutions
   * 
   * Backend: GET /api/admin/business/solutions
   */
  async listSolutions(activeOnly: boolean = false): Promise<any> {
    return this.get('/api/admin/business/solutions', { active_only: activeOnly });
  }

  /**
   * Get solution status
   * 
   * Backend: GET /api/admin/business/solutions/{solution_id}
   */
  async getSolutionStatus(solutionId: string): Promise<any> {
    return this.get(`/api/admin/business/solutions/${solutionId}`);
  }

  /**
   * Register composed solution
   * 
   * Backend: POST /api/admin/business/compose (same as composeSolution)
   */
  async registerSolution(request: SolutionCompositionRequest): Promise<SolutionCompositionResponse> {
    return this.composeSolution(request);
  }

  /**
   * Submit business feature request
   * 
   * Backend: POST /api/admin/business/submit-feature-request
   */
  async submitBusinessFeatureRequest(request: BusinessFeatureRequest): Promise<BusinessFeatureRequestResponse> {
    return this.post<BusinessFeatureRequestResponse>(
      '/api/admin/business/submit-feature-request',
      request
    );
  }
}

// ============================================
// Hook for React Components
// ============================================

import { useMemo } from 'react';
import { useSessionBoundary } from '@/shared/state/SessionBoundaryProvider';
import { useTenant } from '@/shared/contexts/TenantContext';

/**
 * React hook to create AdminAPIManager with current session and tenant context
 * 
 * Usage:
 *   const adminAPI = useAdminAPIManager();
 *   const stats = await adminAPI.getPlatformStatistics();
 */
export function useAdminAPIManager(): AdminAPIManager {
  const { state: sessionState } = useSessionBoundary();
  const { tenantId } = useTenant();
  
  return useMemo(() => {
    const manager = new AdminAPIManager(
      sessionState.sessionId || undefined,
      tenantId || undefined
    );
    return manager;
  }, [sessionState.sessionId, tenantId]);
}
