"use client";

import React from "react";

interface IssuesTabProps {
  data: any;
}

export const IssuesTab: React.FC<IssuesTabProps> = ({ data }) => {
  const hasWarnings = data.warnings && data.warnings.length > 0;
  const hasErrors = data.errors && data.errors.length > 0;
  
  if (!hasWarnings && !hasErrors) {
    return (
      <div className="bg-green-50 border border-green-200 rounded p-4">
        <h4 className="font-semibold text-green-800 mb-2">No Issues Found</h4>
        <p className="text-green-700 text-sm">
          ✓ File parsed successfully without any warnings or errors.
        </p>
      </div>
    );
  }
  
  return (
    <div className="space-y-4">
      {hasWarnings && (
        <div className="bg-yellow-50 border border-yellow-200 rounded p-4">
          <h4 className="font-semibold text-yellow-800 mb-2">Warnings</h4>
          <div className="space-y-2">
            {data.warnings.map((warning: string, idx: number) => (
              <div key={idx} className="text-yellow-700 text-sm flex items-start gap-2">
                <span>⚠️</span>
                <span>{warning}</span>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {hasErrors && (
        <div className="bg-red-50 border border-red-200 rounded p-4">
          <h4 className="font-semibold text-red-800 mb-2">Errors</h4>
          <div className="space-y-2">
            {data.errors.map((error: string, idx: number) => (
              <div key={idx} className="text-red-700 text-sm flex items-start gap-2">
                <span>❌</span>
                <span>{error}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}; 