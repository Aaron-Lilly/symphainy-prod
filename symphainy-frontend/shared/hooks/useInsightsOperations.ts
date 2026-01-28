/**
 * useInsightsOperations Hook
 * 
 * CANONICAL HOOK for insights operations using the Runtime intent architecture.
 * Replaces useInsightsAPI which used stub APIs.
 * 
 * Architecture:
 * Component → useInsightsOperations → usePlatformState → ExperiencePlaneClient → Runtime
 * 
 * Usage:
 * ```tsx
 * const { assessDataQuality, analyzeData, isLoading, error } = useInsightsOperations();
 * 
 * const result = await assessDataQuality(parsedFileId);
 * if (result.success) {
 *   console.log('Quality report:', result.artifacts?.quality_report);
 * }
 * ```
 */

"use client";

import { useCallback, useState } from 'react';
import { usePlatformState } from '../state/PlatformStateProvider';
import { useSessionBoundary, SessionStatus } from '../state/SessionBoundaryProvider';
import type { ExecutionStatusResponse } from '@/shared/types/runtime-contracts';

// =============================================================================
// TYPES
// =============================================================================

export interface InsightsOperationResult {
  success: boolean;
  executionId?: string;
  artifacts?: Record<string, unknown>;
  error?: string;
}

export interface DataQualityReport {
  overall_score: number;
  dimensions: {
    completeness: number;
    accuracy: number;
    consistency: number;
    timeliness: number;
  };
  issues: Array<{
    type: string;
    severity: 'low' | 'medium' | 'high';
    description: string;
    affected_columns?: string[];
  }>;
  recommendations: string[];
}

export interface AnalysisResult {
  analysis_id: string;
  analysis_type: string;
  summary: string;
  findings: Array<{
    title: string;
    description: string;
    confidence: number;
  }>;
  visualizations?: Array<{
    type: string;
    data: unknown;
    config?: Record<string, unknown>;
  }>;
}

export interface InterpretationResult {
  interpretation_id: string;
  insights: Array<{
    title: string;
    description: string;
    importance: 'low' | 'medium' | 'high';
  }>;
  patterns: Array<{
    name: string;
    description: string;
    confidence: number;
  }>;
  recommendations: string[];
}

// =============================================================================
// HOOK
// =============================================================================

