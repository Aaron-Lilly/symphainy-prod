"use client";

import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Workflow, 
  AlertTriangle, 
  CheckCircle2, 
  Circle,
  Users,
  Sparkles,
  Handshake
} from "lucide-react";
import ChartComponent from "@/components/ui/chart";
import dynamic from "next/dynamic";

const GraphComponent = dynamic(
  () => import("@/components/operations/GraphComponent"),
  { ssr: false }
);

interface JourneyFrictionRemovalProps {
  coexistence_analysis: {
    friction_points_identified: number;
    friction_points_removed: number;
    human_focus_areas: number;
    workflow_comparison?: {
      before?: {
        workflow_id?: string;
        friction_points?: Array<{
          task?: string;
          friction_type?: string;
        }>;
      };
      after?: {
        workflow_id?: string;
        ai_assistance_points?: Array<{
          task?: string;
          assistance_type?: string;
        }>;
      };
    };
    coexistence_breakdown: {
      human_tasks: number;
      ai_assisted_tasks: number;
      hybrid_tasks: number;
      total_tasks: number;
    };
    workflow_preview?: {
      workflow_id?: string;
      status: string;
    };
  };
}

export default function JourneyFrictionRemoval({ coexistence_analysis }: JourneyFrictionRemovalProps) {
  const breakdown = coexistence_analysis.coexistence_breakdown;
  const comparison = coexistence_analysis.workflow_comparison;

  // Prepare coexistence breakdown chart data
  const coexistenceData = [
    { name: "Human Tasks", value: breakdown.human_tasks, color: "#3b82f6" },
    { name: "AI-Assisted Tasks", value: breakdown.ai_assisted_tasks, color: "#10b981" },
    { name: "Hybrid Tasks", value: breakdown.hybrid_tasks, color: "#8b5cf6" },
  ].filter(item => item.value > 0);

  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle>Journey Pillar - Coexistence Analysis</CardTitle>
        <CardDescription>
          AI removes friction so humans can focus on high-value work
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Friction Removal Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="border-orange-200 bg-orange-50">
              <CardContent className="p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <AlertTriangle className="w-5 h-5 text-orange-600" />
                  <span className="text-sm font-semibold">Friction Points Identified</span>
                </div>
                <div className="text-3xl font-bold text-orange-600">
                  {coexistence_analysis.friction_points_identified}
                </div>
              </CardContent>
            </Card>

            <Card className="border-green-200 bg-green-50">
              <CardContent className="p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <CheckCircle2 className="w-5 h-5 text-green-600" />
                  <span className="text-sm font-semibold">Friction Removed</span>
                </div>
                <div className="text-3xl font-bold text-green-600">
                  {coexistence_analysis.friction_points_removed}
                </div>
              </CardContent>
            </Card>

            <Card className="border-blue-200 bg-blue-50">
              <CardContent className="p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <Users className="w-5 h-5 text-blue-600" />
                  <span className="text-sm font-semibold">Human Focus Areas</span>
                </div>
                <div className="text-3xl font-bold text-blue-600">
                  {coexistence_analysis.human_focus_areas}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Coexistence Breakdown */}
          <Card className="border-purple-200">
            <CardHeader>
              <CardTitle className="text-base">Task Distribution</CardTitle>
              <CardDescription>
                How tasks are distributed between humans and AI
              </CardDescription>
            </CardHeader>
            <CardContent>
              {coexistenceData.length > 0 ? (
                <div className="space-y-4">
                  <div className="h-48">
                    <ChartComponent
                      data={coexistenceData}
                      config={{
                        type: "pie",
                        library: "recharts",
                        height: 180,
                        dataKey: "value",
                        xAxisKey: "name",
                        colors: coexistenceData.map(d => d.color),
                        showLegend: true,
                        showTooltip: true,
                      }}
                    />
                  </div>
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div>
                      <div className="flex items-center justify-center space-x-2 mb-1">
                        <Users className="w-4 h-4 text-blue-600" />
                        <span className="text-sm font-semibold">Human</span>
                      </div>
                      <div className="text-2xl font-bold text-blue-600">
                        {breakdown.human_tasks}%
                      </div>
                    </div>
                    <div>
                      <div className="flex items-center justify-center space-x-2 mb-1">
                        <Sparkles className="w-4 h-4 text-green-600" />
                        <span className="text-sm font-semibold">AI-Assisted</span>
                      </div>
                      <div className="text-2xl font-bold text-green-600">
                        {breakdown.ai_assisted_tasks}%
                      </div>
                    </div>
                    <div>
                      <div className="flex items-center justify-center space-x-2 mb-1">
                        <Handshake className="w-4 h-4 text-purple-600" />
                        <span className="text-sm font-semibold">Hybrid</span>
                      </div>
                      <div className="text-2xl font-bold text-purple-600">
                        {breakdown.hybrid_tasks}%
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-400">
                  <Circle className="w-8 h-8 mx-auto mb-2" />
                  <p className="text-sm">No coexistence data available</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Workflow Comparison */}
          {comparison && (comparison.before || comparison.after) && (
            <Card className="border-indigo-200">
              <CardHeader>
                <CardTitle className="text-base">Workflow Optimization</CardTitle>
                <CardDescription>
                  Before and after friction removal
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Before */}
                  {comparison.before && (
                    <div className="space-y-3">
                      <h4 className="font-semibold text-sm flex items-center space-x-2">
                        <AlertTriangle className="w-4 h-4 text-orange-600" />
                        <span>Before: Friction Points</span>
                      </h4>
                      {comparison.before.friction_points && comparison.before.friction_points.length > 0 ? (
                        <div className="space-y-2">
                          {comparison.before.friction_points.map((fp, idx) => (
                            <div key={idx} className="p-3 bg-orange-50 rounded-lg border border-orange-200">
                              <div className="text-sm font-medium">{fp.task || `Task ${idx + 1}`}</div>
                              <div className="text-xs text-gray-600 mt-1">
                                {fp.friction_type || "Friction point identified"}
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-sm text-gray-500 italic">No friction points identified</div>
                      )}
                    </div>
                  )}

                  {/* After */}
                  {comparison.after && (
                    <div className="space-y-3">
                      <h4 className="font-semibold text-sm flex items-center space-x-2">
                        <CheckCircle2 className="w-4 h-4 text-green-600" />
                        <span>After: AI Assistance</span>
                      </h4>
                      {comparison.after.ai_assistance_points && comparison.after.ai_assistance_points.length > 0 ? (
                        <div className="space-y-2">
                          {comparison.after.ai_assistance_points.map((ap, idx) => (
                            <div key={idx} className="p-3 bg-green-50 rounded-lg border border-green-200">
                              <div className="text-sm font-medium">{ap.task || `Task ${idx + 1}`}</div>
                              <div className="text-xs text-gray-600 mt-1">
                                {ap.assistance_type || "AI assistance provided"}
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-sm text-gray-500 italic">No AI assistance points</div>
                      )}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Human-Positive Messaging */}
          <Card className="border-blue-200 bg-blue-50">
            <CardContent className="p-4">
              <div className="flex items-start space-x-3">
                <Users className="w-6 h-6 text-blue-600 flex-shrink-0 mt-1" />
                <div>
                  <h4 className="font-semibold text-blue-900 mb-2">Human-Positive Approach</h4>
                  <p className="text-sm text-blue-800">
                    AI doesn't replace humans - it removes friction so you can focus on high-value work like 
                    decision-making, strategic analysis, and creative problem-solving. The platform identifies 
                    repetitive tasks and automates them, freeing you to do what humans do best.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </CardContent>
    </Card>
  );
}
