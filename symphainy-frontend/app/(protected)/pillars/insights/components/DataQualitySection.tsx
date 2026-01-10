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
import { InsightsFileSelector } from './InsightsFileSelector';
import { evaluateDataQuality, DataQualityRequest, DataQualityResponse } from '@/lib/api/insights';

interface DataQualitySectionProps {
  onQualityEvaluationComplete?: (qualityReport: DataQualityResponse) => void;
}

export function DataQualitySection({ 
  onQualityEvaluationComplete 
}: DataQualitySectionProps) {
  const [selectedFileId, setSelectedFileId] = useState<string>('');
  const [selectedSourceType, setSelectedSourceType] = useState<'file' | 'content_metadata'>('file');
  const [qualityReport, setQualityReport] = useState<DataQualityResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

    try {
      setLoading(true);
      setError(null);

      const request: DataQualityRequest = {
        file_id: selectedFileId,
        quality_options: {
          include_recommendations: true,
          include_metrics: true
        }
      };

      const result = await evaluateDataQuality(request);

      if (result.success) {
        setQualityReport(result);
        if (onQualityEvaluationComplete) {
          onQualityEvaluationComplete(result);
        }
      } else {
        setError(result.error || 'Quality evaluation failed');
      }
    } catch (err) {
      console.error('Quality evaluation error:', err);
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  const renderQualityReport = () => {
    if (!qualityReport || !qualityReport.quality_report) return null;

    const report = qualityReport.quality_report;
    const summary = report.summary;
    const overallScore = report.overall_quality_score;
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
                  <p className="text-muted-foreground">Total Records</p>
                  <p className="text-lg font-semibold">{summary.total_records}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Valid Records</p>
                  <p className="text-lg font-semibold text-green-600">{summary.valid_records}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Invalid Records</p>
                  <p className="text-lg font-semibold text-red-600">{summary.invalid_records}</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Issues Summary */}
        {summary.total_issues > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <AlertCircle className="h-5 w-5 text-yellow-600" />
                <span>Quality Issues</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex flex-wrap gap-2">
                  {summary.issues_by_severity.error > 0 && (
                    <Badge variant="destructive" className="flex items-center space-x-1">
                      <XCircle className="h-3 w-3" />
                      <span>{summary.issues_by_severity.error} Errors</span>
                    </Badge>
                  )}
                  {summary.issues_by_severity.warning > 0 && (
                    <Badge variant="secondary" className="flex items-center space-x-1 bg-yellow-100 text-yellow-800">
                      <AlertTriangle className="h-3 w-3" />
                      <span>{summary.issues_by_severity.warning} Warnings</span>
                    </Badge>
                  )}
                  {summary.issues_by_severity.info > 0 && (
                    <Badge variant="secondary" className="flex items-center space-x-1">
                      <AlertCircle className="h-3 w-3" />
                      <span>{summary.issues_by_severity.info} Info</span>
                    </Badge>
                  )}
                </div>

                {/* Issues by Type */}
                {Object.keys(summary.issues_by_type).length > 0 && (
                  <div>
                    <p className="text-sm font-medium mb-2">Issues by Type:</p>
                    <div className="space-y-1">
                      {Object.entries(summary.issues_by_type).map(([type, count]) => (
                        <div key={type} className="flex justify-between text-sm">
                          <span className="text-muted-foreground">{type.replace(/_/g, ' ')}</span>
                          <span className="font-medium">{count as number}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Quality Metrics */}
        {report.quality_metrics && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <FileText className="h-5 w-5" />
                <span>Quality Metrics</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Completeness</p>
                    <p className="text-xl font-semibold">
                      {Math.round(report.quality_metrics.completeness.overall * 100)}%
                    </p>
                    <Progress value={report.quality_metrics.completeness.overall * 100} className="h-2 mt-2" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Total Missing Values</p>
                    <p className="text-xl font-semibold">{report.quality_metrics.missing_values.total_missing}</p>
                  </div>
                </div>

                {/* Completeness by Field */}
                {Object.keys(report.quality_metrics.completeness.by_field).length > 0 && (
                  <div>
                    <p className="text-sm font-medium mb-2">Completeness by Field:</p>
                    <div className="space-y-2">
                      {Object.entries(report.quality_metrics.completeness.by_field)
                        .sort(([, a], [, b]) => (b as number) - (a as number))
                        .slice(0, 10)
                        .map(([field, completeness]) => (
                          <div key={field} className="space-y-1">
                            <div className="flex justify-between text-sm">
                              <span className="text-muted-foreground">{field}</span>
                              <span className="font-medium">{Math.round((completeness as number) * 100)}%</span>
                            </div>
                            <Progress value={(completeness as number) * 100} className="h-1" />
                          </div>
                        ))}
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Recommendations */}
        {report.recommendations && report.recommendations.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Sparkles className="h-5 w-5" />
                <span>Recommendations</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {report.recommendations.map((rec, idx) => (
                  <div key={idx} className="p-3 border rounded-lg">
                    <div className="flex items-start space-x-2">
                      <Badge variant={rec.priority === 'high' ? 'destructive' : rec.priority === 'medium' ? 'secondary' : 'default'}>
                        {rec.priority}
                      </Badge>
                      <div className="flex-1">
                        <p className="font-medium">{rec.action}</p>
                        <p className="text-sm text-muted-foreground mt-1">{rec.description}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Validation Results Sample */}
        {report.validation_results && report.validation_results.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Validation Results</CardTitle>
              <CardDescription>
                Showing first 10 records with issues (out of {report.validation_results.length} total)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {report.validation_results
                  .filter(r => !r.is_valid)
                  .slice(0, 10)
                  .map((result, idx) => (
                    <div key={idx} className="p-3 border rounded-lg">
                      <div className="flex items-center space-x-2 mb-2">
                        <XCircle className="h-4 w-4 text-red-600" />
                        <span className="font-medium">Record {result.record_index}</span>
                        <Badge variant="destructive">Invalid</Badge>
                      </div>
                      {result.issues.length > 0 && (
                        <div className="space-y-1 mt-2">
                          {result.issues.slice(0, 3).map((issue, issueIdx) => (
                            <div key={issueIdx} className="text-sm text-muted-foreground">
                              <span className="font-medium">{issue.field}:</span> {issue.message}
                            </div>
                          ))}
                          {result.issues.length > 3 && (
                            <div className="text-sm text-muted-foreground">
                              +{result.issues.length - 3} more issues
                            </div>
                          )}
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

      {/* Evaluation Trigger */}
      <div className="flex items-center gap-4">
        <Button
          onClick={handleEvaluateQuality}
          disabled={!selectedFileId || loading}
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




