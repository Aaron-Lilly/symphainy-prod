"use client";

import React, { useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  MarkerType,
  Position,
} from 'reactflow';
import 'reactflow/dist/style.css';

interface Relationship {
  source: string;
  target: string;
  type: string;
  confidence?: number;
  attributes?: Record<string, any>;
}

interface Entity {
  name: string;
  type: string;
  attributes?: Record<string, any>;
}

interface RelationshipData {
  entities?: Entity[];
  relationships?: Relationship[];
}

interface RelationshipGraphProps {
  relationships: RelationshipData;
}

/**
 * ✅ PHASE 4.3: Relationship Graph Visualization Component
 * 
 * Interactive graph visualization showing entity relationships
 * - Uses react-flow for interactive exploration
 * - Shows relationship types and confidence scores
 * - Allows relationship exploration
 */
export function RelationshipGraph({ relationships }: RelationshipGraphProps) {
  const { nodes, edges } = useMemo(() => {
    const flowNodes: Node[] = [];
    const flowEdges: Edge[] = [];
    const nodeMap = new Map<string, Node>();

    // Create nodes from entities
    if (relationships.entities && relationships.entities.length > 0) {
      relationships.entities.forEach((entity, index) => {
        const nodeId = entity.name;
        const position = calculateNodePosition(index, relationships.entities!.length);
        
        const node: Node = {
          id: nodeId,
          type: 'default',
          position,
          data: {
            label: (
              <div className="text-center">
                <div className="font-semibold">{entity.name}</div>
                <Badge variant="secondary" className="mt-1 text-xs">
                  {entity.type}
                </Badge>
              </div>
            ),
            entity,
          },
          style: {
            background: getNodeColor(entity.type),
            color: '#fff',
            border: `2px solid ${getNodeColor(entity.type)}`,
            borderRadius: '8px',
            padding: '10px',
            minWidth: '150px',
          },
        };

        nodeMap.set(nodeId, node);
        flowNodes.push(node);
      });
    }

    // Create edges from relationships
    if (relationships.relationships && relationships.relationships.length > 0) {
      relationships.relationships.forEach((rel, index) => {
        // Ensure source and target nodes exist
        if (!nodeMap.has(rel.source)) {
          const sourceNode: Node = {
            id: rel.source,
            type: 'default',
            position: calculateNodePosition(flowNodes.length, flowNodes.length + 1),
            data: {
              label: (
                <div className="text-center">
                  <div className="font-semibold">{rel.source}</div>
                </div>
              ),
            },
            style: {
              background: '#6b7280',
              color: '#fff',
              border: '2px solid #6b7280',
              borderRadius: '8px',
              padding: '10px',
              minWidth: '150px',
            },
          };
          nodeMap.set(rel.source, sourceNode);
          flowNodes.push(sourceNode);
        }

        if (!nodeMap.has(rel.target)) {
          const targetNode: Node = {
            id: rel.target,
            type: 'default',
            position: calculateNodePosition(flowNodes.length, flowNodes.length + 1),
            data: {
              label: (
                <div className="text-center">
                  <div className="font-semibold">{rel.target}</div>
                </div>
              ),
            },
            style: {
              background: '#6b7280',
              color: '#fff',
              border: '2px solid #6b7280',
              borderRadius: '8px',
              padding: '10px',
              minWidth: '150px',
            },
          };
          nodeMap.set(rel.target, targetNode);
          flowNodes.push(targetNode);
        }

        const edge: Edge = {
          id: `${rel.source}-${rel.target}-${index}`,
          source: rel.source,
          target: rel.target,
          type: 'smoothstep',
          animated: true,
          markerEnd: {
            type: MarkerType.ArrowClosed,
          },
          label: (
            <div className="text-center">
              <div className="text-xs font-semibold">{rel.type}</div>
              {rel.confidence !== undefined && (
                <div className="text-xs text-gray-600">
                  {Math.round(rel.confidence * 100)}%
                </div>
              )}
            </div>
          ),
          style: {
            strokeWidth: 2,
            stroke: getEdgeColor(rel.type),
          },
        };

        flowEdges.push(edge);
      });
    }

    return { nodes: flowNodes, edges: flowEdges };
  }, [relationships]);

  return (
    <Card className="border-2 border-purple-200">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <span>Relationship Graph</span>
          <Badge variant="secondary">
            {nodes.length} entities, {edges.length} relationships
          </Badge>
        </CardTitle>
        <CardDescription>
          Interactive visualization of entity relationships. Click and drag to explore.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {nodes.length > 0 ? (
          <div className="border rounded-lg overflow-hidden" style={{ height: '600px' }}>
            <ReactFlow
              nodes={nodes}
              edges={edges}
              fitView
              fitViewOptions={{ padding: 0.2 }}
              attributionPosition="bottom-left"
            >
              <Background variant="dots" gap={20} size={1} />
              <Controls />
              <MiniMap 
                nodeColor={(node) => {
                  const nodeData = node.data as any;
                  return nodeData.entity ? getNodeColor(nodeData.entity.type) : '#6b7280';
                }}
                maskColor="rgba(0, 0, 0, 0.1)"
              />
            </ReactFlow>
          </div>
        ) : (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <p className="text-sm text-gray-600">No relationships found to visualize.</p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

/**
 * Calculate node position in a circular layout
 */
function calculateNodePosition(index: number, total: number): { x: number; y: number } {
  const radius = 200;
  const angle = (2 * Math.PI * index) / total;
  return {
    x: radius * Math.cos(angle) + 400,
    y: radius * Math.sin(angle) + 300,
  };
}

/**
 * Get color for node based on entity type
 */
function getNodeColor(type: string): string {
  const colorMap: Record<string, string> = {
    person: '#3b82f6',
    organization: '#10b981',
    location: '#f59e0b',
    product: '#8b5cf6',
    event: '#ef4444',
    document: '#06b6d4',
    default: '#6b7280',
  };
  return colorMap[type.toLowerCase()] || colorMap.default;
}

/**
 * Get color for edge based on relationship type
 */
function getEdgeColor(type: string): string {
  const colorMap: Record<string, string> = {
    'works_for': '#3b82f6',
    'located_in': '#10b981',
    'related_to': '#8b5cf6',
    'part_of': '#f59e0b',
    'owns': '#ef4444',
    default: '#6b7280',
  };
  return colorMap[type.toLowerCase()] || colorMap.default;
}
