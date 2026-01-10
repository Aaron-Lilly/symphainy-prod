// InsightsTab Core Component
"use client";
import React from "react";
import { useInsightsTab } from "./hooks";
import { InsightsTabProps } from "./types";
import { InsightsTabUI } from "./components";

export function InsightsTabCore({
  insightsData,
  isLoading = false,
}: InsightsTabProps) {
  const {
    summaryText,
    keyInsights,
    recommendations,
    visualizations,
    learningStyle,
    analysisHistory,
    hasData,
  } = useInsightsTab({
    insightsData,
    isLoading,
  });

  return (
    <InsightsTabUI
      summaryText={summaryText}
      keyInsights={keyInsights}
      recommendations={recommendations}
      visualizations={visualizations}
      learningStyle={learningStyle}
      analysisHistory={analysisHistory}
      hasData={hasData}
      isLoading={isLoading}
    />
  );
} 