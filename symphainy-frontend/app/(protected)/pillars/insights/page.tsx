"use client";
/**
 * Insights Pillar Page
 * 
 * Tabbed interface with four main sections:
 * 1. Data Quality - Quality assessment with semantic embeddings
 * 2. Data Interpretation - Self-discovery and guided discovery
 * 3. Your Data Mash - Lineage visualization
 * 4. Business Analysis - Structured and unstructured data analysis
 */

import React, { useEffect, useState } from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useSetAtom } from "jotai";
import { chatbotAgentInfoAtom, mainChatbotOpenAtom } from "@/shared/atoms/chatbot-atoms";
import { SecondaryChatbotAgent, SecondaryChatbotTitle } from "@/shared/types/secondaryChatbot";
import { DataQualitySection } from "./components/DataQualitySection";
import { DataInterpretationSection } from "./components/DataInterpretationSection";
import { YourDataMash } from "./components/YourDataMash";
import { BusinessAnalysisSection } from "./components/BusinessAnalysisSection";
import { QualityAssessmentResponse, InterpretationResponse, AnalysisResponse, LineageVisualizationResponse } from "@/shared/managers/InsightsAPIManager";
import { PillarCompletionMessage } from "../shared/components/PillarCompletionMessage";

export default function InsightsPage() {
  const setAgentInfo = useSetAtom(chatbotAgentInfoAtom);
  const setMainChatbotOpen = useSetAtom(mainChatbotOpenAtom);
  
  // State for current analysis (to provide context to agent)
  const [currentAnalysisId, setCurrentAnalysisId] = useState<string | null>(null);
  const [dataQualityReport, setDataQualityReport] = useState<QualityAssessmentResponse | null>(null);
  const [dataInterpretation, setDataInterpretation] = useState<InterpretationResponse | null>(null);
  const [lineageVisualization, setLineageVisualization] = useState<LineageVisualizationResponse | null>(null);
  const [businessAnalysis, setBusinessAnalysis] = useState<AnalysisResponse | null>(null);

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
          has_data_interpretation: !!dataInterpretation,
          has_lineage_visualization: !!lineageVisualization,
          has_business_analysis: !!businessAnalysis,
          context: "insights_pillar"
        })
    });
    // Keep main chatbot open by default - GuideAgent will be shown
    setMainChatbotOpen(true);
  }, [currentAnalysisId, dataQualityReport, dataInterpretation, lineageVisualization, businessAnalysis, setAgentInfo, setMainChatbotOpen]);

  // Handler for data quality evaluation completion
  const handleQualityEvaluationComplete = (qualityReport: QualityAssessmentResponse) => {
    setDataQualityReport(qualityReport);
    if (qualityReport.parsed_file_id) {
      setCurrentAnalysisId(qualityReport.parsed_file_id);
    }
  };

  // Handler for data interpretation completion
  const handleInterpretationComplete = (interpretation: InterpretationResponse) => {
    setDataInterpretation(interpretation);
    if (interpretation.parsed_file_id) {
      setCurrentAnalysisId(interpretation.parsed_file_id);
    }
  };

  // Handler for lineage visualization completion
  const handleVisualizationComplete = (visualization: LineageVisualizationResponse) => {
    setLineageVisualization(visualization);
    if (visualization.file_id) {
      setCurrentAnalysisId(visualization.file_id);
    }
  };

  // Handler for business analysis completion
  const handleBusinessAnalysisComplete = (analysis: AnalysisResponse) => {
    setBusinessAnalysis(analysis);
    if (analysis.parsed_file_id) {
      setCurrentAnalysisId(analysis.parsed_file_id);
    }
  };

  // Detect completion: user has completed at least one analysis
  const isComplete = dataQualityReport !== null || dataInterpretation !== null || lineageVisualization !== null || businessAnalysis !== null;

  return (
    <div className="flex-grow space-y-6">
      {/* Header */}
      <div className="space-y-3">
        <h2 className="text-h2 font-bold text-gray-800">Insights Pillar</h2>
        <p className="text-lead text-gray-600">
          Transform your data into actionable insights with AI-powered analysis.
          Assess quality, interpret meaning, visualize lineage, and generate business insights.
        </p>
      </div>

      {/* Tabbed Interface */}
      <Tabs defaultValue="data-quality" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="data-quality">Data Quality</TabsTrigger>
          <TabsTrigger value="data-interpretation">Data Interpretation</TabsTrigger>
          <TabsTrigger value="your-data-mash">Your Data Mash</TabsTrigger>
          <TabsTrigger value="business-analysis">Business Analysis</TabsTrigger>
        </TabsList>

        {/* Data Quality Tab */}
        <TabsContent value="data-quality">
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
        </TabsContent>

        {/* Data Interpretation Tab */}
        <TabsContent value="data-interpretation">
          <Card>
            <CardHeader>
              <CardTitle>Data Interpretation</CardTitle>
              <CardDescription>
                Discover entities and relationships in your data through self-discovery or guided interpretation. 
                Self-discovery automatically finds patterns, while guided discovery uses schemas or templates for structured matching.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <DataInterpretationSection 
                onInterpretationComplete={handleInterpretationComplete}
              />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Your Data Mash Tab */}
        <TabsContent value="your-data-mash">
          <Card>
            <CardHeader>
              <CardTitle>Your Data Mash</CardTitle>
              <CardDescription>
                Visualize the complete data lineage pipeline from file upload to final analysis. 
                See how your data flows through parsing, embedding, interpretation, and analysis stages.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <YourDataMash 
                onVisualizationComplete={handleVisualizationComplete}
              />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Business Analysis Tab */}
        <TabsContent value="business-analysis">
          <Card>
            <CardHeader>
              <CardTitle>Business Analysis</CardTitle>
              <CardDescription>
                Generate actionable business insights from structured data (tables, metrics) or unstructured data 
                (documents, reports). Get visual charts, statistical summaries, and business narratives.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <BusinessAnalysisSection 
                onAnalysisComplete={handleBusinessAnalysisComplete}
              />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Completion Message */}
      <PillarCompletionMessage
        show={isComplete}
        message="Congratulations! Hopefully those insights have provided a new perspective on your business. You can return to the Content pillar to upload additional data, or proceed to the Journey pillar to put those insights into action, or you can proceed directly to our Business Outcomes page to see how we would recommend applying those insights."
      />
    </div>
  );
}

