"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { AlertCircle, RefreshCw, Network, FileText } from 'lucide-react';
import { usePlatformState } from '@/shared/state/PlatformStateProvider';
import { useInsightsAPIManager } from '@/shared/hooks/useInsightsAPIManager';
import { InsightsFileSelector } from './InsightsFileSelector';
import { RelationshipGraph } from './RelationshipGraph';

interface RelationshipMappingProps {
  onMappingComplete?: (result: any) => void;
}

/**
 * ✅ PHASE 4.3: Relationship Mapping Component
 * 
 * Interactive relationship mapping that:
 * - Shows entity-relationship graphs
 * - Allows relationship exploration
 * - Displays relationship metadata
 * - Shows relationship types and confidence scores
 */
export function RelationshipMapping({ onMappingComplete }: RelationshipMappingProps) {
  const { state } = usePlatformState();
  const insightsAPIManager = useInsightsAPIManager();

  const [selectedFileId, setSelectedFileId] = useState<string>('');
  const [sourceType, setSourceType] = useState<'file' | 'content_metadata'>('file');
  const [mappingResult, setMappingResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Handle file selection
  const handleFileSelected = (
    fileId: string,
    sourceType: 'file' | 'content_metadata',
    contentType: 'structured' | 'unstructured'
  ) => {
    setSelectedFileId(fileId);
    setSourceType(sourceType);
    setMappingResult(null);
    setError(null);
  };

  // Generate relationship mapping
  const handleMapRelationships = useCallback(async () => {
    if (!selectedFileId) {
      setError('Please select a file first');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Use map_relationships intent
      const result = await insightsAPIManager.mapRelationships(selectedFileId);

      if (result.success && result.relationships) {
        setMappingResult(result);
        
        if (onMappingComplete) {
          onMappingComplete(result);
        }
      } else {
        setError(result.error || 'Failed to map relationships');
      }
    } catch (err) {
      console.error('[RelationshipMapping] Error mapping relationships:', err);
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  }, [selectedFileId, insightsAPIManager, onMappingComplete]);

  // Auto-map when file is selected (optional - can be user-initiated)
  useEffect(() => {
    // For now, require explicit user action
    // if (selectedFileId && !mappingResult) {
    //   handleMapRelationships();
    // }
  }, [selectedFileId, mappingResult, handleMapRelationships]);

  // Get mapping from state if available
  useEffect(() => {
    if (selectedFileId) {
      const mappings = state.realm.insights.relationshipMappings || {};
      if (mappings[selectedFileId]) {
        const mapping = mappings[selectedFileId];
        setMappingResult({ success: true, relationships: mapping });
      }
    }
  }, [selectedFileId, state.realm.insights.relationshipMappings]);

  return (
    <div className="space-y-6">
      {/* File Selector */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Select File for Relationship Mapping
          </CardTitle>
          <CardDescription>
            Choose a file to visualize entity relationships and connections.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <InsightsFileSelector
            onSourceSelected={handleFileSelected}
            contentType="structured"
          />
        </CardContent>
      </Card>

      {/* Mapping Action */}
      {selectedFileId && !mappingResult && (
        <Card>
          <CardContent className="pt-6">
            <Button
              onClick={handleMapRelationships}
              disabled={loading || !selectedFileId}
              className="w-full bg-purple-600 hover:bg-purple-700"
            >
              {loading ? (
                <>
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  Mapping Relationships...
                </>
              ) : (
                <>
                  <Network className="h-4 w-4 mr-2" />
                  Map Relationships
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Error Display */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-red-600" />
              <p className="text-sm text-red-600">{error}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Loading State */}
      {loading && (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-gray-400" />
                <p className="text-sm text-gray-600">Analyzing relationships...</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Relationship Graph Visualization */}
      {mappingResult?.relationships && (
        <div className="space-y-6">
          <RelationshipGraph relationships={mappingResult.relationships} />
          
          {/* Relationship Metadata */}
          <Card>
            <CardHeader>
              <CardTitle>Relationship Metadata</CardTitle>
              <CardDescription>
                Details about discovered relationships
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                  <p className="text-xs font-medium text-blue-700 mb-1">Total Entities</p>
                  <p className="text-2xl font-bold text-blue-900">
                    {mappingResult.relationships.entities?.length || 0}
                  </p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                  <p className="text-xs font-medium text-green-700 mb-1">Total Relationships</p>
                  <p className="text-2xl font-bold text-green-900">
                    {mappingResult.relationships.relationships?.length || 0}
                  </p>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                  <p className="text-xs font-medium text-purple-700 mb-1">Relationship Types</p>
                  <p className="text-2xl font-bold text-purple-900">
                    {new Set(mappingResult.relationships.relationships?.map((r: any) => r.type) || []).size}
                  </p>
                </div>
              </div>

              {/* Relationship Types */}
              {mappingResult.relationships.relationships && (
                <div className="mt-6">
                  <p className="text-sm font-semibold text-gray-800 mb-3">Relationship Types</p>
                  <div className="flex flex-wrap gap-2">
                    {Array.from(new Set(mappingResult.relationships.relationships.map((r: any) => r.type))).map((type: string) => (
                      <Badge key={type} variant="secondary">
                        {type}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Empty State */}
      {!selectedFileId && !loading && (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <Network className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <p className="text-sm text-gray-600">Select a file to visualize relationships.</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
