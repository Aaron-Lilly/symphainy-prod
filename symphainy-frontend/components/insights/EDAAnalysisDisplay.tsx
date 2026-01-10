"use client";

import React, { useRef, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  ArrowLeft,
  Copy,
  Download,
  BarChart3,
  PieChart,
  TrendingUp,
  Database,
  FileText,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface EDAAnalysisData {
  data_summary?: Record<string, any>;
  column_analysis?: Record<string, any>;
  correlations?: Record<string, any>;
  distributions?: Record<string, any>;
  missing_values?: Record<string, any>;
  outliers?: Record<string, any>;
  insights?: string[];
  recommendations?: string[];
}

interface EDAAnalysisDisplayProps {
  // Always updatable props (required)
  data: EDAAnalysisData;
  
  // Sticky props (optional - will use stored values from first render if not provided)
  title?: string;
  description?: string;
  onBack?: () => void;
  loading?: boolean;
}

// Internal interface for stored default values
interface StoredDefaults {
  title?: string;
  description?: string;
  onBack?: () => void;
  loading?: boolean;
}

export default function EDAAnalysisDisplay({
  title: propTitle,
  description: propDescription,
  onBack: propOnBack,
  loading: propLoading,
  data,
}: EDAAnalysisDisplayProps) {
  // Store the initial props values on first render
  const storedDefaults = useRef<StoredDefaults>({});
  
  useEffect(() => {
    // Only capture props on first render (when stored defaults are empty)
    if (Object.keys(storedDefaults.current).length === 0) {
      storedDefaults.current = {
        title: propTitle,
        description: propDescription,
        onBack: propOnBack,
        loading: propLoading,
      };
    }
  }, []); // Empty dependency array - only runs on mount

  // Use provided props or fall back to stored defaults
  const title = propTitle ?? storedDefaults.current.title ?? "EDA Analysis Results";
  const description = propDescription ?? storedDefaults.current.description ?? "Exploratory Data Analysis of your dataset";
  const onBack = propOnBack ?? storedDefaults.current.onBack;
  const loading = propLoading ?? storedDefaults.current.loading ?? false;

  const copyToClipboard = () => {
    navigator.clipboard.writeText(JSON.stringify(data, null, 2));
  };

  const downloadJSON = () => {
    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `eda_analysis_results.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Loading EDA analysis results...</span>
      </div>
    );
  }

  return (
    <div className="w-full max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
          <p className="text-gray-600 mt-1">{description}</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={copyToClipboard}>
            <Copy className="h-4 w-4 mr-2" />
            Copy
          </Button>
          <Button variant="outline" size="sm" onClick={downloadJSON}>
            <Download className="h-4 w-4 mr-2" />
            Download
          </Button>
          {onBack && (
            <Button variant="outline" size="sm" onClick={onBack}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
          )}
        </div>
      </div>

      {/* Results Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Data Summary */}
        {data.data_summary && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5 text-blue-500" />
                Data Summary
              </CardTitle>
              <CardDescription>
                Overview of your dataset structure and basic statistics
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {Object.entries(data.data_summary).map(([key, value]) => (
                  <div key={key} className="flex justify-between items-center py-1">
                    <span className="text-sm font-medium capitalize">
                      {key.replace(/_/g, ' ')}:
                    </span>
                    <span className="text-sm text-gray-600">
                      {typeof value === 'number' ? value.toLocaleString() : String(value)}
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Missing Values */}
        {data.missing_values && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5 text-orange-500" />
                Missing Values
              </CardTitle>
              <CardDescription>
                Analysis of missing data in your dataset
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {Object.entries(data.missing_values).map(([column, count]) => (
                  <div key={column} className="flex justify-between items-center py-1">
                    <span className="text-sm font-medium">{column}:</span>
                    <Badge variant={Number(count) > 0 ? "destructive" : "secondary"}>
                      {String(count)}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Column Analysis */}
        {data.column_analysis && (
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <PieChart className="h-5 w-5 text-green-500" />
                Column Analysis
              </CardTitle>
              <CardDescription>
                Detailed analysis of each column in your dataset
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(data.column_analysis).map(([column, analysis]) => (
                  <div key={column} className="p-4 border rounded-lg bg-gray-50">
                    <h4 className="font-medium mb-2">{column}</h4>
                    <pre className="text-xs text-gray-600 overflow-auto">
                      {JSON.stringify(analysis, null, 2)}
                    </pre>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Correlations */}
        {data.correlations && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-purple-500" />
                Correlations
              </CardTitle>
              <CardDescription>
                Correlation analysis between variables
              </CardDescription>
            </CardHeader>
            <CardContent>
              <pre className="text-xs bg-white p-3 rounded border overflow-auto max-h-40">
                {JSON.stringify(data.correlations, null, 2)}
              </pre>
            </CardContent>
          </Card>
        )}

        {/* Outliers */}
        {data.outliers && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5 text-red-500" />
                Outliers
              </CardTitle>
              <CardDescription>
                Outlier detection results
              </CardDescription>
            </CardHeader>
            <CardContent>
              <pre className="text-xs bg-white p-3 rounded border overflow-auto max-h-40">
                {JSON.stringify(data.outliers, null, 2)}
              </pre>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Insights */}
      {data.insights && data.insights.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-blue-500" />
              Key Insights
            </CardTitle>
            <CardDescription>
              Important findings from the exploratory data analysis
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {data.insights.map((insight, index) => (
                <div key={index} className="flex gap-3">
                  <div className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-medium">
                    {index + 1}
                  </div>
                  <p className="text-sm text-gray-700 leading-relaxed">
                    {insight}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recommendations */}
      {data.recommendations && data.recommendations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-green-500" />
              Recommendations
            </CardTitle>
            <CardDescription>
              Suggested next steps based on the EDA results
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {data.recommendations.map((recommendation, index) => (
                <div key={index} className="flex gap-3">
                  <div className="flex-shrink-0 w-6 h-6 bg-green-100 text-green-600 rounded-full flex items-center justify-center text-sm font-medium">
                    {index + 1}
                  </div>
                  <p className="text-sm text-gray-700 leading-relaxed">
                    {recommendation}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Raw Data */}
      <Card>
        <CardHeader>
          <CardTitle>Raw Results</CardTitle>
          <CardDescription>
            Complete EDA analysis output data
          </CardDescription>
        </CardHeader>
        <CardContent>
          <pre className="text-xs bg-gray-50 p-4 rounded-lg overflow-auto max-h-64">
            {JSON.stringify(data, null, 2)}
          </pre>
        </CardContent>
      </Card>
    </div>
  );
} 