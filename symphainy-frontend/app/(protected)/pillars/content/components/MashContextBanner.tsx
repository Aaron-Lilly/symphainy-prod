'use client';

import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Database, Layers, Sparkles, Zap } from 'lucide-react';

interface MashContextBannerProps {
  mash?: {
    mash_id?: string;
    purpose?: string;
    execution_mode?: string;
    lifecycle_state?: string;
    source_count?: number;
  };
  file_id?: string;
  parsed_file_id?: string;
  content_id?: string;
}

export default function MashContextBanner({ mash, file_id, parsed_file_id, content_id }: MashContextBannerProps) {
  // Determine if this is a single-source mash (default case)
  const isSingleSource = !mash || (mash.source_count === undefined || mash.source_count <= 1);
  const sourceCount = mash?.source_count || 1;
  
  // Determine mash type
  const mashType = isSingleSource ? 'Single-Source Data Mash' : `Multi-Source Data Mash (${sourceCount} sources)`;
  
  // Execution mode badge
  const executionMode = mash?.execution_mode || 'virtual';
  const executionModeLabel = executionMode === 'virtual' ? 'Virtual (No Data Movement)' : 'Materialized';
  const executionModeIcon = executionMode === 'virtual' ? Zap : Database;
  const ExecutionModeIcon = executionModeIcon;
  
  // Lifecycle state badge
  const lifecycleState = mash?.lifecycle_state || 'active';
  const lifecycleColors: Record<string, string> = {
    'proposed': 'bg-yellow-100 text-yellow-800 border-yellow-200',
    'validated': 'bg-blue-100 text-blue-800 border-blue-200',
    'active': 'bg-green-100 text-green-800 border-green-200',
    'paused': 'bg-gray-100 text-gray-800 border-gray-200',
    'dissolved': 'bg-red-100 text-red-800 border-red-200'
  };
  const lifecycleColor = lifecycleColors[lifecycleState] || lifecycleColors['active'];
  
  return (
    <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
      <CardContent className="p-4">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Layers className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <div className="font-semibold text-gray-900">{mashType}</div>
              <div className="text-sm text-gray-600">
                {isSingleSource 
                  ? 'File → Parsed → Embedding → Semantic Layer'
                  : 'Multiple sources composed virtually'
                }
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-2 flex-wrap">
            <Badge variant="outline" className="flex items-center gap-1">
              <ExecutionModeIcon className="h-3 w-3" />
              {executionModeLabel}
            </Badge>
            <Badge className={lifecycleColor}>
              {lifecycleState.charAt(0).toUpperCase() + lifecycleState.slice(1)}
            </Badge>
            {mash?.purpose && (
              <Badge variant="secondary">
                {mash.purpose}
              </Badge>
            )}
          </div>
        </div>
        
        {/* Data flow indicators */}
        {(file_id || parsed_file_id || content_id) && (
          <div className="mt-3 pt-3 border-t border-blue-200">
            <div className="flex items-center gap-2 text-xs text-gray-600">
              <span className="font-medium">Data Flow:</span>
              {file_id && (
                <span className="flex items-center gap-1">
                  <Database className="h-3 w-3" />
                  File
                </span>
              )}
              {parsed_file_id && (
                <span className="flex items-center gap-1">
                  <Sparkles className="h-3 w-3" />
                  Parsed
                </span>
              )}
              {content_id && (
                <span className="flex items-center gap-1">
                  <Layers className="h-3 w-3" />
                  Semantic
                </span>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}







