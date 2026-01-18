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

export class AdminAPIManager {
  private baseUrl: string;

  constructor(baseUrl?: string) {
    this.baseUrl = baseUrl || getApiEndpointUrl('');
  }

  // ============================================
  // Control Room API Methods
  // ============================================

  /**
   * Get platform statistics
   */
  async getPlatformStatistics(): Promise<PlatformStatistics> {
    const url = getApiEndpointUrl('/api/admin/control-room/statistics');
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to get platform statistics' }));
      throw new Error(error.detail || `Failed to get platform statistics: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get execution metrics
   */
  async getExecutionMetrics(timeRange: string = '1h'): Promise<ExecutionMetrics> {
    const url = getApiEndpointUrl(`/api/admin/control-room/execution-metrics?time_range=${encodeURIComponent(timeRange)}`);
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to get execution metrics' }));
      throw new Error(error.detail || `Failed to get execution metrics: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get realm health
   */
  async getRealmHealth(): Promise<RealmHealth> {
    const url = getApiEndpointUrl('/api/admin/control-room/realm-health');
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to get realm health' }));
      throw new Error(error.detail || `Failed to get realm health: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get solution registry status
   */
  async getSolutionRegistryStatus(): Promise<SolutionRegistryStatus> {
    const url = getApiEndpointUrl('/api/admin/control-room/solution-registry');
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to get solution registry status' }));
      throw new Error(error.detail || `Failed to get solution registry status: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get system health
   */
  async getSystemHealth(): Promise<SystemHealth> {
    const url = getApiEndpointUrl('/api/admin/control-room/system-health');
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to get system health' }));
      throw new Error(error.detail || `Failed to get system health: ${response.statusText}`);
    }

    return response.json();
  }

  // ============================================
  // Developer View API Methods
  // ============================================

  /**
   * Get Platform SDK documentation
   */
  async getDocumentation(section?: string): Promise<Documentation> {
    const url = section
      ? getApiEndpointUrl(`/api/admin/developer/docs?section=${encodeURIComponent(section)}`)
      : getApiEndpointUrl('/api/admin/developer/docs');
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to get documentation' }));
      throw new Error(error.detail || `Failed to get documentation: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get code examples
   */
  async getCodeExamples(category?: string): Promise<CodeExamples> {
    const url = category
      ? getApiEndpointUrl(`/api/admin/developer/examples?category=${encodeURIComponent(category)}`)
      : getApiEndpointUrl('/api/admin/developer/examples');
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to get code examples' }));
      throw new Error(error.detail || `Failed to get code examples: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get patterns and best practices
   */
  async getPatterns(): Promise<Patterns> {
    const url = getApiEndpointUrl('/api/admin/developer/patterns');
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to get patterns' }));
      throw new Error(error.detail || `Failed to get patterns: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Validate solution configuration (Playground - gated)
   */
  async validateSolution(request: SolutionValidationRequest): Promise<SolutionValidationResponse> {
    const url = getApiEndpointUrl('/api/admin/developer/solution-builder/validate');
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to validate solution' }));
      throw new Error(error.detail || `Failed to validate solution: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Preview solution structure (Playground - gated)
   */
  async previewSolution(request: SolutionValidationRequest): Promise<SolutionValidationResponse> {
    const url = getApiEndpointUrl('/api/admin/developer/solution-builder/preview');
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to preview solution' }));
      throw new Error(error.detail || `Failed to preview solution: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Submit feature request (gated - "Coming Soon" for MVP)
   */
  async submitFeatureRequest(request: FeatureRequestSubmission): Promise<FeatureRequestResponse> {
    const url = getApiEndpointUrl('/api/admin/developer/features/submit');
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to submit feature request' }));
      throw new Error(error.detail || `Failed to submit feature request: ${response.statusText}`);
    }

    return response.json();
  }

  // ============================================
  // Business User View API Methods
  // ============================================

  /**
   * Get solution composition guide
   */
  async getCompositionGuide(): Promise<CompositionGuide> {
    const url = getApiEndpointUrl('/api/admin/business/composition-guide');
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to get composition guide' }));
      throw new Error(error.detail || `Failed to get composition guide: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get solution templates (gated)
   */
  async getSolutionTemplates(): Promise<SolutionTemplates> {
    const url = getApiEndpointUrl('/api/admin/business/solution-templates');
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to get solution templates' }));
      throw new Error(error.detail || `Failed to get solution templates: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Compose solution (advanced builder - gated)
   */
  async composeSolution(request: SolutionCompositionRequest): Promise<SolutionCompositionResponse> {
    const url = getApiEndpointUrl('/api/admin/business/solutions/compose');
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to compose solution' }));
      throw new Error(error.detail || `Failed to compose solution: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Register composed solution
   */
  async registerSolution(request: SolutionCompositionRequest): Promise<SolutionCompositionResponse> {
    const url = getApiEndpointUrl('/api/admin/business/solutions/register');
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to register solution' }));
      throw new Error(error.detail || `Failed to register solution: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Submit business feature request
   */
  async submitBusinessFeatureRequest(request: BusinessFeatureRequest): Promise<BusinessFeatureRequestResponse> {
    const url = getApiEndpointUrl('/api/admin/business/feature-requests/submit');
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to submit feature request' }));
      throw new Error(error.detail || `Failed to submit feature request: ${response.statusText}`);
    }

    return response.json();
  }
}

// Factory function for use in components
export function useAdminAPIManager(): AdminAPIManager {
  return new AdminAPIManager();
}
