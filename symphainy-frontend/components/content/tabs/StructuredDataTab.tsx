"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { DataGrid } from "../DataGrid";
import { DataQualitySummary } from "../DataQualitySummary";
import { SchemaAnalysisPanel } from "../SchemaAnalysisPanel";
import { IntegrationHintsPanel } from "../IntegrationHintsPanel";
import { FullDatasetModal } from "../FullDatasetModal";

interface StructuredDataTabProps {
  data: any;
  metadata: any;
}

export const StructuredDataTab: React.FC<StructuredDataTabProps> = ({ 
  data, 
  metadata 
}) => {
  const [showFullModal, setShowFullModal] = useState(false);
  const isComplex = metadata.rows > 1000 || metadata.columns > 20;
  
  return (
    <div className="space-y-4">
      <DataQualitySummary metadata={metadata} />
      
      <div className="bg-white border rounded p-3">
        <div className="flex justify-between items-center mb-3">
          <h4 className="font-semibold">Data Preview</h4>
          {isComplex && (
            <Button 
              onClick={() => setShowFullModal(true)} 
              variant="outline" 
              size="sm"
            >
              View Full Dataset
            </Button>
          )}
        </div>
        
        <DataGrid 
          data={data.preview_grid}
          columns={metadata.column_names}
          sortable={true}
          filterable={true}
          maxRows={isComplex ? 50 : 100}
        />
      </div>
      
      <SchemaAnalysisPanel metadata={metadata} />
      <IntegrationHintsPanel fileType="structured" metadata={metadata} />
      
      {showFullModal && (
        <FullDatasetModal 
          data={data} 
          onClose={() => setShowFullModal(false)} 
        />
      )}
    </div>
  );
}; 