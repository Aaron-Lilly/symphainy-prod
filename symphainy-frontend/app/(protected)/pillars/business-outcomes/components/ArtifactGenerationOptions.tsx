"use client";

import React, { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Loader, FileText, Target, Map, AlertTriangle } from "lucide-react";

interface ArtifactGenerationOptionsProps {
  solutionId?: string;
  workflowId?: string; // For blueprint generation
  onArtifactGenerated: (artifactType: 'blueprint' | 'poc' | 'roadmap', artifactId: string) => void;
  onCreateBlueprint?: (workflowId: string) => Promise<{ success: boolean; blueprint_id?: string; error?: string }>;
  onCreatePOC?: () => Promise<{ success: boolean; proposal_id?: string; error?: string }>;
  onGenerateRoadmap?: () => Promise<{ success: boolean; roadmap_id?: string; error?: string }>;
}

export default function ArtifactGenerationOptions({
  solutionId,
  workflowId,
  onArtifactGenerated,
  onCreateBlueprint,
  onCreatePOC,
  onGenerateRoadmap
}: ArtifactGenerationOptionsProps) {
  const [generating, setGenerating] = useState<'blueprint' | 'poc' | 'roadmap' | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerateBlueprint = async () => {
    if (!workflowId) {
      setError("Workflow ID required for blueprint generation. Please create a workflow in the Journey pillar first.");
      return;
    }

    if (!onCreateBlueprint) {
      setError("Blueprint creation not available");
      return;
    }

    setGenerating('blueprint');
    setError(null);

    try {
      const result = await onCreateBlueprint(workflowId);
      
      if (result.success && result.blueprint_id) {
        onArtifactGenerated('blueprint', result.blueprint_id);
      } else {
        setError(result.error || "Failed to create blueprint");
      }
    } catch (err: any) {
      setError(err.message || "Failed to create blueprint");
    } finally {
      setGenerating(null);
    }
  };

  const handleGeneratePOC = async () => {
    if (!onCreatePOC) {
      setError("POC creation not available");
      return;
    }

    setGenerating('poc');
    setError(null);

    try {
      const result = await onCreatePOC();
      
      if (result.success && result.proposal_id) {
        onArtifactGenerated('poc', result.proposal_id);
      } else {
        setError(result.error || "Failed to create POC proposal");
      }
    } catch (err: any) {
      setError(err.message || "Failed to create POC proposal");
    } finally {
      setGenerating(null);
    }
  };

  const handleGenerateRoadmap = async () => {
    if (!onGenerateRoadmap) {
      setError("Roadmap generation not available");
      return;
    }

    setGenerating('roadmap');
    setError(null);

    try {
      const result = await onGenerateRoadmap();
      
      if (result.success && result.roadmap_id) {
        onArtifactGenerated('roadmap', result.roadmap_id);
      } else {
        setError(result.error || "Failed to generate roadmap");
      }
    } catch (err: any) {
      setError(err.message || "Failed to generate roadmap");
    } finally {
      setGenerating(null);
    }
  };

  return (
    <div className="space-y-4">
      {error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Blueprint Card */}
        <Card className="border-blue-200 hover:border-blue-400 transition-colors">
          <CardHeader>
            <div className="flex items-center space-x-2 mb-2">
              <FileText className="w-6 h-6 text-blue-600" />
              <CardTitle className="text-blue-800">Coexistence Blueprint</CardTitle>
            </div>
            <CardDescription>
              Generate a comprehensive coexistence blueprint with workflow charts, responsibility matrix, and transition roadmap
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button
              onClick={handleGenerateBlueprint}
              disabled={generating !== null || !workflowId}
              className="w-full"
              variant={workflowId ? "default" : "secondary"}
            >
              {generating === 'blueprint' ? (
                <>
                  <Loader className="w-4 h-4 mr-2 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <FileText className="w-4 h-4 mr-2" />
                  Generate Blueprint
                </>
              )}
            </Button>
            {!workflowId && (
              <p className="text-xs text-gray-500 mt-2">
                Requires workflow from Journey pillar
              </p>
            )}
          </CardContent>
        </Card>

        {/* POC Card */}
        <Card className="border-green-200 hover:border-green-400 transition-colors">
          <CardHeader>
            <div className="flex items-center space-x-2 mb-2">
              <Target className="w-6 h-6 text-green-600" />
              <CardTitle className="text-green-800">POC Proposal</CardTitle>
            </div>
            <CardDescription>
              Create a proof of concept proposal with objectives, scope, timeline, and resource requirements
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button
              onClick={handleGeneratePOC}
              disabled={generating !== null}
              className="w-full"
              variant="default"
            >
              {generating === 'poc' ? (
                <>
                  <Loader className="w-4 h-4 mr-2 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Target className="w-4 h-4 mr-2" />
                  Generate POC
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Roadmap Card */}
        <Card className="border-purple-200 hover:border-purple-400 transition-colors">
          <CardHeader>
            <div className="flex items-center space-x-2 mb-2">
              <Map className="w-6 h-6 text-purple-600" />
              <CardTitle className="text-purple-800">Strategic Roadmap</CardTitle>
            </div>
            <CardDescription>
              Generate a strategic roadmap with phases, timeline, milestones, and dependencies
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button
              onClick={handleGenerateRoadmap}
              disabled={generating !== null}
              className="w-full"
              variant="default"
            >
              {generating === 'roadmap' ? (
                <>
                  <Loader className="w-4 h-4 mr-2 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Map className="w-4 h-4 mr-2" />
                  Generate Roadmap
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
