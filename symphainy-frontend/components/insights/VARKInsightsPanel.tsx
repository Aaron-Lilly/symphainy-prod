/**
 * VARK-Aligned Insights Panel
 * 
 * Complete Vision Implementation:
 * 1. File Selection (top) - Only parsed files from Content pillar
 * 2. VARK Component Display (middle) - Two elements side by side
 * 3. Summary Section (bottom) - Business analysis + visual/tabular output, save/share with Experience pillar
 */

import React, { useState, useCallback, useMemo, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "@/components/ui/table";
import { 
  BarChart3, 
  Table as TableIcon, 
  TrendingUp, 
  FileText,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  Download,
  Share2,
  Sparkles,
  Loader2,
  Eye,
  FileSpreadsheet
} from "lucide-react";
import { useAGUIEvent } from "@/shared/agui/AGUIEventProvider";
import { withErrorBoundary } from '@/shared/components/ErrorBoundary';
// useErrorHandler will be dynamically imported when needed
import { useGlobalSession } from "@/shared/agui/GlobalSessionProvider";
import { listFiles } from "@/lib/api/fms-insights";
import { FileMetadata } from "@/shared/types/file";

// Import types
import type { 
  InsightsPanelOutput, 
  AGUIResponse, 
  ProcessedResponses 
} from './InsightsPanel/types';

// Import utilities
import { processAGUIResponsesStacked } from './InsightsPanel/utils';

// ============================================
// Component Interface
// ============================================

interface VARKInsightsPanelProps {
  onClose?: () => void;
  className?: string;
  initialData?: any;
}

type LearningStyle = 'tabular' | 'visual';
type DataDepth = 'summary' | 'detailed' | 'drill-down';

// ============================================
// Main Component
// ============================================

function VARKInsightsPanelComponent({ 
  onClose, 
  className = '',
  initialData 
}: VARKInsightsPanelProps) {
  // ============================================
  // State Management
  // ============================================

  const { getPillarState, setPillarState, guideSessionToken } = useGlobalSession();
  
  // File Selection State
  const [files, setFiles] = useState<FileMetadata[]>([]);
  const [selectedFile, setSelectedFile] = useState<FileMetadata | null>(null);
  const [fileLoading, setFileLoading] = useState(true);
  
  // VARK Display State
  const [learningStyle, setLearningStyle] = useState<LearningStyle>('tabular');
  const [dataDepth, setDataDepth] = useState<DataDepth>('summary');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  
  // Summary Section State
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [summaryData, setSummaryData] = useState<any>(null);
  const [showSummary, setShowSummary] = useState(false);
  
  // Insights Data State
  const [insightsData, setInsightsData] = useState<any>({
    businessSummary: "Select a parsed file to begin your VARK-aligned insights journey.",
    tabularData: [],
    visualData: null,
    keyMetrics: [],
    recommendations: []
  });

  // ============================================
  // Error Handling
  // ============================================

  // Simple error state management without external hook
  const [errorState, setErrorState] = useState({ 
    hasError: false, 
    error: null, 
    errorId: null, 
    timestamp: null, 
    retryCount: 0, 
    isRetrying: false 
  });

  const handleError = (error: any) => {
    setErrorState({
      hasError: true,
      error,
      errorId: `error_${Date.now()}`,
      timestamp: Date.now(),
      retryCount: errorState.retryCount + 1,
      isRetrying: false
    });
  };

  const clearError = () => {
    setErrorState({
      hasError: false,
      error: null,
      errorId: null,
      timestamp: null,
      retryCount: 0,
      isRetrying: false
    });
  };

  // ============================================
  // AGUI Event Handling
  // ============================================

  const { sendEvent } = useAGUIEvent();

  const sendAgentEvent = useCallback(async (event: any) => {
    try {
      setIsAnalyzing(true);
      clearError();
      await sendEvent(event);
    } catch (error) {
      handleError(error instanceof Error ? error : new Error('Failed to send agent event'));
    } finally {
      setIsAnalyzing(false);
    }
  }, [sendEvent, handleError, clearError]);

  // ============================================
  // File Management
  // ============================================

  useEffect(() => {
    async function fetchFiles() {
      try {
        setFileLoading(true);
        const fileList = await listFiles();
        const parsedFiles = fileList
          .filter((file) => file.parsed_path)
          .sort(
            (a, b) =>
              new Date(b.created_at).getTime() -
              new Date(a.created_at).getTime(),
          );
        setFiles(parsedFiles);
      } catch (err) {
        handleError(new Error("Failed to load parsed files"));
      } finally {
        setFileLoading(false);
      }
    }
    fetchFiles();
  }, [handleError]);

  const handleFileSelect = useCallback((fileUuid: string) => {
    const file = files.find((f) => f.uuid === fileUuid);
    setSelectedFile(file || null);
    setInsightsData({
      businessSummary: "File selected. Click 'Analyze with VARK' to begin insights generation.",
      tabularData: [],
      visualData: null,
      keyMetrics: [],
      recommendations: []
    });
    setShowSummary(false);
    clearError();
  }, [files, clearError]);

  const handleAnalyze = useCallback(async () => {
    if (!selectedFile) return;

    setIsAnalyzing(true);
    clearError();

    try {
      // Simulate VARK analysis (replace with actual Smart City API calls)
      await new Promise((resolve) => setTimeout(resolve, 2000));
      
      // Generate sample VARK-aligned insights
      const sampleData = {
        businessSummary: `We reviewed your ${selectedFile.ui_name} and identified key business insights. The data shows significant patterns in customer behavior, with ${Math.floor(Math.random() * 50) + 10}% of customers falling into high-value segments. We recommend focusing on retention strategies for these segments and investigating the ${Math.floor(Math.random() * 20) + 5} identified anomalies for potential optimization opportunities.`,
        tabularData: [
          { "Customer ID": "C001", "Segment": "High-Value", "Revenue": "$12,450", "Risk Score": "Low" },
          { "Customer ID": "C002", "Segment": "Medium-Value", "Revenue": "$8,200", "Risk Score": "Medium" },
          { "Customer ID": "C003", "Segment": "High-Value", "Revenue": "$15,800", "Risk Score": "Low" },
          { "Customer ID": "C004", "Segment": "Low-Value", "Revenue": "$3,100", "Risk Score": "High" },
          { "Customer ID": "C005", "Segment": "Medium-Value", "Revenue": "$9,500", "Risk Score": "Medium" }
        ],
        visualData: {
          charts: ["trend", "distribution", "correlation"],
          metrics: {
            totalCustomers: 1250,
            highValuePercentage: 35,
            averageRevenue: 8500
          }
        },
        keyMetrics: [
          { label: "Total Customers", value: "1,250", trend: "+12%" },
          { label: "High-Value Segment", value: "35%", trend: "+8%" },
          { label: "Avg Revenue", value: "$8,500", trend: "+15%" }
        ],
        recommendations: [
          "Focus retention efforts on the 35% high-value customer segment",
          "Investigate the 5 identified anomalies for optimization opportunities",
          "Consider segment-specific marketing campaigns based on behavioral patterns"
        ]
      };
      
      setInsightsData(sampleData);
      
    } catch (err) {
      handleError(new Error("Failed to analyze file with VARK approach"));
    } finally {
      setIsAnalyzing(false);
    }
  }, [selectedFile, handleError, clearError]);

  // ============================================
  // Learning Style Management
  // ============================================

  const handleLearningStyleChange = useCallback((style: LearningStyle) => {
    setLearningStyle(style);
    setDataDepth('summary');
  }, []);

  const handleDataDepthChange = useCallback((depth: DataDepth) => {
    setDataDepth(depth);
  }, []);

  // ============================================
  // Summary Management
  // ============================================

  const handleGenerateSummary = useCallback(async () => {
    if (!guideSessionToken) {
      handleError(new Error("No active session found"));
      return;
    }

    setSummaryLoading(true);
    clearError();

    try {
      // Simulate summary generation (replace with actual Smart City API calls)
      await new Promise((resolve) => setTimeout(resolve, 1500));
      
      const summary = {
        summary_text: insightsData.businessSummary,
        visual_output: learningStyle === 'visual' ? insightsData.visualData : null,
        tabular_output: learningStyle === 'tabular' ? insightsData.tabularData : null,
        key_insights: insightsData.recommendations,
        generated_at: new Date().toISOString(),
        file_analyzed: selectedFile?.ui_name
      };
      
      setSummaryData(summary);
      setShowSummary(true);
      
      // Save to global session for experience pillar
      const currentInsightsState = getPillarState("insights") || {};
      setPillarState("insights", {
        ...currentInsightsState,
        vark_summary: summary,
        selected_file: selectedFile,
        insights_data: insightsData,
        learning_style: learningStyle
      });
      
    } catch (err) {
      handleError(new Error("Failed to generate summary"));
    } finally {
      setSummaryLoading(false);
    }
  }, [guideSessionToken, insightsData, learningStyle, selectedFile, getPillarState, setPillarState, handleError, clearError]);

  const handleExportSummary = useCallback(() => {
    if (summaryData) {
      const dataStr = JSON.stringify(summaryData, null, 2);
      const dataBlob = new Blob([dataStr], { type: "application/json" });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `vark-insights-summary-${new Date().toISOString().split("T")[0]}.json`;
      link.click();
      URL.revokeObjectURL(url);
    }
  }, [summaryData]);

  const handleShareSummary = useCallback(() => {
    if (summaryData) {
      const summaryText = summaryData.summary_text;
      navigator.clipboard.writeText(summaryText).then(() => {
        alert("VARK summary copied to clipboard!");
      });
    }
  }, [summaryData]);

  // ============================================
  // Render Methods
  // ============================================

  const renderFileSelection = useCallback(() => (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileSpreadsheet className="h-5 w-5" />
          Select Parsed File for VARK Analysis
        </CardTitle>
        <p className="text-sm text-gray-600">
          Choose a file that has been processed through the Content pillar
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        {fileLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="w-6 h-6 animate-spin mr-2" />
            <span>Loading parsed files...</span>
          </div>
        ) : files.length === 0 ? (
          <div className="text-center py-8">
            <h3 className="text-lg font-semibold mb-2">
              No parsed files available
            </h3>
            <p className="text-gray-600 mb-4">
              Upload and parse a file in the Content pillar first.
            </p>
            <Button
              onClick={() => typeof window !== 'undefined' && (window.location.href = "/pillars/content")}
            >
              Go to Content Pillar
            </Button>
          </div>
        ) : (
          <>
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">
                Available Parsed Files
              </label>
              <Select onValueChange={handleFileSelect}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select a parsed file..." />
                </SelectTrigger>
                <SelectContent>
                  {files.map((file) => (
                    <SelectItem key={file.uuid} value={file.uuid}>
                      <div className="flex items-center justify-between w-full">
                        <span>{file.ui_name}</span>
                        <span className="text-xs text-gray-500 ml-2">
                          {file.file_type} • {new Date(file.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {selectedFile && (
              <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
                <div>
                  <p className="font-medium text-black text-sm">
                    {selectedFile.ui_name}
                  </p>
                  <p className="text-xs text-black">
                    {selectedFile.file_type} • Ready for VARK analysis
                  </p>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  className="bg-white text-black border border-primary hover:bg-primary hover:text-white"
                  disabled={isAnalyzing}
                  onClick={handleAnalyze}
                >
                  {isAnalyzing ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Eye className="w-4 h-4 mr-2" />
                      Analyze with VARK
                    </>
                  )}
                </Button>
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  ), [files, fileLoading, selectedFile, isAnalyzing, handleFileSelect, handleAnalyze]);

  const renderVARKDisplay = useCallback(() => (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      {/* Left Side - Business Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Business Analysis Summary
            <Badge variant="secondary" className="ml-auto">
              Auditory-Friendly
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="prose prose-sm max-w-none">
            <p className="text-gray-700 leading-relaxed">
              {insightsData.businessSummary}
            </p>
          </div>
          
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
            {insightsData.keyMetrics?.map((metric: any, index: number) => (
              <div key={index} className="text-center p-3 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{metric.value}</div>
                <div className="text-sm text-gray-600">{metric.label}</div>
                <div className={`text-xs ${metric.trend.startsWith('+') ? 'text-green-600' : 'text-red-600'}`}>
                  {metric.trend}
                </div>
              </div>
            ))}
          </div>

          {/* Recommendations */}
          <div className="mt-6">
            <h4 className="font-semibold text-gray-800 mb-3">Key Recommendations</h4>
            <ul className="space-y-2">
              {insightsData.recommendations?.map((rec: string, index: number) => (
                <li key={index} className="flex items-start gap-2 text-sm text-gray-700">
                  <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                  {rec}
                </li>
              ))}
            </ul>
          </div>
        </CardContent>
      </Card>

      {/* Right Side - Learning Style Selector & Dynamic Panel */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Choose Your Learning Style</CardTitle>
          <p className="text-sm text-gray-600">
            Select how you'd like to explore the data
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Learning Style Buttons */}
          <div className="grid grid-cols-2 gap-4">
            <Button
              variant={learningStyle === 'tabular' ? 'default' : 'outline'}
              className="h-auto p-4 flex flex-col items-center gap-2"
              onClick={() => handleLearningStyleChange('tabular')}
            >
              <TableIcon className="h-6 w-6" />
              <div className="text-center">
                <div className="font-semibold">Tabular View</div>
                <div className="text-xs text-gray-600">Read/Write Learners</div>
              </div>
            </Button>
            
            <Button
              variant={learningStyle === 'visual' ? 'default' : 'outline'}
              className="h-auto p-4 flex flex-col items-center gap-2"
              onClick={() => handleLearningStyleChange('visual')}
            >
              <BarChart3 className="h-6 w-6" />
              <div className="text-center">
                <div className="font-semibold">Visual View</div>
                <div className="text-xs text-gray-600">Visual Learners</div>
              </div>
            </Button>
          </div>

          {/* Dynamic Panel */}
          <div className="mt-4">
            {learningStyle === 'tabular' ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h4 className="font-semibold">Tabular Data</h4>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDataDepthChange(dataDepth === 'summary' ? 'detailed' : 'summary')}
                  >
                    {dataDepth === 'summary' ? <ChevronDown className="h-4 w-4" /> : <ChevronUp className="h-4 w-4" />}
                    {dataDepth === 'summary' ? 'Show More' : 'Show Less'}
                  </Button>
                </div>
                {insightsData.tabularData && insightsData.tabularData.length > 0 ? (
                  <div className="overflow-x-auto max-h-64">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          {Object.keys(insightsData.tabularData[0] || {}).map((header) => (
                            <TableHead key={header}>{header}</TableHead>
                          ))}
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {insightsData.tabularData.slice(0, dataDepth === 'summary' ? 3 : 10).map((row: any, index: number) => (
                          <TableRow key={index}>
                            {Object.values(row).map((cell: any, cellIndex: number) => (
                              <TableCell key={cellIndex}>{String(cell)}</TableCell>
                            ))}
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <TableIcon className="h-8 w-8 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">No tabular data available</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h4 className="font-semibold">Visual Data</h4>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDataDepthChange(dataDepth === 'summary' ? 'detailed' : 'summary')}
                  >
                    {dataDepth === 'summary' ? <ChevronDown className="h-4 w-4" /> : <ChevronUp className="h-4 w-4" />}
                    {dataDepth === 'summary' ? 'Show More' : 'Show Less'}
                  </Button>
                </div>
                {insightsData.visualData ? (
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="h-32 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg flex items-center justify-center">
                        <div className="text-center">
                          <TrendingUp className="h-8 w-8 mx-auto mb-1 text-blue-600" />
                          <p className="text-xs text-gray-600">Trend Analysis</p>
                        </div>
                      </div>
                      <div className="h-32 bg-gradient-to-br from-green-50 to-green-100 rounded-lg flex items-center justify-center">
                        <div className="text-center">
                          <BarChart3 className="h-8 w-8 mx-auto mb-1 text-green-600" />
                          <p className="text-xs text-gray-600">Distribution</p>
                        </div>
                      </div>
                    </div>
                    
                    {dataDepth === 'detailed' && (
                      <div className="grid grid-cols-3 gap-2">
                        <div className="h-24 bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg flex items-center justify-center">
                          <div className="text-center">
                            <div className="text-lg font-bold text-purple-600">85%</div>
                            <p className="text-xs text-gray-600">Quality</p>
                          </div>
                        </div>
                        <div className="h-24 bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg flex items-center justify-center">
                          <div className="text-center">
                            <div className="text-lg font-bold text-orange-600">12</div>
                            <p className="text-xs text-gray-600">Patterns</p>
                          </div>
                        </div>
                        <div className="h-24 bg-gradient-to-br from-red-50 to-red-100 rounded-lg flex items-center justify-center">
                          <div className="text-center">
                            <div className="text-lg font-bold text-red-600">3</div>
                            <p className="text-xs text-gray-600">Anomalies</p>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <BarChart3 className="h-8 w-8 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">No visual data available</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  ), [insightsData, learningStyle, dataDepth, handleLearningStyleChange, handleDataDepthChange]);

  const renderSummarySection = useCallback(() => (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-purple-600" />
          VARK Insights Summary
        </CardTitle>
        <p className="text-sm text-gray-600">
          Generate and save insights aligned with your learning style preferences
        </p>
      </CardHeader>
      <CardContent>
        {!showSummary ? (
          <div className="text-center py-8">
            <Button
              onClick={handleGenerateSummary}
              disabled={summaryLoading || !selectedFile || insightsData.businessSummary.includes("Select a parsed file")}
              size="lg"
              className="bg-purple-600 hover:bg-purple-700"
            >
              {summaryLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Generating VARK Summary...
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-4 w-4" />
                  Generate VARK Summary
                </>
              )}
            </Button>
            {(!selectedFile || insightsData.businessSummary.includes("Select a parsed file")) && (
              <p className="text-sm text-gray-500 mt-2">
                Select a file and run VARK analysis to generate summary
              </p>
            )}
          </div>
        ) : (
          <div className="space-y-6">
            {/* Business Analysis Summary */}
            <div className="bg-blue-50 p-4 rounded-lg">
              <h4 className="font-semibold text-blue-800 mb-2">Business Analysis Summary</h4>
              <p className="text-blue-700 text-sm leading-relaxed">
                {summaryData?.summary_text}
              </p>
            </div>

            {/* Learning Style Output */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-semibold text-gray-800 mb-2">
                {learningStyle === 'visual' ? 'Visual Output' : 'Tabular Output'}
              </h4>
              {learningStyle === 'visual' && summaryData?.visual_output ? (
                <div className="text-sm text-gray-600">
                  <p>Charts generated: {summaryData.visual_output.charts?.join(', ')}</p>
                  <p>Key metrics available for visualization</p>
                </div>
              ) : learningStyle === 'tabular' && summaryData?.tabular_output ? (
                <div className="text-sm text-gray-600">
                  <p>Data table with {summaryData.tabular_output.length} rows available</p>
                  <p>Structured data ready for export</p>
                </div>
              ) : (
                <p className="text-sm text-gray-500">No output data available</p>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-4">
              <Button onClick={handleExportSummary} variant="outline">
                <Download className="w-4 h-4 mr-2" />
                Export Summary
              </Button>
              <Button onClick={handleShareSummary} variant="outline">
                <Share2 className="w-4 h-4 mr-2" />
                Share with Experience Pillar
              </Button>
              <Button 
                onClick={() => setShowSummary(false)} 
                variant="ghost"
              >
                Generate New Summary
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  ), [showSummary, summaryLoading, selectedFile, insightsData, summaryData, learningStyle, handleGenerateSummary, handleExportSummary, handleShareSummary]);

  // ============================================
  // Main Render
  // ============================================

  if (errorState.hasError) {
    return (
      <div className={`vark-insights-panel-error ${className}`}>
        <div className="text-center p-8">
          <h3 className="text-lg font-semibold text-red-600 mb-2">
            VARK Insights Panel Error
          </h3>
          <p className="text-gray-600 mb-4">
            {errorState.error?.message || 'An error occurred while loading insights'}
          </p>
          <Button onClick={clearError} variant="outline">
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className={`vark-insights-panel ${className} max-w-7xl mx-auto`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b bg-white">
        <div>
          <h2 className="text-xl font-semibold">VARK-Aligned Insights</h2>
          <p className="text-sm text-gray-600">Learning-style optimized data exploration with Smart City integration</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" disabled={isAnalyzing}>
            <RefreshCw className={`h-4 w-4 ${isAnalyzing ? 'animate-spin' : ''}`} />
          </Button>
          {onClose && (
            <Button 
              onClick={onClose} 
              variant="ghost" 
              size="sm"
              disabled={isAnalyzing}
            >
              ✕
            </Button>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="p-6 space-y-6">
        {/* Section 1: File Selection */}
        {renderFileSelection()}
        
        {/* Section 2: VARK Component Display */}
        {renderVARKDisplay()}
        
        {/* Section 3: Summary Section */}
        {renderSummarySection()}
      </div>
    </div>
  );
}

// ============================================
// Export with Error Boundary
// ============================================

export const VARKInsightsPanel = React.memo(
  withErrorBoundary(VARKInsightsPanelComponent, {
    fallback: ({ error, retry }: any) => (
      <div className="vark-insights-panel-error p-8 text-center">
        <h3 className="text-lg font-semibold text-red-600 mb-2">
          VARK Insights Panel Error
        </h3>
        <p className="text-gray-600 mb-4">
          {error.message}
        </p>
        <Button onClick={retry} variant="outline">
          Try Again
        </Button>
      </div>
    ),
  })
);

VARKInsightsPanel.displayName = 'VARKInsightsPanel'; 