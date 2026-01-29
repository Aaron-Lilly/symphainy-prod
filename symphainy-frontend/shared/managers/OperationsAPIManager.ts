/**
 * Operations API Manager (Intent-Based Architecture)
 * 
 * Operations Realm API client using Experience Plane Client and Runtime-based intent submission.
 * 
 * NAMING NOTE:
 * - Backend: "Operations Realm" (handles SOPs, workflows, process optimization)
 * - Frontend State Key: "journey" (internal implementation detail, may be renamed later)
 * - Frontend API Manager: "OperationsAPIManager" (this file)
 * 
 * The state key "journey" is used internally for backwards compatibility but represents
 * the Operations Realm data. This aligns with the vocabulary: "journey" = user journey
 * through pillars (platform concept), "operations" = realm for SOPs/workflows.
 * 
 * Architecture:
 * - All operations via Experience Plane Client
 * - Intent submission to Runtime
 * - Execution tracking via PlatformStateProvider
 * 
 * Replaces direct API calls with Runtime-based intent flow.
 */

import { ExperiencePlaneClient, getGlobalExperiencePlaneClient, ExecutionStatusResponse } from "@/shared/services/ExperiencePlaneClient";
import { usePlatformState } from "@/shared/state/PlatformStateProvider";
import { validateSession } from "@/shared/utils/sessionValidation";

// ============================================
// Operations API Manager Types
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

/**
 * Optimized SOP structure (from optimize_coexistence_with_content)
 */
export interface OptimizedSOP {
  sop_id?: string;
  content?: string;
  optimizations_applied?: string[];
  sections?: Array<{ title: string; content: string }>;
}

/**
 * Optimized workflow structure (from optimize_coexistence_with_content)
 */
export interface OptimizedWorkflow {
  workflow_id?: string;
  name?: string;
  steps?: Array<{ id: string; name: string; type: string }>;
  optimizations_applied?: string[];
}

/**
 * Coexistence blueprint result structure
 */
export interface CoexistenceBlueprintResult {
  blueprint_id?: string;
  summary?: string;
  recommendations?: string[];
  visualization?: string;
}

/**
 * Draft SOP from wizard conversation
 */
export interface WizardDraftSOP {
  draft_id?: string;
  title?: string;
  content?: string;
  sections?: Array<{ title: string; content: string }>;
  status?: 'draft' | 'review' | 'approved';
}

/**
 * Query result SOP structure
 */
export interface QueryResultSOP {
  sop_id?: string;
  title?: string;
  content?: string;
  relevance_score?: number;
}

/**
 * Query result workflow structure
 */
export interface QueryResultWorkflow {
  workflow_id?: string;
  name?: string;
  steps?: Array<{ id: string; name: string; type: string }>;
  relevance_score?: number;
}

/**
 * User intent analysis result
 */
export interface IntentAnalysisResult {
  intent_type?: string;
  confidence?: number;
  suggested_pillar?: string;
  suggested_actions?: string[];
  parameters?: Record<string, unknown>;
}

/**
 * Journey guidance result
 */
export interface JourneyGuidanceResult {
  current_phase?: string;
  progress_percentage?: number;
  recommendations?: string[];
  blockers?: string[];
  completed_steps?: string[];
}

/**
 * Conversation history message structure
 */
export interface ConversationHistoryMessage {
  role?: 'user' | 'assistant' | 'system';
  content?: string;
  timestamp?: string;
  metadata?: Record<string, unknown>;
}

/**
 * Pillar agent response structure
 */
export interface PillarAgentResponse {
  content?: string;
  suggested_actions?: string[];
  artifacts?: string[];
  metadata?: Record<string, unknown>;
}

/**
 * Pillar conversation structure
 */
export interface PillarConversation {
  conversation_id?: string;
  pillar?: string;
  messages?: ConversationHistoryMessage[];
  started_at?: string;
  last_activity?: string;
}

// ============================================
// Operations API Manager Class
// ============================================

/**
 * Operations Realm API Manager
 * 
 * Uses intent-based architecture to communicate with the Operations Realm
 * via Runtime. All operations go through submitIntent → Runtime → Operations Realm.
 * 
 * State is stored under the "journey" key in realm state for backwards compatibility.
 */
