/**
 * Permit Processing Section Component
 * 
 * Complete section for permit processing operations
 * Supports PSO extraction and multi-system mapping
 * Includes file selection, target system configuration, execution, and results display
 */

"use client";

import React, { useState, useEffect } from 'react';
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
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  FileText, 
  AlertCircle, 
  ArrowRight, 
  Loader2,
  CheckCircle,
  XCircle,
  Settings,
  Map
} from 'lucide-react';
import { InsightsFileSelector } from './InsightsFileSelector';
import { InsightsService } from '@/shared/services/insights/core';
import { 
  PermitProcessingResponse,
  TargetSystem,
  PermitProcessingOptions
} from '@/shared/services/insights/types';
import { useAuth } from '@/shared/auth/AuthProvider';
import { usePlatformState } from '@/shared/state/PlatformStateProvider';
import { toast } from 'sonner';

interface PermitProcessingSectionProps {
  onProcessingComplete?: (result: PermitProcessingResponse) => void;
}

export function PermitProcessingSection({ 
  onProcessingComplete 
}: PermitProcessingSectionProps) {
  const { sessionToken } = useAuth();
  const { state } = usePlatformState();
  const guideSessionToken = sessionToken || state.session.sessionId;
  const [permitFileId, setPermitFileId] = useState<string>('');
  const [targetSystems, setTargetSystems] = useState<TargetSystem[]>([]);
  const [processingOptions, setProcessingOptions] = useState<PermitProcessingOptions>({
    include_citations: true,
    validation_level: 'moderate'
  });
  
  const [processingResult, setProcessingResult] = useState<PermitProcessingResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<'idle' | 'processing' | 'completed' | 'failed'>('idle');
  const [progress, setProgress] = useState(0);

  // Available target systems
  const availableSystems: Array<{ value: string; label: string }> = [
    { value: 'compliance', label: 'Compliance System' },
    { value: 'task_management', label: 'Task Management' },
    { value: 'environmental', label: 'Environmental Monitoring' },
    { value: 'erp', label: 'ERP System' }
  ];

  const handlePermitFileSelected = (
    fileId: string,
    fileType: 'file' | 'content_metadata',
    contentType: 'structured' | 'unstructured'
  ) => {
    setPermitFileId(fileId);
    setProcessingResult(null);
    setError(null);
    setStatus('idle');
  };

  const handleAddTargetSystem = () => {
    setTargetSystems([...targetSystems, { system: 'compliance', target_file_id: '' }]);
  };

  const handleRemoveTargetSystem = (index: number) => {
    setTargetSystems(targetSystems.filter((_, i) => i !== index));
  };

  const handleTargetSystemChange = (index: number, field: 'system' | 'target_file_id', value: string) => {
    const updated = [...targetSystems];
    updated[index] = { ...updated[index], [field]: value };
    setTargetSystems(updated);
  };

  const handleExecuteProcessing = async () => {
    if (!permitFileId) {
      setError('Please select a permit file');
      return;
    }

    if (targetSystems.length === 0) {
      setError('Please add at least one target system');
      return;
    }

    // Validate all target systems have target_file_id
    const invalidSystems = targetSystems.filter(ts => !ts.target_file_id);
    if (invalidSystems.length > 0) {
      setError('Please provide target file IDs for all target systems');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setStatus('processing');
      setProgress(0);

      const insightsService = new InsightsService(guideSessionToken);
      
      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 500);

      const response: PermitProcessingResponse = await insightsService.executePermitProcessing(
        permitFileId,
        targetSystems,
        processingOptions,
        guideSessionToken
      );

      clearInterval(progressInterval);
      setProgress(100);

      if (response.success) {
        setProcessingResult(response);
        setStatus('completed');
        toast.success('Permit processing completed successfully');
        if (onProcessingComplete) {
          onProcessingComplete(response);
        }
      } else {
        setError(response.error || 'Permit processing failed');
        setStatus('failed');
        toast.error('Permit processing failed');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to execute permit processing');
      setStatus('failed');
      toast.error('Permit processing failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Permit Processing
          </CardTitle>
          <CardDescription>
            Extract Permit Semantic Objects (PSO) from permit documents and map to target systems
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Permit File Selection */}
          <div className="space-y-2">
            <Label>Permit File</Label>
            <InsightsFileSelector
              onSourceSelected={handlePermitFileSelected}
              selectedSourceId={permitFileId}
              contentType="unstructured"
            />
          </div>

          {/* Target Systems Configuration */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <Label>Target Systems</Label>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={handleAddTargetSystem}
              >
                Add System
              </Button>
            </div>
            
            {targetSystems.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                No target systems configured. Click "Add System" to add one.
              </p>
            ) : (
              <div className="space-y-3">
                {targetSystems.map((targetSystem, index) => (
                  <div key={index} className="flex items-center gap-3 p-3 border rounded-lg">
                    <Select
                      value={targetSystem.system}
                      onValueChange={(value) => handleTargetSystemChange(index, 'system', value)}
                    >
                      <SelectTrigger className="w-48">
                        <SelectValue placeholder="Select system" />
                      </SelectTrigger>
                      <SelectContent>
                        {availableSystems.map((sys) => (
                          <SelectItem key={sys.value} value={sys.value}>
                            {sys.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <Input
                      placeholder="Target file ID"
                      value={targetSystem.target_file_id}
                      onChange={(e) => handleTargetSystemChange(index, 'target_file_id', e.target.value)}
                      className="flex-1"
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => handleRemoveTargetSystem(index)}
                    >
                      Remove
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Processing Options */}
          <div className="space-y-4">
            <Label>Processing Options</Label>
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="include_citations"
                  checked={processingOptions.include_citations}
                  onCheckedChange={(checked) =>
                    setProcessingOptions({ ...processingOptions, include_citations: checked as boolean })
                  }
                />
                <Label htmlFor="include_citations" className="font-normal">
                  Include legal citations extraction
                </Label>
              </div>
              <div className="space-y-2">
                <Label>Validation Level</Label>
                <Select
                  value={processingOptions.validation_level}
                  onValueChange={(value: "strict" | "moderate" | "lenient") =>
                    setProcessingOptions({ ...processingOptions, validation_level: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="strict">Strict</SelectItem>
                    <SelectItem value="moderate">Moderate</SelectItem>
                    <SelectItem value="lenient">Lenient</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="flex items-center gap-2 p-3 bg-destructive/10 text-destructive rounded-lg">
              <AlertCircle className="h-4 w-4" />
              <span className="text-sm">{error}</span>
            </div>
          )}

          {/* Progress Display */}
          {status === 'processing' && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span>Processing permit...</span>
                <span>{progress}%</span>
              </div>
              <Progress value={progress} />
            </div>
          )}

          {/* Execute Button */}
          <Button
            onClick={handleExecuteProcessing}
            disabled={loading || !permitFileId || targetSystems.length === 0}
            className="w-full"
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <Map className="mr-2 h-4 w-4" />
                Process Permit
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Results Display */}
      {processingResult && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {status === 'completed' ? (
                <CheckCircle className="h-5 w-5 text-green-500" />
              ) : (
                <XCircle className="h-5 w-5 text-red-500" />
              )}
              Processing Results
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* PSO Summary */}
            <div className="space-y-2">
              <h4 className="font-semibold">PSO Summary</h4>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-muted-foreground">PSO ID</Label>
                  <p className="font-mono text-sm">{processingResult.pso_id}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Permit ID</Label>
                  <p className="font-mono text-sm">{processingResult.permit_id}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Permit Type</Label>
                  <Badge>{processingResult.permit_type}</Badge>
                </div>
                <div>
                  <Label className="text-muted-foreground">Obligations</Label>
                  <p className="text-sm">{processingResult.obligations_count}</p>
                </div>
              </div>
            </div>

            {/* Validation Results */}
            {processingResult.validation_result && (
              <div className="space-y-2">
                <h4 className="font-semibold">Validation</h4>
                <div className="flex items-center gap-2">
                  {processingResult.validation_result.valid ? (
                    <CheckCircle className="h-4 w-4 text-green-500" />
                  ) : (
                    <XCircle className="h-4 w-4 text-red-500" />
                  )}
                  <span className="text-sm">
                    {processingResult.validation_result.valid ? 'Valid' : 'Invalid'}
                  </span>
                </div>
                {processingResult.validation_result.issues.length > 0 && (
                  <div className="text-sm text-muted-foreground">
                    <p>Issues:</p>
                    <ul className="list-disc list-inside">
                      {processingResult.validation_result.issues.map((issue, i) => (
                        <li key={i}>{issue}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Mapping Results */}
            {processingResult.mapping_results && processingResult.mapping_results.length > 0 && (
              <div className="space-y-2">
                <h4 className="font-semibold">Mapping Results</h4>
                <div className="space-y-2">
                  {processingResult.mapping_results.map((result, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 border rounded-lg"
                    >
                      <div className="flex items-center gap-2">
                        {result.success ? (
                          <CheckCircle className="h-4 w-4 text-green-500" />
                        ) : (
                          <XCircle className="h-4 w-4 text-red-500" />
                        )}
                        <span className="font-medium">{result.system}</span>
                      </div>
                      {result.success && result.output_file_id && (
                        <Badge variant="outline">{result.output_file_id}</Badge>
                      )}
                      {result.error && (
                        <span className="text-sm text-destructive">{result.error}</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Report Link */}
            {processingResult.report && (
              <div className="pt-4 border-t">
                <p className="text-sm text-muted-foreground">
                  Report generated at: {new Date(processingResult.report.generated_at).toLocaleString()}
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}

