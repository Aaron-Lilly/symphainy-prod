"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { DataGrid } from "../DataGrid";
import { TextAnalysisPanel } from "../TextAnalysisPanel";
import { FullTextModal } from "../FullTextModal";
import { HighlightedText } from "../HighlightedText";

interface TextDataTabProps {
  data: any;
  metadata: any;
}

export const TextDataTab: React.FC<TextDataTabProps> = ({ 
  data, 
  metadata 
}) => {
  const [searchText, setSearchText] = useState('');
  const [showFullText, setShowFullText] = useState(false);
  
  return (
    <div className="space-y-4">
      <div className="bg-white border rounded p-3">
        <div className="flex justify-between items-center mb-3">
          <h4 className="font-semibold">Extracted Text</h4>
          {data.text && data.text.length > 1000 && (
            <Button 
              onClick={() => setShowFullText(true)} 
              variant="outline" 
              size="sm"
            >
              View Full Text
            </Button>
          )}
        </div>
        
        <input
          type="text"
          placeholder="Search text content..."
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          className="w-full px-3 py-2 border rounded mb-3"
        />
        
        <div className="max-h-64 overflow-y-auto text-sm font-mono bg-gray-50 p-3 rounded">
          <HighlightedText 
            text={data.text || ''} 
            searchTerm={searchText}
            maxLength={showFullText ? undefined : 1000}
          />
        </div>
      </div>
      
      {data.preview_grid && data.preview_grid.length > 0 && (
        <div className="bg-white border rounded p-3">
          <h4 className="font-semibold mb-2">Detected Data Tables</h4>
          <DataGrid data={data.preview_grid} />
        </div>
      )}
      
      <TextAnalysisPanel text={data.text || ''} metadata={metadata} />
      
      {showFullText && (
        <FullTextModal 
          text={data.text || ''} 
          onClose={() => setShowFullText(false)} 
        />
      )}
    </div>
  );
}; 