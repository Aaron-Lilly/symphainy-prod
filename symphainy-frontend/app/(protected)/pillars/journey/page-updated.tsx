"use client";
import React, { useState, useEffect } from "react";
import { useAuth } from "@/shared/auth/AuthProvider";
import { usePlatformState } from "@/shared/state/PlatformStateProvider";
import { useWebSocket } from "@/shared/agui/WebSocketProvider";
import { OperationsService } from "@/shared/services/operations";
import { useSessionElements } from "@/shared/hooks/useSessionElements";
import { FileMetadata, FileType, FileStatus } from "@/shared/types/file";
import { LoadingState, OperationsError } from "@/shared/types/operations";
import { chatbotAgentInfoAtom, mainChatbotOpenAtom } from "@/shared/atoms/chatbot-atoms";
import { useSetAtom } from "jotai";
import { usePathname } from "next/navigation";
import { StateHandler, LoadingIndicator, ErrorDisplay, SuccessDisplay } from "@/components/ui/loading-error-states";
import { SecondaryChatbotAgent, SecondaryChatbotTitle } from "@/shared/types/secondaryChatbot";

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

// File types that are relevant for operations
const OPERATION_FILE_TYPES = [FileType.Document, FileType.Pdf, FileType.Text, FileType.SopWorkflow];

