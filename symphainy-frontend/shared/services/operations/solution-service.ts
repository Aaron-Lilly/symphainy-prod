/**
 * Operations Solution Service
 * 
 * Service layer for Operations Solution Orchestrator endpoints.
 * Follows the same pattern as Insights Solution Service.
 * 
 * Endpoints:
 * - POST /api/v1/operations-solution/workflow-from-sop
 * - POST /api/v1/operations-solution/sop-from-workflow
 * - POST /api/v1/operations-solution/coexistence-analysis
 * - POST /api/v1/operations-solution/interactive-sop/start
 * - POST /api/v1/operations-solution/interactive-sop/chat
 * - POST /api/v1/operations-solution/interactive-sop/publish
 * - POST /api/v1/operations-solution/interactive-blueprint/chat
 * - POST /api/v1/operations-solution/ai-optimized-blueprint
 * - POST /api/v1/operations-solution/workflow-visualization
 * - POST /api/v1/operations-solution/sop-visualization
 */

import {
  OperationsWorkflowResponse,
  OperationsCoexistenceResponse,
  OperationsWizardResponse,
  WorkflowGenerationRequest,
  SopGenerationRequest,
  CoexistenceAnalysisRequest,
  WizardRequest,
  OperationsConversationRequest
} from './types';

import { getApiEndpointUrl } from '@/shared/config/api-config';

// Use centralized API config (NO hardcoded values)
const API_BASE = getApiEndpointUrl('/api/v1/operations-solution');

// Helper to create standardized authenticated headers
const getAuthHeaders = (token?: string, sessionToken?: string) => {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  
  if (sessionToken) {
    headers["X-Session-Token"] = sessionToken;
  }
  
  return headers;
};

export class OperationsSolutionService {
  private token?: string;

  constructor(token?: string) {
    this.token = token;
  }

  /**
   * Generate workflow from SOP
   */
  async generateWorkflowFromSop(
    request: WorkflowGenerationRequest
  ): Promise<OperationsWorkflowResponse> {
    const res = await fetch(`${API_BASE}/workflow-from-sop`, {
      method: "POST",
      headers: getAuthHeaders(this.token, request.sessionToken),
      body: JSON.stringify({
        sop_file_id: request.sopFileUuid,
        sop_content: request.sopContent,
        workflow_options: request.workflowOptions,
        user_context: {
          user_id: request.userId,
          session_id: request.sessionId,
          session_token: request.sessionToken
        }
      }),
    });
    
    if (!res.ok) {
      throw new Error(`Failed to generate workflow from SOP: ${res.status} ${res.statusText}`);
    }
    
    return await res.json();
  }

  /**
   * Generate SOP from workflow
   */
  async generateSopFromWorkflow(
    request: SopGenerationRequest
  ): Promise<OperationsWorkflowResponse> {
    const res = await fetch(`${API_BASE}/sop-from-workflow`, {
      method: "POST",
      headers: getAuthHeaders(this.token, request.sessionToken),
      body: JSON.stringify({
        workflow_file_id: request.workflowFileUuid,
        workflow_content: request.workflowContent,
        sop_options: request.sopOptions,
        user_context: {
          user_id: request.userId,
          session_id: request.sessionId,
          session_token: request.sessionToken
        }
      }),
    });
    
    if (!res.ok) {
      throw new Error(`Failed to generate SOP from workflow: ${res.status} ${res.statusText}`);
    }
    
    return await res.json();
  }

  /**
   * Analyze coexistence
   */
  async analyzeCoexistence(
    request: CoexistenceAnalysisRequest
  ): Promise<OperationsCoexistenceResponse> {
    const res = await fetch(`${API_BASE}/coexistence-analysis`, {
      method: "POST",
      headers: getAuthHeaders(this.token, request.sessionToken),
      body: JSON.stringify({
        coexistence_content: {
          sop_content: request.sopContent,
          workflow_content: request.workflowContent,
          current_state: request.currentState,
          target_state: request.targetState
        },
        analysis_options: request.analysisOptions,
        user_context: {
          user_id: request.userId,
          session_id: request.sessionId,
          session_token: request.sessionToken
        }
      }),
    });
    
    if (!res.ok) {
      throw new Error(`Failed to analyze coexistence: ${res.status} ${res.statusText}`);
    }
    
    return await res.json();
  }

  /**
   * Start interactive SOP creation
   */
  async startInteractiveSopCreation(
    sessionToken?: string,
    userId?: string,
    sessionId?: string
  ): Promise<OperationsWizardResponse> {
    const res = await fetch(`${API_BASE}/interactive-sop/start`, {
      method: "POST",
      headers: getAuthHeaders(this.token, sessionToken),
      body: JSON.stringify({
        user_context: {
          user_id: userId,
          session_id: sessionId,
          session_token: sessionToken
        }
      }),
    });
    
    if (!res.ok) {
      throw new Error(`Failed to start interactive SOP creation: ${res.status} ${res.statusText}`);
    }
    
    return await res.json();
  }

