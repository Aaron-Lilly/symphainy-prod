// components/operations/CustomNode.tsx
import React from "react";
import { Handle, Position } from "reactflow";

export default function CustomNode({ data }: any) {
  return (
    <div className="rounded-xl border border-gray-300 shadow-md bg-white p-4 w-64 text-left">
      <div className="font-bold text-sm mb-1">{data.title}</div>
      <div className="text-xs text-gray-600 whitespace-pre-wrap">
        {data.description}
      </div>
      <Handle type="target" position={Position.Top} />
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}
