// WizardActive Hooks
"use client";
import React, { useState, useEffect } from "react";
// ✅ PHASE 5: Use PlatformStateProvider instead of Jotai atoms
import { usePlatformState } from "@/shared/state/PlatformStateProvider";
// Uses OperationsAPIManager for Operations Realm intents (SOPs, workflows)
import { useOperationsAPIManager } from "@/shared/hooks/useOperationsAPIManager";
import { 
  WizardActiveProps, 
  WizardActiveState, 
  WizardActiveActions,
  ChatTurn,
  WizardChatRequest,
  WizardChatResponse,
  WizardPublishRequest,
  WizardPublishResponse
} from "./types";

export function useWizardActive({ onBack }: WizardActiveProps): WizardActiveState & WizardActiveActions {
  // ✅ PHASE 5: Use PlatformStateProvider instead of Jotai atoms
  const { setChatbotAgentInfo, setMainChatbotOpen, setRealmState } = usePlatformState();
  const setAgentInfo = setChatbotAgentInfo; // Alias for compatibility
  // ✅ ARCHITECTURAL FIX: Actually instantiate the Operations API Manager
  const operationsAPIManager = useOperationsAPIManager();

  const [chatHistory, setChatHistory] = useState<ChatTurn[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [draftSop, setDraftSop] = useState<any | null>(null);
  const [published, setPublished] = useState(false);
  const [publishedSop, setPublishedSop] = useState<any | null>(null);
  const [publishedWorkflow, setPublishedWorkflow] = useState<any | null>(null);
  // For MVP, use a simple session token
  const [sessionToken] = useState(() => `wizard-session-${Math.random().toString(36).slice(2)}`);

  useEffect(() => {
    // Set agent info for the wizard
    setAgentInfo({
      title: "Workflow Builder Wizard",
      agent: "WorkflowBuilderWizardAgent",
      file_url: "",
      additional_info: ""
    });
    setMainChatbotOpen(false);
  }, [setAgentInfo, setMainChatbotOpen]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    
    setLoading(true);
    setError(null);
    
    try {
      setChatHistory((h) => [...h, { role: 'user', content: input }]);
      
      const request: WizardChatRequest = {
        sessionToken,
        userMessage: input,
      };
      
      // Uses OperationsAPIManager (intent-based API)
      const result = await operationsAPIManager.processWizardConversation(
        input,
        sessionToken,
        { agent_type: 'WorkflowBuilderWizardAgent' }
      );
      
      if (result.success) {
        setChatHistory((h) => [...h, { role: 'agent', content: result.agent_response || 'Response received' }]);
        if (result.draft_sop) setDraftSop(result.draft_sop);
      } else {
        throw new Error(result.error || 'Failed to process wizard conversation');
      }
      setInput("");
    } catch (e: any) {
      setError(e.message || "Failed to send message");
    } finally {
      setLoading(false);
    }
  };

  const handlePublish = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const request: WizardPublishRequest = {
        sessionToken,
      };
      
      // Uses OperationsAPIManager (intent-based API)
      const result = await operationsAPIManager.processOperationsQuery(
        "publish_workflow_and_sop",
        sessionToken,
        { agent_type: 'WorkflowBuilderWizardAgent' }
      );
      
      if (result.success) {
        setPublishedSop(result.sop);
        setPublishedWorkflow(result.workflow);
        setPublished(true);
      } else {
        throw new Error(result.error || 'Failed to process operations query');
      }

      // Save to realm state for journey realm
      setRealmState('journey', 'operations', {
        sopText: result.sop,
        workflowData: result.workflow,
        published: true,
        source: 'wizard'
      });
    } catch (e: any) {
      setError(e.message || "Failed to publish");
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    setMainChatbotOpen(true);
    onBack();
  };

  return {
    chatHistory,
    input,
    setInput,
    loading,
    error,
    draftSop,
    published,
    publishedSop,
    publishedWorkflow,
    sessionToken,
    handleSend,
    handlePublish,
    handleBack,
  };
} 