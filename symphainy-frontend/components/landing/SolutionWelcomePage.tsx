"use client";
import React, { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { useRouter } from "next/navigation";
import { useGuideAgent } from "@/shared/agui/GuideAgentProvider";
import { useSetAtom } from "jotai";
import { chatbotAgentInfoAtom, mainChatbotOpenAtom } from "@/shared/atoms/chatbot-atoms";
import { SecondaryChatbotAgent, SecondaryChatbotTitle } from "@/shared/types/secondaryChatbot";
import { SolutionLiaisonAgent } from "@/components/liaison-agents/SolutionLiaisonAgent";
import { Loader2, Target, Lightbulb, TrendingUp, FileText, Zap } from "lucide-react";

interface BusinessOutcomeTemplate {
  id: string;
  name: string;
  description: string;
  icon: string;
  examples: string[];
  guide_agent_prompt: string;
}

interface SolutionResponse {
  success: boolean;
  solution_id?: string;
  business_outcome: string;
  solution_intent: string;
  status: string;
  current_step: string;
  guide_agent_prompt: string;
  next_steps: string[];
  solution_metadata: {
    created_at: string;
    tenant_id: string;
    user_id: string;
  };
  error?: string;
}

export function SolutionWelcomePage() {
  const [selectedOutcome, setSelectedOutcome] = useState<string>("");
  const [customOutcome, setCustomOutcome] = useState<string>("");
  const [isCreatingSolution, setIsCreatingSolution] = useState(false);
  const [solutionResponse, setSolutionResponse] = useState<SolutionResponse | null>(null);
  const [showGuideAgent, setShowGuideAgent] = useState(false);
  const router = useRouter();
  const { state: guideAgentState, createSolution } = useGuideAgent();
  
  // Dual chat interface setup
  const setAgentInfo = useSetAtom(chatbotAgentInfoAtom);
  const setMainChatbotOpen = useSetAtom(mainChatbotOpenAtom);

  // Set up Solution Liaison Agent as secondary option
  useEffect(() => {
    setAgentInfo({
      agent: SecondaryChatbotAgent.SOLUTION_LIAISON,
      title: SecondaryChatbotTitle.SOLUTION_LIAISON,
      file_url: "",
      additional_info: "Solution discovery and business outcome analysis assistance"
    });
    // Keep main chatbot open by default - GuideAgent will be shown
    setMainChatbotOpen(true);
  }, [setAgentInfo, setMainChatbotOpen]);

  // Journey templates
  const journeyTemplates: BusinessOutcomeTemplate[] = [
    {
      id: "data_analysis",
      name: "Data Analysis & Insights",
      description: "Analyze your data to generate actionable business insights",
      icon: "📊",
      examples: [
        "Analyze customer data for insights",
        "Generate sales performance reports",
        "Create data visualizations"
      ],
      guide_agent_prompt: "I can help you analyze your data and generate insights. What data would you like to analyze?"
    },
    {
      id: "process_optimization",
      name: "Process Optimization",
      description: "Optimize your business processes and workflows for better efficiency",
      icon: "⚡",
      examples: [
        "Optimize workflow processes",
        "Improve operational efficiency",
        "Streamline business operations"
      ],
      guide_agent_prompt: "I can help you optimize your processes. What workflow would you like to improve?"
    },
    {
      id: "strategic_planning",
      name: "Strategic Planning",
      description: "Create strategic plans and roadmaps for your business goals",
      icon: "🎯",
      examples: [
        "Create strategic roadmaps",
        "Plan business objectives",
        "Develop growth strategies"
      ],
      guide_agent_prompt: "I can help you create strategic plans. What business goals would you like to plan for?"
    },
    {
      id: "content_management",
      name: "Content Management",
      description: "Organize and manage your content and documents effectively",
      icon: "📁",
      examples: [
        "Organize document library",
        "Manage content workflows",
        "Create content catalogs"
      ],
      guide_agent_prompt: "I can help you manage your content. What content would you like to organize?"
    }
  ];

  const handleOutcomeSelection = (outcomeId: string) => {
    setSelectedOutcome(outcomeId);
    setCustomOutcome("");
  };

  const handleCustomOutcomeChange = (value: string) => {
    setCustomOutcome(value);
    setSelectedOutcome("custom");
  };

  const handleCreateSolution = async () => {
    if (!selectedOutcome && !customOutcome.trim()) {
      return;
    }

    setIsCreatingSolution(true);
    
    try {
      const businessOutcome = selectedOutcome === "custom" 
        ? customOutcome.trim() 
        : journeyTemplates.find(t => t.id === selectedOutcome)?.name || "";

      // Create solution using Guide Agent
      const response = await createSolution({
        business_outcome: businessOutcome,
        solution_intent: "mvp"
      });

      if (response.success) {
        setSolutionResponse(response);
        setShowGuideAgent(true);
      } else {
        console.error("Failed to create solution:", response.error);
      }
    } catch (error) {
      console.error("Error creating solution:", error);
    } finally {
      setIsCreatingSolution(false);
    }
  };

  const handleGuideAgentComplete = () => {
    // Solution completed, redirect to appropriate pillar
    if (solutionResponse?.next_steps.includes("content_pillar")) {
      router.push("/pillars/content");
    } else if (solutionResponse?.next_steps.includes("insights_pillar")) {
      router.push("/pillars/insights");
    } else if (solutionResponse?.next_steps.includes("operations_pillar")) {
      router.push("/pillars/operations");
    } else {
      router.push("/pillars/content"); // Default fallback
    }
  };

  if (showGuideAgent && solutionResponse) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="text-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                🎯 Solution Created Successfully!
              </h2>
              <p className="text-gray-600">
                Your business outcome solution is ready. Let's work with our Guide Agent to achieve your goals.
              </p>
            </div>
            
            <div className="bg-blue-50 rounded-lg p-4 mb-6">
              <h3 className="font-semibold text-blue-900 mb-2">Solution Details</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium">Business Outcome:</span>
                  <p className="text-blue-700">{solutionResponse.business_outcome}</p>
                </div>
                <div>
                  <span className="font-medium">Solution ID:</span>
                  <p className="text-blue-700 font-mono">{solutionResponse.solution_id}</p>
                </div>
                <div>
                  <span className="font-medium">Status:</span>
                  <Badge variant="outline" className="text-blue-700">
                    {solutionResponse.status}
                  </Badge>
                </div>
                <div>
                  <span className="font-medium">Current Step:</span>
                  <p className="text-blue-700">{solutionResponse.current_step}</p>
                </div>
              </div>
            </div>

            <div className="text-center">
              <Button 
                onClick={handleGuideAgentComplete}
                className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg"
              >
                Continue with Guide Agent
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Welcome to your Solution!
          </h1>
          <p className="text-xl text-gray-600 mb-2">
            Let's create a personalized solution to achieve your business goals
          </p>
          <p className="text-gray-500">
            Our Guide Agent will help you navigate the platform and create a customized experience based on your specific needs and objectives.
          </p>
        </div>

        {/* Solution Templates */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {journeyTemplates.map((template) => (
            <Card 
              key={template.id}
              className={`cursor-pointer transition-all duration-200 hover:shadow-lg ${
                selectedOutcome === template.id 
                  ? 'ring-2 ring-blue-500 bg-blue-50' 
                  : 'hover:shadow-md'
              }`}
              onClick={() => handleOutcomeSelection(template.id)}
            >
              <CardHeader className="text-center">
                <div className="text-4xl mb-2">{template.icon}</div>
                <CardTitle className="text-lg">{template.name}</CardTitle>
                <CardDescription className="text-sm">
                  {template.description}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <p className="text-sm font-medium text-gray-700">Examples:</p>
                  <ul className="text-xs text-gray-600 space-y-1">
                    {template.examples.map((example, index) => (
                      <li key={index} className="flex items-start">
                        <span className="text-blue-500 mr-2">•</span>
                        {example}
                      </li>
                    ))}
                  </ul>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Custom Solution */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center">
              <Lightbulb className="w-5 h-5 mr-2 text-yellow-500" />
              Custom Solution
            </CardTitle>
            <CardDescription>
              Don't see what you're looking for? Tell us about your specific solution goals.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <Input
                placeholder="Describe your solution goals (e.g., 'I want to transform my call center')"
                value={customOutcome}
                onChange={(e) => handleCustomOutcomeChange(e.target.value)}
                className="w-full"
              />
              {customOutcome && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                  <p className="text-sm text-yellow-800">
                    <strong>Custom Solution:</strong> {customOutcome}
                  </p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="text-center">
            <Button 
              onClick={handleCreateSolution}
              disabled={!selectedOutcome && !customOutcome.trim() || isCreatingSolution}
              className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg text-lg"
            >
              {isCreatingSolution ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Creating Solution...
                </>
              ) : (
                <>
                  <Target className="w-5 h-5 mr-2" />
                  Start My Solution
                </>
              )}
          </Button>
        </div>

        {/* Help Text */}
        <div className="mt-8 text-center">
          <p className="text-gray-500 text-sm">
            Our Guide Agent will help you navigate the platform and create a personalized solution.
            <br />
            You can always modify your solution or create a new one later.
          </p>
        </div>
      </div>
    </div>
  );
}
