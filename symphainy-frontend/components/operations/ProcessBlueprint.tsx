"use client";
import React, { useState } from "react";
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

interface ProcessBlueprintProps {
  operationsState?: {
    optimizedWorkflow?: any;
    workflowData?: any;
    optimizedSop?: string;
    sopText?: string;
    analysisResults?: {
      errors?: Array<{ type: string; error: string }>;
      analysisType?: string;
    };
  };
  onGenerateWorkflowFromSop?: () => Promise<void>;
  onGenerateSopFromWorkflow?: () => Promise<void>;
  isLoading?: boolean;
}

export default function ProcessBlueprint({
  operationsState,
  onGenerateWorkflowFromSop,
  onGenerateSopFromWorkflow,
  isLoading = false,
}: ProcessBlueprintProps) {
  console.log("operationsState", operationsState);

  // Helper function to safely extract string content
  const getSafeTextContent = (data: any): string => {
    if (typeof data === "string") {
      // Try to parse as JSON first
      try {
        const parsed = JSON.parse(data);
        // If it's a SOP object, format it nicely
        if (parsed.title && parsed.steps) {
          return formatSOPContent(parsed);
        }
        // If it's other JSON, return as is
        return data;
      } catch {
        // If it's not JSON, return as is
        return data;
      }
    }
    if (typeof data === "object" && data !== null) {
      // If it's an object, try to extract text content or format it
      if (data.sop) {
        if (typeof data.sop === "string") {
          try {
            const parsed = JSON.parse(data.sop);
            if (parsed.title && parsed.steps) {
              return formatSOPContent(parsed);
            }
          } catch {
            return data.sop;
          }
        } else if (data.sop.title && data.sop.steps) {
          return formatSOPContent(data.sop);
        }
      }
      if (data.sopText) {
        if (typeof data.sopText === "string") {
          try {
            const parsed = JSON.parse(data.sopText);
            if (parsed.title && parsed.steps) {
              return formatSOPContent(parsed);
            }
          } catch {
            return data.sopText;
          }
        } else if (data.sopText.title && data.sopText.steps) {
          return formatSOPContent(data.sopText);
        }
      }
      if (data.text) {
        return typeof data.text === "string" ? data.text : JSON.stringify(data.text, null, 2);
      }
      // If no known text property, stringify the whole object
      return JSON.stringify(data, null, 2);
    }
    return String(data || "");
  };

  // Helper function to format SOP content nicely
  const formatSOPContent = (sop: any): string => {
    let formatted = `# ${sop.title}\n\n`;
    
    if (sop.description) {
      formatted += `${sop.description}\n\n`;
    }
    
    if (sop.steps && Array.isArray(sop.steps)) {
      formatted += "## Steps\n\n";
      sop.steps.forEach((step: any) => {
        formatted += `### ${step.step_number}. ${step.title}\n\n`;
        formatted += `${step.description}\n\n`;
        
        if (step.responsible_role) {
          formatted += `**Responsible Role:** ${step.responsible_role}\n\n`;
        }
        
        if (step.expected_output) {
          formatted += `**Expected Output:** ${step.expected_output}\n\n`;
        }
        
        formatted += "---\n\n";
      });
    }
    
    return formatted;
  };

  // Get the SOP text content safely
  const sopContent = getSafeTextContent(
    operationsState?.optimizedSop || operationsState?.sopText,
  );

  // Check if elements exist
  const hasSop = !!sopContent && sopContent.trim() !== "";
  const hasWorkflow = !!(operationsState?.optimizedWorkflow || operationsState?.workflowData);

  // Determine which conditional button to show
  const showGenerateWorkflowButton = hasSop && !hasWorkflow && onGenerateWorkflowFromSop;
  const showGenerateSopButton = hasWorkflow && !hasSop && onGenerateSopFromWorkflow;

  return (
    <div className="space-y-4 mb-26">
      {/* Analysis Status and Errors */}
      {operationsState?.analysisResults?.errors &&
        operationsState.analysisResults.errors.length > 0 && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <svg
                  className="h-5 w-5 text-yellow-400"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-yellow-800">
                  Partial Analysis Results
                </h3>
                <div className="mt-2 text-sm text-yellow-700">
                  <p>
                    Some analyses completed successfully, but others encountered
                    issues:
                  </p>
                  <ul className="mt-2 list-disc list-inside space-y-1">
                    {operationsState.analysisResults.errors.map(
                      (error, index) => (
                        <li key={index}>
                          <span className="font-medium">{error.type}:</span>{" "}
                          {error.error}
                        </li>
                      ),
                    )}
                  </ul>
                  <p className="mt-2 text-xs">
                    <strong>Tip:</strong> If workflow generation failed due to
                    JSON format issues, try using a simpler, more structured SOP
                    document.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-start">
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle className="text-gray-800 text-lg font-normal">
                Standard Operating Procedure (SOP)
              </CardTitle>
              {operationsState?.optimizedSop && <Badge>Optimized</Badge>}
            </div>
            <CardDescription>
              A step-by-step document for the process.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {sopContent ? (
              <div className="prose max-w-none">
                <ReactMarkdown className="text-xs">{sopContent}</ReactMarkdown>
              </div>
            ) : (
              <EmptyState
                icon={<FileText className="h-12 w-12" />}
                title="No SOP"
                description="Your SOP document will appear here after analysis."
              />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle className="text-gray-800 text-lg font-normal">
                Workflow Diagram
              </CardTitle>
              {operationsState?.optimizedWorkflow && <Badge>Optimized</Badge>}
            </div>
            <CardDescription>
              A visual representation of the process (BPMN).
            </CardDescription>
          </CardHeader>
          <CardContent>
            {operationsState?.optimizedWorkflow ||
            operationsState?.workflowData ? (
              <GraphComponent
                data={
                  operationsState.optimizedWorkflow ||
                  operationsState.workflowData
                }
              />
            ) : (
              <EmptyState
                icon={<Workflow className="h-12 w-12" />}
                title="No Workflow"
                description="Your workflow diagram will appear here after analysis."
              />
            )}
          </CardContent>
        </Card>
      </div>

      {/* Conditional Generation Buttons for Section 2 */}
      {(showGenerateWorkflowButton || showGenerateSopButton) && (
        <Card className="border-blue-200 bg-blue-50">
          <CardHeader>
            <CardTitle className="text-blue-800 text-lg">
              Generate Missing Element
            </CardTitle>
            <CardDescription className="text-blue-700">
              {showGenerateWorkflowButton 
                ? "Generate a workflow diagram from your SOP document."
                : "Generate an SOP document from your workflow diagram."
              }
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button
              onClick={showGenerateWorkflowButton ? onGenerateWorkflowFromSop : onGenerateSopFromWorkflow}
              disabled={isLoading}
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              {isLoading ? (
                "Generating..."
              ) : (
                <>
                  {showGenerateWorkflowButton ? "Generate Workflow from SOP" : "Generate SOP from Workflow"}
                  <ArrowRight className="ml-2 h-4 w-4" />
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
