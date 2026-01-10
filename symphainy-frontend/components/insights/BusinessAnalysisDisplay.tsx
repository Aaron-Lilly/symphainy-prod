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
  TrendingUp,
  FileText,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface BusinessAnalysisData {
  gaps_or_weaknesses?: string[];
  recommendations?: string[];
  potential_risks?: string[];
  business_summary?: string;
}

interface BusinessAnalysisDisplayProps {
  // Always updatable props (required)
  data: BusinessAnalysisData;
  
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

export default function BusinessAnalysisDisplay({
  title: propTitle,
  description: propDescription,
  data,
  onBack: propOnBack,
  loading: propLoading = false,
}: BusinessAnalysisDisplayProps) {
  // Store the initial values that should "stick"
  const storedDefaults = useRef<StoredDefaults>({});
  const isInitialized = useRef(false);

  // On first render, store the provided sticky props
  useEffect(() => {
    if (!isInitialized.current) {
      if (propTitle !== undefined) {
        storedDefaults.current.title = propTitle;
      }
      if (propDescription !== undefined) {
        storedDefaults.current.description = propDescription;
      }
      if (propOnBack !== undefined) {
        storedDefaults.current.onBack = propOnBack;
      }
      if (propLoading !== undefined) {
        storedDefaults.current.loading = propLoading;
      }
      isInitialized.current = true;
    }
  }, []); // Only run on mount

  // Use provided props if available, otherwise fall back to stored defaults
  const title = propTitle ?? storedDefaults.current.title ?? "Business Analysis";
  const description = propDescription ?? storedDefaults.current.description ?? "Analysis results";
  const onBack = propOnBack ?? storedDefaults.current.onBack;
  const loading = propLoading ?? storedDefaults.current.loading ?? false;

  // Parse the data if it comes wrapped in raw_response
  const parseBusinessData = (rawData: any): BusinessAnalysisData => {
    console.log("Raw business analysis data:", rawData);

    // If data has results field (API response wrapper), extract it
    if (rawData?.results) {
      console.log("Extracting results from API response:", rawData.results);
      return rawData.results;
    }

    // If data has data field (API response wrapper), extract it
    if (rawData?.data) {
      console.log("Extracting data from API response:", rawData.data);
      
      // Check if the data object has a nested results field
      if (rawData.data?.results) {
        console.log("Extracting nested results:", rawData.data.results);
        return rawData.data.results;
      }
      
      return rawData.data;
    }

    // If data has raw_response field, extract JSON from markdown
    if (rawData?.raw_response) {
      try {
        // Extract JSON from markdown code block
        const jsonMatch = rawData.raw_response.match(
          /```json\n([\s\S]*?)\n```/,
        );
        if (jsonMatch && jsonMatch[1]) {
          const jsonString = jsonMatch[1].trim();
          const parsed = JSON.parse(jsonString);
          console.log("Parsed business analysis data:", parsed);
          return parsed;
        }
      } catch (error) {
        console.error("Error parsing raw_response:", error);
      }
    }

    // Return data as-is if it's already in the expected format
    console.log("Using data as-is:", rawData);
    return rawData || {};
  };

  const parsedData = parseBusinessData(data);

  const copyToClipboard = () => {
    navigator.clipboard.writeText(JSON.stringify(parsedData, null, 2));
  };

  const downloadJSON = () => {
    const blob = new Blob([JSON.stringify(parsedData, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `business_analysis_results.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="flex-grow space-y-8 min-h-screen">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p>Analyzing your business data...</p>
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

      {/* Business Summary */}
      {parsedData.business_summary && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-blue-600" />
              Business Summary
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-800 text-sm leading-relaxed">
              {parsedData.business_summary}
            </p>
          </CardContent>
        </Card>
      )}

      {/* Analysis Results Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Gaps & Weaknesses */}
        {parsedData.gaps_or_weaknesses &&
          parsedData.gaps_or_weaknesses.length > 0 && (
            <Card className="border-yellow-400">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-yellow-500">
                  <AlertTriangle className="h-5 w-5" />
                  Gaps & Weaknesses
                </CardTitle>
                <CardDescription>Areas that need improvements</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {parsedData.gaps_or_weaknesses.map((gap, index) => (
                    <div key={index}>
                      <div className="flex items-start gap-3">
                        <div className="w-[6px] h-[6px] rounded-full bg-gray-800 mt-2 flex-shrink-0"></div>
                        <p className="text-sm text-gray-800 flex-1">{gap}</p>
                      </div>
                      {index < parsedData.gaps_or_weaknesses!.length - 1 && (
                        <div className="border-b border-gray-100 my-3"></div>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

        {/* Recommendations */}
        {parsedData.recommendations &&
          parsedData.recommendations.length > 0 && (
            <Card className="border-green-200">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-green-700">
                  <CheckCircle className="h-5 w-5" />
                  Recommendations
                </CardTitle>
                <CardDescription>
                  Suggested actions and improvements
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {parsedData.recommendations.map((recommendation, index) => (
                    <div key={index}>
                      <div className="flex items-start gap-3">
                        <div className="w-[6px] h-[6px] rounded-full bg-gray-800 mt-2 flex-shrink-0"></div>
                        <p className="text-sm text-gray-800 flex-1">
                          {recommendation}
                        </p>
                      </div>
                      {index < parsedData.recommendations!.length - 1 && (
                        <div className="border-b border-gray-100 my-3"></div>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

        {/* Potential Risks */}
        {parsedData.potential_risks &&
          parsedData.potential_risks.length > 0 && (
            <Card className="border-orange-200">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-orange-700">
                  <TrendingUp className="h-5 w-5" />
                  Potential Risks
                </CardTitle>
                <CardDescription>Identified risks and concerns</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {parsedData.potential_risks.map((risk, index) => (
                    <div key={index}>
                      <div className="flex items-start gap-3">
                        <div className="w-[6px] h-[6px] rounded-full bg-gray-800 mt-2 flex-shrink-0"></div>
                        <p className="text-sm text-gray-800 flex-1">{risk}</p>
                      </div>
                      {index < parsedData.potential_risks!.length - 1 && (
                        <div className="border-b border-gray-100 my-3"></div>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
      </div>

      {/* Empty State */}
      {!parsedData.business_summary &&
        (!parsedData.gaps_or_weaknesses ||
          parsedData.gaps_or_weaknesses.length === 0) &&
        (!parsedData.recommendations ||
          parsedData.recommendations.length === 0) &&
        (!parsedData.potential_risks ||
          parsedData.potential_risks.length === 0) && (
          <Card>
            <CardContent className="text-center py-8 text-gray-500">
              <p>No business analysis results available</p>
            </CardContent>
          </Card>
        )}
    </div>
  );
}
