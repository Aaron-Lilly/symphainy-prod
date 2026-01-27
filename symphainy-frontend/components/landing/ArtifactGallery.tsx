"use client";

import React, { useState, useMemo } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ArtifactCard, ArtifactCardData } from "./ArtifactCard";
import { usePlatformState } from "@/shared/state/PlatformStateProvider";
import { ChevronRight, Filter } from "lucide-react";
import { useRouter } from "next/navigation";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export function ArtifactGallery() {
  const router = useRouter();
  const { getRealmState } = usePlatformState();
  const [showAll, setShowAll] = useState(false);
  const [filterType, setFilterType] = useState<string>("all");

  // ✅ PHASE 2.1: Retrieve artifacts from realm states
  const artifacts = useMemo(() => {
    const allArtifacts: ArtifactCardData[] = [];

    // Get artifacts from Outcomes realm (roadmaps, POCs, blueprints)
    const outcomesState = getRealmState("outcomes", "artifacts") || {};
    if (outcomesState.roadmap) {
      allArtifacts.push({
        id: outcomesState.roadmap.id || "roadmap-1",
        type: "roadmap",
        title: outcomesState.roadmap.title || "Strategic Roadmap",
        description: outcomesState.roadmap.description || "Strategic roadmap for business transformation",
        status: outcomesState.roadmap.status || "active",
        createdAt: outcomesState.roadmap.createdAt || new Date(),
        metadata: outcomesState.roadmap,
      });
    }
    if (outcomesState.poc) {
      allArtifacts.push({
        id: outcomesState.poc.id || "poc-1",
        type: "poc",
        title: outcomesState.poc.title || "Proof of Concept",
        description: outcomesState.poc.description || "POC proposal for validation",
        status: outcomesState.poc.status || "draft",
        createdAt: outcomesState.poc.createdAt || new Date(),
        metadata: outcomesState.poc,
      });
    }
    if (outcomesState.blueprint) {
      allArtifacts.push({
        id: outcomesState.blueprint.id || "blueprint-1",
        type: "blueprint",
        title: outcomesState.blueprint.title || "Coexistence Blueprint",
        description: outcomesState.blueprint.description || "Blueprint for system coexistence",
        status: outcomesState.blueprint.status || "active",
        createdAt: outcomesState.blueprint.createdAt || new Date(),
        metadata: outcomesState.blueprint,
      });
    }

    // Get artifacts from Journey realm (SOPs, workflows)
    const journeyState = getRealmState("journey", "artifacts") || {};
    if (journeyState.sop) {
      allArtifacts.push({
        id: journeyState.sop.id || "sop-1",
        type: "sop",
        title: journeyState.sop.title || "Standard Operating Procedure",
        description: journeyState.sop.description || "SOP for process execution",
        status: journeyState.sop.status || "active",
        createdAt: journeyState.sop.createdAt || new Date(),
        metadata: journeyState.sop,
      });
    }
    if (journeyState.workflow) {
      allArtifacts.push({
        id: journeyState.workflow.id || "workflow-1",
        type: "workflow",
        title: journeyState.workflow.title || "Workflow Definition",
        description: journeyState.workflow.description || "Workflow for process automation",
        status: journeyState.workflow.status || "active",
        createdAt: journeyState.workflow.createdAt || new Date(),
        metadata: journeyState.workflow,
      });
    }

    // Sort by creation date (newest first)
    return allArtifacts.sort((a, b) => {
      const dateA = a.createdAt ? new Date(a.createdAt).getTime() : 0;
      const dateB = b.createdAt ? new Date(b.createdAt).getTime() : 0;
      return dateB - dateA;
    });
  }, [getRealmState]);

  // Filter artifacts by type
  const filteredArtifacts = useMemo(() => {
    if (filterType === "all") return artifacts;
    return artifacts.filter(a => a.type === filterType);
  }, [artifacts, filterType]);

  // ✅ PHASE 2.1: Show 6 artifacts initially, with "Show All" option
  const displayedArtifacts = showAll ? filteredArtifacts : filteredArtifacts.slice(0, 6);
  const hasMore = filteredArtifacts.length > 6;

  const handleArtifactClick = (artifact: ArtifactCardData) => {
    // Navigate to appropriate pillar based on artifact type
    if (artifact.type === "roadmap" || artifact.type === "poc" || artifact.type === "blueprint") {
      router.push("/pillars/business-outcomes");
    } else if (artifact.type === "sop" || artifact.type === "workflow") {
      router.push("/pillars/journey");
    }
  };

  if (artifacts.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Artifact Gallery</CardTitle>
          <CardDescription>
            Your Purpose-Bound Outcomes will appear here once you generate roadmaps, POCs, blueprints, SOPs, or workflows.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-gray-500">
            <p>No artifacts yet. Start your journey to create artifacts!</p>
            <Button
              className="mt-4"
              onClick={() => router.push("/pillars/content")}
            >
              Start Journey
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Artifact Gallery</CardTitle>
            <CardDescription>
              Your Purpose-Bound Outcomes: roadmaps, POCs, blueprints, SOPs, and workflows
            </CardDescription>
          </div>
          <Badge variant="outline">{artifacts.length} artifacts</Badge>
        </div>
      </CardHeader>
      <CardContent>
        {/* Filter */}
        <div className="mb-4 flex items-center gap-2">
          <Filter className="h-4 w-4 text-gray-500" />
          <Select value={filterType} onValueChange={setFilterType}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Filter by type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              <SelectItem value="roadmap">Roadmaps</SelectItem>
              <SelectItem value="poc">POCs</SelectItem>
              <SelectItem value="blueprint">Blueprints</SelectItem>
              <SelectItem value="sop">SOPs</SelectItem>
              <SelectItem value="workflow">Workflows</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Artifact Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {displayedArtifacts.map((artifact) => (
            <ArtifactCard
              key={artifact.id}
              artifact={artifact}
              onClick={() => handleArtifactClick(artifact)}
            />
          ))}
        </div>

        {/* Show All / Show Less Button */}
        {hasMore && (
          <div className="mt-6 text-center">
            <Button
              variant="outline"
              onClick={() => setShowAll(!showAll)}
            >
              {showAll ? (
                <>
                  Show Less
                </>
              ) : (
                <>
                  Show All ({filteredArtifacts.length} artifacts)
                  <ChevronRight className="ml-2 h-4 w-4" />
                </>
              )}
            </Button>
          </div>
        )}

        {/* Link to Artifact Library */}
        <div className="mt-6 text-center">
          <Button
            variant="ghost"
            onClick={() => router.push("/artifacts")}
          >
            View Full Artifact Library
            <ChevronRight className="ml-2 h-4 w-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
