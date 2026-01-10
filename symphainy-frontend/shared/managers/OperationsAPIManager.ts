/**
 * Operations API Manager
 * 
 * Centralizes all Operations pillar API calls and operations.
 * Provides a clean interface for all operations-related functionality.
 */

// ============================================
// Operations API Manager Types
// ============================================

export interface SessionElement {
  id: string;
  type: string;
  name: string;
  content: any;
  metadata?: any;
}

export interface SessionResponse {
  valid: boolean;
  elements?: Record<string, SessionElement>;
  error?: string;
}

export interface CoexistenceRequest {
  sessionToken: string;
  sopInputFileUuid: string;
  workflowInputFileUuid: string;
}

export interface CoexistenceResponse {
  status: string;
  message?: string;
  result?: any;
}

export interface WorkflowRequest {
  sopFileUuid: string;
  sessionToken: string;
}

export interface WorkflowResponse {
  status: string;
  message?: string;
  workflow?: any;
}

export interface SOPRequest {
  workflowFileUuid: string;
  sessionToken: string;
}

export interface SOPResponse {
  status: string;
  message?: string;
  sop?: any;
}

// ============================================
// Operations API Manager Class
// ============================================

import { BaseAPIManager, UserContext } from './BaseAPIManager';

export class OperationsAPIManager extends BaseAPIManager {
  constructor(sessionToken: string, baseURL?: string, userContext?: UserContext) {
    super(sessionToken, baseURL, userContext);
  }


  // ============================================
  // Session Management
  // ============================================

  async getSessionElements(): Promise<SessionResponse> {
      const result = await this.post<SessionResponse>('/api/v1/operations-pillar/session/elements', {
      sessionToken: (this as any).sessionToken
    });

    if (!result.success || !result.data) {
      return {
        valid: false,
        error: result.error || 'Failed to get session elements'
      };
    }

    return result.data;
  }

  // ============================================
  // Coexistence Analysis
  // ============================================

  async analyzeCoexistence(request: CoexistenceRequest): Promise<CoexistenceResponse> {
    const result = await this.post<CoexistenceResponse>('/api/v1/operations-pillar/coexistence/analyze', request);

    if (!result.success || !result.data) {
      return {
        status: 'error',
        message: result.error || 'Coexistence analysis failed'
      };
    }

    return result.data;
  }

  // ============================================
  // Workflow Generation
  // ============================================

  // ============================================
  // SOP Management (Semantic APIs)
  // ============================================

  async createSOP(sopContent: any, options?: any): Promise<SOPResponse> {
    const result = await this.post<SOPResponse>('/api/v1/operations-pillar/create-standard-operating-procedure', {
      sop_content: sopContent,
      ...options
    });

    if (!result.success || !result.data) {
      return {
        status: 'error',
        message: result.error || 'SOP creation failed'
      };
    }

    return result.data;
  }

  async listSOPs(): Promise<any[]> {
    const result = await this.get<{ standard_operating_procedures?: any[]; sops?: any[] }>('/api/v1/operations-pillar/list-standard-operating-procedures');

    if (!result.success || !result.data) {
      throw new Error(result.error || 'Failed to list SOPs');
    }

    return result.data.standard_operating_procedures || result.data.sops || [];
  }

  // ============================================
  // Workflow Management (Semantic APIs)
  // ============================================

  async createWorkflow(workflowData: any, options?: any): Promise<WorkflowResponse> {
    const result = await this.post<WorkflowResponse>('/api/v1/operations-pillar/create-workflow', {
      workflow: workflowData,
      ...options
    });

    if (!result.success || !result.data) {
      return {
        status: 'error',
        message: result.error || 'Workflow creation failed'
      };
    }

    return result.data;
  }

  async listWorkflows(): Promise<any[]> {
    const result = await this.get<{ workflows?: any[] }>('/api/v1/operations-pillar/list-workflows');

    if (!result.success || !result.data) {
      throw new Error(result.error || 'Failed to list workflows');
    }

    return result.data.workflows || [];
  }

  // ============================================
  // Conversion (Semantic APIs)
  // ============================================

  async convertSOPToWorkflow(sopId: string, options?: any): Promise<WorkflowResponse> {
    const result = await this.post<WorkflowResponse>('/api/v1/operations-pillar/convert-sop-to-workflow', {
      sop_id: sopId,
      sop_file_uuid: sopId,
      sop_content: options?.sop_content,
      conversion_type: 'sop_to_workflow',
      ...options
    });

    if (!result.success || !result.data) {
      return {
        status: 'error',
        message: result.error || 'SOP to workflow conversion failed'
      };
    }

    return result.data;
  }

  async convertWorkflowToSOP(workflowId: string, options?: any): Promise<SOPResponse> {
    const result = await this.post<SOPResponse>('/api/v1/operations-pillar/convert-workflow-to-sop', {
      workflow_id: workflowId,
      workflow_file_uuid: workflowId,
      workflow: options?.workflow,
      workflow_content: options?.workflow,
      conversion_type: 'workflow_to_sop',
      ...options
    });

    if (!result.success || !result.data) {
      return {
        status: 'error',
        message: result.error || 'Workflow to SOP conversion failed'
      };
    }

    return result.data;
  }

  // ============================================
  // Legacy Methods (for backward compatibility)
  // ============================================

  async generateWorkflowFromSOP(request: WorkflowRequest): Promise<WorkflowResponse> {
    // Use semantic API
    return this.convertSOPToWorkflow(request.sopFileUuid);
  }

  async generateSOPFromWorkflow(request: SOPRequest): Promise<SOPResponse> {
    // Use semantic API
    return this.convertWorkflowToSOP(request.workflowFileUuid);
  }

  // ============================================
  // Process Optimization
  // ============================================

  async optimizeProcess(processId: string, optimizationType: string): Promise<any> {
    const result = await this.post<any>(`/api/v1/operations-pillar/process/${processId}/optimize`, {
      optimizationType
    });

    if (!result.success || !result.data) {
      throw new Error(result.error || 'Process optimization failed');
    }

    return result.data;
  }

  // ============================================
  // Compliance Checking
  // ============================================

  async checkCompliance(processId: string, complianceType: string): Promise<any> {
    const result = await this.post<any>('/api/v1/operations-pillar/compliance/check', {
      processId,
      complianceType
    });

    if (!result.success || !result.data) {
      throw new Error(result.error || 'Compliance check failed');
    }

    return result.data;
  }

  // ============================================
  // Operations Health
  // ============================================

  async getHealthStatus(): Promise<any> {
    const result = await this.get<any>('/api/v1/operations-pillar/health');

    if (!result.success || !result.data) {
      throw new Error(result.error || 'Health check failed');
    }

    return result.data;
  }
}





























