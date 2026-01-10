'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Database, FileText, Layers, ArrowRight } from 'lucide-react';

interface CorrelationChainProps {
  file_id?: string;
  parsed_file_id?: string;
  content_id?: string;
  correlation_id?: string;
  workflow_id?: string;
}

export default function CorrelationChain({ 
  file_id, 
  parsed_file_id, 
  content_id,
  correlation_id,
  workflow_id 
}: CorrelationChainProps) {
  const hasData = file_id || parsed_file_id || content_id;
  
  if (!hasData) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Correlation Chain</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-500 text-center py-4">
            No correlation data available. Create embeddings to see the data flow.
          </p>
        </CardContent>
      </Card>
    );
  }
  
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm flex items-center gap-2">
          <Layers className="h-4 w-4" />
          Data Correlation Chain
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Correlation IDs */}
          {(correlation_id || workflow_id) && (
            <div className="p-3 bg-gray-50 rounded-lg">
              <div className="text-xs font-medium text-gray-600 mb-2">Correlation IDs</div>
              <div className="flex flex-wrap gap-2">
                {correlation_id && (
                  <Badge variant="outline" className="text-xs">
                    Correlation: {correlation_id.slice(0, 8)}...
                  </Badge>
                )}
                {workflow_id && (
                  <Badge variant="outline" className="text-xs">
                    Workflow: {workflow_id.slice(0, 8)}...
                  </Badge>
                )}
              </div>
            </div>
          )}
          
          {/* Data Flow Chain */}
          <div className="flex items-center gap-2 flex-wrap">
            {file_id && (
              <>
                <div className="flex items-center gap-2 p-3 bg-blue-50 rounded-lg border border-blue-200">
                  <Database className="h-4 w-4 text-blue-600" />
                  <div>
                    <div className="text-xs font-medium text-gray-700">File</div>
                    <div className="text-xs text-gray-500 font-mono">
                      {file_id.slice(0, 8)}...
                    </div>
                  </div>
                </div>
                <ArrowRight className="h-4 w-4 text-gray-400" />
              </>
            )}
            
            {parsed_file_id && (
              <>
                <div className="flex items-center gap-2 p-3 bg-purple-50 rounded-lg border border-purple-200">
                  <FileText className="h-4 w-4 text-purple-600" />
                  <div>
                    <div className="text-xs font-medium text-gray-700">Parsed</div>
                    <div className="text-xs text-gray-500 font-mono">
                      {parsed_file_id.slice(0, 8)}...
                    </div>
                  </div>
                </div>
                <ArrowRight className="h-4 w-4 text-gray-400" />
              </>
            )}
            
            {content_id && (
              <div className="flex items-center gap-2 p-3 bg-green-50 rounded-lg border border-green-200">
                <Layers className="h-4 w-4 text-green-600" />
                <div>
                  <div className="text-xs font-medium text-gray-700">Semantic Layer</div>
                  <div className="text-xs text-gray-500 font-mono">
                    {content_id.slice(0, 8)}...
                  </div>
                </div>
              </div>
            )}
          </div>
          
          {/* Description */}
          <div className="text-xs text-gray-600 bg-blue-50 p-3 rounded-lg border border-blue-100">
            <strong>How it works:</strong> This chain shows how your data flows through the platform. 
            Each step is tracked with correlation IDs, enabling end-to-end traceability from upload → parse → embed → semantic layer.
          </div>
        </div>
      </CardContent>
    </Card>
  );
}







