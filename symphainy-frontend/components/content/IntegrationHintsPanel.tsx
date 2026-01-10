"use client";

import React from "react";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import { FileType } from "@/shared/types/file";

interface IntegrationHintsPanelProps {
  fileType: string;
  metadata: any;
}

export const IntegrationHintsPanel: React.FC<IntegrationHintsPanelProps> = ({ 
  fileType, 
  metadata 
}) => {
  const router = useRouter();
  const hints = getIntegrationHints(fileType, metadata, router);
  
  if (hints.length === 0) {
    return null;
  }
  
  return (
    <div className="bg-purple-50 border border-purple-200 rounded p-3">
      <h4 className="font-semibold text-purple-800 mb-2">Integration Suggestions</h4>
      
      <div className="space-y-2">
        {hints.map((hint, idx) => (
          <div key={idx} className="text-purple-700 text-sm flex items-center gap-2">
            <span>🔗</span>
            <span>{hint.message}</span>
            {hint.action && (
              <Button 
                onClick={hint.action} 
                variant="outline" 
                size="sm"
                className="ml-auto"
              >
                {hint.actionLabel}
              </Button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

const getIntegrationHints = (fileType: string, metadata: any, router: any) => {
  const hints = [];
  
  // Structured data hints
  if (fileType === "structured") {
    if (metadata.rows && metadata.rows > 100) {
      hints.push({
        message: "Large dataset detected - consider using Insights pillar for analysis",
        action: () => router.push('/pillars/insights'),
        actionLabel: "Go to Insights"
      });
    }
    
    if (metadata.columns && metadata.columns > 5) {
      hints.push({
        message: "Complex data structure - Operations pillar can help create workflows",
        action: () => router.push('/pillars/operation'),
        actionLabel: "Go to Operations"
      });
    }
    
    hints.push({
      message: "Ready for Business Outcomes pillar roadmap generation",
      action: () => router.push('/pillars/business-outcomes'),
      actionLabel: "Go to Business Outcomes"
    });
  }
  
  // Text/PDF hints
  if (fileType === "text" || fileType === "pdf") {
    hints.push({
      message: "Text content ready for SOP/Workflow conversion in Operations pillar",
      action: () => router.push('/pillars/operation'),
      actionLabel: "Go to Operations"
    });
    
    hints.push({
      message: "Document content can be used for Business Outcomes pillar roadmaps",
      action: () => router.push('/pillars/business-outcomes'),
      actionLabel: "Go to Business Outcomes"
    });
  }
  
  // Image hints
  if (fileType === "image") {
    hints.push({
      message: "Image data can be analyzed in Insights pillar",
      action: () => router.push('/pillars/insights'),
      actionLabel: "Go to Insights"
    });
  }
  
  // Binary/Mainframe hints
  if (fileType === "binary") {
    hints.push({
      message: "Mainframe data ready for modernization analysis in Business Outcomes pillar",
      action: () => router.push('/pillars/business-outcomes'),
      actionLabel: "Go to Business Outcomes"
    });
  }
  
  return hints;
}; 