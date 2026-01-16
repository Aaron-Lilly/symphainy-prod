"use client";

import React, { useState, useEffect } from "react";

// Force dynamic rendering to avoid SSR issues
export const dynamic = 'force-dynamic';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import ReactMarkdown from "react-markdown";

import dynamicImport from "next/dynamic";
import RoadmapTimeline from "@/components/experience/RoadmapTimeline";
import { Button } from "@/components/ui/button";
import { usePlatformState } from "@/shared/state/PlatformStateProvider";
import { useOutcomesAPIManager } from "@/shared/hooks/useOutcomesAPIManager";
import { Loader, AlertTriangle, FileText, Play, Download, Upload, MessageCircle } from "lucide-react";
import { FileMetadata, FileType, FileStatus } from "@/shared/types/file";
import { useSetAtom } from "jotai";
import { chatbotAgentInfoAtom, mainChatbotOpenAtom } from "@/shared/atoms/chatbot-atoms";
import { SecondaryChatbotAgent, SecondaryChatbotTitle } from "@/shared/types/secondaryChatbot";
import { StateHandler, LoadingIndicator, ErrorDisplay, SuccessDisplay } from "@/components/ui/loading-error-states";

// Import new micro-modular components
import InsightsTab from "./components/InsightsTab";
// ExperienceService will be dynamically imported when needed

const GraphComponent = dynamicImport(
  () => import("@/components/operations/GraphComponent"),
  {
    ssr: false,
    loading: () => <Loader className="animate-spin" size={24} />,
  },
);

// File types that are relevant for business outcomes pillar (all types)
const BUSINESS_OUTCOMES_FILE_TYPES = [
  FileType.Document,
  FileType.Pdf,
  FileType.Structured,
  FileType.Text,
];

