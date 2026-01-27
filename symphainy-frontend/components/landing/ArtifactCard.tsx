"use client";

import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { FileText, Target, Map, CheckCircle2, Clock, Archive } from "lucide-react";

export interface ArtifactCardData {
  id: string;
  type: 'blueprint' | 'poc' | 'roadmap' | 'sop' | 'workflow';
  title: string;
  description?: string;
  status?: 'draft' | 'active' | 'archived';
  createdAt?: string | Date;
  updatedAt?: string | Date;
  metadata?: Record<string, any>;
}

interface ArtifactCardProps {
  artifact: ArtifactCardData;
  onClick?: () => void;
}

const artifactIcons = {
  blueprint: FileText,
  poc: Target,
  roadmap: Map,
  sop: FileText,
  workflow: FileText,
};

const artifactColors = {
  blueprint: "bg-blue-100 text-blue-800",
  poc: "bg-green-100 text-green-800",
  roadmap: "bg-purple-100 text-purple-800",
  sop: "bg-orange-100 text-orange-800",
  workflow: "bg-indigo-100 text-indigo-800",
};

const statusIcons = {
  draft: Clock,
  active: CheckCircle2,
  archived: Archive,
};

const statusColors = {
  draft: "bg-gray-100 text-gray-800",
  active: "bg-green-100 text-green-800",
  archived: "bg-gray-100 text-gray-600",
};

export function ArtifactCard({ artifact, onClick }: ArtifactCardProps) {
  const Icon = artifactIcons[artifact.type] || FileText;
  const StatusIcon = artifact.status ? statusIcons[artifact.status] : null;
  
  // Simple date formatting without date-fns dependency
  const formatDate = (date?: string | Date) => {
    if (!date) return null;
    try {
      const d = new Date(date);
      const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
      return `${months[d.getMonth()]} ${d.getDate()}, ${d.getFullYear()}`;
    } catch {
      return null;
    }
  };

  return (
    <Card 
      className={`cursor-pointer hover:shadow-lg transition-shadow ${onClick ? 'hover:border-blue-500' : ''}`}
      onClick={onClick}
    >
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <Icon className="h-5 w-5 text-gray-600" />
            <CardTitle className="text-lg">{artifact.title}</CardTitle>
          </div>
          <Badge className={artifactColors[artifact.type]}>
            {artifact.type}
          </Badge>
        </div>
        {artifact.description && (
          <CardDescription className="mt-2 line-clamp-2">
            {artifact.description}
          </CardDescription>
        )}
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {artifact.status && StatusIcon && (
              <Badge className={statusColors[artifact.status]} variant="outline">
                <StatusIcon className="h-3 w-3 mr-1" />
                {artifact.status}
              </Badge>
            )}
          </div>
          {artifact.createdAt && (
            <span className="text-xs text-gray-500">
              {formatDate(artifact.createdAt)}
            </span>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
