"use client";

import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Loader2, ArrowLeft, Send, CheckCircle, FileText, Share2 } from "lucide-react";
import { wizardChat, wizardPublish, startWizard } from "@/lib/api/operations";
import { useGlobalSession } from "@/shared/agui/GlobalSessionProvider";
import { useAuth } from "@/shared/agui/AuthProvider";
import { chatbotAgentInfoAtom, mainChatbotOpenAtom } from "@/shared/atoms/chatbot-atoms";
import { useSetAtom } from "jotai";

interface ChatTurn {
  role: 'user' | 'agent';
  content: string;
}

interface WizardActiveProps {
  onBack: () => void;
}

export default function WizardActive({ onBack }: WizardActiveProps) {
  const setAgentInfo = useSetAtom(chatbotAgentInfoAtom);
  const setMainChatbotOpen = useSetAtom(mainChatbotOpenAtom);
  const { setPillarState } = useGlobalSession();

  const { guideSessionToken } = useGlobalSession();
  const { user } = useAuth();
  const [chatHistory, setChatHistory] = useState<ChatTurn[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [draftSop, setDraftSop] = useState<any | null>(null);
  const [published, setPublished] = useState(false);
  const [publishedSop, setPublishedSop] = useState<any | null>(null);
  const [publishedWorkflow, setPublishedWorkflow] = useState<any | null>(null);
  const [sessionToken, setSessionToken] = useState<string | null>(null);
  const [wizardStarted, setWizardStarted] = useState(false);

  useEffect(() => {
    // Set agent info for the wizard
    setAgentInfo({
      title: "Workflow Builder Wizard",
      agent: "WorkflowBuilderWizardAgent",
      file_url: "",
      additional_info: ""
    });
    setMainChatbotOpen(false);
    
    // Start wizard session on mount
    const initializeWizard = async () => {
      if (wizardStarted) return;
      setLoading(true);
      try {
        const userId = user?.id || undefined;
        const response = await startWizard(guideSessionToken || undefined, userId);
        // Extract session token from response
        const token = (response as any).session_token || (response as any).wizard_session_id || (response as any).data?.session_token || guideSessionToken || `wizard-${Math.random().toString(36).slice(2)}`;
        setSessionToken(token);
        setWizardStarted(true);
        // Add welcome message if provided
        if (response.message || response.data?.message) {
          setChatHistory([{ role: 'agent', content: response.message || response.data?.message || 'Welcome! Let\'s create your SOP together.' }]);
        }
      } catch (e: any) {
        setError(e.message || "Failed to start wizard");
      } finally {
        setLoading(false);
      }
    };
    
    initializeWizard();
  }, [setAgentInfo, setMainChatbotOpen, guideSessionToken, user, wizardStarted]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !sessionToken) return;
    setLoading(true);
    setError(null);
    try {
      setChatHistory((h) => [...h, { role: 'user', content: input }]);
      const resp = await wizardChat(sessionToken, input);
      setChatHistory((h) => [...h, { role: 'agent', content: resp.message || resp.data?.message || 'Response received' }]);
      if (resp.data?.draft_sop) setDraftSop(resp.data.draft_sop);
      setInput("");
    } catch (e: any) {
      setError(e.message || "Failed to send message");
    } finally {
      setLoading(false);
    }
  };

  const handlePublish = async () => {
    if (!sessionToken) {
      setError("Wizard session not started");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const userId = user?.id || undefined;
      const resp = await wizardPublish(sessionToken, userId);
      setPublishedSop((resp as any).data?.sop || (resp as any).sop);
      setPublishedWorkflow((resp as any).data?.workflow || (resp as any).workflow);
      setPublished(true);

      // Save to global session for experience pillar
      setPillarState('operations', {
        sopText: (resp as any).data?.sop || (resp as any).sop,
        workflowData: (resp as any).data?.workflow || (resp as any).workflow,
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Workflow Builder Wizard</h2>
          <p className="text-gray-600 mt-1">
            Let's build your process step by step. Describe what you want to accomplish.
          </p>
        </div>
        <Button variant="outline" onClick={handleBack}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Operations
        </Button>
      </div>

      {/* Chat Interface */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-blue-600" />
            Interactive Workflow Builder
          </CardTitle>
          <CardDescription>
            Describe your process and I'll help you build a structured workflow
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Chat History */}
          <div className="space-y-4 mb-6 max-h-96 overflow-y-auto">
            {chatHistory.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <FileText className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p>Start by describing your process or asking for help!</p>
                <p className="text-sm mt-2">Example: "I want to automate customer onboarding"</p>
              </div>
            )}
            {chatHistory.map((turn, index) => (
              <div
                key={index}
                className={`flex ${turn.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                    turn.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {turn.content}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 text-gray-800 px-4 py-2 rounded-lg">
                  <div className="flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Thinking...
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Input Form */}
          <form onSubmit={handleSend} className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Describe your process step or ask a question..."
              disabled={loading}
              className="flex-1"
            />
            <Button type="submit" disabled={loading || !input.trim()}>
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </form>

          {error && (
            <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-md text-sm">
              {error}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Draft SOP Preview */}
      {draftSop && !published && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              Draft SOP
            </CardTitle>
            <CardDescription>
              Review your SOP before publishing
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h4 className="font-semibold">{draftSop.title || "Untitled SOP"}</h4>
                {draftSop.description && (
                  <p className="text-gray-600 text-sm mt-1">{draftSop.description}</p>
                )}
              </div>
              <div>
                <h5 className="font-medium mb-2">Steps:</h5>
                <ol className="list-decimal list-inside space-y-1">
                  {draftSop.steps?.map((step: any, index: number) => (
                    <li key={index} className="text-sm">
                      {step.title}: {step.description}
                    </li>
                  ))}
                </ol>
              </div>
              <Button onClick={handlePublish} disabled={loading} className="w-full">
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Publishing...
                  </>
                ) : (
                  <>
                    <Share2 className="h-4 w-4 mr-2" />
                    Publish SOP & Generate Workflow
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Published Results */}
      {published && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              Workflow Created Successfully!
            </CardTitle>
            <CardDescription>
              Your SOP and workflow have been generated and saved
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-blue-50 rounded-lg">
                  <h4 className="font-semibold text-blue-800 mb-2">SOP Generated</h4>
                  <p className="text-sm text-blue-700">
                    {publishedSop?.steps?.length || 0} steps created
                  </p>
                </div>
                <div className="p-4 bg-green-50 rounded-lg">
                  <h4 className="font-semibold text-green-800 mb-2">Workflow Generated</h4>
                  <p className="text-sm text-green-700">
                    {publishedWorkflow?.nodes?.length || 0} nodes created
                  </p>
                </div>
              </div>
              <div className="text-center">
                <p className="text-sm text-gray-600 mb-4">
                  Your workflow is now available in the Operations pillar and can be used in the Experience pillar.
                </p>
                <Button onClick={handleBack} variant="outline">
                  Return to Operations
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
