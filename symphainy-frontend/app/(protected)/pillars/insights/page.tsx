"use client";
/**
 * Unified Insights Pillar Page
 * 
 * Two-section layout for Structured and Unstructured data insights
 * Replaces the old VARK/APG toggle pages with a cleaner unified interface
 */

import React, { useEffect, useState } from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { useSetAtom } from "jotai";
import { chatbotAgentInfoAtom, mainChatbotOpenAtom } from "@/shared/atoms/chatbot-atoms";
import { SecondaryChatbotAgent, SecondaryChatbotTitle } from "@/shared/types/secondaryChatbot";
import { DataQualitySection } from "./components/DataQualitySection";
import { StructuredDataInsightsSection } from "./components/StructuredDataInsightsSection";
import { UnstructuredDataInsightsSection } from "./components/UnstructuredDataInsightsSection";
import { DataMappingSection } from "./components/DataMappingSection";
import { PermitProcessingSection } from "./components/PermitProcessingSection";
import { AnalyzeContentResponse, DataQualityResponse } from "@/lib/api/insights";
import { DataMappingResultsResponse, PermitProcessingResponse } from "@/shared/services/insights/types";
import { PillarCompletionMessage } from "../shared/components/PillarCompletionMessage";

export default function InsightsPage() {
  const setAgentInfo = useSetAtom(chatbotAgentInfoAtom);
  const setMainChatbotOpen = useSetAtom(mainChatbotOpenAtom);
  
  // State for current analysis (to provide context to agent)
  const [currentAnalysisId, setCurrentAnalysisId] = useState<string | null>(null);
  const [dataQualityReport, setDataQualityReport] = useState<DataQualityResponse | null>(null);
  const [structuredAnalysis, setStructuredAnalysis] = useState<AnalyzeContentResponse | null>(null);
  const [unstructuredAnalysis, setUnstructuredAnalysis] = useState<AnalyzeContentResponse | null>(null);
  const [dataMapping, setDataMapping] = useState<DataMappingResultsResponse | null>(null);
  const [permitProcessing, setPermitProcessing] = useState<PermitProcessingResponse | null>(null);

  // Configure Insights Liaison Agent for side panel (not inline)
  useEffect(() => {
    // Configure the secondary agent but don't show it by default
    setAgentInfo({
      agent: SecondaryChatbotAgent.INSIGHTS_LIAISON,
      title: SecondaryChatbotTitle.INSIGHTS_LIAISON,
      file_url: "",
        additional_info: JSON.stringify({
          current_analysis_id: currentAnalysisId,
          has_data_quality_report: !!dataQualityReport,
          has_structured_analysis: !!structuredAnalysis,
          has_unstructured_analysis: !!unstructuredAnalysis,
          has_data_mapping: !!dataMapping,
          has_permit_processing: !!permitProcessing,
          context: "insights_pillar"
        })
    });
    // Keep main chatbot open by default - GuideAgent will be shown
    setMainChatbotOpen(true);
  }, [currentAnalysisId, dataQualityReport, structuredAnalysis, unstructuredAnalysis, dataMapping, permitProcessing, setAgentInfo, setMainChatbotOpen]);

  // Handler for data quality evaluation completion
  const handleQualityEvaluationComplete = (qualityReport: DataQualityResponse) => {
    setDataQualityReport(qualityReport);
    if (qualityReport.workflow_id) {
      setCurrentAnalysisId(qualityReport.workflow_id);
    }
  };

  // Handler for structured analysis completion
  const handleStructuredAnalysisComplete = (analysis: AnalyzeContentResponse) => {
    setStructuredAnalysis(analysis);
    if (analysis.analysis_id) {
      setCurrentAnalysisId(analysis.analysis_id);
    }
  };

  // Handler for unstructured analysis completion
  const handleUnstructuredAnalysisComplete = (analysis: AnalyzeContentResponse) => {
    setUnstructuredAnalysis(analysis);
    if (analysis.analysis_id) {
      setCurrentAnalysisId(analysis.analysis_id);
    }
  };

  // Handler for data mapping completion
  const handleMappingComplete = (mapping: DataMappingResultsResponse) => {
    setDataMapping(mapping);
    if (mapping.mapping_id) {
      setCurrentAnalysisId(mapping.mapping_id);
    }
  };

  // Handler for permit processing completion
  const handlePermitProcessingComplete = (result: PermitProcessingResponse) => {
    setPermitProcessing(result);
    if (result.workflow_id) {
      setCurrentAnalysisId(result.workflow_id);
    }
  };

  // Detect completion: user has completed at least one analysis
  const isComplete = dataQualityReport !== null || structuredAnalysis !== null || unstructuredAnalysis !== null || dataMapping !== null || permitProcessing !== null;

  return (
    <div className="flex-grow space-y-6">
      {/* Header */}
      <div className="space-y-3">
        <h2 className="text-h2 font-bold text-gray-800">Insights Pillar</h2>
        <p className="text-lead text-gray-600">
          Transform your data into actionable insights with AI-powered analysis.
          Analyze structured data (tables, metrics) or unstructured data (documents, reports).
        </p>
      </div>

      {/* Section 1: Data Quality Evaluation */}
      <Card>
        <CardHeader>
          <CardTitle>Data Quality Evaluation</CardTitle>
          <CardDescription>
            Evaluate the quality of your parsed data files using validation rules (88 codes, level-01 metadata), 
            schema validation, quality metrics, and AI-generated recommendations. Get comprehensive insights into 
            data completeness, accuracy, and issues that need attention.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <DataQualitySection 
            onQualityEvaluationComplete={handleQualityEvaluationComplete}
          />
        </CardContent>
      </Card>

      {/* Section 2: Insights from Structured Data */}
      <Card>
        <CardHeader>
          <CardTitle>Insights from Structured Data</CardTitle>
          <CardDescription>
            Generate insights from structured data such as CSV files, Excel spreadsheets, databases, 
            and tabular formats. Get visual charts, statistical summaries, and business narratives.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <StructuredDataInsightsSection 
            onAnalysisComplete={handleStructuredAnalysisComplete}
          />
        </CardContent>
      </Card>

      {/* Section 3: Insights from Unstructured Data */}
      <Card>
        <CardHeader>
          <CardTitle>Insights from Unstructured Data</CardTitle>
          <CardDescription>
            Generate insights from unstructured content such as text documents, PDFs, reports, 
            and emails. Enable AAR mode for specialized Navy after-action report analysis.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <UnstructuredDataInsightsSection 
            onAnalysisComplete={handleUnstructuredAnalysisComplete}
          />
        </CardContent>
      </Card>

      {/* Section 4: Data Mapping */}
      <Card>
        <CardHeader>
          <CardTitle>Data Mapping</CardTitle>
          <CardDescription>
            Map data from source files to target data models. Supports both unstructured-to-structured 
            (e.g., license PDF to Excel) and structured-to-structured (e.g., legacy policy records to new model) 
            with quality validation and cleanup actions.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <DataMappingSection 
            onMappingComplete={handleMappingComplete}
          />
        </CardContent>
      </Card>

      {/* Section 5: Permit Processing */}
      <Card>
        <CardHeader>
          <CardTitle>Permit Processing</CardTitle>
          <CardDescription>
            Extract Permit Semantic Objects (PSO) from permit documents and map to multiple target systems 
            (compliance, task management, environmental monitoring, ERP). Uses AI to extract structured 
            permit data including obligations, legal citations, and metadata.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <PermitProcessingSection 
            onProcessingComplete={handlePermitProcessingComplete}
          />
        </CardContent>
      </Card>

      {/* Completion Message */}
      <PillarCompletionMessage
        show={isComplete}
        message="Congratulations! Hopefully those insights have provided a new perspective on your business. You can return to the Content pillar to upload additional data, or proceed to the Operations pillar to put those insights into action, or you can proceed directly to our Business Outcomes page to see how we would recommend applying those insights."
      />
    </div>
  );
}

