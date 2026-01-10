/**
 * Optimized Insights Panel Component
 * 
 * Main container component for the insights panel with optimized performance
 * and better separation of concerns.
 */

import React, { useState, useCallback, useMemo } from 'react';
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useAGUIEvent } from "@/shared/agui/AGUIEventProvider";
import { withErrorBoundary } from '@/shared/components/ErrorBoundary';
import { useErrorHandler } from '@/shared/hooks/useErrorHandler';

// Import optimized sub-components
import { InsightsDataGrid } from './InsightsDataGrid';

// Import types
import type { 
  InsightsPanelOutput, 
  AGUIResponse, 
  ProcessedResponses 
} from './types';

// Import utilities
import { processAGUIResponsesStacked } from './utils';

// ============================================
// Component Interface
// ============================================

interface InsightsPanelProps {
  onClose?: () => void;
  className?: string;
}

// ============================================
// Main Component
// ============================================

function InsightsPanelComponent({ onClose, className = '' }: InsightsPanelProps) {
  // ============================================
  // State Management
  // ============================================

  const [activeTab, setActiveTab] = useState<string>('summary');
  const [isLoading, setIsLoading] = useState(false);

  // ============================================
  // Error Handling
  // ============================================

  const { errorState, handleError, clearError } = useErrorHandler({
    maxRetries: 3,
    autoRetry: true,
  });

  // ============================================
  // AGUI Event Handling
  // ============================================

  const { sendEvent } = useAGUIEvent();

  const sendAgentEvent = useCallback(async (event: any) => {
    try {
      setIsLoading(true);
      clearError();
      await sendEvent(event);
    } catch (error) {
      handleError(error instanceof Error ? error : new Error('Failed to send agent event'));
    } finally {
      setIsLoading(false);
    }
  }, [sendEvent, handleError, clearError]);

  // ============================================
  // Tab Management
  // ============================================

  const handleTabChange = useCallback((value: string) => {
    setActiveTab(value);
  }, []);

  // ============================================
  // Memoized Values
  // ============================================

  const tabConfig = useMemo(() => [
    { value: 'summary', label: 'Summary', icon: '📊' },
    { value: 'data', label: 'Data Grid', icon: '📋' },
    { value: 'visualizations', label: 'Charts', icon: '📈' },
    { value: 'alerts', label: 'Alerts', icon: '⚠️' },
    { value: 'messages', label: 'Messages', icon: '💬' },
    { value: 'errors', label: 'Errors', icon: '❌' },
  ], []);

  // ============================================
  // Render Methods
  // ============================================

  const renderTabContent = useCallback((tabValue: string) => {
    switch (tabValue) {
      case 'summary':
        return <div>Summary placeholder</div>;
      case 'data':
        return <InsightsDataGrid />;
      case 'visualizations':
        return <div>Visualizations placeholder</div>;
      case 'alerts':
        return <div>Alerts placeholder</div>;
      case 'messages':
        return <div>Messages placeholder</div>;
      case 'errors':
        return <div>Error messages placeholder</div>;
      default:
        return <div>Summary placeholder</div>;
    }
  }, []);

  // ============================================
  // Main Render
  // ============================================

  if (errorState.hasError) {
    return (
      <div className={`insights-panel-error ${className}`}>
        <div className="text-center p-8">
          <h3 className="text-lg font-semibold text-red-600 mb-2">
            Insights Panel Error
          </h3>
          <p className="text-gray-600 mb-4">
            {errorState.error?.message || 'An error occurred while loading insights'}
          </p>
          <Button onClick={clearError} variant="outline">
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className={`insights-panel ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <h2 className="text-xl font-semibold">Insights Panel</h2>
        {onClose && (
          <Button 
            onClick={onClose} 
            variant="ghost" 
            size="sm"
            disabled={isLoading}
          >
            ✕
          </Button>
        )}
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center p-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600">Processing insights...</span>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        <Tabs value={activeTab} onValueChange={handleTabChange} className="h-full">
          <div className="border-b px-4">
            <TabsList className="grid w-full grid-cols-6">
              {tabConfig.map((tab) => (
                <TabsTrigger 
                  key={tab.value} 
                  value={tab.value}
                  className="flex items-center space-x-1"
                >
                  <span>{tab.icon}</span>
                  <span className="hidden sm:inline">{tab.label}</span>
                </TabsTrigger>
              ))}
            </TabsList>
          </div>

          <div className="flex-1 overflow-auto">
            {tabConfig.map((tab) => (
              <TabsContent 
                key={tab.value} 
                value={tab.value}
                className="h-full p-4"
              >
                {renderTabContent(tab.value)}
              </TabsContent>
            ))}
          </div>
        </Tabs>
      </div>
    </div>
  );
}

// ============================================
// Export with Error Boundary
// ============================================

export const InsightsPanel = React.memo(
  withErrorBoundary(InsightsPanelComponent, {
    fallback: ({ error, retry }: any) => (
      <div className="insights-panel-error p-8 text-center">
        <h3 className="text-lg font-semibold text-red-600 mb-2">
          Insights Panel Error
        </h3>
        <p className="text-gray-600 mb-4">
          {error.message}
        </p>
        <Button onClick={retry} variant="outline">
          Try Again
        </Button>
      </div>
    ),
  })
);

InsightsPanel.displayName = 'InsightsPanel'; 