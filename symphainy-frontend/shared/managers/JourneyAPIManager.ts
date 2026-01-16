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
      
      if (!platformState.state.session.sessionId || !platformState.state.session.tenantId) {
        throw new Error("Session required to create workflow");
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
      
      if (!platformState.state.session.sessionId || !platformState.state.session.tenantId) {
        throw new Error("Session required to analyze coexistence");
      }

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
      
      if (!platformState.state.session.sessionId || !platformState.state.session.tenantId) {
        throw new Error("Session required to create blueprint");
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
