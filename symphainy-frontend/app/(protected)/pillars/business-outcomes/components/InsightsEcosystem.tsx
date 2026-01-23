"use client";

import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  BarChart3, 
  Target, 
  FileText, 
  CheckCircle2, 
  Circle,
  TrendingUp,
  Network
} from "lucide-react";
import ChartComponent from "@/components/ui/chart";

interface InsightsEcosystemProps {
  capabilities: {
    quality_assessment?: {
      overall_score: number;
      breakdown: {
        completeness: number;
        accuracy: number;
        consistency: number;
        timeliness: number;
      };
      status: string;
    };
    business_analysis?: {
      insights_count: number;
      patterns_identified: number;
      trends_detected: number;
      status: string;
    };
    specialized_pipelines?: {
      pso?: {
        name: string;
        icon: string;
        active: boolean;
        insights_count: number;
        status: string;
      };
      aar?: {
        name: string;
        icon: string;
        active: boolean;
        insights_count: number;
        status: string;
      };
      variable_life?: {
        name: string;
        icon: string;
        active: boolean;
        insights_count: number;
        status: string;
      };
    };
    relationship_graph?: {
      nodes_count: number;
      edges_count: number;
      preview_size: string;
      status: string;
    };
  };
}

const iconMap: Record<string, React.ComponentType<any>> = {
  permit: FileText,
  report: FileText,
  policy: FileText,
};

