"use client";
/**
 * Insights Pillar Page
 * 
 * Multi-tenant tabbed interface with conditional sections:
 * 1. Data Quality - Quality assessment with semantic embeddings
 * 2. Data Interpretation - Self-discovery and guided discovery
 * 3. Your Data Mash - Lineage visualization
 * 4. Business Analysis - Structured and unstructured data analysis
 *    - AAR Analysis (AAR tenant)
 *    - PSO Viewer (PSO tenant)
 *    - VLP Extraction (VLP tenant)
 * 5. Relationship Mapping - Entity relationships
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
import { usePlatformState } from "@/shared/state/PlatformStateProvider";
import { useTenant } from "@/shared/contexts/TenantContext";
import { SecondaryChatbotAgent, SecondaryChatbotTitle } from "@/shared/types/secondaryChatbot";
import { DataQualitySection } from "./components/DataQualitySection";
import { DataInterpretationSection } from "./components/DataInterpretationSection";
import { YourDataMash } from "./components/YourDataMash";
import { BusinessAnalysisSection } from "./components/BusinessAnalysisSection";
import { RelationshipMapping } from "./components/RelationshipMapping";
import { AARAnalysisSection } from "./components/AARAnalysisSection";
import { PSOViewer } from "./components/PSOViewer";
import { PermitProcessingSection } from "./components/PermitProcessingSection";
import { VLPExtractionSection } from "./components/VLPExtractionSection";
import { QualityAssessmentResponse, InterpretationResponse, AnalysisResponse, LineageVisualizationResponse } from "@/shared/managers/InsightsAPIManager";
import { PillarCompletionMessage } from "../shared/components/PillarCompletionMessage";
import { Target, FileText, Database } from "lucide-react";

export default function InsightsPage() {
  const { setChatbotAgentInfo, setMainChatbotOpen } = usePlatformState();
  const setAgentInfo = setChatbotAgentInfo;
  
  // Get tenant configuration
  const { currentTenant, isTabEnabled } = useTenant();
  const insightsFeatures = currentTenant.features.insights;
  
  // State for current analysis (to provide context to agent)
  const [currentAnalysisId, setCurrentAnalysisId] = useState<string | null>(null);
  const [dataQualityReport, setDataQualityReport] = useState<QualityAssessmentResponse | null>(null);
  const [dataInterpretation, setDataInterpretation] = useState<InterpretationResponse | null>(null);
  const [lineageVisualization, setLineageVisualization] = useState<LineageVisualizationResponse | null>(null);
  const [businessAnalysis, setBusinessAnalysis] = useState<AnalysisResponse | null>(null);
  
  // AAR Analysis data (for demo)
  const [aarAnalysisData] = useState({
    lessons_learned: [
      {
        lesson_id: 'LL-001',
        category: 'Communication',
        description: 'Radio communication breakdown during phase 2 of the exercise led to delayed response times.',
        importance: 'high' as const,
        actionable_steps: ['Implement redundant communication channels', 'Conduct quarterly radio drills'],
      },
      {
        lesson_id: 'LL-002',
        category: 'Logistics',
        description: 'Supply chain coordination exceeded expectations, enabling rapid deployment.',
        importance: 'medium' as const,
        actionable_steps: ['Document successful logistics procedures', 'Share best practices with other units'],
      },
    ],
    risks: [
      {
        risk_id: 'R-001',
        category: 'Operational',
        description: 'Single point of failure in command structure during night operations.',
        severity: 'high' as const,
        mitigation_strategies: ['Establish backup command hierarchy', 'Cross-train leadership personnel'],
      },
    ],
    recommendations: [
      {
        recommendation_id: 'REC-001',
        area: 'Training',
        recommendation: 'Increase frequency of joint exercises with allied units.',
        priority: 'high' as const,
        estimated_impact: 'Improved inter-operability and response coordination',
      },
    ],
    timeline: [
      {
        timestamp: '2024-01-15T08:00:00Z',
        event: 'Exercise commenced with initial deployment',
        event_type: 'milestone' as const,
      },
      {
        timestamp: '2024-01-15T14:30:00Z',
        event: 'Communication failure reported in sector 3',
        event_type: 'incident' as const,
      },
    ],
  });
  
  // PSO state for viewer
  const [selectedPsoId, setSelectedPsoId] = useState<string | null>(null);

  // Configure Insights Liaison Agent for side panel
  useEffect(() => {
    setAgentInfo({
      agent: SecondaryChatbotAgent.INSIGHTS_LIAISON,
      title: SecondaryChatbotTitle.INSIGHTS_LIAISON,
      file_url: "",
      additional_info: currentTenant.agents?.liaison_agent_prompt_context || 
        "Data quality, interpretation, and business analysis expert. Ask me about data quality assessment, semantic interpretation, lineage visualization, and business insights."
    });
    setMainChatbotOpen(true);
  }, [currentAnalysisId, dataQualityReport, dataInterpretation, lineageVisualization, businessAnalysis, setAgentInfo, setMainChatbotOpen, currentTenant]);

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

  // Calculate enabled tabs for dynamic grid
  const enabledTabs = [
    insightsFeatures.tabs.data_quality,
    insightsFeatures.tabs.data_interpretation,
    insightsFeatures.tabs.your_data_mash,
    insightsFeatures.tabs.business_analysis,
    insightsFeatures.tabs.relationship_mapping,
  ].filter(Boolean).length;

  // Detect completion: user has completed at least one analysis
  const isComplete = dataQualityReport !== null || dataInterpretation !== null || lineageVisualization !== null || businessAnalysis !== null;

  // Get tenant-specific description for Business Analysis
  const getBusinessAnalysisDescription = () => {
    switch (currentTenant.tenant_id) {
      case 'aar':
        return 'Analyze After Action Reports for lessons learned, risks, and recommendations.';
      case 'pso':
        return 'Analyze permit and service order data for compliance and optimization.';
      case 'vlp':
        return 'Analyze policy data for migration readiness and data quality.';
      default:
        return 'Generate actionable business insights from your data.';
    }
  };

  return (
    <div className="flex-grow space-y-6">
      {/* Header */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-h2 font-bold text-gray-800">Insights Pillar</h2>
            <p className="text-lead text-gray-600">
              {currentTenant.tenant_id === 'aar' 
                ? 'Extract actionable insights from After Action Reports with AI-powered analysis.'
                : currentTenant.tenant_id === 'pso'
                ? 'Transform permit and service order data into structured insights.'
                : currentTenant.tenant_id === 'vlp'
                ? 'Analyze policy data for migration readiness and modernization planning.'
                : 'Transform your data into actionable insights with AI-powered analysis.'}
            </p>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 bg-blue-50 border border-blue-200 rounded-lg">
            <span className="text-xs font-semibold text-blue-900">Available:</span>
            <span className="text-xs text-blue-700">Insights Liaison Agent</span>
            <span className="flex h-2 w-2 rounded-full bg-blue-500" title="Liaison agent available" />
          </div>
        </div>
      </div>

      {/* Tabbed Interface */}
      <Tabs defaultValue="data-quality" className="space-y-6">
        <TabsList 
          className="grid w-full" 
          style={{ gridTemplateColumns: `repeat(${enabledTabs}, 1fr)` }}
        >
          {insightsFeatures.tabs.data_quality && (
            <TabsTrigger value="data-quality">Data Quality</TabsTrigger>
          )}
          {insightsFeatures.tabs.data_interpretation && (
            <TabsTrigger value="data-interpretation">Data Interpretation</TabsTrigger>
          )}
          {insightsFeatures.tabs.your_data_mash && (
            <TabsTrigger value="your-data-mash" className="relative">
              Your Data Mash
              <span className="ml-2 px-2 py-0.5 text-xs bg-blue-100 text-blue-800 rounded-full">Lineage</span>
            </TabsTrigger>
          )}
          {insightsFeatures.tabs.business_analysis && (
            <TabsTrigger value="business-analysis">Business Analysis</TabsTrigger>
          )}
          {insightsFeatures.tabs.relationship_mapping && (
            <TabsTrigger value="relationship-mapping">Relationships</TabsTrigger>
          )}
        </TabsList>

        {/* Data Quality Tab */}
        {insightsFeatures.tabs.data_quality && (
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
        )}

        {/* Data Interpretation Tab */}
        {insightsFeatures.tabs.data_interpretation && (
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
        )}

        {/* Your Data Mash Tab */}
        {insightsFeatures.tabs.your_data_mash && (
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
        )}

        {/* Business Analysis Tab - with demo-specific sections */}
        {insightsFeatures.tabs.business_analysis && (
          <TabsContent value="business-analysis">
            <Card>
              <CardHeader>
                <CardTitle>Business Analysis</CardTitle>
                <CardDescription>
                  {getBusinessAnalysisDescription()}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* AAR Analysis Section - Only for AAR and Base tenants */}
                {insightsFeatures.show_aar_analysis && (
                  <div className="mb-6">
                    <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                      <Target className="h-5 w-5 text-blue-600" />
                      AAR Analysis
                    </h3>
                    <AARAnalysisSection 
                      aarAnalysis={aarAnalysisData} 
                      defaultExpanded={currentTenant.tenant_id === 'aar'}
                    />
                  </div>
                )}
                
                {/* PSO Viewer Section - Only for PSO and Base tenants */}
                {insightsFeatures.show_pso_viewer && (
                  <div className="mb-6">
                    <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                      <FileText className="h-5 w-5 text-green-600" />
                      Permit Processing
                    </h3>
                    <PermitProcessingSection />
                    {selectedPsoId && (
                      <div className="mt-4">
                        <PSOViewer psoId={selectedPsoId} onClose={() => setSelectedPsoId(null)} />
                      </div>
                    )}
                  </div>
                )}
                
                {/* VLP Extraction Section - Only for VLP and Base tenants */}
                {insightsFeatures.show_vlp_extraction && (
                  <div className="mb-6">
                    <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                      <Database className="h-5 w-5 text-purple-600" />
                      Policy Data Extraction
                    </h3>
                    <VLPExtractionSection 
                      onExtractionComplete={(result) => {
                        console.log("VLP Extraction completed:", result);
                      }}
                    />
                  </div>
                )}
                
                {/* Standard Business Analysis - Always shown */}
                <div className="pt-4 border-t">
                  <h3 className="text-lg font-semibold mb-4">General Business Analysis</h3>
                  <BusinessAnalysisSection 
                    onAnalysisComplete={handleBusinessAnalysisComplete}
                  />
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        )}

        {/* Relationship Mapping Tab */}
        {insightsFeatures.tabs.relationship_mapping && (
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
                    console.log("Relationship mapping completed:", result);
                  }}
                />
              </CardContent>
            </Card>
          </TabsContent>
        )}
      </Tabs>

      {/* Completion Message */}
      <PillarCompletionMessage
        show={isComplete}
        message="Congratulations! Hopefully those insights have provided a new perspective on your business. You can return to the Content pillar to upload additional data, or proceed to the Operations pillar to put those insights into action, or you can proceed directly to our Business Outcomes page to see how we would recommend applying those insights."
      />
    </div>
  );
}
