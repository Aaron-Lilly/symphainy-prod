// Experience Service Orchestrator
export * from './types';
export * from './core';

// Explicit exports to avoid conflicts
export {
  analyzeFileForRoadmap,
  generateRoadmap,
  validateRoadmap,
  optimizeRoadmap
} from './roadmap-generation';

export {
  generatePOCProposal,
  generatePOCDocument,
  validatePOC,
  optimizePOC
} from './poc-generation';

export {
  routeExperienceSession,
  sendExperienceMessage,
  orchestrateExperience,
  persistExperienceState,
  getCrossPillarData,
  processExperienceLiaisonRequest
} from './smart-city-integration';

// Main ExperienceService class for unified access
import {
  ExperienceSessionResponse,
  ExperienceRoadmapResponse,
  ExperiencePOCResponse,
  ExperienceDocumentResponse,
  ExperienceErrorResponse,
  SourceFile,
  AdditionalContextRequest,
  ExperienceSessionState,
  RoadmapGenerationRequest,
  POCGenerationRequest,
  DocumentGenerationRequest,
  ExperienceOutputsRequest,
  ExperienceOutputsResponse,
  TrafficCopSessionRequest,
  TrafficCopSessionResponse,
  PostOfficeMessage,
  PostOfficeResponse,
  ConductorExperienceRequest,
  ConductorExperienceResponse,
  ArchiveStateRequest,
  ArchiveStateResponse,
  CrossPillarDataRequest,
  CrossPillarDataResponse,
  ExperienceLiaisonEvent,
  RoadmapMilestone,
  RoadmapPhase,
  RoadmapTimeline,
  RoadmapValidationResult,
  RoadmapOptimizationRequest,
  RoadmapOptimizationResult,
  POCRequirement,
  POCResource,
  POCTimeline,
  POCValidationResult,
  POCOptimizationRequest,
  POCOptimizationResult
} from './types';

import {
  getExperienceSession,
  createExperienceSession,
  getExperienceSessionState,
  storeAdditionalContext,
  generateExperienceOutputs,
  getSourceFiles
} from './core';

import {
  analyzeFileForRoadmap,
  generateRoadmap,
  validateRoadmap,
  optimizeRoadmap
} from './roadmap-generation';

import {
  generatePOCProposal,
  generatePOCDocument,
  validatePOC,
  optimizePOC
} from './poc-generation';

import {
  routeExperienceSession,
  sendExperienceMessage,
  orchestrateExperience,
  persistExperienceState,
  getCrossPillarData,
  processExperienceLiaisonRequest
} from './smart-city-integration';

export class ExperienceService {
  // Session Management
  static async getExperienceSession(sessionToken: string): Promise<ExperienceSessionResponse> {
    return getExperienceSession(sessionToken);
  }

  static async createExperienceSession(sessionToken: string): Promise<ExperienceSessionResponse> {
    return createExperienceSession(sessionToken);
  }

  static async getExperienceSessionState(sessionToken: string): Promise<ExperienceSessionState> {
    return getExperienceSessionState(sessionToken);
  }

  static async storeAdditionalContext(request: AdditionalContextRequest): Promise<{ success: boolean; message: string }> {
    return storeAdditionalContext(request);
  }

  static async generateExperienceOutputs(request: ExperienceOutputsRequest): Promise<ExperienceOutputsResponse> {
    return generateExperienceOutputs(request);
  }

  static async getSourceFiles(sessionToken: string): Promise<SourceFile[]> {
    return getSourceFiles(sessionToken);
  }

  // Roadmap Generation
  static async analyzeFileForRoadmap(fileUuid: string, sessionToken: string): Promise<ExperienceRoadmapResponse> {
    return analyzeFileForRoadmap(fileUuid, sessionToken);
  }

  static async generateRoadmap(request: RoadmapGenerationRequest): Promise<ExperienceRoadmapResponse> {
    return generateRoadmap(request);
  }

  static async validateRoadmap(roadmapData: any, sessionToken: string): Promise<RoadmapValidationResult> {
    return validateRoadmap(roadmapData, sessionToken);
  }

  static async optimizeRoadmap(request: RoadmapOptimizationRequest): Promise<RoadmapOptimizationResult> {
    return optimizeRoadmap(request);
  }

  // POC Generation
  static async generatePOCProposal(request: POCGenerationRequest): Promise<ExperiencePOCResponse> {
    return generatePOCProposal(request);
  }

  static async generatePOCDocument(request: DocumentGenerationRequest): Promise<ExperienceDocumentResponse> {
    return generatePOCDocument(request);
  }

  static async validatePOC(pocData: any, sessionToken: string): Promise<POCValidationResult> {
    return validatePOC(pocData, sessionToken);
  }

  static async optimizePOC(request: POCOptimizationRequest): Promise<POCOptimizationResult> {
    return optimizePOC(request);
  }

  // Smart City Integration
  static async routeExperienceSession(request: TrafficCopSessionRequest): Promise<TrafficCopSessionResponse> {
    return routeExperienceSession(request);
  }

  static async sendExperienceMessage(message: PostOfficeMessage): Promise<PostOfficeResponse> {
    return sendExperienceMessage(message);
  }

  static async orchestrateExperience(request: ConductorExperienceRequest): Promise<ConductorExperienceResponse> {
    return orchestrateExperience(request);
  }

  static async persistExperienceState(request: ArchiveStateRequest): Promise<ArchiveStateResponse> {
    return persistExperienceState(request);
  }

  static async getCrossPillarData(request: CrossPillarDataRequest): Promise<CrossPillarDataResponse> {
    return getCrossPillarData(request);
  }

  static async processExperienceLiaisonRequest(event: ExperienceLiaisonEvent): Promise<any> {
    return processExperienceLiaisonRequest(event);
  }
}

// Default export for convenience
export default ExperienceService; 