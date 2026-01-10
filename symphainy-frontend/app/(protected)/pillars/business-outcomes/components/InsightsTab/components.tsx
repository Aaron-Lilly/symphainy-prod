// InsightsTab UI Components
"use client";
import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { Loader2, TrendingUp, Lightbulb, Target, BarChart3, Table, FileText, Clock, Zap } from "lucide-react";
import ReactMarkdown from "react-markdown";
import dynamic from "next/dynamic";
import { InsightsTabUIProps, VisualizationData, AnalysisHistoryEntry } from "./types";
import { LearningStyleType } from "@/shared/services/insights/types";

// Dynamic import for chart components
const ChartComponent = dynamic(
  () => import("@/components/ui/chart"),
  { ssr: false, loading: () => <div className="flex items-center justify-center h-32"><Loader2 className="animate-spin" /></div> }
);

export function InsightsTabUI({
  summaryText,
  keyInsights,
  recommendations,
  visualizations,
  learningStyle,
  analysisHistory,
  hasData,
  isLoading,
}: InsightsTabUIProps) {
  if (isLoading) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-center py-8">
            <Loader2 className="animate-spin h-8 w-8 mr-3" />
            <span className="text-gray-600">Loading insights data...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!hasData) {
    return (
      <Card>
        <CardContent className="pt-6">
          <EmptyState
            icon={<BarChart3 className="w-12 h-12 text-gray-400" />}
            title="No Insights Data"
            description="Complete the Insights pillar analysis to see strategic findings and recommendations."
          />
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Summary Section */}
      {summaryText && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <FileText className="w-5 h-5 mr-2" />
              Strategic Summary
            </CardTitle>
            <CardDescription>
              Key strategic findings from data analysis
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="prose max-w-none">
              <ReactMarkdown className="text-gray-700 leading-relaxed">
                {summaryText}
              </ReactMarkdown>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Visual/Tabular Section */}
      {visualizations && visualizations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              {learningStyle === LearningStyleType.VISUAL ? (
                <BarChart3 className="w-5 h-5 mr-2" />
              ) : (
                <Table className="w-5 h-5 mr-2" />
              )}
              {learningStyle === LearningStyleType.VISUAL ? 'Visual Insights' : 'Tabular Data'}
            </CardTitle>
            <CardDescription>
              {learningStyle === LearningStyleType.VISUAL 
                ? 'Visual representations of key data insights'
                : 'Structured data analysis results'
              }
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {visualizations.map((viz: VisualizationData, index: number) => (
                <div key={index} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-semibold text-gray-800">{viz.title}</h4>
                    <Badge variant="secondary">{viz.type}</Badge>
                  </div>
                  
                  {viz.description && (
                    <p className="text-sm text-gray-600 mb-3">{viz.description}</p>
                  )}
                  
                  <div className="min-h-[200px] flex items-center justify-center bg-gray-50 rounded-md">
                    {viz.type === 'chart' || viz.type === 'graph' ? (
                      <ChartComponent data={viz.data} config={viz.config} />
                    ) : viz.type === 'table' ? (
                      <div className="w-full overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                          <thead className="bg-gray-50">
                            {viz.data.headers && (
                              <tr>
                                {viz.data.headers.map((header: string, i: number) => (
                                  <th key={i} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    {header}
                                  </th>
                                ))}
                              </tr>
                            )}
                          </thead>
                          <tbody className="bg-white divide-y divide-gray-200">
                            {viz.data.rows && viz.data.rows.map((row: any[], i: number) => (
                              <tr key={i}>
                                {row.map((cell: any, j: number) => (
                                  <td key={j} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                    {cell}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <div className="text-gray-500">Unsupported visualization type: {viz.type}</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Key Insights Section */}
      {keyInsights && keyInsights.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Lightbulb className="w-5 h-5 mr-2" />
              Key Strategic Insights
            </CardTitle>
            <CardDescription>
              Critical findings and discoveries from the analysis
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {keyInsights.map((insight: string, index: number) => (
                <div key={index} className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                  <div className="flex-shrink-0 w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center">
                    <span className="text-white text-xs font-bold">{index + 1}</span>
                  </div>
                  <div className="flex-1">
                    <p className="text-gray-800 font-medium">{insight}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recommendations Section */}
      {recommendations && recommendations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Target className="w-5 h-5 mr-2" />
              Strategic Recommendations
            </CardTitle>
            <CardDescription>
              Actionable recommendations based on insights analysis
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {recommendations.map((recommendation: string, index: number) => (
                <div key={index} className="flex items-start space-x-3 p-3 bg-green-50 rounded-lg">
                  <div className="flex-shrink-0 w-6 h-6 bg-green-600 rounded-full flex items-center justify-center">
                    <Zap className="w-3 h-3 text-white" />
                  </div>
                  <div className="flex-1">
                    <p className="text-gray-800 font-medium">{recommendation}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Analysis History Section */}
      {analysisHistory && analysisHistory.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Clock className="w-5 h-5 mr-2" />
              Analysis History
            </CardTitle>
            <CardDescription>
              Timeline of analysis iterations and queries
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {analysisHistory.map((entry: AnalysisHistoryEntry, index: number) => (
                <div key={entry.id} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                  <div className="flex-shrink-0 w-6 h-6 bg-gray-600 rounded-full flex items-center justify-center">
                    <span className="text-white text-xs font-bold">{index + 1}</span>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <Badge variant="outline" className="text-xs">
                        {entry.type.replace('_', ' ')}
                      </Badge>
                      <span className="text-xs text-gray-500">
                        {entry.timestamp.toLocaleDateString()}
                      </span>
                    </div>
                    {entry.query && (
                      <p className="text-sm text-gray-600 mb-1">
                        <strong>Query:</strong> {entry.query}
                      </p>
                    )}
                    <p className="text-sm text-gray-800">{entry.summary}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Learning Style Indicator */}
      <Card className="border-blue-200 bg-blue-50">
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-semibold text-blue-800">Analysis Style</h4>
              <p className="text-sm text-blue-700">
                This analysis was optimized for {learningStyle === LearningStyleType.VISUAL ? 'visual' : 'tabular'} learning preferences
              </p>
            </div>
            <Badge variant="secondary" className="bg-blue-100 text-blue-800">
              {learningStyle === LearningStyleType.VISUAL ? 'Visual' : 'Tabular'}
            </Badge>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 