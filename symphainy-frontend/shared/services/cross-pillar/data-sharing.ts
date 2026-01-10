// Cross-Pillar Data Sharing Module
import { 
  CrossPillarDataRequest,
  CrossPillarDataResponse,
  CrossPillarValidationRequest,
  CrossPillarValidationResponse,
  CrossPillarErrorResponse
} from './types';

// EC2 default: http://35.215.64.103:8000 (accessible from outside EC2)
// Option C: Override via NEXT_PUBLIC_API_URL environment variable
import { getApiUrl } from '@/shared/config/api-config';

// Use centralized API config (NO hardcoded values)
const API_URL = getApiUrl();

// Error handling utilities
class CrossPillarAPIError extends Error {
  public code?: string;
  public details?: any;
  public operation: 'data_sharing' | 'communication' | 'state_sync' | 'validation';
  public sourcePillar?: string;
  public targetPillar?: string;

  constructor(
    message: string,
    operation: 'data_sharing' | 'communication' | 'state_sync' | 'validation',
    code?: string,
    details?: any,
    sourcePillar?: string,
    targetPillar?: string
  ) {
    super(message);
    this.name = 'CrossPillarAPIError';
    this.operation = operation;
    this.code = code;
    this.details = details;
    this.sourcePillar = sourcePillar;
    this.targetPillar = targetPillar;
  }
}

// Enhanced error parsing
function parseAPIError(response: Response, responseText: string, operation: 'data_sharing' | 'communication' | 'state_sync' | 'validation', sourcePillar?: string, targetPillar?: string): CrossPillarAPIError {
  let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
  let errorCode = response.status.toString();
  let errorDetails = null;

  try {
    const errorJson = JSON.parse(responseText);
    errorMessage = errorJson.detail || errorJson.message || errorJson.error || errorMessage;
    errorCode = errorJson.code || errorCode;
    errorDetails = errorJson;
  } catch {
    // Response is not JSON, use as-is
    errorMessage = responseText || errorMessage;
  }

  // Provide user-friendly error messages
  const userFriendlyMessages: Record<string, string> = {
    '400': 'Invalid cross-pillar request. Please check your data and try again.',
    '401': 'Authentication required. Please log in again.',
    '403': 'Access denied. You may not have permission for cross-pillar operations.',
    '404': 'Cross-pillar service not found. The service may be temporarily unavailable.',
    '422': 'Invalid cross-pillar data format. Please ensure your data is in the correct format.',
    '500': 'Cross-pillar service error. Please try again later or contact support.',
    '502': 'Cross-pillar service temporarily unavailable. Please try again later.',
    '503': 'Cross-pillar service temporarily unavailable. Please try again later.',
    '504': 'Cross-pillar request timeout. Please try again with a smaller dataset.',
  };

  const friendlyMessage = userFriendlyMessages[errorCode] || errorMessage;

  return new CrossPillarAPIError(friendlyMessage, operation, errorCode, errorDetails, sourcePillar, targetPillar);
}

// Data sharing types and interfaces
export interface DataSharingConfig {
  sessionToken: string;
  sourcePillar: string;
  targetPillar: string;
  dataType: string;
  validationEnabled: boolean;
  retryAttempts: number;
  timeout: number;
}

export interface DataSharingResult {
  success: boolean;
  data?: any;
  error?: string;
  validationResult?: CrossPillarValidationResponse;
  metadata: {
    sourcePillar: string;
    targetPillar: string;
    dataType: string;
    timestamp: string;
    size: number;
    duration: number;
  };
}