export function useInsightsOperations() {
  const { state: sessionState } = useSessionBoundary();
  const { submitIntent, getExecutionStatus } = usePlatformState();
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Wait for execution to complete with polling
   */
  const waitForExecution = useCallback(async (
    executionId: string,
    maxWaitMs: number = 60000, // Insights operations can take longer
    pollIntervalMs: number = 2000
  ): Promise<ExecutionStatusResponse | null> => {
    const startTime = Date.now();
    
    while (Date.now() - startTime < maxWaitMs) {
      const status = await getExecutionStatus(executionId);
      
      if (!status) {
        await new Promise(resolve => setTimeout(resolve, pollIntervalMs));
        continue;
      }
      
      if (status.status === 'completed' || status.status === 'failed') {
        return status;
      }
      
      await new Promise(resolve => setTimeout(resolve, pollIntervalMs));
    }
    
    return null;
  }, [getExecutionStatus]);

  /**
   * Assess data quality using assess_data_quality intent
   */
  const assessDataQuality = useCallback(async (
    parsedFileId: string,
    options?: {
      dimensions?: ('completeness' | 'accuracy' | 'consistency' | 'timeliness')[];
      threshold?: number;
    }
  ): Promise<{ success: boolean; report?: DataQualityReport; error?: string }> => {
    if (sessionState.status !== SessionStatus.Active) {
      return { success: false, error: 'Session not active' };
    }

    setIsLoading(true);
    setError(null);

    try {
      const executionId = await submitIntent('assess_data_quality', {
        parsed_file_id: parsedFileId,
        dimensions: options?.dimensions || ['completeness', 'accuracy', 'consistency', 'timeliness'],
        quality_threshold: options?.threshold || 0.8,
      });

      const result = await waitForExecution(executionId);

      if (!result) {
        return { success: false, error: 'Execution timed out' };
      }

      if (result.status === 'failed') {
        return { success: false, error: result.error || 'Data quality assessment failed' };
      }

      return {
        success: true,
        report: result.artifacts?.quality_report as DataQualityReport,
      };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Data quality assessment failed';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setIsLoading(false);
    }
  }, [sessionState.status, submitIntent, waitForExecution]);

  /**
   * Analyze structured data using analyze_structured_data intent
   */
  const analyzeStructuredData = useCallback(async (
    parsedFileId: string,
    options?: {
      analysisType?: 'descriptive' | 'diagnostic' | 'predictive';
      targetColumns?: string[];
      includeVisualization?: boolean;
    }
  ): Promise<{ success: boolean; analysis?: AnalysisResult; error?: string }> => {
    if (sessionState.status !== SessionStatus.Active) {
      return { success: false, error: 'Session not active' };
    }

    setIsLoading(true);
    setError(null);

    try {
      const executionId = await submitIntent('analyze_structured_data', {
        parsed_file_id: parsedFileId,
        analysis_type: options?.analysisType || 'descriptive',
        target_columns: options?.targetColumns,
        include_visualization: options?.includeVisualization ?? true,
      });

      const result = await waitForExecution(executionId);

      if (!result) {
        return { success: false, error: 'Execution timed out' };
      }

      if (result.status === 'failed') {
        return { success: false, error: result.error || 'Analysis failed' };
      }

      return {
        success: true,
        analysis: result.artifacts?.analysis_result as AnalysisResult,
      };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Analysis failed';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setIsLoading(false);
    }
  }, [sessionState.status, submitIntent, waitForExecution]);

  /**
   * Self-discovery interpretation using interpret_data_self_discovery intent
   */
  const interpretDataSelfDiscovery = useCallback(async (
    parsedFileId: string,
    options?: {
      depth?: 'shallow' | 'medium' | 'deep';
      focus?: string[];
    }
  ): Promise<{ success: boolean; interpretation?: InterpretationResult; error?: string }> => {
    if (sessionState.status !== SessionStatus.Active) {
      return { success: false, error: 'Session not active' };
    }

    setIsLoading(true);
    setError(null);

    try {
      const executionId = await submitIntent('interpret_data_self_discovery', {
        parsed_file_id: parsedFileId,
        exploration_depth: options?.depth || 'medium',
        focus_areas: options?.focus,
      });

      const result = await waitForExecution(executionId);

      if (!result) {
        return { success: false, error: 'Execution timed out' };
      }

      if (result.status === 'failed') {
        return { success: false, error: result.error || 'Interpretation failed' };
      }

      return {
        success: true,
        interpretation: result.artifacts?.interpretation as InterpretationResult,
      };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Interpretation failed';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setIsLoading(false);
    }
  }, [sessionState.status, submitIntent, waitForExecution]);

  /**
   * Guided interpretation using interpret_data_guided intent
   */
  const interpretDataGuided = useCallback(async (
    parsedFileId: string,
    question: string,
    options?: {
      context?: string;
      expectedFormat?: 'text' | 'chart' | 'table';
    }
  ): Promise<{ success: boolean; interpretation?: InterpretationResult; error?: string }> => {
    if (sessionState.status !== SessionStatus.Active) {
      return { success: false, error: 'Session not active' };
    }

    setIsLoading(true);
    setError(null);

    try {
      const executionId = await submitIntent('interpret_data_guided', {
        parsed_file_id: parsedFileId,
        question,
        context: options?.context,
        expected_format: options?.expectedFormat || 'text',
      });

      const result = await waitForExecution(executionId);

      if (!result) {
        return { success: false, error: 'Execution timed out' };
      }

      if (result.status === 'failed') {
        return { success: false, error: result.error || 'Guided interpretation failed' };
      }

      return {
        success: true,
        interpretation: result.artifacts?.interpretation as InterpretationResult,
      };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Guided interpretation failed';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setIsLoading(false);
    }
  }, [sessionState.status, submitIntent, waitForExecution]);

  return {
    // Operations
    assessDataQuality,
    analyzeStructuredData,
    interpretDataSelfDiscovery,
    interpretDataGuided,
    
    // State
    isLoading,
    error,
    clearError: () => setError(null),
    
    // Session info
    isSessionActive: sessionState.status === SessionStatus.Active,
  };
}
