/**
 * Experience Dimension Example Component
 * 
 * Demonstrates how to use the new Experience Dimension API integration
 * with the extracted working patterns from business_orchestrator_old.
 */

import React, { useState, useEffect } from 'react';
import { useExperienceDimensionAPI } from '../../lib/hooks/useExperienceDimensionAPI';
import { useExperienceDimensionContext } from '../../lib/contexts/ExperienceDimensionContext';
import { UserContext } from '../../lib/api/experience-dimension';

// Example component props
interface ExperienceDimensionExampleProps {
  className?: string;
}

// Example component
export function ExperienceDimensionExample({ className = '' }: ExperienceDimensionExampleProps) {
  const { setUserContext, isConnected, connectionError } = useExperienceDimensionContext();
  const {
    loading,
    error,
    data,
    getInsightsHealth,
    getInsightsCapabilities,
    analyzeDataset,
    createVisualization,
    sendChatMessage,
    testConnection
  } = useExperienceDimensionAPI();

  const [testResults, setTestResults] = useState<Record<string, any>>({});
  const [isRunningTests, setIsRunningTests] = useState(false);

  // Set up example user context
  useEffect(() => {
    const exampleUserContext: UserContext = {
      user_id: 'example_user_123',
      full_name: 'Example User',
      email: 'example@example.com',
      session_id: 'example_session_123',
      permissions: ['read', 'write', 'analyze', 'visualize']
    };

    setUserContext(exampleUserContext);
  }, [setUserContext]);

  // Run comprehensive tests
  const runTests = async () => {
    setIsRunningTests(true);
    const results: Record<string, any> = {};

    try {
      // Test 1: Connection test
      console.log('🧪 Testing connection...');
      const connectionResult = await testConnection();
      results.connection = {
        success: connectionResult.success,
        error: connectionResult.error,
        timestamp: connectionResult.timestamp
      };

      // Test 2: Insights health check
      console.log('🧪 Testing insights health...');
      const healthResult = await getInsightsHealth();
      results.insightsHealth = {
        success: healthResult.success,
        error: healthResult.error,
        timestamp: healthResult.timestamp
      };

      // Test 3: Insights capabilities
      console.log('🧪 Testing insights capabilities...');
      const capabilitiesResult = await getInsightsCapabilities();
      results.insightsCapabilities = {
        success: capabilitiesResult.success,
        error: capabilitiesResult.error,
        timestamp: capabilitiesResult.timestamp
      };

      // Test 4: Dataset analysis
      console.log('🧪 Testing dataset analysis...');
      const testDataset = {
        data: [1, 2, 3, 4, 5],
        labels: ['A', 'B', 'C', 'D', 'E']
      };
      const analysisResult = await analyzeDataset(testDataset, 'comprehensive');
      results.datasetAnalysis = {
        success: analysisResult.success,
        error: analysisResult.error,
        timestamp: analysisResult.timestamp
      };

      // Test 5: Visualization creation
      console.log('🧪 Testing visualization creation...');
      const visualizationResult = await createVisualization(testDataset, 'auto');
      results.visualization = {
        success: visualizationResult.success,
        error: visualizationResult.error,
        timestamp: visualizationResult.timestamp
      };

      // Test 6: Chat message
      console.log('🧪 Testing chat message...');
      const chatResult = await sendChatMessage('Hello, this is a test message');
      results.chat = {
        success: chatResult.success,
        error: chatResult.error,
        timestamp: chatResult.timestamp
      };

    } catch (error: any) {
      console.error('❌ Test failed:', error);
      results.error = error.message;
    } finally {
      setIsRunningTests(false);
    }

    setTestResults(results);
  };

  return (
    <div className={`p-6 bg-white rounded-lg shadow-lg ${className}`}>
      <h2 className="text-2xl font-bold mb-4">Experience Dimension API Integration</h2>
      
      {/* Connection Status */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-2">Connection Status</h3>
        <div className="flex items-center space-x-2">
          <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
          <span className={isConnected ? 'text-green-600' : 'text-red-600'}>
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
        {connectionError && (
          <p className="text-red-600 text-sm mt-1">Error: {connectionError}</p>
        )}
      </div>

      {/* Test Controls */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-2">API Tests</h3>
        <button
          onClick={runTests}
          disabled={isRunningTests || loading}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isRunningTests ? 'Running Tests...' : 'Run Comprehensive Tests'}
        </button>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="mb-4 p-4 bg-blue-50 rounded">
          <p className="text-blue-600">Loading...</p>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 rounded">
          <p className="text-red-600">Error: {error}</p>
        </div>
      )}

      {/* Test Results */}
      {Object.keys(testResults).length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-2">Test Results</h3>
          <div className="space-y-2">
            {Object.entries(testResults).map(([testName, result]) => (
              <div key={testName} className="p-3 bg-gray-50 rounded">
                <div className="flex items-center justify-between">
                  <span className="font-medium capitalize">{testName.replace(/([A-Z])/g, ' $1')}</span>
                  <div className="flex items-center space-x-2">
                    <div className={`w-2 h-2 rounded-full ${result.success ? 'bg-green-500' : 'bg-red-500'}`}></div>
                    <span className={result.success ? 'text-green-600' : 'text-red-600'}>
                      {result.success ? 'Success' : 'Failed'}
                    </span>
                  </div>
                </div>
                {result.error && (
                  <p className="text-red-600 text-sm mt-1">Error: {result.error}</p>
                )}
                {result.timestamp && (
                  <p className="text-gray-500 text-xs mt-1">
                    {new Date(result.timestamp).toLocaleString()}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Data Display */}
      {data && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-2">Latest Response Data</h3>
          <pre className="bg-gray-100 p-4 rounded text-sm overflow-auto">
            {JSON.stringify(data, null, 2)}
          </pre>
        </div>
      )}

      {/* Instructions */}
      <div className="text-sm text-gray-600">
        <h4 className="font-semibold mb-2">How to Use:</h4>
        <ul className="list-disc list-inside space-y-1">
          <li>This component demonstrates the new Experience Dimension API integration</li>
          <li>It uses the extracted working patterns from business_orchestrator_old</li>
          <li>All requests are routed through the Experience Dimension's Frontend Integration Service</li>
          <li>Click "Run Comprehensive Tests" to test all API endpoints</li>
          <li>The component shows real-time connection status and test results</li>
        </ul>
      </div>
    </div>
  );
}

export default ExperienceDimensionExample;


