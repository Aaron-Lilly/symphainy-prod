// CoexistenceBlueprint UI Components
"use client";
import React from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useAtomValue } from "jotai";
import ReactMarkdown from "react-markdown";
import dynamic from "next/dynamic";
import { CoexistenceBlueprintUIProps } from "./types";

// Dynamic import for GraphComponent
const GraphComponent = dynamic(
  () => import("@/components/operations/GraphComponent"),
  { ssr: false }
);

export function CoexistenceBlueprintUI({
  loading,
  error,
  optimizedSop,
  optimizedWorkflow,
  blueprint,
  sopText,
  workflowData,
  isEnabled,
  onOptimize,
  onSaveBlueprint,
  formatSOPContent,
  formatWorkflowContent,
  getSafeFormattedContent,
}: CoexistenceBlueprintUIProps) {
  const sopContent = getSafeFormattedContent(sopText, 'sop');
  const workflowContent = getSafeFormattedContent(workflowData, 'workflow');

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Coexistence Blueprint</h2>
          <p className="text-gray-600 mt-1">
            Optimize SOP and workflow coexistence for better process efficiency
          </p>
        </div>
        <div className="flex space-x-2">
          <Button
            onClick={onOptimize}
            disabled={!isEnabled || loading}
            className="bg-blue-600 hover:bg-blue-700"
          >
            {loading ? "Optimizing..." : "Optimize Coexistence"}
          </Button>
          {blueprint && (
            <Button
              onClick={onSaveBlueprint}
              disabled={loading}
              variant="outline"
            >
              Save Blueprint
            </Button>
          )}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="text-red-800">
              <strong>Error:</strong> {error}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Loading State */}
      {loading && (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <span className="ml-3 text-gray-600">Optimizing coexistence...</span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Input Content Display */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* SOP Content */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <span className="text-lg">Current SOP</span>
            </CardTitle>
            <CardDescription>
              Standard Operating Procedure content
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="max-h-96 overflow-y-auto">
              <ReactMarkdown className="prose prose-sm max-w-none">
                {sopContent}
              </ReactMarkdown>
            </div>
          </CardContent>
        </Card>

        {/* Workflow Content */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <span className="text-lg">Current Workflow</span>
            </CardTitle>
            <CardDescription>
              Process workflow diagram and structure
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="max-h-96 overflow-y-auto">
              <ReactMarkdown className="prose prose-sm max-w-none">
                {workflowContent}
              </ReactMarkdown>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Optimized Results */}
      {(optimizedSop || optimizedWorkflow) && (
        <div className="space-y-6">
          <h3 className="text-xl font-semibold text-gray-800">Optimized Results</h3>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Optimized SOP */}
            {optimizedSop && (
              <Card className="border-green-200 bg-green-50">
                <CardHeader>
                  <CardTitle className="flex items-center text-green-800">
                    <span className="text-lg">Optimized SOP</span>
                  </CardTitle>
                  <CardDescription className="text-green-700">
                    Enhanced Standard Operating Procedure
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="max-h-96 overflow-y-auto">
                    <ReactMarkdown className="prose prose-sm max-w-none">
                      {optimizedSop}
                    </ReactMarkdown>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Optimized Workflow */}
            {optimizedWorkflow && (
              <Card className="border-green-200 bg-green-50">
                <CardHeader>
                  <CardTitle className="flex items-center text-green-800">
                    <span className="text-lg">Optimized Workflow</span>
                  </CardTitle>
                  <CardDescription className="text-green-700">
                    Enhanced process workflow
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="max-h-96 overflow-y-auto">
                    <ReactMarkdown className="prose prose-sm max-w-none">
                      {formatWorkflowContent(optimizedWorkflow)}
                    </ReactMarkdown>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      )}

      {/* Blueprint Display */}
      {blueprint && (
        <Card className="border-blue-200 bg-blue-50">
          <CardHeader>
            <CardTitle className="flex items-center text-blue-800">
              <span className="text-lg">Coexistence Blueprint</span>
            </CardTitle>
            <CardDescription className="text-blue-700">
              Implementation plan and recommendations
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Blueprint Summary */}
              {blueprint.summary && (
                <div>
                  <h4 className="font-semibold text-blue-800 mb-2">Summary</h4>
                  <p className="text-blue-700">{blueprint.summary}</p>
                </div>
              )}

              {/* Recommendations */}
              {blueprint.recommendations && blueprint.recommendations.length > 0 && (
                <div>
                  <h4 className="font-semibold text-blue-800 mb-2">Recommendations</h4>
                  <ul className="list-disc list-inside space-y-1 text-blue-700">
                    {blueprint.recommendations.map((rec: string, index: number) => (
                      <li key={index}>{rec}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Implementation Steps */}
              {blueprint.implementationSteps && blueprint.implementationSteps.length > 0 && (
                <div>
                  <h4 className="font-semibold text-blue-800 mb-2">Implementation Steps</h4>
                  <ol className="list-decimal list-inside space-y-1 text-blue-700">
                    {blueprint.implementationSteps.map((step: string, index: number) => (
                      <li key={index}>{step}</li>
                    ))}
                  </ol>
                </div>
              )}

              {/* Risk Assessment */}
              {blueprint.riskAssessment && (
                <div>
                  <h4 className="font-semibold text-blue-800 mb-2">Risk Assessment</h4>
                  <div className="space-y-2">
                    {Object.entries(blueprint.riskAssessment).map(([level, risks]: [string, any]) => (
                      <div key={level}>
                        <span className="font-medium text-blue-700 capitalize">{level} Risk:</span>
                        <ul className="list-disc list-inside ml-4 text-blue-700">
                          {Array.isArray(risks) && risks.map((risk: string, index: number) => (
                            <li key={index}>{risk}</li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Success Metrics */}
              {blueprint.successMetrics && blueprint.successMetrics.length > 0 && (
                <div>
                  <h4 className="font-semibold text-blue-800 mb-2">Success Metrics</h4>
                  <ul className="list-disc list-inside space-y-1 text-blue-700">
                    {blueprint.successMetrics.map((metric: string, index: number) => (
                      <li key={index}>{metric}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Graph Visualization */}
      {optimizedWorkflow && optimizedWorkflow.nodes && (
        <Card>
          <CardHeader>
            <CardTitle>Workflow Visualization</CardTitle>
            <CardDescription>
              Interactive workflow diagram
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-96">
              <GraphComponent data={optimizedWorkflow} />
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
} 