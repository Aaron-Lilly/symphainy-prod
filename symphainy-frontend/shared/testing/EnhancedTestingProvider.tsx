/**
 * Enhanced Testing Provider
 * React context provider for advanced testing functionality
 */

import React, { createContext, useContext, useRef, useEffect } from 'react';
import { getGlobalConfig } from '../config';
import { TestConfig } from './core/AdvancedTestFramework';
import { VisualTestConfig } from './visual/VisualRegressionTesting';
import { PerformanceTestConfig } from './performance/PerformanceTesting';
import { TestGenerationConfig } from './generation/TestGeneration';

interface EnhancedTestingContextValue {
  testConfig: TestConfig;
  visualConfig: VisualTestConfig;
  performanceConfig: PerformanceTestConfig;
  generationConfig: TestGenerationConfig;
  isEnabled: boolean;
}

const EnhancedTestingContext = createContext<EnhancedTestingContextValue | null>(null);

interface EnhancedTestingProviderProps {
  children: React.ReactNode;
  config?: {
    test?: Partial<TestConfig>;
    visual?: Partial<VisualTestConfig>;
    performance?: Partial<PerformanceTestConfig>;
    generation?: Partial<TestGenerationConfig>;
  };
}

export function EnhancedTestingProvider({ 
  children, 
  config = {} 
}: EnhancedTestingProviderProps) {
  const globalConfig = getGlobalConfig();
  const isEnabled = globalConfig.getSection('features').analytics;

  const testConfig: TestConfig = {
    enableVisualRegression: true,
    enablePerformanceTesting: true,
    enableAutomatedGeneration: true,
    enableParallelExecution: true,
    enableTestCaching: true,
    timeout: 30000,
    retries: 3,
    ...config.test,
  };

  const visualConfig: VisualTestConfig = {
    enableScreenshotCapture: true,
    enableBaselineComparison: true,
    enableDiffDetection: true,
    screenshotQuality: 0.9,
    tolerance: 0.95,
    outputDir: './screenshots',
    ...config.visual,
  };

  const performanceConfig: PerformanceTestConfig = {
    enableRenderTimeTesting: true,
    enableMemoryTesting: true,
    enableNetworkTesting: true,
    enableBundleAnalysis: true,
    enableCpuProfiling: true,
    iterations: 10,
    warmupIterations: 3,
    timeout: 30000,
    ...config.performance,
  };

  const generationConfig: TestGenerationConfig = {
    enableComponentAnalysis: true,
    enablePropsGeneration: true,
    enableEventGeneration: true,
    enableAccessibilityGeneration: true,
    enableEdgeCaseGeneration: true,
    maxGeneratedTests: 50,
    includeComplexScenarios: true,
    ...config.generation,
  };

  const contextValue: EnhancedTestingContextValue = {
    testConfig,
    visualConfig,
    performanceConfig,
    generationConfig,
    isEnabled,
  };

  return (
    <EnhancedTestingContext.Provider value={contextValue}>
      {children}
    </EnhancedTestingContext.Provider>
  );
}

// Hook to use enhanced testing context
export function useEnhancedTestingContext() {
  const context = useContext(EnhancedTestingContext);
  if (!context) {
    throw new Error('useEnhancedTestingContext must be used within EnhancedTestingProvider');
  }
  return context;
} 