/**
 * Insights API Module
 * 
 * Provides API functions for the Insights pillar.
 * Uses ExperiencePlaneClient for real backend calls.
 * 
 * NOTE: These functions work outside React context. For React components,
 * prefer using useInsightsOperations hook when possible.
 */

import { getGlobalExperiencePlaneClient } from '@/shared/services/ExperiencePlaneClient';

export interface ContentMetadata {
  id: string;
  name: string;
  type: 'structured' | 'unstructured';
  source: string;
  created_at: string;
}

export interface ContentMetadataResponse {
  success: boolean;
  content_metadata_items?: ContentMetadata[];
  error?: string;
}

export interface AnalyzeContentRequest {
  content_id?: string;
  file_id?: string;
  content_type?: string;
  source_type?: 'file' | 'content_metadata';
  analysis_type?: 'structured' | 'unstructured';
  generate_visualizations?: boolean;
  analysis_options?: {
    include_visualizations?: boolean;
    include_tabular_summary?: boolean;
    aar_specific_analysis?: boolean;
    [key: string]: any;
  };
  options?: Record<string, any>;
  [key: string]: any;
}

export interface AnalyzeContentResponse {
  success: boolean;
  // Summary in the format expected by InsightsSummaryDisplay
  summary?: {
    textual: string;
    tabular?: {
      columns: string[];
      rows: any[][];
      summary_stats?: any;
    };
    visualizations?: Array<{
      visualization_id?: string;
      chart_type: string;
      library?: string;
      title?: string;
      rationale?: string;
      chart_data?: any[];
      x_axis_key?: string;
      data_key?: string;
      colors?: string[];
      vega_lite_spec?: any;
    }>;
  };
  // Nested analysis object
  analysis?: {
    analysis_type: 'structured' | 'unstructured';
    summary: string;
    insights: Array<{
      insight_id?: string;
      type: string;
      title?: string;
      description: string;
      confidence?: number;
      confidence_score?: number;
      category?: string;
      priority?: string;
      action_items?: string[];
    }>;
    confidence_score?: number;
    visualizations?: Array<{
      type: string;
      data: any;
    }>;
  };
  // Direct insights for convenience
  insights?: Array<{
    insight_id?: string;
    type: string;
    title?: string;
    description: string;
    confidence?: number;
    confidence_score?: number;
    category?: string;
    priority?: string;
    action_items?: string[];
    recommendations?: string[];
    [key: string]: any;
  }>;
  // AAR specific analysis - flexible type to accommodate various analysis formats
  aar_analysis?: any;
  error?: string;
}

/**
 * Get available content metadata from the Content pillar
 * 
 * Uses content_list_files intent to get available files.
 * 
 * @param tenantId - Tenant ID (optional)
 * @param contentType - Content type filter (optional)
 * @param limit - Max results (optional)
 * @param offset - Offset for pagination (optional)
 * @returns Promise<ContentMetadataResponse>
 */
export async function getAvailableContentMetadata(
  tenantId?: string,
  contentType?: 'structured' | 'unstructured',
  limit?: number,
  offset?: number
): Promise<ContentMetadataResponse> {
  const client = getGlobalExperiencePlaneClient();
  const resolvedTenantId = tenantId || (typeof window !== 'undefined' ? sessionStorage.getItem('tenant_id') || 'default' : 'default');
  const sessionId = typeof window !== 'undefined' ? sessionStorage.getItem('session_id') || '' : '';
  
  if (!sessionId) {
    console.warn('[insights API] No session ID available');
    return { success: true, content_metadata_items: [] };
  }
  
  try {
    const submitResponse = await client.submitIntent({
      intent_type: 'content_list_files',
      tenant_id: resolvedTenantId,
      session_id: sessionId,
      parameters: {
        artifact_type: 'parsed_content',
        limit,
        offset,
      },
    });
    
    // Poll for completion
    const maxAttempts = 30;
    let attempts = 0;
    
    while (attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 500));
      const status = await client.getExecutionStatus(submitResponse.execution_id, resolvedTenantId);
      
      if (status.status === 'completed') {
        const artifacts = status.artifacts || {};
        const files = (artifacts.files || []) as Array<{
          artifact_id?: string;
          name?: string;
          artifact_type?: string;
          created_at?: string;
        }>;
        
        // Transform to ContentMetadata format
        const contentMetadataItems: ContentMetadata[] = files.map(file => ({
          id: file.artifact_id || '',
          name: file.name || 'Unnamed',
          type: (contentType || 'structured') as 'structured' | 'unstructured',
          source: file.artifact_type || 'file',
          created_at: file.created_at || new Date().toISOString(),
        }));
        
        return { success: true, content_metadata_items: contentMetadataItems };
      } else if (status.status === 'failed') {
        return { success: false, error: status.error || 'Failed to get content metadata' };
      }
      
      attempts++;
    }
    
    return { success: false, error: 'Request timed out' };
  } catch (error) {
    console.error('[insights API] getAvailableContentMetadata error:', error);
    return { success: true, content_metadata_items: [] }; // Return empty on error to avoid breaking UI
  }
}

/**
 * Get content metadata by ID
 */
export async function getContentMetadataById(id: string): Promise<ContentMetadata | null> {
  console.warn('[insights API] getContentMetadataById - stub implementation');
  return null;
}

