"use client";

import React, { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  Upload, 
  FileSearch, 
  Brain, 
  Lightbulb, 
  CheckCircle2, 
  Circle, 
  ChevronDown, 
  ChevronUp,
  ArrowRight
} from "lucide-react";

interface TutorialStage {
  id: string;
  name: string;
  icon: string;
  status: "complete" | "pending";
  count: number;
  tutorial: {
    what_happens: string;
    why_it_matters: string;
    think_of_it_like: string[];
    example: any;
  };
}

interface DataMashTutorialProps {
  stages: TutorialStage[];
  flowConnections: Array<{ from: string; to: string; status: string }>;
}

const iconMap: Record<string, React.ComponentType<any>> = {
  upload: Upload,
  parse: FileSearch,
  brain: Brain,
  lightbulb: Lightbulb,
};

export default function DataMashTutorial({ stages, flowConnections }: DataMashTutorialProps) {
  const [expandedStages, setExpandedStages] = useState<Set<string>>(new Set());

  const toggleStage = (stageId: string) => {
    const newExpanded = new Set(expandedStages);
    if (newExpanded.has(stageId)) {
      newExpanded.delete(stageId);
    } else {
      newExpanded.add(stageId);
    }
    setExpandedStages(newExpanded);
  };

  const getStatusColor = (status: string) => {
    return status === "complete" ? "text-green-600" : "text-gray-400";
  };

  const getConnectionStatus = (from: string, to: string) => {
    const connection = flowConnections.find(c => c.from === from && c.to === to);
    return connection?.status || "pending";
  };

  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle>Data Mash: How Your Data Transforms</CardTitle>
        <CardDescription>
          Follow your data's journey from raw files to meaningful insights. Click each stage to learn more.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Pipeline Flow Visualization */}
          <div className="flex items-center justify-between gap-4 overflow-x-auto pb-4">
            {stages.map((stage, index) => {
              const IconComponent = iconMap[stage.icon] || Circle;
              const isExpanded = expandedStages.has(stage.id);
              const isComplete = stage.status === "complete";
              
              return (
                <React.Fragment key={stage.id}>
                  <div className="flex-shrink-0 w-full sm:w-auto">
                    <Card 
                      className={`cursor-pointer transition-all hover:shadow-md ${
                        isExpanded ? "border-blue-500 shadow-lg" : ""
                      }`}
                      onClick={() => toggleStage(stage.id)}
                    >
                      <CardContent className="p-4">
                        <div className="flex flex-col items-center text-center space-y-2">
                          <div className={`p-3 rounded-full ${isComplete ? "bg-green-100" : "bg-gray-100"}`}>
                            <IconComponent className={`w-6 h-6 ${getStatusColor(stage.status)}`} />
                          </div>
                          <div>
                            <h3 className="font-semibold text-sm">{stage.name}</h3>
                            <div className="flex items-center justify-center gap-1 mt-1">
                              {isComplete ? (
                                <CheckCircle2 className="w-4 h-4 text-green-600" />
                              ) : (
                                <Circle className="w-4 h-4 text-gray-400" />
                              )}
                              <span className="text-xs text-gray-600">{stage.count}</span>
                            </div>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-xs"
                            onClick={(e) => {
                              e.stopPropagation();
                              toggleStage(stage.id);
                            }}
                          >
                            {isExpanded ? (
                              <>
                                <ChevronUp className="w-3 h-3 mr-1" />
                                Hide Details
                              </>
                            ) : (
                              <>
                                <ChevronDown className="w-3 h-3 mr-1" />
                                Learn More
                              </>
                            )}
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                  
                  {/* Connection Arrow */}
                  {index < stages.length - 1 && (
                    <div className="flex-shrink-0 flex items-center">
                      <ArrowRight 
                        className={`w-6 h-6 ${
                          getConnectionStatus(stage.id, stages[index + 1].id) === "complete"
                            ? "text-green-600"
                            : "text-gray-300"
                        }`}
                      />
                    </div>
                  )}
                </React.Fragment>
              );
            })}
          </div>

          {/* Expanded Tutorial Content */}
          {stages.map((stage) => {
            if (!expandedStages.has(stage.id)) return null;

            return (
              <Card key={`tutorial-${stage.id}`} className="border-blue-200 bg-blue-50">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{stage.name}</CardTitle>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => toggleStage(stage.id)}
                    >
                      <ChevronUp className="w-4 h-4" />
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* What Happens */}
                  <div>
                    <h4 className="font-semibold mb-2">What happens here?</h4>
                    <p className="text-sm text-gray-700">{stage.tutorial.what_happens}</p>
                  </div>

                  {/* Why It Matters */}
                  <div>
                    <h4 className="font-semibold mb-2">Why it matters:</h4>
                    <p className="text-sm text-gray-700">{stage.tutorial.why_it_matters}</p>
                  </div>

                  {/* Think of it like */}
                  <div>
                    <h4 className="font-semibold mb-2">Think of it like:</h4>
                    <ul className="list-disc pl-5 space-y-1">
                      {stage.tutorial.think_of_it_like.map((item, idx) => (
                        <li key={idx} className="text-sm text-gray-700">{item}</li>
                      ))}
                    </ul>
                  </div>

                  {/* Example */}
                  {stage.tutorial.example && (
                    <div>
                      <h4 className="font-semibold mb-2">Example:</h4>
                      <div className="bg-white p-4 rounded-lg border">
                        {stage.id === "ingestion" && (
                          <div className="space-y-2 text-sm">
                            <p><strong>File:</strong> {stage.tutorial.example.file_name}</p>
                            <p><strong>Type:</strong> {stage.tutorial.example.file_type}</p>
                            <p><strong>Size:</strong> {stage.tutorial.example.file_size}</p>
                            <p><strong>Status:</strong> {stage.tutorial.example.status}</p>
                          </div>
                        )}
                        {stage.id === "parsing" && stage.tutorial.example.before && (
                          <div className="space-y-3">
                            <div>
                              <p className="font-semibold mb-1">Before Parsing:</p>
                              <pre className="bg-gray-100 p-2 rounded text-xs overflow-x-auto">
                                {stage.tutorial.example.before.preview}
                              </pre>
                            </div>
                            <div>
                              <p className="font-semibold mb-1">After Parsing:</p>
                              <div className="bg-gray-100 p-2 rounded text-xs">
                                <p><strong>Columns:</strong></p>
                                <ul className="list-disc pl-5">
                                  {stage.tutorial.example.after?.columns?.map((col: any, idx: number) => (
                                    <li key={idx}>{col.name} ({col.type})</li>
                                  ))}
                                </ul>
                                <p className="mt-2"><strong>Rows:</strong> {stage.tutorial.example.after?.row_count || 0}</p>
                              </div>
                            </div>
                          </div>
                        )}
                        {stage.id === "deterministic_embedding" && stage.tutorial.example.input_structure && (
                          <div className="space-y-3">
                            <div>
                              <p className="font-semibold mb-1">Input Structure:</p>
                              <div className="bg-gray-100 p-2 rounded text-xs">
                                <p><strong>Columns:</strong> {stage.tutorial.example.input_structure.columns.join(", ")}</p>
                                <p><strong>Types:</strong> {stage.tutorial.example.input_structure.types.join(", ")}</p>
                              </div>
                            </div>
                            <div>
                              <p className="font-semibold mb-1">Output Fingerprint:</p>
                              <div className="bg-gray-100 p-2 rounded text-xs">
                                <p><strong>Schema Fingerprint:</strong> {stage.tutorial.example.output_fingerprint.schema_fingerprint}</p>
                                <p><strong>Pattern Signature:</strong> {stage.tutorial.example.output_fingerprint.pattern_signature}</p>
                              </div>
                            </div>
                            <p className="text-xs text-gray-600 italic">{stage.tutorial.example.explanation}</p>
                          </div>
                        )}
                        {stage.id === "interpreted_meaning" && stage.tutorial.example.interpreted_meaning && (
                          <div className="space-y-3">
                            <div>
                              <p className="font-semibold mb-1">Interpreted Meaning:</p>
                              <div className="bg-gray-100 p-2 rounded text-xs">
                                <p><strong>Data Type:</strong> {stage.tutorial.example.interpreted_meaning.data_type}</p>
                                <p className="mt-2"><strong>Relationships:</strong></p>
                                <ul className="list-disc pl-5">
                                  {stage.tutorial.example.interpreted_meaning.relationships.map((rel: string, idx: number) => (
                                    <li key={idx}>{rel}</li>
                                  ))}
                                </ul>
                                <p className="mt-2"><strong>Insights Available:</strong></p>
                                <ul className="list-disc pl-5">
                                  {stage.tutorial.example.interpreted_meaning.insights_available.map((insight: string, idx: number) => (
                                    <li key={idx}>{insight}</li>
                                  ))}
                                </ul>
                              </div>
                            </div>
                            {stage.tutorial.example.example_queries && (
                              <div>
                                <p className="font-semibold mb-1">Example Queries:</p>
                                <ul className="list-disc pl-5 text-xs">
                                  {stage.tutorial.example.example_queries.map((query: string, idx: number) => (
                                    <li key={idx} className="text-gray-700">{query}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
