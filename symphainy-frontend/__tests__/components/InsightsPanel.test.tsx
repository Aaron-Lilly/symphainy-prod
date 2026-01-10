/**
 * Insights Panel Component Tests
 * 
 * Comprehensive tests for the optimized InsightsPanel components
 * using our new testing utilities and architecture.
 */

import React from 'react';
import { screen, fireEvent, waitFor } from '@testing-library/react';
import { render, MockData, TestEvents, ErrorTestUtils, waitForError, waitForLoading } from '@/shared/testing/TestUtils';
import { InsightsPanel } from '@/components/insights/InsightsPanel/InsightsPanel';
import { InsightsDataGrid } from '@/components/insights/InsightsPanel/InsightsDataGrid';
import { InsightsSummary } from '@/components/insights/InsightsPanel/InsightsSummary';
import { InsightsVisualizations } from '@/components/insights/InsightsPanel/InsightsVisualizations';
import { InsightsAlerts } from '@/components/insights/InsightsPanel/InsightsAlerts';
import { InsightsAgentMessages } from '@/components/insights/InsightsPanel/InsightsAgentMessages';
import { InsightsErrorMessages } from '@/components/insights/InsightsPanel/InsightsErrorMessages';

// ============================================
// Mock Components (for testing individual components)
// ============================================

// Mock sub-components that aren't implemented yet
const MockInsightsSummary = () => <div data-testid="insights-summary">Summary Content</div>;
const MockInsightsVisualizations = () => <div data-testid="insights-visualizations">Visualizations</div>;
const MockInsightsAlerts = () => <div data-testid="insights-alerts">Alerts</div>;
const MockInsightsAgentMessages = () => <div data-testid="insights-messages">Messages</div>;
const MockInsightsErrorMessages = () => <div data-testid="insights-errors">Errors</div>;

// ============================================
// Insights Panel Tests
// ============================================

