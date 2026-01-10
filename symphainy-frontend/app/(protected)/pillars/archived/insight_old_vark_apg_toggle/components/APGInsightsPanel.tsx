"use client";

import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  FileText, 
  Upload, 
  Brain, 
  Shield, 
  TrendingUp, 
  AlertTriangle,
  CheckCircle,
  Clock,
  BarChart3
} from "lucide-react";

interface APGInsightsPanelProps {
  className?: string;
}

interface ProcessingState {
  isProcessing: boolean;
  progress: number;
  currentStep: string;
}

interface AARResult {
  success: boolean;
  filename: string;
  lessons_learned: Array<{
    content: string;
    source_section: string;
    relevance_score: number;
  }>;
  risk_factors: Array<{
    content: string;
    risk_category: string;
    severity: string;
  }>;
  recommendations: Array<{
    type: string;
    priority: string;
    recommendation: string;
  }>;
  outcome_forecasts: {
    predicted_outcomes: string[];
    risk_mitigation_recommendations: string[];
  };
}

export function APGInsightsPanel({ className }: APGInsightsPanelProps) {
  const [processingState, setProcessingState] = useState<ProcessingState>({
    isProcessing: false,
    progress: 0,
    currentStep: ""
  });
  
  const [aarResult, setAarResult] = useState<AARResult | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setSelectedFile(file);
    setProcessingState({
      isProcessing: true,
      progress: 0,
      currentStep: "Uploading file..."
    });

    try {
      // Convert file to base64
      const base64 = await new Promise<string>((resolve) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result as string);
        reader.readAsDataURL(file);
      });

      // Simulate processing steps
      const steps = [
        "Uploading file...",
        "Parsing document...",
        "Extracting lessons learned...",
        "Assessing risks...",
        "Generating forecasts...",
        "Storing insights..."
      ];

      for (let i = 0; i < steps.length; i++) {
        setProcessingState(prev => ({
          ...prev,
          currentStep: steps[i],
          progress: ((i + 1) / steps.length) * 100
        }));
        await new Promise(resolve => setTimeout(resolve, 1000));
      }

      // Mock result for demonstration
      const mockResult: AARResult = {
        success: true,
        filename: file.name,
        lessons_learned: [
          {
            content: "Improved coordination between agencies reduced response time by 30%",
            source_section: "lessons learned",
            relevance_score: 0.95
          },
          {
            content: "Early warning systems prevented 3 potential safety incidents",
            source_section: "successes",
            relevance_score: 0.88
          }
        ],
        risk_factors: [
          {
            content: "Communication delays during high-stress situations",
            risk_category: "operational",
            severity: "medium"
          },
          {
            content: "Resource allocation conflicts between agencies",
            risk_category: "coordination",
            severity: "high"
          }
        ],
        recommendations: [
          {
            type: "coordination",
            priority: "high",
            recommendation: "Implement standardized communication protocols"
          },
          {
            type: "risk_mitigation",
            priority: "high",
            recommendation: "Establish resource sharing agreements"
          }
        ],
        outcome_forecasts: {
          predicted_outcomes: [
            "Improved coordination between agencies",
            "Reduced regulatory compliance time",
            "Enhanced asset utilization"
          ],
          risk_mitigation_recommendations: [
            "Implement early warning systems",
            "Establish backup communication channels",
            "Create contingency resource plans"
          ]
        }
      };

      setAarResult(mockResult);
      setProcessingState({
        isProcessing: false,
        progress: 100,
        currentStep: "Complete!"
      });

    } catch (error) {
      console.error("File processing failed:", error);
      setProcessingState({
        isProcessing: false,
        progress: 0,
        currentStep: "Error occurred"
      });
    }
  };

  return (
    <div className={`space-y-6 ${className}`} data-testid="apg-insights-panel">
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-6 w-6 text-blue-600" />
            APG Exercise Planning Intelligence
          </CardTitle>
          <p className="text-sm text-gray-600">
            Process After Action Reports (AARs) to extract lessons learned, assess risks, 
            and generate exercise planning insights for the Autonomous Proving Ground.
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* File Upload */}
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <div className="space-y-2">
                <h3 className="text-lg font-medium">Upload AAR Document</h3>
                <p className="text-sm text-gray-600">
                  Upload PDF, DOCX, or other document formats containing After Action Reports
                </p>
                <input
                  type="file"
                  accept=".pdf,.docx,.txt"
                  onChange={handleFileUpload}
                  disabled={processingState.isProcessing}
                  className="hidden"
                  id="aar-upload"
                />
                <Button 
                  onClick={() => document.getElementById('aar-upload')?.click()}
                  disabled={processingState.isProcessing}
                  className="mt-4"
                >
                  {processingState.isProcessing ? "Processing..." : "Select AAR File"}
                </Button>
              </div>
            </div>

            {/* Processing Status */}
            {processingState.isProcessing && (
              <Card>
                <CardContent className="pt-6">
                  <div className="space-y-4">
                    <div className="flex items-center gap-2">
                      <Clock className="h-4 w-4 text-blue-600" />
                      <span className="text-sm font-medium">{processingState.currentStep}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${processingState.progress}%` }}
                      />
                    </div>
                    <p className="text-xs text-gray-600">
                      {Math.round(processingState.progress)}% complete
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Results */}
      {aarResult && (
        <Tabs defaultValue="lessons" className="space-y-4">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="lessons">Lessons Learned</TabsTrigger>
            <TabsTrigger value="risks">Risk Assessment</TabsTrigger>
            <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
            <TabsTrigger value="forecasts">Outcome Forecasts</TabsTrigger>
          </TabsList>

          {/* Lessons Learned */}
          <TabsContent value="lessons">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  Lessons Learned
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {aarResult.lessons_learned.map((lesson, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <div className="flex items-start justify-between mb-2">
                        <Badge variant="secondary">{lesson.source_section}</Badge>
                        <Badge variant="outline">
                          {Math.round(lesson.relevance_score * 100)}% relevant
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-700">{lesson.content}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Risk Assessment */}
          <TabsContent value="risks">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5 text-red-600" />
                  Risk Assessment
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {aarResult.risk_factors.map((risk, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <div className="flex items-start justify-between mb-2">
                        <Badge variant="outline">{risk.risk_category}</Badge>
                        <Badge 
                          variant={risk.severity === "high" ? "destructive" : "secondary"}
                        >
                          {risk.severity} severity
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-700">{risk.content}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Recommendations */}
          <TabsContent value="recommendations">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-blue-600" />
                  Exercise Planning Recommendations
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {aarResult.recommendations.map((rec, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <div className="flex items-start justify-between mb-2">
                        <Badge variant="outline">{rec.type}</Badge>
                        <Badge 
                          variant={rec.priority === "high" ? "destructive" : "secondary"}
                        >
                          {rec.priority} priority
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-700">{rec.recommendation}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Outcome Forecasts */}
          <TabsContent value="forecasts">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="h-5 w-5 text-green-600" />
                    Predicted Outcomes
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {aarResult.outcome_forecasts.predicted_outcomes.map((outcome, index) => (
                      <li key={index} className="flex items-center gap-2 text-sm">
                        <CheckCircle className="h-4 w-4 text-green-600" />
                        {outcome}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <AlertTriangle className="h-5 w-5 text-orange-600" />
                    Risk Mitigation
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {aarResult.outcome_forecasts.risk_mitigation_recommendations.map((rec, index) => (
                      <li key={index} className="flex items-center gap-2 text-sm">
                        <Shield className="h-4 w-4 text-orange-600" />
                        {rec}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      )}

      {/* Key Features */}
      <Card>
        <CardHeader>
          <CardTitle>APG Document Intelligence Features</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <h4 className="font-medium text-green-700">Cost Optimization</h4>
              <p className="text-sm text-gray-600">
                Intelligent chunking and relevance scoring reduce AI processing costs by up to 50x
              </p>
            </div>
            <div className="space-y-2">
              <h4 className="font-medium text-blue-700">Pattern Detection</h4>
              <p className="text-sm text-gray-600">
                Identify recurring lessons and risks across multiple exercises for better planning
              </p>
            </div>
            <div className="space-y-2">
              <h4 className="font-medium text-purple-700">Risk Assessment</h4>
              <p className="text-sm text-gray-600">
                Assess potential risks for proposed exercises based on historical data
              </p>
            </div>
            <div className="space-y-2">
              <h4 className="font-medium text-orange-700">Outcome Forecasting</h4>
              <p className="text-sm text-gray-600">
                Predict likely outcomes and generate mitigation strategies for exercise planning
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

