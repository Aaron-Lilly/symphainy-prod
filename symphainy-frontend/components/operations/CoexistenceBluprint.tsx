"use client";
import React, { useState, useEffect } from "react";
import { useGlobalSession } from "@/shared/agui/GlobalSessionProvider";
import { optimizeCoexistence, optimizeCoexistenceWithContent, saveBlueprint } from "@/lib/api/operations";
// import { saveBlueprint } from "@/lib/api/operations";
// import { CoexistenceDeliverable, OptimizeResponse, isOptimizeResponse } from "@/shared/types/coexistence";
import ProcessBlueprint from "./ProcessBlueprint";
import { Button } from "../ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../ui/card";
import { useAtomValue } from "jotai";
import ReactMarkdown from "react-markdown";
import dynamic from "next/dynamic";

// Dynamic import for GraphComponent
const GraphComponent = dynamic(
  () => import("@/components/operations/GraphComponent"),
  { ssr: false }
);

// Helper function to format SOP content nicely (copied from ProcessBlueprint)
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

// Helper function to format workflow content nicely
const formatWorkflowContent = (workflow: any): string => {
  let formatted = `# Workflow Diagram\n\n`;
  
  if (workflow.description) {
    formatted += `${workflow.description}\n\n`;
  }
  
  if (workflow.nodes && Array.isArray(workflow.nodes)) {
    formatted += "## Process Nodes\n\n";
    workflow.nodes.forEach((node: any, index: number) => {
      if (node.type === 'start' || node.type === 'end') {
        formatted += `### ${node.label || node.type.toUpperCase()}\n\n`;
      } else {
        formatted += `### ${index + 1}. ${node.label}\n\n`;
      }
      
      if (node.type) {
        formatted += `**Type:** ${node.type}\n\n`;
      }
      
      if (node.metadata) {
        if (node.metadata.design_pattern) {
          formatted += `**Design Pattern:** ${node.metadata.design_pattern}\n\n`;
        }
        if (node.metadata.expected_outcome) {
          formatted += `**Expected Outcome:** ${node.metadata.expected_outcome}\n\n`;
        }
        if (node.metadata.step_number) {
          formatted += `**Step Number:** ${node.metadata.step_number}\n\n`;
        }
        if (node.metadata.responsible_role) {
          formatted += `**Responsible Role:** ${node.metadata.responsible_role}\n\n`;
        }
        if (node.metadata.expected_output) {
          formatted += `**Expected Output:** ${node.metadata.expected_output}\n\n`;
        }
      }
      
      formatted += "---\n\n";
    });
  }
  
  if (workflow.edges && Array.isArray(workflow.edges)) {
    formatted += "## Process Flow\n\n";
    workflow.edges.forEach((edge: any, index: number) => {
      formatted += `${index + 1}. **${edge.from_node || edge.from}** → **${edge.to_node || edge.to}**\n`;
      if (edge.label) {
        formatted += `   ${edge.label}\n`;
      }
      formatted += "\n";
    });
  }
  
  return formatted;
};

// Helper function to safely extract and format content
const getSafeFormattedContent = (data: any, type: 'sop' | 'workflow'): string => {
  if (typeof data === "string") {
    // Try to parse as JSON first
    try {
      const parsed = JSON.parse(data);
      if (type === 'sop' && parsed.title && parsed.steps) {
        return formatSOPContent(parsed);
      }
      if (type === 'workflow' && parsed.nodes && parsed.edges) {
        return formatWorkflowContent(parsed);
      }
      // If it's other JSON, return as is
      return data;
    } catch {
      // If it's not JSON, return as is
      return data;
    }
  }
  if (typeof data === "object" && data !== null) {
    if (type === 'sop' && data.title && data.steps) {
      return formatSOPContent(data);
    }
    if (type === 'workflow' && data.nodes && data.edges) {
      return formatWorkflowContent(data);
    }
    // If no known structure, stringify the whole object
    return JSON.stringify(data, null, 2);
  }
  return String(data || "");
};

// Placeholder types - replace with actual types when available
interface CoexistenceDeliverable {
  content?: {
    optimized_sop?: string;
    optimized_workflow?: any;
  };
  [key: string]: any;
}

interface OptimizeResponse {
  deliverable?: CoexistenceDeliverable;
  blueprint?: any;
  optimized_sop?: string;
  optimized_workflow?: any;
}

// Placeholder function - replace with actual function when available
const isOptimizeResponse = (obj: any): obj is OptimizeResponse => {
  return obj && (obj.deliverable || obj.blueprint);
};

const saveBlueprintLocal = async (data: any): Promise<any> => {
  console.log("Saving blueprint with data:", data);
  
  try {
    const result = await saveBlueprint(data.blueprint, data.user_id);
    console.log("Blueprint saved successfully:", result);
    return result;
  } catch (error) {
    console.error("Error saving blueprint:", error);
    throw error;
  }
};

