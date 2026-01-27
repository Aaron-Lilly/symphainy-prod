"use client";
import React, { useState, useEffect } from "react";

// Force dynamic rendering to avoid SSR issues
export const dynamic = 'force-dynamic';
// ✅ PHASE 4: Session-First - Use SessionBoundary for session state
import { useSessionBoundary, SessionStatus } from "@/shared/state/SessionBoundaryProvider";
import { useAuth } from "@/shared/auth/AuthProvider"; // Keep for user data
import { usePlatformState } from "@/shared/state/PlatformStateProvider";
import { useJourneyAPIManager } from "@/shared/hooks/useJourneyAPIManager";
import { SecondaryChatbotAgent } from "@/shared/types/secondaryChatbot";
// ✅ PHASE 5: Use PlatformStateProvider instead of Jotai atoms (already imported above)
import { usePathname } from "next/navigation";
import { StateHandler, LoadingIndicator, ErrorDisplay, SuccessDisplay } from "@/components/ui/loading-error-states";
import { toast } from "sonner";
import { FileType, FileMetadata } from "@/shared/types/file";
import { LoadingState, OperationsError } from "@/shared/types/operations";
import { Badge } from "@/components/ui/badge";

// Import micro-modular components
import JourneyChoice from "@/components/operations/JourneyChoice";
import FileSelector from "./components/FileSelector";
import WizardActive from "./components/WizardActive";
import ProcessBlueprint from "./components/ProcessBlueprint";
import CoexistenceBlueprint from "./components/CoexistenceBlueprint";
import {
  Card,
  CardDescription,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { PillarCompletionMessage } from "../shared/components/PillarCompletionMessage";

// File types that are relevant for journey
const JOURNEY_FILE_TYPES = [FileType.Document, FileType.Pdf, FileType.Text, FileType.SopWorkflow];

export default function JourneyPillar() {
  // ✅ PHASE 4: Session-First - Use SessionBoundary for session state
  const { state: sessionState } = useSessionBoundary();
  const { user } = useAuth(); // Keep for user data
  // ✅ PHASE 5: Use PlatformStateProvider instead of Jotai atoms
  const { state, setChatbotAgentInfo, setMainChatbotOpen } = usePlatformState();
  const setAgentInfo = setChatbotAgentInfo; // Alias for compatibility
  const isAuthenticated = sessionState.status === SessionStatus.Active;
  const journeyAPIManager = useJourneyAPIManager();

  const pathname = usePathname();

  // Local UI state
  const [selected, setSelected] = useState<{
    [type: string]: FileMetadata | null;
  }>({ SOP: null, workflow: null });
  const [loading, setLoading] = useState<LoadingState>({
    isLoading: false,
    operation: undefined,
    progress: undefined,
    message: undefined
  });
  const [error, setError] = useState<OperationsError | null>(null);
  const [success, setSuccess] = useState<string | undefined>(undefined);
  const [journey, setJourney] = useState<"select" | "wizard" | null>(null);
  const [journeyFiles, setJourneyFiles] = useState<FileMetadata[]>([]);
  const [isLoadingFiles, setIsLoadingFiles] = useState(false);

  // Journey state initialization
  const [initialized, setInitialized] = useState(false);

  // State for ProcessBlueprint and CoexistenceBlueprint
  const [journeyState, setJourneyState] = useState<{
    workflowData?: any;
    sopText?: string;
    optimizedWorkflow?: any;
    optimizedSop?: string;
    analysisResults?: {
      errors?: Array<{ type: string; error: string }>;
      analysisType?: string;
    };
  }>({});
  
  const [coexistenceState, setCoexistenceState] = useState<{
    sopText?: string | any;
    workflowData?: any;
    generatedSopUuid?: string;
    generatedWorkflowUuid?: string;
    blueprint?: any;
    isEnabled?: boolean;
  }>({
    isEnabled: false
  });

  // Helper functions for state management
  const setLoadingState = (isLoading: boolean, operation?: string, message?: string, progress?: number) => {
    setLoading({
      isLoading,
      operation: operation as any,
      message,
      progress
    });
  };

  const setErrorState = (message: string, operation?: 'sop_to_workflow' | 'workflow_to_sop' | 'coexistence_analysis', code?: string, file_uuid?: string) => {
    setError({
      message,
      operation: operation || 'sop_to_workflow',
      code,
      file_uuid
    });
  };

  const clearError = () => setError(null);
  const clearSuccess = () => setSuccess(undefined);

  // Get files from Content Realm state
  useEffect(() => {
    const getAllFiles = async () => {
      if (!isAuthenticated || !sessionState.sessionId) return;
      
      setIsLoadingFiles(true);
      try {
        // Get files from Content realm state
        const contentFiles = state.realm.content.files || [];
        
        // Filter for journey-relevant files
        const journeyFiles = contentFiles.filter((file: any) => 
          file && JOURNEY_FILE_TYPES.includes(file.file_type || file.type)
        );
        
        setJourneyFiles(journeyFiles as FileMetadata[]);
      } catch (error) {
        console.error("[JourneyPillar] Error getting files:", error);
        toast.error("Failed to load files", {
          description: "Unable to retrieve files for journey"
        });
      } finally {
        setIsLoadingFiles(false);
      }
    };

    if (!initialized && isAuthenticated && sessionState.sessionId) {
      getAllFiles();
      setInitialized(true);
    }
  }, [isAuthenticated, initialized, sessionState.sessionId, state.realm.content.files]);


  // Set up journey liaison agent
  useEffect(() => {
    setAgentInfo({
      title: "Journey Liaison",
      agent: "journey",
      file_url: "",
      additional_info: "Your AI assistant for journey and workflow management",
    });
    // Keep main chatbot open by default - GuideAgent will be shown
    setMainChatbotOpen(true);
  }, [setAgentInfo, setMainChatbotOpen]);

  // Handle coexistence analysis
  const handleAnalyze = async () => {
    if (!selected.SOP || !selected.workflow) {
      setErrorState("Please select both SOP and workflow files for analysis");
      return;
    }

    setLoadingState(true, 'coexistence_analysis', 'Analyzing coexistence...');

    try {
      const result = await journeyAPIManager.analyzeCoexistence(
        selected.SOP.uuid,
        selected.workflow.uuid
      );

      if (result.success && result.coexistence_analysis) {
        setSuccess("Coexistence analysis completed successfully!");
        
        // Update coexistence state with blueprint
        const blueprint = result.coexistence_analysis.blueprint || {};
        const optimizedSop = result.coexistence_analysis.opportunities?.find((o: any) => o.type === 'sop_optimization');
        const optimizedWorkflow = result.coexistence_analysis.opportunities?.find((o: any) => o.type === 'workflow_optimization');
        
        setCoexistenceState(prev => ({
          ...prev,
          blueprint,
          sopText: optimizedSop?.description || prev.sopText,
        }));
        
        // ✅ PHASE 4.2: Set IDs for process optimization
        if (selected.SOP?.uuid) setSelectedSopId(selected.SOP.uuid);
        if (selected.workflow?.uuid) setSelectedWorkflowId(selected.workflow.uuid);
          workflowData: optimizedWorkflow?.description || prev.workflowData,
          isEnabled: true
        }));
        
        // Update journey state with optimized results
        if (optimizedSop || optimizedWorkflow) {
          setJourneyState(prev => ({
            ...prev,
            optimizedSop: optimizedSop?.description,
            optimizedWorkflow: optimizedWorkflow?.description,
            analysisResults: {
              analysisType: 'coexistence',
              errors: []
            }
          }));
        }
        
        toast.success("Coexistence analysis completed!", {
          description: "Analysis results are ready for review"
        });
      } else {
        setErrorState(result.error || "Analysis failed", 'coexistence_analysis');
      }
    } catch (error: any) {
      setErrorState(error.message || "Failed to analyze coexistence", 'coexistence_analysis');
    } finally {
      setLoadingState(false);
    }
  };

  // Handle wizard start
  const handleStartWizard = async () => {
    setJourney('wizard');
  };

  // Handle workflow generation from SOP
  const handleGenerateWorkflowFromSop = async () => {
    if (!selected.SOP) {
      setErrorState("Please select an SOP file");
      return;
    }

    setLoadingState(true, 'sop_to_workflow', 'Generating workflow from SOP...');

    try {
      const result = await journeyAPIManager.createWorkflow(selected.SOP.uuid);

      if (result.success && result.workflow) {
        setSuccess("Workflow generated successfully!");
        
        // Update journey state with generated workflow
        setJourneyState(prev => ({
          ...prev,
          workflowData: result.workflow,
          sopText: selected.SOP?.ui_name || prev.sopText
        }));
        
        // Update coexistence state
        setCoexistenceState(prev => ({
          ...prev,
          workflowData: result.workflow,
          generatedWorkflowUuid: result.workflow?.workflow_id,
          isEnabled: !!(prev.sopText || selected.SOP) && !!result.workflow
        }));
        
        toast.success("Workflow generated successfully!", {
          description: "Your workflow is ready for review and optimization"
        });
      } else {
        setErrorState(result.error || "Workflow generation failed", 'sop_to_workflow');
      }
    } catch (error: any) {
      setErrorState(error.message || "Failed to generate workflow", 'sop_to_workflow');
    } finally {
      setLoadingState(false);
    }
  };

  // Handle SOP generation from workflow
  const handleGenerateSopFromWorkflow = async () => {
    if (!selected.workflow) {
      setErrorState("Please select a workflow file");
      return;
    }

    setLoadingState(true, 'workflow_to_sop', 'Generating SOP from workflow...');

    try {
      const result = await journeyAPIManager.generateSOP(selected.workflow.uuid);

      if (result.success && result.sop) {
        setSuccess("SOP generated successfully!");
        
        // Update journey state with generated SOP
        const sopText = result.sop.content || "";
        setJourneyState(prev => ({
          ...prev,
          sopText: sopText,
          workflowData: selected.workflow || prev.workflowData
        }));
        
        // Update coexistence state
        setCoexistenceState(prev => ({
          ...prev,
          sopText,
          generatedSopUuid: result.sop?.sop_id,
          isEnabled: !!sopText && !!(prev.workflowData || selected.workflow)
        }));
        
        toast.success("SOP generated successfully!", {
          description: "Your SOP is ready for review and implementation"
        });
      } else {
        setErrorState(result.error || "SOP generation failed", 'workflow_to_sop');
      }
    } catch (error: any) {
      setErrorState(error.message || "Failed to generate SOP", 'workflow_to_sop');
    } finally {
      setLoadingState(false);
    }
  };

  // Reset journey
  const resetJourney = () => {
    setJourney(null);
    setSelected({ SOP: null, workflow: null });
    // Don't clear operations state - keep panels visible with existing data
  };

  // Handle selection change
  const handleSelectionChange = (type: string, file: FileMetadata | null) => {
    setSelected(prev => ({
      ...prev,
      [type]: file
    }));
  };

  // Render current view
  const renderCurrentView = () => {
    if (journey === 'wizard') {
      return (
        <WizardActive onBack={resetJourney} />
      );
    }

    if (journey === 'select') {
      return (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-gray-800">Select Files</h2>
              <p className="text-gray-600 mt-1">
                Choose SOP and workflow files for journey
              </p>
            </div>
            {/* ✅ PHASE 1.2: Show which Liaison Agent is available */}
            <div className="flex items-center gap-2 px-4 py-2 bg-blue-50 border border-blue-200 rounded-lg">
              <span className="text-xs font-semibold text-blue-900">Available:</span>
              <span className="text-xs text-blue-700">Journey Liaison Agent</span>
              <span className="flex h-2 w-2 rounded-full bg-blue-500" title="Liaison agent available" />
            </div>
            <button
              onClick={resetJourney}
              className="text-gray-500 hover:text-gray-700"
            >
              Back to Journey Choice
            </button>
          </div>

          <FileSelector
            files={journeyFiles}
            selected={selected}
            onSelectionChange={handleSelectionChange}
            fileTypes={JOURNEY_FILE_TYPES}
            isLoading={isLoadingFiles}
          />

          {(selected.SOP || selected.workflow) && (
            <div className="flex space-x-4">
              {selected.SOP && selected.workflow && (
                <button
                  onClick={handleAnalyze}
                  disabled={loading.isLoading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  Analyze Coexistence
                </button>
              )}
              {selected.SOP && (
                <button
                  onClick={handleGenerateWorkflowFromSop}
                  disabled={loading.isLoading}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                >
                  Generate Workflow from SOP
                </button>
              )}
              {selected.workflow && (
                <button
                  onClick={handleGenerateSopFromWorkflow}
                  disabled={loading.isLoading}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
                >
                  Generate SOP from Workflow
                </button>
              )}
            </div>
          )}
        </div>
      );
    }

    // Default journey choice view
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">Journey</h1>
            <p className="text-gray-600 mt-2">
              Manage workflows, SOPs, and process optimization
            </p>
          </div>
          {/* ✅ PHASE 1.2: Show which Liaison Agent is available */}
          <div className="flex items-center gap-2 px-4 py-2 bg-blue-50 border border-blue-200 rounded-lg">
            <span className="text-xs font-semibold text-blue-900">Available:</span>
            <span className="text-xs text-blue-700">Journey Liaison Agent</span>
            <span className="flex h-2 w-2 rounded-full bg-blue-500" title="Liaison agent available" />
          </div>
        </div>

        <JourneyChoice
          onSelectExisting={() => setJourney('select')}
          onStartWizard={() => setJourney('wizard')}
        />

        {/* Display results when available */}
        {success && (
          <div className="space-y-6">
            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <h3 className="font-medium text-green-900">Operation Completed</h3>
              <p className="text-green-800">{success}</p>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="container mx-auto px-4 py-8 space-y-6">
      {/* Loading and Error States */}
      <StateHandler
        loading={loading}
        error={error}
        success={success}
        onDismissError={clearError}
        onRetry={() => {}}
      />

      {/* Main Content */}
      {renderCurrentView()}

      {/* ProcessBlueprint Panel - Always Visible */}
      <div className="mt-8">
        <ProcessBlueprint
          operationsState={journeyState}
          onGenerateWorkflowFromSop={handleGenerateWorkflowFromSop}
          onGenerateSopFromWorkflow={handleGenerateSopFromWorkflow}
          isLoading={loading.isLoading}
        />
      </div>

      {/* ✅ PHASE 3.2: Enhanced Coexistence Analysis - More Prominent */}
      <div className="mt-8">
        {/* Coexistence Explanation Section */}
        {(!selected.SOP || !selected.workflow) && (
          <Card className="mb-6 border-2 border-blue-200 bg-blue-50/30">
            <CardHeader>
              <CardTitle className="text-xl">Coexistence Analysis</CardTitle>
              <CardDescription>
                Understand how your SOPs and workflows coexist and identify opportunities for alignment
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-white border border-gray-200 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-800 mb-2">SOP (Standard Operating Procedure)</h4>
                    <p className="text-sm text-gray-600">
                      Defines how work <em>should</em> be done according to policies and procedures.
                    </p>
                  </div>
                  <div className="bg-white border border-gray-200 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-800 mb-2">Workflow</h4>
                    <p className="text-sm text-gray-600">
                      Defines how work <em>is</em> done in practice, including actual processes and tools.
                    </p>
                  </div>
                </div>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-semibold text-blue-900 mb-2">How They Coexist</h4>
                  <p className="text-sm text-blue-800">
                    The platform analyzes the relationship between SOPs and workflows, identifying gaps, overlaps,
                    and opportunities for alignment. This helps bridge the gap between policy (SOP) and practice (workflow).
                  </p>
                </div>
                <div className="text-center text-sm text-gray-600">
                  <p>Select both an SOP file and a workflow file to begin coexistence analysis</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Coexistence Analysis Results - Enhanced Display */}
        {(selected.SOP && selected.workflow) && (
          <Card className="mb-6 border-2 border-green-200 bg-green-50/30">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-xl">Coexistence Analysis Ready</CardTitle>
                  <CardDescription>
                    SOP and workflow selected. Click "Analyze Coexistence" to generate the coexistence blueprint.
                  </CardDescription>
                </div>
                <div className="flex gap-2">
                  <Badge variant="outline" className="bg-white">SOP: {selected.SOP.name}</Badge>
                  <Badge variant="outline" className="bg-white">Workflow: {selected.workflow.name}</Badge>
                </div>
              </div>
            </CardHeader>
          </Card>
        )}

        <CoexistenceBlueprint
          sopText={coexistenceState.sopText}
          workflowData={coexistenceState.workflowData}
          generatedSopUuid={coexistenceState.generatedSopUuid}
          generatedWorkflowUuid={coexistenceState.generatedWorkflowUuid}
          selectedSopFileUuid={selected.SOP?.uuid || null}
          selectedWorkflowFileUuid={selected.workflow?.uuid || null}
          sessionToken={sessionState.sessionId || ""}
          sessionState={coexistenceState}
          isEnabled={coexistenceState.isEnabled || !!(selected.SOP && selected.workflow)}
        />
      </div>

      {/* Completion Message */}
      <PillarCompletionMessage
        show={
          !!journeyState.workflowData || 
          !!journeyState.sopText || 
          !!coexistenceState.blueprint ||
          (coexistenceState.isEnabled && !!(selected.SOP && selected.workflow))
        }
        message="Congratulations! You've explored your coexistence future. You can return to the Content pillar to upload additional data, or the Insights pillar if you want to keep exploring, but if you're ready to proceed then our Business Outcomes pillar will summarize what we've accomplished and provide you with our recommendations."
      />
    </div>
  );
}