export default function OperationsPillarUpdated() {
  const setAgentInfo = useSetAtom(chatbotAgentInfoAtom);
  const setMainChatbotOpen = useSetAtom(mainChatbotOpenAtom);

  const { sessionToken } = useAuth();
  const { state, getRealmState, setRealmState } = usePlatformState();
  const guideSessionToken = sessionToken || state.session.sessionId;
  
  // Compatibility wrappers for old API
  const getPillarState = (pillar: string) => getRealmState('journey', pillar);
  const setPillarState = (pillar: string, value: any) => setRealmState('journey', pillar, value);

  const pathname = usePathname();

  const { connect, isConnected } = useWebSocket();

  // Session state management
  const {
    sessionState,
    sessionElements,
    isValid: sessionValid,
    action: sessionAction,
    missing: sessionMissing,
    isLoading: sessionLoading,
    error: sessionError,
    refreshSession,
    clearSession,
  } = useSessionElements(guideSessionToken);

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
  const [initialized, setInitialized] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [conversationHistory, setConversationHistory] = useState<any[]>([]);

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

  // Get files from global session state - check all pillar states for files
  useEffect(() => {
    const getAllFiles = () => {
      setIsLoadingFiles(true);
      try {
        const contentState = getPillarState('content');
        const insightsState = getPillarState('insights');
        const operationsState = getPillarState('operations');
        const businessOutcomesState = getPillarState('business-outcomes');

        const allFiles: FileMetadata[] = [];
        
        // Collect files from all pillars
        [contentState, insightsState, operationsState, businessOutcomesState].forEach(state => {
          if (state?.files) {
            allFiles.push(...state.files);
          }
        });

        // Filter for operations-relevant files
        const operationsFiles = allFiles.filter(file => 
          OPERATION_FILE_TYPES.includes(file.file_type as FileType) ||
          file.ui_name.toLowerCase().includes('sop') ||
          file.ui_name.toLowerCase().includes('workflow') ||
          file.ui_name.toLowerCase().includes('process')
        );

        setOperationFiles(operationsFiles);
        setInitialized(true);
      } catch (error) {
        console.error('Error loading files:', error);
        setErrorState('Failed to load files');
      } finally {
        setIsLoadingFiles(false);
      }
    };

    if (guideSessionToken) {
      getAllFiles();
    }
  }, [guideSessionToken, getPillarState]);

  // Initialize conversation
  useEffect(() => {
    if (!conversationId) {
      setConversationId(`ops-conversation-${Date.now()}`);
    }
  }, [conversationId]);

  // Handle coexistence analysis with new API
  const handleCoexistenceAnalysis = async () => {
    if (!selected.SOP && !selected.workflow) {
      setErrorState("Please select at least one SOP or workflow file");
      return;
    }

    setLoadingState(true, 'coexistence_analysis', 'Analyzing coexistence opportunities...');

    try {
      // Use the new CoexistenceEvaluator bypass endpoint
      const userRequirements = {
        involves_documents: true,
        data_heavy: true,
        needs_analysis: true,
        involves_processes: true,
        process_heavy: true,
        strategic_focus: true,
        outcome_driven: true,
        description: "Analyze AI-human coexistence opportunities for the selected process",
        sop_data: selected.SOP,
        workflow_data: selected.workflow
      };

      const response = await OperationsService.createCoexistenceBlueprintDirectly(
        userRequirements,
        conversationId || `ops-conversation-${Date.now()}`,
        guideSessionToken
      );

      if (response.status === 'success') {
        setSuccess("Coexistence analysis completed successfully!");
        
        // Save to global session
        setPillarState('operations', {
          coexistence_blueprint: response.blueprint,
          platform_recommendations: response.deliverable,
          analysisComplete: true,
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

  // Handle workflow generation from SOP using new API
  const handleGenerateWorkflowFromSop = async () => {
    if (!selected.SOP) {
      setErrorState("Please select an SOP file");
      return;
    }

    setLoadingState(true, 'sop_to_workflow', 'Generating workflow from SOP...');

    try {
      // Use the new real conversion endpoint
      const response = await OperationsService.convertSopToWorkflowReal(
        selected.SOP,
        guideSessionToken
      );

      if (response.status === 'success') {
        setSuccess("Workflow generated successfully!");
        
        // Save to global session
        setPillarState('operations', {
          workflowData: response.workflow,
          sopData: selected.SOP,
          workflowGenerated: true,
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

  // Handle SOP generation from workflow using new API
  const handleGenerateSopFromWorkflow = async () => {
    if (!selected.workflow) {
      setErrorState("Please select a workflow file");
      return;
    }

    setLoadingState(true, 'workflow_to_sop', 'Generating SOP from workflow...');

    try {
      // Use the new real conversion endpoint
      const response = await OperationsService.convertWorkflowToSopReal(
        selected.workflow,
        guideSessionToken
      );

      if (response.status === 'success') {
        setSuccess("SOP generated successfully!");
        
        // Save to global session
        setPillarState('operations', {
          sopData: response.sop,
          workflowData: selected.workflow,
          sopGenerated: true,
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

  // Handle DOCX file upload and extraction
  const handleDocxUpload = async (file: File) => {
    setLoadingState(true, 'sop_to_workflow', 'Extracting SOP from DOCX...');

    try {
      const response = await OperationsService.extractSopFromDocx(file, guideSessionToken);

      if (response.status === 'success') {
        setSuccess("SOP extracted from DOCX successfully!");
        
        // Save extracted SOP data
        setPillarState('operations', {
          extractedSop: response.sop,
          docxFile: file.name,
          extractionComplete: true,
        });
      } else {
        setErrorState(response.message || "DOCX extraction failed", 'sop_to_workflow');
      }
    } catch (error: any) {
      setErrorState(error.message || "Failed to extract SOP from DOCX", 'sop_to_workflow');
    } finally {
      setLoadingState(false);
    }
  };

  // Handle operations conversation
  const handleOperationsConversation = async (message: string) => {
    if (!conversationId) {
      setConversationId(`ops-conversation-${Date.now()}`);
    }

    try {
      const response = await OperationsService.processOperationsConversation(
        message,
        conversationId!,
        guideSessionToken
      );

      if (response.status === 'success') {
        // Add to conversation history
        setConversationHistory(prev => [
          ...prev,
          { type: 'user', message },
          { type: 'assistant', message: response.message || 'Response received' }
        ]);
      } else {
        setErrorState(response.message || "Conversation failed");
      }
    } catch (error: any) {
      setErrorState(error.message || "Failed to process conversation");
    }
  };

  // Handle wizard start
  const handleStartWizard = async () => {
    setJourney('wizard');
  };

  // Reset journey
  const resetJourney = () => {
    setJourney(null);
    setSelected({ SOP: null, workflow: null });
  };

  // Handle selection change
  const handleSelectionChange = (type: string, file: FileMetadata | null) => {
    setSelected(prev => ({
      ...prev,
      [type]: file
    }));
  };

  // Check if we can proceed with analysis
  const canAnalyze = selected.SOP || selected.workflow;
  const canGenerateWorkflow = selected.SOP;
  const canGenerateSop = selected.workflow;

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold">Operations Pillar</h1>
        <p className="text-muted-foreground">
          Transform your processes with AI-human collaboration
        </p>
      </div>

      {/* Health Status */}
      <Card>
        <CardHeader>
          <CardTitle>Service Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-sm">Operations Pillar Online</span>
          </div>
        </CardContent>
      </Card>

      {/* Journey Selection */}
      {!journey && (
        <JourneyChoice
          onStartWizard={handleStartWizard}
          onSelectExisting={() => setJourney('select')}
        />
      )}

      {/* File Selection Journey */}
      {journey === 'select' && (
        <div className="space-y-6">
          <div className="text-center">
            <h2 className="text-2xl font-semibold mb-2">Select Your Process Files</h2>
            <p className="text-muted-foreground">
              Choose SOP or workflow files to analyze and optimize
            </p>
          </div>

          <FileSelector
            files={operationFiles}
            selected={selected}
            onSelectionChange={handleSelectionChange}
            isLoading={isLoadingFiles}
          />

          {/* Action Buttons */}
          <div className="flex flex-wrap gap-4 justify-center">
            {canGenerateWorkflow && (
              <button
                onClick={handleGenerateWorkflowFromSop}
                disabled={loading.isLoading}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {loading.isLoading && loading.operation === 'sop_to_workflow' ? (
                  <LoadingIndicator state={loading} />
                ) : (
                  'Convert SOP to Workflow'
                )}
              </button>
            )}

            {canGenerateSop && (
              <button
                onClick={handleGenerateSopFromWorkflow}
                disabled={loading.isLoading}
                className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
              >
                {loading.isLoading && loading.operation === 'workflow_to_sop' ? (
                  <LoadingIndicator state={loading} />
                ) : (
                  'Convert Workflow to SOP'
                )}
              </button>
            )}

            {canAnalyze && (
              <button
                onClick={handleCoexistenceAnalysis}
                disabled={loading.isLoading}
                className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
              >
                {loading.isLoading && loading.operation === 'coexistence_analysis' ? (
                  <LoadingIndicator state={loading} />
                ) : (
                  'Analyze AI-Human Coexistence'
                )}
              </button>
            )}
          </div>

          <div className="text-center">
            <button
              onClick={resetJourney}
              className="px-4 py-2 text-gray-600 hover:text-gray-800"
            >
              ← Back to Journey Selection
            </button>
          </div>
        </div>
      )}

      {/* Wizard Journey */}
      {journey === 'wizard' && (
        <WizardActive
          onBack={() => setJourney(null)}
        />
      )}

      {/* Process Blueprint Display */}
      {getPillarState('operations')?.workflowData && (
        <ProcessBlueprint
          operationsState={getPillarState('operations')}
        />
      )}

      {/* Coexistence Blueprint Display */}
      {getPillarState('operations')?.coexistence_blueprint && (
        <CoexistenceBlueprint
          sopText={getPillarState('operations').sopData}
          workflowData={getPillarState('operations').workflowData}
        />
      )}

      {/* Error Display */}
      {error && (
        <ErrorDisplay
          error={error}
          onRetry={() => {
            clearError();
            // Retry logic based on error type
          }}
          onDismiss={clearError}
        />
      )}

      {/* Success Display */}
      {success && (
        <SuccessDisplay
          message={success}
          onDismiss={clearSuccess}
        />
      )}

      {/* Conversation History */}
      {conversationHistory.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Operations Assistant</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4 max-h-64 overflow-y-auto">
              {conversationHistory.map((msg, index) => (
                <div
                  key={index}
                  className={`p-3 rounded-lg ${
                    msg.type === 'user'
                      ? 'bg-blue-100 ml-8'
                      : 'bg-gray-100 mr-8'
                  }`}
                >
                  <div className="font-medium text-sm mb-1">
                    {msg.type === 'user' ? 'You' : 'Operations Assistant'}
                  </div>
                  <div className="text-sm">{msg.message}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}



