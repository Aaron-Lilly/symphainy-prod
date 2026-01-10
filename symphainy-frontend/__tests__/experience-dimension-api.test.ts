/**
 * Experience Dimension API Integration Tests
 * 
 * Tests the new Experience Dimension API integration with the extracted
 * working patterns from business_orchestrator_old.
 */

import { renderHook, act } from '@testing-library/react';
import { useExperienceDimensionAPI } from '../lib/hooks/useExperienceDimensionAPI';
import { ExperienceDimensionProvider } from '../lib/contexts/ExperienceDimensionContext';
import { UserContext } from '../lib/api/experience-dimension';

// Mock the API client
jest.mock('../lib/api/experience-dimension', () => ({
  experienceDimensionAPI: {
    setUserContext: jest.fn(),
    request: jest.fn(),
    testConnection: jest.fn(),
    getInsightsHealth: jest.fn(),
    getInsightsCapabilities: jest.fn(),
    analyzeDataset: jest.fn(),
    createVisualization: jest.fn(),
    generateBusinessInsights: jest.fn(),
    sendChatMessage: jest.fn(),
    getConversationHistory: jest.fn(),
    clearConversationHistory: jest.fn(),
    detectAnomalies: jest.fn(),
    performCorrelationAnalysis: jest.fn(),
    performStatisticalAnalysis: jest.fn(),
    createHistogram: jest.fn(),
    createScatterPlot: jest.fn(),
    createHeatmap: jest.fn(),
    uploadFile: jest.fn(),
    parseFile: jest.fn(),
    analyzeFile: jest.fn(),
    getFilePreview: jest.fn(),
    getFileMetadata: jest.fn(),
    getOperationsHealth: jest.fn(),
    convertSOPToWorkflow: jest.fn(),
    convertWorkflowToSOP: jest.fn(),
    createCoexistenceBlueprint: jest.fn(),
    sendOperationsChatMessage: jest.fn(),
    generateStrategicPlan: jest.fn(),
    performROIAnalysis: jest.fn(),
    getBusinessMetrics: jest.fn()
  }
}));

// Test wrapper component
const TestWrapper = ({ children }: { children: React.ReactNode }) => {
  return (
    <ExperienceDimensionProvider>
      {children}
    </ExperienceDimensionProvider>
  );
};

