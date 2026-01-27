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
// ✅ PHASE 5: Use PlatformStateProvider instead of Jotai atoms
import { usePlatformState } from "@/shared/state/PlatformStateProvider";
import { SecondaryChatbotAgent, SecondaryChatbotTitle } from "@/shared/types/secondaryChatbot";
import { DataQualitySection } from "./components/DataQualitySection";
import { DataInterpretationSection } from "./components/DataInterpretationSection";
import { YourDataMash } from "./components/YourDataMash";
import { BusinessAnalysisSection } from "./components/BusinessAnalysisSection";
import { RelationshipMapping } from "./components/RelationshipMapping";
import { QualityAssessmentResponse, InterpretationResponse, AnalysisResponse, LineageVisualizationResponse } from "@/shared/managers/InsightsAPIManager";
import { PillarCompletionMessage } from "../shared/components/PillarCompletionMessage";

export default function InsightsPage() {
  // ✅ PHASE 5: Use PlatformStateProvider instead of Jotai atoms
  const { setChatbotAgentInfo, setMainChatbotOpen } = usePlatformState();
  const setAgentInfo = setChatbotAgentInfo; // Alias for compatibility
  
  // State for current analysis (to provide context to agent)
  const [currentAnalysisId, setCurrentAnalysisId] = useState<string | null>(null);
  const [dataQualityReport, setDataQualityReport] = useState<QualityAssessmentResponse | null>(null);
  const [dataInterpretation, setDataInterpretation] = useState<InterpretationResponse | null>(null);
  const [lineageVisualization, setLineageVisualization] = useState<LineageVisualizationResponse | null>(null);
  const [businessAnalysis, setBusinessAnalysis] = useState<AnalysisResponse | null>(null);

  // ✅ PHASE 1.2: Configure Insights Liaison Agent for side panel
  useEffect(() => {
    // Configure the secondary agent but don't show it by default
    setAgentInfo({
      agent: SecondaryChatbotAgent.INSIGHTS_LIAISON,
      title: SecondaryChatbotTitle.INSIGHTS_LIAISON,
      file_url: "",
      additional_info: "Data quality, interpretation, and business analysis expert. Ask me about data quality assessment, semantic interpretation, lineage visualization, and business insights."
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
  const handleVisualizationComplete = (visualization: LineageVisualizationResponse | any) => {
    // Convert LineageVisualization to LineageVisualizationResponse if needed
    const response: LineageVisualizationResponse = visualization.success !== undefined 
      ? visualization 
      : { success: true, visualization };
    setLineageVisualization(response);
    if (response.file_id || (response.visualization as any)?.file_id) {
      setCurrentAnalysisId(response.file_id || (response.visualization as any)?.file_id);
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
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-h2 font-bold text-gray-800">Insights Pillar</h2>
            <p className="text-lead text-gray-600">
              Transform your data into actionable insights with AI-powered analysis.
              Assess quality, interpret meaning, visualize lineage, and generate business insights.
            </p>
          </div>
          {/* ✅ PHASE 1.2: Show which Liaison Agent is available */}
          <div className="flex items-center gap-2 px-4 py-2 bg-blue-50 border border-blue-200 rounded-lg">
            <span className="text-xs font-semibold text-blue-900">Available:</span>
            <span className="text-xs text-blue-700">Insights Liaison Agent</span>
            <span className="flex h-2 w-2 rounded-full bg-blue-500" title="Liaison agent available" />
          </div>
        </div>
      </div>

      {/* Tabbed Interface */}
      <Tabs defaultValue="data-quality" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="data-quality">Data Quality</TabsTrigger>
          <TabsTrigger value="data-interpretation">Data Interpretation</TabsTrigger>
          {/* ✅ PHASE 4.1: Make "Your Data Mash" more prominent */}
          <TabsTrigger value="your-data-mash" className="relative">
            Your Data Mash
            <span className="ml-2 px-2 py-0.5 text-xs bg-blue-100 text-blue-800 rounded-full">Lineage</span>
          </TabsTrigger>
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

        {/* ✅ PHASE 4.3: Relationship Mapping Tab */}
        <TabsContent value="relationship-mapping">
          <Card>
            <CardHeader>
              <CardTitle>Relationship Mapping</CardTitle>
              <CardDescription>
                Visualize entity-relationship graphs to explore connections and patterns in your data.
                Discover how entities relate to each other with interactive graph exploration.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <RelationshipMapping 
                onMappingComplete={(result) => {
                  // Update state if needed
                  console.log("Relationship mapping completed:", result);
                }}
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

