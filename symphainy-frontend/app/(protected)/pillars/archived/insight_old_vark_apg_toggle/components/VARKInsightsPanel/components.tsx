/**
 * VARKInsightsPanel Components
 * Sub-components for VARKInsightsPanel functionality
 */

import React from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { 
  BarChart3, 
  Table as TableIcon, 
  TrendingUp, 
  FileText,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  Download,
  Share2,
  Sparkles,
  Loader2,
  Eye,
  FileSpreadsheet,
  Users,
  Lightbulb
} from 'lucide-react';
import { FileMetadata } from '@/shared/types/file';
import { 
  FileSelectorProps,
  LearningStyleSelectorProps,
  BusinessSummaryProps,
  VARKDisplayProps,
  SummarySectionProps,
  LearningStyle,
  DataDepth
} from './types';
import { 
  getLearningStyleLabel, 
  getLearningStyleIcon,
  getDataDepthLabel,
  getDataDepthDescription 
} from './utils';

export function FileSelector({ files, selectedFile, onFileSelect, loading }: FileSelectorProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            File Selection
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin" />
            <span className="ml-2">Loading files...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (files.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            File Selection
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-gray-500">
            <FileText className="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <p>No parsed files available</p>
            <p className="text-sm">Upload and parse files in the Content pillar first</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          File Selection
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Select
          value={selectedFile?.uuid || ''}
          onValueChange={(value) => {
            const file = files.find(f => f.uuid === value);
            if (file) onFileSelect(file);
          }}
        >
          <SelectTrigger>
            <SelectValue placeholder="Choose a parsed file to analyze" />
          </SelectTrigger>
          <SelectContent>
            {files.map((file) => (
              <SelectItem key={file.uuid} value={file.uuid}>
                <div className="flex flex-col">
                  <span className="font-medium">{file.ui_name}</span>
                  <span className="text-xs text-gray-500">{file.file_type}</span>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </CardContent>
    </Card>
  );
}

export function LearningStyleSelector({ 
  learningStyle, 
  onStyleChange, 
  dataDepth, 
  onDepthChange 
}: LearningStyleSelectorProps) {
  const getIcon = (style: LearningStyle) => {
    switch (style) {
      case 'visual':
        return <BarChart3 className="h-5 w-5" />;
      case 'tabular':
        return <TableIcon className="h-5 w-5" />;
      default:
        return <FileText className="h-5 w-5" />;
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Users className="h-5 w-5" />
          Learning Style & Data Depth
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <label className="text-sm font-medium mb-2 block">Learning Style</label>
          <div className="grid grid-cols-2 gap-2">
            {(['visual', 'tabular'] as LearningStyle[]).map((style) => (
              <Button
                key={style}
                variant={learningStyle === style ? 'default' : 'outline'}
                onClick={() => onStyleChange(style)}
                className="justify-start"
              >
                {getIcon(style)}
                <span className="ml-2">{getLearningStyleLabel(style)}</span>
              </Button>
            ))}
          </div>
        </div>

        <div>
          <label className="text-sm font-medium mb-2 block">Data Depth</label>
          <Select value={dataDepth} onValueChange={(value) => onDepthChange(value as DataDepth)}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {(['summary', 'detailed', 'drill-down'] as DataDepth[]).map((depth) => (
                <SelectItem key={depth} value={depth}>
                  <div>
                    <div className="font-medium">{getDataDepthLabel(depth)}</div>
                    <div className="text-xs text-gray-500">{getDataDepthDescription(depth)}</div>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </CardContent>
    </Card>
  );
}

export function BusinessSummary({ summary, loading, onRefresh }: BusinessSummaryProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Lightbulb className="h-5 w-5" />
            Business Summary
          </div>
          <Button variant="outline" size="sm" onClick={onRefresh} disabled={loading}>
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          </Button>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin" />
            <span className="ml-2">Generating summary...</span>
          </div>
        ) : (
          <div className="prose prose-sm max-w-none">
            <p className="text-gray-700 leading-relaxed">{summary}</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export function VARKDisplay({ 
  learningStyle, 
  dataDepth, 
  analysisResults, 
  isAnalyzing, 
  onAnalysisComplete 
}: VARKDisplayProps) {
  const handleAnalyze = async () => {
    // This would trigger the analysis
    console.log('Starting analysis...');
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {learningStyle === 'visual' ? <BarChart3 className="h-5 w-5" /> : <TableIcon className="h-5 w-5" />}
          {getLearningStyleLabel(learningStyle)} Analysis
        </CardTitle>
      </CardHeader>
      <CardContent>
        {isAnalyzing ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin" />
            <span className="ml-2">Analyzing data...</span>
          </div>
        ) : analysisResults ? (
          <div className="space-y-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-medium mb-2">Analysis Results</h4>
              <pre className="text-sm overflow-x-auto">
                {JSON.stringify(analysisResults, null, 2)}
              </pre>
            </div>
          </div>
        ) : (
          <div className="text-center py-8">
            <Button onClick={handleAnalyze} disabled={isAnalyzing}>
              <Sparkles className="h-4 w-4 mr-2" />
              Start Analysis
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export function SummarySection({ 
  businessSummary, 
  analysisResults, 
  learningStyle, 
  onExport, 
  onShare 
}: SummarySectionProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Summary & Export
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={onExport}>
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
            <Button variant="outline" size="sm" onClick={onShare}>
              <Share2 className="h-4 w-4 mr-2" />
              Share
            </Button>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            <h4 className="font-medium mb-2">Business Summary</h4>
            <p className="text-sm text-gray-700">{businessSummary}</p>
          </div>
          
          {analysisResults && (
            <div>
              <h4 className="font-medium mb-2">Analysis Overview</h4>
              <div className="bg-gray-50 p-3 rounded text-sm">
                <p>Learning Style: {getLearningStyleLabel(learningStyle)}</p>
                <p>Results available for export and sharing with Experience pillar</p>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
} 