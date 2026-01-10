/**
 * MVP Solution Service
 * 
 * Service layer for interacting with MVP Solution Orchestrator
 * Implements agentic-forward pattern for solution customization
 */

import { APIService } from "../APIService";
import type {
  SolutionStructureResponse,
  CustomizeSolutionResponse,
  MVPSessionResponse,
  PillarNavigationResponse,
  UserCustomizations,
} from "./types";

const API_BASE = "/api/v1/mvp-solution";

export class MVPSolutionService {
  private apiService: APIService;

  constructor(apiService?: APIService) {
    this.apiService = apiService || new APIService();
  }

  /**
   * Get solution structure guidance from Guide Agent (AGENTIC-FORWARD PATTERN)
   * 
   * The agent performs critical reasoning FIRST to determine:
   * - Which pillars to include and in what order
   * - What data types are needed
   * - What customizations make sense
   * - Strategic priorities and focus areas
   * 
   * @param userGoals User's stated goals, challenges, or desired outcomes
   * @param userContext Optional user context (industry, role, constraints)
   * @returns Solution structure specification with agent reasoning
   */
  async getSolutionGuidance(
    userGoals: string,
    userContext?: Record<string, any>
  ): Promise<SolutionStructureResponse> {
    try {
      const response = await this.apiService.post<SolutionStructureResponse>(
        `${API_BASE}/guidance`,
        {
          user_goals: userGoals,
          user_context: userContext || {},
        }
      );

      // Extract data from APIResponse wrapper
      return response.data;
    } catch (error: any) {
      console.error("Failed to get solution guidance:", error);
      return {
        success: false,
        error: error.message || "Failed to get solution guidance",
        solution_structure: {
          pillars: [],
          recommended_data_types: [],
          strategic_focus: "general",
          customization_options: {
            workflow_creation: false,
            interactive_guidance: false,
            automated_analysis: false,
          },
        },
        reasoning: {
          analysis: "",
          key_insights: [],
          recommendations: [],
          confidence: 0,
        },
      };
    }
  }

  /**
   * Customize solution structure based on user preferences
   * 
   * @param solutionStructure Agent-created solution structure
   * @param userCustomizations User's customization preferences
   * @param userContext Optional user context
   * @returns Customized solution structure
   */
  async customizeSolution(
    solutionStructure: SolutionStructureResponse["solution_structure"],
    userCustomizations: UserCustomizations,
    userContext?: Record<string, any>
  ): Promise<CustomizeSolutionResponse> {
    try {
      const response = await this.apiService.post<CustomizeSolutionResponse>(
        `${API_BASE}/customize`,
        {
          solution_structure: solutionStructure,
          user_customizations: userCustomizations,
          user_context: userContext || {},
        }
      );

      // Extract data from APIResponse wrapper
      return response.data;
    } catch (error: any) {
      console.error("Failed to customize solution:", error);
      return {
        success: false,
        error: error.message || "Failed to customize solution",
        solution_structure: solutionStructure,
        customizations_applied: userCustomizations,
      };
    }
  }

  /**
   * Create MVP session with platform correlation
   * 
   * @param userId User identifier
   * @param sessionType Type of session (default: "mvp")
   * @param userContext Optional user context
   * @returns Session details with workflow_id
   */
  async createSession(
    userId: string,
    sessionType: string = "mvp",
    userContext?: Record<string, any>
  ): Promise<MVPSessionResponse> {
    try {
      const response = await this.apiService.post<MVPSessionResponse>(
        `${API_BASE}/session`,
        {
          user_id: userId,
          session_type: sessionType,
          user_context: userContext || {},
        }
      );

      // Extract data from APIResponse wrapper
      return response.data;
    } catch (error: any) {
      console.error("Failed to create MVP session:", error);
      return {
        success: false,
        error: error.message || "Failed to create MVP session",
      };
    }
  }

  /**
   * Navigate to a specific pillar
   * 
   * @param sessionId Session identifier
   * @param pillar Pillar name (content, insights, operations, business-outcomes)
   * @param userContext Optional user context
   * @returns Pillar context with available actions
   */
  async navigateToPillar(
    sessionId: string,
    pillar: string,
    userContext?: Record<string, any>
  ): Promise<PillarNavigationResponse> {
    try {
      const response = await this.apiService.post<PillarNavigationResponse>(
        `${API_BASE}/navigate`,
        {
          session_id: sessionId,
          pillar: pillar,
          user_context: userContext || {},
        }
      );

      // Extract data from APIResponse wrapper
      return response.data;
    } catch (error: any) {
      console.error("Failed to navigate to pillar:", error);
      return {
        success: false,
        error: error.message || "Failed to navigate to pillar",
      };
    }
  }
}

// Export singleton instance
export const mvpSolutionService = new MVPSolutionService();











