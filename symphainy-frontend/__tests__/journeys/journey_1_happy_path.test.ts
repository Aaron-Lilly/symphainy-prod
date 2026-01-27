/**
 * Journey 1 Happy Path Test
 * 
 * IMMEDIATE TEST: Run this to see where Journey 1 breaks
 * 
 * This test executes Journey 1 Happy Path end-to-end and documents failures.
 * Fix only what blocks Journey 1.
 */

import { ContentAPIManager } from '@/shared/managers/ContentAPIManager';
import {
  createMockPlatformState,
  createMockFile,
  mockSuccessfulIntent,
  resetAllMocks,
} from '../utils/test-helpers';

describe('Journey 1: Happy Path Test (IMMEDIATE)', () => {
  let contentAPIManager: ContentAPIManager;
  let mockPlatformState: ReturnType<typeof createMockPlatformState>;
  let executionStatuses: Record<string, { pollCount: number; maxPolls: number }>;
  let testResults: {
    step1_ingest_file: 'pass' | 'fail' | 'not_run';
    step2_parse_content: 'pass' | 'fail' | 'not_run';
    step3_extract_embeddings: 'pass' | 'fail' | 'not_run';
    step4_save_materialization: 'pass' | 'fail' | 'not_run';
    step5_get_semantic_interpretation: 'pass' | 'fail' | 'not_run';
    blockers: string[];
  };

  beforeEach(() => {
    mockPlatformState = createMockPlatformState();
    executionStatuses = {}; // Initialize execution statuses tracking
    // Create ContentAPIManager with mock getPlatformState
    contentAPIManager = new ContentAPIManager(
      undefined, // experiencePlaneClient (will use default)
      () => mockPlatformState as any // getPlatformState function
    );
    resetAllMocks(mockPlatformState);
    
    testResults = {
      step1_ingest_file: 'not_run',
      step2_parse_content: 'not_run',
      step3_extract_embeddings: 'not_run',
      step4_save_materialization: 'not_run',
      step5_get_semantic_interpretation: 'not_run',
      blockers: [],
    };
  });

  afterEach(() => {
    // Log test results
    console.log('\n=== Journey 1 Happy Path Test Results ===');
    console.log('Step 1 (ingest_file):', testResults.step1_ingest_file);
    console.log('Step 2 (parse_content):', testResults.step2_parse_content);
    console.log('Step 3 (extract_embeddings):', testResults.step3_extract_embeddings);
    console.log('Step 4 (save_materialization):', testResults.step4_save_materialization);
    console.log('Step 5 (get_semantic_interpretation):', testResults.step5_get_semantic_interpretation);
    if (testResults.blockers.length > 0) {
      console.log('\n🚨 Blockers Identified:');
      testResults.blockers.forEach((blocker, i) => {
        console.log(`${i + 1}. ${blocker}`);
      });
    }
    console.log('==========================================\n');
  });

  test('Journey 1 Happy Path - Complete End-to-End', async () => {
    const file = createMockFile('test-document.txt', 'This is test content for Journey 1', 5000);

    // ============================================
    // Step 1: ingest_file
    // ============================================
    try {
      console.log('📤 Step 1: Testing ingest_file...');
      
      // Mock successful intent execution
      const executionId = `exec-ingest-${Date.now()}`;
      (mockPlatformState.submitIntent as jest.Mock).mockResolvedValueOnce(executionId);
      
      // Mock execution status polling - track by execution ID
      executionStatuses[executionId] = { pollCount: 0, maxPolls: 2 };
      
      (mockPlatformState.getExecutionStatus as jest.Mock).mockImplementation(async (execId?: string) => {
        const execIdToUse = execId || executionId;
        if (!executionStatuses[execIdToUse]) {
          executionStatuses[execIdToUse] = { pollCount: 0, maxPolls: 2 };
        }
        
        executionStatuses[execIdToUse].pollCount++;
        const pollCount = executionStatuses[execIdToUse].pollCount;
        
        if (execIdToUse === executionId) {
          if (pollCount < 2) {
            // First call: pending
            return {
              status: 'pending',
              execution_id: executionId,
            };
          } else {
            // Second call: completed with artifacts
            return {
              status: 'completed',
              execution_id: executionId,
              artifacts: {
                file: {
                  semantic_payload: {
                    file_id: 'file-123',
                    boundary_contract_id: 'boundary-123',
                    materialization_pending: true,
                    file_reference: 'file:test-tenant:test-session:file-123',
                  },
                },
              },
            };
          }
        }
        
        // Default: pending
        return { status: 'pending', execution_id: execIdToUse };
      });

      const uploadResult = await contentAPIManager.uploadFile(file);
      
      // Log actual result for debugging
      if (!uploadResult.success) {
        console.log('❌ uploadResult.error:', uploadResult.error);
        console.log('❌ uploadResult:', JSON.stringify(uploadResult, null, 2));
      }
      
      expect(uploadResult.success).toBe(true);
      expect(uploadResult.file?.metadata?.file_id).toBe('file-123');
      expect(uploadResult.file?.metadata?.materialization_pending).toBe(true);
      // submitIntent is called with (intent, params, metadata) - 3 arguments
      expect(mockPlatformState.submitIntent).toHaveBeenCalledWith('ingest_file', expect.any(Object), expect.any(Object));
      expect(mockPlatformState.trackExecution).toHaveBeenCalled();
      
      testResults.step1_ingest_file = 'pass';
      console.log('✅ Step 1 (ingest_file): PASS');
    } catch (error) {
      testResults.step1_ingest_file = 'fail';
      testResults.blockers.push(`Step 1 (ingest_file) failed: ${error instanceof Error ? error.message : String(error)}`);
      console.log('❌ Step 1 (ingest_file): FAIL -', error);
      throw error; // Stop here if ingest_file fails
    }

    // ============================================
    // Step 2: parse_content
    // ============================================
    try {
      console.log('📄 Step 2: Testing parse_content...');
      
      mockSuccessfulIntent(mockPlatformState, 'parse_content', {
        parsed_file: {
          semantic_payload: {
            parsed_file_id: 'file-123',
            parsed_file_reference: 'parsed:test-tenant:test-session:file-123',
            structure: { type: 'unstructured' },
            chunks: ['chunk1', 'chunk2'],
          },
        },
      });

      const parseResult = await contentAPIManager.parseFile(
        'file-123',
        'file:test-tenant:test-session:file-123'
      );
      
      expect(parseResult.success).toBe(true);
      expect(mockPlatformState.submitIntent).toHaveBeenCalledWith('parse_content', expect.any(Object));
      expect(mockPlatformState.trackExecution).toHaveBeenCalled();
      
      testResults.step2_parse_content = 'pass';
      console.log('✅ Step 2 (parse_content): PASS');
    } catch (error) {
      testResults.step2_parse_content = 'fail';
      testResults.blockers.push(`Step 2 (parse_content) failed: ${error instanceof Error ? error.message : String(error)}`);
      console.log('❌ Step 2 (parse_content): FAIL -', error);
      throw error; // Stop here if parse_content fails
    }

    // ============================================
    // Step 3: extract_embeddings
    // ============================================
    try {
      console.log('🔍 Step 3: Testing extract_embeddings...');
      
      // Mock successful extract_embeddings execution
      const embeddingExecutionId = `exec-embed-${Date.now()}`;
      (mockPlatformState.submitIntent as jest.Mock).mockResolvedValue(embeddingExecutionId);
      
      let embedPollCount = 0;
      (mockPlatformState.getExecutionStatus as jest.Mock).mockImplementation(async () => {
        embedPollCount++;
        if (embedPollCount < 2) {
          return { status: 'pending', execution_id: embeddingExecutionId };
        } else {
          return {
            status: 'completed',
            execution_id: embeddingExecutionId,
            artifacts: {
              embeddings: {
                semantic_payload: {
                  embeddings_id: 'emb-123',
                  embedding_reference: 'emb:test-tenant:test-session:emb-123',
                  embeddings: [[0.1, 0.2, 0.3]],
                  metadata: { model: 'test-model' },
                },
              },
            },
          };
        }
      });

      const embeddingResult = await contentAPIManager.extractEmbeddings(
        'file-123',
        'parsed:test-tenant:test-session:file-123'
      );
      
      expect(embeddingResult.success).toBe(true);
      expect(mockPlatformState.submitIntent).toHaveBeenCalledWith('extract_embeddings', expect.any(Object));
      expect(mockPlatformState.trackExecution).toHaveBeenCalled();
      
      testResults.step3_extract_embeddings = 'pass';
      console.log('✅ Step 3 (extract_embeddings): PASS');
    } catch (error) {
      testResults.step3_extract_embeddings = 'fail';
      testResults.blockers.push(`Step 3 (extract_embeddings) failed: ${error instanceof Error ? error.message : String(error)}`);
      console.log('❌ Step 3 (extract_embeddings): FAIL -', error);
      throw error; // Stop here if extract_embeddings fails
    }

    // ============================================
    // Step 4: save_materialization
    // ============================================
    try {
      console.log('💾 Step 4: Testing save_materialization...');
      
      // Mock successful save_materialization execution
      const saveExecutionId = `exec-save-${Date.now()}`;
      (mockPlatformState.submitIntent as jest.Mock).mockResolvedValueOnce(saveExecutionId);
      
      executionStatuses[saveExecutionId] = { pollCount: 0, maxPolls: 2 };
      
      (mockPlatformState.getExecutionStatus as jest.Mock).mockImplementation(async (execId?: string) => {
        const execIdToUse = execId || saveExecutionId;
        if (!executionStatuses[execIdToUse]) {
          executionStatuses[execIdToUse] = { pollCount: 0, maxPolls: 2 };
        }
        
        executionStatuses[execIdToUse].pollCount++;
        const pollCount = executionStatuses[execIdToUse].pollCount;
        
        if (execIdToUse === saveExecutionId) {
          if (pollCount < 2) {
            return { status: 'pending', execution_id: saveExecutionId };
          } else {
            return {
              status: 'completed',
              execution_id: saveExecutionId,
              artifacts: {
                materialization: {
                  semantic_payload: {
                    materialization_id: 'mat-123',
                    materialization_pending: false,
                    success: true,
                  },
                },
              },
            };
          }
        }
        
        // Handle previous execution IDs
        if (execIdToUse.startsWith('exec-ingest-') || execIdToUse.startsWith('exec-parse-') || execIdToUse.startsWith('exec-embed-')) {
          return {
            status: 'completed',
            execution_id: execIdToUse,
            artifacts: {},
          };
        }
        
        return { status: 'pending', execution_id: execIdToUse };
      });

      const saveResult = await contentAPIManager.saveMaterialization('boundary-123', 'file-123');
      
      // Log actual result for debugging
      if (!saveResult.success) {
        console.log('❌ saveResult.error:', saveResult.error);
        console.log('❌ saveResult:', JSON.stringify(saveResult, null, 2));
      }
      
      expect(saveResult.success).toBe(true);
      expect(saveResult.materialization_id).toBe('mat-123');
      expect(mockPlatformState.submitIntent).toHaveBeenCalledWith('save_materialization', expect.any(Object));
      expect(mockPlatformState.trackExecution).toHaveBeenCalled();
      
      testResults.step4_save_materialization = 'pass';
      console.log('✅ Step 4 (save_materialization): PASS');
    } catch (error) {
      testResults.step4_save_materialization = 'fail';
      testResults.blockers.push(`Step 4 (save_materialization) failed: ${error instanceof Error ? error.message : String(error)}`);
      console.log('❌ Step 4 (save_materialization): FAIL -', error);
      throw error; // Stop here if save_materialization fails
    }

    // ============================================
    // Step 5: get_semantic_interpretation (Optional)
    // ============================================
    try {
      console.log('🧠 Step 5: Testing get_semantic_interpretation (optional)...');
      
      // Mock successful get_semantic_interpretation execution
      const interpretationExecutionId = `exec-interp-${Date.now()}`;
      (mockPlatformState.submitIntent as jest.Mock).mockResolvedValueOnce(interpretationExecutionId);
      
      executionStatuses[interpretationExecutionId] = { pollCount: 0, maxPolls: 2 };
      
      (mockPlatformState.getExecutionStatus as jest.Mock).mockImplementation(async (execId?: string) => {
        const execIdToUse = execId || interpretationExecutionId;
        if (!executionStatuses[execIdToUse]) {
          executionStatuses[execIdToUse] = { pollCount: 0, maxPolls: 2 };
        }
        
        executionStatuses[execIdToUse].pollCount++;
        const pollCount = executionStatuses[execIdToUse].pollCount;
        
        if (execIdToUse === interpretationExecutionId) {
          if (pollCount < 2) {
            return { status: 'pending', execution_id: interpretationExecutionId };
          } else {
            return {
              status: 'completed',
              execution_id: interpretationExecutionId,
              artifacts: {
                interpretation: {
                  semantic_payload: {
                    interpretation: { summary: 'test interpretation' },
                    entities: ['entity1', 'entity2'],
                    relationships: ['rel1'],
                  },
                },
              },
            };
          }
        }
        
        // Handle previous execution IDs
        if (execIdToUse.startsWith('exec-ingest-') || execIdToUse.startsWith('exec-parse-') || 
            execIdToUse.startsWith('exec-embed-') || execIdToUse.startsWith('exec-save-')) {
          return {
            status: 'completed',
            execution_id: execIdToUse,
            artifacts: {},
          };
        }
        
        return { status: 'pending', execution_id: execIdToUse };
      });

      const interpretationResult = await contentAPIManager.getSemanticInterpretation(
        'file-123',
        'file:test-tenant:test-session:file-123'
      );
      
      expect(interpretationResult.success).toBe(true);
      expect(mockPlatformState.submitIntent).toHaveBeenCalledWith('get_semantic_interpretation', expect.any(Object));
      expect(mockPlatformState.trackExecution).toHaveBeenCalled();
      
      testResults.step5_get_semantic_interpretation = 'pass';
      console.log('✅ Step 5 (get_semantic_interpretation): PASS');
    } catch (error) {
      testResults.step5_get_semantic_interpretation = 'fail';
      // This is optional, so we log but don't fail the test
      console.log('⚠️ Step 5 (get_semantic_interpretation): FAIL (optional, non-gating) -', error);
    }

    // ============================================
    // Final Verification
    // ============================================
    console.log('\n🔍 Final Verification...');
    
    // Verify all intents used intent-based API
    const submitIntentCalls = (mockPlatformState.submitIntent as jest.Mock).mock.calls;
    expect(submitIntentCalls.length).toBeGreaterThanOrEqual(4); // At least 4 core intents
    
    const intentNames = submitIntentCalls.map(call => call[0]);
    expect(intentNames).toContain('ingest_file');
    expect(intentNames).toContain('parse_content');
    expect(intentNames).toContain('extract_embeddings');
    expect(intentNames).toContain('save_materialization');
    
    // Verify all executions were tracked
    const trackExecutionCalls = (mockPlatformState.trackExecution as jest.Mock).mock.calls;
    expect(trackExecutionCalls.length).toBeGreaterThanOrEqual(4);
    
    console.log('✅ All intents used intent-based API');
    console.log('✅ All executions tracked');
    console.log('\n🎉 Journey 1 Happy Path: COMPLETE');
  });
});
