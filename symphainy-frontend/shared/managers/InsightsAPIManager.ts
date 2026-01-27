/**
 * Insights API Manager (New Architecture)
 * 
 * Insights Realm API client using Experience Plane Client and Runtime-based intent submission.
 * 
 * Architecture:
 * - All operations via Experience Plane Client
 * - Intent submission to Runtime
 * - Execution tracking via PlatformStateProvider
 * 
 * Replaces direct API calls with Runtime-based intent flow.
 */

import { ExperiencePlaneClient, getGlobalExperiencePlaneClient } from "@/shared/services/ExperiencePlaneClient";
import { usePlatformState } from "@/shared/state/PlatformStateProvider";
import { validateSession } from "@/shared/utils/sessionValidation";

// ============================================
// Insights API Manager Types
// ============================================

export interface QualityAssessment {
  quality_score: number;
  completeness: number;
  accuracy: number;
  consistency: number;
  issues: Array<{
    type: string;
    severity: "low" | "medium" | "high";
    message: string;
    recommendation?: string;
  }>;
  metadata?: Record<string, any>;
}

export interface QualityAssessmentResponse {
  success: boolean;
  quality_assessment?: QualityAssessment;
  parsed_file_id?: string;
  source_file_id?: string;
  error?: string;
}

export interface InterpretationResult {
  interpretation_type: "self_discovery" | "guided";
  entities: Array<{
    name: string;
    type: string;
    attributes?: Record<string, any>;
  }>;
  relationships: Array<{
    source: string;
    target: string;
    type: string;
    attributes?: Record<string, any>;
  }>;
  confidence_score?: number;
  coverage_score?: number;
  metadata?: Record<string, any>;
}

export interface InterpretationResponse {
  success: boolean;
  interpretation?: InterpretationResult;
  parsed_file_id?: string;
  guide_id?: string;
  error?: string;
}

export interface AnalysisResult {
  analysis_type: "structured" | "unstructured";
  summary: string;
  insights: Array<{
    type: string;
    description: string;
    confidence?: number;
  }>;
  visualizations?: Array<{
    type: string;
    data: any;
    url?: string;
  }>;
  deep_dive?: {
    session_id?: string;
    initiated: boolean;
  };
  metadata?: Record<string, any>;
}

export interface AnalysisResponse {
  success: boolean;
  analysis?: AnalysisResult;
  parsed_file_id?: string;
  error?: string;
}

export interface LineageVisualization {
  visualization_type: "lineage_graph";
  image_base64?: string;
  storage_path?: string;
  lineage_graph: {
    nodes: Array<{
      id: string;
      label: string;
      type: "file" | "parsed_result" | "embedding" | "interpretation" | "analysis" | "guide" | "agent_session";
      [key: string]: any;
    }>;
    edges: Array<{
      source: string;
      target: string;
      type: string;
    }>;
    file_id: string;
    tenant_id: string;
  };
  metadata?: Record<string, any>;
}

export interface LineageVisualizationResponse {
  success: boolean;
  visualization?: LineageVisualization;
  file_id?: string;
  error?: string;
}

export interface RelationshipMapping {
  entities?: Array<{
    name: string;
    type: string;
    attributes?: Record<string, any>;
  }>;
  relationships?: Array<{
    source: string;
    target: string;
    type: string;
    confidence?: number;
    attributes?: Record<string, any>;
  }>;
}

export interface RelationshipMappingResponse {
  success: boolean;
  relationships?: RelationshipMapping;
  file_id?: string;
  error?: string;
}

// ============================================
// Insights API Manager Class
// ============================================

export class InsightsAPIManager {
  private experiencePlaneClient: ExperiencePlaneClient;
  private getPlatformState: () => ReturnType<typeof usePlatformState>;

