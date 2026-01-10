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
  AlertTriangle,
  CheckCircle,
  TrendingDown,
  FileText,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface AnomalyDetectionData {
  anomalies_detected?: any[];
  anomaly_scores?: number[];
  statistical_summary?: Record<string, any>;
  recommendations?: string[];
  confidence_level?: number;
}

interface AnomalyDetectionDisplayProps {
  // Always updatable props (required)
  data: AnomalyDetectionData;
  
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

export default function AnomalyDetectionDisplay({
  title: propTitle,
  description: propDescription,
  onBack: propOnBack,
  loading: propLoading,
  data,
}: AnomalyDetectionDisplayProps) {
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
  const title = propTitle ?? storedDefaults.current.title ?? "Anomaly Detection Results";
  const description = propDescription ?? storedDefaults.current.description ?? "Analysis of anomalies in your data";
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
    a.download = `anomaly_detection_results.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Loading anomaly detection results...</span>
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
        {/* Anomalies Summary */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-orange-500" />
              Anomalies Detected
            </CardTitle>
            <CardDescription>
              Overview of detected anomalies in your dataset
            </CardDescription>
          </CardHeader>
          <CardContent>
            {data.anomalies_detected && data.anomalies_detected.length > 0 ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Total Anomalies:</span>
                  <Badge variant="destructive">{data.anomalies_detected.length}</Badge>
                </div>
                {data.confidence_level && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Confidence Level:</span>
                    <Badge variant="outline">{(data.confidence_level * 100).toFixed(1)}%</Badge>
                  </div>
                )}
                <div className="max-h-40 overflow-y-auto">
                  {data.anomalies_detected.slice(0, 5).map((anomaly, index) => (
                    <div key={index} className="p-2 bg-red-50 border border-red-200 rounded mb-2">
                      <pre className="text-xs text-red-800">{JSON.stringify(anomaly, null, 2)}</pre>
                    </div>
                  ))}
                  {data.anomalies_detected.length > 5 && (
                    <p className="text-sm text-gray-500 text-center">
                      ... and {data.anomalies_detected.length - 5} more anomalies
                    </p>
                  )}
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-2 text-green-600">
                <CheckCircle className="h-4 w-4" />
                <span className="text-sm">No anomalies detected</span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Statistical Summary */}
        {data.statistical_summary && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingDown className="h-5 w-5 text-blue-500" />
                Statistical Summary
              </CardTitle>
              <CardDescription>
                Statistical analysis of the dataset
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {Object.entries(data.statistical_summary).map(([key, value]) => (
                  <div key={key} className="flex justify-between items-center py-1">
                    <span className="text-sm font-medium capitalize">
                      {key.replace(/_/g, ' ')}:
                    </span>
                    <span className="text-sm text-gray-600">
                      {typeof value === 'number' ? value.toFixed(3) : String(value)}
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Recommendations */}
      {data.recommendations && data.recommendations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-green-500" />
              Recommendations
            </CardTitle>
            <CardDescription>
              Suggested actions based on anomaly detection results
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
            Complete anomaly detection output data
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