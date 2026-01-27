/**
 * Your Data Mash Component
 * 
 * Interactive lineage visualization showing the complete data pipeline:
 * File → Parsed → Embedding → Interpretation → Analysis
 * 
 * This is the reimagined "Virtual Data Mapper" - it visualizes how data flows
 * through the system without requiring data ingestion.
 */

"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { AlertCircle, RefreshCw, Download, Eye, FileText, Database, Brain, Sparkles, GitBranch } from 'lucide-react';
import { usePlatformState } from '@/shared/state/PlatformStateProvider';
import { useInsightsAPIManager } from '@/shared/hooks/useInsightsAPIManager';
import { LineageVisualization, LineageVisualizationResponse } from '@/shared/managers/InsightsAPIManager';
import { InsightsFileSelector } from './InsightsFileSelector';
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  MarkerType,
  Position,
  ConnectionMode,
} from 'reactflow';
import 'reactflow/dist/style.css';

interface YourDataMashProps {
  onVisualizationComplete?: (visualization: LineageVisualizationResponse) => void;
}

export function YourDataMash({ onVisualizationComplete }: YourDataMashProps) {
  const { state } = usePlatformState();
  const insightsAPIManager = useInsightsAPIManager();

  const [selectedFileId, setSelectedFileId] = useState<string>('');
  const [visualization, setVisualization] = useState<LineageVisualizationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);

  // Handle file selection
  const handleFileSelected = (
    fileId: string,
    sourceType: 'file' | 'content_metadata',
    contentType: 'structured' | 'unstructured'
  ) => {
    setSelectedFileId(fileId);
    setVisualization(null);
    setError(null);
    setNodes([]);
    setEdges([]);
  };

  // Generate visualization
  const handleVisualize = useCallback(async () => {
    if (!selectedFileId) {
      setError('Please select a file first');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const result = await insightsAPIManager.visualizeLineage(selectedFileId);

      if (result.success && result.visualization) {
        setVisualization(result);
        
        // Convert lineage graph to React Flow nodes and edges
        const { flowNodes, flowEdges } = convertLineageToFlow(result.visualization.lineage_graph);
        setNodes(flowNodes);
        setEdges(flowEdges);

        if (onVisualizationComplete) {
          onVisualizationComplete(result);
        }
      } else {
        setError(result.error || 'Failed to visualize lineage');
      }
    } catch (err) {
      console.error('[YourDataMash] Error visualizing lineage:', err);
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  }, [selectedFileId, insightsAPIManager, onVisualizationComplete]);

  // Auto-visualize when file is selected
  useEffect(() => {
    if (selectedFileId && !visualization) {
      handleVisualize();
    }
  }, [selectedFileId, visualization, handleVisualize]);

  // Get visualization from state if available
  useEffect(() => {
    if (selectedFileId) {
      const visualizations = state.realm.insights.lineageVisualizations || {};
      if (visualizations[selectedFileId]) {
        const viz = visualizations[selectedFileId];
        setVisualization({ success: true, visualization: viz, file_id: selectedFileId });
        const { flowNodes, flowEdges } = convertLineageToFlow(viz.lineage_graph);
        setNodes(flowNodes);
        setEdges(flowEdges);
      }
    }
  }, [selectedFileId, state.realm.insights.lineageVisualizations]);

  return (
    <div className="space-y-6">
      {/* ✅ PHASE 4.1: Enhanced Header - More Prominent */}
      <Card className="border-2 border-blue-200 bg-gradient-to-br from-blue-50 to-purple-50">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-3 text-2xl">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <GitBranch className="h-6 w-6 text-blue-600" />
                </div>
                Your Data Mash
                <Badge variant="secondary" className="ml-2 bg-blue-100 text-blue-800">
                  Interactive Lineage
                </Badge>
              </CardTitle>
              <CardDescription className="mt-2 text-base">
                Visualize the complete data pipeline: File → Parsed → Embedding → Interpretation → Analysis
              </CardDescription>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* File Selector */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Select File for Lineage Visualization
          </CardTitle>
          <CardDescription>
            Choose a file to visualize its complete data lineage pipeline from upload to final analysis.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <InsightsFileSelector
            onSourceSelected={handleFileSelected}
            contentType="structured"
          />
        </CardContent>
      </Card>

      {/* Visualization */}
      {selectedFileId && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <Database className="h-5 w-5" />
                  Your Data Mash
                </CardTitle>
                <CardDescription>
                  Complete data lineage pipeline visualization
                </CardDescription>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleVisualize}
                  disabled={loading}
                >
                  <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                  Refresh
                </Button>
                {visualization?.visualization?.storage_path && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      if (visualization.visualization?.storage_path) {
                        window.open(visualization.visualization.storage_path, '_blank');
                      }
                    }}
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Export
                  </Button>
                )}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {loading && (
              <div className="flex items-center justify-center py-12">
                <div className="text-center">
                  <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-gray-400" />
                  <p className="text-sm text-gray-600">Generating lineage visualization...</p>
                </div>
              </div>
            )}

            {error && (
              <div className="flex items-center gap-2 p-4 bg-red-50 border border-red-200 rounded-lg">
                <AlertCircle className="h-5 w-5 text-red-600" />
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}

            {visualization?.visualization && nodes.length > 0 && (
              <div className="border rounded-lg overflow-hidden" style={{ height: '600px' }}>
                <ReactFlow
                  nodes={nodes}
                  edges={edges}
                  connectionMode={ConnectionMode.Loose}
                  fitView
                  attributionPosition="bottom-left"
                >
                  <Background />
                  <Controls />
                  <MiniMap />
                </ReactFlow>
              </div>
            )}

            {visualization?.visualization && nodes.length === 0 && (
              <div className="flex items-center justify-center py-12">
                <div className="text-center">
                  <Database className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                  <p className="text-sm text-gray-600">No lineage data available for this file.</p>
                  <p className="text-xs text-gray-500 mt-2">
                    Upload and parse files in the Content Pillar to see lineage visualization.
                  </p>
                </div>
              </div>
            )}

            {!selectedFileId && !loading && (
              <div className="flex items-center justify-center py-12">
                <div className="text-center">
                  <FileText className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                  <p className="text-sm text-gray-600">Select a file to visualize its data lineage.</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* ✅ PHASE 4.1: Enhanced Lineage Metadata Display */}
      {visualization?.visualization && (
        <Card className="border-2 border-gray-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="h-5 w-5" />
              Lineage Metadata
            </CardTitle>
            <CardDescription>
              Detailed information about the data pipeline stages and transformations
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                  <p className="text-xs font-medium text-blue-700 mb-1">Total Nodes</p>
                  <p className="text-3xl font-bold text-blue-900">{visualization.visualization.lineage_graph.nodes.length}</p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                  <p className="text-xs font-medium text-green-700 mb-1">Connections</p>
                  <p className="text-3xl font-bold text-green-900">{visualization.visualization.lineage_graph.edges.length}</p>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                  <p className="text-xs font-medium text-purple-700 mb-1">Stages</p>
                  <p className="text-3xl font-bold text-purple-900">{getUniqueNodeTypes(visualization.visualization.lineage_graph.nodes).length}</p>
                </div>
                <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
                  <p className="text-xs font-medium text-orange-700 mb-1">File ID</p>
                  <p className="text-sm font-mono text-orange-900 truncate">{visualization.file_id || 'N/A'}</p>
                </div>
              </div>

              <div>
                <p className="text-sm font-semibold text-gray-800 mb-3">Pipeline Stages</p>
                <div className="flex flex-wrap gap-2">
                  {getUniqueNodeTypes(visualization.visualization.lineage_graph.nodes).map((type) => (
                    <Badge key={type} variant="secondary" className="text-sm px-3 py-1">
                      {type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* ✅ PHASE 4.1: Show lineage metadata if available */}
              {visualization.visualization.metadata && (
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <p className="text-sm font-semibold text-gray-800 mb-2">Additional Metadata</p>
                  <div className="text-xs text-gray-600 space-y-1">
                    {Object.entries(visualization.visualization.metadata).map(([key, value]) => (
                      <div key={key} className="flex justify-between">
                        <span className="font-medium">{key.replace(/_/g, ' ')}:</span>
                        <span>{String(value)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

/**
 * Convert lineage graph to React Flow nodes and edges
 */
function convertLineageToFlow(lineageGraph: LineageVisualization['lineage_graph']): {
  flowNodes: Node[];
  flowEdges: Edge[];
} {
  const flowNodes: Node[] = [];
  const flowEdges: Edge[] = [];

  // Node type configurations
  const nodeConfigs: Record<string, { color: string; icon: any }> = {
    file: { color: '#3b82f6', icon: FileText },
    parsed_result: { color: '#10b981', icon: Database },
    embedding: { color: '#8b5cf6', icon: Brain },
    interpretation: { color: '#f59e0b', icon: Eye },
    analysis: { color: '#ef4444', icon: Sparkles },
    guide: { color: '#06b6d4', icon: GitBranch },
    agent_session: { color: '#ec4899', icon: Sparkles },
  };

  // Create nodes with positions
  const nodePositions = calculateNodePositions(lineageGraph.nodes, lineageGraph.edges);
  
  lineageGraph.nodes.forEach((node, index) => {
    const config = nodeConfigs[node.type] || { color: '#6b7280', icon: FileText };
    const position = nodePositions[node.id] || { x: 0, y: index * 150 };

    flowNodes.push({
      id: node.id,
      type: 'default',
      position,
      data: {
        label: (
          <div className="text-center">
            <div className="font-semibold">{node.label}</div>
            {node.type === 'parsed_result' && node.record_count && (
              <div className="text-xs text-gray-500">{node.record_count} records</div>
            )}
            {node.type === 'embedding' && node.model_name && (
              <div className="text-xs text-gray-500">{node.model_name}</div>
            )}
            {node.type === 'interpretation' && node.confidence_score && (
              <div className="text-xs text-gray-500">
                Confidence: {Math.round(node.confidence_score * 100)}%
              </div>
            )}
          </div>
        ),
        type: node.type,
      },
      style: {
        background: config.color,
        color: '#fff',
        border: `2px solid ${config.color}`,
        borderRadius: '8px',
        padding: '10px',
        minWidth: '150px',
      },
    });
  });

  // Create edges
  lineageGraph.edges.forEach((edge) => {
    flowEdges.push({
      id: `${edge.source}-${edge.target}`,
      source: edge.source,
      target: edge.target,
      type: 'smoothstep',
      animated: true,
      markerEnd: {
        type: MarkerType.ArrowClosed,
      },
      label: edge.type.replace('_', ' '),
      style: {
        strokeWidth: 2,
      },
    });
  });

  return { flowNodes, flowEdges };
}

/**
 * Calculate node positions using a hierarchical layout
 */
function calculateNodePositions(
  nodes: LineageVisualization['lineage_graph']['nodes'],
  edges: LineageVisualization['lineage_graph']['edges']
): Record<string, { x: number; y: number }> {
  const positions: Record<string, { x: number; y: number }> = {};
  
  // Group nodes by type for hierarchical layout
  const typeOrder = ['file', 'parsed_result', 'embedding', 'interpretation', 'analysis', 'guide', 'agent_session'];
  const nodesByType: Record<string, typeof nodes> = {};
  
  nodes.forEach((node) => {
    if (!nodesByType[node.type]) {
      nodesByType[node.type] = [];
    }
    nodesByType[node.type].push(node);
  });

  // Calculate positions
  let xOffset = 0;
  const horizontalSpacing = 300;
  const verticalSpacing = 150;

  typeOrder.forEach((type) => {
    const typeNodes = nodesByType[type] || [];
    if (typeNodes.length === 0) return;

    typeNodes.forEach((node, index) => {
      positions[node.id] = {
        x: xOffset,
        y: index * verticalSpacing,
      };
    });

    xOffset += horizontalSpacing;
  });

  return positions;
}

/**
 * Get unique node types from nodes
 */
function getUniqueNodeTypes(nodes: LineageVisualization['lineage_graph']['nodes']): string[] {
  const types = new Set(nodes.map((node) => node.type));
  return Array.from(types);
}
