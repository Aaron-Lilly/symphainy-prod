// WizardActive Core Component
"use client";
import React from "react";
import { useWizardActive } from "./hooks";
import { WizardActiveProps } from "./types";
import { WizardActiveUI } from "./components";

export function WizardActiveCore({ onBack }: WizardActiveProps) {
  const {
    chatHistory,
    input,
    setInput,
    loading,
    error,
    draftSop,
    published,
    publishedSop,
    publishedWorkflow,
    handleSend,
    handlePublish,
    handleBack,
  } = useWizardActive({ onBack });

  return (
    <WizardActiveUI
      chatHistory={chatHistory}
      input={input}
      setInput={setInput}
      loading={loading}
      error={error}
      draftSop={draftSop}
      published={published}
      publishedSop={publishedSop}
      publishedWorkflow={publishedWorkflow}
      onSend={handleSend}
      onPublish={handlePublish}
      onBack={handleBack}
    />
  );
} 