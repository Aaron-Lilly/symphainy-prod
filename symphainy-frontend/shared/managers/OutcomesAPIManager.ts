/**
 * Outcomes API Manager (New Architecture)
 * 
 * Outcomes Realm API client using Experience Plane Client and Runtime-based intent submission.
 * 
 * Architecture:
 * - All operations via Experience Plane Client
 * - Intent submission to Runtime
 * - Execution tracking via PlatformStateProvider
 * 
 * Replaces direct API calls with Runtime-based intent flow.
 * 
 * Note: Frontend uses "Business Outcomes" naming, backend uses "outcomes" realm.
 */

import { ExperiencePlaneClient, getGlobalExperiencePlaneClient, ExecutionStatusResponse } from "@/shared/services/ExperiencePlaneClient";
import { usePlatformState } from "@/shared/state/PlatformStateProvider";
import { ensureArtifactLifecycle } from "@/shared/services/artifactLifecycle";
import { validateSession } from "@/shared/utils/sessionValidation";

// ============================================
// Outcomes API Manager Types
// ============================================

export interface OutcomeSynthesisResponse {
  success: boolean;
  synthesis?: {
    synthesis_id: string;
    content_summary?: string;
    insights_summary?: string;
    journey_summary?: string;
    overall_synthesis: string;
    report?: {
      report_id: string;
      report_type: string;
      content: string;
      format: string;
    };
  };
  error?: string;
}

export interface RoadmapGenerationResponse {
  success: boolean;
  roadmap?: {
    roadmap_id: string;
    goals: string[];
    status: string;
    plan: Array<{
      phase: string;
      description: string;
    }>;
    metrics?: {
      estimated_duration_weeks?: number;
      estimated_cost_usd?: number;
    };
    generated_at: string;
  };
  error?: string;
}

export interface POCCreationResponse {
  success: boolean;
  poc_proposal?: {
    poc_id: string;
    description: string;
    status: string;
    objectives: string[];
    scope: string;
    deliverables: string[];
    estimated_duration_weeks: number;
    generated_at: string;
  };
  error?: string;
}

export interface SolutionCreationResponse {
  success: boolean;
  platform_solution?: {
    solution_id: string;
    name?: string;
    description?: string;
    domain_bindings?: Array<{
      domain: string;
      system_name: string;
      adapter_type: string;
    }>;
    intents?: string[];
    metadata?: Record<string, any>;
  };
  error?: string;
}

// ============================================
// Outcomes API Manager Class
// ============================================

export class OutcomesAPIManager {
  private experiencePlaneClient: ExperiencePlaneClient;
  private getPlatformState: () => ReturnType<typeof usePlatformState>;

  constructor(
    experiencePlaneClient?: ExperiencePlaneClient,
    getPlatformState?: () => ReturnType<typeof usePlatformState>
  ) {
    this.experiencePlaneClient = experiencePlaneClient || getGlobalExperiencePlaneClient();
    // Note: getPlatformState will be provided by components using the hook
    this.getPlatformState = getPlatformState || (() => {
      throw new Error("PlatformStateProvider not available. Use OutcomesAPIManager with usePlatformState hook.");
    });
  }

