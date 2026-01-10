'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Database, FileText, Layers, Sparkles, ArrowRight, CheckCircle2, Circle } from 'lucide-react';

interface ThreeLayerPatternDiagramProps {
  currentLayer?: 'infrastructure' | 'business' | 'semantic';
  fileData?: {
    file_id?: string;
    parsed_file_id?: string;
    content_id?: string;
  };
}

export default function ThreeLayerPatternDiagram({ 
  currentLayer,
  fileData 
}: ThreeLayerPatternDiagramProps) {
  const [hoveredLayer, setHoveredLayer] = useState<string | null>(null);
  
  const layers = [
    {
      id: 'infrastructure',
      name: 'Layer 1: Infrastructure',
      description: 'File parsing → stores parsed files',
      icon: FileText,
      color: 'blue',
      status: fileData?.parsed_file_id ? 'complete' : 'pending',
      data: fileData?.parsed_file_id ? 'Parsed file available' : 'No parsed file'
    },
    {
      id: 'business',
      name: 'Layer 2: Business Enablement',
      description: 'Embedding creation → extracts metadata FROM parsed files',
      icon: Sparkles,
      color: 'purple',
      status: fileData?.content_id ? 'complete' : 'pending',
      data: fileData?.content_id ? 'Embeddings created' : 'No embeddings'
    },
    {
      id: 'semantic',
      name: 'Layer 3: Semantic Layer',
      description: 'Embeddings storage → stores embeddings + metadata in ArangoDB',
      icon: Layers,
      color: 'green',
      status: fileData?.content_id ? 'complete' : 'pending',
      data: fileData?.content_id ? 'Semantic layer active' : 'Not available'
    }
  ];
  
  const getColorClasses = (color: string, isActive: boolean) => {
    const colors: Record<string, { bg: string; border: string; text: string }> = {
      blue: {
        bg: isActive ? 'bg-blue-50' : 'bg-gray-50',
        border: isActive ? 'border-blue-300' : 'border-gray-200',
        text: isActive ? 'text-blue-600' : 'text-gray-400'
      },
      purple: {
        bg: isActive ? 'bg-purple-50' : 'bg-gray-50',
        border: isActive ? 'border-purple-300' : 'border-gray-200',
        text: isActive ? 'text-purple-600' : 'text-gray-400'
      },
      green: {
        bg: isActive ? 'bg-green-50' : 'bg-gray-50',
        border: isActive ? 'border-green-300' : 'border-gray-200',
        text: isActive ? 'text-green-600' : 'text-gray-400'
      }
    };
    return colors[color] || colors.blue;
  };
  
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm flex items-center gap-2">
          <Database className="h-4 w-4" />
          How Data Mash Works
        </CardTitle>
        <CardDescription>
          The 3-Layer Pattern: Your data flows through infrastructure, business enablement, and semantic layers
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {layers.map((layer, index) => {
            const Icon = layer.icon;
            const isActive = currentLayer === layer.id || layer.status === 'complete';
            const isHovered = hoveredLayer === layer.id;
            const colors = getColorClasses(layer.color, isActive || isHovered);
            const isCurrent = currentLayer === layer.id;
            
            return (
              <div key={layer.id}>
                <div
                  className={`flex items-center gap-4 p-4 rounded-lg border-2 transition-all cursor-pointer ${colors.bg} ${colors.border} ${
                    isCurrent ? 'ring-2 ring-offset-2 ring-blue-400' : ''
                  }`}
                  onMouseEnter={() => setHoveredLayer(layer.id)}
                  onMouseLeave={() => setHoveredLayer(null)}
                >
                  {/* Layer Number */}
                  <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${colors.bg} border-2 ${colors.border}`}>
                    {layer.status === 'complete' ? (
                      <CheckCircle2 className={`h-5 w-5 ${colors.text}`} />
                    ) : (
                      <Circle className={`h-5 w-5 ${colors.text}`} />
                    )}
                  </div>
                  
                  {/* Layer Icon */}
                  <div className={`flex-shrink-0 p-2 rounded-lg ${colors.bg} border ${colors.border}`}>
                    <Icon className={`h-5 w-5 ${colors.text}`} />
                  </div>
                  
                  {/* Layer Info */}
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-semibold text-gray-900">{layer.name}</span>
                      {isCurrent && (
                        <Badge variant="outline" className="text-xs">
                          Current View
                        </Badge>
                      )}
                      {layer.status === 'complete' && (
                        <Badge variant="outline" className="text-xs bg-green-50 text-green-700 border-green-200">
                          Complete
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-gray-600">{layer.description}</p>
                    <p className="text-xs text-gray-500 mt-1">{layer.data}</p>
                  </div>
                  
                  {/* Arrow (except for last layer) */}
                  {index < layers.length - 1 && (
                    <div className="flex-shrink-0">
                      <ArrowRight className={`h-5 w-5 ${colors.text}`} />
                    </div>
                  )}
                </div>
              </div>
            );
          })}
          
          {/* Virtual Query Indicator */}
          <div className="mt-4 p-3 bg-indigo-50 rounded-lg border border-indigo-200">
            <div className="flex items-start gap-2">
              <Sparkles className="h-4 w-4 text-indigo-600 mt-0.5" />
              <div className="flex-1">
                <div className="text-xs font-semibold text-indigo-900 mb-1">Virtual by Default</div>
                <div className="text-xs text-indigo-700">
                  Data Mash queries data virtually - no data movement. Your data stays in its original location 
                  (GCS for files, ArangoDB for embeddings) and is composed on-the-fly for queries.
                </div>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}







