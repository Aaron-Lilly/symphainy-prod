"use client";

import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useRouter } from "next/navigation";
import { ArrowRight, Loader2, Lightbulb, Target, CheckCircle2, XCircle, Settings, Brain, Sparkles } from "lucide-react";
import { useApp } from "@/shared/agui/AppProvider";
import { useAuth } from '@/shared/auth/AuthProvider';
// ✅ PHASE 4: Session-First - Use SessionBoundary for session state
import { useSessionBoundary, SessionStatus } from '@/shared/state/SessionBoundaryProvider';
import { useGuideAgent } from "@/lib/contexts/ExperienceLayerProvider";
import { pillars } from "@/shared/data/pillars";
import { toast } from "sonner";
import { mvpSolutionService } from "@/shared/services/mvp";
import type { SolutionStructureResponse, SolutionPillar, UserCustomizations } from "@/shared/services/mvp/types";
import { ArtifactGallery } from "./ArtifactGallery";

export function WelcomeJourney({
  handleWelcomeComplete,
}: {
  handleWelcomeComplete: () => void;
}) {
  const router = useRouter();
  const { dispatch } = useApp();
  // ✅ PHASE 4: Session-First - Use SessionBoundary for session state
  const { state: sessionState } = useSessionBoundary();
  const { user } = useAuth(); // Keep for user data
  const isAuthenticated = sessionState.status === SessionStatus.Active;
  const guideAgent = useGuideAgent();
  
  // All hooks must be called before any conditional returns (Rules of Hooks)
  const [userGoals, setUserGoals] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showGoalInput, setShowGoalInput] = useState(false);
  const [solutionStructure, setSolutionStructure] = useState<SolutionStructureResponse | null>(null);
  const [showCustomization, setShowCustomization] = useState(false);
  const [customizedPillars, setCustomizedPillars] = useState<SolutionPillar[]>([]);
  // Discovery context state
  const [discoveryContext, setDiscoveryContext] = useState<any>(null);
  const [showDiscoverySummary, setShowDiscoverySummary] = useState(false);
  const [userEdits, setUserEdits] = useState<any>({});
  const [isCommitting, setIsCommitting] = useState(false);

  const handleCommitContext = async () => {
    setIsCommitting(true);
    try {
      // Commit the discovery context and user edits
      // This would typically save to backend or update state
      setShowDiscoverySummary(false);
      setDiscoveryContext(null);
      setUserEdits({});
      toast.success("Context committed successfully");
    } catch (error: any) {
      toast.error("Failed to commit context", {
        description: error.message || "An error occurred"
      });
    } finally {
      setIsCommitting(false);
    }
  };

  const handleStartJourney = () => {
    // Set a proactive message for the chat assistant by dispatching an action
    dispatch({
      type: "SET_CHAT_STATE",
      payload: {
        initialMessage:
          "Welcome! I'm your guide on this journey. We'll start with the Data Pillar. Please upload a file to begin.",
      },
    });
    handleWelcomeComplete();
  };

  const handleGoalAnalysis = async () => {
    if (!userGoals.trim()) {
      toast.error("Please describe your goals");
      return;
    }

    setIsAnalyzing(true);
    try {
      // AGENTIC-FORWARD PATTERN: Agent does critical reasoning FIRST
      const response = await mvpSolutionService.getSolutionGuidance(
        userGoals,
        {
          current_pillar: 'landing',
          user_context: 'new_user',
          user_name: user?.name || 'User'
        }
      );
      
      if (response.success && response.solution_structure) {
        setSolutionStructure(response);
        setCustomizedPillars(response.solution_structure.pillars);
        setShowCustomization(true);
        
        toast.success("Solution structure created!", {
          description: `Agent analyzed your goals with ${(response.reasoning.confidence * 100).toFixed(0)}% confidence.`,
          duration: 5000,
        });
      } else {
        toast.error("Analysis failed", {
          description: response.error || "Unable to analyze your goals"
        });
      }
    } catch (error: any) {
      toast.error("Analysis failed", {
        description: error.message || "An error occurred while analyzing your goals"
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleCustomizePillar = (pillarName: string, enabled: boolean) => {
    setCustomizedPillars(prev => 
      prev.map(p => 
        p.name === pillarName 
          ? { ...p, enabled }
          : p
      )
    );
  };

  const handleApplyCustomizations = async () => {
    if (!solutionStructure) return;

    setIsAnalyzing(true);
    try {
      const customizations: UserCustomizations = {
        pillars: customizedPillars.map(p => ({
          name: p.name,
          enabled: p.enabled,
          priority: p.priority,
          customizations: p.customizations
        }))
      };

      const response = await mvpSolutionService.customizeSolution(
        solutionStructure.solution_structure,
        customizations,
        {
          user_id: user?.id || "anonymous",
          user_name: user?.name || "User"
        }
      );

      if (response.success) {
        setSolutionStructure({
          ...solutionStructure,
          solution_structure: response.solution_structure
        });
        toast.success("Customizations applied!", {
          description: "Your solution has been customized based on your preferences."
        });
      } else {
        toast.error("Customization failed", {
          description: response.error || "Unable to apply customizations"
        });
      }
    } catch (error: any) {
      toast.error("Customization failed", {
        description: error.message || "An error occurred"
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleStartCustomizedJourney = async () => {
    if (!solutionStructure) {
      handleStartJourney();
      return;
    }

    // Get enabled pillars in navigation order
    const enabledPillars = customizedPillars
      .filter(p => p.enabled)
      .sort((a, b) => a.navigation_order - b.navigation_order);

    if (enabledPillars.length === 0) {
      toast.error("Please enable at least one pillar");
      return;
    }

    // Create session
    setIsAnalyzing(true);
    try {
      const sessionResponse = await mvpSolutionService.createSession(
        user?.id || "anonymous",
        "mvp",
        {
          user_name: user?.name || "User",
          solution_structure: solutionStructure.solution_structure,
          reasoning: solutionStructure.reasoning,
          user_goals: userGoals
        }
      );

      if (sessionResponse.success && sessionResponse.session_id) {
        // Navigate to first enabled pillar
        const firstPillar = enabledPillars[0];
        const navResponse = await mvpSolutionService.navigateToPillar(
          sessionResponse.session_id,
          firstPillar.name,
          {
            user_id: user?.id || "anonymous"
          }
        );

        if (navResponse.success) {
          // Set enhanced initial message with solution context
          dispatch({
            type: "SET_CHAT_STATE",
            payload: {
              initialMessage: `Welcome! I'm your guide on this customized journey. Based on your goals: "${userGoals}", I've prepared a solution focusing on ${solutionStructure.solution_structure.strategic_focus}. We'll start with the ${firstPillar.name} pillar. ${solutionStructure.solution_structure.recommended_data_types.length > 0 ? `I recommend uploading ${solutionStructure.solution_structure.recommended_data_types.join(', ')} files.` : ''}`,
            },
          });
          
          // Navigate to the first pillar
          router.push(`/pillars/${firstPillar.name}`);
        } else {
          toast.error("Navigation failed", {
            description: navResponse.error || "Unable to navigate to pillar"
          });
        }
      } else {
        toast.error("Session creation failed", {
          description: sessionResponse.error || "Unable to create session"
        });
      }
    } catch (error: any) {
      toast.error("Failed to start journey", {
        description: error.message || "An error occurred"
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen w-full">
      <div className="w-full min-h-screen bg-card text-card-foreground pt-15 md:pt-20 rounded-xl shadow-lg border">
        <div className="text-center mb-10">
          <h1 className="text-h1 text-4xl bg-gradient-to-r from-blue-700 via-green-500 via-purple-500 to-orange-700 bg-clip-text text-transparent font-bold">
            Let's Build Your Coexistence Future
          </h1>
          <p className="text-lead text-sm mt-8 max-w-3xl mx-auto">
            Follow a guided journey through the four pillars of SymphAIny to
            transform your business. Our AI agent will analyze your goals and
            create a customized solution structure just for you.
          </p>
        </div>

        {/* Goal Analysis Section */}
        <div className="max-w-2xl mx-auto mb-8">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Target className="h-5 w-5" />
                <span>Tell Us About Your Goals</span>
              </CardTitle>
              <CardDescription>
                Help our AI agent understand what you want to achieve. The agent will perform critical reasoning to create a customized solution structure.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {!showGoalInput ? (
                <Button
                  onClick={() => setShowGoalInput(true)}
                  variant="outline"
                  className="w-full"
                >
                  <Lightbulb className="h-4 w-4 mr-2" />
                  Share Your Goals for AI-Powered Solution Design
                </Button>
              ) : (
                <div className="space-y-4">
                  <Textarea
                    placeholder="Describe your business goals, challenges, or what you hope to achieve with AI and automation..."
                    value={userGoals}
                    onChange={(e) => setUserGoals(e.target.value)}
                    rows={4}
                  />
                  <div className="flex space-x-2">
                    <Button
                      onClick={handleGoalAnalysis}
                      disabled={isAnalyzing || !userGoals.trim()}
                      className="flex-1"
                    >
                      {isAnalyzing ? (
                        <>
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                          Agent Analyzing...
                        </>
                      ) : (
                        <>
                          <Brain className="h-4 w-4 mr-2" />
                          Get AI-Powered Solution Structure
                        </>
                      )}
                    </Button>
                    <Button
                      onClick={() => {
                        setShowGoalInput(false);
                        setUserGoals("");
                        setSolutionStructure(null);
                        setShowCustomization(false);
                      }}
                      variant="outline"
                    >
                      Clear
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Discovery Context Summary */}
        {showDiscoverySummary && discoveryContext && (
          <div className="max-w-2xl mx-auto mb-8">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Brain className="h-5 w-5" />
                  <span>Discovered Business Context</span>
                  <span className="text-sm font-normal text-muted-foreground">
                    (Review and confirm)
                  </span>
                </CardTitle>
                <CardDescription>
                  Our AI agent discovered the following from your goals. Please review and confirm.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {discoveryContext.industry && (
                  <div>
                    <h4 className="font-semibold mb-2">Industry:</h4>
                    <Input
                      value={userEdits.industry || discoveryContext.industry || ''}
                      onChange={(e) => setUserEdits({ ...userEdits, industry: e.target.value })}
                      placeholder="Industry"
                    />
                    {discoveryContext.confidence?.industry && (
                      <p className="text-xs text-muted-foreground mt-1">
                        Confidence: {(discoveryContext.confidence.industry * 100).toFixed(0)}%
                      </p>
                    )}
                  </div>
                )}
                
                {discoveryContext.systems && discoveryContext.systems.length > 0 && (
                  <div>
                    <h4 className="font-semibold mb-2">Legacy Systems:</h4>
                    <div className="space-y-2">
                      {discoveryContext.systems.map((system: string, idx: number) => (
                        <div key={idx} className="flex items-center space-x-2">
                          <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                            {system}
                          </span>
                        </div>
                      ))}
                    </div>
                    {discoveryContext.confidence?.systems && (
                      <p className="text-xs text-muted-foreground mt-1">
                        Confidence: {(discoveryContext.confidence.systems * 100).toFixed(0)}%
                      </p>
                    )}
                  </div>
                )}
                
                {discoveryContext.goals && discoveryContext.goals.length > 0 && (
                  <div>
                    <h4 className="font-semibold mb-2">Goals:</h4>
                    <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
                      {discoveryContext.goals.map((goal: string, idx: number) => (
                        <li key={idx}>{goal}</li>
                      ))}
                    </ul>
                    {discoveryContext.confidence?.goals && (
                      <p className="text-xs text-muted-foreground mt-1">
                        Confidence: {(discoveryContext.confidence.goals * 100).toFixed(0)}%
                      </p>
                    )}
                  </div>
                )}
                
                {discoveryContext.constraints && discoveryContext.constraints.length > 0 && (
                  <div>
                    <h4 className="font-semibold mb-2">Constraints:</h4>
                    <div className="flex flex-wrap gap-2">
                      {discoveryContext.constraints.map((constraint: string, idx: number) => (
                        <span
                          key={idx}
                          className="px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-sm"
                        >
                          {constraint}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                <div className="flex space-x-2 pt-4">
                  <Button
                    onClick={handleCommitContext}
                    disabled={isCommitting}
                    className="flex-1"
                  >
                    {isCommitting ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Committing...
                      </>
                    ) : (
                      <>
                        <CheckCircle2 className="h-4 w-4 mr-2" />
                        Confirm & Commit Context
                      </>
                    )}
                  </Button>
                  <Button
                    onClick={() => {
                      setShowDiscoverySummary(false);
                      setDiscoveryContext(null);
                      setUserEdits({});
                    }}
                    variant="outline"
                  >
                    Edit
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Agent Reasoning Display */}
        {solutionStructure && solutionStructure.reasoning && (
          <div className="max-w-2xl mx-auto mb-8">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Brain className="h-5 w-5" />
                  <span>Agent Reasoning</span>
                  <span className="text-sm font-normal text-muted-foreground">
                    (Confidence: {(solutionStructure.reasoning.confidence * 100).toFixed(0)}%)
                  </span>
                </CardTitle>
                <CardDescription>
                  The AI agent's critical reasoning about your goals
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="font-semibold mb-2">Analysis:</h4>
                  <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                    {solutionStructure.reasoning.analysis || "No analysis available"}
                  </p>
                </div>
                {solutionStructure.reasoning.key_insights.length > 0 && (
                  <div>
                    <h4 className="font-semibold mb-2">Key Insights:</h4>
                    <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
                      {solutionStructure.reasoning.key_insights.map((insight, idx) => (
                        <li key={idx}>{insight}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {solutionStructure.reasoning.recommendations.length > 0 && (
                  <div>
                    <h4 className="font-semibold mb-2">Recommendations:</h4>
                    <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
                      {solutionStructure.reasoning.recommendations.map((rec, idx) => (
                        <li key={idx}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        {/* Solution Structure Display */}
        {solutionStructure && solutionStructure.solution_structure && (
          <div className="max-w-4xl mx-auto mb-8">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Sparkles className="h-5 w-5" />
                  <span>Your Customized Solution Structure</span>
                </CardTitle>
                <CardDescription>
                  Based on agent analysis, here's your recommended solution structure
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Pillars */}
                <div>
                  <h4 className="font-semibold mb-4">Pillars (in recommended order):</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {customizedPillars
                      .sort((a, b) => a.navigation_order - b.navigation_order)
                      .map((pillar) => {
                        const pillarInfo = pillars.find(p => p.name.toLowerCase() === pillar.name);
                        return (
                          <div
                            key={pillar.name}
                            className={`p-4 border rounded-lg ${
                              pillar.enabled ? "bg-primary/5 border-primary" : "bg-muted/50 border-muted"
                            }`}
                          >
                            <div className="flex items-center justify-between mb-2">
                              <div className="flex items-center space-x-2">
                                {pillarInfo && (
                                  <div className={`w-8 h-8 rounded-full flex items-center justify-center ${pillarInfo.color}`}>
                                    <pillarInfo.icon className="w-4 h-4 text-white" />
                                  </div>
                                )}
                                <div>
                                  <h5 className="font-semibold capitalize">{pillar.name}</h5>
                                  <p className="text-xs text-muted-foreground">
                                    Priority: {pillar.priority} | Order: {pillar.navigation_order}
                                  </p>
                                </div>
                              </div>
                              <div className="flex items-center space-x-2">
                                {pillar.enabled ? (
                                  <CheckCircle2 className="h-5 w-5 text-green-500" />
                                ) : (
                                  <XCircle className="h-5 w-5 text-gray-400" />
                                )}
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => handleCustomizePillar(pillar.name, !pillar.enabled)}
                                >
                                  <Settings className="h-4 w-4" />
                                </Button>
                              </div>
                            </div>
                            {pillar.customizations.focus_areas && pillar.customizations.focus_areas.length > 0 && (
                              <div className="mt-2">
                                <p className="text-xs text-muted-foreground">
                                  Focus: {pillar.customizations.focus_areas.join(", ")}
                                </p>
                              </div>
                            )}
                          </div>
                        );
                      })}
                  </div>
                </div>

                {/* Recommended Data Types */}
                {solutionStructure.solution_structure.recommended_data_types.length > 0 && (
                  <div>
                    <h4 className="font-semibold mb-2">Recommended Data Types:</h4>
                    <div className="flex flex-wrap gap-2">
                      {solutionStructure.solution_structure.recommended_data_types.map((dataType, index) => (
                        <span
                          key={index}
                          className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                        >
                          {dataType.toUpperCase()}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Strategic Focus */}
                <div>
                  <h4 className="font-semibold mb-2">Strategic Focus:</h4>
                  <p className="text-sm text-muted-foreground capitalize">
                    {solutionStructure.solution_structure.strategic_focus}
                  </p>
                </div>

                {/* Customization Options */}
                <div>
                  <h4 className="font-semibold mb-2">Available Customizations:</h4>
                  <div className="flex flex-wrap gap-2">
                    {solutionStructure.solution_structure.customization_options.workflow_creation && (
                      <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                        Workflow Creation
                      </span>
                    )}
                    {solutionStructure.solution_structure.customization_options.interactive_guidance && (
                      <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm">
                        Interactive Guidance
                      </span>
                    )}
                    {solutionStructure.solution_structure.customization_options.automated_analysis && (
                      <span className="px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-sm">
                        Automated Analysis
                      </span>
                    )}
                  </div>
                </div>

                {/* Apply Customizations Button */}
                {showCustomization && (
                  <div className="flex justify-end">
                    <Button
                      onClick={handleApplyCustomizations}
                      disabled={isAnalyzing}
                      variant="outline"
                    >
                      {isAnalyzing ? (
                        <>
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                          Applying...
                        </>
                      ) : (
                        <>
                          <Settings className="h-4 w-4 mr-2" />
                          Apply Customizations
                        </>
                      )}
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        {/* Start Journey Button */}
        <div className="text-center pt-4">
          <Button
            onClick={solutionStructure ? handleStartCustomizedJourney : handleStartJourney}
            size="lg"
            className="bg-gradient-to-r from-blue-600 to-purple-600 button-traverse-border"
            disabled={isAnalyzing}
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="mr-2 w-5 h-5 animate-spin" />
                Starting Journey...
              </>
            ) : (
              <>
                {solutionStructure ? "Start Your Customized Journey" : "Start Your Journey"}
                <ArrowRight className="ml-2 w-5 h-5" />
              </>
            )}
          </Button>
        </div>

        {/* ✅ PHASE 2.1: Artifact Gallery */}
        <div className="mt-12">
          <ArtifactGallery />
        </div>

        {/* ✅ PHASE 3.1: Coexistence Explanation */}
        <div className="mt-12">
          <CoexistenceExplanation />
        </div>
      </div>
    </div>
  );
}
