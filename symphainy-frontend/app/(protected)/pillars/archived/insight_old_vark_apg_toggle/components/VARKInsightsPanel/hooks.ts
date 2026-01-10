/**
 * VARKInsightsPanel Hooks
 * Custom hooks for VARKInsightsPanel component
 */

import React, { useState, useEffect, useCallback } from 'react';
import { FileMetadata } from '@/shared/types/file';
import { useGlobalSession } from '@/shared/agui/GlobalSessionProvider';
import { useAGUIEvent } from '@/shared/agui/AGUIEventProvider';
import { 
  VARKInsightsPanelState, 
  LearningStyle, 
  DataDepth,
  AnalysisRequest,
  AnalysisResponse,
  AnalysisHistoryEntry
} from './types';
import { 
  filterParsedFiles, 
  validateAnalysisRequest, 
  formatAnalysisResults,
  generateBusinessSummary 
} from './utils';
import { InsightsService } from '@/shared/services/insights';

export function useVARKInsightsPanel() {
  const { getPillarState, setPillarState, guideSessionToken } = useGlobalSession();
  const { sendEvent } = useAGUIEvent();
  
  const [state, setState] = useState<VARKInsightsPanelState>({
    files: [],
    selectedFile: null,
    fileLoading: true,
    learningStyle: 'tabular',
    dataDepth: 'summary',
    isAnalyzing: false,
    analysisResults: null,
    businessSummary: '',
    summaryLoading: false,
    error: null,
    // New state for iterative analysis
    analysisHistory: [],
    currentSessionId: null,
    isIterativeAnalysis: false,
  });

  // Load files from content pillar
  useEffect(() => {
    const loadFiles = async () => {
      setState(prev => ({ ...prev, fileLoading: true, error: null }));

      try {
        // Get files from content pillar state
        const contentState = getPillarState('content');
        const contentFiles = contentState?.files || [];

        // Filter for parsed files
        const parsedFiles = filterParsedFiles(contentFiles);
        
        setState(prev => ({
          ...prev,
          files: parsedFiles,
          fileLoading: false,
        }));

        // Auto-select first file if available
        if (parsedFiles.length > 0 && !state.selectedFile) {
          setState(prev => ({ ...prev, selectedFile: parsedFiles[0] }));
        }
      } catch (error) {
        setState(prev => ({
          ...prev,
          error: error instanceof Error ? error.message : 'Failed to load files',
          fileLoading: false,
        }));
      }
    };

    loadFiles();
  }, [getPillarState, state.selectedFile]);

  // Listen for InsightsLiaisonAgent events
  useEffect(() => {
    const handleInsightsLiaisonEvent = (event: any) => {
      if (event.type === 'insights_analysis_request') {
        handleIterativeAnalysis(event.data);
      } else if (event.type === 'insights_query_request') {
        handleNaturalLanguageQuery(event.data);
      }
    };

    // Subscribe to InsightsLiaisonAgent events
    sendEvent({
      type: 'subscribe',
      session_token: guideSessionToken || '',
      agent_type: 'insights_liaison',
      pillar: 'insights',
      data: { callback: handleInsightsLiaisonEvent }
    });

    return () => {
      sendEvent({
        type: 'unsubscribe',
        session_token: guideSessionToken || '',
        agent_type: 'insights_liaison',
        pillar: 'insights'
      });
    };
  }, [sendEvent, guideSessionToken]);

  const handleFileSelect = useCallback((file: FileMetadata) => {
    setState(prev => ({
      ...prev,
      selectedFile: file,
      analysisResults: null,
      businessSummary: '',
      analysisHistory: [],
      currentSessionId: null,
      error: null,
    }));
  }, []);

  const handleLearningStyleChange = useCallback((style: LearningStyle) => {
    setState(prev => ({
      ...prev,
      learningStyle: style,
      analysisResults: null,
      businessSummary: '',
    }));
  }, []);

  const handleDataDepthChange = useCallback((depth: DataDepth) => {
    setState(prev => ({
      ...prev,
      dataDepth: depth,
      analysisResults: null,
      businessSummary: '',
    }));
  }, []);

  const handleAnalysis = useCallback(async (): Promise<AnalysisResponse> => {
    const validation = validateAnalysisRequest(
      state.selectedFile,
      state.learningStyle,
      state.dataDepth
    );

    if (!validation.valid) {
      setState(prev => ({ ...prev, error: validation.error }));
      return { success: false, error: validation.error };
    }

    setState(prev => ({ ...prev, isAnalyzing: true, error: null }));

    try {
      const insightsService = new InsightsService();
      
      const request: AnalysisRequest = {
        fileUuid: state.selectedFile!.uuid,
        learningStyle: state.learningStyle,
        dataDepth: state.dataDepth,
        sessionToken: guideSessionToken,
      };

      // Start insights session
      const sessionResponse = await insightsService.startInsightsSession(
        request.fileUuid,
        undefined,
        request.sessionToken
      );

      if (!sessionResponse.session_id) {
        throw new Error('Failed to start insights session');
      }

      // Store session ID for iterative analysis
      setState(prev => ({ ...prev, currentSessionId: sessionResponse.session_id }));

      // Perform VARK analysis based on learning style
      let analysisResults;
      
      if (state.learningStyle === 'visual') {
        analysisResults = await insightsService.getVisualizationAnalysis(
          state.selectedFile!.original_path,
          sessionResponse.session_id,
          `VARK Visual Analysis - ${state.dataDepth}`,
          request.sessionToken
        );
      } else {
        analysisResults = await insightsService.getEDAAnalysis(
          state.selectedFile!.original_path,
          {
            session_id: sessionResponse.session_id,
            title: `VARK Tabular Analysis - ${state.dataDepth}`
          },
          request.sessionToken
        );
      }

      if (analysisResults.success) {
        const formattedResults = formatAnalysisResults(analysisResults.data);
        const businessSummary = generateBusinessSummary(formattedResults);

        // Add to analysis history
        const analysisEntry: AnalysisHistoryEntry = {
          id: Date.now().toString(),
          timestamp: new Date(),
          type: 'initial_analysis',
          learningStyle: state.learningStyle,
          dataDepth: state.dataDepth,
          results: formattedResults,
          summary: businessSummary,
        };

        setState(prev => ({
          ...prev,
          analysisResults: formattedResults,
          businessSummary,
          isAnalyzing: false,
          analysisHistory: [...prev.analysisHistory, analysisEntry],
        }));

        // Update pillar state
        setPillarState('insights', {
          current_file: state.selectedFile!.uuid,
          analysis_results: formattedResults,
          business_summary: businessSummary,
          session_id: sessionResponse.session_id,
          analysis_history: [...state.analysisHistory, analysisEntry],
        });

        // Notify InsightsLiaisonAgent of initial analysis completion
        sendEvent({
          type: 'insights_analysis_complete',
          session_token: guideSessionToken || '',
          agent_type: 'insights_liaison',
          pillar: 'insights',
          session_id: sessionResponse.session_id,
          analysis_results: formattedResults,
          business_summary: businessSummary,
          learning_style: state.learningStyle,
          data_depth: state.dataDepth,
        });

        return { success: true, data: formattedResults };
      } else {
        throw new Error(analysisResults.error || 'Analysis failed');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Analysis failed';
      setState(prev => ({
        ...prev,
        error: errorMessage,
        isAnalyzing: false,
      }));
      
      return { success: false, error: errorMessage };
    }
  }, [state.selectedFile, state.learningStyle, state.dataDepth, guideSessionToken, setPillarState, sendEvent, state.analysisHistory]);

  const handleIterativeAnalysis = useCallback(async (analysisRequest: any) => {
    if (!state.currentSessionId || !state.selectedFile) {
      setState(prev => ({ ...prev, error: 'No active analysis session' }));
      return;
    }

    setState(prev => ({ ...prev, isIterativeAnalysis: true, error: null }));

    try {
      const insightsService = new InsightsService();
      
      // Process iterative analysis request
      const iterativeResults = await insightsService.processNaturalLanguageQuery({
        sessionId: state.currentSessionId,
        query: analysisRequest.query,
        fileUrl: state.selectedFile.original_path,
        context: {
          previous_analysis: state.analysisResults,
          learning_style: state.learningStyle,
          data_depth: state.dataDepth,
        },
        sessionToken: guideSessionToken,
      });

      if (iterativeResults.success) {
        const formattedResults = formatAnalysisResults(iterativeResults.data);
        const businessSummary = generateBusinessSummary(formattedResults);

        // Add to analysis history
        const analysisEntry: AnalysisHistoryEntry = {
          id: Date.now().toString(),
          timestamp: new Date(),
          type: 'iterative_analysis',
          query: analysisRequest.query,
          learningStyle: state.learningStyle,
          dataDepth: state.dataDepth,
          results: formattedResults,
          summary: businessSummary,
        };

        setState(prev => ({
          ...prev,
          analysisResults: formattedResults,
          businessSummary,
          isIterativeAnalysis: false,
          analysisHistory: [...prev.analysisHistory, analysisEntry],
        }));

        // Update pillar state
        setPillarState('insights', {
          current_file: state.selectedFile!.uuid,
          analysis_results: formattedResults,
          business_summary: businessSummary,
          session_id: state.currentSessionId,
          analysis_history: [...state.analysisHistory, analysisEntry],
        });

        // Notify InsightsLiaisonAgent of iterative analysis completion
        sendEvent({
          type: 'insights_iterative_complete',
          session_token: guideSessionToken || '',
          agent_type: 'insights_liaison',
          pillar: 'insights',
          session_id: state.currentSessionId,
          query: analysisRequest.query,
          analysis_results: formattedResults,
          business_summary: businessSummary,
        });

      } else {
        throw new Error(iterativeResults.error || 'Iterative analysis failed');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Iterative analysis failed';
      setState(prev => ({
        ...prev,
        error: errorMessage,
        isIterativeAnalysis: false,
      }));
    }
  }, [state.currentSessionId, state.selectedFile, state.analysisResults, state.learningStyle, state.dataDepth, guideSessionToken, setPillarState, sendEvent, state.analysisHistory]);

  const handleNaturalLanguageQuery = useCallback(async (queryRequest: any) => {
    if (!state.currentSessionId || !state.selectedFile) {
      setState(prev => ({ ...prev, error: 'No active analysis session' }));
      return;
    }

    try {
      const insightsService = new InsightsService();
      
      // Process natural language query
      const queryResults = await insightsService.processChatMessage({
        sessionId: state.currentSessionId,
        message: queryRequest.message,
        context: {
          current_analysis: state.analysisResults,
          business_summary: state.businessSummary,
          learning_style: state.learningStyle,
          data_depth: state.dataDepth,
          analysis_history: state.analysisHistory,
        },
        sessionToken: guideSessionToken,
      });

      if (queryResults.success) {
        // Handle query response (could trigger analysis updates)
        sendEvent({
          type: 'insights_query_response',
          session_token: guideSessionToken || '',
          agent_type: 'insights_liaison',
          pillar: 'insights',
          session_id: state.currentSessionId,
          query: queryRequest.message,
          response: queryResults.data,
        });
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Query processing failed';
      setState(prev => ({ ...prev, error: errorMessage }));
    }
  }, [state.currentSessionId, state.selectedFile, state.analysisResults, state.businessSummary, state.learningStyle, state.dataDepth, guideSessionToken, sendEvent, state.analysisHistory]);

  const handleRefreshSummary = useCallback(async () => {
    if (!state.selectedFile) return;

    setState(prev => ({ ...prev, summaryLoading: true }));

    try {
      const insightsService = new InsightsService();
      
      const summaryResponse = await insightsService.generateInsightsSummary(
        state.currentSessionId || 'temp-session-id',
        'Refresh business summary',
        guideSessionToken
      );

      if (summaryResponse.success) {
        const businessSummary = generateBusinessSummary(summaryResponse.data);
        setState(prev => ({
          ...prev,
          businessSummary,
          summaryLoading: false,
        }));
      } else {
        throw new Error(summaryResponse.error || 'Failed to refresh summary');
      }
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Failed to refresh summary',
        summaryLoading: false,
      }));
    }
  }, [state.selectedFile, state.currentSessionId, guideSessionToken]);

  const handleExport = useCallback(() => {
    if (!state.analysisResults) return;
    
    // Export functionality would be implemented here
    console.log('Exporting analysis results:', state.analysisResults);
  }, [state.analysisResults]);

  const handleShare = useCallback(() => {
    if (!state.analysisResults || !state.businessSummary) return;
    
    // Share functionality would be implemented here
    console.log('Sharing insights with Experience pillar');
  }, [state.analysisResults, state.businessSummary]);

  return {
    state,
    handleFileSelect,
    handleLearningStyleChange,
    handleDataDepthChange,
    handleAnalysis,
    handleRefreshSummary,
    handleExport,
    handleShare,
  };
} 