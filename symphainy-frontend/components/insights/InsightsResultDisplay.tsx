"use client";

import React from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Copy, Download } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface InsightsResultDisplayProps {
  title: string;
  description: string;
  data: any;
  onBack?: () => void;
  loading?: boolean;
}

export default function InsightsResultDisplay({
  title,
  description,
  data,
  onBack,
  loading = false,
}: InsightsResultDisplayProps) {
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
    a.download = `${title.toLowerCase().replace(/\s+/g, "_")}_results.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const renderValue = (value: any, key?: string): React.ReactNode => {
    if (value === null || value === undefined) {
      return <span className="text-gray-400 italic">null</span>;
    }

    if (typeof value === "boolean") {
      return (
        <Badge variant={value ? "default" : "secondary"}>
          {value.toString()}
        </Badge>
      );
    }

    if (typeof value === "number") {
      return (
        <span className="font-mono text-blue-600">
          {value.toLocaleString()}
        </span>
      );
    }

    if (typeof value === "string") {
      // Handle long strings
      if (value.length > 100) {
        return (
          <div className="bg-gray-50 p-3 rounded text-sm font-mono whitespace-pre-wrap break-words max-h-40 overflow-y-auto">
            {value}
          </div>
        );
      }
      return <span className="text-gray-900">{value}</span>;
    }

    if (Array.isArray(value)) {
      return (
        <div className="space-y-3">
          <Badge variant="outline">{value.length} items</Badge>
          <div className="bg-gray-50 p-4 rounded max-h-60 overflow-y-auto">
            <div className="space-y-3">
              {value.map((item, index) => (
                <div key={index} className="flex items-start">
                  <div className="flex-shrink-0 w-8 text-xs text-gray-500 pt-1">
                    {index + 1}.
                  </div>
                  <div className="flex-1 text-gray-800 leading-relaxed">
                    {renderValue(item)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      );
    }

    if (typeof value === "object") {
      return (
        <div className="bg-gray-50 p-3 rounded">
          <div className="overflow-x-auto">
            <table className="w-full">
              <tbody>
                {Object.entries(value).map(([nestedKey, nestedValue]) => (
                  <tr
                    key={nestedKey}
                    className="border-b border-gray-200 last:border-b-0"
                  >
                    <td className="py-3 pr-4 text-sm font-medium text-gray-700 align-top w-[180px] min-w-[180px]">
                      {nestedKey}:
                    </td>
                    <td className="py-3 align-top">
                      <div className="min-w-0">
                        {renderValue(nestedValue, nestedKey)}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      );
    }

    return <span className="text-gray-900">{String(value)}</span>;
  };

  if (loading) {
    return (
      <div className="flex-grow space-y-8 min-h-screen">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p>Analyzing your data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-grow space-y-8 min-h-screen">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold">{title}</h1>
            <p className="text-gray-600 text-sm">{description}</p>
          </div>
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
            <Button onClick={onBack} variant="outline" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
          )}
        </div>
      </div>

      {/* Results */}
      <Card>
        <CardHeader>
          <CardTitle>Analysis Results</CardTitle>
          <CardDescription>
            Detailed insights and analysis results from your data
          </CardDescription>
        </CardHeader>
        <CardContent>
          {data && typeof data === "object" ? (
            <div className="space-y-4">
              {Object.entries(data).map(([key, value]) => (
                <>
                  <div key={key} className="border rounded-lg p-4">
                    <div className="flex flex-col gap-3">
                      {/* <h3 className="text-lg font-semibold text-gray-900 capitalize">
                      {key.replace(/_/g, ' ')}
                    </h3> */}
                      <div className="min-w-0">{renderValue(value, key)}</div>
                    </div>
                  </div>
                  <hr className="my-4" />
                </>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <p>No results available</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
