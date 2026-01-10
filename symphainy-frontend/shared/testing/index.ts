/**
 * Advanced Testing Architecture Orchestrator
 * Provides unified access to all testing functionality
 */

// Export core functionality
export { AdvancedTestFramework } from './core/AdvancedTestFramework';
export type { 
  TestConfig, 
  TestResult, 
  TestSuite, 
  TestCase,
  PerformanceMetrics 
} from './core/AdvancedTestFramework';

// Export visual regression testing
export { VisualRegressionTesting } from './visual/VisualRegressionTesting';
export type { 
  VisualTestConfig, 
  ScreenshotData, 
  VisualTestResult, 
  VisualDifference 
} from './visual/VisualRegressionTesting';

// Export performance testing
export { PerformanceTesting } from './performance/PerformanceTesting';
export type { 
  PerformanceTestConfig, 
  PerformanceTestResult, 
  PerformanceThresholds 
} from './performance/PerformanceTesting';

// Export test generation
export { TestGeneration } from './generation/TestGeneration';
export type { 
  TestGenerationConfig, 
  ComponentAnalysis, 
  PropInfo, 
  EventInfo, 
  GeneratedTest 
} from './generation/TestGeneration';

// Export enhanced testing provider
export { EnhancedTestingProvider } from './EnhancedTestingProvider'; 