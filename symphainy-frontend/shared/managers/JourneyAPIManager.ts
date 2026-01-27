/**
 * Journey API Manager (New Architecture)
 * 
 * Journey Realm API client using Experience Plane Client and Runtime-based intent submission.
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

// ============================================
// Journey API Manager Types
// ============================================

export interface ProcessOptimizationResponse {
  success: boolean;
  optimized_process?: {
    process_id: string;
    optimizations: Array<{
      type: string;
      description: string;
      impact: "low" | "medium" | "high";
      recommendation: string;
    }>;
    metrics?: {
      efficiency_gain?: number;
      time_savings?: number;
      cost_reduction?: number;
    };
  };
  error?: string;
}

export interface SOPGenerationResponse {
  success: boolean;
  sop?: {
    sop_id: string;
    title: string;
    content: string;
    sections: Array<{
      title: string;
      content: string;
    }>;
    metadata?: Record<string, any>;
  };
  error?: string;
}

export interface WorkflowCreationResponse {
  success: boolean;
  workflow?: {
    workflow_id: string;
    name: string;
    steps: Array<{
      id: string;
      name: string;
      type: string;
      dependencies?: string[];
    }>;
    metadata?: Record<string, any>;
  };
  error?: string;
}

export interface CoexistenceAnalysisResponse {
  success: boolean;
  coexistence_analysis?: {
    analysis_id: string;
    sop_id?: string;
    workflow_id?: string;
    opportunities: Array<{
      type: string;
      description: string;
      potential_impact: string;
      recommendation: string;
    }>;
    blueprint?: {
      blueprint_id: string;
      visualization?: string;
      recommendations?: Array<string>;
    };
  };
  error?: string;
}

export interface BlueprintCreationResponse {
  success: boolean;
  blueprint?: {
    blueprint_id: string;
    name: string;
    description: string;
    visualization?: string;
    components: Array<{
      id: string;
      type: string;
      name: string;
      relationships?: Array<{
        target: string;
        type: string;
      }>;
    }>;
    metadata?: Record<string, any>;
  };
  error?: string;
}

// ============================================
// Journey API Manager Class
// ============================================

export class JourneyAPIManager {
  private experiencePlaneClient: ExperiencePlaneClient;
  private getPlatformState: () => ReturnType<typeof usePlatformState>;

  constructor(
    experiencePlaneClient?: ExperiencePlaneClient,
    getPlatformState?: () => ReturnType<typeof usePlatformState>
  ) {
    this.experiencePlaneClient = experiencePlaneClient || getGlobalExperiencePlaneClient();
    // Note: getPlatformState will be provided by components using the hook
    this.getPlatformState = getPlatformState || (() => {
      throw new Error("PlatformStateProvider not available. Use JourneyAPIManager with usePlatformState hook.");
    });
  }

  /**
   * Optimize process (optimize_process intent)
   * 
   * Flow: Experience Plane → Runtime → Journey Realm
   */
  async optimizeProcess(
    workflowId: string,
    optimizationOptions?: Record<string, any>
  ): Promise<ProcessOptimizationResponse> {
    try {
      const platformState = this.getPlatformState();
      
      if (!platformState.state.session.sessionId || !platformState.state.session.tenantId) {
        throw new Error("Session required to optimize process");
      }

      // ✅ FIX ISSUE 3: Parameter validation before submitIntent
      if (!workflowId) {
        throw new Error("workflow_id is required for optimize_process");
      }

      // Submit intent via Experience Plane Client
      const execution = await platformState.submitIntent(
        "optimize_process",
        {
          workflow_id: workflowId,
          optimization_options: optimizationOptions || {}
        }
      );

      // Wait for execution completion
      const result = await this._waitForExecution(execution, platformState);

      if (result.status === "completed" && result.artifacts?.optimized_process) {
        // Update realm state
        platformState.setRealmState("journey", "optimizedProcesses", {
          ...platformState.getRealmState("journey", "optimizedProcesses") || {},
          [workflowId]: result.artifacts.optimized_process
        });

        return {
          success: true,
          optimized_process: result.artifacts.optimized_process
        };
      } else {
        throw new Error(result.error || "Failed to optimize process");
      }
    } catch (error) {
      console.error("[JourneyAPIManager] Error optimizing process:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Generate SOP (generate_sop intent)
   * 
   * Flow: Experience Plane → Runtime → Journey Realm
   */
  async generateSOP(
    workflowId: string,
    sopOptions?: Record<string, any>
  ): Promise<SOPGenerationResponse> {
    try {
      const platformState = this.getPlatformState();
      
      if (!platformState.state.session.sessionId || !platformState.state.session.tenantId) {
        throw new Error("Session required to generate SOP");
      }

      // ✅ FIX ISSUE 3: Parameter validation before submitIntent
      if (!workflowId) {
        throw new Error("workflow_id is required for generate_sop");
      }

      // Submit intent via Experience Plane Client
      const execution = await platformState.submitIntent(
        "generate_sop",
        {
          workflow_id: workflowId,
          sop_options: sopOptions || {}
        }
      );

      // Wait for execution completion
      const result = await this._waitForExecution(execution, platformState);

      if (result.status === "completed" && result.artifacts?.sop) {
        // Update realm state
        platformState.setRealmState("journey", "sops", {
          ...platformState.getRealmState("journey", "sops") || {},
          [workflowId]: result.artifacts.sop
        });

        return {
          success: true,
          sop: result.artifacts.sop
        };
      } else {
        throw new Error(result.error || "Failed to generate SOP");
      }
    } catch (error) {
      console.error("[JourneyAPIManager] Error generating SOP:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Create workflow (create_workflow intent)
   * 
   * Flow: Experience Plane → Runtime → Journey Realm
   */
  async createWorkflow(
    sopId: string,
    workflowOptions?: Record<string, any>
  ): Promise<WorkflowCreationResponse> {
    try {
      const platformState = this.getPlatformState();
      
      // ✅ FIX ISSUE 4: Use standardized session validation
      validateSession(platformState, "create workflow");

      // ✅ FIX ISSUE 3: Parameter validation before submitIntent
      if (!sopId) {
        throw new Error("sop_id is required for create_workflow");
      }

      // Submit intent via Experience Plane Client
      const execution = await platformState.submitIntent(
        "create_workflow",
        {
          sop_id: sopId,
          workflow_options: workflowOptions || {}
        }
      );

      // Wait for execution completion
      const result = await this._waitForExecution(execution, platformState);

      if (result.status === "completed" && result.artifacts?.workflow) {
        // Update realm state
        platformState.setRealmState("journey", "workflows", {
          ...platformState.getRealmState("journey", "workflows") || {},
          [sopId]: result.artifacts.workflow
        });

        return {
          success: true,
          workflow: result.artifacts.workflow
        };
      } else {
        throw new Error(result.error || "Failed to create workflow");
      }
    } catch (error) {
      console.error("[JourneyAPIManager] Error creating workflow:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Optimize coexistence with content (optimize_coexistence_with_content intent)
   * 
   * ✅ FIX ISSUE 1: Migrated from OperationsService to intent-based API
   * 
   * Flow: Experience Plane → Runtime → Journey Realm
   */
  async optimizeCoexistenceWithContent(
    sopContent: string,
    workflowContent: string
  ): Promise<{
    success: boolean;
    optimized_sop?: any;
    optimized_workflow?: any;
    blueprint?: any;
    error?: string;
  }> {
    try {
      const platformState = this.getPlatformState();
      
      // ✅ FIX ISSUE 4: Use standardized session validation
      validateSession(platformState, "optimize coexistence");

      // ✅ FIX ISSUE 3: Parameter validation
      if (!sopContent || !workflowContent) {
        throw new Error("SOP content and workflow content are required for optimization");
      }

      // ✅ FIX ISSUE 1: Submit intent via Runtime (not direct API call)
      const execution = await platformState.submitIntent(
        "optimize_coexistence_with_content",
        {
          sop_content: sopContent,
          workflow_content: workflowContent
        }
      );

      // Wait for execution completion
      const result = await this._waitForExecution(execution, platformState);

      if (result.status === "completed" && result.artifacts?.optimized_coexistence) {
        const optimizedData = result.artifacts.optimized_coexistence;
        
        // Update realm state
        platformState.setRealmState("journey", "operations", {
          ...platformState.getRealmState("journey", "operations") || {},
          optimizedSop: optimizedData.optimized_sop,
          optimizedWorkflow: optimizedData.optimized_workflow,
          blueprint: optimizedData.blueprint,
          analysisComplete: true,
        });

        return {
          success: true,
          optimized_sop: optimizedData.optimized_sop,
          optimized_workflow: optimizedData.optimized_workflow,
          blueprint: optimizedData.blueprint,
        };
      } else {
        throw new Error(result.error || "Failed to optimize coexistence");
      }
    } catch (error) {
      console.error("[JourneyAPIManager] Error optimizing coexistence:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Analyze coexistence (analyze_coexistence intent)
   * 
   * Flow: Experience Plane → Runtime → Journey Realm
   */
  async analyzeCoexistence(
    sopId: string,
    workflowId: string,
    analysisOptions?: Record<string, any>
  ): Promise<CoexistenceAnalysisResponse> {
    try {
      const platformState = this.getPlatformState();
      
      // ✅ FIX ISSUE 4: Use standardized session validation
      validateSession(platformState, "analyze coexistence");

      // Submit intent via Experience Plane Client
      const execution = await platformState.submitIntent(
        "analyze_coexistence",
        {
          sop_id: sopId,
          workflow_id: workflowId,
          analysis_options: analysisOptions || {}
        }
      );

      // Wait for execution completion
      const result = await this._waitForExecution(execution, platformState);

      if (result.status === "completed" && result.artifacts?.coexistence_analysis) {
        // Update realm state
        const analysisId = result.artifacts.coexistence_analysis.analysis_id;
        platformState.setRealmState("journey", "coexistenceAnalyses", {
          ...platformState.getRealmState("journey", "coexistenceAnalyses") || {},
          [analysisId]: result.artifacts.coexistence_analysis
        });

        return {
          success: true,
          coexistence_analysis: result.artifacts.coexistence_analysis
        };
      } else {
        throw new Error(result.error || "Failed to analyze coexistence");
      }
    } catch (error) {
      console.error("[JourneyAPIManager] Error analyzing coexistence:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Create blueprint (create_blueprint intent)
   * 
   * Flow: Experience Plane → Runtime → Journey Realm
   */
  async createBlueprint(
    blueprintData: {
      name: string;
      description: string;
      components?: Array<{
        id: string;
        type: string;
        name: string;
      }>;
    },
    blueprintOptions?: Record<string, any>
  ): Promise<BlueprintCreationResponse> {
    try {
      const platformState = this.getPlatformState();
      
      // ✅ FIX ISSUE 4: Use standardized session validation
      validateSession(platformState, "create blueprint");

      // ✅ FIX ISSUE 3: Parameter validation before submitIntent
      if (!blueprintData || !blueprintData.name) {
        throw new Error("blueprint_data.name is required for create_blueprint");
      }
      if (!blueprintData.description) {
        throw new Error("blueprint_data.description is required for create_blueprint");
      }

      // Submit intent via Experience Plane Client
      const execution = await platformState.submitIntent(
        "create_blueprint",
        {
          blueprint_data: blueprintData,
          blueprint_options: blueprintOptions || {}
        }
      );

      // Wait for execution completion
      const result = await this._waitForExecution(execution, platformState);

      if (result.status === "completed" && result.artifacts?.blueprint) {
        // Update realm state
        const blueprintId = result.artifacts.blueprint.blueprint_id;
        platformState.setRealmState("journey", "blueprints", {
          ...platformState.getRealmState("journey", "blueprints") || {},
          [blueprintId]: result.artifacts.blueprint
        });

        return {
          success: true,
          blueprint: result.artifacts.blueprint
        };
      } else {
        throw new Error(result.error || "Failed to create blueprint");
      }
    } catch (error) {
      console.error("[JourneyAPIManager] Error creating blueprint:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Process operations conversation (process_operations_conversation intent)
   * 
   * ✅ PHASE 5.6.1: Agent operation migrated to intent-based API
   * 
   * Flow: Experience Plane → Runtime → Journey Realm
   */
  async processOperationsConversation(
    message: string,
    conversationId: string,
    context?: Record<string, any>
  ): Promise<{ success: boolean; message?: string; error?: string }> {
    try {
      const platformState = this.getPlatformState();
      
      // ✅ FIX ISSUE 4: Use standardized session validation
      validateSession(platformState, "process operations conversation");

      // ✅ FIX ISSUE 3: Parameter validation before submitIntent
      if (!message) {
        throw new Error("message is required for process_operations_conversation");
      }
      if (!conversationId) {
        throw new Error("conversation_id is required for process_operations_conversation");
      }

      // Submit intent via Experience Plane Client
      const execution = await platformState.submitIntent(
        "process_operations_conversation",
        {
          message,
          conversation_id: conversationId,
          context: context || {}
        }
      );

      // Wait for execution completion
      const result = await this._waitForExecution(execution, platformState);

      if (result.status === "completed" && result.artifacts?.conversation_response) {
        return {
          success: true,
          message: result.artifacts.conversation_response.message
        };
      } else {
        throw new Error(result.error || "Failed to process operations conversation");
      }
    } catch (error) {
      console.error("[JourneyAPIManager] Error processing operations conversation:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Process wizard conversation (process_wizard_conversation intent)
   * 
   * ✅ PHASE 5.6.1: Agent operation migrated to intent-based API
   * 
   * Flow: Experience Plane → Runtime → Journey Realm
   */
  async processWizardConversation(
    message: string,
    sessionId: string,
    context?: Record<string, any>
  ): Promise<{ success: boolean; agent_response?: string; draft_sop?: any; error?: string }> {
    try {
      const platformState = this.getPlatformState();
      
      // ✅ FIX ISSUE 4: Use standardized session validation
      validateSession(platformState, "process wizard conversation");

      // ✅ FIX ISSUE 3: Parameter validation before submitIntent
      if (!message) {
        throw new Error("message is required for process_wizard_conversation");
      }
      if (!sessionId) {
        throw new Error("session_id is required for process_wizard_conversation");
      }

      // Submit intent via Experience Plane Client
      const execution = await platformState.submitIntent(
        "process_wizard_conversation",
        {
          message,
          session_id: sessionId,
          context: context || {}
        }
      );

      // Wait for execution completion
      const result = await this._waitForExecution(execution, platformState);

      if (result.status === "completed" && result.artifacts?.wizard_response) {
        return {
          success: true,
          agent_response: result.artifacts.wizard_response.agent_response,
          draft_sop: result.artifacts.wizard_response.draft_sop
        };
      } else {
        throw new Error(result.error || "Failed to process wizard conversation");
      }
    } catch (error) {
      console.error("[JourneyAPIManager] Error processing wizard conversation:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Process operations query (process_operations_query intent)
   * 
   * ✅ PHASE 5.6.1: Agent operation migrated to intent-based API
   * 
   * Flow: Experience Plane → Runtime → Journey Realm
   */
  async processOperationsQuery(
    query: string,
    sessionId: string,
    context?: Record<string, any>
  ): Promise<{ success: boolean; sop?: any; workflow?: any; error?: string }> {
    try {
      const platformState = this.getPlatformState();
      
      // ✅ FIX ISSUE 4: Use standardized session validation
      validateSession(platformState, "process operations query");

      // ✅ FIX ISSUE 3: Parameter validation before submitIntent
      if (!query) {
        throw new Error("query is required for process_operations_query");
      }
      if (!sessionId) {
        throw new Error("session_id is required for process_operations_query");
      }

      // Submit intent via Experience Plane Client
      const execution = await platformState.submitIntent(
        "process_operations_query",
        {
          query,
          session_id: sessionId,
          context: context || {}
        }
      );

      // Wait for execution completion
      const result = await this._waitForExecution(execution, platformState);

      if (result.status === "completed" && result.artifacts?.query_response) {
        return {
          success: true,
          sop: result.artifacts.query_response.sop,
          workflow: result.artifacts.query_response.workflow
        };
      } else {
        throw new Error(result.error || "Failed to process operations query");
      }
    } catch (error) {
      console.error("[JourneyAPIManager] Error processing operations query:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Analyze user intent (analyze_user_intent intent)
   * 
   * ✅ PHASE 5.6.3: Guide agent operation migrated to intent-based API
   * 
   * Flow: Experience Plane → Runtime → Journey Realm (Guide Agent)
   */
  async analyzeUserIntent(
    message: string,
    context?: Record<string, any>
  ): Promise<{ success: boolean; intent_analysis?: any; error?: string }> {
    try {
      const platformState = this.getPlatformState();
      
      // ✅ FIX ISSUE 4: Use standardized session validation
      validateSession(platformState, "analyze user intent");

      // ✅ FIX ISSUE 3: Parameter validation before submitIntent
      if (!message) {
        throw new Error("message is required for analyze_user_intent");
      }

      // Submit intent via Experience Plane Client
      const execution = await platformState.submitIntent(
        "analyze_user_intent",
        {
          message,
          context: context || {}
        }
      );

      // Wait for execution completion
      const result = await this._waitForExecution(execution, platformState);

      if (result.status === "completed" && result.artifacts?.intent_analysis) {
        return {
          success: true,
          intent_analysis: result.artifacts.intent_analysis
        };
      } else {
        throw new Error(result.error || "Failed to analyze user intent");
      }
    } catch (error) {
      console.error("[JourneyAPIManager] Error analyzing user intent:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Get journey guidance (get_journey_guidance intent)
   * 
   * ✅ PHASE 5.6.3: Guide agent operation migrated to intent-based API
   * 
   * Flow: Experience Plane → Runtime → Journey Realm (Guide Agent)
   */
  async getJourneyGuidance(
    userGoal: string,
    currentStep?: string,
    context?: Record<string, any>
  ): Promise<{ success: boolean; guidance?: any; next_steps?: string[]; error?: string }> {
    try {
      const platformState = this.getPlatformState();
      
      // ✅ FIX ISSUE 4: Use standardized session validation
      validateSession(platformState, "get journey guidance");

      // ✅ FIX ISSUE 3: Parameter validation before submitIntent
      if (!userGoal) {
        throw new Error("user_goal is required for get_journey_guidance");
      }

      // Submit intent via Experience Plane Client
      const execution = await platformState.submitIntent(
        "get_journey_guidance",
        {
          user_goal: userGoal,
          current_step: currentStep,
          context: context || {}
        }
      );

      // Wait for execution completion
      const result = await this._waitForExecution(execution, platformState);

      if (result.status === "completed" && result.artifacts?.journey_guidance) {
        return {
          success: true,
          guidance: result.artifacts.journey_guidance.guidance,
          next_steps: result.artifacts.journey_guidance.next_steps
        };
      } else {
        throw new Error(result.error || "Failed to get journey guidance");
      }
    } catch (error) {
      console.error("[JourneyAPIManager] Error getting journey guidance:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Get conversation history (get_conversation_history intent)
   * 
   * ✅ PHASE 5.6.3: Guide agent operation migrated to intent-based API
   * 
   * Flow: Experience Plane → Runtime → Journey Realm (Guide Agent)
   */
  async getConversationHistory(
    sessionId: string
  ): Promise<{ success: boolean; conversation_history?: any[]; error?: string }> {
    try {
      const platformState = this.getPlatformState();
      
      // ✅ FIX ISSUE 4: Use standardized session validation
      validateSession(platformState, "get conversation history");

      // ✅ FIX ISSUE 3: Parameter validation before submitIntent
      if (!sessionId) {
        throw new Error("session_id is required for get_conversation_history");
      }

      // Submit intent via Experience Plane Client
      const execution = await platformState.submitIntent(
        "get_conversation_history",
        {
          session_id: sessionId
        }
      );

      // Wait for execution completion
      const result = await this._waitForExecution(execution, platformState);

      if (result.status === "completed" && result.artifacts?.conversation_history) {
        return {
          success: true,
          conversation_history: result.artifacts.conversation_history
        };
      } else {
        throw new Error(result.error || "Failed to get conversation history");
      }
    } catch (error) {
      console.error("[JourneyAPIManager] Error getting conversation history:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Send message to pillar agent (send_message_to_pillar_agent intent)
   * 
   * ✅ PHASE 5.6.4: Liaison agent operation migrated to intent-based API
   * 
   * Flow: Experience Plane → Runtime → Appropriate Realm (based on pillar)
   */
  async sendMessageToPillarAgent(
    message: string,
    pillar: 'content' | 'insights' | 'journey' | 'outcomes',
    conversationId?: string,
    context?: Record<string, any>
  ): Promise<{ success: boolean; response?: any; error?: string }> {
    try {
      const platformState = this.getPlatformState();
      
      // ✅ FIX ISSUE 4: Use standardized session validation
      validateSession(platformState, "send message to pillar agent");

      // ✅ FIX ISSUE 3: Parameter validation before submitIntent
      if (!message) {
        throw new Error("message is required for send_message_to_pillar_agent");
      }
      if (!pillar) {
        throw new Error("pillar is required for send_message_to_pillar_agent");
      }

      // Submit intent via Experience Plane Client
      const execution = await platformState.submitIntent(
        "send_message_to_pillar_agent",
        {
          message,
          pillar,
          conversation_id: conversationId,
          context: context || {}
        }
      );

      // Wait for execution completion
      const result = await this._waitForExecution(execution, platformState);

      if (result.status === "completed" && result.artifacts?.agent_response) {
        return {
          success: true,
          response: result.artifacts.agent_response
        };
      } else {
        throw new Error(result.error || "Failed to send message to pillar agent");
      }
    } catch (error) {
      console.error("[JourneyAPIManager] Error sending message to pillar agent:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Get pillar conversation history (get_pillar_conversation_history intent)
   * 
   * ✅ PHASE 5.6.4: Liaison agent operation migrated to intent-based API
   * 
   * Flow: Experience Plane → Runtime → Appropriate Realm (based on pillar)
   */
  async getPillarConversationHistory(
    sessionId: string,
    pillar: 'content' | 'insights' | 'journey' | 'outcomes'
  ): Promise<{ success: boolean; conversation?: any; error?: string }> {
    try {
      const platformState = this.getPlatformState();
      
      // ✅ FIX ISSUE 4: Use standardized session validation
      validateSession(platformState, "get pillar conversation history");

      // ✅ FIX ISSUE 3: Parameter validation before submitIntent
      if (!sessionId) {
        throw new Error("session_id is required for get_pillar_conversation_history");
      }
      if (!pillar) {
        throw new Error("pillar is required for get_pillar_conversation_history");
      }

      // Submit intent via Experience Plane Client
      const execution = await platformState.submitIntent(
        "get_pillar_conversation_history",
        {
          session_id: sessionId,
          pillar
        }
      );

      // Wait for execution completion
      const result = await this._waitForExecution(execution, platformState);

      if (result.status === "completed" && result.artifacts?.conversation_history) {
        return {
          success: true,
          conversation: result.artifacts.conversation_history
        };
      } else {
        throw new Error(result.error || "Failed to get pillar conversation history");
      }
    } catch (error) {
      console.error("[JourneyAPIManager] Error getting pillar conversation history:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Wait for execution completion
   * 
   * Polls execution status until completion or failure
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
}