// Share data with validation
export async function shareDataWithValidation(request: CrossPillarDataRequest): Promise<DataSharingResult> {
  const startTime = Date.now();
  
  try {
    // First validate the data
    const validationRequest: CrossPillarValidationRequest = {
      sessionToken: request.sessionToken,
      data: request.data,
      dataType: request.dataType,
      sourcePillar: request.sourcePillar,
      targetPillar: request.targetPillar,
      validationRules: getValidationRules(request.dataType, request.sourcePillar, request.targetPillar),
    };

    const validationResult = await validateCrossPillarData(validationRequest);
    
    if (!validationResult.isValid) {
      return {
        success: false,
        error: `Data validation failed: ${validationResult.errors.join(', ')}`,
        validationResult,
        metadata: {
          sourcePillar: request.sourcePillar,
          targetPillar: request.targetPillar,
          dataType: request.dataType,
          timestamp: new Date().toISOString(),
          size: JSON.stringify(request.data).length,
          duration: Date.now() - startTime,
        },
      };
    }

    // If validation passes, share the data
    const response = await fetch(
      `${API_URL}/api/cross-pillar/share-data`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${request.sessionToken}`,
        },
        body: JSON.stringify({
          session_token: request.sessionToken,
          source_pillar: request.sourcePillar,
          target_pillar: request.targetPillar,
          data_type: request.dataType,
          data: request.data,
          context: request.context || {},
        }),
      },
    );

    const responseText = await response.text();
    console.log("Share data with validation raw response:", responseText);

    if (!response.ok) {
      throw parseAPIError(response, responseText, 'data_sharing', request.sourcePillar, request.targetPillar);
    }

    const data = JSON.parse(responseText);
    
    return {
      success: true,
      data: data.data,
      validationResult,
      metadata: {
        sourcePillar: request.sourcePillar,
        targetPillar: request.targetPillar,
        dataType: request.dataType,
        timestamp: new Date().toISOString(),
        size: JSON.stringify(request.data).length,
        duration: Date.now() - startTime,
      },
    };
  } catch (error) {
    if (error instanceof CrossPillarAPIError) {
      throw error;
    }
    throw new CrossPillarAPIError(
      error instanceof Error ? error.message : 'Failed to share data with validation',
      'data_sharing',
      undefined,
      undefined,
      request.sourcePillar,
      request.targetPillar
    );
  }
}

// Get validation rules based on data type and pillars
function getValidationRules(dataType: string, sourcePillar: string, targetPillar: string): any {
  const baseRules = {
    required: true,
    maxSize: 10 * 1024 * 1024, // 10MB
    allowedTypes: ['object', 'array', 'string', 'number', 'boolean'],
  };

  // Pillar-specific rules
  const pillarRules: Record<string, any> = {
    content: {
      fileTypes: ['document', 'pdf', 'text', 'structured'],
      maxFileSize: 50 * 1024 * 1024, // 50MB
    },
    insights: {
      dataTypes: ['summary', 'analysis', 'recommendations', 'visualizations'],
      maxInsights: 100,
    },
    operations: {
      dataTypes: ['workflow', 'sop', 'blueprint', 'coexistence'],
      maxWorkflows: 10,
    },
    experience: {
      dataTypes: ['roadmap', 'poc', 'session', 'outputs'],
      maxOutputs: 20,
    },
  };

  // Data type specific rules
  const dataTypeRules: Record<string, any> = {
    file: {
      required: ['uuid', 'filename', 'file_type', 'file_size'],
      maxSize: 100 * 1024 * 1024, // 100MB
    },
    summary: {
      required: ['summary', 'key_insights', 'recommendations'],
      maxLength: 10000,
    },
    workflow: {
      required: ['nodes', 'edges'],
      maxNodes: 100,
      maxEdges: 200,
    },
    roadmap: {
      required: ['phases', 'timeline', 'milestones'],
      maxPhases: 20,
    },
  };

  return {
    ...baseRules,
    ...pillarRules[sourcePillar],
    ...pillarRules[targetPillar],
    ...dataTypeRules[dataType],
  };
}

// Validate cross-pillar data
export async function validateCrossPillarData(request: CrossPillarValidationRequest): Promise<CrossPillarValidationResponse> {
  try {
    const response = await fetch(
      `${API_URL}/api/cross-pillar/validate`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${request.sessionToken}`,
        },
        body: JSON.stringify({
          session_token: request.sessionToken,
          data: request.data,
          data_type: request.dataType,
          source_pillar: request.sourcePillar,
          target_pillar: request.targetPillar,
          validation_rules: request.validationRules,
        }),
      },
    );

    const responseText = await response.text();
    console.log("Validate cross-pillar data raw response:", responseText);

    if (!response.ok) {
      throw parseAPIError(response, responseText, 'validation', request.sourcePillar, request.targetPillar);
    }

    const data = JSON.parse(responseText);
    return data;
  } catch (error) {
    if (error instanceof CrossPillarAPIError) {
      throw error;
    }
    throw new CrossPillarAPIError(
      error instanceof Error ? error.message : 'Failed to validate cross-pillar data',
      'validation',
      undefined,
      undefined,
      request.sourcePillar,
      request.targetPillar
    );
  }
}

// Batch data sharing
export interface BatchDataSharingRequest {
  sessionToken: string;
  requests: CrossPillarDataRequest[];
  parallel: boolean;
  maxConcurrent: number;
}

export interface BatchDataSharingResult {
  results: DataSharingResult[];
  summary: {
    total: number;
    successful: number;
    failed: number;
    totalDuration: number;
    avgDuration: number;
  };
}

export async function batchShareData(request: BatchDataSharingRequest): Promise<BatchDataSharingResult> {
  const startTime = Date.now();
  const results: DataSharingResult[] = [];

  if (request.parallel) {
    // Execute requests in parallel with concurrency limit
    const chunks = [];
    for (let i = 0; i < request.requests.length; i += request.maxConcurrent) {
      chunks.push(request.requests.slice(i, i + request.maxConcurrent));
    }

    for (const chunk of chunks) {
      const chunkPromises = chunk.map(req => shareDataWithValidation(req));
      const chunkResults = await Promise.allSettled(chunkPromises);
      
      chunkResults.forEach((result, index) => {
        if (result.status === 'fulfilled') {
          results.push(result.value);
        } else {
          results.push({
            success: false,
            error: result.reason?.message || 'Unknown error',
            metadata: {
              sourcePillar: chunk[index].sourcePillar,
              targetPillar: chunk[index].targetPillar,
              dataType: chunk[index].dataType,
              timestamp: new Date().toISOString(),
              size: 0,
              duration: 0,
            },
          });
        }
      });
    }
  } else {
    // Execute requests sequentially
    for (const req of request.requests) {
      try {
        const result = await shareDataWithValidation(req);
        results.push(result);
      } catch (error) {
        results.push({
          success: false,
          error: error instanceof Error ? error.message : 'Unknown error',
          metadata: {
            sourcePillar: req.sourcePillar,
            targetPillar: req.targetPillar,
            dataType: req.dataType,
            timestamp: new Date().toISOString(),
            size: 0,
            duration: 0,
          },
        });
      }
    }
  }

  const totalDuration = Date.now() - startTime;
  const successful = results.filter(r => r.success).length;
  const failed = results.filter(r => !r.success).length;

  return {
    results,
    summary: {
      total: results.length,
      successful,
      failed,
      totalDuration,
      avgDuration: totalDuration / results.length,
    },
  };
} 