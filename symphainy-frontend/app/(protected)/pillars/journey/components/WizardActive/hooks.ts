// WizardActive Hooks
"use client";
import React, { useState, useEffect } from "react";
import { usePlatformState } from "@/shared/state/PlatformStateProvider";
import { chatbotAgentInfoAtom, mainChatbotOpenAtom } from "@/shared/atoms/chatbot-atoms";
import { useSetAtom } from "jotai";
import { OperationsService } from "@/shared/services/operations";
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
  const setAgentInfo = useSetAtom(chatbotAgentInfoAtom);
  const setMainChatbotOpen = useSetAtom(mainChatbotOpenAtom);
  const { setRealmState } = usePlatformState();

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
      
      const response: WizardChatResponse = await OperationsService.processOperationsWizardConversation({
        session_id: sessionToken,
        message: input,
        context: { agent_type: 'WorkflowBuilderWizardAgent' }
      });
      
      setChatHistory((h) => [...h, { role: 'agent', content: response.agent_response }]);
      if (response.draft_sop) setDraftSop(response.draft_sop);
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
      
      const response: WizardPublishResponse = await OperationsService.processOperationsQuery({
        session_id: sessionToken,
        query: "publish_workflow_and_sop",
        context: { agent_type: 'WorkflowBuilderWizardAgent' }
      });
      
      setPublishedSop(response.sop);
      setPublishedWorkflow(response.workflow);
      setPublished(true);

      // Save to realm state for journey realm
      setRealmState('journey', 'operations', {
        sopText: response.sop,
        workflowData: response.workflow,
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