  constructor(
    experiencePlaneClient?: ExperiencePlaneClient,
    getPlatformState?: () => ReturnType<typeof usePlatformState>
  ) {
    this.experiencePlaneClient = experiencePlaneClient || getGlobalExperiencePlaneClient();
    // Note: getPlatformState will be provided by components using the hook
    this.getPlatformState = getPlatformState || (() => {
      throw new Error("PlatformStateProvider not available. Use InsightsAPIManager with usePlatformState hook.");
    });
  }

  /**
   * Assess data quality (assess_data_quality intent)
   * 
   * Flow: Experience Plane → Runtime → Insights Realm
   */
  async assessDataQuality(
    parsedFileId: string,
    sourceFileId: string,
    parserType: string
  ): Promise<QualityAssessmentResponse> {
    try {
      const platformState = this.getPlatformState();
      
      if (!platformState.state.session.sessionId || !platformState.state.session.tenantId) {
        throw new Error("Session required to assess data quality");
      }

      // ✅ FIX ISSUE 3: Parameter validation before submitIntent
      if (!parsedFileId) {
        throw new Error("parsed_file_id is required for assess_data_quality");
      }
      if (!sourceFileId) {
        throw new Error("source_file_id is required for assess_data_quality");
      }
      if (!parserType) {
        throw new Error("parser_type is required for assess_data_quality");
      }

      // Submit intent via Experience Plane Client
      const execution = await platformState.submitIntent(
        "assess_data_quality",
        {
          parsed_file_id: parsedFileId,
          source_file_id: sourceFileId,
          parser_type: parserType
        }
      );

      // Wait for execution completion
      const result = await this._waitForExecution(execution, platformState);

      if (result.status === "completed" && result.artifacts?.quality_assessment) {
        // Update realm state
        platformState.setRealmState("insights", "qualityAssessments", {
          ...platformState.getRealmState("insights", "qualityAssessments") || {},
          [parsedFileId]: result.artifacts.quality_assessment
        });

        return {
          success: true,
          quality_assessment: result.artifacts.quality_assessment,
          parsed_file_id: parsedFileId,
          source_file_id: sourceFileId
        };
      } else {
        throw new Error(result.error || "Failed to assess data quality");
      }
    } catch (error) {
      console.error("[InsightsAPIManager] Error assessing data quality:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Interpret data with self-discovery (interpret_data_self_discovery intent)
   * 
   * Flow: Experience Plane → Runtime → Insights Realm
   */
  async interpretDataSelfDiscovery(
    parsedFileId: string,
    discoveryOptions?: Record<string, any>
  ): Promise<InterpretationResponse> {
    try {
      const platformState = this.getPlatformState();
      
      // ✅ FIX ISSUE 4: Use standardized session validation
      validateSession(platformState, "interpret data (self-discovery)");

      // ✅ FIX ISSUE 3: Parameter validation before submitIntent
      if (!parsedFileId) {
        throw new Error("parsed_file_id is required for interpret_data_self_discovery");
      }

      // Submit intent via Experience Plane Client
      const execution = await platformState.submitIntent(
        "interpret_data_self_discovery",
        {
          parsed_file_id: parsedFileId,
          discovery_options: discoveryOptions || {}
        }
      );

      // Wait for execution completion
      const result = await this._waitForExecution(execution, platformState);

      if (result.status === "completed" && result.artifacts?.discovery) {
        // Update realm state
        platformState.setRealmState("insights", "interpretations", {
          ...platformState.getRealmState("insights", "interpretations") || {},
          [parsedFileId]: result.artifacts.discovery
        });

        return {
          success: true,
          interpretation: result.artifacts.discovery,
          parsed_file_id: parsedFileId
        };
      } else {
        throw new Error(result.error || "Failed to interpret data");
      }
    } catch (error) {
      console.error("[InsightsAPIManager] Error interpreting data:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Interpret data with guide (interpret_data_guided intent)
   * 
   * Flow: Experience Plane → Runtime → Insights Realm
   */
  async interpretDataGuided(
    parsedFileId: string,
    guideId: string,
    matchingOptions?: Record<string, any>
  ): Promise<InterpretationResponse> {
    try {
      const platformState = this.getPlatformState();
      
      if (!platformState.state.session.sessionId || !platformState.state.session.tenantId) {
        throw new Error("Session required to interpret data");
      }

      // Submit intent via Experience Plane Client
      const execution = await platformState.submitIntent(
        "interpret_data_guided",
        {
          parsed_file_id: parsedFileId,
          guide_id: guideId,
          matching_options: matchingOptions || {}
        }
      );

      // Wait for execution completion
      const result = await this._waitForExecution(execution, platformState);

      if (result.status === "completed" && result.artifacts?.interpretation) {
        // Update realm state
        platformState.setRealmState("insights", "interpretations", {
          ...platformState.getRealmState("insights", "interpretations") || {},
          [parsedFileId]: result.artifacts.interpretation
        });

        return {
          success: true,
          interpretation: result.artifacts.interpretation,
          parsed_file_id: parsedFileId,
          guide_id: guideId
        };
      } else {
        throw new Error(result.error || "Failed to interpret data with guide");
      }
    } catch (error) {
      console.error("[InsightsAPIManager] Error interpreting data with guide:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Analyze structured data (analyze_structured_data intent)
   * 
   * Flow: Experience Plane → Runtime → Insights Realm
   */
  async analyzeStructuredData(
    parsedFileId: string,
    analysisOptions?: Record<string, any>
  ): Promise<AnalysisResponse> {
    try {
      const platformState = this.getPlatformState();
      
      if (!platformState.state.session.sessionId || !platformState.state.session.tenantId) {
        throw new Error("Session required to analyze data");
      }

      // ✅ FIX ISSUE 3: Parameter validation before submitIntent
      if (!parsedFileId) {
        throw new Error("parsed_file_id is required for analyze_structured_data");
      }

      // Submit intent via Experience Plane Client
      const execution = await platformState.submitIntent(
        "analyze_structured_data",
        {
          parsed_file_id: parsedFileId,
          analysis_options: analysisOptions || {}
        }
      );

      // Wait for execution completion
      const result = await this._waitForExecution(execution, platformState);

      if (result.status === "completed" && result.artifacts?.structured_analysis) {
        // Update realm state
        platformState.setRealmState("insights", "analyses", {
          ...platformState.getRealmState("insights", "analyses") || {},
          [parsedFileId]: result.artifacts.structured_analysis
        });

        return {
          success: true,
          analysis: result.artifacts.structured_analysis,
          parsed_file_id: parsedFileId
        };
      } else {
        throw new Error(result.error || "Failed to analyze structured data");
      }
    } catch (error) {
      console.error("[InsightsAPIManager] Error analyzing structured data:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Analyze unstructured data (analyze_unstructured_data intent)
   * 
   * Flow: Experience Plane → Runtime → Insights Realm
   */
  async analyzeUnstructuredData(
    parsedFileId: string,
    analysisOptions?: Record<string, any>
  ): Promise<AnalysisResponse> {
    try {
      const platformState = this.getPlatformState();
      
      // ✅ FIX ISSUE 4: Use standardized session validation
      validateSession(platformState, "analyze unstructured data");

      // ✅ FIX ISSUE 3: Parameter validation before submitIntent
      if (!parsedFileId) {
        throw new Error("parsed_file_id is required for analyze_unstructured_data");
      }

      // Submit intent via Experience Plane Client
      const execution = await platformState.submitIntent(
        "analyze_unstructured_data",
        {
          parsed_file_id: parsedFileId,
          analysis_options: analysisOptions || {}
        }
      );

      // Wait for execution completion
      const result = await this._waitForExecution(execution, platformState);

      if (result.status === "completed" && result.artifacts?.unstructured_analysis) {
        // Update realm state
        platformState.setRealmState("insights", "analyses", {
          ...platformState.getRealmState("insights", "analyses") || {},
          [parsedFileId]: result.artifacts.unstructured_analysis
        });

        return {
          success: true,
          analysis: result.artifacts.unstructured_analysis,
          parsed_file_id: parsedFileId
        };
      } else {
        throw new Error(result.error || "Failed to analyze unstructured data");
      }
    } catch (error) {
      console.error("[InsightsAPIManager] Error analyzing unstructured data:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Visualize lineage (visualize_lineage intent) - "Your Data Mash"
   * 
   * Flow: Experience Plane → Runtime → Insights Realm
   */
  async visualizeLineage(
    fileId: string
  ): Promise<LineageVisualizationResponse> {
    try {
      const platformState = this.getPlatformState();
      
      // ✅ FIX ISSUE 4: Use standardized session validation
      validateSession(platformState, "visualize lineage");

      // ✅ FIX ISSUE 3: Parameter validation before submitIntent
      if (!fileId) {
        throw new Error("file_id is required for visualize_lineage");
      }

      // Submit intent via Experience Plane Client
      const execution = await platformState.submitIntent(
        "visualize_lineage",
        {
          file_id: fileId
        }
      );

      // Wait for execution completion
      const result = await this._waitForExecution(execution, platformState);

      if (result.status === "completed" && result.artifacts?.lineage_visualization) {
        // Update realm state
        platformState.setRealmState("insights", "lineageVisualizations", {
          ...platformState.getRealmState("insights", "lineageVisualizations") || {},
          [fileId]: result.artifacts.lineage_visualization
        });

        return {
          success: true,
          visualization: result.artifacts.lineage_visualization,
          file_id: fileId
        };
      } else {
        throw new Error(result.error || "Failed to visualize lineage");
      }
    } catch (error) {
      console.error("[InsightsAPIManager] Error visualizing lineage:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error"
      };
    }
  }

  /**
   * Get data mash visualization (retrieve from state or GCS)
   */
  /**
   * Map relationships (map_relationships intent)
   * 
   * Discovers and visualizes entity relationships in parsed data.
   */
  async mapRelationships(
    fileId: string
  ): Promise<RelationshipMappingResponse> {
    try {
      const platformState = this.getPlatformState();
      
      // ✅ FIX ISSUE 4: Use standardized session validation
      validateSession(platformState, "map relationships");

      // ✅ FIX ISSUE 3: Parameter validation before submitIntent
      if (!fileId) {
        throw new Error("file_id is required for map_relationships");
      }

      // Submit intent via Experience Plane Client
      const execution = await platformState.submitIntent(
        "map_relationships",
        {
          file_id: fileId,
        }
      );

      // Wait for execution completion
      const result = await this._waitForExecution(execution, platformState);

      if (result.status === "completed" && result.artifacts?.relationships) {
        // Update realm state
        platformState.setRealmState("insights", "relationshipMappings", {
          [fileId]: result.artifacts.relationships,
        });

        return {
          success: true,
          relationships: result.artifacts.relationships,
          file_id: fileId,
        };
      } else {
        return {
          success: false,
          error: result.error || "Failed to map relationships",
        };
      }
    } catch (error: any) {
      console.error("[InsightsAPIManager] Error mapping relationships:", error);
      return {
        success: false,
        error: error.message || "An unexpected error occurred",
      };
    }
  }

  async getDataMashVisualization(fileId: string): Promise<LineageVisualizationResponse> {
    try {
      const platformState = this.getPlatformState();
      
      // Check if visualization is already in state
      const visualizations = platformState.getRealmState("insights", "lineageVisualizations") || {};
      if (visualizations[fileId]) {
        return {
          success: true,
          visualization: visualizations[fileId],
          file_id: fileId
        };
      }

      // If not in state, trigger visualization
      return await this.visualizeLineage(fileId);
    } catch (error) {
      console.error("[InsightsAPIManager] Error getting data mash visualization:", error);
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

      // Wait before next poll
      await new Promise(resolve => setTimeout(resolve, pollInterval));
    }

    throw new Error("Execution timeout");
  }
}