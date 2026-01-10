/**
 * Enhanced File Processor Core
 * Core component for enhanced file processing with metadata extraction
 */

import React from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { FileText, Database, GitBranch, BarChart3, Download } from 'lucide-react';
import { EnhancedFileProcessorProps } from './types';
import { useEnhancedFileProcessor } from './hooks';

export function EnhancedFileProcessor({ 
  file, 
  onProcessingComplete, 
  onError,
  className 
}: EnhancedFileProcessorProps) {
  const {
    processingState,
    metadata,
    lineage,
    startProcessing,
    downloadMetadata,
    downloadFile
  } = useEnhancedFileProcessor(file, onProcessingComplete, onError);

  return (
    <div className={`space-y-6 ${className || ''}`}>
      {/* Processing Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Enhanced File Processing
          </CardTitle>
        </CardHeader>
        <CardContent>
          {!processingState.isProcessing && !processingState.isComplete && (
            <div className="text-center space-y-4">
              <p className="text-sm text-gray-600">
                Process this file with enhanced metadata extraction and lineage tracking?
              </p>
              <Button onClick={startProcessing} className="w-full">
                Extract Metadata & Process
              </Button>
            </div>
          )}

          {processingState.isProcessing && (
            <div className="text-center space-y-4">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="text-sm text-gray-600">Processing file...</p>
              <p className="text-xs text-gray-500">
                Extracting metadata, analyzing content, and tracking lineage
              </p>
            </div>
          )}

          {processingState.isComplete && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Badge variant="default" className="bg-green-100 text-green-800">
                    ✓ Processing Complete
                  </Badge>
                  <span className="text-sm text-gray-600">
                    {processingState.processingTime}s
                  </span>
                </div>
                <div className="flex gap-2">
                  <Button size="sm" variant="outline" onClick={downloadMetadata}>
                    <Database className="h-4 w-4 mr-1" />
                    Download Metadata
                  </Button>
                  <Button size="sm" variant="outline" onClick={downloadFile}>
                    <Download className="h-4 w-4 mr-1" />
                    Download File
                  </Button>
                </div>
              </div>
            </div>
          )}

          {processingState.error && (
            <div className="text-red-600 text-sm">
              Error: {processingState.error}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Results Display */}
      {processingState.isComplete && metadata && (
        <Tabs defaultValue="metadata" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="metadata">Metadata</TabsTrigger>
            <TabsTrigger value="structure">Structure</TabsTrigger>
            <TabsTrigger value="quality">Quality</TabsTrigger>
            <TabsTrigger value="lineage">Lineage</TabsTrigger>
          </TabsList>
          
          <TabsContent value="metadata" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Database className="h-5 w-5" />
                  Content Metadata
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium">Content Type</label>
                    <p className="text-sm text-gray-600">{metadata.content_type}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Business Domain</label>
                    <p className="text-sm text-gray-600">{metadata.business_context?.domain || 'Unknown'}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="structure" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  Data Structure
                </CardTitle>
              </CardHeader>
              <CardContent>
                {metadata.data_structure?.type === 'tabular' && metadata.data_structure?.tables && (
                  <div className="space-y-4">
                    {metadata.data_structure.tables.map((table: any, index: number) => (
                      <div key={index} className="border rounded-lg p-4">
                        <h4 className="font-medium mb-2">Table {index + 1}</h4>
                        <div className="grid grid-cols-3 gap-4 text-sm">
                          <div>
                            <span className="font-medium">Columns:</span> {table.column_count}
                          </div>
                          <div>
                            <span className="font-medium">Rows:</span> {table.row_count}
                          </div>
                          <div>
                            <span className="font-medium">ID:</span> {table.table_id}
                          </div>
                        </div>
                        <div className="mt-2">
                          <span className="font-medium">Columns:</span>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {table.columns.map((col: string, i: number) => (
                              <Badge key={i} variant="secondary" className="text-xs">
                                {col}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
                {metadata.data_structure?.type === 'unstructured' && (
                  <div className="text-sm text-gray-600">
                    <p>Text Length: {metadata.data_structure.text_length} characters</p>
                    <p>Has Content: {metadata.data_structure.has_text_content ? 'Yes' : 'No'}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="quality" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Data Quality
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium">Completeness</label>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{ width: `${(metadata.data_quality?.completeness_score || 0) * 100}%` }}
                      ></div>
                    </div>
                    <p className="text-xs text-gray-600 mt-1">
                      {Math.round((metadata.data_quality?.completeness_score || 0) * 100)}%
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Overall Quality</label>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-green-600 h-2 rounded-full" 
                        style={{ width: `${(metadata.data_quality?.overall_score || 0) * 100}%` }}
                      ></div>
                    </div>
                    <p className="text-xs text-gray-600 mt-1">
                      {Math.round((metadata.data_quality?.overall_score || 0) * 100)}%
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="lineage" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <GitBranch className="h-5 w-5" />
                  File Lineage
                </CardTitle>
              </CardHeader>
              <CardContent>
                {lineage && lineage.length > 0 ? (
                  <div className="space-y-2">
                    {lineage.map((item: any, index: number) => (
                      <div key={index} className="flex items-center gap-2 p-2 border rounded">
                        <GitBranch className="h-4 w-4 text-gray-400" />
                        <div className="flex-1">
                          <p className="text-sm font-medium">{item.relationship_type}</p>
                          <p className="text-xs text-gray-500">
                            {item.parent_file_id ? `From: ${item.parent_file_id}` : `To: ${item.child_file_id}`}
                          </p>
                        </div>
                        <span className="text-xs text-gray-400">
                          {new Date(item.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-600">No lineage relationships found</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
}