export default function InsightsEcosystem({ capabilities }: InsightsEcosystemProps) {
  const quality = capabilities.quality_assessment;
  const business = capabilities.business_analysis;
  const pipelines = capabilities.specialized_pipelines;
  const relationships = capabilities.relationship_graph;

  // Prepare quality breakdown chart data
  const qualityBreakdownData = quality?.breakdown ? [
    { name: "Completeness", value: Math.round(quality.breakdown.completeness * 100) },
    { name: "Accuracy", value: Math.round(quality.breakdown.accuracy * 100) },
    { name: "Consistency", value: Math.round(quality.breakdown.consistency * 100) },
    { name: "Timeliness", value: Math.round(quality.breakdown.timeliness * 100) },
  ] : [];

  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle>Insights Pillar - Capabilities Showcase</CardTitle>
        <CardDescription>
          Quality assessment, business analysis, specialized pipelines, and relationship mapping
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          {/* Quality Assessment Card */}
          <Card className="border-green-200">
            <CardHeader className="pb-3">
              <div className="flex items-center space-x-2">
                <BarChart3 className="w-5 h-5 text-green-600" />
                <CardTitle className="text-base">Quality Assessment</CardTitle>
                {quality?.status === "complete" ? (
                  <CheckCircle2 className="w-4 h-4 text-green-600" />
                ) : (
                  <Circle className="w-4 h-4 text-gray-400" />
                )}
              </div>
            </CardHeader>
            <CardContent>
              {quality ? (
                <div className="space-y-4">
                  {/* Overall Score Gauge */}
                  <div className="text-center">
                    <div className="relative inline-block">
                      <div className="text-4xl font-bold text-green-600">
                        {quality.overall_score}%
                      </div>
                      <div className="text-xs text-gray-600 mt-1">Overall Quality</div>
                    </div>
                  </div>
                  
                  {/* Quality Breakdown Chart */}
                  {qualityBreakdownData.length > 0 && (
                    <div className="h-32">
                      <ChartComponent
                        data={qualityBreakdownData}
                        config={{
                          type: "bar",
                          library: "recharts",
                          height: 120,
                          dataKey: "value",
                          xAxisKey: "name",
                          colors: ["#10b981"],
                          showLegend: false,
                          showGrid: true,
                        }}
                      />
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-400">
                  <Circle className="w-8 h-8 mx-auto mb-2" />
                  <p className="text-sm">No quality data available</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Business Analysis Card */}
          <Card className="border-blue-200">
            <CardHeader className="pb-3">
              <div className="flex items-center space-x-2">
                <TrendingUp className="w-5 h-5 text-blue-600" />
                <CardTitle className="text-base">Business Analysis</CardTitle>
                {business?.status === "complete" ? (
                  <CheckCircle2 className="w-4 h-4 text-green-600" />
                ) : (
                  <Circle className="w-4 h-4 text-gray-400" />
                )}
              </div>
            </CardHeader>
            <CardContent>
              {business ? (
                <div className="space-y-3">
                  <div className="p-3 bg-blue-50 rounded-lg">
                    <div className="text-sm text-gray-600 mb-1">Insights Generated</div>
                    <div className="text-2xl font-bold text-blue-600">
                      {business.insights_count}
                    </div>
                  </div>
                  <div className="p-3 bg-blue-50 rounded-lg">
                    <div className="text-sm text-gray-600 mb-1">Patterns Identified</div>
                    <div className="text-2xl font-bold text-blue-600">
                      {business.patterns_identified}
                    </div>
                  </div>
                  <div className="p-3 bg-blue-50 rounded-lg">
                    <div className="text-sm text-gray-600 mb-1">Trends Detected</div>
                    <div className="text-2xl font-bold text-blue-600">
                      {business.trends_detected}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-400">
                  <Circle className="w-8 h-8 mx-auto mb-2" />
                  <p className="text-sm">No business analysis data</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Specialized Pipelines Card */}
          <Card className="border-purple-200">
            <CardHeader className="pb-3">
              <div className="flex items-center space-x-2">
                <Target className="w-5 h-5 text-purple-600" />
                <CardTitle className="text-base">Specialized Pipelines</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              {pipelines ? (
                <div className="space-y-3">
                  {pipelines.pso && (
                    <div className={`p-3 rounded-lg border ${
                      pipelines.pso.active ? "bg-purple-50 border-purple-200" : "bg-gray-50 border-gray-200"
                    }`}>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <FileText className="w-4 h-4 text-purple-600" />
                          <span className="text-sm font-medium">{pipelines.pso.name}</span>
                        </div>
                        {pipelines.pso.active ? (
                          <Badge variant="outline" className="bg-green-100">
                            {pipelines.pso.insights_count} insights
                          </Badge>
                        ) : (
                          <Badge variant="outline">Inactive</Badge>
                        )}
                      </div>
                    </div>
                  )}
                  {pipelines.aar && (
                    <div className={`p-3 rounded-lg border ${
                      pipelines.aar.active ? "bg-purple-50 border-purple-200" : "bg-gray-50 border-gray-200"
                    }`}>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <FileText className="w-4 h-4 text-purple-600" />
                          <span className="text-sm font-medium">{pipelines.aar.name}</span>
                        </div>
                        {pipelines.aar.active ? (
                          <Badge variant="outline" className="bg-green-100">
                            {pipelines.aar.insights_count} insights
                          </Badge>
                        ) : (
                          <Badge variant="outline">Inactive</Badge>
                        )}
                      </div>
                    </div>
                  )}
                  {pipelines.variable_life && (
                    <div className={`p-3 rounded-lg border ${
                      pipelines.variable_life.active ? "bg-purple-50 border-purple-200" : "bg-gray-50 border-gray-200"
                    }`}>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <FileText className="w-4 h-4 text-purple-600" />
                          <span className="text-sm font-medium">{pipelines.variable_life.name}</span>
                        </div>
                        {pipelines.variable_life.active ? (
                          <Badge variant="outline" className="bg-green-100">
                            {pipelines.variable_life.insights_count} insights
                          </Badge>
                        ) : (
                          <Badge variant="outline">Inactive</Badge>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-400">
                  <Circle className="w-8 h-8 mx-auto mb-2" />
                  <p className="text-sm">No specialized pipelines</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Relationship Graph Preview */}
        {relationships && (
          <Card className="border-indigo-200">
            <CardHeader className="pb-3">
              <div className="flex items-center space-x-2">
                <Network className="w-5 h-5 text-indigo-600" />
                <CardTitle className="text-base">Relationship Graph</CardTitle>
                {relationships.status === "complete" ? (
                  <CheckCircle2 className="w-4 h-4 text-green-600" />
                ) : (
                  <Circle className="w-4 h-4 text-gray-400" />
                )}
              </div>
            </CardHeader>
            <CardContent>
              {relationships.status === "complete" ? (
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Nodes (Entities)</span>
                    <span className="font-semibold">{relationships.nodes_count}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Edges (Relationships)</span>
                    <span className="font-semibold">{relationships.edges_count}</span>
                  </div>
                  <div className="mt-4 p-4 bg-indigo-50 rounded-lg text-center">
                    <Network className="w-12 h-12 mx-auto text-indigo-400 mb-2" />
                    <p className="text-sm text-gray-600">
                      Relationship graph visualization available
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      Click to explore full graph in Insights pillar
                    </p>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-400">
                  <Circle className="w-8 h-8 mx-auto mb-2" />
                  <p className="text-sm">No relationship data available</p>
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </CardContent>
    </Card>
  );
}
