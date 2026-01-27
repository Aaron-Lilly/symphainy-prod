"use client";

import React from "react";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import { FileMetadata } from "@/shared/types/file";

interface SOPWorkflowTabProps {
  file: FileMetadata;
  metadata: any;
}

export const SOPWorkflowTab: React.FC<SOPWorkflowTabProps> = ({ 
  file, 
  metadata 
}) => {
  const router = useRouter();
  
  return (
    <div className="space-y-4">
      <div className="bg-blue-50 border border-blue-200 rounded p-4">
        <h4 className="font-semibold text-blue-800 mb-2">Operations Pillar Processing</h4>
        <p className="text-blue-700 text-sm">
          This file will be processed in the Operations pillar for SOP/Workflow conversion.
        </p>
        <div className="mt-3">
          <Button 
            onClick={() => router.push('/pillars/journey')}
            className="bg-blue-600 hover:bg-blue-700"
          >
            Go to Operations Pillar
          </Button>
        </div>
      </div>
      
      <div className="bg-white border rounded p-3">
        <h4 className="font-semibold mb-2">File Information</h4>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div>Name: {file.ui_name}</div>
          <div>Type: {file.file_type}</div>
          <div>Status: {file.status}</div>
          <div>Uploaded: {new Date(file.created_at).toLocaleDateString()}</div>
          {metadata && (
            <>
              {metadata.pages && <div>Pages: {metadata.pages}</div>}
              {metadata.file_size && <div>Size: {metadata.file_size}</div>}
            </>
          )}
        </div>
      </div>
    </div>
  );
}; 