export class OperationsAPIManager {
  private experiencePlaneClient: ExperiencePlaneClient;
  private getPlatformState: () => ReturnType<typeof usePlatformState>;

  // Internal state key - "journey" for backwards compatibility
  // This represents Operations Realm data in PlatformStateProvider
  private static readonly REALM_STATE_KEY = "journey" as const;

  constructor(
    experiencePlaneClient?: ExperiencePlaneClient,
    getPlatformState?: () => ReturnType<typeof usePlatformState>
  ) {
    this.experiencePlaneClient = experiencePlaneClient || getGlobalExperiencePlaneClient();
    // Note: getPlatformState will be provided by components using the hook
    this.getPlatformState = getPlatformState || (() => {
      throw new Error("PlatformStateProvider not available. Use OperationsAPIManager with usePlatformState hook.");
    });
  }

  /**
   * Optimize process (optimize_process intent)
   * 
   * Flow: Experience Plane → Runtime → Operations Realm
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
        const optimizedProcess = result.artifacts.optimized_process as {
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
        
        // Update realm state (using internal key "journey" for Operations Realm data)
        platformState.setRealmState(OperationsAPIManager.REALM_STATE_KEY, "optimizedProcesses", {
          ...platformState.getRealmState(OperationsAPIManager.REALM_STATE_KEY, "optimizedProcesses") || {},
          [workflowId]: optimizedProcess
        });

        return {
          success: true,
          optimized_process: optimizedProcess
        };
      } else {
        throw new Error(result.error || "Failed to optimize process");
      }
    } catch (error) {
      console.error("[OperationsAPIManager] Error optimizing process:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Generate SOP (generate_sop intent)
   * 
   * Flow: Experience Plane → Runtime → Operations Realm
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
        const sop = result.artifacts.sop as {
          sop_id: string;
          title: string;
          content: string;
          sections: { title: string; content: string; }[];
          metadata?: Record<string, unknown>;
        };
        
        // Update realm state
        platformState.setRealmState(OperationsAPIManager.REALM_STATE_KEY, "sops", {
          ...platformState.getRealmState(OperationsAPIManager.REALM_STATE_KEY, "sops") || {},
          [workflowId]: sop
        });

        return {
          success: true,
          sop
        };
      } else {
        throw new Error(result.error || "Failed to generate SOP");
      }
    } catch (error) {
      console.error("[OperationsAPIManager] Error generating SOP:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Create workflow (create_workflow intent)
   * 
   * Flow: Experience Plane → Runtime → Operations Realm
   */
  async createWorkflow(
    sopId: string,
    workflowOptions?: Record<string, any>
  ): Promise<WorkflowCreationResponse> {
    try {
      const platformState = this.getPlatformState();
      
      validateSession(platformState, "create workflow");

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
        const workflow = result.artifacts.workflow as {
          workflow_id: string;
          name: string;
          steps: { id: string; name: string; type: string; dependencies?: string[]; }[];
          metadata?: Record<string, unknown>;
        };
        
        // Update realm state
        platformState.setRealmState(OperationsAPIManager.REALM_STATE_KEY, "workflows", {
          ...platformState.getRealmState(OperationsAPIManager.REALM_STATE_KEY, "workflows") || {},
          [sopId]: workflow
        });

        return {
          success: true,
          workflow
        };
      } else {
        throw new Error(result.error || "Failed to create workflow");
      }
    } catch (error) {
      console.error("[OperationsAPIManager] Error creating workflow:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Optimize coexistence with content (optimize_coexistence_with_content intent)
   * 
   * Flow: Experience Plane → Runtime → Operations Realm
   */
  async optimizeCoexistenceWithContent(
    sopContent: string,
    workflowContent: string
  ): Promise<{
    success: boolean;
    optimized_sop?: OptimizedSOP;
    optimized_workflow?: OptimizedWorkflow;
    blueprint?: CoexistenceBlueprintResult;
    error?: string;
  }> {
    try {
      const platformState = this.getPlatformState();
      
      validateSession(platformState, "optimize coexistence");

      if (!sopContent || !workflowContent) {
        throw new Error("SOP content and workflow content are required for optimization");
      }

      // Submit intent via Runtime (not direct API call)
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
        const optimizedData = result.artifacts.optimized_coexistence as {
          optimized_sop?: unknown;
          optimized_workflow?: unknown;
          blueprint?: unknown;
        };
        
        // Update realm state
        platformState.setRealmState(OperationsAPIManager.REALM_STATE_KEY, "operations", {
          ...platformState.getRealmState(OperationsAPIManager.REALM_STATE_KEY, "operations") || {},
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
      console.error("[OperationsAPIManager] Error optimizing coexistence:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Analyze coexistence (analyze_coexistence intent)
   * 
   * Flow: Experience Plane → Runtime → Operations Realm
   */
  async analyzeCoexistence(
    sopId: string,
    workflowId: string,
    analysisOptions?: Record<string, any>
  ): Promise<CoexistenceAnalysisResponse> {
    try {
      const platformState = this.getPlatformState();
      
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
        const coexistenceAnalysis = result.artifacts.coexistence_analysis as {
          analysis_id: string;
          [key: string]: unknown;
        };
        
        // Update realm state
        platformState.setRealmState(OperationsAPIManager.REALM_STATE_KEY, "coexistenceAnalyses", {
          ...platformState.getRealmState(OperationsAPIManager.REALM_STATE_KEY, "coexistenceAnalyses") || {},
          [coexistenceAnalysis.analysis_id]: coexistenceAnalysis
        });

        return {
          success: true,
          coexistence_analysis: coexistenceAnalysis as CoexistenceAnalysisResponse["coexistence_analysis"]
        };
      } else {
        throw new Error(result.error || "Failed to analyze coexistence");
      }
    } catch (error) {
      console.error("[OperationsAPIManager] Error analyzing coexistence:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Create blueprint (create_blueprint intent)
   * 
   * Flow: Experience Plane → Runtime → Operations Realm
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
      
      validateSession(platformState, "create blueprint");

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
        const blueprint = result.artifacts.blueprint as {
          blueprint_id: string;
          [key: string]: unknown;
        };
        
        // Update realm state
        platformState.setRealmState(OperationsAPIManager.REALM_STATE_KEY, "blueprints", {
          ...platformState.getRealmState(OperationsAPIManager.REALM_STATE_KEY, "blueprints") || {},
          [blueprint.blueprint_id]: blueprint
        });

        return {
          success: true,
          blueprint: blueprint as BlueprintCreationResponse["blueprint"]
        };
      } else {
        throw new Error(result.error || "Failed to create blueprint");
      }
    } catch (error) {
      console.error("[OperationsAPIManager] Error creating blueprint:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Process operations conversation (process_operations_conversation intent)
   * 
   * Flow: Experience Plane → Runtime → Operations Realm
   */
  async processOperationsConversation(
    message: string,
    conversationId: string,
    context?: Record<string, any>
  ): Promise<{ success: boolean; message?: string; error?: string }> {
    try {
      const platformState = this.getPlatformState();
      
      validateSession(platformState, "process operations conversation");

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
        const conversationResponse = result.artifacts.conversation_response as { message?: string };
        return {
          success: true,
          message: conversationResponse.message
        };
      } else {
        throw new Error(result.error || "Failed to process operations conversation");
      }
    } catch (error) {
      console.error("[OperationsAPIManager] Error processing operations conversation:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Process wizard conversation (process_wizard_conversation intent)
   * 
   * Flow: Experience Plane → Runtime → Operations Realm
   */
  async processWizardConversation(
    message: string,
    sessionId: string,
    context?: Record<string, unknown>
  ): Promise<{ success: boolean; agent_response?: string; draft_sop?: WizardDraftSOP; error?: string }> {
    try {
      const platformState = this.getPlatformState();
      
      validateSession(platformState, "process wizard conversation");

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
        const wizardResponse = result.artifacts.wizard_response as { agent_response?: string; draft_sop?: unknown };
        return {
          success: true,
          agent_response: wizardResponse.agent_response,
          draft_sop: wizardResponse.draft_sop
        };
      } else {
        throw new Error(result.error || "Failed to process wizard conversation");
      }
    } catch (error) {
      console.error("[OperationsAPIManager] Error processing wizard conversation:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Process operations query (process_operations_query intent)
   * 
   * Flow: Experience Plane → Runtime → Operations Realm
   */
  async processOperationsQuery(
    query: string,
    sessionId: string,
    context?: Record<string, unknown>
  ): Promise<{ success: boolean; sop?: QueryResultSOP; workflow?: QueryResultWorkflow; error?: string }> {
    try {
      const platformState = this.getPlatformState();
      
      validateSession(platformState, "process operations query");

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
        const queryResponse = result.artifacts.query_response as { sop?: unknown; workflow?: unknown };
        return {
          success: true,
          sop: queryResponse.sop,
          workflow: queryResponse.workflow
        };
      } else {
        throw new Error(result.error || "Failed to process operations query");
      }
    } catch (error) {
      console.error("[OperationsAPIManager] Error processing operations query:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Analyze user intent (analyze_user_intent intent)
   * 
   * Flow: Experience Plane → Runtime → Operations Realm (Guide Agent)
   */
  async analyzeUserIntent(
    message: string,
    context?: Record<string, unknown>
  ): Promise<{ success: boolean; intent_analysis?: IntentAnalysisResult; error?: string }> {
    try {
      const platformState = this.getPlatformState();
      
      validateSession(platformState, "analyze user intent");

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
          intent_analysis: result.artifacts.intent_analysis as unknown
        };
      } else {
        throw new Error(result.error || "Failed to analyze user intent");
      }
    } catch (error) {
      console.error("[OperationsAPIManager] Error analyzing user intent:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Get journey guidance (get_journey_guidance intent)
   * 
   * NOTE: "journey" here refers to user journey (platform concept), not the old realm name.
   * 
   * Flow: Experience Plane → Runtime → Operations Realm (Guide Agent)
   */
  async getJourneyGuidance(
    userGoal: string,
    currentStep?: string,
    context?: Record<string, unknown>
  ): Promise<{ success: boolean; guidance?: JourneyGuidanceResult; next_steps?: string[]; error?: string }> {
    try {
      const platformState = this.getPlatformState();
      
      validateSession(platformState, "get journey guidance");

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
        const journeyGuidance = result.artifacts.journey_guidance as { guidance?: unknown; next_steps?: string[] };
        return {
          success: true,
          guidance: journeyGuidance.guidance,
          next_steps: journeyGuidance.next_steps
        };
      } else {
        throw new Error(result.error || "Failed to get journey guidance");
      }
    } catch (error) {
      console.error("[OperationsAPIManager] Error getting journey guidance:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Get conversation history (get_conversation_history intent)
   * 
   * Flow: Experience Plane → Runtime → Operations Realm (Guide Agent)
   */
  async getConversationHistory(
    sessionId: string
  ): Promise<{ success: boolean; conversation_history?: ConversationHistoryMessage[]; error?: string }> {
    try {
      const platformState = this.getPlatformState();
      
      validateSession(platformState, "get conversation history");

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
          conversation_history: result.artifacts.conversation_history as unknown[]
        };
      } else {
        throw new Error(result.error || "Failed to get conversation history");
      }
    } catch (error) {
      console.error("[OperationsAPIManager] Error getting conversation history:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Send message to pillar agent (send_message_to_pillar_agent intent)
   * 
   * Flow: Experience Plane → Runtime → Appropriate Realm (based on pillar)
   */
  async sendMessageToPillarAgent(
    message: string,
    pillar: 'content' | 'insights' | 'operations' | 'outcomes',
    conversationId?: string,
    context?: Record<string, unknown>
  ): Promise<{ success: boolean; response?: PillarAgentResponse; error?: string }> {
    try {
      const platformState = this.getPlatformState();
      
      validateSession(platformState, "send message to pillar agent");

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
      console.error("[OperationsAPIManager] Error sending message to pillar agent:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Get pillar conversation history (get_pillar_conversation_history intent)
   * 
   * Flow: Experience Plane → Runtime → Appropriate Realm (based on pillar)
   */
  async getPillarConversationHistory(
    sessionId: string,
    pillar: 'content' | 'insights' | 'operations' | 'outcomes'
  ): Promise<{ success: boolean; conversation?: PillarConversation; error?: string }> {
    try {
      const platformState = this.getPlatformState();
      
      validateSession(platformState, "get pillar conversation history");

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
      console.error("[OperationsAPIManager] Error getting pillar conversation history:", error);
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
  ): Promise<ExecutionStatusResponse> {
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
