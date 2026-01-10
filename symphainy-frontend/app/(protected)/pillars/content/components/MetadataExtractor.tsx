"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, FileText, Database, Brain, CheckCircle, AlertCircle, Info } from 'lucide-react';
import { FileSelector } from './FileSelector';
import { FileStatus, FileMetadata } from '@/shared/types/file';

interface ExtractedFileMetadata {
  file_id: string;
  file_name: string;
  file_type: string;
  file_size: number;
  creation_date: string;
  page_count?: number;
  text_length?: number;
}

interface DataSummary {
  schema_compliance: number;
  completeness: number;
  consistency: number;
  data_quality_score: number;
  recommendations: string[];
}

interface SemanticSummary {
  data_domain: string;
  data_purpose: string;
  key_insights: string[];
  business_context: string;
  confidence_score: number;
}

interface Categorization {
  content_type: string;
  domain: string;
  complexity: string;
  confidence_score: number;
}

interface MetadataExtractionResult {
  success: boolean;
  file_id: string;
  extraction_type: string;
  data_summary: DataSummary;
  semantic_summary: SemanticSummary;
  categorization: Categorization;
  metadata: ExtractedFileMetadata;
  extraction_timestamp: string;
  api_version: string;
  endpoint: string;
  error?: string;
}

interface MetadataExtractionProps {
  selectedFile: FileMetadata | null;
  onMetadataExtracted?: (metadata: MetadataExtractionResult) => void;
  onFileSelected?: (file: FileMetadata) => void; // Callback to update parent state
}

