// Cross-Pillar Integration Test Suite
import { CrossPillarService } from '../shared/services/cross-pillar';
import { ContentService } from '../shared/services/content';
import { InsightsService } from '../shared/services/insights';
import { OperationsService } from '../shared/services/operations';
import { ExperienceService } from '../shared/services/experience';

// Mock fetch for testing
const mockFetch = jest.fn();
global.fetch = mockFetch;

// Helper function to create mock responses
const createMockResponse = (data: any) => ({
  ok: true,
  text: async () => JSON.stringify(data),
  json: async () => data
});

describe('Cross-Pillar Integration Tests', () => {
  const testSessionToken = 'test-session-token';
  const mockData = {
    content: { files: [{ uuid: 'test-file-1', filename: 'test.pdf', file_type: 'pdf' }] },
    insights: { summary: 'Test insights summary', key_insights: ['Insight 1', 'Insight 2'] },
    operations: { workflow: { nodes: [], edges: [] }, sop: 'Test SOP content' },
    experience: { roadmap: { phases: [] }, poc: { proposal: 'Test POC' } }
  };

  beforeEach(() => {
    mockFetch.mockClear();
    mockFetch.mockReset();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Data Sharing Tests', () => {
    test('should share data between Content and Insights pillars', async () => {
      // Mock successful response
      mockFetch.mockResolvedValueOnce(createMockResponse({
        success: true,
        sourcePillar: 'content',
        targetPillar: 'insights',
        dataType: 'files',
        timestamp: new Date().toISOString()
      }));

      const request = {
        sessionToken: testSessionToken,
        sourcePillar: 'content' as const,
        targetPillar: 'insights' as const,
        dataType: 'files',
        data: mockData.content.files,
        context: { analysis_type: 'file_analysis' }
      };

      const result = await CrossPillarService.shareData(request);
      expect(result.success).toBe(true);
      expect(result.sourcePillar).toBe('content');
      expect(result.targetPillar).toBe('insights');
    });

    test('should share data between Insights and Operations pillars', async () => {
      // Mock successful response
      mockFetch.mockResolvedValueOnce(createMockResponse({
        success: true,
        sourcePillar: 'insights',
        targetPillar: 'operations',
        dataType: 'analysis_results',
        timestamp: new Date().toISOString()
      }));

      const request = {
        sessionToken: testSessionToken,
        sourcePillar: 'insights' as const,
        targetPillar: 'operations' as const,
        dataType: 'analysis_results',
        data: mockData.insights,
        context: { workflow_generation: true }
      };

      const result = await CrossPillarService.shareData(request);
      expect(result.success).toBe(true);
      expect(result.sourcePillar).toBe('insights');
      expect(result.targetPillar).toBe('operations');
    });

    test('should share data between Operations and Experience pillars', async () => {
      // Mock successful response
      mockFetch.mockResolvedValueOnce(createMockResponse({
        success: true,
        sourcePillar: 'operations',
        targetPillar: 'experience',
        dataType: 'blueprint',
        timestamp: new Date().toISOString()
      }));

      const request = {
        sessionToken: testSessionToken,
        sourcePillar: 'operations' as const,
        targetPillar: 'experience' as const,
        dataType: 'blueprint',
        data: mockData.operations,
        context: { roadmap_generation: true }
      };

      const result = await CrossPillarService.shareData(request);
      expect(result.success).toBe(true);
      expect(result.sourcePillar).toBe('operations');
      expect(result.targetPillar).toBe('experience');
    });

    test('should validate data before sharing', async () => {
      // Mock validation response first
      mockFetch.mockResolvedValueOnce(createMockResponse({
        isValid: true,
        errors: [],
        warnings: [],
        suggestions: [],
        validationScore: 95
      }));
      
      // Mock data sharing response second
      mockFetch.mockResolvedValueOnce(createMockResponse({
        success: true,
        data: mockData.content.files,
        sourcePillar: 'content',
        targetPillar: 'insights',
        dataType: 'files',
        timestamp: new Date().toISOString()
      }));

      const request = {
        sessionToken: testSessionToken,
        sourcePillar: 'content' as const,
        targetPillar: 'insights' as const,
        dataType: 'files',
        data: mockData.content.files,
        context: { analysis_type: 'file_analysis' }
      };

      const result = await CrossPillarService.shareDataWithValidation(request);
      expect(result.success).toBe(true);
      expect(result.validationResult?.isValid).toBe(true);
    });

    test('should handle batch data sharing', async () => {
      // Mock responses for batch data sharing (2 requests, each needs validation + data sharing)
      // Request 1: content -> insights (validation + data sharing)
      mockFetch
        .mockResolvedValueOnce(createMockResponse({
          isValid: true,
          errors: [],
          warnings: [],
          suggestions: [],
          validationScore: 95
        }))
        .mockResolvedValueOnce(createMockResponse({
          success: true,
          data: mockData.content.files,
          sourcePillar: 'content',
          targetPillar: 'insights',
          dataType: 'files',
          timestamp: new Date().toISOString()
        }))
        // Request 2: insights -> operations (validation + data sharing)
        .mockResolvedValueOnce(createMockResponse({
          isValid: true,
          errors: [],
          warnings: [],
          suggestions: [],
          validationScore: 90
        }))
        .mockResolvedValueOnce(createMockResponse({
          success: true,
          data: mockData.insights,
          sourcePillar: 'insights',
          targetPillar: 'operations',
          dataType: 'analysis_results',
          timestamp: new Date().toISOString()
        }));

      const requests = [
        {
          sessionToken: testSessionToken,
          sourcePillar: 'content' as const,
          targetPillar: 'insights' as const,
          dataType: 'files',
          data: mockData.content.files,
          context: { analysis_type: 'file_analysis' }
        },
        {
          sessionToken: testSessionToken,
          sourcePillar: 'insights' as const,
          targetPillar: 'operations' as const,
          dataType: 'analysis_results',
          data: mockData.insights,
          context: { workflow_generation: true }
        }
      ];

      const result = await CrossPillarService.batchShareData({
        sessionToken: testSessionToken,
        requests,
        parallel: true,
        maxConcurrent: 2
      });

      expect(result.summary.total).toBe(2);
      expect(result.summary.successful).toBe(2);
    });
  });

  describe('Communication Tests', () => {
    test('should send communication between pillars', async () => {
      // Mock successful communication response
      mockFetch.mockResolvedValueOnce(createMockResponse({
        success: true,
        messageId: 'msg-123',
        timestamp: new Date().toISOString()
      }));

      const request = {
        sessionToken: testSessionToken,
        sourcePillar: 'content' as const,
        targetPillar: 'insights' as const,
        messageType: 'data_request' as const,
        message: { request_type: 'file_analysis', file_uuids: ['test-file-1'] },
        priority: 'medium' as const
      };

      const result = await CrossPillarService.sendCommunication(request);
      expect(result.success).toBe(true);
      expect(result.messageId).toBeDefined();
    });

    test('should broadcast messages to multiple pillars', async () => {
      // Mock multiple responses for broadcast (one for each target pillar)
      mockFetch
        .mockResolvedValueOnce(createMockResponse({
          success: true,
          messageId: 'msg-1',
          timestamp: new Date().toISOString()
        }))
        .mockResolvedValueOnce(createMockResponse({
          success: true,
          messageId: 'msg-2',
          timestamp: new Date().toISOString()
        }))
        .mockResolvedValueOnce(createMockResponse({
          success: true,
          messageId: 'msg-3',
          timestamp: new Date().toISOString()
        }));

      const request = {
        sessionToken: testSessionToken,
        sourcePillar: 'content' as const,
        targetPillars: ['insights', 'operations', 'experience'],
        messageType: 'status_update' as const,
        message: { status: 'files_uploaded', count: 5 },
        priority: 'high' as const
      };

      const result = await CrossPillarService.broadcastMessage(request);
      expect(result.summary.total).toBe(3);
      expect(result.summary.successful).toBe(3);
    });

    test('should handle communication retries', async () => {
      // Mock successful retry response
      mockFetch.mockResolvedValueOnce(createMockResponse({
        success: true,
        messageId: 'msg-retry-123',
        timestamp: new Date().toISOString()
      }));

      const request = {
        sessionToken: testSessionToken,
        sourcePillar: 'content' as const,
        targetPillar: 'insights' as const,
        messageType: 'data_request' as const,
        message: { request_type: 'file_analysis' },
        priority: 'high' as const
      };

      const result = await CrossPillarService.sendMessageWithRetry(request, 3);
      expect(result.success).toBe(true);
    });
  });

  describe('State Synchronization Tests', () => {
    test('should sync state between pillars', async () => {
      // Mock successful state sync response
      mockFetch.mockResolvedValueOnce(createMockResponse({
        success: true,
        version: '1.0.0',
        timestamp: new Date().toISOString()
      }));

      const request = {
        sessionToken: testSessionToken,
        pillar: 'content' as const,
        state: { files: mockData.content.files, status: 'uploaded' },
        version: '1.0.0',
        timestamp: new Date().toISOString()
      };

      const result = await CrossPillarService.syncState(request);
      expect(result.success).toBe(true);
      expect(result.version).toBe('1.0.0');
    });

    test('should handle state conflicts', async () => {
      // Mock state sync with conflicts response
      mockFetch.mockResolvedValueOnce(createMockResponse({
        success: true,
        version: '1.0.1',
        conflicts: ['conflict-1'],
        timestamp: new Date().toISOString()
      }));

      const request = {
        sessionToken: testSessionToken,
        pillar: 'insights' as const,
        state: { analysis: mockData.insights, conflicts: ['conflict-1'] },
        version: '1.0.1',
        timestamp: new Date().toISOString()
      };

      const result = await CrossPillarService.syncState(request);
      expect(result.success).toBe(true);
      expect(result.conflicts).toBeDefined();
    });
  });

  describe('Validation Tests', () => {
    test('should validate cross-pillar data', async () => {
      // Mock successful validation response
      mockFetch.mockResolvedValueOnce(createMockResponse({
        isValid: true,
        errors: [],
        warnings: [],
        suggestions: [],
        validationScore: 95
      }));

      const request = {
        sessionToken: testSessionToken,
        data: mockData.content.files,
        dataType: 'files',
        sourcePillar: 'content',
        targetPillar: 'insights',
        validationRules: {
          required: true,
          maxSize: 10 * 1024 * 1024,
          allowedTypes: ['object', 'array']
        }
      };

      const result = await CrossPillarService.validateData(request);
      expect(result.isValid).toBe(true);
      expect(result.validationScore).toBeGreaterThan(80);
    });

    test('should handle validation errors', async () => {
      // Mock validation error response
      mockFetch.mockResolvedValueOnce(createMockResponse({
        isValid: false,
        errors: ['Data is required'],
        warnings: [],
        suggestions: ['Provide valid data'],
        validationScore: 0
      }));

      const request = {
        sessionToken: testSessionToken,
        data: null,
        dataType: 'files',
        sourcePillar: 'content',
        targetPillar: 'insights',
        validationRules: { required: true }
      };

      const result = await CrossPillarService.validateData(request);
      expect(result.isValid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
    });
  });

  describe('Smart City Integration Tests', () => {
    test('should route requests through Traffic Cop', async () => {
      // Mock Traffic Cop routing response
      mockFetch.mockResolvedValueOnce(createMockResponse({
        status: 'approved',
        route: {
          path: ['content', 'insights'],
          priority: 'medium'
        }
      }));

      const request = {
        sessionToken: testSessionToken,
        sourcePillar: 'content',
        targetPillar: 'insights',
        operation: 'data_sharing',
        data: mockData.content.files,
        priority: 'medium' as const
      };

      const result = await CrossPillarService.routeRequest(request);
      expect(result.status).toBe('approved');
      expect(result.route.path).toBeDefined();
    });

    test('should send messages through Post Office', async () => {
      // Mock Post Office message response
      mockFetch.mockResolvedValueOnce(createMockResponse({
        status: 'delivered',
        messageId: 'post-msg-123',
        timestamp: new Date().toISOString()
      }));

      const message = {
        type: 'data_request',
        sessionToken: testSessionToken,
        sourcePillar: 'content',
        targetPillar: 'insights',
        data: { request_type: 'file_analysis' },
        priority: 'medium' as const,
        timestamp: new Date().toISOString()
      };

      const result = await CrossPillarService.sendMessage(message);
      expect(result.status).toBe('delivered');
      expect(result.messageId).toBeDefined();
    });

    test('should orchestrate workflows through Conductor', async () => {
      // Mock Conductor orchestration response
      mockFetch.mockResolvedValueOnce(createMockResponse({
        status: 'queued',
        workflowId: 'workflow-123',
        timestamp: new Date().toISOString()
      }));

      const request = {
        sessionToken: testSessionToken,
        workflowType: 'comprehensive' as const,
        sourcePillar: 'content',
        targetPillar: 'experience',
        inputs: { files: mockData.content.files, analysis: mockData.insights },
        priority: 'high' as const
      };

      const result = await CrossPillarService.orchestrateWorkflow(request);
      expect(result.status).toBe('queued');
      expect(result.workflowId).toBeDefined();
    });

    test('should persist state through Archive', async () => {
      // Mock Archive state persistence response
      mockFetch.mockResolvedValueOnce(createMockResponse({
        status: 'saved',
        stateId: 'state-123',
        timestamp: new Date().toISOString()
      }));

      const request = {
        sessionToken: testSessionToken,
        pillar: 'content',
        state: { files: mockData.content.files, metadata: { uploaded: true } },
        metadata: {
          operation: 'file_upload',
          timestamp: new Date().toISOString(),
          userId: 'test-user',
          version: '1.0.0',
          crossPillar: true
        }
      };

      const result = await CrossPillarService.persistState(request);
      expect(result.status).toBe('saved');
      expect(result.stateId).toBeDefined();
    });
  });

  describe('Performance and Health Tests', () => {
    test('should get performance metrics', async () => {
      // Mock performance metrics response
      mockFetch.mockResolvedValueOnce(createMockResponse({
        sessionToken: testSessionToken,
        timestamp: new Date().toISOString(),
        metrics: {
          dataSharing: {
            totalRequests: 10,
            successfulRequests: 9,
            failedRequests: 1,
            avgResponseTime: 150
          },
          communication: {
            totalMessages: 20,
            deliveredMessages: 18,
            failedMessages: 2,
            avgDeliveryTime: 100
          },
          stateSync: {
            totalSyncs: 5,
            successfulSyncs: 5,
            failedSyncs: 0,
            avgSyncTime: 200
          },
          validation: {
            totalValidations: 15,
            passedValidations: 14,
            failedValidations: 1,
            avgValidationTime: 50
          }
        }
      }));

      const metrics = await CrossPillarService.getPerformanceMetrics(testSessionToken);
      expect(metrics.sessionToken).toBe(testSessionToken);
      expect(metrics.metrics.dataSharing.totalRequests).toBeGreaterThanOrEqual(0);
      expect(metrics.metrics.communication.totalMessages).toBeGreaterThanOrEqual(0);
    });

    test('should get health check', async () => {
      // Mock health check response
      mockFetch.mockResolvedValueOnce(createMockResponse({
        sessionToken: testSessionToken,
        timestamp: new Date().toISOString(),
        status: 'healthy',
        checks: {
          dataSharing: 'healthy',
          communication: 'healthy',
          stateSync: 'healthy',
          validation: 'healthy'
        },
        details: {}
      }));

      const health = await CrossPillarService.getHealthCheck(testSessionToken);
      expect(health.sessionToken).toBe(testSessionToken);
      expect(['healthy', 'degraded', 'unhealthy']).toContain(health.status);
    });

    test('should monitor comprehensive health', async () => {
      // Mock health check response
      mockFetch.mockResolvedValueOnce(createMockResponse({
        sessionToken: testSessionToken,
        timestamp: new Date().toISOString(),
        status: 'healthy',
        checks: {
          dataSharing: 'healthy',
          communication: 'healthy',
          stateSync: 'healthy',
          validation: 'healthy'
        },
        details: {}
      }));
      
      // Mock performance metrics response
      mockFetch.mockResolvedValueOnce(createMockResponse({
        sessionToken: testSessionToken,
        timestamp: new Date().toISOString(),
        metrics: {
          dataSharing: { totalRequests: 10, successfulRequests: 9 },
          communication: { totalMessages: 20, deliveredMessages: 18 },
          stateSync: { totalSyncs: 5, successfulSyncs: 5 },
          validation: { totalValidations: 15, passedValidations: 14 }
        }
      }));
      
      // Mock bridge state response
      mockFetch.mockResolvedValueOnce(createMockResponse({
        isConnected: true,
        activePillars: ['content', 'insights', 'operations', 'experience'],
        lastSync: new Date().toISOString(),
        errors: []
      }));

      const monitoring = await CrossPillarService.monitorCrossPillarHealth(testSessionToken);
      expect(monitoring.health).toBeDefined();
      expect(monitoring.performance).toBeDefined();
      expect(monitoring.bridgeState).toBeDefined();
    });
  });

  describe('Event System Tests', () => {
    test('should emit cross-pillar events', async () => {
      // Mock event emission response
      mockFetch.mockResolvedValueOnce(createMockResponse({
        success: true,
        eventId: 'event-123',
        timestamp: new Date().toISOString()
      }));

      const event = {
        type: 'data_shared' as const,
        sessionToken: testSessionToken,
        sourcePillar: 'content',
        targetPillar: 'insights',
        data: { files: mockData.content.files },
        timestamp: new Date().toISOString(),
        metadata: { operation: 'file_analysis' }
      };

      const result = await CrossPillarService.emitEvent(event);
      expect(result.success).toBe(true);
      expect(result.eventId).toBeDefined();
    });
  });

  describe('Comprehensive Integration Tests', () => {
    test('should perform end-to-end cross-pillar workflow', async () => {
      // Mock multiple responses for the end-to-end workflow
      mockFetch
        .mockResolvedValueOnce(createMockResponse({
          success: true,
          sourcePillar: 'content',
          targetPillar: 'insights',
          dataType: 'files',
          timestamp: new Date().toISOString()
        }))
        .mockResolvedValueOnce(createMockResponse({
          success: true,
          sourcePillar: 'insights',
          targetPillar: 'operations',
          dataType: 'analysis_results',
          timestamp: new Date().toISOString()
        }))
        .mockResolvedValueOnce(createMockResponse({
          success: true,
          sourcePillar: 'operations',
          targetPillar: 'experience',
          dataType: 'blueprint',
          timestamp: new Date().toISOString()
        }))
        .mockResolvedValueOnce(createMockResponse({
          status: 'approved',
          route: {
            path: ['content', 'experience'],
            priority: 'medium'
          }
        }))
        .mockResolvedValueOnce(createMockResponse({
          workflowId: 'comprehensive-workflow-123',
          status: 'completed',
          timestamp: new Date().toISOString()
        }));

      // 1. Share content data to insights
      const contentToInsights = await CrossPillarService.shareData({
        sessionToken: testSessionToken,
        sourcePillar: 'content',
        targetPillar: 'insights',
        dataType: 'files',
        data: mockData.content.files
      });
      expect(contentToInsights.success).toBe(true);

      // 2. Share insights data to operations
      const insightsToOperations = await CrossPillarService.shareData({
        sessionToken: testSessionToken,
        sourcePillar: 'insights',
        targetPillar: 'operations',
        dataType: 'analysis_results',
        data: mockData.insights
      });
      expect(insightsToOperations.success).toBe(true);

      // 3. Share operations data to experience
      const operationsToExperience = await CrossPillarService.shareData({
        sessionToken: testSessionToken,
        sourcePillar: 'operations',
        targetPillar: 'experience',
        dataType: 'blueprint',
        data: mockData.operations
      });
      expect(operationsToExperience.success).toBe(true);

      // 4. Perform comprehensive operation
      const comprehensive = await CrossPillarService.comprehensiveCrossPillarOperation(
        testSessionToken,
        'content',
        'experience',
        'comprehensive',
        { files: mockData.content.files, analysis: mockData.insights, blueprint: mockData.operations }
      );
      expect(comprehensive.workflowId).toBeDefined();
    });

    test('should handle error scenarios gracefully', async () => {
      // Mock error response for invalid session token
      mockFetch.mockRejectedValueOnce(new Error('Invalid session token'));

      // Test with invalid session token
      await expect(CrossPillarService.shareData({
        sessionToken: 'invalid-token',
        sourcePillar: 'content',
        targetPillar: 'insights',
        dataType: 'files',
        data: mockData.content.files
      })).rejects.toThrow();

      // Mock validation error response for invalid data
      mockFetch.mockResolvedValueOnce(createMockResponse({
        isValid: false,
        errors: ['Data is required'],
        warnings: [],
        suggestions: ['Provide valid data'],
        validationScore: 0
      }));

      // Test with invalid data
      await expect(CrossPillarService.validateData({
        sessionToken: testSessionToken,
        data: null,
        dataType: 'files',
        sourcePillar: 'content',
        targetPillar: 'insights',
        validationRules: { required: true }
      })).resolves.toHaveProperty('isValid', false);
    });
  });
}); 