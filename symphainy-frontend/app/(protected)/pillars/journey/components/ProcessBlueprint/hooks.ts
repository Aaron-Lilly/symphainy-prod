// ProcessBlueprint Hooks
"use client";
import React, { useMemo } from "react";
import { ProcessBlueprintProps, ProcessBlueprintState, ProcessBlueprintActions } from "./types";

export function useProcessBlueprint(props: ProcessBlueprintProps): ProcessBlueprintState & ProcessBlueprintActions {
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
        return data.text;
      }
      // If it's a SOP object directly
      if (data.title && data.steps) {
        return formatSOPContent(data);
      }
      // If all else fails, stringify it
      return JSON.stringify(data, null, 2);
    }
    return "No content available";
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

  // Memoized state calculations
  const sopContent = useMemo(() => {
    if (!props.operationsState) return "No SOP content available";
    
    const sopData = props.operationsState.optimizedSop || props.operationsState.sopText;
    return getSafeTextContent(sopData);
  }, [props.operationsState]);

  const workflowContent = useMemo(() => {
    if (!props.operationsState) return "No workflow content available";
    
    const workflowData = props.operationsState.optimizedWorkflow || props.operationsState.workflowData;
    return getSafeTextContent(workflowData);
  }, [props.operationsState]);

  const workflowData = useMemo(() => {
    if (!props.operationsState) return null;
    
    return props.operationsState.optimizedWorkflow || props.operationsState.workflowData;
  }, [props.operationsState]);

  const analysisResults = useMemo(() => {
    return props.operationsState?.analysisResults || null;
  }, [props.operationsState]);

  return {
    sopContent,
    workflowContent,
    workflowData,
    analysisResults,
    formatSOPContent,
    getSafeTextContent,
  };
} 