// CoexistenceBlueprint Core Component
"use client";
import React from "react";
import { useCoexistenceBlueprint } from "./hooks";
import { CoexistenceBlueprintProps } from "./types";
import { CoexistenceBlueprintUI } from "./components";

export function CoexistenceBlueprintCore({
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
  const {
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
  } = useCoexistenceBlueprint({
    sopText,
    workflowData,
    generatedSopUuid,
    generatedWorkflowUuid,
    selectedSopFileUuid,
    selectedWorkflowFileUuid,
    sessionToken,
    sessionState,
    isEnabled,
  });

  return (
    <CoexistenceBlueprintUI
      loading={loading}
      error={error}
      optimizedSop={optimizedSop}
      optimizedWorkflow={optimizedWorkflow}
      blueprint={blueprint}
      sopText={sopText}
      workflowData={workflowData}
      isEnabled={isEnabled}
      onOptimize={handleOptimize}
      onSaveBlueprint={handleSaveBlueprint}
      formatSOPContent={formatSOPContent}
      formatWorkflowContent={formatWorkflowContent}
      getSafeFormattedContent={getSafeFormattedContent}
    />
  );
} 