  /**
   * Chat for interactive SOP creation
   */
  async chatInteractiveSop(
    request: WizardRequest
  ): Promise<OperationsWizardResponse> {
    const res = await fetch(`${API_BASE}/interactive-sop/chat`, {
      method: "POST",
      headers: getAuthHeaders(this.token, request.sessionToken),
      body: JSON.stringify({
        message: request.userMessage || "",
        session_token: request.sessionToken,
        user_context: {
          session_token: request.sessionToken
        }
      }),
    });
    
    if (!res.ok) {
      throw new Error(`Failed to process interactive SOP chat: ${res.status} ${res.statusText}`);
    }
    
    return await res.json();
  }

  /**
   * Publish interactive SOP
   */
  async publishInteractiveSop(
    sessionToken: string,
    userId?: string,
    sessionId?: string
  ): Promise<OperationsWorkflowResponse> {
    const res = await fetch(`${API_BASE}/interactive-sop/publish`, {
      method: "POST",
      headers: getAuthHeaders(this.token, sessionToken),
      body: JSON.stringify({
        session_token: sessionToken,
        user_context: {
          user_id: userId,
          session_id: sessionId,
          session_token: sessionToken
        }
      }),
    });
    
    if (!res.ok) {
      throw new Error(`Failed to publish interactive SOP: ${res.status} ${res.statusText}`);
    }
    
    return await res.json();
  }

  /**
   * Interactive blueprint creation
   */
  async createInteractiveBlueprint(
    request: OperationsConversationRequest
  ): Promise<OperationsCoexistenceResponse> {
    const res = await fetch(`${API_BASE}/interactive-blueprint/chat`, {
      method: "POST",
      headers: getAuthHeaders(this.token),
      body: JSON.stringify({
        message: request.message,
        session_token: request.session_id,
        user_context: {
          session_id: request.session_id
        }
      }),
    });
    
    if (!res.ok) {
      throw new Error(`Failed to create interactive blueprint: ${res.status} ${res.statusText}`);
    }
    
    return await res.json();
  }

  /**
   * Generate AI-optimized blueprint from documents
   */
  async generateAIOptimizedBlueprint(
    sopFileIds?: string[],
    workflowFileIds?: string[],
    optimizationOptions?: Record<string, any>,
    sessionToken?: string,
    userId?: string,
    sessionId?: string
  ): Promise<OperationsCoexistenceResponse> {
    const res = await fetch(`${API_BASE}/ai-optimized-blueprint`, {
      method: "POST",
      headers: getAuthHeaders(this.token, sessionToken),
      body: JSON.stringify({
        sop_file_ids: sopFileIds,
        workflow_file_ids: workflowFileIds,
        optimization_options: optimizationOptions,
        user_context: {
          user_id: userId,
          session_id: sessionId,
          session_token: sessionToken
        }
      }),
    });
    
    if (!res.ok) {
      throw new Error(`Failed to generate AI-optimized blueprint: ${res.status} ${res.statusText}`);
    }
    
    return await res.json();
  }

  /**
   * Visualize workflow
   */
  async visualizeWorkflow(
    workflowFileId?: string,
    workflowContent?: Record<string, any>,
    visualizationOptions?: Record<string, any>,
    sessionToken?: string,
    userId?: string,
    sessionId?: string
  ): Promise<OperationsWorkflowResponse> {
    const res = await fetch(`${API_BASE}/workflow-visualization`, {
      method: "POST",
      headers: getAuthHeaders(this.token, sessionToken),
      body: JSON.stringify({
        workflow_file_id: workflowFileId,
        workflow_content: workflowContent,
        visualization_options: visualizationOptions,
        user_context: {
          user_id: userId,
          session_id: sessionId,
          session_token: sessionToken
        }
      }),
    });
    
    if (!res.ok) {
      throw new Error(`Failed to visualize workflow: ${res.status} ${res.statusText}`);
    }
    
    return await res.json();
  }

  /**
   * Visualize SOP
   */
  async visualizeSop(
    sopFileId?: string,
    sopContent?: Record<string, any>,
    visualizationOptions?: Record<string, any>,
    sessionToken?: string,
    userId?: string,
    sessionId?: string
  ): Promise<OperationsWorkflowResponse> {
    const res = await fetch(`${API_BASE}/sop-visualization`, {
      method: "POST",
      headers: getAuthHeaders(this.token, sessionToken),
      body: JSON.stringify({
        sop_file_id: sopFileId,
        sop_content: sopContent,
        visualization_options: visualizationOptions,
        user_context: {
          user_id: userId,
          session_id: sessionId,
          session_token: sessionToken
        }
      }),
    });
    
    if (!res.ok) {
      throw new Error(`Failed to visualize SOP: ${res.status} ${res.statusText}`);
    }
    
    return await res.json();
  }
}

// Export singleton instance
export const operationsSolutionService = new OperationsSolutionService();