interface CoexistenceBlueprintProps {
  sopText?: string | any;
  workflowData?: any;
  generatedSopUuid?: string;
  generatedWorkflowUuid?: string;
  selectedSopFileUuid?: string | null;
  selectedWorkflowFileUuid?: string | null;
  sessionToken?: string;
  sessionState?: any;
  isEnabled?: boolean;
}

export default function CoexistenceBlueprint({
  sopText,
  workflowData,
  generatedSopUuid,
  generatedWorkflowUuid,
  selectedSopFileUuid,
  selectedWorkflowFileUuid,
  sessionToken,
  sessionState,
  isEnabled = false,
}: CoexistenceBlueprintProps) {
  const { getPillarState, setPillarState, guideSessionToken } = useGlobalSession();

  // Local state for blueprint functionality
  const [blueprint, setBlueprint] = useState<CoexistenceDeliverable | any | null>(null);
  const [blueprintLoading, setBlueprintLoading] = useState(false);
  const [saveToast, setSaveToast] = useState(false);
  const [specialization, setSpecialization] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [coexistenceAnalysis, setCoexistenceAnalysis] = useState<string>("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [optimizedSop, setOptimizedSop] = useState<string>("");
  const [optimizedWorkflow, setOptimizedWorkflow] = useState<any>(null);
  const [optimizedWorkflowRaw, setOptimizedWorkflowRaw] = useState<any>(null);
  const [showOptimized, setShowOptimized] = useState(false);
  // Get operations state for user_id
  const operationsState = getPillarState('operations') || {};

  // Domain options for specialization
  const DOMAIN_OPTIONS = [
    { value: "", label: "Auto-detect (recommended)" },
    { value: "HR", label: "Human Resources" },
    { value: "Finance", label: "Finance & Accounting" },
    { value: "Healthcare", label: "Healthcare" },
    { value: "Legal", label: "Legal" },
    { value: "Manufacturing", label: "Manufacturing" },
    { value: "Retail", label: "Retail" },
    { value: "Education", label: "Education" },
    { value: "Insurance", label: "Insurance (Life & Annuities)" },
    { value: "Banking", label: "Banking" },
    { value: "General", label: "General Business" }
  ];

  // Handler for Optimize with Coexistence
  const handleOptimize = async () => {
    setIsStreaming(true);

    // Check if we have the actual content
    if (!sopText && !workflowData) {
      console.error("5. Frontend: ERROR - No content available");
      setError("Please generate both SOP and workflow content first.");
      return;
    }

    setBlueprintLoading(true);
    setError(null);

    try {
      const sessionToken = guideSessionToken || "demo-session";

      // Use the content directly instead of file UUIDs
      const result: any = await optimizeCoexistenceWithContent(
        sessionToken,
        sopText || "",
        workflowData || "",
      );
      setIsStreaming(false);
      console.log("7. Frontend: API response received:", result);

      // Set coexistence analysis if available
      if (result.coexistence_analysis) {
        setCoexistenceAnalysis(result.coexistence_analysis);
      }

      // Handle optimized SOP and workflow
      if (result.optimized_sop) {
        // Format SOP content properly
        const sopContent = getSafeFormattedContent(result.optimized_sop, 'sop');
        setOptimizedSop(sopContent);
        setShowOptimized(true);
      }

      if (result.optimized_workflow) {
        // Format workflow content properly
        const workflowContent = getSafeFormattedContent(result.optimized_workflow, 'workflow');
        setOptimizedWorkflow(workflowContent);
        setOptimizedWorkflowRaw(result.optimized_workflow); // Store raw object
        setShowOptimized(true);
      }

      // Set the blueprint state for saving
      const blueprintData = {
        coexistence_analysis: result.coexistence_analysis,
        optimized_sop: result.optimized_sop,
        optimized_workflow: result.optimized_workflow,
        original_sop: result.original_sop,
        original_workflow: result.original_workflow,
        created_at: new Date().toISOString(),
        user_id: operationsState.user_id || "demo-user"
      };
      setBlueprint(blueprintData);
      console.log("Blueprint state set:", blueprintData);

      // Save to global session for experience pillar
      const currentOperationsState = getPillarState('operations') || {};
      setPillarState('operations', {
        ...currentOperationsState,
        coexistenceAnalysis: result.coexistence_analysis,
        optimizedSop: result.optimized_sop,
        optimizedWorkflow: result.optimized_workflow,
        workflowData: result.optimized_workflow || currentOperationsState.workflowData,
        sopText: result.optimized_sop || currentOperationsState.sopText,
      });

    } catch (e: any) {
      setError(e.message || "Failed to optimize blueprint");
    } finally {
      setBlueprintLoading(false);
      setIsStreaming(false);
    }
  };

  // Handler for Save Blueprint
  const handleSaveBlueprint = async () => {
    console.log("Save Blueprint button clicked!");
    console.log("Current blueprint state:", blueprint);
    
    if (!blueprint) {
      console.log("No blueprint data available for saving");
      setError("No blueprint data available. Please generate a blueprint first.");
      return;
    }
    
    setSaveToast(false);
    setError(null);

    try {
      console.log("Attempting to save blueprint with data:", blueprint);
      
      // Handle both new deliverable format and legacy blueprint format
      const blueprintData = isOptimizeResponse({ deliverable: blueprint }) ? blueprint : blueprint;

      const result = await saveBlueprintLocal({
        blueprint: blueprintData,
        user_id: operationsState.user_id || "demo-user"
      });

      console.log("Blueprint saved successfully:", result);
      setSaveToast(true);
      setTimeout(() => setSaveToast(false), 2000);
    } catch (e: any) {
      console.error("Error saving blueprint:", e);
      setError(e.message || "Failed to save blueprint");
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="">
          Coexistence Blueprint
        </CardTitle>
        <CardDescription>
          Generate an optimized coexistence blueprint for your Human+AI workforce process.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {error && (
          <div className="mb-4 text-red-600">{error}</div>
        )}

        {/* Domain Specialization Section */}
        <div className="mb-6 p-4 rounded-lg border">
          <CardTitle className="text-gray-800 text-lg font-normal mb-3">
            Domain Specialization
          </CardTitle>
          <div className="flex gap-4 items-end">
            <div className="flex-1">
              <label htmlFor="specialization" className="block text-sm font-medium text-gray-700 mb-2">
                Select Domain (Optional)
              </label>
              <select
                id="specialization"
                value={specialization}
                onChange={(e) => {
                  console.log("Frontend: Specialization changed to:", e.target.value);
                  setSpecialization(e.target.value);
                }}
                className="w-full border rounded px-3 py-2 text-sm"
              >
                {DOMAIN_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              <p className="text-xs text-gray-500 mt-1">
                {specialization
                  ? `Using ${specialization} domain expertise for analysis`
                  : "Auto-detecting domain from process content (recommended)"
                }
              </p>
            </div>
            <Button
              className="mb-5"
              variant="default"
              disabled={blueprintLoading || !isEnabled || (!selectedSopFileUuid && !selectedWorkflowFileUuid)}
              onClick={() => {
                console.log("Frontend: Optimize button clicked");
                if (!selectedSopFileUuid && !selectedWorkflowFileUuid) {
                  setError("Please select at least a SOP or workflow file to optimize.");
                  return;
                }
                if (!selectedSopFileUuid || !selectedWorkflowFileUuid) {
                  setError("Warning: Only one file selected. Optimization will proceed with available data.");
                }
                handleOptimize();
              }}
            >
              {blueprintLoading ? "Optimizing..." : "Optimize with Coexistence"}
            </Button>
          </div>
        </div>

        { coexistenceAnalysis === "" && (
        <CardDescription>
          Click the button above to generate an optimized coexistence blueprint for your process.
        </CardDescription>
        )}



{(coexistenceAnalysis || isStreaming) && (
  <div className="mt-6 p-4 border rounded-lg bg-gray-50">
    <div className="flex items-center gap-4 mb-3">
      <h3 className="font-semibold">Coexistence Analysis</h3>
      {isStreaming && (
        <div className="flex items-center gap-1 text-blue-600">
          <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
          <span className="text-sm">Generating analysis...</span>
        </div>
      )}
    </div>
    <div className="prose max-w-none">
      <ReactMarkdown className="text-xs leading-relaxed">
        {coexistenceAnalysis}
      </ReactMarkdown>
      {isStreaming && (
        <div className="mt-2 w-1 h-4 bg-black animate-pulse inline-block"></div>
      )}
    </div>
  </div>
)}

{/* Optimized SOP and Workflow Section */}
{showOptimized && (optimizedSop || optimizedWorkflow) && (
  <div className="mt-6 space-y-4">
    <h3 className="font-semibold text-lg">Future State Recommendations</h3>
    
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-start">
      {/* Optimized SOP */}
      {optimizedSop && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Optimized SOP</CardTitle>
            <CardDescription>
              Enhanced SOP incorporating coexistence analysis recommendations
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="prose max-w-none">
              <ReactMarkdown className="text-sm leading-relaxed">
                {optimizedSop}
              </ReactMarkdown>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Optimized Workflow */}
      {optimizedWorkflowRaw && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Optimized Workflow</CardTitle>
            <CardDescription>
              Enhanced workflow incorporating coexistence analysis recommendations
            </CardDescription>
          </CardHeader>
          <CardContent>
            <GraphComponent data={optimizedWorkflowRaw} />
          </CardContent>
        </Card>
      )}
    </div>
  </div>
)}

{coexistenceAnalysis && (
          <div className="mt-6">
            {/* <ProcessBlueprint operationsState={{ optimizedSop: blueprint }} /> */}
            <div className="flex gap-4 mt-6">
              <Button onClick={handleSaveBlueprint}>Save Blueprint</Button>
              {saveToast && (
                <span className="text-green-600 ml-2">Blueprint saved!</span>
              )}
            </div>
          </div>
        )}

      </CardContent>
    </Card>
  );
}