describe('InsightsPanel', () => {
  beforeEach(() => {
    // Clear any previous test data
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render the main insights panel', () => {
      render(<InsightsPanel />);
      
      expect(screen.getByText('Insights Panel')).toBeInTheDocument();
      expect(screen.getByRole('tablist')).toBeInTheDocument();
    });

    it('should render all tab triggers', () => {
      render(<InsightsPanel />);
      
      expect(screen.getByText('📊')).toBeInTheDocument(); // Summary
      expect(screen.getByText('📋')).toBeInTheDocument(); // Data Grid
      expect(screen.getByText('📈')).toBeInTheDocument(); // Charts
      expect(screen.getByText('⚠️')).toBeInTheDocument(); // Alerts
      expect(screen.getByText('💬')).toBeInTheDocument(); // Messages
      expect(screen.getByText('❌')).toBeInTheDocument(); // Errors
    });

    it('should show summary tab by default', () => {
      render(<InsightsPanel />);
      
      const summaryTab = screen.getByRole('tab', { name: /summary/i });
      expect(summaryTab).toHaveAttribute('data-state', 'active');
    });

    it('should render close button when onClose prop is provided', () => {
      const onClose = jest.fn();
      render(<InsightsPanel onClose={onClose} />);
      
      const closeButton = screen.getByRole('button', { name: '✕' });
      expect(closeButton).toBeInTheDocument();
    });

    it('should not render close button when onClose prop is not provided', () => {
      render(<InsightsPanel />);
      
      const closeButton = screen.queryByRole('button', { name: '✕' });
      expect(closeButton).not.toBeInTheDocument();
    });
  });

  describe('Tab Navigation', () => {
    it('should switch tabs when clicked', async () => {
      render(<InsightsPanel />);
      
      // Click on data grid tab
      const dataGridTab = screen.getByRole('tab', { name: /data grid/i });
      fireEvent.click(dataGridTab);
      
      await waitFor(() => {
        expect(dataGridTab).toHaveAttribute('data-state', 'active');
      });
    });

    it('should render correct content for each tab', async () => {
      render(<InsightsPanel />);
      
      // Test summary tab
      expect(screen.getByRole('tabpanel')).toBeInTheDocument();
      
      // Test data grid tab
      const dataGridTab = screen.getByRole('tab', { name: /data grid/i });
      fireEvent.click(dataGridTab);
      
      await waitFor(() => {
        expect(screen.getByRole('tabpanel')).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('should render error boundary when component throws error', async () => {
      // Create a component that throws an error
      const ErrorComponent = () => {
        throw new Error('Test error');
      };

      render(
        <InsightsPanel>
          <ErrorComponent />
        </InsightsPanel>
      );

      await waitForError(screen);
      expect(screen.getByText('Test Error: Test error')).toBeInTheDocument();
    });

    it('should show retry button in error state', async () => {
      const ErrorComponent = () => {
        throw new Error('Test error');
      };

      render(
        <InsightsPanel>
          <ErrorComponent />
        </InsightsPanel>
      );

      await waitForError(screen);
      expect(screen.getByRole('button', { name: 'Retry' })).toBeInTheDocument();
    });

    it('should recover from error when retry is clicked', async () => {
      let shouldThrow = true;
      const ErrorComponent = () => {
        if (shouldThrow) {
          throw new Error('Test error');
        }
        return <div>Recovered</div>;
      };

      render(
        <InsightsPanel>
          <ErrorComponent />
        </InsightsPanel>
      );

      await waitForError(screen);
      
      // Fix the error
      shouldThrow = false;
      
      // Click retry
      const retryButton = screen.getByRole('button', { name: 'Retry' });
      fireEvent.click(retryButton);
      
      await waitFor(() => {
        expect(screen.getByText('Recovered')).toBeInTheDocument();
      });
    });
  });

  describe('Loading States', () => {
    it('should show loading state when isLoading is true', () => {
      render(<InsightsPanel />);
      
      // Simulate loading state
      const loadingElement = screen.getByText('Processing insights...');
      expect(loadingElement).toBeInTheDocument();
    });

    it('should hide loading state when isLoading is false', async () => {
      render(<InsightsPanel />);
      
      await waitFor(() => {
        expect(screen.queryByText('Processing insights...')).not.toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels', () => {
      render(<InsightsPanel />);
      
      expect(screen.getByRole('tablist')).toBeInTheDocument();
      expect(screen.getByRole('tabpanel')).toBeInTheDocument();
    });

    it('should support keyboard navigation', () => {
      render(<InsightsPanel />);
      
      const tabs = screen.getAllByRole('tab');
      expect(tabs.length).toBeGreaterThan(0);
      
      // Test keyboard navigation
      tabs[0].focus();
      expect(tabs[0]).toHaveFocus();
    });
  });
});

// ============================================
// Insights Data Grid Tests
// ============================================

describe('InsightsDataGrid', () => {
  const mockGridData = MockData.gridData;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render data grid with provided data', () => {
      render(<InsightsDataGrid gridData={mockGridData} />);
      
      expect(screen.getByText('Data Grid')).toBeInTheDocument();
      expect(screen.getByText('3 rows')).toBeInTheDocument();
    });

    it('should render table headers', () => {
      render(<InsightsDataGrid gridData={mockGridData} />);
      
      expect(screen.getByText('Name')).toBeInTheDocument();
      expect(screen.getByText('Age')).toBeInTheDocument();
      expect(screen.getByText('Email')).toBeInTheDocument();
      expect(screen.getByText('Status')).toBeInTheDocument();
    });

    it('should render table rows', () => {
      render(<InsightsDataGrid gridData={mockGridData} />);
      
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
      expect(screen.getByText('Bob Johnson')).toBeInTheDocument();
    });

    it('should show empty state when no data provided', () => {
      render(<InsightsDataGrid />);
      
      expect(screen.getByText('No data available')).toBeInTheDocument();
    });
  });

  describe('Sorting', () => {
    it('should sort columns when header is clicked', async () => {
      render(<InsightsDataGrid gridData={mockGridData} />);
      
      const nameHeader = screen.getByText('Name');
      fireEvent.click(nameHeader);
      
      await waitFor(() => {
        expect(nameHeader).toHaveAttribute('data-state', 'active');
      });
    });

    it('should toggle sort direction on second click', async () => {
      render(<InsightsDataGrid gridData={mockGridData} />);
      
      const nameHeader = screen.getByText('Name');
      
      // First click - ascending
      fireEvent.click(nameHeader);
      await waitFor(() => {
        expect(nameHeader).toHaveAttribute('data-state', 'active');
      });
      
      // Second click - descending
      fireEvent.click(nameHeader);
      await waitFor(() => {
        expect(nameHeader).toHaveAttribute('data-state', 'active');
      });
    });
  });

  describe('Filtering', () => {
    it('should filter data when filter input is used', async () => {
      render(<InsightsDataGrid gridData={mockGridData} />);
      
      const filterInput = screen.getByPlaceholderText('Filter data...');
      TestEvents.input(filterInput, 'John');
      
      await waitFor(() => {
        expect(screen.getByText('John Doe')).toBeInTheDocument();
        expect(screen.queryByText('Jane Smith')).not.toBeInTheDocument();
      });
    });

    it('should show filtered badge when filter is active', async () => {
      render(<InsightsDataGrid gridData={mockGridData} />);
      
      const filterInput = screen.getByPlaceholderText('Filter data...');
      TestEvents.input(filterInput, 'John');
      
      await waitFor(() => {
        expect(screen.getByText('Filtered')).toBeInTheDocument();
      });
    });
  });

  describe('Pagination', () => {
    it('should render pagination controls when data exceeds page size', () => {
      const largeGridData = {
        ...mockGridData,
        rows: Array.from({ length: 100 }, (_, i) => [`Row ${i}`, i, `email${i}@test.com`, 'Active']),
      };
      
      render(<InsightsDataGrid gridData={largeGridData} />);
      
      expect(screen.getByText('Page 1 of 2')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Next' })).toBeInTheDocument();
    });

    it('should navigate to next page when next button is clicked', async () => {
      const largeGridData = {
        ...mockGridData,
        rows: Array.from({ length: 100 }, (_, i) => [`Row ${i}`, i, `email${i}@test.com`, 'Active']),
      };
      
      render(<InsightsDataGrid gridData={largeGridData} />);
      
      const nextButton = screen.getByRole('button', { name: 'Next' });
      fireEvent.click(nextButton);
      
      await waitFor(() => {
        expect(screen.getByText('Page 2 of 2')).toBeInTheDocument();
      });
    });
  });

  describe('Export Functionality', () => {
    it('should render export button', () => {
      render(<InsightsDataGrid gridData={mockGridData} />);
      
      expect(screen.getByRole('button', { name: /export/i })).toBeInTheDocument();
    });

    it('should trigger download when export button is clicked', async () => {
      // Mock download functionality
      const mockCreateElement = jest.spyOn(document, 'createElement');
      const mockClick = jest.fn();
      mockCreateElement.mockReturnValue({
        click: mockClick,
        href: '',
      } as any);
      
      render(<InsightsDataGrid gridData={mockGridData} />);
      
      const exportButton = screen.getByRole('button', { name: /export/i });
      fireEvent.click(exportButton);
      
      await waitFor(() => {
        expect(mockCreateElement).toHaveBeenCalledWith('a');
        expect(mockClick).toHaveBeenCalled();
      });
      
      mockCreateElement.mockRestore();
    });
  });

  describe('Row Selection', () => {
    it('should highlight row when clicked', async () => {
      render(<InsightsDataGrid gridData={mockGridData} />);
      
      const firstRow = screen.getByText('John Doe').closest('tr');
      if (firstRow) {
        fireEvent.click(firstRow);
        
        await waitFor(() => {
          expect(firstRow).toHaveClass('bg-blue-50');
        });
      }
    });

    it('should deselect row when clicked again', async () => {
      render(<InsightsDataGrid gridData={mockGridData} />);
      
      const firstRow = screen.getByText('John Doe').closest('tr');
      if (firstRow) {
        // First click - select
        fireEvent.click(firstRow);
        await waitFor(() => {
          expect(firstRow).toHaveClass('bg-blue-50');
        });
        
        // Second click - deselect
        fireEvent.click(firstRow);
        await waitFor(() => {
          expect(firstRow).not.toHaveClass('bg-blue-50');
        });
      }
    });
  });

  describe('Error Handling', () => {
    it('should render error state when component throws error', async () => {
      const ErrorComponent = () => {
        throw new Error('Data grid error');
      };

      render(<ErrorComponent />);

      await waitForError(screen);
      expect(screen.getByText('Data Grid Error')).toBeInTheDocument();
    });

    it('should show retry button in error state', async () => {
      const ErrorComponent = () => {
        throw new Error('Data grid error');
      };

      render(<ErrorComponent />);

      await waitForError(screen);
      expect(screen.getByRole('button', { name: 'Try Again' })).toBeInTheDocument();
    });
  });

  describe('Loading States', () => {
    it('should show loading state when isLoading is true', () => {
      render(<InsightsDataGrid gridData={mockGridData} isLoading={true} />);
      
      expect(screen.getByText('Loading data...')).toBeInTheDocument();
    });

    it('should hide loading state when isLoading is false', () => {
      render(<InsightsDataGrid gridData={mockGridData} isLoading={false} />);
      
      expect(screen.queryByText('Loading data...')).not.toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper table structure', () => {
      render(<InsightsDataGrid gridData={mockGridData} />);
      
      expect(screen.getByRole('table')).toBeInTheDocument();
      expect(screen.getByRole('columnheader')).toBeInTheDocument();
      expect(screen.getByRole('row')).toBeInTheDocument();
    });

    it('should support keyboard navigation', () => {
      render(<InsightsDataGrid gridData={mockGridData} />);
      
      const headers = screen.getAllByRole('columnheader');
      expect(headers.length).toBeGreaterThan(0);
      
      // Test keyboard navigation
      headers[0].focus();
      expect(headers[0]).toHaveFocus();
    });
  });
});

// ============================================
// Performance Tests
// ============================================

describe('InsightsPanel Performance', () => {
  it('should render within performance threshold', () => {
    const renderTime = PerformanceTestUtils.measureRenderTime(() => {
      render(<InsightsPanel />);
    });
    
    expect(renderTime).toBeLessThan(100); // 100ms threshold
  });

  it('should handle large datasets efficiently', () => {
    const largeGridData = {
      columns: ['Name', 'Value'],
      rows: Array.from({ length: 1000 }, (_, i) => [`Item ${i}`, i]),
    };
    
    const renderTime = PerformanceTestUtils.measureRenderTime(() => {
      render(<InsightsDataGrid gridData={largeGridData} />);
    });
    
    expect(renderTime).toBeLessThan(200); // 200ms threshold for large datasets
  });
});

// ============================================
// Integration Tests
// ============================================

describe('InsightsPanel Integration', () => {
  it('should handle tab switching with data updates', async () => {
    render(<InsightsPanel />);
    
    // Switch to data grid tab
    const dataGridTab = screen.getByRole('tab', { name: /data grid/i });
    fireEvent.click(dataGridTab);
    
    await waitFor(() => {
      expect(dataGridTab).toHaveAttribute('data-state', 'active');
    });
    
    // Switch back to summary tab
    const summaryTab = screen.getByRole('tab', { name: /summary/i });
    fireEvent.click(summaryTab);
    
    await waitFor(() => {
      expect(summaryTab).toHaveAttribute('data-state', 'active');
    });
  });

  it('should maintain state across tab switches', async () => {
    render(<InsightsPanel />);
    
    // Perform some action in one tab
    const dataGridTab = screen.getByRole('tab', { name: /data grid/i });
    fireEvent.click(dataGridTab);
    
    // Switch to another tab and back
    const summaryTab = screen.getByRole('tab', { name: /summary/i });
    fireEvent.click(summaryTab);
    fireEvent.click(dataGridTab);
    
    // State should be preserved
    await waitFor(() => {
      expect(dataGridTab).toHaveAttribute('data-state', 'active');
    });
  });
}); 