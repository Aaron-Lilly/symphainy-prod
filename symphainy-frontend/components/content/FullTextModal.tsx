"use client";

import React from "react";
import { Button } from "@/components/ui/button";

interface FullTextModalProps {
  text: string;
  onClose: () => void;
}

export const FullTextModal: React.FC<FullTextModalProps> = ({ 
  text, 
  onClose 
}) => {
  if (!text) {
    return null;
  }
  
  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg w-full max-w-4xl h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex justify-between items-center p-4 border-b">
          <h2 className="text-lg font-semibold">Full Text Content</h2>
          <Button onClick={onClose} variant="ghost" size="sm">
            ✕
          </Button>
        </div>
        
        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="text-sm font-mono bg-gray-50 p-4 rounded whitespace-pre-wrap">
            {text}
          </div>
        </div>
        
        {/* Footer */}
        <div className="flex justify-end gap-3 p-4 border-t">
          <Button onClick={onClose} variant="outline">
            Close
          </Button>
        </div>
      </div>
    </div>
  );
}; 