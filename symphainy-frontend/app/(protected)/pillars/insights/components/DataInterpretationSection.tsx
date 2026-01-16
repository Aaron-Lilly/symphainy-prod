/**
 * Data Interpretation Section
 * 
 * Supports both self-discovery and guided discovery interpretation modes.
 * 
 * Self-discovery: Automatically discovers entities and relationships from parsed data
 * Guided discovery: Uses a guide (schema/template) to interpret data with matching
 */

"use client";

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { AlertCircle, Eye, BookOpen, Sparkles, RefreshCw } from 'lucide-react';
import { InsightsFileSelector } from './InsightsFileSelector';
import { useInsightsAPIManager, InterpretationResponse } from '@/shared/managers/InsightsAPIManager';
import { usePlatformState } from '@/shared/state/PlatformStateProvider';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface DataInterpretationSectionProps {
  onInterpretationComplete?: (interpretation: InterpretationResponse) => void;
}

export function DataInterpretationSection({ 
  onInterpretationComplete 
}: DataInterpretationSectionProps) {
  const { state } = usePlatformState();
  const insightsAPIManager = useInsightsAPIManager();

  const [selectedFileId, setSelectedFileId] = useState<string>('');
  const [selectedParsedFileId, setSelectedParsedFileId] = useState<string>('');
  const [selectedSourceType, setSelectedSourceType] = useState<'file' | 'content_metadata'>('file');
  const [interpretationMode, setInterpretationMode] = useState<'self_discovery' | 'guided'>('self_discovery');
  const [selectedGuideId, setSelectedGuideId] = useState<string>('');
  const [interpretationResult, setInterpretationResult] = useState<InterpretationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Available guides (would come from a guides service/API)
  const [availableGuides, setAvailableGuides] = useState<Array<{id: string; name: string; description?: string}>>([]);

  const handleFileSelected = (
    fileId: string, 
    sourceType: 'file' | 'content_metadata',
    contentType: 'structured' | 'unstructured'
  ) => {
    setSelectedFileId(fileId);
    setSelectedSourceType(sourceType);
    setSelectedParsedFileId('');
    setSelectedGuideId('');
    setInterpretationResult(null);
    setError(null);
    
    // Load parsed files for this file
    loadParsedFiles(fileId);
    
    // Load available guides
    loadAvailableGuides();
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

  // Load available guides (placeholder - would come from a guides service)
  const loadAvailableGuides = async () => {
    // TODO: Load guides from a guides service/API
    // For now, use placeholder data
    setAvailableGuides([
      { id: 'guide_1', name: 'Standard Schema Template', description: 'Common data structure template' },
      { id: 'guide_2', name: 'Custom Business Model', description: 'Company-specific data model' },
    ]);
  };

  // Handle self-discovery interpretation
  const handleSelfDiscovery = async () => {
    if (!selectedFileId || !selectedParsedFileId) {
      setError('Please select a file and parsed file first');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const result = await insightsAPIManager.interpretDataSelfDiscovery(
        selectedParsedFileId,
        {
          include_confidence_scores: true,
          include_coverage_analysis: true
        }
      );

      if (result.success) {
        setInterpretationResult(result);
        if (onInterpretationComplete) {
          onInterpretationComplete(result);
        }
      } else {
        setError(result.error || 'Self-discovery interpretation failed');
      }
    } catch (err) {
      console.error('[DataInterpretationSection] Self-discovery error:', err);
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  // Handle guided discovery interpretation
  const handleGuidedDiscovery = async () => {
    if (!selectedFileId || !selectedParsedFileId) {
      setError('Please select a file and parsed file first');
      return;
    }

    if (!selectedGuideId) {
      setError('Please select a guide for guided discovery');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const result = await insightsAPIManager.interpretDataGuided(
        selectedParsedFileId,
        selectedGuideId,
        {
          matching_threshold: 0.7,
          include_confidence_scores: true
        }
      );

      if (result.success) {
        setInterpretationResult(result);
        if (onInterpretationComplete) {
          onInterpretationComplete(result);
        }
      } else {
        setError(result.error || 'Guided discovery interpretation failed');
      }
    } catch (err) {
      console.error('[DataInterpretationSection] Guided discovery error:', err);
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  const renderInterpretationResults = () => {
    if (!interpretationResult || !interpretationResult.interpretation) return null;

    const interpretation = interpretationResult.interpretation;

    return (
      <div className="space-y-6 mt-6">
        {/* Interpretation Summary */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Eye className="h-5 w-5" />
              Interpretation Results
            </CardTitle>
            <CardDescription>
              {interpretation.interpretation_type === 'self_discovery' 
                ? 'Automatically discovered entities and relationships'
                : 'Guided interpretation using selected guide'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4 mb-4">
              {interpretation.confidence_score !== undefined && (
                <div>
                  <p className="text-sm font-medium text-gray-700">Confidence Score</p>
                  <p className="text-2xl font-bold">{Math.round(interpretation.confidence_score * 100)}%</p>
                </div>
              )}
              {interpretation.coverage_score !== undefined && (
                <div>
                  <p className="text-sm font-medium text-gray-700">Coverage Score</p>
                  <p className="text-2xl font-bold">{Math.round(interpretation.coverage_score * 100)}%</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Entities */}
        {interpretation.entities && interpretation.entities.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Discovered Entities ({interpretation.entities.length})</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {interpretation.entities.map((entity, idx) => (
                  <div key={idx} className="p-3 border rounded-lg">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <Badge variant="secondary">{entity.type}</Badge>
                          <span className="font-semibold">{entity.name}</span>
                        </div>
                        {entity.attributes && Object.keys(entity.attributes).length > 0 && (
                          <div className="mt-2 space-y-1">
                            {Object.entries(entity.attributes).slice(0, 3).map(([key, value]) => (
                              <div key={key} className="text-sm text-gray-600">
                                <span className="font-medium">{key}:</span> {String(value)}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Relationships */}
        {interpretation.relationships && interpretation.relationships.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Discovered Relationships ({interpretation.relationships.length})</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {interpretation.relationships.map((rel, idx) => (
                  <div key={idx} className="p-3 border rounded-lg">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold">{rel.source}</span>
                      <Badge variant="outline">{rel.type}</Badge>
                      <span className="font-semibold">{rel.target}</span>
                    </div>
                    {rel.attributes && Object.keys(rel.attributes).length > 0 && (
                      <div className="mt-2 space-y-1">
                        {Object.entries(rel.attributes).slice(0, 3).map(([key, value]) => (
                          <div key={key} className="text-sm text-gray-600">
                            <span className="font-medium">{key}:</span> {String(value)}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* File Selection */}
      <InsightsFileSelector
        onSourceSelected={handleFileSelected}
        contentType="structured"
        selectedSourceId={selectedFileId}
        selectedSourceType={selectedSourceType}
      />

      {/* Parsed File Selection */}
      {selectedFileId && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Select Parsed File</CardTitle>
            <CardDescription>
              Choose which parsed file to interpret
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

      {/* Interpretation Mode Tabs */}
      {selectedParsedFileId && (
        <Tabs value={interpretationMode} onValueChange={(v) => setInterpretationMode(v as 'self_discovery' | 'guided')}>
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="self_discovery">
              <Sparkles className="h-4 w-4 mr-2" />
              Self-Discovery
            </TabsTrigger>
            <TabsTrigger value="guided">
              <BookOpen className="h-4 w-4 mr-2" />
              Guided Discovery
            </TabsTrigger>
          </TabsList>

          {/* Self-Discovery Tab */}
          <TabsContent value="self_discovery" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Self-Discovery Interpretation</CardTitle>
                <CardDescription>
                  Automatically discover entities and relationships from your parsed data without requiring a guide.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button
                  onClick={handleSelfDiscovery}
                  disabled={!selectedParsedFileId || loading}
                  size="lg"
                  className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                >
                  <Sparkles className="h-5 w-5 mr-2" />
                  {loading ? 'Discovering...' : 'Start Self-Discovery'}
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Guided Discovery Tab */}
          <TabsContent value="guided" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Guided Discovery Interpretation</CardTitle>
                <CardDescription>
                  Use a guide (schema or template) to interpret your data with structured matching.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">Select Guide</label>
                  <Select
                    value={selectedGuideId}
                    onValueChange={setSelectedGuideId}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Choose a guide for interpretation" />
                    </SelectTrigger>
                    <SelectContent>
                      {availableGuides.map((guide) => (
                        <SelectItem key={guide.id} value={guide.id}>
                          <div className="flex flex-col">
                            <span className="font-medium">{guide.name}</span>
                            {guide.description && (
                              <span className="text-xs text-gray-500">{guide.description}</span>
                            )}
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <Button
                  onClick={handleGuidedDiscovery}
                  disabled={!selectedParsedFileId || !selectedGuideId || loading}
                  size="lg"
                  className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
                >
                  <BookOpen className="h-5 w-5 mr-2" />
                  {loading ? 'Interpreting...' : 'Start Guided Discovery'}
                </Button>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}

      {/* Error Display */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-2 text-red-800">
          <AlertCircle className="h-5 w-5" />
          <span>{error}</span>
        </div>
      )}

      {/* Interpretation Results */}
      {interpretationResult && renderInterpretationResults()}
    </div>
  );
}
