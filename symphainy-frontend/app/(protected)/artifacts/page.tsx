"use client";

import React, { useState, useMemo } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ArtifactCard, ArtifactCardData } from "@/components/landing/ArtifactCard";
import { usePlatformState } from "@/shared/state/PlatformStateProvider";
import { Search, Filter, Download, Eye } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useRouter } from "next/navigation";

export default function ArtifactLibraryPage() {
  const router = useRouter();
  const { getRealmState } = usePlatformState();
  const [searchQuery, setSearchQuery] = useState("");
  const [filterType, setFilterType] = useState<string>("all");
  const [filterStatus, setFilterStatus] = useState<string>("all");

  // ✅ PHASE 2.2: Aggregate artifacts from all realms
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

  // ✅ PHASE 2.2: Filter and search artifacts
  const filteredArtifacts = useMemo(() => {
    let filtered = artifacts;

    // Filter by type
    if (filterType !== "all") {
      filtered = filtered.filter(a => a.type === filterType);
    }

    // Filter by status
    if (filterStatus !== "all") {
      filtered = filtered.filter(a => a.status === filterStatus);
    }

    // Search by name/description
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(a => 
        a.title.toLowerCase().includes(query) ||
        (a.description && a.description.toLowerCase().includes(query))
      );
    }

    return filtered;
  }, [artifacts, filterType, filterStatus, searchQuery]);

  const handleArtifactClick = (artifact: ArtifactCardData) => {
    // Navigate to appropriate pillar based on artifact type
    if (artifact.type === "roadmap" || artifact.type === "poc" || artifact.type === "blueprint") {
      router.push("/pillars/business-outcomes");
    } else if (artifact.type === "sop" || artifact.type === "workflow") {
      router.push("/pillars/journey");
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 space-y-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800">Artifact Library</h1>
        <p className="text-gray-600 mt-2">
          View and manage all your Purpose-Bound Outcomes: roadmaps, POCs, blueprints, SOPs, and workflows
        </p>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardHeader>
          <CardTitle>Filters & Search</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search by name or description..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>

            {/* Type Filter */}
            <Select value={filterType} onValueChange={setFilterType}>
              <SelectTrigger>
                <Filter className="h-4 w-4 mr-2" />
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

            {/* Status Filter */}
            <Select value={filterStatus} onValueChange={setFilterStatus}>
              <SelectTrigger>
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="draft">Draft</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="archived">Archived</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Results Summary */}
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600">
            Showing <span className="font-semibold">{filteredArtifacts.length}</span> of{" "}
            <span className="font-semibold">{artifacts.length}</span> artifacts
          </p>
        </div>
        {(filterType !== "all" || filterStatus !== "all" || searchQuery.trim()) && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setFilterType("all");
              setFilterStatus("all");
              setSearchQuery("");
            }}
          >
            Clear Filters
          </Button>
        )}
      </div>

      {/* Artifact Grid */}
      {filteredArtifacts.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-gray-500 mb-4">
              {artifacts.length === 0
                ? "No artifacts yet. Start your journey to create artifacts!"
                : "No artifacts match your filters. Try adjusting your search or filters."}
            </p>
            {artifacts.length === 0 && (
              <Button onClick={() => router.push("/pillars/content")}>
                Start Journey
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredArtifacts.map((artifact) => (
            <ArtifactCard
              key={artifact.id}
              artifact={artifact}
              onClick={() => handleArtifactClick(artifact)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