/**
 * Analyze content for insights
 * 
 * Uses analyze_structured_data or interpret_data_self_discovery intent
 * based on content type.
 */
export async function analyzeContentForInsights(
  requestOrContentId: AnalyzeContentRequest | string,
  options?: {
    analysisType?: 'structured' | 'unstructured';
    generateVisualizations?: boolean;
  }
): Promise<AnalyzeContentResponse> {
  const request = typeof requestOrContentId === 'string' 
    ? { content_id: requestOrContentId } 
    : requestOrContentId;
  
  const client = getGlobalExperiencePlaneClient();
  const tenantId = typeof window !== 'undefined' ? sessionStorage.getItem('tenant_id') || 'default' : 'default';
  const sessionId = typeof window !== 'undefined' ? sessionStorage.getItem('session_id') || '' : '';
  
  if (!sessionId) {
    console.warn('[insights API] No session ID available');
    return { success: false, error: 'No active session' };
  }
  
  try {
    const analysisType = request.analysis_type || request.content_type || options?.analysisType || 'unstructured';
    const fileId = request.file_id || request.content_id || '';
    
    // Choose intent based on analysis type
    const intentType = analysisType === 'structured' 
      ? 'analyze_structured_data' 
      : 'interpret_data_self_discovery';
    
    // Submit intent
    const submitResponse = await client.submitIntent({
      intent_type: intentType,
      tenant_id: tenantId,
      session_id: sessionId,
      parameters: {
        parsed_file_id: fileId,
        analysis_type: analysisType,
        include_visualization: request.analysis_options?.include_visualizations ?? options?.generateVisualizations ?? true,
      },
    });
    
    // Poll for completion
    const maxAttempts = 60;
    let attempts = 0;
    
    while (attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      const status = await client.getExecutionStatus(submitResponse.execution_id, tenantId);
      
      if (status.status === 'completed') {
        // Transform backend response to expected format
        const artifacts = status.artifacts || {};
        const analysis = (artifacts.analysis_result || artifacts.discovery || artifacts.interpretation) as Record<string, unknown> | undefined;
        
        return {
          success: true,
          summary: {
            textual: (analysis?.summary as string) || '',
            visualizations: (analysis?.visualizations as AnalyzeContentResponse['summary'])?.visualizations || [],
          },
          analysis: {
            analysis_type: analysisType as 'structured' | 'unstructured',
            summary: (analysis?.summary as string) || '',
            insights: ((analysis?.insights || analysis?.findings) as AnalyzeContentResponse['analysis'])?.insights || [],
            confidence_score: (analysis?.confidence as number) || 0,
          },
          insights: ((analysis?.insights || analysis?.findings) as AnalyzeContentResponse['insights']) || [],
        };
      } else if (status.status === 'failed') {
        return { success: false, error: status.error || 'Analysis failed' };
      }
      
      attempts++;
    }
    
    return { success: false, error: 'Analysis timed out' };
  } catch (error) {
    console.error('[insights API] analyzeContentForInsights error:', error);
    return { 
      success: false, 
      error: error instanceof Error ? error.message : 'Analysis failed' 
    };
  }
}

/**
 * Get EDA (Exploratory Data Analysis) analysis
 */
export async function getEDAAnalysis(
  fileId: string,
  options?: Record<string, any>
): Promise<{ success: boolean; analysis?: any; error?: string }> {
  console.warn('[insights API] getEDAAnalysis - stub implementation');
  return { success: true, analysis: {} };
}

/**
 * Get visualization analysis
 */
export async function getVisualizationAnalysis(
  fileId: string,
  options?: Record<string, any>
): Promise<{ success: boolean; visualizations?: any[]; error?: string }> {
  console.warn('[insights API] getVisualizationAnalysis - stub implementation');
  return { success: true, visualizations: [] };
}

/**
 * Process natural language query
 */
export async function processNaturalLanguageQuery(
  queryOrParams: string | {
    session_id?: string;
    query?: string;
    file_url?: string;
    context?: any;
    sessionToken?: string;
    token?: string;
  },
  context?: Record<string, any>
): Promise<{ success: boolean; result?: any; error?: string }> {
  console.warn('[insights API] processNaturalLanguageQuery - stub implementation');
  return { success: true, result: {} };
}

/**
 * Process chat message for insights
 */
export async function processChatMessage(params: {
  session_id?: string;
  message?: string;
  context?: any;
  sessionToken?: string;
  token?: string;
}): Promise<{ success: boolean; response?: any; error?: string }> {
  console.warn('[insights API] processChatMessage - stub implementation');
  return { success: true, response: {} };
}

/**
 * Run EDA analysis
 */
export async function runEDAAnalysis(params: {
  session_id?: string;
  file_url?: string;
  analysis_type?: string;
  options?: any;
}): Promise<{ success: boolean; result?: any; error?: string }> {
  console.warn('[insights API] runEDAAnalysis - stub implementation');
  return { success: true, result: {} };
}

/**
 * Generate visualizations
 */
export async function generateVisualizations(params: {
  session_id?: string;
  file_url?: string;
  chart_types?: string[];
  options?: any;
}): Promise<{ success: boolean; visualizations?: any[]; error?: string }> {
  console.warn('[insights API] generateVisualizations - stub implementation');
  return { success: true, visualizations: [] };
}
