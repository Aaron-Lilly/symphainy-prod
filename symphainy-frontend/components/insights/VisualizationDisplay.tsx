"use client";

import React, { useState } from "react";
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
  Image as ImageIcon,
  ZoomIn,
  ZoomOut,
} from "lucide-react";

interface VisualizationDisplayProps {
  title: string;
  description: string;
  data: any;
  onBack?: () => void;
  loading?: boolean;
}

export default function VisualizationDisplay({
  title,
  description,
  data,
  onBack,
  loading = false,
}: VisualizationDisplayProps) {
  const [expandedImage, setExpandedImage] = useState<string | null>(null);

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
    a.download = `visualization_results.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const downloadImage = (base64Data: string, filename: string) => {
    const link = document.createElement("a");
    link.href = `data:image/png;base64,${base64Data}`;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const renderValue = (value: any, key?: string): React.ReactNode => {
    if (value === null || value === undefined) {
      return <span className="text-gray-400 italic">null</span>;
    }

    // Handle base64 images
    if (key === "image_base64" && typeof value === "string") {
      return (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">
              Generated Visualization
            </span>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setExpandedImage(value)}
              >
                <ZoomIn className="h-4 w-4 mr-1" />
                Expand
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => downloadImage(value, "visualization.png")}
              >
                <Download className="h-4 w-4 mr-1" />
                Download
              </Button>
            </div>
          </div>
          <div className="border rounded-lg p-2 bg-gray-50">
            <img
              src={`data:image/png;base64,${value}`}
              alt="Data Visualization"
              className="max-w-full h-auto rounded cursor-pointer hover:opacity-90 transition-opacity"
              onClick={() => setExpandedImage(value)}
              style={{ maxHeight: "400px" }}
            />
          </div>
        </div>
      );
    }

    if (typeof value === "boolean") {
      return (
        <span
          className={`px-2 py-1 rounded text-xs ${value ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-800"}`}
        >
          {value.toString()}
        </span>
      );
    }

    if (typeof value === "number") {
      return <span className="text-blue-600 font-mono">{value}</span>;
    }

    if (typeof value === "string") {
      if (value.length > 200) {
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
          <div className="text-sm text-gray-500">{value.length} items</div>
          <div className="bg-gray-50 p-4 rounded space-y-4 max-h-60 overflow-y-auto">
            {value.map((item, index) => (
              <div key={index}>
                <div className="text-gray-800 leading-relaxed">
                  {renderValue(item)}
                </div>
                {index < value.length - 1 && (
                  <div className="border-b border-gray-200 my-3"></div>
                )}
              </div>
            ))}
          </div>
        </div>
      );
    }

    if (typeof value === "object") {
      return (
        <div className="bg-gray-50 p-4 rounded space-y-4">
          {Object.entries(value).map(([nestedKey, nestedValue]) => (
            <div
              key={nestedKey}
              className="border-b border-gray-200 last:border-b-0 pb-3 last:pb-0"
            >
              <div className="grid grid-cols-1 sm:grid-cols-[180px_1fr] gap-3">
                <span className="text-sm font-medium text-gray-700 w-[180px] capitalize">
                  {nestedKey.replace(/_/g, " ")}:
                </span>
                <div className="min-w-0">
                  {renderValue(nestedValue, nestedKey)}
                </div>
              </div>
            </div>
          ))}
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
          <p>Generating visualizations...</p>
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
          <CardTitle className="flex items-center gap-2">
            <ImageIcon className="h-5 w-5 text-purple-600" />
            Visualization Results
          </CardTitle>
          <CardDescription>
            Generated charts and visual analysis of your data
          </CardDescription>
        </CardHeader>
        <CardContent>
          {data && typeof data === "object" ? (
            <div className="space-y-6">
              {Object.entries(data).map(([key, value]) => (
                <div key={key}>
                  <div className="border rounded-lg p-4">
                    <div className="space-y-3">
                      {/* <h3 className="text-lg font-semibold text-gray-900 capitalize">
                      {key.replace(/_/g, ' ')}
                    </h3> */}
                      <div>{renderValue(value, key)}</div>
                    </div>
                  </div>
                  <hr className="my-4" />
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <p>No visualization results available</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Image Modal */}
      {expandedImage && (
        <div
          className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4"
          onClick={() => setExpandedImage(null)}
        >
          <div className="relative max-w-full max-h-full">
            <Button
              variant="outline"
              size="sm"
              className="absolute top-4 right-4 bg-white"
              onClick={() => setExpandedImage(null)}
            >
              <ZoomOut className="h-4 w-4" />
            </Button>
            <img
              src={`data:image/png;base64,${expandedImage}`}
              alt="Expanded Visualization"
              className="max-w-full max-h-full object-contain rounded"
              onClick={(e) => e.stopPropagation()}
            />
          </div>
        </div>
      )}
    </div>
  );
}
