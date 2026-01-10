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
import { useGlobalSession } from "@/shared/agui/GlobalSessionProvider";
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

  const { getPillarState, setPillarState } = useGlobalSession();
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

  // Get files from global session state - check all pillar states for files
  useEffect(() => {
    const getAllFiles = () => {
      try {
        const contentState = getPillarState('content');
        const files: FileMetadata[] = [];
        
        if (contentState?.files) {
          files.push(...contentState.files);
        }
        
        if (contentState?.uploadedFiles) {
          files.push(...contentState.uploadedFiles);
        }
        
        setBusinessOutcomesFiles(files);
      } catch (error) {
        console.error("Error getting files:", error);
      }
    };

    if (!initialized) {
      getAllFiles();
      setInitialized(true);
    }
  }, [getPillarState, initialized]);

  // Initialize experience session
  const initializeSession = async () => {
    try {
      const token = `business-outcomes-session-${Math.random().toString(36).slice(2)}`;
      setSessionToken(token);
      
      // Create business outcomes session
      const { ExperienceService } = await import("@/shared/services/experience");
      await ExperienceService.createExperienceSession(token);
      
      // Get cross-pillar data
      await loadCrossPillarData(token);
      
    } catch (error: any) {
      console.error("Error initializing session:", error);
      setError(error.message || "Failed to initialize business outcomes session");
    }
  };

  // Load cross-pillar data
  const loadCrossPillarData = async (token: string) => {
    setIsLoadingData(true);
    try {
      // Get insights data
      const { ExperienceService } = await import("@/shared/services/experience");
      const insightsResponse = await ExperienceService.getCrossPillarData({
        sessionToken: token,
        pillar: 'insights',
        dataType: 'summary',
      });
      
      if (insightsResponse.success) {
        setInsightsData(insightsResponse.data);
      }
      
      // Get operations data
      const operationsResponse = await ExperienceService.getCrossPillarData({
        sessionToken: token,
        pillar: 'operations',
        dataType: 'blueprint',
      });
      
      if (operationsResponse.success) {
        setOperationsData(operationsResponse.data);
      }
      
    } catch (error: any) {
      console.error("Error loading cross-pillar data:", error);
      setError(error.message || "Failed to load cross-pillar data");
    } finally {
      setIsLoadingData(false);
    }
  };

  // Initialize session on component mount
  useEffect(() => {
    if (!sessionToken) {
      initializeSession();
    }
  }, [sessionToken]);

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
      if (!sessionToken) return;
      
      const { ExperienceService } = await import("@/shared/services/experience");
      await ExperienceService.storeAdditionalContext({
        session_token: sessionToken,
        context_type: 'additional_file',
        context_data: file,
        priority: 'medium',
      });
      
      setAdditionalFiles(prev => [...prev, file]);
    } catch (error: any) {
      console.error("Error uploading additional file:", error);
      setError(error.message || "Failed to upload additional file");
    }
  };

  const handleGenerateExperienceOutputs = async () => {
    setIsGeneratingOutputs(true);
    try {
      if (!sessionToken) return;
      
      // Prepare pillar outputs
      const pillarOutputs = {
        content_pillar: {
          files: businessOutcomesFiles,
          additional_files: additionalFiles
        },
        insights_pillar: insightsData,
        operations_pillar: operationsData
      };

      // Generate Strategic Roadmap using new BusinessOutcomesSolutionService
      try {
        const { BusinessOutcomesSolutionService } = await import("@/shared/services/business-outcomes");
        const businessOutcomesService = new BusinessOutcomesSolutionService();
        
        const roadmapData = await businessOutcomesService.generateRoadmap({
          sessionId: sessionToken,
          roadmapOptions: {},
          userId: "anonymous",
          sessionToken: sessionToken
        });

        if (roadmapData.success && roadmapData.roadmap) {
          setRoadmapResult(roadmapData);
        }
      } catch (error: any) {
        console.error("Error generating roadmap:", error);
        setError(error.message || "Failed to generate roadmap");
      }

      // Generate POC Proposal using new BusinessOutcomesSolutionService
      try {
        const { BusinessOutcomesSolutionService } = await import("@/shared/services/business-outcomes");
        const businessOutcomesService = new BusinessOutcomesSolutionService();
        
        const pocData = await businessOutcomesService.generatePOCProposal({
          sessionId: sessionToken,
          pocOptions: {},
          userId: "anonymous",
          sessionToken: sessionToken
        });

        if (pocData.success && pocData.poc_proposal) {
          setPocProposal(pocData);
        }
      } catch (error: any) {
        console.error("Error generating POC proposal:", error);
        setError(error.message || "Failed to generate POC proposal");
      }

      // Also call ExperienceService for any additional outputs
      const { ExperienceService } = await import("@/shared/services/experience");
      const response = await ExperienceService.generateExperienceOutputs({
        sessionToken,
        outputType: 'all',
        includeVisualizations: true,
      });
      
      if (response.status === 'success') {
        setBusinessOutcomesOutputs(response.outputs);
      }
    } catch (error: any) {
      console.error("Error generating outputs:", error);
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
          <TabsTrigger value="operations">Operations</TabsTrigger>
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
                No operations data available. Complete the Operations pillar analysis first.
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