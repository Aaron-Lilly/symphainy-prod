"use client";

import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Download, Share2, RefreshCw, BarChart3, TrendingUp, AlertTriangle } from "lucide-react";
import { InsightsAnalysisResponse } from "@/shared/types/responses";

interface InsightsSummaryDisplayProps {
  summary: InsightsAnalysisResponse;
  onRefresh?: () => void;
  onExport?: () => void;
  onShare?: () => void;
}

export default function InsightsSummaryDisplay({
  summary,
  onRefresh,
  onExport,
  onShare,
}: InsightsSummaryDisplayProps) {
  const formatSummaryText = (text: string) => {
    // Split by sections and format
    const sections = text.split(/\*\*(.*?)\*\*/g);
    return sections.map((section, index) => {
      if (index % 2 === 1) {
        // This is a header (bold text)
        return <h3 key={index} className="text-lg font-semibold mt-4 mb-2 text-gray-800">{section}</h3>;
      } else {
        // This is content
        return <p key={index} className="text-gray-700 leading-relaxed mb-3">{section}</p>;
      }
    });
  };

  return (
    <div className="space-y-6">
      {/* Summary Text Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Executive Summary</span>
            <div className="flex gap-2">
              {onRefresh && (
                <Button variant="outline" size="sm" onClick={onRefresh}>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Refresh
                </Button>
              )}
              {onExport && (
                <Button variant="outline" size="sm" onClick={onExport}>
                  <Download className="h-4 w-4 mr-2" />
                  Export
                </Button>
              )}
              {onShare && (
                <Button variant="outline" size="sm" onClick={onShare}>
                  <Share2 className="h-4 w-4 mr-2" />
                  Share
                </Button>
              )}
            </div>
          </CardTitle>
          <CardDescription>
            Comprehensive analysis summary generated on {new Date(summary.timestamp).toLocaleString()}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="prose max-w-none">
            {formatSummaryText(
              (summary.data as { summary_text?: string } | undefined)?.summary_text || 
              summary.message || 
              "No summary available"
            )}
          </div>
        </CardContent>
      </Card>

      {/* Visualization Section */}
      <Card>
        <CardHeader>
          <CardTitle>Insights Dashboard</CardTitle>
          <CardDescription>
            Key metrics and findings visualization
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Data Quality Score */}
            <div className="text-center p-6 bg-blue-50 rounded-lg border">
              <div className="text-3xl font-bold text-blue-600 mb-2">85%</div>
              <div className="text-sm text-gray-600 mb-2">Data Quality</div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-blue-600 h-2 rounded-full" style={{ width: '85%' }}></div>
              </div>
            </div>

            {/* Anomalies Detected */}
            <div className="text-center p-6 bg-orange-50 rounded-lg border">
              <div className="text-3xl font-bold text-orange-600 mb-2">26</div>
              <div className="text-sm text-gray-600 mb-2">Anomalies</div>
              <AlertTriangle className="h-6 w-6 mx-auto text-orange-500" />
            </div>

            {/* Performance Trend */}
            <div className="text-center p-6 bg-green-50 rounded-lg border">
              <div className="text-3xl font-bold text-green-600 mb-2">+15%</div>
              <div className="text-sm text-gray-600 mb-2">Performance</div>
              <TrendingUp className="h-6 w-6 mx-auto text-green-500" />
            </div>

            {/* Critical Insights */}
            <div className="text-center p-6 bg-purple-50 rounded-lg border">
              <div className="text-3xl font-bold text-purple-600 mb-2">5</div>
              <div className="text-sm text-gray-600 mb-2">Key Insights</div>
              <BarChart3 className="h-6 w-6 mx-auto text-purple-500" />
            </div>
          </div>

          {/* Simple Chart Representation */}
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <h4 className="font-semibold mb-3">Anomaly Distribution</h4>
            <div className="flex items-end space-x-2 h-32">
              <div className="flex-1 bg-green-500 rounded-t" style={{ height: '60%' }}>
                <div className="text-center text-white text-xs mt-1">Low</div>
              </div>
              <div className="flex-1 bg-orange-500 rounded-t" style={{ height: '40%' }}>
                <div className="text-center text-white text-xs mt-1">Medium</div>
              </div>
              <div className="flex-1 bg-red-500 rounded-t" style={{ height: '20%' }}>
                <div className="text-center text-white text-xs mt-1">High</div>
              </div>
            </div>
            <div className="flex justify-between text-xs text-gray-600 mt-2">
              <span>15</span>
              <span>8</span>
              <span>3</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Key Metrics Section */}
      <Card>
        <CardHeader>
          <CardTitle>Key Metrics</CardTitle>
          <CardDescription>
            Quick reference of critical insights
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">85%</div>
              <div className="text-sm text-gray-600">Data Quality Score</div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">26</div>
              <div className="text-sm text-gray-600">Anomalies Detected</div>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">5</div>
              <div className="text-sm text-gray-600">Critical Insights</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 