export default function BusinessOutcomesPillarPage() {
  const setAgentInfo = useSetAtom(chatbotAgentInfoAtom);
  const setMainChatbotOpen = useSetAtom(mainChatbotOpenAtom);

  const { state } = usePlatformState();
  const outcomesAPIManager = useOutcomesAPIManager();
  const [showProposal, setShowProposal] = useState(false);
  const [selectedFile, setSelectedFile] = useState<FileMetadata | null>(null);
  const [businessOutcomesFiles, setBusinessOutcomesFiles] = useState<FileMetadata[]>([]);
  const [initialized, setInitialized] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [roadmapResult, setRoadmapResult] = useState<any | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  
  // New state for dual-agent architecture
  const [sessionToken, setSessionToken] = useState<string | null>(null);
  const [insightsData, setInsightsData] = useState<any>(null);
  const [operationsData, setOperationsData] = useState<any>(null);
  const [pocProposal, setPocProposal] = useState<any | null>(null);
  const [isLoadingPoc, setIsLoadingPoc] = useState(false);
  const [isLoadingData, setIsLoadingData] = useState(false);
  
  // New state for source files and additional context
  const [sourceFiles, setSourceFiles] = useState<any[]>([]);
  const [additionalFiles, setAdditionalFiles] = useState<FileMetadata[]>([]);
  const [sessionState, setSessionState] = useState<any | null>(null);
  const [isGeneratingOutputs, setIsGeneratingOutputs] = useState(false);
  const [businessOutcomesOutputs, setBusinessOutcomesOutputs] = useState<any>(null);

  // Get files from Content realm state
  useEffect(() => {
    const getAllFiles = () => {
      try {
        // Get files from Content realm state
        const contentFiles = state.realm.content.files || [];
        setBusinessOutcomesFiles(contentFiles as FileMetadata[]);
      } catch (error) {
        console.error("[BusinessOutcomes] Error getting files:", error);
      }
    };

    if (!initialized && state.session.sessionId) {
      getAllFiles();
      setInitialized(true);
    }
  }, [state.realm.content.files, state.session.sessionId, initialized]);

  // Load cross-pillar data from realm states
  useEffect(() => {
    const loadCrossPillarData = () => {
      setIsLoadingData(true);
      try {
        // Get insights data from Insights realm state
        const insightsState = state.realm.insights;
        if (insightsState && Object.keys(insightsState).length > 0) {
          setInsightsData(insightsState);
        }
        
        // Get journey data from Journey realm state
        const journeyState = state.realm.journey;
        if (journeyState && Object.keys(journeyState).length > 0) {
          setOperationsData(journeyState); // Keep variable name for compatibility
        }
        
      } catch (error: any) {
        console.error("[BusinessOutcomes] Error loading cross-pillar data:", error);
        setError(error.message || "Failed to load cross-pillar data");
      } finally {
        setIsLoadingData(false);
      }
    };

    if (state.session.sessionId) {
      loadCrossPillarData();
      setSessionToken(state.session.sessionId);
    }
  }, [state.realm.insights, state.realm.journey, state.session.sessionId]);

  // Set up Business Outcomes Liaison Agent as secondary option (not default)
  useEffect(() => {
    // Configure the secondary agent but don't show it by default
    setAgentInfo({
      agent: SecondaryChatbotAgent.BUSINESS_OUTCOMES_LIAISON,
      title: SecondaryChatbotTitle.BUSINESS_OUTCOMES_LIAISON,
      file_url: "",
      additional_info: "Business outcomes and strategic planning assistance"
    });
    // Keep main chatbot open by default - GuideAgent will be shown
    setMainChatbotOpen(true);
  }, [setAgentInfo, setMainChatbotOpen]);

  const getFileTypeDisplay = (fileType: FileType | string): string => {
    const typeMap: Record<FileType, string> = {
      [FileType.Document]: "Document",
      [FileType.Pdf]: "PDF",
      [FileType.Structured]: "Structured",
      [FileType.Text]: "Text",
      [FileType.Image]: "Image",
      [FileType.Binary]: "Binary",
      [FileType.SopWorkflow]: "SOP/Workflow",
    };
    return typeMap[fileType] || "Unknown";
  };

  const handleAdditionalFileUpload = async (file: FileMetadata) => {
    try {
      if (!state.session.sessionId) return;
      
      // Store additional file in realm state
      const currentFiles = state.realm.outcomes.additionalFiles || [];
      const updatedFiles = [...currentFiles, file];
      
      // Note: This would ideally be done via State Surface, but for now we'll store in local state
      setAdditionalFiles(prev => [...prev, file]);
    } catch (error: any) {
      console.error("[BusinessOutcomes] Error uploading additional file:", error);
      setError(error.message || "Failed to upload additional file");
    }
  };

  const handleGenerateExperienceOutputs = async () => {
    setIsGeneratingOutputs(true);
    setError(null);
    
    try {
      if (!state.session.sessionId) {
        setError("Session required to generate outcomes");
        return;
      }

      // First, synthesize outcome from all pillars
      const synthesisResult = await outcomesAPIManager.synthesizeOutcome();
      
      if (!synthesisResult.success) {
        setError(synthesisResult.error || "Failed to synthesize outcome");
        return;
      }

      // Extract goals from synthesis for roadmap generation
      const goals: string[] = [];
      if (synthesisResult.synthesis?.content_summary) {
        goals.push("Content analysis and processing");
      }
      if (synthesisResult.synthesis?.insights_summary) {
        goals.push("Data insights and interpretation");
      }
      if (synthesisResult.synthesis?.journey_summary) {
        goals.push("Process optimization and workflow");
      }
      
      // If no specific goals, use default
      if (goals.length === 0) {
        goals.push("Complete platform implementation");
      }

      // Generate Strategic Roadmap using OutcomesAPIManager
      try {
        const roadmapResult = await outcomesAPIManager.generateRoadmap(goals);

        if (roadmapResult.success && roadmapResult.roadmap) {
          setRoadmapResult({
            success: true,
            roadmap: roadmapResult.roadmap,
            roadmap_id: roadmapResult.roadmap.roadmap_id
          });
        } else {
          console.error("[BusinessOutcomes] Roadmap generation failed:", roadmapResult.error);
        }
      } catch (error: any) {
        console.error("[BusinessOutcomes] Error generating roadmap:", error);
        setError(error.message || "Failed to generate roadmap");
      }

      // Generate POC Proposal using OutcomesAPIManager
      try {
        const pocDescription = synthesisResult.synthesis?.overall_synthesis || 
          "Proof of concept for platform implementation based on analysis across all pillars";
        
        const pocResult = await outcomesAPIManager.createPOC(pocDescription);

        if (pocResult.success && pocResult.poc_proposal) {
          setPocProposal({
            success: true,
            proposal: pocResult.poc_proposal,
            proposal_id: pocResult.poc_proposal.poc_id
          });
        } else {
          console.error("[BusinessOutcomes] POC generation failed:", pocResult.error);
        }
      } catch (error: any) {
        console.error("[BusinessOutcomes] Error generating POC proposal:", error);
        setError(error.message || "Failed to generate POC proposal");
      }

      // Store synthesis in realm state
      if (synthesisResult.synthesis) {
        setBusinessOutcomesOutputs({
          synthesis: synthesisResult.synthesis,
          roadmap: roadmapResult?.roadmap,
          poc: pocProposal?.poc_proposal
        });
      }
    } catch (error: any) {
      console.error("[BusinessOutcomes] Error generating outputs:", error);
      setError(error.message || "Failed to generate business outcomes outputs");
    } finally {
      setIsGeneratingOutputs(false);
    }
  };

  // Check if we have data from other pillars
  const hasInsights = !!insightsData;
  const hasOperations = !!operationsData;
  const hasSourceFiles = businessOutcomesFiles.length > 0 || additionalFiles.length > 0;

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800">Business Outcomes</h1>
        <p className="text-gray-600 mt-2">
          Review and synthesize insights from all pillars to create strategic roadmaps and POC proposals
        </p>
      </div>

      {/* Error Display */}
      {error && (
        <Alert className="mb-6 border-red-200 bg-red-50">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Main Content */}
      <Tabs defaultValue="journey" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="journey">Journey Recap</TabsTrigger>
          <TabsTrigger value="data">Data</TabsTrigger>
          <TabsTrigger value="insights">Insights</TabsTrigger>
          <TabsTrigger value="operations">Journey</TabsTrigger>
        </TabsList>

        <TabsContent value="journey" className="pt-4">
          <Card>
            <CardHeader>
              <CardTitle>Business Outcomes Journey</CardTitle>
              <CardDescription>
                Overview of your analysis journey across all pillars
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">
                      {businessOutcomesFiles.length}
                    </div>
                    <div className="text-sm text-gray-600">Source Files</div>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">
                      {hasInsights ? "✓" : "✗"}
                    </div>
                    <div className="text-sm text-gray-600">Insights Analysis</div>
                  </div>
                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">
                      {hasOperations ? "✓" : "✗"}
                    </div>
                    <div className="text-sm text-gray-600">Operations Blueprint</div>
                  </div>
                </div>

                {hasInsights && hasOperations && (
                  <div className="mt-6">
                    <Button
                      onClick={handleGenerateExperienceOutputs}
                      disabled={isGeneratingOutputs}
                      className="w-full"
                    >
                      {isGeneratingOutputs ? (
                        <>
                          <Loader className="w-4 h-4 mr-2 animate-spin" />
                          Generating Business Outcomes...
                        </>
                      ) : (
                        <>
                          <Play className="w-4 h-4 mr-2" />
                          Generate Strategic Roadmap & POC
                        </>
                      )}
                    </Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="data" className="pt-4">
          {hasSourceFiles ? (
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Source Files</CardTitle>
                  <CardDescription>
                    Files used for analysis across all pillars
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {businessOutcomesFiles.map((file) => (
                      <div key={file.uuid} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <FileText className="w-5 h-5 text-gray-500" />
                          <div>
                            <p className="font-medium text-gray-900">{file.ui_name}</p>
                            <p className="text-sm text-gray-500">{getFileTypeDisplay(file.file_type)}</p>
                          </div>
                        </div>
                        <Badge variant="secondary">{file.status}</Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {additionalFiles.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Additional Context Files</CardTitle>
                    <CardDescription>
                      Files added during the business outcomes phase
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {additionalFiles.map((file) => (
                        <div key={file.uuid} className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                          <div className="flex items-center space-x-3">
                            <Upload className="w-5 h-5 text-blue-500" />
                            <div>
                              <p className="font-medium text-gray-900">{file.ui_name}</p>
                              <p className="text-sm text-gray-500">{getFileTypeDisplay(file.file_type)}</p>
                            </div>
                          </div>
                          <Badge variant="secondary">Additional</Badge>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-muted-foreground">
                No source files available. Complete Insights and Operations pillar analysis first.
              </p>
            </div>
          )}
        </TabsContent>

        <TabsContent value="insights" className="pt-4">
          <InsightsTab 
            insightsData={insightsData}
            isLoading={isLoadingData}
          />
        </TabsContent>

        <TabsContent value="operations" className="pt-4">
          {hasOperations ? (
            <div className="space-y-6">
              <h3 className="text-h3 mb-2">Process Optimization Results</h3>

              {/* Coexistence Analysis Summary */}
              {operationsData.coexistence_analysis && (
                <Card className="border-blue-200 bg-blue-50">
                  <CardHeader>
                    <CardTitle className="text-blue-800">Coexistence Analysis</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="prose max-w-none">
                      <p className="text-sm text-gray-700 leading-relaxed">
                        {operationsData.coexistence_analysis.summary || "Analysis completed successfully."}
                      </p>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Optimized Workflow Visualization */}
              {operationsData.optimized_workflow && Object.keys(operationsData.optimized_workflow).length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Optimized Workflow</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="min-h-[400px] flex items-center justify-center bg-accent/50 rounded-md p-2 border">
                      <GraphComponent data={operationsData.optimized_workflow} />
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Optimized SOP */}
              {operationsData.optimized_sop && (
                <Card className="border-green-200 bg-green-50">
                  <CardHeader>
                    <CardTitle className="text-green-800">Optimized SOP</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="prose max-w-none">
                      <ReactMarkdown className="text-sm text-gray-700 leading-relaxed">
                        {operationsData.optimized_sop}
                      </ReactMarkdown>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-muted-foreground">
                No journey data available. Complete the Journey pillar analysis first.
              </p>
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Roadmap Section - Always Visible */}
      <div className="mt-8">
        <Card>
          <CardHeader>
            <CardTitle>Strategic Roadmap</CardTitle>
            <CardDescription>
              Phased timeline and milestones for your strategic plan
            </CardDescription>
          </CardHeader>
          <CardContent>
            {roadmapResult?.roadmap ? (
              <RoadmapTimeline roadmapData={typeof roadmapResult.roadmap === 'string' ? roadmapResult.roadmap : JSON.stringify(roadmapResult.roadmap)} />
            ) : (
              <div className="text-center py-12">
                <p className="text-muted-foreground mb-4">
                  No roadmap generated yet. Complete Insights and Operations pillar analysis, then click "Generate Strategic Roadmap & POC" above.
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* POC Proposal Section - Always Visible */}
      <div className="mt-8">
        <Card>
          <CardHeader>
            <CardTitle>Proof of Concept Proposal</CardTitle>
            <CardDescription>
              Comprehensive POC proposal based on your analysis
            </CardDescription>
          </CardHeader>
          <CardContent>
            {pocProposal?.proposal ? (
              <div className="space-y-6">
                {typeof pocProposal.proposal === 'string' ? (
                  <div className="prose max-w-none">
                    <ReactMarkdown className="text-sm text-gray-700 leading-relaxed">
                      {pocProposal.proposal}
                    </ReactMarkdown>
                  </div>
                ) : (
                  <>
                    {pocProposal.proposal.objectives && (
                      <div>
                        <h3 className="text-lg font-semibold mb-2">Objectives</h3>
                        <ul className="list-disc pl-5 space-y-1">
                          {Array.isArray(pocProposal.proposal.objectives) ? (
                            pocProposal.proposal.objectives.map((obj: any, idx: number) => (
                              <li key={idx} className="text-sm text-gray-700">
                                {typeof obj === 'string' ? obj : obj.description || JSON.stringify(obj)}
                              </li>
                            ))
                          ) : (
                            <li className="text-sm text-gray-700">{JSON.stringify(pocProposal.proposal.objectives)}</li>
                          )}
                        </ul>
                      </div>
                    )}
                    {pocProposal.proposal.scope && (
                      <div>
                        <h3 className="text-lg font-semibold mb-2">Scope</h3>
                        <div className="prose max-w-none text-sm text-gray-700">
                          {typeof pocProposal.proposal.scope === 'string' ? (
                            <ReactMarkdown>{pocProposal.proposal.scope}</ReactMarkdown>
                          ) : (
                            <pre className="whitespace-pre-wrap">{JSON.stringify(pocProposal.proposal.scope, null, 2)}</pre>
                          )}
                        </div>
                      </div>
                    )}
                    {pocProposal.proposal.timeline && (
                      <div>
                        <h3 className="text-lg font-semibold mb-2">Timeline</h3>
                        <div className="prose max-w-none text-sm text-gray-700">
                          {typeof pocProposal.proposal.timeline === 'string' ? (
                            <ReactMarkdown>{pocProposal.proposal.timeline}</ReactMarkdown>
                          ) : (
                            <pre className="whitespace-pre-wrap">{JSON.stringify(pocProposal.proposal.timeline, null, 2)}</pre>
                          )}
                        </div>
                      </div>
                    )}
                    {pocProposal.proposal.success_criteria && (
                      <div>
                        <h3 className="text-lg font-semibold mb-2">Success Criteria</h3>
                        <ul className="list-disc pl-5 space-y-1">
                          {Array.isArray(pocProposal.proposal.success_criteria) ? (
                            pocProposal.proposal.success_criteria.map((criteria: any, idx: number) => (
                              <li key={idx} className="text-sm text-gray-700">
                                {typeof criteria === 'string' ? criteria : criteria.description || JSON.stringify(criteria)}
                              </li>
                            ))
                          ) : (
                            <li className="text-sm text-gray-700">{JSON.stringify(pocProposal.proposal.success_criteria)}</li>
                          )}
                        </ul>
                      </div>
                    )}
                    {pocProposal.proposal.description && (
                      <div>
                        <h3 className="text-lg font-semibold mb-2">Description</h3>
                        <div className="prose max-w-none">
                          <ReactMarkdown className="text-sm text-gray-700 leading-relaxed">
                            {pocProposal.proposal.description}
                          </ReactMarkdown>
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>
            ) : (
              <div className="text-center py-12">
                <p className="text-muted-foreground mb-4">
                  No POC proposal generated yet. Complete Insights and Operations pillar analysis, then click "Generate Strategic Roadmap & POC" above.
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}