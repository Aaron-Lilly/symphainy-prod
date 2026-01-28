/**
 * DataMappingSection Component
 * 
 * Complete section for data mapping operations
 * Supports both unstructured→structured and structured→structured mapping
 * Includes file selection, mapping options, execution, and results display
 */

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Sparkles, AlertCircle, ArrowRight, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { InsightsFileSelector } from './InsightsFileSelector';
import { MappingResultsDisplay } from './MappingResultsDisplay';
// ✅ PHASE 4: Removed InsightsService import - using intent-based API
import { DataMappingResponse, DataMappingResultsResponse, DataMappingOptions } from '@/shared/services/insights/types';
// ✅ PHASE 4: Session-First - Use SessionBoundary for session state
import { useSessionBoundary } from '@/shared/state/SessionBoundaryProvider';
import { usePlatformState } from '@/shared/state/PlatformStateProvider';

interface DataMappingSectionProps {
  onMappingComplete?: (mapping: DataMappingResultsResponse) => void;
}

export function DataMappingSection({ 
  onMappingComplete 
}: DataMappingSectionProps) {
  // ✅ PHASE 4: Session-First - Use SessionBoundary for session state
  const { state: sessionState } = useSessionBoundary();
  const { submitIntent, getExecutionStatus } = usePlatformState();
  const [sourceFileId, setSourceFileId] = useState<string>('');
  const [targetFileId, setTargetFileId] = useState<string>('');
  const [mappingType, setMappingType] = useState<'auto' | 'unstructured_to_structured' | 'structured_to_structured'>('auto');
  const [qualityValidation, setQualityValidation] = useState<boolean>(false);
  const [minConfidence, setMinConfidence] = useState<number>(0.8);
  const [includeCitations, setIncludeCitations] = useState<boolean>(true);
  
  const [mappingResult, setMappingResult] = useState<DataMappingResultsResponse | null>(null);
  const [mappingId, setMappingId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<'idle' | 'mapping' | 'completed' | 'failed'>('idle');

  const handleSourceSelected = (
    sourceId: string, 
    sourceType: 'file' | 'content_metadata',
    contentType: 'structured' | 'unstructured'
  ) => {
    setSourceFileId(sourceId);
    // Clear previous results
    setMappingResult(null);
    setMappingId(null);
    setError(null);
    setStatus('idle');
  };

  const handleTargetSelected = (
    targetId: string, 
    targetType: 'file' | 'content_metadata',
    contentType: 'structured' | 'unstructured'
  ) => {
    setTargetFileId(targetId);
    // Clear previous results
    setMappingResult(null);
    setMappingId(null);
    setError(null);
    setStatus('idle');
  };

  const handleExecuteMapping = async () => {
    if (!sourceFileId || !targetFileId) {
      setError('Please select both source and target files');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setStatus('mapping');

      // ✅ PHASE 4: Migrate to intent-based API
      // NOTE: Data mapping (file-to-file) doesn't have a direct intent mapping yet
      // map_relationships intent is for relationships within a parsed file, not file-to-file mapping
      // TODO: Need to determine if this should be:
      // 1. New intent: `map_data` or `execute_data_mapping`
      // 2. Use artifact retrieval if mapping results are stored as artifacts
      // 3. Use a different pattern
      
      if (!sessionState.sessionId || !sessionState.tenantId) {
        throw new Error("Session required to execute data mapping");
      }

      // Submit intent (will work when backend implements `map_data` intent)
      // TODO: Backend needs to implement `map_data` intent for file-to-file mapping
      const executionId = await submitIntent(
        'map_data', // New intent needed - see PHASE_4_MIGRATION_GAPS.md
        {
          source_file_id: sourceFileId,
          target_file_id: targetFileId,
          mapping_type: mappingType,
          quality_validation: qualityValidation,
          min_confidence: minConfidence,
          include_citations: includeCitations
        }
      );

      // Wait for execution to complete
      const maxAttempts = 30;
      let attempts = 0;
      let mappingResult: any = null;

      while (attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 500));
        
        const status = await getExecutionStatus(executionId);
        
        if (status?.status === "completed") {
          // Extract mapping result from execution artifacts
          const mappingArtifact = status.artifacts?.mapping || status.artifacts?.relationships;
          if (mappingArtifact?.semantic_payload) {
            mappingResult = mappingArtifact.semantic_payload;
          }
          break;
        } else if (status?.status === "failed") {
          throw new Error(status.error || "Data mapping failed");
        }
        
        attempts++;
      }

      if (!mappingResult) {
        throw new Error("Mapping result not found in execution result");
      }

      // Transform to DataMappingResponse format
      // Use mappingResult if it contains full response, otherwise construct minimal response
      const response: DataMappingResponse = {
        success: true,
        mapping_id: mappingResult.mapping_id || executionId,
        mapping_type: mappingResult.mapping_type || mappingType,
        mapping_rules: mappingResult.mapping_rules || [],
        mapped_data: mappingResult.mapped_data || { success: true },
        metadata: mappingResult.metadata || {
          source_file_id: sourceFileId,
          target_file_id: targetFileId,
          mapping_timestamp: new Date().toISOString()
        },
        mapping_result: mappingResult
      };

      setMappingId(response.mapping_id);
      setMappingResult(response);
      setStatus('completed');
      if (onMappingComplete) {
        onMappingComplete(response);
      }
    } catch (err) {
      console.error('Mapping error:', err);
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
      setStatus('failed');
    } finally {
      setLoading(false);
    }
  };

  // Auto-detect mapping type based on file selections
  const canExecute = sourceFileId && targetFileId && !loading;
  const isStructuredToStructured = mappingType === 'structured_to_structured';

  return (
    <div className="space-y-6">
      {/* File Selection */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Source File */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Source File</CardTitle>
            <CardDescription>
              Select the source file to map from (e.g., license PDF, legacy policy records)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <InsightsFileSelector
              onSourceSelected={handleSourceSelected}
              contentType="unstructured" // Can be either, but defaulting to unstructured for mapping
              selectedSourceId={sourceFileId}
              selectedSourceType="file"
            />
          </CardContent>
        </Card>

        {/* Target File */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Target File</CardTitle>
            <CardDescription>
              Select the target file/data model to map to (e.g., Excel template, new data model)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <InsightsFileSelector
              onSourceSelected={handleTargetSelected}
              contentType="structured" // Target is typically structured
              selectedSourceId={targetFileId}
              selectedSourceType="file"
            />
          </CardContent>
        </Card>
      </div>

      {/* Mapping Options */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Mapping Options</CardTitle>
          <CardDescription>
            Configure how the mapping should be performed
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Mapping Type */}
          <div className="space-y-3">
            <label className="text-sm font-medium">Mapping Type</label>
            <Select
              value={mappingType}
              onValueChange={(value) => setMappingType(value as typeof mappingType)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select mapping type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="auto">Auto-detect (recommended)</SelectItem>
                <SelectItem value="unstructured_to_structured">
                  Unstructured → Structured (e.g., PDF to Excel)
                </SelectItem>
                <SelectItem value="structured_to_structured">
                  Structured → Structured (e.g., Legacy records to new model)
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Quality Validation (only for structured→structured) */}
          {isStructuredToStructured && (
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="quality-validation"
                checked={qualityValidation}
                onChange={(e) => setQualityValidation(e.target.checked)}
                className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <label htmlFor="quality-validation" className="text-sm font-normal cursor-pointer">
                Enable Quality Validation
                <span className="text-xs text-gray-500 ml-2">
                  (Validates data quality and generates cleanup actions)
                </span>
              </label>
            </div>
          )}

          {/* Minimum Confidence */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium">
                Minimum Confidence: {Math.round(minConfidence * 100)}%
              </label>
              <span className="text-xs text-gray-500">
                Only include mappings above this threshold
              </span>
            </div>
            <div className="flex items-center gap-3">
              <Input
                type="range"
                min="0.5"
                max="1.0"
                step="0.05"
                value={minConfidence}
                onChange={(e) => setMinConfidence(parseFloat(e.target.value))}
                className="flex-1"
              />
              <span className="text-sm text-gray-600 w-12 text-right">
                {Math.round(minConfidence * 100)}%
              </span>
            </div>
          </div>

          {/* Include Citations */}
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="include-citations"
              checked={includeCitations}
              onChange={(e) => setIncludeCitations(e.target.checked)}
              className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <label htmlFor="include-citations" className="text-sm font-normal cursor-pointer">
              Include Citations
              <span className="text-xs text-gray-500 ml-2">
                (Show source location for each mapped field)
              </span>
            </label>
          </div>
        </CardContent>
      </Card>

      {/* Execute Button */}
      <div className="flex items-center gap-4">
        <Button
          onClick={handleExecuteMapping}
          disabled={!canExecute || loading}
          size="lg"
          className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
        >
          {loading ? (
            <>
              <Loader2 className="h-5 w-5 mr-2 animate-spin" />
              Mapping...
            </>
          ) : (
            <>
              <Sparkles className="h-5 w-5 mr-2" />
              Execute Mapping
            </>
          )}
        </Button>

        {canExecute && !loading && (
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <ArrowRight className="h-4 w-4" />
            <span>Ready to map from source to target</span>
          </div>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-red-900">Mapping Error</p>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* Results Display */}
      {mappingResult && (
        <MappingResultsDisplay
          mappingResults={mappingResult}
          onExport={(format) => {
            // Handle export
            // ✅ PHASE 4: Export mapping results - TODO: Migrate to artifact export API
            // Note: Export functionality may need artifact export API or specific intent
            if (mappingId) {
              // TODO: Implement artifact export when available
              toast.error("Export not yet available", {
                description: "Mapping results export needs migration to artifact export API"
              });
              /* Future implementation:
              const exportUrl = await getArtifactExportUrl(mappingId, format);
              // Download file
              fetch(exportUrl)
                .then(blob => {
                  const url = window.URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `mapping-results.${format}`;
                  a.click();
                  window.URL.revokeObjectURL(url);
                })
                .catch(err => {
                  console.error('Export error:', err);
                  setError('Failed to export mapping results');
                });
              */
            }
          }}
        />
      )}
    </div>
  );
}

