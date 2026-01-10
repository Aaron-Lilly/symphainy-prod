"use client";
import React from "react";
import ReactFlow, { Background, Controls, Node, Edge } from "reactflow";
import "reactflow/dist/style.css";

interface WorkflowNode {
  id: string;
  data?: {
    label?: string;
  };
  title?: string;
  label?: string;
  description?: string;
}

interface WorkflowEdge {
  from: string;
  to: string;
}

export default function GraphComponent({
  data,
}: {
  data?: { nodes?: WorkflowNode[]; edges?: WorkflowEdge[] };
}) {
  if (!data || !data.nodes || !data.edges) {
    return (
      <div className="text-red-500">Invalid or missing workflow data.</div>
    );
  }

  const nodes: Node[] = data.nodes.map((node, index) => ({
    id: node.id,
    data: {
      label:
        node.data?.label ||
        node.label ||
        `${node.title || "Step"}: ${node.description || ""}`,
    },
    position: { x: 100, y: index * 150 },
    type: "default",
  }));

  const edges: Edge[] = data.edges.map((edge) => ({
    id: `e-${edge.from}-${edge.to}`,
    source: edge.from,
    target: edge.to,
    type: "default",
  }));

  return (
    <div style={{ width: "100%", height: "600px" }}>
      <ReactFlow nodes={nodes} edges={edges} fitView>
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}
