// ProcessBlueprint Core Component
"use client";
import React from "react";
import { useProcessBlueprint } from "./hooks";
import { ProcessBlueprintProps } from "./types";
import { ProcessBlueprintUI } from "./components";

export function ProcessBlueprintCore({
  operationsState,
  onGenerateWorkflowFromSop,
  onGenerateSopFromWorkflow,
  isLoading = false,
}: ProcessBlueprintProps) {
  const {
    sopContent,
    workflowContent,
    workflowData,
    analysisResults,
    formatSOPContent,
    getSafeTextContent,
  } = useProcessBlueprint({
    operationsState,
    onGenerateWorkflowFromSop,
    onGenerateSopFromWorkflow,
    isLoading,
  });

  return (
    <ProcessBlueprintUI
      sopContent={sopContent}
      workflowContent={workflowContent}
      workflowData={workflowData}
      analysisResults={analysisResults}
      isLoading={isLoading}
      onGenerateWorkflowFromSop={onGenerateWorkflowFromSop}
      onGenerateSopFromWorkflow={onGenerateSopFromWorkflow}
      formatSOPContent={formatSOPContent}
      getSafeTextContent={getSafeTextContent}
    />
  );
} 