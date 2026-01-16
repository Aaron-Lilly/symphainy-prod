/**
 * DataQualitySection Component
 * 
 * Holistic data quality evaluation section for Insights pillar
 * Evaluates data quality using validation rules (88 codes, level-01 metadata),
 * schema validation, quality metrics, and generates recommendations
 */

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { AlertCircle, CheckCircle, XCircle, AlertTriangle, TrendingUp, FileText, Sparkles } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { InsightsFileSelector } from './InsightsFileSelector';
import { useInsightsAPIManager, QualityAssessmentResponse } from '@/shared/managers/InsightsAPIManager';
import { usePlatformState } from '@/shared/state/PlatformStateProvider';
import { useContentAPIManager } from '@/shared/managers/ContentAPIManager';

interface DataQualitySectionProps {
  onQualityEvaluationComplete?: (qualityReport: QualityAssessmentResponse) => void;
}

export function DataQualitySection({ 
  onQualityEvaluationComplete 
}: DataQualitySectionProps) {
  const { state } = usePlatformState();
  const insightsAPIManager = useInsightsAPIManager();
  const contentAPIManager = useContentAPIManager();

  const [selectedFileId, setSelectedFileId] = useState<string>('');
  const [selectedParsedFileId, setSelectedParsedFileId] = useState<string>('');
  const [selectedSourceType, setSelectedSourceType] = useState<'file' | 'content_metadata'>('file');
  const [qualityReport, setQualityReport] = useState<QualityAssessmentResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [availableEmbeddings, setAvailableEmbeddings] = useState<Array<{id: string; name: string}>>([]);
  const [selectedEmbeddingId, setSelectedEmbeddingId] = useState<string>('');

  const handleFileSelected = (
    fileId: string, 
    sourceType: 'file' | 'content_metadata',
    contentType: 'structured' | 'unstructured'
  ) => {
    setSelectedFileId(fileId);
    setSelectedSourceType(sourceType);
    // Clear previous results and errors
    setQualityReport(null);
    setError(null);
  };

  const handleEvaluateQuality = async () => {
    if (!selectedFileId) {
      setError('Please select a file first');
      return;
    }

    if (!selectedParsedFileId) {
      setError('Please select a parsed file (or ensure file has been parsed)');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Determine parser type from parsed file metadata
      const parsedFiles = state.realm.content.parsedFiles || [];
      const parsedFile = parsedFiles.find((pf: any) => 
        (pf.parsed_file_id || pf.id) === selectedParsedFileId
      );
      const parserType = parsedFile?.parser_type || 'unknown';

      // Use InsightsAPIManager to assess data quality
      const result = await insightsAPIManager.assessDataQuality(
        selectedParsedFileId,
        selectedFileId,
        parserType
      );

      if (result.success) {
        setQualityReport(result);
        if (onQualityEvaluationComplete) {
          onQualityEvaluationComplete(result);
        }
      } else {
        setError(result.error || 'Quality evaluation failed');
      }
    } catch (err) {
      console.error('[DataQualitySection] Quality evaluation error:', err);
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  const renderQualityReport = () => {
    if (!qualityReport || !qualityReport.quality_assessment) return null;

    const assessment = qualityReport.quality_assessment;
    const overallScore = assessment.quality_score;
    const scorePercentage = Math.round(overallScore * 100);

    // Determine score color
    let scoreColor = 'text-green-600';
    let scoreBadgeVariant: 'default' | 'destructive' | 'secondary' = 'default';
    if (overallScore < 0.5) {
      scoreColor = 'text-red-600';
      scoreBadgeVariant = 'destructive';
    } else if (overallScore < 0.8) {
      scoreColor = 'text-yellow-600';
      scoreBadgeVariant = 'secondary';
    }

    return (
      <div className="space-y-6 mt-6">
        {/* Overall Quality Score */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5" />
              <span>Overall Quality Score</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-2xl font-bold" style={{ color: scoreColor.includes('green') ? '#16a34a' : scoreColor.includes('red') ? '#dc2626' : '#ca8a04' }}>
                  {scorePercentage}%
                </span>
                <Badge variant={scoreBadgeVariant}>
                  {overallScore >= 0.8 ? 'Excellent' : overallScore >= 0.5 ? 'Good' : 'Needs Improvement'}
                </Badge>
              </div>
              <Progress value={scorePercentage} className="h-3" />
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground">Completeness</p>
                  <p className="text-lg font-semibold">{Math.round(assessment.completeness * 100)}%</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Accuracy</p>
                  <p className="text-lg font-semibold text-green-600">{Math.round(assessment.accuracy * 100)}%</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Consistency</p>
                  <p className="text-lg font-semibold">{Math.round(assessment.consistency * 100)}%</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Issues Summary */}
        {assessment.issues && assessment.issues.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <AlertCircle className="h-5 w-5 text-yellow-600" />
                <span>Quality Issues</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {assessment.issues.map((issue, idx) => (
                  <div key={idx} className="p-3 border rounded-lg">
                    <div className="flex items-start space-x-2">
                      <Badge 
                        variant={issue.severity === 'high' ? 'destructive' : issue.severity === 'medium' ? 'secondary' : 'default'}
                        className="flex items-center space-x-1"
                      >
                        {issue.severity === 'high' && <XCircle className="h-3 w-3" />}
                        {issue.severity === 'medium' && <AlertTriangle className="h-3 w-3" />}
                        {issue.severity === 'low' && <AlertCircle className="h-3 w-3" />}
                        <span>{issue.severity}</span>
                      </Badge>
                      <div className="flex-1">
                        <p className="font-medium">{issue.type}</p>
                        <p className="text-sm text-muted-foreground mt-1">{issue.message}</p>
                        {issue.recommendation && (
                          <p className="text-sm text-blue-600 mt-1">💡 {issue.recommendation}</p>
                        )}
                      </div>
                    </div>
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

      {/* Parsed File & Embeddings Selection */}
      {selectedFileId && availableEmbeddings.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Select Parsed File & Semantic Embeddings</CardTitle>
            <CardDescription>
              Choose which parsed file and semantic embeddings to use for quality assessment
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Parsed File</label>
              <Select
                value={selectedParsedFileId}
                onValueChange={setSelectedParsedFileId}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select parsed file" />
                </SelectTrigger>
                <SelectContent>
                  {availableEmbeddings.map((emb) => (
                    <SelectItem key={emb.id} value={emb.id}>
                      {emb.name.replace('_embeddings', '')}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Semantic Embeddings</label>
              <Select
                value={selectedEmbeddingId || availableEmbeddings[0]?.id || ''}
                onValueChange={setSelectedEmbeddingId}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select semantic embeddings" />
                </SelectTrigger>
                <SelectContent>
                  {availableEmbeddings.map((emb) => (
                    <SelectItem key={emb.id} value={emb.id}>
                      {emb.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <p className="text-xs text-gray-500 mt-2">
                Semantic embeddings pattern: <code className="bg-gray-100 px-1 rounded">userfriendlyfilename_embeddings</code>
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Evaluation Trigger */}
      <div className="flex items-center gap-4">
        <Button
          onClick={handleEvaluateQuality}
          disabled={!selectedFileId || !selectedParsedFileId || loading}
          size="lg"
          className="bg-gradient-to-r from-green-600 to-teal-600 hover:from-green-700 hover:to-teal-700"
        >
          <CheckCircle className="h-5 w-5 mr-2" />
          {loading ? 'Evaluating Quality...' : 'Evaluate Data Quality'}
        </Button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-2 text-red-800">
          <AlertCircle className="h-5 w-5" />
          <span>{error}</span>
        </div>
      )}

      {/* Quality Report Display */}
      {qualityReport && renderQualityReport()}
    </div>
  );
}




