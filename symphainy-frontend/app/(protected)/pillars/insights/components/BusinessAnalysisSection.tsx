/**
 * Business Analysis Section
 * 
 * Combines structured and unstructured data analysis into a single unified section.
 * Supports both analysis types with a tabbed interface.
 */

"use client";

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Checkbox } from '@/components/ui/checkbox';
import { AlertCircle, Sparkles, Target, Database, FileText } from 'lucide-react';
import { InsightsFileSelector } from './InsightsFileSelector';
import { InsightsSummaryDisplay } from './InsightsSummaryDisplay';
import { AARAnalysisSection } from './AARAnalysisSection';
import { useInsightsAPIManager, AnalysisResponse } from '@/shared/managers/InsightsAPIManager';
import { usePlatformState } from '@/shared/state/PlatformStateProvider';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface BusinessAnalysisSectionProps {
  onAnalysisComplete?: (analysis: AnalysisResponse) => void;
}

export function BusinessAnalysisSection({ 
  onAnalysisComplete 
}: BusinessAnalysisSectionProps) {
  const { state } = usePlatformState();
  const insightsAPIManager = useInsightsAPIManager();

  const [selectedFileId, setSelectedFileId] = useState<string>('');
  const [selectedParsedFileId, setSelectedParsedFileId] = useState<string>('');
  const [selectedSourceType, setSelectedSourceType] = useState<'file' | 'content_metadata'>('file');
  const [analysisType, setAnalysisType] = useState<'structured' | 'unstructured'>('structured');
  const [aarMode, setAarMode] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelected = (
    fileId: string, 
    sourceType: 'file' | 'content_metadata',
    contentType: 'structured' | 'unstructured'
  ) => {
    setSelectedFileId(fileId);
    setSelectedSourceType(sourceType);
    setSelectedParsedFileId('');
    setAnalysisResult(null);
    setError(null);
    
    // Load parsed files for this file
    loadParsedFiles(fileId);
  };

  // Load parsed files for the selected file
  const loadParsedFiles = (fileId: string) => {
    const parsedFiles = state.realm.content.parsedFiles || [];
    const fileParsedFiles = parsedFiles.filter((pf: any) => 
      pf.file_id === fileId || pf.source_file_id === fileId
    );
    
    if (fileParsedFiles.length > 0) {
      setSelectedParsedFileId(fileParsedFiles[0].parsed_file_id || fileParsedFiles[0].id);
    }
  };

  // Handle structured data analysis
  const handleStructuredAnalysis = async () => {
    if (!selectedFileId || !selectedParsedFileId) {
      setError('Please select a file and parsed file first');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const result = await insightsAPIManager.analyzeStructuredData(
        selectedParsedFileId,
        {
          include_visualizations: true,
          include_tabular_summary: true
        }
      );

      if (result.success) {
        setAnalysisResult(result);
        if (onAnalysisComplete) {
          onAnalysisComplete(result);
        }
      } else {
        setError(result.error || 'Structured analysis failed');
      }
    } catch (err) {
      console.error('[BusinessAnalysisSection] Structured analysis error:', err);
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  // Handle unstructured data analysis
  const handleUnstructuredAnalysis = async () => {
    if (!selectedFileId || !selectedParsedFileId) {
      setError('Please select a file and parsed file first');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const result = await insightsAPIManager.analyzeUnstructuredData(
        selectedParsedFileId,
        {
          include_visualizations: true,
          include_tabular_summary: true,
          aar_specific_analysis: aarMode
        }
      );

      if (result.success) {
        setAnalysisResult(result);
        if (onAnalysisComplete) {
          onAnalysisComplete(result);
        }
      } else {
        setError(result.error || 'Unstructured analysis failed');
      }
    } catch (err) {
      console.error('[BusinessAnalysisSection] Unstructured analysis error:', err);
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* File Selection */}
      <InsightsFileSelector
        onSourceSelected={handleFileSelected}
        contentType={analysisType}
        selectedSourceId={selectedFileId}
        selectedSourceType={selectedSourceType}
      />

      {/* Parsed File Selection */}
      {selectedFileId && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Select Parsed File</CardTitle>
            <CardDescription>
              Choose which parsed file to analyze
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Select
              value={selectedParsedFileId}
              onValueChange={setSelectedParsedFileId}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select parsed file" />
              </SelectTrigger>
              <SelectContent>
                {(() => {
                  const parsedFiles = state.realm.content.parsedFiles || [];
                  const fileParsedFiles = parsedFiles.filter((pf: any) => 
                    pf.file_id === selectedFileId || pf.source_file_id === selectedFileId
                  );
                  return fileParsedFiles.map((pf: any) => (
                    <SelectItem key={pf.parsed_file_id || pf.id} value={pf.parsed_file_id || pf.id}>
                      {pf.ui_name || pf.filename || 'Parsed File'}
                    </SelectItem>
                  ));
                })()}
              </SelectContent>
            </Select>
          </CardContent>
        </Card>
      )}

      {/* Analysis Type Tabs */}
      {selectedParsedFileId && (
        <Tabs value={analysisType} onValueChange={(v) => setAnalysisType(v as 'structured' | 'unstructured')}>
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="structured">
              <Database className="h-4 w-4 mr-2" />
              Structured Data
            </TabsTrigger>
            <TabsTrigger value="unstructured">
              <FileText className="h-4 w-4 mr-2" />
              Unstructured Data
            </TabsTrigger>
          </TabsList>

          {/* Structured Analysis Tab */}
          <TabsContent value="structured" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Structured Data Analysis</CardTitle>
                <CardDescription>
                  Generate insights from structured data such as CSV files, Excel spreadsheets, databases, 
                  and tabular formats. Get visual charts, statistical summaries, and business narratives.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button
                  onClick={handleStructuredAnalysis}
                  disabled={!selectedParsedFileId || loading}
                  size="lg"
                  className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                >
                  <Sparkles className="h-5 w-5 mr-2" />
                  {loading ? 'Analyzing...' : 'Analyze Structured Data'}
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Unstructured Analysis Tab */}
          <TabsContent value="unstructured" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Unstructured Data Analysis</CardTitle>
                <CardDescription>
                  Generate insights from unstructured content such as text documents, PDFs, reports, 
                  and emails. Enable AAR mode for specialized Navy after-action report analysis.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* AAR Mode Toggle */}
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-center space-x-3">
                    <Checkbox
                      id="aar-mode"
                      checked={aarMode}
                      onCheckedChange={(checked) => setAarMode(checked === true)}
                    />
                    <div className="flex-1">
                      <label
                        htmlFor="aar-mode"
                        className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer flex items-center gap-2"
                      >
                        <Target className="h-4 w-4 text-blue-600" />
                        Navy AAR (After Action Report) Mode
                      </label>
                      <p className="text-xs text-gray-600 mt-1">
                        Enable specialized analysis for after-action reports including lessons learned, 
                        risk assessment, recommendations, and timeline extraction
                      </p>
                    </div>
                  </div>
                </div>

                <Button
                  onClick={handleUnstructuredAnalysis}
                  disabled={!selectedParsedFileId || loading}
                  size="lg"
                  className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                >
                  <Sparkles className="h-5 w-5 mr-2" />
                  {loading ? 'Analyzing...' : aarMode ? 'Analyze AAR' : 'Analyze Unstructured Data'}
                </Button>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-red-900">Analysis Error</p>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* Results Display */}
      {analysisResult && analysisResult.analysis && (
        <div className="space-y-6">
          {/* Summary Display */}
          <InsightsSummaryDisplay
            summary={analysisResult.analysis.summary}
            loading={loading}
            defaultTab="text"
          />

          {/* Insights List */}
          {analysisResult.analysis.insights && analysisResult.analysis.insights.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Key Insights ({analysisResult.analysis.insights.length})</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {analysisResult.analysis.insights.map((insight, idx) => (
                    <div
                      key={idx}
                      className="bg-purple-50 p-4 rounded-lg border border-purple-100"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <Badge variant="secondary" className="mb-2">
                            {insight.type}
                          </Badge>
                          <p className="text-sm text-gray-900">{insight.description}</p>
                        </div>
                        {insight.confidence !== undefined && (
                          <div className="text-xs text-gray-500 ml-4">
                            {Math.round(insight.confidence * 100)}% confidence
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Visualizations */}
          {analysisResult.analysis.visualizations && analysisResult.analysis.visualizations.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Visualizations</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  {analysisResult.analysis.visualizations.map((viz, idx) => (
                    <div key={idx} className="border rounded-lg p-4">
                      <p className="text-sm font-medium mb-2">{viz.type}</p>
                      {viz.url && (
                        <img src={viz.url} alt={viz.type} className="w-full h-auto rounded" />
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Deep Dive Agent Integration */}
          {analysisResult.analysis.deep_dive && analysisResult.analysis.deep_dive.initiated && (
            <Card>
              <CardHeader>
                <CardTitle>Deep Dive Analysis</CardTitle>
                <CardDescription>
                  Agent session initiated for deeper analysis
                </CardDescription>
              </CardHeader>
              <CardContent>
                {analysisResult.analysis.deep_dive.session_id && (
                  <p className="text-sm text-gray-600">
                    Session ID: {analysisResult.analysis.deep_dive.session_id}
                  </p>
                )}
              </CardContent>
            </Card>
          )}

          {/* AAR Analysis (if applicable) */}
          {analysisType === 'unstructured' && aarMode && analysisResult.analysis.metadata?.aar_analysis && (
            <AARAnalysisSection
              aarAnalysis={analysisResult.analysis.metadata.aar_analysis}
              defaultExpanded={true}
            />
          )}
        </div>
      )}
    </div>
  );
}
