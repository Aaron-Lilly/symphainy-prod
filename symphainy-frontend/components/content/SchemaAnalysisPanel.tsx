"use client";

import React from "react";
import { Button } from "@/components/ui/button";

interface SchemaAnalysisPanelProps {
  metadata: any;
}

export const SchemaAnalysisPanel: React.FC<SchemaAnalysisPanelProps> = ({ 
  metadata 
}) => {
  const suggestions = analyzeSchema(metadata);
  
  if (suggestions.length === 0) {
    return (
      <div className="bg-green-50 border border-green-200 rounded p-3">
        <h4 className="font-semibold text-green-800 mb-2">Schema Analysis</h4>
        <p className="text-green-700 text-sm">
          ✓ Schema looks good - no suggestions at this time.
        </p>
      </div>
    );
  }
  
  return (
    <div className="bg-green-50 border border-green-200 rounded p-3">
      <h4 className="font-semibold text-green-800 mb-2">Schema Suggestions</h4>
      
      <div className="space-y-2">
        {suggestions.map((suggestion, idx) => (
          <div key={idx} className="text-green-700 text-sm flex items-center gap-2">
            <span>💡</span>
            <span>{suggestion.message}</span>
            {suggestion.action && (
              <Button 
                onClick={suggestion.action} 
                variant="outline" 
                size="sm"
                className="ml-auto"
              >
                Apply
              </Button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

const analyzeSchema = (metadata: any) => {
  const suggestions = [];
  
  if (!metadata) {
    return suggestions;
  }
  
  // Check for missing column names
  if (metadata.rows && metadata.rows > 0 && !metadata.column_names) {
    suggestions.push({
      message: "Consider adding column names for better data structure",
      action: null
    });
  }
  
  // Check for too many columns
  if (metadata.columns && metadata.columns > 20) {
    suggestions.push({
      message: "Large number of columns detected - consider normalizing the data",
      action: null
    });
  }
  
  // Check for potential data type issues
  if (metadata.column_names) {
    const numericColumns = metadata.column_names.filter((name: string) => 
      name.toLowerCase().includes('id') || 
      name.toLowerCase().includes('count') ||
      name.toLowerCase().includes('number') ||
      name.toLowerCase().includes('amount')
    );
    
    if (numericColumns.length > 0) {
      suggestions.push({
        message: `Found ${numericColumns.length} potential numeric columns: ${numericColumns.join(', ')}`,
        action: null
      });
    }
  }
  
  // Check for missing values
  if (metadata.missing_values && metadata.missing_values > 0) {
    suggestions.push({
      message: `${metadata.missing_values} missing values detected - consider data cleaning`,
      action: null
    });
  }
  
  return suggestions;
}; 