  /**
   * Synthesize outcome (synthesize_outcome intent)
   * 
   * Flow: Experience Plane → Runtime → Outcomes Realm
   */
  async synthesizeOutcome(
    synthesisOptions?: Record<string, any>
  ): Promise<OutcomeSynthesisResponse> {
    try {
      const platformState = this.getPlatformState();
      
      // ✅ FIX ISSUE 4: Use standardized session validation
      validateSession(platformState, "synthesize outcome");

      // ✅ FIX ISSUE 3: Parameter validation before submitIntent
      // synthesize_outcome doesn't require parameters (uses synthesis_options which can be empty)
      // No validation needed - empty object is acceptable

      // Submit intent via Experience Plane Client
      const execution = await platformState.submitIntent(
        "synthesize_outcome",
        {
          synthesis_options: synthesisOptions || {}
        }
      );

      // Wait for execution completion
      const result = await this._waitForExecution(execution, platformState);

      if (result.status === "completed" && result.artifacts?.synthesis_summary) {
        const synthesisSummary = result.artifacts.synthesis_summary as { synthesis_id?: string; [key: string]: unknown };
        
        // Update realm state
        platformState.setRealmState("outcomes", "syntheses", {
          ...platformState.getRealmState("outcomes", "syntheses") || {},
          [synthesisSummary.synthesis_id || "latest"]: synthesisSummary
        });

        return {
          success: true,
          synthesis: synthesisSummary as OutcomeSynthesisResponse["synthesis"]
        };
      } else {
        throw new Error(result.error || "Failed to synthesize outcome");
      }
    } catch (error) {
      console.error("[OutcomesAPIManager] Error synthesizing outcome:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Generate roadmap (generate_roadmap intent)
   * 
   * Flow: Experience Plane → Runtime → Outcomes Realm
   */
  async generateRoadmap(
    goals: string[],
    roadmapOptions?: Record<string, any>
  ): Promise<RoadmapGenerationResponse> {
    try {
      const platformState = this.getPlatformState();
      
      if (!platformState.state.session.sessionId || !platformState.state.session.tenantId) {
        throw new Error("Session required to generate roadmap");
      }

      // ✅ FIX ISSUE 3: Parameter validation before submitIntent
      if (!goals || goals.length === 0) {
        throw new Error("goals array is required for generate_roadmap");
      }

      // Submit intent via Experience Plane Client
      const execution = await platformState.submitIntent(
        "generate_roadmap",
        {
          goals,
          roadmap_options: roadmapOptions || {}
        }
      );

      // Wait for execution completion
      const result = await this._waitForExecution(execution, platformState);

      if (result.status === "completed" && result.artifacts?.roadmap) {
        // ✅ PHASE 5.3: Ensure artifact has lifecycle state (purpose, scope, owner)
        const rawRoadmap = result.artifacts.roadmap as { roadmap_id: string; [key: string]: unknown };
        const roadmapId = rawRoadmap.roadmap_id;
        const lifecycleInfo = ensureArtifactLifecycle(
          rawRoadmap,
          'strategic_planning',
          'business_transformation',
          platformState.state.session.userId || 'system'
        );
        
        // Combine original roadmap properties with lifecycle info for state storage
        const roadmapWithLifecycle = {
          ...rawRoadmap,
          ...lifecycleInfo
        };
        
        // Update realm state
        platformState.setRealmState("outcomes", "roadmaps", {
          ...platformState.getRealmState("outcomes", "roadmaps") || {},
          [roadmapId]: roadmapWithLifecycle
        });

        // Return the roadmap with its original shape for API response
        return {
          success: true,
          roadmap: rawRoadmap as RoadmapGenerationResponse['roadmap']
        };
      } else {
        throw new Error(result.error || "Failed to generate roadmap");
      }
    } catch (error) {
      console.error("[OutcomesAPIManager] Error generating roadmap:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Create POC (create_poc intent)
   * 
   * Flow: Experience Plane → Runtime → Outcomes Realm
   */
  async createPOC(
    description: string,
    pocOptions?: Record<string, any>
  ): Promise<POCCreationResponse> {
    try {
      const platformState = this.getPlatformState();
      
      // ✅ FIX ISSUE 4: Use standardized session validation
      validateSession(platformState, "create POC");

      if (!description) {
        throw new Error("Description is required for POC creation");
      }

      // Submit intent via Experience Plane Client
      const execution = await platformState.submitIntent(
        "create_poc",
        {
          description,
          poc_options: pocOptions || {}
        }
      );

      // Wait for execution completion
      const result = await this._waitForExecution(execution, platformState);

      if (result.status === "completed" && result.artifacts?.poc_proposal) {
        // ✅ PHASE 5.3: Ensure artifact has lifecycle state (purpose, scope, owner)
        const pocProposal = result.artifacts.poc_proposal as { poc_id: string; [key: string]: unknown };
        const pocWithLifecycle = ensureArtifactLifecycle(
          pocProposal,
          'proof_of_concept',
          'validation',
          platformState.state.session.userId || 'system'
        );
        
        // Update realm state
        platformState.setRealmState("outcomes", "pocProposals", {
          ...platformState.getRealmState("outcomes", "pocProposals") || {},
          [pocProposal.poc_id]: pocWithLifecycle
        });

        return {
          success: true,
          poc_proposal: pocProposal as POCCreationResponse["poc_proposal"]
        };
      } else {
        throw new Error(result.error || "Failed to create POC");
      }
    } catch (error) {
      console.error("[OutcomesAPIManager] Error creating POC:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Create solution (create_solution intent)
   * 
   * Flow: Experience Plane → Runtime → Outcomes Realm
   */
  /**
   * Create blueprint (create_blueprint intent)
   * 
   * Flow: Experience Plane → Runtime → Outcomes Realm
   */
  async createBlueprint(
    workflowId: string,
    currentStateWorkflowId?: string
  ): Promise<{ success: boolean; blueprint?: any; blueprint_id?: string; error?: string }> {
    try {
      const platformState = this.getPlatformState();
      
      // ✅ FIX ISSUE 4: Use standardized session validation
      validateSession(platformState, "create blueprint");

      if (!workflowId) {
        throw new Error("workflow_id is required for blueprint creation");
      }

      // Submit intent via Experience Plane Client
      const execution = await platformState.submitIntent(
        "create_blueprint",
        {
          workflow_id: workflowId,
          current_state_workflow_id: currentStateWorkflowId
        }
      );

      // Wait for execution completion
      const result = await this._waitForExecution(execution, platformState);

      if (result.status === "completed" && result.artifacts?.blueprint) {
        // ✅ PHASE 5.3: Ensure artifact has lifecycle state (purpose, scope, owner)
        const blueprint = result.artifacts.blueprint as { blueprint_id?: string; [key: string]: unknown };
        const blueprintId = blueprint.blueprint_id || (result.artifacts.blueprint_id as string | undefined) || "unknown";
        const blueprintWithLifecycle = ensureArtifactLifecycle(
          blueprint,
          'coexistence_planning',
          'workflow_optimization',
          platformState.state.session.userId || 'system'
        );
        
        // Update realm state
        platformState.setRealmState("outcomes", "blueprints", {
          ...platformState.getRealmState("outcomes", "blueprints") || {},
          [blueprintId]: blueprintWithLifecycle
        });

        return {
          success: true,
          blueprint: blueprintWithLifecycle,
          blueprint_id: blueprintId
        };
      } else {
        throw new Error(result.error || "Failed to create blueprint");
      }
    } catch (error) {
      console.error("[OutcomesAPIManager] Error creating blueprint:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Export artifact (export_artifact intent)
   * 
   * Flow: Experience Plane → Runtime → Outcomes Realm
   */
  async exportArtifact(
    artifactType: "blueprint" | "poc" | "roadmap",
    artifactId: string,
    format: "json" | "docx" | "yaml" = "json"
  ): Promise<{ success: boolean; download_url?: string; filename?: string; error?: string }> {
    try {
      const platformState = this.getPlatformState();
      
      if (!platformState.state.session.sessionId || !platformState.state.session.tenantId) {
        throw new Error("Session required to export artifact");
      }

      if (!artifactType || !artifactId) {
        throw new Error("artifact_type and artifact_id are required for export");
      }

      // Submit intent via Experience Plane Client
      const execution = await platformState.submitIntent(
        "export_artifact",
        {
          artifact_type: artifactType,
          artifact_id: artifactId,
          export_format: format
        }
      );

      // Wait for execution completion
      const result = await this._waitForExecution(execution, platformState);

      if (result.status === "completed" && result.artifacts?.export) {
        const exportResult = result.artifacts.export as { download_url?: string; filename?: string };
        
        return {
          success: true,
          download_url: exportResult.download_url,
          filename: exportResult.filename
        };
      } else {
        throw new Error(result.error || "Failed to export artifact");
      }
    } catch (error) {
      console.error("[OutcomesAPIManager] Error exporting artifact:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  async createSolution(
    solutionSource: "roadmap" | "poc" | "blueprint",
    sourceId: string,
    sourceData: any,
    solutionOptions?: Record<string, any>
  ): Promise<SolutionCreationResponse> {
    try {
      const platformState = this.getPlatformState();
      
      // ✅ FIX ISSUE 4: Use standardized session validation
      validateSession(platformState, "create solution");

      if (!solutionSource || !sourceId || !sourceData) {
        throw new Error("solution_source, source_id, and source_data are required for solution creation");
      }

      // Submit intent via Experience Plane Client
      const execution = await platformState.submitIntent(
        "create_solution",
        {
          solution_source: solutionSource,
          source_id: sourceId,
          source_data: sourceData,
          solution_options: solutionOptions || {}
        }
      );

      // Wait for execution completion
      const result = await this._waitForExecution(execution, platformState);

      if (result.status === "completed" && result.artifacts?.platform_solution) {
        // Update realm state
        const platformSolution = result.artifacts.platform_solution as { solution_id: string; [key: string]: unknown };
        platformState.setRealmState("outcomes", "solutions", {
          ...platformState.getRealmState("outcomes", "solutions") || {},
          [platformSolution.solution_id]: platformSolution
        });

        return {
          success: true,
          platform_solution: platformSolution as SolutionCreationResponse["platform_solution"]
        };
      } else {
        throw new Error(result.error || "Failed to create solution");
      }
    } catch (error) {
      console.error("[OutcomesAPIManager] Error creating solution:", error);
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
