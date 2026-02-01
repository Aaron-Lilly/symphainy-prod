/**
 * VLP Extraction Section
 * 
 * Policy data extraction for Variable Life Policy demo.
 * Shows extracted fields, data quality, and migration readiness.
 */

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Database, FileText, CheckCircle, AlertTriangle, RefreshCw } from 'lucide-react';

interface PolicyField {
  name: string;
  value: string | null;
  confidence: number;
  source: 'mainframe' | 'document' | 'inferred';
  issues?: string[];
}

interface VLPExtractionSectionProps {
  onExtractionComplete?: (result: any) => void;
}

export function VLPExtractionSection({ onExtractionComplete }: VLPExtractionSectionProps) {
  const [extractedFields, setExtractedFields] = useState<PolicyField[]>([]);
  const [migrationReadiness, setMigrationReadiness] = useState<number>(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [dataCompleteness, setDataCompleteness] = useState(0);
  const [schemaCompliance, setSchemaCompliance] = useState(0);
  const [dataQuality, setDataQuality] = useState(0);

  // Standard VLP fields
  const standardFields = [
    'Policy Number',
    'Policy Holder Name',
    'Policy Holder SSN',
    'Issue Date',
    'Effective Date',
    'Face Amount',
    'Premium Amount',
    'Payment Frequency',
    'Beneficiary Name',
    'Beneficiary Relationship',
    'Agent Code',
    'Product Code',
    'Status Code',
  ];

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return 'bg-green-100 text-green-800';
    if (confidence >= 0.7) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  const getSourceBadge = (source: 'mainframe' | 'document' | 'inferred') => {
    switch (source) {
      case 'mainframe':
        return <Badge variant="outline" className="text-xs bg-blue-50">Mainframe</Badge>;
      case 'document':
        return <Badge variant="outline" className="text-xs bg-green-50">Document</Badge>;
      case 'inferred':
        return <Badge variant="outline" className="text-xs bg-yellow-50">Inferred</Badge>;
    }
  };

  const handleRunExtraction = async () => {
    setIsProcessing(true);
    
    // Simulate extraction process
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Generate sample extracted fields
    const sampleExtraction: PolicyField[] = [
      { name: 'Policy Number', value: 'VLP-2024-001234', confidence: 0.99, source: 'mainframe' },
      { name: 'Policy Holder Name', value: 'John A. Smith', confidence: 0.95, source: 'mainframe' },
      { name: 'Policy Holder SSN', value: '***-**-1234', confidence: 0.98, source: 'mainframe' },
      { name: 'Issue Date', value: '2020-03-15', confidence: 0.97, source: 'mainframe' },
      { name: 'Effective Date', value: '2020-04-01', confidence: 0.97, source: 'mainframe' },
      { name: 'Face Amount', value: '$500,000.00', confidence: 0.99, source: 'mainframe' },
      { name: 'Premium Amount', value: '$450.00', confidence: 0.95, source: 'mainframe' },
      { name: 'Payment Frequency', value: 'Monthly', confidence: 0.92, source: 'inferred' },
      { name: 'Beneficiary Name', value: 'Jane M. Smith', confidence: 0.88, source: 'document', issues: ['Name partially obscured in source'] },
      { name: 'Beneficiary Relationship', value: 'Spouse', confidence: 0.85, source: 'inferred' },
      { name: 'Agent Code', value: 'AG-5521', confidence: 0.99, source: 'mainframe' },
      { name: 'Product Code', value: 'VUL-FLEX-100', confidence: 0.99, source: 'mainframe' },
      { name: 'Status Code', value: 'ACTIVE', confidence: 0.99, source: 'mainframe' },
    ];
    
    setExtractedFields(sampleExtraction);
    setDataCompleteness(87);
    setSchemaCompliance(72);
    setDataQuality(91);
    setMigrationReadiness(83);
    setIsProcessing(false);
    
    if (onExtractionComplete) {
      onExtractionComplete({
        fields: sampleExtraction,
        metrics: {
          completeness: 87,
          compliance: 72,
          quality: 91,
          readiness: 83
        }
      });
    }
  };

  return (
    <div className="space-y-6">
      {/* Migration Readiness Score */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5 text-purple-600" />
            Migration Readiness Assessment
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Overall Readiness</span>
              <span className="text-2xl font-bold text-purple-600">
                {migrationReadiness}%
              </span>
            </div>
            <Progress value={migrationReadiness} className="h-3" />
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div className="text-center p-3 bg-green-50 rounded-lg">
                <div className="font-semibold text-green-700">Data Completeness</div>
                <div className="text-2xl font-bold text-green-600">{dataCompleteness}%</div>
              </div>
              <div className="text-center p-3 bg-yellow-50 rounded-lg">
                <div className="font-semibold text-yellow-700">Schema Compliance</div>
                <div className="text-2xl font-bold text-yellow-600">{schemaCompliance}%</div>
              </div>
              <div className="text-center p-3 bg-blue-50 rounded-lg">
                <div className="font-semibold text-blue-700">Data Quality</div>
                <div className="text-2xl font-bold text-blue-600">{dataQuality}%</div>
              </div>
            </div>
            
            {/* Run Extraction Button */}
            {extractedFields.length === 0 && (
              <Button 
                onClick={handleRunExtraction} 
                disabled={isProcessing}
                className="w-full mt-4"
              >
                {isProcessing ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    Extracting Policy Data...
                  </>
                ) : (
                  <>
                    <Database className="h-4 w-4 mr-2" />
                    Run Policy Data Extraction
                  </>
                )}
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Extracted Fields */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-purple-600" />
              Extracted Policy Fields
            </CardTitle>
            {extractedFields.length > 0 && (
              <Button variant="outline" size="sm" onClick={handleRunExtraction} disabled={isProcessing}>
                <RefreshCw className={`h-4 w-4 mr-1 ${isProcessing ? 'animate-spin' : ''}`} />
                Re-extract
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {standardFields.map((field) => {
              const extracted = extractedFields.find(f => f.name === field);
              return (
                <div key={field} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    {extracted ? (
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    ) : (
                      <AlertTriangle className="h-4 w-4 text-yellow-500" />
                    )}
                    <span className="font-medium text-sm">{field}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    {extracted ? (
                      <>
                        <span className="text-sm text-gray-600 font-mono">{extracted.value || '—'}</span>
                        {getSourceBadge(extracted.source)}
                        <Badge className={getConfidenceColor(extracted.confidence)}>
                          {Math.round(extracted.confidence * 100)}%
                        </Badge>
                      </>
                    ) : (
                      <Badge variant="outline">Pending</Badge>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
          
          {/* Issues Summary */}
          {extractedFields.some(f => f.issues && f.issues.length > 0) && (
            <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <h4 className="font-semibold text-yellow-800 text-sm mb-2">Extraction Issues</h4>
              <ul className="text-xs text-yellow-700 space-y-1">
                {extractedFields
                  .filter(f => f.issues && f.issues.length > 0)
                  .map(f => (
                    f.issues?.map((issue, idx) => (
                      <li key={`${f.name}-${idx}`}>
                        <span className="font-medium">{f.name}:</span> {issue}
                      </li>
                    ))
                  ))}
              </ul>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