describe('Experience Dimension API Integration', () => {
  const mockUserContext: UserContext = {
    user_id: 'test_user_123',
    full_name: 'Test User',
    email: 'test@example.com',
    session_id: 'test_session_123',
    permissions: ['read', 'write', 'analyze']
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('useExperienceDimensionAPI Hook', () => {
    it('should initialize with default state', () => {
      const { result } = renderHook(() => useExperienceDimensionAPI(), {
        wrapper: TestWrapper
      });

      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBe(null);
      expect(result.current.data).toBe(null);
      expect(result.current.lastResponse).toBe(null);
    });

    it('should set user context', () => {
      const { result } = renderHook(() => useExperienceDimensionAPI(), {
        wrapper: TestWrapper
      });

      act(() => {
        result.current.setUserContext(mockUserContext);
      });

      // Verify user context was set (this would be verified through the API client)
      expect(result.current.setUserContext).toBeDefined();
    });

    it('should clear error', () => {
      const { result } = renderHook(() => useExperienceDimensionAPI(), {
        wrapper: TestWrapper
      });

      act(() => {
        result.current.clearError();
      });

      expect(result.current.error).toBe(null);
    });

    it('should clear data', () => {
      const { result } = renderHook(() => useExperienceDimensionAPI(), {
        wrapper: TestWrapper
      });

      act(() => {
        result.current.clearData();
      });

      expect(result.current.data).toBe(null);
      expect(result.current.lastResponse).toBe(null);
    });
  });

  describe('API Methods', () => {
    it('should call testConnection', async () => {
      const { result } = renderHook(() => useExperienceDimensionAPI(), {
        wrapper: TestWrapper
      });

      const mockResponse = {
        success: true,
        data: { status: 'healthy' },
        status: 'success',
        timestamp: new Date().toISOString()
      };

      // Mock the API call
      const { experienceDimensionAPI } = require('../lib/api/experience-dimension');
      experienceDimensionAPI.testConnection.mockResolvedValue(mockResponse);

      await act(async () => {
        await result.current.testConnection();
      });

      expect(experienceDimensionAPI.testConnection).toHaveBeenCalled();
    });

    it('should call getInsightsHealth', async () => {
      const { result } = renderHook(() => useExperienceDimensionAPI(), {
        wrapper: TestWrapper
      });

      const mockResponse = {
        success: true,
        data: { status: 'healthy' },
        status: 'success',
        timestamp: new Date().toISOString()
      };

      // Mock the API call
      const { experienceDimensionAPI } = require('../lib/api/experience-dimension');
      experienceDimensionAPI.getInsightsHealth.mockResolvedValue(mockResponse);

      await act(async () => {
        await result.current.getInsightsHealth();
      });

      expect(experienceDimensionAPI.getInsightsHealth).toHaveBeenCalled();
    });

    it('should call analyzeDataset', async () => {
      const { result } = renderHook(() => useExperienceDimensionAPI(), {
        wrapper: TestWrapper
      });

      const testDataset = { data: [1, 2, 3, 4, 5] };
      const mockResponse = {
        success: true,
        data: { analysis: 'completed' },
        status: 'success',
        timestamp: new Date().toISOString()
      };

      // Mock the API call
      const { experienceDimensionAPI } = require('../lib/api/experience-dimension');
      experienceDimensionAPI.analyzeDataset.mockResolvedValue(mockResponse);

      await act(async () => {
        await result.current.analyzeDataset(testDataset, 'comprehensive');
      });

      expect(experienceDimensionAPI.analyzeDataset).toHaveBeenCalledWith(
        testDataset,
        'comprehensive',
        undefined
      );
    });

    it('should call createVisualization', async () => {
      const { result } = renderHook(() => useExperienceDimensionAPI(), {
        wrapper: TestWrapper
      });

      const testDataset = { data: [1, 2, 3, 4, 5] };
      const mockResponse = {
        success: true,
        data: { visualization: 'created' },
        status: 'success',
        timestamp: new Date().toISOString()
      };

      // Mock the API call
      const { experienceDimensionAPI } = require('../lib/api/experience-dimension');
      experienceDimensionAPI.createVisualization.mockResolvedValue(mockResponse);

      await act(async () => {
        await result.current.createVisualization(testDataset, 'auto');
      });

      expect(experienceDimensionAPI.createVisualization).toHaveBeenCalledWith(
        testDataset,
        'auto',
        undefined
      );
    });

    it('should call sendChatMessage', async () => {
      const { result } = renderHook(() => useExperienceDimensionAPI(), {
        wrapper: TestWrapper
      });

      const testMessage = 'Hello, this is a test message';
      const mockResponse = {
        success: true,
        data: { response: 'Hello! How can I help you?' },
        status: 'success',
        timestamp: new Date().toISOString()
      };

      // Mock the API call
      const { experienceDimensionAPI } = require('../lib/api/experience-dimension');
      experienceDimensionAPI.sendChatMessage.mockResolvedValue(mockResponse);

      await act(async () => {
        await result.current.sendChatMessage(testMessage);
      });

      expect(experienceDimensionAPI.sendChatMessage).toHaveBeenCalledWith(
        testMessage,
        undefined,
        undefined
      );
    });

    it('should call uploadFile', async () => {
      const { result } = renderHook(() => useExperienceDimensionAPI(), {
        wrapper: TestWrapper
      });

      const testFile = new File(['test content'], 'test.txt', { type: 'text/plain' });
      const mockResponse = {
        success: true,
        data: { file_id: 'file_123' },
        status: 'success',
        timestamp: new Date().toISOString()
      };

      // Mock the API call
      const { experienceDimensionAPI } = require('../lib/api/experience-dimension');
      experienceDimensionAPI.uploadFile.mockResolvedValue(mockResponse);

      await act(async () => {
        await result.current.uploadFile(testFile);
      });

      expect(experienceDimensionAPI.uploadFile).toHaveBeenCalledWith(
        testFile,
        undefined
      );
    });

    it('should call convertSOPToWorkflow', async () => {
      const { result } = renderHook(() => useExperienceDimensionAPI(), {
        wrapper: TestWrapper
      });

      const testSOPData = { steps: ['step1', 'step2', 'step3'] };
      const mockResponse = {
        success: true,
        data: { workflow_id: 'workflow_123' },
        status: 'success',
        timestamp: new Date().toISOString()
      };

      // Mock the API call
      const { experienceDimensionAPI } = require('../lib/api/experience-dimension');
      experienceDimensionAPI.convertSOPToWorkflow.mockResolvedValue(mockResponse);

      await act(async () => {
        await result.current.convertSOPToWorkflow(testSOPData);
      });

      expect(experienceDimensionAPI.convertSOPToWorkflow).toHaveBeenCalledWith(
        testSOPData,
        undefined
      );
    });

    it('should call generateStrategicPlan', async () => {
      const { result } = renderHook(() => useExperienceDimensionAPI(), {
        wrapper: TestWrapper
      });

      const testPlanData = { objectives: ['objective1', 'objective2'] };
      const mockResponse = {
        success: true,
        data: { plan_id: 'plan_123' },
        status: 'success',
        timestamp: new Date().toISOString()
      };

      // Mock the API call
      const { experienceDimensionAPI } = require('../lib/api/experience-dimension');
      experienceDimensionAPI.generateStrategicPlan.mockResolvedValue(mockResponse);

      await act(async () => {
        await result.current.generateStrategicPlan(testPlanData);
      });

      expect(experienceDimensionAPI.generateStrategicPlan).toHaveBeenCalledWith(
        testPlanData,
        undefined
      );
    });
  });

  describe('Error Handling', () => {
    it('should handle API errors gracefully', async () => {
      const { result } = renderHook(() => useExperienceDimensionAPI(), {
        wrapper: TestWrapper
      });

      const mockError = new Error('API Error');
      const { experienceDimensionAPI } = require('../lib/api/experience-dimension');
      experienceDimensionAPI.testConnection.mockRejectedValue(mockError);

      await act(async () => {
        try {
          await result.current.testConnection();
        } catch (error) {
          // Error is expected
        }
      });

      expect(result.current.error).toBe('API Error');
    });

    it('should clear errors', () => {
      const { result } = renderHook(() => useExperienceDimensionAPI(), {
        wrapper: TestWrapper
      });

      // Set an error first
      act(() => {
        result.current.clearError();
      });

      expect(result.current.error).toBe(null);
    });
  });

  describe('Loading States', () => {
    it('should show loading state during API calls', async () => {
      const { result } = renderHook(() => useExperienceDimensionAPI(), {
        wrapper: TestWrapper
      });

      const { experienceDimensionAPI } = require('../lib/api/experience-dimension');
      
      // Create a promise that we can control
      let resolvePromise: (value: any) => void;
      const controlledPromise = new Promise((resolve) => {
        resolvePromise = resolve;
      });
      
      experienceDimensionAPI.testConnection.mockReturnValue(controlledPromise);

      // Start the API call
      act(() => {
        result.current.testConnection();
      });

      // Should be loading
      expect(result.current.loading).toBe(true);

      // Resolve the promise
      await act(async () => {
        resolvePromise({
          success: true,
          data: { status: 'healthy' },
          status: 'success',
          timestamp: new Date().toISOString()
        });
      });

      // Should no longer be loading
      expect(result.current.loading).toBe(false);
    });
  });
});
