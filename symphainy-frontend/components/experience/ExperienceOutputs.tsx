import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { FileText, Download, Calendar, Target, CheckCircle } from "lucide-react";
import RoadmapTimeline from "./RoadmapTimeline";
import dynamic from "next/dynamic";

const GraphComponent = dynamic(
  () => import("@/components/operations/GraphComponent"),
  {
    ssr: false,
    loading: () => <div className="animate-pulse bg-gray-200 h-64 rounded"></div>,
  },
);

interface ExperienceOutputsProps {
  roadmap: string;
  poc: any;
  generatedAt?: string;
  onDownloadPOC?: () => void;
  onDownloadRoadmap?: () => void;
}

export default function ExperienceOutputs({
  roadmap,
  poc,
  generatedAt,
  onDownloadPOC,
  onDownloadRoadmap
}: ExperienceOutputsProps) {
  const formatDate = (dateString?: string) => {
    if (!dateString) return "Unknown";
    return new Date(dateString).toLocaleString();
  };

  const parseRoadmapPhases = (roadmapText: string) => {
    // Simple parsing logic - can be enhanced based on actual roadmap format
    const phases = roadmapText.split(/(?=Phase \d+)/).filter(phase => phase.trim());
    return phases.map((phase, index) => ({
      id: index,
      title: `Phase ${index + 1}`,
      content: phase.trim()
    }));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Experience Outcomes</h2>
          <p className="text-gray-600">Your generated roadmap and POC proposal</p>
        </div>
        {generatedAt && (
          <div className="text-sm text-gray-500">
            Generated: {formatDate(generatedAt)}
          </div>
        )}
      </div>

      {/* Roadmap Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Calendar className="h-5 w-5 text-blue-600" />
            <span>Implementation Roadmap</span>
            {onDownloadRoadmap && (
              <Button
                variant="outline"
                size="sm"
                onClick={onDownloadRoadmap}
                className="ml-auto"
              >
                <Download className="h-4 w-4 mr-2" />
                Download
              </Button>
            )}
          </CardTitle>
          <CardDescription>
            Step-by-step implementation plan based on your requirements
          </CardDescription>
        </CardHeader>
        <CardContent>
          {roadmap ? (
            <div className="space-y-4">
              <RoadmapTimeline roadmapData={roadmap} />
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              No roadmap available
            </div>
          )}
        </CardContent>
      </Card>

      {/* POC Section */}
      {poc && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Target className="h-5 w-5 text-green-600" />
              <span>POC Proposal</span>
              {onDownloadPOC && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={onDownloadPOC}
                  className="ml-auto"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Download
                </Button>
              )}
            </CardTitle>
            <CardDescription>
              Proof of Concept proposal with timeline, budget, and success metrics
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {/* POC Summary */}
              {poc.executive_summary && (
                <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <h4 className="font-semibold text-blue-900 mb-2">Executive Summary</h4>
                  <p className="text-blue-800">{poc.executive_summary}</p>
                </div>
              )}

              {/* Timeline */}
              {poc.timeline && (
                <div className="space-y-3">
                  <h4 className="font-semibold text-gray-900">Timeline</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <div className="text-sm text-gray-600">Duration</div>
                      <div className="font-medium">{poc.timeline.total_duration_days} days</div>
                    </div>
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <div className="text-sm text-gray-600">Start Date</div>
                      <div className="font-medium">{poc.timeline.start_date}</div>
                    </div>
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <div className="text-sm text-gray-600">End Date</div>
                      <div className="font-medium">{poc.timeline.end_date}</div>
                    </div>
                  </div>
                </div>
              )}

              {/* Budget */}
              {poc.budget && (
                <div className="space-y-3">
                  <h4 className="font-semibold text-gray-900">Budget</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-3 bg-green-50 rounded-lg border border-green-200">
                      <div className="text-sm text-green-600">Total Cost</div>
                      <div className="font-medium text-green-800">
                        {poc.budget.currency} {poc.budget.total_cost.toLocaleString()}
                      </div>
                    </div>
                    <div className="p-3 bg-green-50 rounded-lg border border-green-200">
                      <div className="text-sm text-green-600">Payment Schedule</div>
                      <div className="font-medium text-green-800">
                        {poc.budget.payment_schedule?.length || 0} milestones
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Success Metrics */}
              {poc.success_metrics && poc.success_metrics.length > 0 && (
                <div className="space-y-3">
                  <h4 className="font-semibold text-gray-900">Success Metrics</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {poc.success_metrics.map((metric: string, index: number) => (
                      <div key={index} className="flex items-center space-x-2 p-2 bg-gray-50 rounded">
                        <CheckCircle className="h-4 w-4 text-green-500" />
                        <span className="text-sm">{metric}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Resource Requirements */}
              {poc.resource_requirements && (
                <div className="space-y-3">
                  <h4 className="font-semibold text-gray-900">Resource Requirements</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {poc.resource_requirements.client_team && (
                      <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                        <h5 className="font-medium text-blue-900 mb-2">Client Team</h5>
                        <ul className="text-sm text-blue-800 space-y-1">
                          {poc.resource_requirements.client_team.map((member: string, index: number) => (
                            <li key={index}>• {member}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {poc.resource_requirements.symphainy_team && (
                      <div className="p-3 bg-purple-50 rounded-lg border border-purple-200">
                        <h5 className="font-medium text-purple-900 mb-2">SymphAIny Team</h5>
                        <ul className="text-sm text-purple-800 space-y-1">
                          {poc.resource_requirements.symphainy_team.map((member: string, index: number) => (
                            <li key={index}>• {member}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Next Steps */}
              {poc.next_steps && (
                <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                  <h4 className="font-semibold text-yellow-900 mb-2">Next Steps</h4>
                  <p className="text-yellow-800">{poc.next_steps}</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Raw Data View (for debugging) */}
      <details className="mt-6">
        <summary className="cursor-pointer text-sm text-gray-500 hover:text-gray-700">
          View Raw Data
        </summary>
        <div className="mt-2 p-4 bg-gray-100 rounded-lg">
          <pre className="text-xs overflow-auto">
            {JSON.stringify({ roadmap, poc, generatedAt }, null, 2)}
          </pre>
        </div>
      </details>
    </div>
  );
}