export default function MetadataExtractor({ 
  selectedFile: propSelectedFile, 
  onMetadataExtracted,
  onFileSelected 
}: MetadataExtractionProps) {
  const [selectedFileId, setSelectedFileId] = useState<string | null>(null);
  const [selectedFileFromSelector, setSelectedFileFromSelector] = useState<FileMetadata | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [extractionResult, setExtractionResult] = useState<MetadataExtractionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [extractionType, setExtractionType] = useState<string>("comprehensive");

  // Use FileSelector as single source of truth - show only parsed files
  // FileSelector handles loading from FileDashboard's API
  const selectedFile = selectedFileFromSelector || propSelectedFile;

  // Sync with propSelectedFile from parent
  useEffect(() => {
    if (propSelectedFile) {
      const fileId = propSelectedFile.file_id || propSelectedFile.uuid;
      if (fileId) {
        setSelectedFileId(fileId);
        setSelectedFileFromSelector(propSelectedFile);
      }
    }
  }, [propSelectedFile]);

  // Handle file selection from FileSelector
  const handleFileSelected = (fileId: string, file: FileMetadata | null) => {
    setSelectedFileId(fileId);
    setSelectedFileFromSelector(file);
    // Update parent state so button can be enabled
    if (file && onFileSelected) {
      onFileSelected(file);
    }
    // Reset extraction state when file changes
    setExtractionResult(null);
    setError(null);
  };

  const handleExtractMetadata = async () => {
    if (!selectedFile) {
      setError("Please select a file to extract metadata from");
      return;
    }

    setIsLoading(true);
    setError(null);
    setExtractionResult(null);

    try {
      // Real API call to Content Pillar Service
      const fileId = selectedFile.file_id || selectedFile.uuid;
      const response = await fetch(`/api/v1/business_enablement/content/get-file-details/${fileId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Token': sessionStorage.getItem('session_token') || ''
        },
        body: JSON.stringify({
          extraction_type: extractionType,
          options: {}
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result: MetadataExtractionResult = await response.json();
      
      if (result.success) {
        setExtractionResult(result);
        onMetadataExtracted?.(result);
      } else {
        setError(result.error || "Failed to extract metadata");
      }
    } catch (err) {
      console.error('Metadata extraction error:', err);
      setError(err instanceof Error ? err.message : "An unexpected error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  const getQualityColor = (score: number) => {
    if (score >= 0.8) return "text-green-600";
    if (score >= 0.6) return "text-yellow-600";
    return "text-red-600";
  };

  const getQualityBadgeVariant = (score: number) => {
    if (score >= 0.8) return "default";
    if (score >= 0.6) return "secondary";
    return "destructive";
  };

  return (
    <div className="space-y-6" data-testid="content-pillar-metadata-extractor">
      {/* File Selection */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            File Selection
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Select File</label>
              <FileSelector
                value={selectedFileId || undefined}
                onValueChange={handleFileSelected}
                showOnlyParsed={true} // Only show parsed files for metadata extraction
                placeholder="Choose a file to analyze"
                dataTestId="metadata-file-selector"
              />
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Extraction Type</label>
              <Select 
                value={extractionType} 
                onValueChange={setExtractionType}
                data-testid="metadata-extraction-type-selector"
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="basic">Basic Metadata</SelectItem>
                  <SelectItem value="comprehensive">Comprehensive Analysis</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          
          <Button 
            onClick={handleExtractMetadata} 
            disabled={!selectedFile || isLoading}
            className="w-full"
            data-testid="extract-metadata-button"
            aria-label="Extract metadata from selected file"
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Extracting Metadata...
              </>
            ) : (
              <>
                <Brain className="mr-2 h-4 w-4" />
                Extract Content Metadata
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Error Display */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Results Display - Persistent Preview Area */}
      <div className="space-y-6">
        {extractionResult ? (
          <>
          {/* Data Summary Table */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                Data Summary
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Schema Compliance</span>
                    <Badge variant={getQualityBadgeVariant(extractionResult.data_summary.schema_compliance)}>
                      {(extractionResult.data_summary.schema_compliance * 100).toFixed(0)}%
                    </Badge>
                  </div>
                  <Progress value={extractionResult.data_summary.schema_compliance * 100} className="h-2" />
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Completeness</span>
                    <Badge variant={getQualityBadgeVariant(extractionResult.data_summary.completeness)}>
                      {(extractionResult.data_summary.completeness * 100).toFixed(0)}%
                    </Badge>
                  </div>
                  <Progress value={extractionResult.data_summary.completeness * 100} className="h-2" />
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Consistency</span>
                    <Badge variant={getQualityBadgeVariant(extractionResult.data_summary.consistency)}>
                      {(extractionResult.data_summary.consistency * 100).toFixed(0)}%
                    </Badge>
                  </div>
                  <Progress value={extractionResult.data_summary.consistency * 100} className="h-2" />
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Overall Quality</span>
                    <Badge variant={getQualityBadgeVariant(extractionResult.data_summary.data_quality_score)}>
                      {(extractionResult.data_summary.data_quality_score * 100).toFixed(0)}%
                    </Badge>
                  </div>
                  <Progress value={extractionResult.data_summary.data_quality_score * 100} className="h-2" />
                </div>
              </div>
              
              {extractionResult.data_summary.recommendations.length > 0 && (
                <div className="mt-4">
                  <h4 className="text-sm font-medium mb-2">Recommendations</h4>
                  <ul className="space-y-1">
                    {extractionResult.data_summary.recommendations.map((rec, index) => (
                      <li key={index} className="text-sm text-gray-600 flex items-start gap-2">
                        <Info className="h-4 w-4 mt-0.5 flex-shrink-0" />
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Semantic Summary */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5" />
                Semantic Summary
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 className="text-sm font-medium mb-2">Data Domain</h4>
                  <Badge variant="outline" className="text-sm">
                    {extractionResult.semantic_summary.data_domain}
                  </Badge>
                </div>
                <div>
                  <h4 className="text-sm font-medium mb-2">Data Purpose</h4>
                  <Badge variant="outline" className="text-sm">
                    {extractionResult.semantic_summary.data_purpose}
                  </Badge>
                </div>
              </div>
              
              <div>
                <h4 className="text-sm font-medium mb-2">Business Context</h4>
                <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded-md">
                  {extractionResult.semantic_summary.business_context}
                </p>
              </div>
              
              <div>
                <h4 className="text-sm font-medium mb-2">Key Insights</h4>
                <ul className="space-y-1">
                  {extractionResult.semantic_summary.key_insights.map((insight, index) => (
                    <li key={index} className="text-sm text-gray-600 flex items-start gap-2">
                      <CheckCircle className="h-4 w-4 mt-0.5 flex-shrink-0 text-green-500" />
                      {insight}
                    </li>
                  ))}
                </ul>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">Confidence Score</span>
                <Badge variant={getQualityBadgeVariant(extractionResult.semantic_summary.confidence_score)}>
                  {(extractionResult.semantic_summary.confidence_score * 100).toFixed(0)}%
                </Badge>
              </div>
            </CardContent>
          </Card>

          {/* Categorization */}
          <Card>
            <CardHeader>
              <CardTitle>Content Categorization</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <h4 className="text-sm font-medium mb-2">Content Type</h4>
                  <Badge variant="secondary">
                    {extractionResult.categorization.content_type}
                  </Badge>
                </div>
                <div>
                  <h4 className="text-sm font-medium mb-2">Domain</h4>
                  <Badge variant="secondary">
                    {extractionResult.categorization.domain}
                  </Badge>
                </div>
                <div>
                  <h4 className="text-sm font-medium mb-2">Complexity</h4>
                  <Badge variant="secondary">
                    {extractionResult.categorization.complexity}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Metadata Display */}
          <Card>
            <CardHeader>
              <CardTitle>Extracted Metadata</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="bg-gray-50 p-4 rounded-md">
                <pre className="text-sm overflow-x-auto">
                  {JSON.stringify(extractionResult.metadata, null, 2)}
                </pre>
              </div>
            </CardContent>
          </Card>
          </>
        ) : (
          <Card>
            <CardHeader>
              <CardTitle>Metadata Preview</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="relative block w-full rounded-lg border-2 border-dashed p-12 text-center border-gray-300 min-h-[300px] flex items-center justify-center">
                <div className="text-gray-500">
                  {!selectedFile ? (
                    <>
                      <FileText className="mx-auto h-12 w-12 mb-2" />
                      <p className="font-medium">No file selected</p>
                      <p className="text-sm mt-1">Select a file and click "Extract Content Metadata" to see results here</p>
                    </>
                  ) : isLoading ? (
                    <>
                      <Loader2 className="mx-auto h-12 w-12 mb-2 animate-spin text-blue-500" />
                      <p className="font-medium">Extracting metadata...</p>
                      <p className="text-sm mt-1">Please wait while we analyze your file</p>
                    </>
                  ) : (
                    <>
                      <Brain className="mx-auto h-12 w-12 mb-2" />
                      <p className="font-medium">Ready to extract metadata</p>
                      <p className="text-sm mt-1">Click "Extract Content Metadata" to analyze the selected file</p>
                    </>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
