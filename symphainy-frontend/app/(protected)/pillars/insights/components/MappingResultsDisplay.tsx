/**
 * MappingResultsDisplay Component
 * 
 * Displays data mapping results including:
 * - Mapping rules table
 * - Sample mapped records
 * - Citations
 * - Quality report (for structured→structured)
 * - Cleanup actions (for structured→structured)
 */

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '@/components/ui/table';
import { 
  Download, 
  CheckCircle, 
  AlertCircle, 
  FileText, 
  Link as LinkIcon,
  TrendingUp,
  Database
} from 'lucide-react';
import { DataMappingResultsResponse, MappingRule, Citation, QualityReport, CleanupAction } from '@/shared/services/insights/types';
import { QualityDashboard } from './QualityDashboard';
import { CleanupActionsPanel } from './CleanupActionsPanel';

interface MappingResultsDisplayProps {
  mappingResults: DataMappingResultsResponse;
  onExport?: (format: 'excel' | 'json' | 'csv') => void;
}

export function MappingResultsDisplay({ 
  mappingResults,
  onExport 
}: MappingResultsDisplayProps) {
  const [selectedTab, setSelectedTab] = useState('overview');

  // Backend structure: mapping_rules, mapped_data, data_quality, cleanup_actions, citations, confidence_scores, metadata
  const { 
    mapping_rules, 
    mapped_data, 
    data_quality, 
    cleanup_actions, 
    citations, 
    confidence_scores, 
    metadata 
  } = mappingResults;

  // Extract mapped records from mapped_data
  // Always get records array from transformed_data, or use empty array
  const mapped_records: Record<string, unknown>[] = Array.isArray(mapped_data?.transformed_data?.records)
    ? mapped_data.transformed_data.records
    : Array.isArray(mapped_data?.transformed_data)
      ? mapped_data.transformed_data as Record<string, unknown>[]
      : [];

  // Transform backend data_quality to frontend QualityReport format
  const quality_report = data_quality ? {
    overall_score: data_quality.summary.overall_quality_score,
    pass_rate: data_quality.summary.pass_rate,
    completeness: data_quality.summary.valid_records / data_quality.summary.total_records,
    accuracy: data_quality.summary.overall_quality_score, // Use overall score as accuracy proxy
    record_count: data_quality.summary.total_records,
    quality_issues: data_quality.validation_results.flatMap(result => 
      result.issues.map(issue => ({
        ...issue,
        record_id: result.record_id
      }))
    ),
    metrics: {
      total_records: data_quality.summary.total_records,
      passed_records: data_quality.summary.valid_records,
      failed_records: data_quality.summary.invalid_records,
      records_with_issues: data_quality.summary.invalid_records
    }
  } : undefined;

  // Transform citations from array to object format for display
  const citationsByField: Record<string, Citation[]> = {};
  if (citations && Array.isArray(citations)) {
    citations.forEach(citation => {
      if (!citationsByField[citation.field]) {
        citationsByField[citation.field] = [];
      }
      citationsByField[citation.field].push(citation);
    });
  }

  // Calculate average confidence
  const avgConfidence = mapping_rules.length > 0
    ? mapping_rules.reduce((sum, rule) => sum + rule.confidence, 0) / mapping_rules.length
    : 0;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Mapping Results</CardTitle>
            <CardDescription>
              {mapped_records.length} records mapped • Average confidence: {Math.round(avgConfidence * 100)}%
            </CardDescription>
          </div>
          <div className="flex gap-2">
            {onExport && (
              <>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onExport('excel')}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Excel
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onExport('json')}
                >
                  <Download className="h-4 w-4 mr-2" />
                  JSON
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onExport('csv')}
                >
                  <Download className="h-4 w-4 mr-2" />
                  CSV
                </Button>
              </>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <Tabs value={selectedTab} onValueChange={setSelectedTab}>
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="rules">Mapping Rules</TabsTrigger>
            <TabsTrigger value="sample">Sample Data</TabsTrigger>
            <TabsTrigger value="citations">Citations</TabsTrigger>
            {quality_report && <TabsTrigger value="quality">Quality</TabsTrigger>}
            {cleanup_actions && cleanup_actions.length > 0 && (
              <TabsTrigger value="cleanup">Cleanup</TabsTrigger>
            )}
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            {/* Summary Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Mapped Records</p>
                      <p className="text-2xl font-bold">{mapped_records.length}</p>
                    </div>
                    <Database className="h-8 w-8 text-blue-500" />
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Mapping Rules</p>
                      <p className="text-2xl font-bold">{mapping_rules.length}</p>
                    </div>
                    <FileText className="h-8 w-8 text-purple-500" />
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Avg Confidence</p>
                      <p className="text-2xl font-bold">{Math.round(avgConfidence * 100)}%</p>
                    </div>
                    <TrendingUp className="h-8 w-8 text-green-500" />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Quality Report Summary (if available) */}
            {quality_report && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Quality Report Summary</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div>
                      <p className="text-sm text-gray-600">Overall Score</p>
                      <p className="text-2xl font-bold">{Math.round(quality_report.overall_score * 100)}%</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Pass Rate</p>
                      <p className="text-2xl font-bold">{Math.round(quality_report.pass_rate * 100)}%</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Completeness</p>
                      <p className="text-2xl font-bold">{Math.round(quality_report.completeness * 100)}%</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Accuracy</p>
                      <p className="text-2xl font-bold">{Math.round(quality_report.accuracy * 100)}%</p>
                    </div>
                  </div>
                  <div className="mt-4">
                    <p className="text-sm text-gray-600">
                      {quality_report.quality_issues.length} quality issues found. 
                      See the Quality tab for details.
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Cleanup Actions Summary (if available) */}
            {cleanup_actions && cleanup_actions.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Cleanup Actions Summary</CardTitle>
                  <CardDescription>
                    {cleanup_actions.length} recommended actions to improve data quality
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {cleanup_actions.slice(0, 3).map((action) => (
                      <div key={action.action_id} className="flex items-center gap-2 text-sm">
                        <Badge
                          variant={
                            action.priority === 'high' ? 'destructive' :
                            action.priority === 'medium' ? 'default' : 'secondary'
                          }
                        >
                          {action.priority}
                        </Badge>
                        <span>{action.description}</span>
                        <span className="text-gray-500">({action.affected_records} records)</span>
                      </div>
                    ))}
                    {cleanup_actions.length > 3 && (
                      <p className="text-xs text-gray-500">
                        +{cleanup_actions.length - 3} more actions. See the Cleanup tab for details.
                      </p>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Mapping Rules Tab */}
          <TabsContent value="rules">
            <div className="border rounded-lg">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Source Field</TableHead>
                    <TableHead>Target Field</TableHead>
                    <TableHead>Confidence</TableHead>
                    <TableHead>Method</TableHead>
                    <TableHead>Transformation</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {mapping_rules.map((rule, idx) => (
                    <TableRow key={idx}>
                      <TableCell className="font-medium">{rule.source_field}</TableCell>
                      <TableCell>{rule.target_field}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <span>{Math.round(rule.confidence * 100)}%</span>
                          {rule.confidence >= 0.8 ? (
                            <CheckCircle className="h-4 w-4 text-green-500" />
                          ) : rule.confidence >= 0.6 ? (
                            <AlertCircle className="h-4 w-4 text-yellow-500" />
                          ) : (
                            <AlertCircle className="h-4 w-4 text-red-500" />
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">{rule.extraction_method}</Badge>
                      </TableCell>
                      <TableCell className="text-sm text-gray-600">
                        {rule.transformation || 'None'}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </TabsContent>

          {/* Sample Data Tab */}
          <TabsContent value="sample">
            <div className="border rounded-lg">
              {mapped_records.length > 0 ? (
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        {Object.keys(mapped_records[0]).map((key) => (
                          <TableHead key={key}>{key}</TableHead>
                        ))}
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {mapped_records.slice(0, 10).map((record, idx) => (
                        <TableRow key={idx}>
                          {Object.values(record).map((value: any, valIdx) => (
                            <TableCell key={valIdx} className="text-sm">
                              {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                            </TableCell>
                          ))}
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                  {mapped_records.length > 10 && (
                    <div className="p-4 text-center text-sm text-gray-500">
                      Showing 10 of {mapped_records.length} records
                    </div>
                  )}
                </div>
              ) : (
                <div className="p-8 text-center text-gray-500">
                  No mapped records to display
                </div>
              )}
            </div>
          </TabsContent>

          {/* Citations Tab */}
          <TabsContent value="citations">
            <div className="space-y-4">
              {Object.entries(citationsByField).length > 0 ? (
                Object.entries(citationsByField).map(([field, fieldCitations]) => (
                  <Card key={field}>
                    <CardHeader>
                      <CardTitle className="text-sm font-medium">{field}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {fieldCitations.map((citation, idx) => (
                          <div
                            key={idx}
                            className="flex items-start gap-2 p-2 bg-gray-50 rounded"
                          >
                            <LinkIcon className="h-4 w-4 text-blue-500 mt-0.5 flex-shrink-0" />
                            <div className="flex-1 text-sm">
                              <p className="font-medium">{citation.source}</p>
                              <p className="text-gray-600">{citation.location}</p>
                              <p className="text-xs text-gray-500 mt-1">
                                Confidence: {Math.round(citation.confidence * 100)}%
                              </p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                ))
              ) : (
                <div className="p-8 text-center text-gray-500">
                  No citations available
                </div>
              )}
            </div>
          </TabsContent>

          {/* Quality Tab */}
          {data_quality && quality_report && (
            <TabsContent value="quality">
              <QualityDashboard
                qualityReport={data_quality}
                onRecordSelect={(recordId) => {
                  console.log('Selected record:', recordId);
                  // Could navigate to record details or highlight in sample data
                }}
              />
            </TabsContent>
          )}

          {/* Cleanup Actions Tab */}
          {cleanup_actions && cleanup_actions.length > 0 && (
            <TabsContent value="cleanup">
              <CleanupActionsPanel
                cleanupActions={cleanup_actions}
                onExport={() => {
                  // Export cleanup actions report
                  if (onExport) {
                    onExport('json'); // Default to JSON for cleanup actions
                  }
                }}
              />
            </TabsContent>
          )}
        </Tabs>
      </CardContent>
    </Card>
  );
}

