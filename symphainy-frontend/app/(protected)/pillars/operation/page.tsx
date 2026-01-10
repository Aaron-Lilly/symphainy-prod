"use client";
import React, { useState, useEffect } from "react";

// Force dynamic rendering to avoid SSR issues
export const dynamic = 'force-dynamic';
import { useAuth } from "@/shared/agui/AuthProvider";
import { useOperationsOrchestrator } from "@/shared/hooks/usePillarOrchestrator";
import { useGlobalSession } from "@/shared/agui/GlobalSessionProvider";
import { chatbotAgentInfoAtom, mainChatbotOpenAtom } from "@/shared/atoms/chatbot-atoms";
import { useSetAtom } from "jotai";
import { usePathname } from "next/navigation";
import { StateHandler, LoadingIndicator, ErrorDisplay, SuccessDisplay } from "@/components/ui/loading-error-states";
import { toast } from "sonner";
import { FileType, FileMetadata } from "@/shared/types/file";
import { LoadingState, OperationsError } from "@/shared/types/operations";

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

// File types that are relevant for operations
const OPERATION_FILE_TYPES = [FileType.Document, FileType.Pdf, FileType.Text, FileType.SopWorkflow];

export default function OperationsPillar() {
  const setAgentInfo = useSetAtom(chatbotAgentInfoAtom);
  const setMainChatbotOpen = useSetAtom(mainChatbotOpenAtom);
  const { isAuthenticated, user } = useAuth();
  const { guideSessionToken } = useGlobalSession();
  const { 
    orchestrator, 
    isInitialized: orchestratorInitialized, 
    isLoading: orchestratorLoading, 
    error: orchestratorError,
    executeOperation,
    getPillarData
  } = useOperationsOrchestrator(guideSessionToken || "");

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
  const [operationFiles, setOperationFiles] = useState<FileMetadata[]>([]);
  const [isLoadingFiles, setIsLoadingFiles] = useState(false);

  // Operations orchestrator handles all service layer initialization
  const [initialized, setInitialized] = useState(false);

  // State for ProcessBlueprint and CoexistenceBlueprint
  const [operationsState, setOperationsState] = useState<{
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

  // Get files from Experience Layer Client
  useEffect(() => {
  const getAllFiles = async () => {
    if (!isAuthenticated || !orchestratorInitialized) return;
    
    setIsLoadingFiles(true);
    try {
      const pillarData = await getPillarData();
      
      if (pillarData.elements) {
        // Filter for operation-relevant files from elements
        const operationFiles = Object.values(pillarData.elements).filter((file: any) => 
          file && OPERATION_FILE_TYPES.includes(file.file_type)
        );
        
        setOperationFiles(operationFiles as FileMetadata[]);
      }
    } catch (error) {
      console.error("Error getting files:", error);
      toast.error("Failed to load files", {
        description: "Unable to retrieve files for operations"
      });
    } finally {
      setIsLoadingFiles(false);
    }
  };

    if (!initialized && isAuthenticated) {
      getAllFiles();
      setInitialized(true);
    }
  }, [isAuthenticated, initialized, guideSessionToken, orchestratorInitialized]);


  // Set up operations liaison agent
  useEffect(() => {
    setAgentInfo({
      title: "Operations Liaison",
      agent: "operations",
      file_url: "",
      additional_info: "Your AI assistant for operations and workflow management",
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
      const response = await executeOperation('analyzeCoexistence', {
        sopFileUuid: selected.SOP.uuid,
        workflowFileUuid: selected.workflow.uuid
      });

      if (response.status === 'success') {
        setSuccess("Coexistence analysis completed successfully!");
        
        // Update coexistence state with blueprint
        const blueprint = response.data?.blueprint || response.blueprint || {};
        const optimizedSop = response.data?.optimized_sop || response.optimized_sop;
        const optimizedWorkflow = response.data?.optimized_workflow || response.optimized_workflow;
        
        setCoexistenceState(prev => ({
          ...prev,
          blueprint,
          sopText: optimizedSop || prev.sopText,
          workflowData: optimizedWorkflow || prev.workflowData,
          isEnabled: true
        }));
        
        // Update operations state with optimized results
        if (optimizedSop || optimizedWorkflow) {
          setOperationsState(prev => ({
            ...prev,
            optimizedSop,
            optimizedWorkflow,
            analysisResults: {
              analysisType: 'coexistence',
              errors: response.data?.errors || []
            }
          }));
        }
        
        toast.success("Coexistence analysis completed!", {
          description: "Analysis results are ready for review"
        });
      } else {
        setErrorState(response.message || "Analysis failed", 'coexistence_analysis');
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
      const response = await executeOperation('generateWorkflow', {
        sopFileUuid: selected.SOP.uuid
      });

      if (response.status === 'success') {
        setSuccess("Workflow generated successfully!");
        
        // Update operations state with generated workflow
        const workflowData = response.data?.workflow || response.workflow || {};
        setOperationsState(prev => ({
          ...prev,
          workflowData,
          sopText: selected.SOP?.ui_name || prev.sopText
        }));
        
        // Update coexistence state
        setCoexistenceState(prev => ({
          ...prev,
          workflowData,
          generatedWorkflowUuid: response.data?.workflow_uuid || response.workflow_uuid,
          isEnabled: !!(prev.sopText || selected.SOP) && !!workflowData
        }));
        
        toast.success("Workflow generated successfully!", {
          description: "Your workflow is ready for review and optimization"
        });
      } else {
        setErrorState(response.message || "Workflow generation failed", 'sop_to_workflow');
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
      const response = await executeOperation('generateSOP', {
        workflowFileUuid: selected.workflow.uuid
      });

      if (response.status === 'success') {
        setSuccess("SOP generated successfully!");
        
        // Update operations state with generated SOP
        const sopText = response.data?.sop || response.sop || "";
        setOperationsState(prev => ({
          ...prev,
          sopText: sopText,
          workflowData: selected.workflow || prev.workflowData
        }));
        
        // Update coexistence state
        setCoexistenceState(prev => ({
          ...prev,
          sopText,
          generatedSopUuid: response.data?.sop_uuid || response.sop_uuid,
          isEnabled: !!sopText && !!(prev.workflowData || selected.workflow)
        }));
        
        toast.success("SOP generated successfully!", {
          description: "Your SOP is ready for review and implementation"
        });
      } else {
        setErrorState(response.message || "SOP generation failed", 'workflow_to_sop');
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
                Choose SOP and workflow files for operations
              </p>
            </div>
            <button
              onClick={resetJourney}
              className="text-gray-500 hover:text-gray-700"
            >
              Back to Journey Choice
            </button>
          </div>

          <FileSelector
            files={operationFiles}
            selected={selected}
            onSelectionChange={handleSelectionChange}
            fileTypes={OPERATION_FILE_TYPES}
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
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Operations</h1>
          <p className="text-gray-600 mt-2">
            Manage workflows, SOPs, and process optimization
          </p>
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
          operationsState={operationsState}
          onGenerateWorkflowFromSop={handleGenerateWorkflowFromSop}
          onGenerateSopFromWorkflow={handleGenerateSopFromWorkflow}
          isLoading={loading.isLoading}
        />
      </div>

      {/* CoexistenceBlueprint Panel - Always Visible */}
      <div className="mt-8">
        <CoexistenceBlueprint
          sopText={coexistenceState.sopText}
          workflowData={coexistenceState.workflowData}
          generatedSopUuid={coexistenceState.generatedSopUuid}
          generatedWorkflowUuid={coexistenceState.generatedWorkflowUuid}
          selectedSopFileUuid={selected.SOP?.uuid || null}
          selectedWorkflowFileUuid={selected.workflow?.uuid || null}
          sessionToken={guideSessionToken}
          sessionState={coexistenceState}
          isEnabled={coexistenceState.isEnabled || !!(selected.SOP && selected.workflow)}
        />
      </div>

      {/* Completion Message */}
      <PillarCompletionMessage
        show={
          !!operationsState.workflowData || 
          !!operationsState.sopText || 
          !!coexistenceState.blueprint ||
          (coexistenceState.isEnabled && !!(selected.SOP && selected.workflow))
        }
        message="Congratulations! You've explored your coexistence future. You can return to the Content pillar to upload additional data, or the Insights pillar if you want to keep exploring, but if you're ready to proceed then our Business Outcomes pillar will summarize what we've accomplished and provide you with our recommendations."
      />
    </div>
  );
}
