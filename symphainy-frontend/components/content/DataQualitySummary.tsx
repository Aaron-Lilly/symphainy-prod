"use client";

import React from "react";

interface DataQualitySummaryProps {
  metadata: any;
}

export const DataQualitySummary: React.FC<DataQualitySummaryProps> = ({ 
  metadata 
}) => {
  if (!metadata) {
    return null;
  }
  
  const qualityScore = calculateQualityScore(metadata);
  
  return (
    <div className="bg-blue-50 border border-blue-200 rounded p-3">
      <div className="flex items-center justify-between mb-2">
        <h4 className="font-semibold text-blue-800">Data Quality Summary</h4>
        <div className="flex items-center gap-2">
          <span className="text-sm text-blue-700">Score:</span>
          <div className="w-16 h-2 bg-blue-200 rounded-full overflow-hidden">
            <div 
              className="h-full bg-blue-600 transition-all duration-300"
              style={{ width: `${qualityScore}%` }}
            />
          </div>
          <span className="text-sm text-blue-700">{qualityScore}%</span>
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-2 text-sm">
        {metadata.rows && (
          <div className="text-blue-700">
            <span className="font-medium">Rows:</span> {metadata.rows.toLocaleString()}
          </div>
        )}
        {metadata.columns && (
          <div className="text-blue-700">
            <span className="font-medium">Columns:</span> {metadata.columns}
          </div>
        )}
        {metadata.pages && (
          <div className="text-blue-700">
            <span className="font-medium">Pages:</span> {metadata.pages}
          </div>
        )}
        {metadata.file_size && (
          <div className="text-blue-700">
            <span className="font-medium">Size:</span> {formatFileSize(metadata.file_size)}
          </div>
        )}
      </div>
    </div>
  );
};

const calculateQualityScore = (metadata: any): number => {
  let score = 100;
  
  // Deduct points for potential issues
  if (metadata.rows && metadata.rows > 10000) {
    score -= 10; // Large datasets might have performance issues
  }
  
  if (metadata.columns && metadata.columns > 50) {
    score -= 15; // Too many columns might indicate poor structure
  }
  
  if (metadata.missing_values && metadata.missing_values > 0) {
    score -= Math.min(20, metadata.missing_values * 2); // Missing values reduce quality
  }
  
  return Math.max(0, score);
};

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}; 