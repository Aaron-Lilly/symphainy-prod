// Operations Service Orchestrator
export * from './types';
export * from './solution-service';
// Note: Removed star exports to avoid conflicts, using specific imports below

// Main OperationsService class for unified access
import {
  OperationsSessionResponse,
  OperationsWorkflowResponse,
  OperationsCoexistenceResponse,
  OperationsWizardResponse,
  WorkflowGenerationRequest,
  SopGenerationRequest,
  CoexistenceAnalysisRequest,
  CoexistenceContentRequest,
  WizardRequest,
  BlueprintSaveRequest,
  OperationsQueryRequest,
  OperationsConversationRequest
} from './types';

import {
  getSessionElements,
  clearSessionElements,
  generateWorkflowFromSop,
  generateSopFromWorkflow,
  optimizeCoexistence,
  optimizeCoexistenceWithContent,
  saveBlueprint
} from './core';

// Import new real conversion functions
import {
  convertSopToWorkflowReal,
  convertWorkflowToSopReal,
  extractSopFromDocx,
  createCoexistenceBlueprintDirectly,
  processOperationsConversation,
  checkOperationsHealth
} from './operations-service-updated';

import {
  sopToWorkflow,
  workflowToSop,
  getWorkflowStatus,
  validateWorkflow
} from './workflow-generation';

import {
  validateSop,
  optimizeSop,
  generateSopTemplate
} from './sop-generation';

import {
  analyzeCoexistence,
  generateBlueprint,
  evaluateCoexistence
} from './coexistence';

import {
  routeOperationsSession,
  sendOperationsMessage,
  orchestrateOperationsWorkflow,
  persistOperationsState,
  processOperationsQuery,
  getOperationsConversationContext,
  analyzeOperationsIntent
} from './smart-city-integration';

export class OperationsService {
  // Session Management
  static async getSessionElements(sessionToken: string): Promise<OperationsSessionResponse> {
    return getSessionElements(sessionToken);
  }

  static async clearSessionElements(sessionToken: string): Promise<{ success: boolean; message: string }> {
    return clearSessionElements(sessionToken);
  }

  // Workflow Generation
  static async generateWorkflowFromSop(request: WorkflowGenerationRequest): Promise<OperationsWorkflowResponse> {
    return generateWorkflowFromSop(request);
  }

  static async generateSopFromWorkflow(request: SopGenerationRequest): Promise<OperationsWorkflowResponse> {
    return generateSopFromWorkflow(request);
  }

  static async sopToWorkflow(fileUuid: string, token: string): Promise<OperationsWorkflowResponse> {
    return sopToWorkflow(fileUuid, token);
  }

  static async workflowToSop(fileUuid: string, token: string): Promise<OperationsWorkflowResponse> {
    return workflowToSop(fileUuid, token);
  }

  static async getWorkflowStatus(workflowId: string, token: string): Promise<any> {
    return getWorkflowStatus(workflowId, token);
  }

  static async validateWorkflow(workflowData: any, token: string): Promise<any> {
    return validateWorkflow(workflowData, token);
  }

  // SOP Generation
  static async validateSop(sopData: any, token: string): Promise<any> {
    return validateSop(sopData, token);
  }

  static async optimizeSop(request: any): Promise<any> {
    return optimizeSop(request);
  }

  static async generateSopTemplate(request: any): Promise<any> {
    return generateSopTemplate(request);
  }

  // Coexistence Analysis
  static async optimizeCoexistence(request: CoexistenceAnalysisRequest): Promise<OperationsCoexistenceResponse> {
    return optimizeCoexistence(request);
  }

  static async optimizeCoexistenceWithContent(request: CoexistenceContentRequest): Promise<OperationsCoexistenceResponse> {
    return optimizeCoexistenceWithContent(request);
  }

  static async analyzeCoexistence(sopData: any, workflowData: any, token: string): Promise<any> {
    return analyzeCoexistence(sopData, workflowData, token);
  }

  static async generateBlueprint(request: any): Promise<any> {
    return generateBlueprint(request);
  }

  static async evaluateCoexistence(request: any): Promise<any> {
    return evaluateCoexistence(request);
  }

  // Blueprint Management
  static async saveBlueprint(request: BlueprintSaveRequest): Promise<{ blueprint_id: string }> {
    return saveBlueprint(request);
  }

  // Smart City Integration
  static async routeOperationsSession(request: any): Promise<any> {
    return routeOperationsSession(request);
  }

  static async sendOperationsMessage(message: any): Promise<any> {
    return sendOperationsMessage(message);
  }

  static async orchestrateOperationsWorkflow(request: any): Promise<any> {
    return orchestrateOperationsWorkflow(request);
  }

  static async persistOperationsState(request: any): Promise<any> {
    return persistOperationsState(request);
  }

  // Operations Liaison
  static async processOperationsQuery(request: OperationsQueryRequest): Promise<any> {
    return processOperationsQuery(request);
  }


  static async getOperationsConversationContext(sessionId: string): Promise<any> {
    return getOperationsConversationContext(sessionId);
  }

  static async analyzeOperationsIntent(query: string): Promise<any> {
    return analyzeOperationsIntent(query);
  }

  // NEW: Real Conversion Methods
  static async convertSopToWorkflowReal(sopData: any, token: string): Promise<OperationsWorkflowResponse> {
    return convertSopToWorkflowReal(sopData, token);
  }

  static async convertWorkflowToSopReal(workflowData: any, token: string): Promise<OperationsWorkflowResponse> {
    return convertWorkflowToSopReal(workflowData, token);
  }

  static async extractSopFromDocx(file: File, token: string): Promise<OperationsWorkflowResponse> {
    return extractSopFromDocx(file, token);
  }

  // NEW: CoexistenceEvaluator Bypass Methods
  static async createCoexistenceBlueprintDirectly(
    userRequirements: any, 
    conversationId: string, 
    token: string
  ): Promise<OperationsCoexistenceResponse> {
    return createCoexistenceBlueprintDirectly(userRequirements, conversationId, token);
  }

  // NEW: Operations Conversation Methods
  static async processOperationsConversation(
    message: string, 
    conversationId: string, 
    token: string
  ): Promise<OperationsCoexistenceResponse> {
    return processOperationsConversation(message, conversationId, token);
  }

  // NEW: Operations Wizard Conversation Method
  static async processOperationsWizardConversation(
    request: OperationsConversationRequest
  ): Promise<OperationsWizardResponse> {
    const response = await fetch(
      // Use centralized API config (NO hardcoded values)
      (await import('@/shared/config/api-config')).getApiEndpointUrl('/api/operations/liaison/conversation'),
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
      },
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }

  // NEW: Health Check Methods
  static async checkOperationsHealth(): Promise<any> {
    return checkOperationsHealth();
  }
}

// Default export for convenience
export default OperationsService; 