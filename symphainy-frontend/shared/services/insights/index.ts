/**
 * Insights Service Orchestrator
 * Unified access point for insights service functionality
 */

// Types
export type {
  InsightsSessionResponse,
  InsightsAnalysisResponse,
  InsightsSummaryResponse,
  VARKInsightsRequest,
  BusinessSummaryRequest,
  CrossPillarIntegrationRequest,
  SmartCityInsightsRequest,
  AGUIEvent,
  FileUrlRequest,
  LearningStyleType
} from './types';

// Core service
export { InsightsService } from './core';

// VARK analysis
export { VARKAnalysisService } from './vark-analysis';
export type {
  VARKAnalysisRequest,
  VARKAnalysisResponse,
  LearningStyleAdaptation
} from './vark-analysis';

// Business analysis
export { BusinessAnalysisService } from './business-analysis';
export type {
  BusinessAnalysisRequest,
  BusinessAnalysisResponse,
  BusinessInsights
} from './business-analysis';

// Smart City integration
export { InsightsSmartCityService } from './smart-city-integration';
export type {
  InsightsSmartCityMessage,
  InsightsSmartCityResponse
} from './smart-city-integration'; 