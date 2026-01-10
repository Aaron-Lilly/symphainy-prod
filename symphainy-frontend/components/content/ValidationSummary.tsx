/**
 * ValidationSummary - Component for displaying file parsing validation results
 * 
 * Displays validation results from binary file parsing (88 codes, ASCII level-01 metadata)
 */

"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import {
  CheckCircle,
  XCircle,
  AlertTriangle,
  Search,
  ChevronDown,
  ChevronUp,
  Info
} from 'lucide-react';

export interface ValidationData {
  total_records: number;
  valid_records: number;
  invalid_records: number;
  total_errors: number;
  total_warnings: number;
  total_anomalies: number;
  validation_rate: number;
}

interface ValidationSummaryProps {
  validation: ValidationData;
  encoding?: string;
  className?: string;
}

export function ValidationSummary({ 
  validation, 
  encoding,
  className 
}: ValidationSummaryProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const {
    total_records,
    valid_records,
    invalid_records,
    total_errors,
    total_warnings,
    total_anomalies,
    validation_rate
  } = validation;

  const hasIssues = invalid_records > 0 || total_errors > 0 || total_warnings > 0 || total_anomalies > 0;
  const validationPercentage = Math.round(validation_rate * 100);

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center space-x-2">
            <Info className="h-5 w-5 text-blue-600" />
            <span>Validation Summary</span>
          </CardTitle>
          {encoding && (
            <Badge variant="outline" className="text-xs">
              {encoding.toUpperCase()}
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Summary Metrics */}
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{valid_records}</div>
            <div className="text-xs text-gray-600">Valid Records</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">{invalid_records}</div>
            <div className="text-xs text-gray-600">Invalid Records</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{total_records}</div>
            <div className="text-xs text-gray-600">Total Records</div>
          </div>
        </div>

        {/* Validation Rate Progress Bar */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-700">Validation Rate</span>
            <span className={`font-semibold ${
              validationPercentage >= 90 ? 'text-green-600' :
              validationPercentage >= 70 ? 'text-yellow-600' :
              'text-red-600'
            }`}>
              {validationPercentage}%
            </span>
          </div>
          <Progress 
            value={validationPercentage} 
            className={`h-2 ${
              validationPercentage >= 90 ? 'bg-green-100' :
              validationPercentage >= 70 ? 'bg-yellow-100' :
              'bg-red-100'
            }`}
          />
        </div>

        {/* Issue Badges */}
        {hasIssues ? (
          <div className="flex flex-wrap gap-2">
            {total_errors > 0 && (
              <Badge variant="destructive" className="flex items-center space-x-1">
                <XCircle className="h-3 w-3" />
                <span>{total_errors} Error{total_errors !== 1 ? 's' : ''}</span>
              </Badge>
            )}
            {total_warnings > 0 && (
              <Badge variant="outline" className="flex items-center space-x-1 border-yellow-500 text-yellow-700">
                <AlertTriangle className="h-3 w-3" />
                <span>{total_warnings} Warning{total_warnings !== 1 ? 's' : ''}</span>
              </Badge>
            )}
            {total_anomalies > 0 && (
              <Badge variant="outline" className="flex items-center space-x-1 border-blue-500 text-blue-700">
                <Search className="h-3 w-3" />
                <span>{total_anomalies} Anomal{total_anomalies !== 1 ? 'ies' : 'y'}</span>
              </Badge>
            )}
          </div>
        ) : (
          <div className="flex items-center space-x-2 text-green-600 bg-green-50 p-3 rounded-lg">
            <CheckCircle className="h-5 w-5" />
            <span className="text-sm font-medium">All records passed validation!</span>
          </div>
        )}

        {/* Expandable Details */}
        {hasIssues && (
          <div className="border-t pt-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsExpanded(!isExpanded)}
              className="w-full justify-between"
            >
              <span className="text-sm">View Details</span>
              {isExpanded ? (
                <ChevronUp className="h-4 w-4" />
              ) : (
                <ChevronDown className="h-4 w-4" />
              )}
            </Button>
            
            {isExpanded && (
              <div className="mt-4 space-y-3 text-sm">
                <div className="bg-gray-50 p-3 rounded-lg">
                  <div className="font-medium text-gray-900 mb-2">Validation Statistics</div>
                  <div className="space-y-1 text-gray-700">
                    <div>Total Records: <span className="font-semibold">{total_records}</span></div>
                    <div>Valid: <span className="font-semibold text-green-600">{valid_records}</span></div>
                    <div>Invalid: <span className="font-semibold text-red-600">{invalid_records}</span></div>
                    <div>Validation Rate: <span className="font-semibold">{validationPercentage}%</span></div>
                  </div>
                </div>
                
                {(total_errors > 0 || total_warnings > 0 || total_anomalies > 0) && (
                  <div className="bg-yellow-50 p-3 rounded-lg">
                    <div className="font-medium text-yellow-900 mb-2">Issues Found</div>
                    <div className="space-y-1 text-yellow-800">
                      {total_errors > 0 && (
                        <div>Errors: <span className="font-semibold">{total_errors}</span></div>
                      )}
                      {total_warnings > 0 && (
                        <div>Warnings: <span className="font-semibold">{total_warnings}</span></div>
                      )}
                      {total_anomalies > 0 && (
                        <div>Anomalies: <span className="font-semibold">{total_anomalies}</span></div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}




