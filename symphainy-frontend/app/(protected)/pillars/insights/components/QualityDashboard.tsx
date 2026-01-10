/**
 * QualityDashboard Component
 * 
 * Displays data quality metrics and issues for structured→structured mappings
 * Includes quality score visualization, metrics, and record-level drill-down
 */

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { 
  AlertCircle, 
  CheckCircle, 
  TrendingUp, 
  TrendingDown,
  Filter,
  Search
} from 'lucide-react';
import { QualityReport, QualityIssue } from '@/shared/services/insights/types';
import { Input } from '@/components/ui/input';

interface QualityDashboardProps {
  qualityReport: QualityReport;
  onRecordSelect?: (recordId: string) => void;
}

export function QualityDashboard({ 
  qualityReport,
  onRecordSelect 
}: QualityDashboardProps) {
  const [selectedSeverity, setSelectedSeverity] = useState<string>('all');
  const [selectedIssueType, setSelectedIssueType] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState<string>('');

  // Handle backend structure: validation_results, summary
  const { validation_results, summary } = qualityReport;
  
  // Extract quality issues from validation_results
  const quality_issues: QualityIssue[] = validation_results.flatMap(result => 
    result.issues.map(issue => ({
      ...issue,
      record_id: result.record_id
    }))
  );
  
  // Use summary for metrics
  const overall_score = summary.overall_quality_score;
  const pass_rate = summary.pass_rate;
  const completeness = summary.valid_records / summary.total_records;
  const accuracy = summary.overall_quality_score; // Use overall score as accuracy proxy
  const metrics = {
    total_records: summary.total_records,
    passed_records: summary.valid_records,
    failed_records: summary.invalid_records,
    records_with_issues: summary.invalid_records
  };

  // Filter issues
  const filteredIssues = quality_issues.filter(issue => {
    if (selectedSeverity !== 'all' && issue.severity !== selectedSeverity) return false;
    if (selectedIssueType !== 'all' && issue.issue_type !== selectedIssueType) return false;
    if (searchTerm && !issue.field.toLowerCase().includes(searchTerm.toLowerCase()) && 
        !issue.message.toLowerCase().includes(searchTerm.toLowerCase())) return false;
    return true;
  });

  // Group issues by type
  const issuesByType = quality_issues.reduce((acc, issue) => {
    acc[issue.issue_type] = (acc[issue.issue_type] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  // Group issues by severity
  const issuesBySeverity = quality_issues.reduce((acc, issue) => {
    acc[issue.severity] = (acc[issue.severity] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const getScoreColor = (score: number) => {
    if (score >= 0.9) return 'text-green-600';
    if (score >= 0.7) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreIcon = (score: number) => {
    if (score >= 0.9) return <CheckCircle className="h-5 w-5 text-green-500" />;
    if (score >= 0.7) return <TrendingUp className="h-5 w-5 text-yellow-500" />;
    return <TrendingDown className="h-5 w-5 text-red-500" />;
  };

  return (
    <div className="space-y-6">
      {/* Quality Metrics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Overall Score</p>
                <p className={`text-3xl font-bold ${getScoreColor(overall_score)}`}>
                  {Math.round(overall_score * 100)}%
                </p>
              </div>
              {getScoreIcon(overall_score)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Pass Rate</p>
                <p className={`text-2xl font-bold ${getScoreColor(pass_rate)}`}>
                  {Math.round(pass_rate * 100)}%
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {metrics.passed_records} / {metrics.total_records} records
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Completeness</p>
                <p className={`text-2xl font-bold ${getScoreColor(completeness)}`}>
                  {Math.round(completeness * 100)}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Accuracy</p>
                <p className={`text-2xl font-bold ${getScoreColor(accuracy)}`}>
                  {Math.round(accuracy * 100)}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Issue Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Issues by Type</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {Object.entries(issuesByType).map(([type, count]) => (
                <div key={type} className="flex items-center justify-between">
                  <span className="text-sm capitalize">{type.replace('_', ' ')}</span>
                  <Badge variant="outline">{count}</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Issues by Severity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {Object.entries(issuesBySeverity).map(([severity, count]) => (
                <div key={severity} className="flex items-center justify-between">
                  <span className="text-sm capitalize">{severity}</span>
                  <Badge
                    variant={
                      severity === 'high' ? 'destructive' :
                      severity === 'medium' ? 'default' : 'secondary'
                    }
                  >
                    {count}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quality Issues Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-lg">Quality Issues</CardTitle>
              <CardDescription>
                {filteredIssues.length} of {quality_issues.length} issues
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-gray-400" />
                <Input
                  type="text"
                  placeholder="Search issues..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8 w-64"
                />
              </div>
              <Select value={selectedSeverity} onValueChange={setSelectedSeverity}>
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="Severity" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Severity</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="low">Low</SelectItem>
                </SelectContent>
              </Select>
              <Select value={selectedIssueType} onValueChange={setSelectedIssueType}>
                <SelectTrigger className="w-40">
                  <SelectValue placeholder="Issue Type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  <SelectItem value="missing">Missing</SelectItem>
                  <SelectItem value="invalid_type">Invalid Type</SelectItem>
                  <SelectItem value="invalid_format">Invalid Format</SelectItem>
                  <SelectItem value="out_of_range">Out of Range</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="border rounded-lg">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Record ID</TableHead>
                  <TableHead>Field</TableHead>
                  <TableHead>Issue Type</TableHead>
                  <TableHead>Severity</TableHead>
                  <TableHead>Message</TableHead>
                  <TableHead>Suggested Fix</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredIssues.length > 0 ? (
                  filteredIssues.map((issue, idx) => (
                    <TableRow
                      key={idx}
                      className={onRecordSelect ? 'cursor-pointer hover:bg-gray-50' : ''}
                      onClick={() => onRecordSelect && onRecordSelect(issue.record_id)}
                    >
                      <TableCell className="font-mono text-xs">{issue.record_id}</TableCell>
                      <TableCell className="font-medium">{issue.field}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className="capitalize">
                          {issue.issue_type.replace('_', ' ')}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant={
                            issue.severity === 'high' ? 'destructive' :
                            issue.severity === 'medium' ? 'default' : 'secondary'
                          }
                        >
                          {issue.severity}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-sm">{issue.message}</TableCell>
                      <TableCell className="text-sm text-gray-600">
                        {issue.suggested_fix || '—'}
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center text-gray-500 py-8">
                      No issues found matching your filters
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {/* Record Metrics Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Record Metrics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-600">Total Records</p>
              <p className="text-2xl font-bold">{metrics.total_records}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Passed</p>
              <p className="text-2xl font-bold text-green-600">{metrics.passed_records}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Failed</p>
              <p className="text-2xl font-bold text-red-600">{metrics.failed_records}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">With Issues</p>
              <p className="text-2xl font-bold text-orange-600">{metrics.records_with_issues}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

