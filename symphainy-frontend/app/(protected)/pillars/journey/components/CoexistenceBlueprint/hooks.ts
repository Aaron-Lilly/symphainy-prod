// CoexistenceBlueprint Hooks
"use client";
import React, { useState, useCallback } from "react";
import { usePlatformState } from "@/shared/state/PlatformStateProvider";
// ✅ FIX ISSUE 1: Use JourneyAPIManager instead of OperationsService
import { useJourneyAPIManager } from "@/shared/hooks/useJourneyAPIManager";
import { 
  CoexistenceBlueprintProps, 
  CoexistenceBlueprintState, 
  CoexistenceBlueprintActions,
  OptimizationRequest,
  OptimizationResponse,
  BlueprintSaveRequest,
  BlueprintSaveResponse
} from "./types";

export function useCoexistenceBlueprint(props: CoexistenceBlueprintProps): CoexistenceBlueprintState & CoexistenceBlueprintActions {
  const { setRealmState, getRealmState } = usePlatformState();
  // ✅ FIX ISSUE 1: Use JourneyAPIManager instead of OperationsService
  const journeyAPIManager = useJourneyAPIManager();
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [optimizedSop, setOptimizedSop] = useState<string | null>(null);
  const [optimizedWorkflow, setOptimizedWorkflow] = useState<any | null>(null);
  const [blueprint, setBlueprint] = useState<any | null>(null);

  // ✅ FIX ISSUE 2: Read from Runtime state (realm state) if available
  React.useEffect(() => {
    const operations = getRealmState('journey', 'operations');
    if (operations?.optimizedSop || operations?.optimizedWorkflow || operations?.blueprint) {
      if (operations.optimizedSop && !optimizedSop) {
        setOptimizedSop(operations.optimizedSop);
      }
      if (operations.optimizedWorkflow && !optimizedWorkflow) {
        setOptimizedWorkflow(operations.optimizedWorkflow);
      }
      if (operations.blueprint && !blueprint) {
        setBlueprint(operations.blueprint);
      }
    }
  }, [getRealmState, optimizedSop, optimizedWorkflow, blueprint]);

  // Helper function to format SOP content nicely
  const formatSOPContent = useCallback((sop: any): string => {
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
  }, []);

  // Helper function to format workflow content nicely
  const formatWorkflowContent = useCallback((workflow: any): string => {
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
        formatted += `### ${index + 1}. ${edge.source} → ${edge.target}\n\n`;
        
        if (edge.label) {
          formatted += `**Condition:** ${edge.label}\n\n`;
        }
        
        if (edge.metadata) {
          if (edge.metadata.condition) {
            formatted += `**Condition:** ${edge.metadata.condition}\n\n`;
          }
          if (edge.metadata.action) {
            formatted += `**Action:** ${edge.metadata.action}\n\n`;
          }
        }
        
        formatted += "---\n\n";
      });
    }
    
    return formatted;
  }, []);

  // Helper function to safely extract and format content
  const getSafeFormattedContent = useCallback((data: any, type: 'sop' | 'workflow'): string => {
    if (!data) return "No content available";
    
    if (typeof data === "string") {
      try {
        const parsed = JSON.parse(data);
        if (type === 'sop' && parsed.title && parsed.steps) {
          return formatSOPContent(parsed);
        }
        if (type === 'workflow' && (parsed.nodes || parsed.edges)) {
          return formatWorkflowContent(parsed);
        }
        return data;
      } catch {
        return data;
      }
    }
    
    if (typeof data === "object" && data !== null) {
      if (type === 'sop') {
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
          return data.text;
        }
      }
      
      if (type === 'workflow') {
        if (data.workflow) {
          if (typeof data.workflow === "string") {
            try {
              const parsed = JSON.parse(data.workflow);
              if (parsed.nodes || parsed.edges) {
                return formatWorkflowContent(parsed);
              }
            } catch {
              return data.workflow;
            }
          } else if (data.workflow.nodes || data.workflow.edges) {
            return formatWorkflowContent(data.workflow);
          }
        }
        if (data.workflowData) {
          if (typeof data.workflowData === "string") {
            try {
              const parsed = JSON.parse(data.workflowData);
              if (parsed.nodes || parsed.edges) {
                return formatWorkflowContent(parsed);
              }
            } catch {
              return data.workflowData;
            }
          } else if (data.workflowData.nodes || data.workflowData.edges) {
            return formatWorkflowContent(data.workflowData);
          }
        }
      }
    }
    
    return JSON.stringify(data, null, 2);
  }, [formatSOPContent, formatWorkflowContent]);

  // Handle coexistence optimization
  const handleOptimize = useCallback(async () => {
    if (!props.sessionToken || !props.sopText || !props.workflowData) {
      setError("Missing required data for optimization");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const sopContent = getSafeFormattedContent(props.sopText, 'sop');
      const workflowContent = props.workflowData;

      // ✅ FIX ISSUE 1: Use JourneyAPIManager (intent-based API) instead of OperationsService
      const response = await journeyAPIManager.optimizeCoexistenceWithContent(
        sopContent,
        workflowContent
      );

      if (response.success) {
        setOptimizedSop(response.optimized_sop || null);
        setOptimizedWorkflow(response.optimized_workflow || null);
        setBlueprint(response.blueprint || null);

        // Realm state already updated by JourneyAPIManager, but ensure local state is set
        // (JourneyAPIManager already calls setRealmState)
      } else {
        setError(response.error || "Optimization failed");
      }
    } catch (err: any) {
      console.error("Optimization error:", err);
      setError(err.message || "Failed to optimize coexistence");
    } finally {
      setLoading(false);
    }
  }, [props.sessionToken, props.sopText, props.workflowData, getSafeFormattedContent, setRealmState]);

  // Handle blueprint saving
  const handleSaveBlueprint = useCallback(async () => {
    if (!blueprint) {
      setError("No blueprint to save");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // ✅ FIX ISSUE 1: Use JourneyAPIManager (intent-based API) instead of OperationsService
      // Adapt blueprint data to createBlueprint format
      const blueprintData = {
        name: blueprint.name || "Coexistence Blueprint",
        description: blueprint.description || "Generated coexistence blueprint",
        components: blueprint.components || (blueprint.visualization ? [{
          id: "main",
          type: "coexistence",
          name: "Coexistence Analysis"
        }] : [])
      };

      const response = await journeyAPIManager.createBlueprint(blueprintData);
      
      if (response.success && response.blueprint) {
        console.log("Blueprint saved with ID:", response.blueprint.blueprint_id);
        
        // Update realm state (already updated by JourneyAPIManager, but ensure local state is set)
        setRealmState('journey', 'operations', {
          ...getRealmState('journey', 'operations') || {},
          savedBlueprintId: response.blueprint.blueprint_id,
          blueprintSaved: true,
        });
      } else {
        throw new Error(response.error || "Failed to save blueprint");
      }
    } catch (err: any) {
      console.error("Save blueprint error:", err);
      setError(err.message || "Failed to save blueprint");
    } finally {
      setLoading(false);
    }
  }, [blueprint, journeyAPIManager, setRealmState, getRealmState]);

  return {
    loading,
    error,
    optimizedSop,
    optimizedWorkflow,
    blueprint,
    handleOptimize,
    handleSaveBlueprint,
    formatSOPContent,
    formatWorkflowContent,
    getSafeFormattedContent,
  };
} 