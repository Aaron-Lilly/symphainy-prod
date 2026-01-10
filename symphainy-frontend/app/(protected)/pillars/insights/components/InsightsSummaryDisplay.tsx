/**
 * InsightsSummaryDisplay Component
 * 
 * Reusable 3-way summary display (Text | Table | Charts)
 * Used for both structured and unstructured insights
 */

import React from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent } from '@/components/ui/card';
import { FileText, Table as TableIcon, BarChart3, Loader2 } from 'lucide-react';
import { AnalyzeContentResponse } from '@/lib/api/insights';
import ChartComponent, { ChartConfig, ChartData } from '@/components/ui/chart';

interface InsightsSummaryDisplayProps {
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
      vega_lite_spec?: any; // Legacy support
    }>;
  };
  loading?: boolean;
  defaultTab?: 'text' | 'table' | 'charts';
}

export function InsightsSummaryDisplay({ 
  summary, 
  loading = false,
  defaultTab = 'text'
}: InsightsSummaryDisplayProps) {
  if (loading) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <span className="ml-3 text-gray-600">Analyzing content...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!summary) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center py-12 text-gray-500">
            <FileText className="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <p className="text-base font-medium">No analysis results yet</p>
            <p className="text-sm text-gray-400 mt-2">
              Select a file and click "Analyze Content" to generate insights
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Determine which tabs should be shown
  const hasTabular = summary.tabular && summary.tabular.rows && summary.tabular.rows.length > 0;
  const hasVisualizations = summary.visualizations && summary.visualizations.length > 0;

  return (
    <Card>
      <CardContent className="pt-6">
        <Tabs defaultValue={defaultTab} className="w-full">
          <TabsList className="grid w-full" style={{ gridTemplateColumns: `repeat(${1 + (hasTabular ? 1 : 0) + (hasVisualizations ? 1 : 0)}, minmax(0, 1fr))` }}>
            <TabsTrigger value="text" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Text
            </TabsTrigger>
            {hasTabular && (
              <TabsTrigger value="table" className="flex items-center gap-2">
                <TableIcon className="h-4 w-4" />
                Table
              </TabsTrigger>
            )}
            {hasVisualizations && (
              <TabsTrigger value="charts" className="flex items-center gap-2">
                <BarChart3 className="h-4 w-4" />
                Charts
              </TabsTrigger>
            )}
          </TabsList>

          {/* Textual Summary Tab */}
          <TabsContent value="text" className="space-y-4 mt-4">
            <div className="prose prose-sm max-w-none">
              <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">
                  Business Analysis Summary
                </h3>
                <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                  {summary.textual}
                </p>
              </div>
            </div>
          </TabsContent>

          {/* Tabular Summary Tab */}
          {hasTabular && (
            <TabsContent value="table" className="space-y-4 mt-4">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 border border-gray-200 rounded-lg">
                  <thead className="bg-gray-50">
                    <tr>
                      {summary.tabular!.columns.map((column, idx) => (
                        <th
                          key={idx}
                          className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                        >
                          {column}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {summary.tabular!.rows.map((row, rowIdx) => (
                      <tr key={rowIdx} className="hover:bg-gray-50">
                        {row.map((cell, cellIdx) => (
                          <td key={cellIdx} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {typeof cell === 'object' ? JSON.stringify(cell) : String(cell)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Summary Statistics */}
              {summary.tabular!.summary_stats && (
                <div className="mt-4 bg-blue-50 p-4 rounded-lg border border-blue-200">
                  <h4 className="text-sm font-semibold text-blue-900 mb-2">Summary Statistics</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {Object.entries(summary.tabular!.summary_stats).map(([key, value]) => (
                      <div key={key} className="text-sm">
                        <span className="text-blue-700 font-medium">{key}:</span>{' '}
                        <span className="text-blue-900">
                          {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </TabsContent>
          )}

          {/* Visualizations Tab */}
          {hasVisualizations && (
            <TabsContent value="charts" className="space-y-6 mt-4">
              {summary.visualizations!.map((viz, idx) => {
                // Transform backend visualization spec to Recharts format
                const chartData: ChartData[] = viz.chart_data || [];
                const chartConfig: ChartConfig = {
                  type: viz.chart_type as any, // 'bar', 'line', 'pie', 'area'
                  library: (viz.library || 'recharts') as 'recharts' | 'nivo',
                  title: viz.title || `Visualization ${idx + 1}`,
                  description: viz.rationale,
                  xAxisKey: viz.x_axis_key || 'name',
                  dataKey: viz.data_key || 'value',
                  colors: viz.colors || undefined,
                  height: 350,
                  showLegend: true,
                  showTooltip: true,
                  showGrid: true
                };
                
                return (
                  <div key={viz.visualization_id}>
                    <ChartComponent data={chartData} config={chartConfig} />
                  </div>
                );
              })}
            </TabsContent>
          )}
        </Tabs>
      </CardContent>
    </Card>
  );
}

