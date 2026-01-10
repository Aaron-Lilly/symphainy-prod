/**
 * VARKInsightsPanel Utilities
 * Utility functions for VARKInsightsPanel component
 */

import { FileMetadata } from '@/shared/types/file';
import { LearningStyle, DataDepth } from './types';

export function filterParsedFiles(files: FileMetadata[]): FileMetadata[] {
  return files
    .filter((file) => file.parsed_path && file.status === 'parsed')
    .sort((a, b) => {
      const dateA = new Date(a.created_at).getTime();
      const dateB = new Date(b.created_at).getTime();
      return dateB - dateA;
    });
}

export function getLearningStyleLabel(style: LearningStyle): string {
  switch (style) {
    case 'visual':
      return 'Visual (Charts & Graphs)';
    case 'tabular':
      return 'Read/Write (Tables & Data)';
    default:
      return 'Unknown';
  }
}

export function getLearningStyleIcon(style: LearningStyle): string {
  switch (style) {
    case 'visual':
      return 'BarChart3';
    case 'tabular':
      return 'Table';
    default:
      return 'FileText';
  }
}

export function getDataDepthLabel(depth: DataDepth): string {
  switch (depth) {
    case 'summary':
      return 'Summary';
    case 'detailed':
      return 'Detailed';
    case 'drill-down':
      return 'Drill-Down';
    default:
      return 'Unknown';
  }
}

export function getDataDepthDescription(depth: DataDepth): string {
  switch (depth) {
    case 'summary':
      return 'High-level overview and key insights';
    case 'detailed':
      return 'Comprehensive analysis with patterns and trends';
    case 'drill-down':
      return 'Deep dive into specific data points and correlations';
    default:
      return '';
  }
}

export function validateAnalysisRequest(
  file: FileMetadata | null,
  learningStyle: LearningStyle,
  dataDepth: DataDepth
): { valid: boolean; error?: string } {
  if (!file) {
    return { valid: false, error: 'No file selected' };
  }

  if (!file.parsed_path) {
    return { valid: false, error: 'Selected file has not been parsed' };
  }

  if (!learningStyle) {
    return { valid: false, error: 'No learning style selected' };
  }

  if (!dataDepth) {
    return { valid: false, error: 'No data depth selected' };
  }

  return { valid: true };
}

export function formatAnalysisResults(results: any): any {
  if (!results) return null;

  // Format results based on learning style
  if (results.visual_data) {
    return {
      ...results,
      visual_data: {
        charts: results.visual_data.charts || [],
        graphs: results.visual_data.graphs || [],
        color_scheme: results.visual_data.color_scheme || 'default',
      },
    };
  }

  if (results.tabular_data) {
    return {
      ...results,
      tabular_data: {
        tables: results.tabular_data.tables || [],
        structured_data: results.tabular_data.structured_data || [],
        sort_options: results.tabular_data.sort_options || [],
        filter_options: results.tabular_data.filter_options || [],
      },
    };
  }

  return results;
}

export function generateBusinessSummary(results: any): string {
  if (!results) return 'No analysis results available.';

  const insights = results.insights || [];
  const keyFindings = results.key_findings || [];
  const recommendations = results.recommendations || [];

  let summary = '';

  if (keyFindings.length > 0) {
    summary += `Key Findings: ${keyFindings.slice(0, 3).join(', ')}. `;
  }

  if (insights.length > 0) {
    summary += `Insights: ${insights.slice(0, 2).join(', ')}. `;
  }

  if (recommendations.length > 0) {
    summary += `Recommendations: ${recommendations.slice(0, 2).join(', ')}.`;
  }

  return summary || 'Analysis completed successfully. Review the detailed results below.';
}

export function exportAnalysisResults(results: any, format: 'json' | 'csv' | 'pdf' = 'json'): string {
  switch (format) {
    case 'csv':
      return convertToCSV(results);
    case 'pdf':
      return convertToPDF(results);
    case 'json':
    default:
      return JSON.stringify(results, null, 2);
  }
}

function convertToCSV(results: any): string {
  // Mock CSV conversion - in real implementation, use a CSV library
  return 'CSV export of analysis results';
}

function convertToPDF(results: any): string {
  // Mock PDF conversion - in real implementation, use a PDF library
  return 'PDF export of analysis results';
} 