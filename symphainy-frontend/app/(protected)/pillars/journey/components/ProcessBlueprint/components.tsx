// ProcessBlueprint UI Components
"use client";
import React from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { FileText, Workflow, ArrowRight } from "lucide-react";
import ReactMarkdown from "react-markdown";
import dynamic from "next/dynamic";
import { ProcessBlueprintUIProps } from "./types";

const GraphComponent = dynamic(
  () => import("@/components/operations/GraphComponent"),
  {
    ssr: false,
    loading: () => (
      <div className="flex items-center justify-center h-full">
        Loading graph...
      </div>
    ),
  },
);

export function ProcessBlueprintUI({
  sopContent,
  workflowContent,
  workflowData,
  analysisResults,
  isLoading,
  onGenerateWorkflowFromSop,
  onGenerateSopFromWorkflow,
  formatSOPContent,
  getSafeTextContent,
}: ProcessBlueprintUIProps) {
  const hasSopContent = sopContent && sopContent !== "No SOP content available";
  const hasWorkflowContent = workflowContent && workflowContent !== "No workflow content available";

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Process Blueprint</h2>
          <p className="text-gray-600 mt-1">
            View and manage SOP and workflow conversions
          </p>
        </div>
        <div className="flex space-x-2">
          {hasSopContent && onGenerateWorkflowFromSop && (
            <Button
              onClick={onGenerateWorkflowFromSop}
              disabled={isLoading}
              className="bg-blue-600 hover:bg-blue-700"
            >
              <FileText className="w-4 h-4 mr-2" />
              Generate Workflow
            </Button>
          )}
          {hasWorkflowContent && onGenerateSopFromWorkflow && (
            <Button
              onClick={onGenerateSopFromWorkflow}
              disabled={isLoading}
              variant="outline"
            >
              <Workflow className="w-4 h-4 mr-2" />
              Generate SOP
            </Button>
          )}
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <span className="ml-3 text-gray-600">Processing...</span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Analysis Results */}
      {analysisResults && (
        <Card className="border-yellow-200 bg-yellow-50">
          <CardHeader>
            <CardTitle className="flex items-center text-yellow-800">
              <span className="text-lg">Analysis Results</span>
              {analysisResults.analysisType && (
                <Badge variant="secondary" className="ml-2">
                  {analysisResults.analysisType}
                </Badge>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {analysisResults.errors && analysisResults.errors.length > 0 && (
              <div className="space-y-2">
                <h4 className="font-semibold text-yellow-800">Issues Found:</h4>
                <ul className="list-disc list-inside space-y-1 text-yellow-700">
                  {analysisResults.errors.map((error, index) => (
                    <li key={index}>
                      <strong>{error.type}:</strong> {error.error}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Content Display */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* SOP Content */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <FileText className="w-5 h-5 mr-2" />
              <span className="text-lg">Standard Operating Procedure</span>
            </CardTitle>
            <CardDescription>
              Documented process steps and procedures
            </CardDescription>
          </CardHeader>
          <CardContent>
            {hasSopContent ? (
              <div className="max-h-96 overflow-y-auto">
                <ReactMarkdown className="prose prose-sm max-w-none">
                  {sopContent}
                </ReactMarkdown>
              </div>
            ) : (
              <EmptyState
                icon={<FileText className="w-12 h-12 text-gray-400" />}
                title="No SOP Content"
                description="Upload or generate an SOP to get started"
              />
            )}
          </CardContent>
        </Card>

        {/* Workflow Content */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Workflow className="w-5 h-5 mr-2" />
              <span className="text-lg">Process Workflow</span>
            </CardTitle>
            <CardDescription>
              Visual workflow diagram and process flow
            </CardDescription>
          </CardHeader>
          <CardContent>
            {hasWorkflowContent ? (
              <div className="max-h-96 overflow-y-auto">
                <ReactMarkdown className="prose prose-sm max-w-none">
                  {workflowContent}
                </ReactMarkdown>
              </div>
            ) : (
              <EmptyState
                icon={<Workflow className="w-12 h-12 text-gray-400" />}
                title="No Workflow Content"
                description="Generate a workflow from SOP or upload existing workflow"
              />
            )}
          </CardContent>
        </Card>
      </div>

      {/* Conversion Actions */}
      {(hasSopContent || hasWorkflowContent) && (
        <Card>
          <CardHeader>
            <CardTitle>Conversion Actions</CardTitle>
            <CardDescription>
              Convert between SOP and workflow formats
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col sm:flex-row gap-4">
              {hasSopContent && onGenerateWorkflowFromSop && (
                <Button
                  onClick={onGenerateWorkflowFromSop}
                  disabled={isLoading}
                  className="flex-1"
                  variant="outline"
                >
                  <FileText className="w-4 h-4 mr-2" />
                  <span>SOP to Workflow</span>
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              )}
              {hasWorkflowContent && onGenerateSopFromWorkflow && (
                <Button
                  onClick={onGenerateSopFromWorkflow}
                  disabled={isLoading}
                  className="flex-1"
                  variant="outline"
                >
                  <Workflow className="w-4 h-4 mr-2" />
                  <span>Workflow to SOP</span>
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Graph Visualization */}
      {hasWorkflowContent && (
        <Card>
          <CardHeader>
            <CardTitle>Workflow Visualization</CardTitle>
            <CardDescription>
              Interactive workflow diagram
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-96">
              <GraphComponent data={workflowData} />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Empty State */}
      {!hasSopContent && !hasWorkflowContent && !isLoading && (
        <Card>
          <CardContent className="pt-6">
            <EmptyState
              icon={<FileText className="w-12 h-12 text-gray-400" />}
              title="No Process Content"
              description="Upload files or generate content to get started with process blueprint"
            />
          </CardContent>
        </Card>
      )}
    </div>
  );
} 