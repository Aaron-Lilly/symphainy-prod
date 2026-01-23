"use client";

import React from "react";
import { Loader } from "lucide-react";
import DataMashTutorial from "./DataMashTutorial";
import InsightsEcosystem from "./InsightsEcosystem";
import JourneyFrictionRemoval from "./JourneyFrictionRemoval";

interface RealmVisual {
  realm: string;
  title: string;
  visual_type: string;
  primary_visual?: any;
  secondary_metrics?: any;
  capabilities?: any;
  coexistence_analysis?: any;
  status: "completed" | "pending";
}

interface SummaryVisualizationProps {
  realmVisuals?: {
    content_visual?: RealmVisual;
    insights_visual?: RealmVisual;
    journey_visual?: RealmVisual;
  };
  synthesis?: any;
  onVisualizationReady?: (visualUrl: string) => void;
}

export default function SummaryVisualization({
  realmVisuals,
  synthesis,
  onVisualizationReady
}: SummaryVisualizationProps) {
  const contentVisual = realmVisuals?.content_visual;
  const insightsVisual = realmVisuals?.insights_visual;
  const journeyVisual = realmVisuals?.journey_visual;

  return (
    <div className="space-y-6">
      {/* Content Pillar - Data Mash Tutorial */}
      {contentVisual && contentVisual.visual_type === "data_mash_tutorial" && contentVisual.primary_visual ? (
        <DataMashTutorial
          stages={contentVisual.primary_visual.stages || []}
          flowConnections={contentVisual.primary_visual.flow_connections || []}
        />
      ) : contentVisual ? (
        <div className="text-center py-12 text-gray-400">
          <Loader className="w-8 h-8 mx-auto mb-2 animate-spin" />
          <p className="text-sm">Loading Data Mash tutorial...</p>
        </div>
      ) : null}

      {/* Insights Pillar - Insights Ecosystem */}
      {insightsVisual && insightsVisual.visual_type === "insights_ecosystem" && insightsVisual.capabilities ? (
        <InsightsEcosystem capabilities={insightsVisual.capabilities} />
      ) : insightsVisual ? (
        <div className="text-center py-12 text-gray-400">
          <Loader className="w-8 h-8 mx-auto mb-2 animate-spin" />
          <p className="text-sm">Loading insights ecosystem...</p>
        </div>
      ) : null}

      {/* Journey Pillar - Friction Removal */}
      {journeyVisual && journeyVisual.visual_type === "friction_removal" && journeyVisual.coexistence_analysis ? (
        <JourneyFrictionRemoval coexistence_analysis={journeyVisual.coexistence_analysis} />
      ) : journeyVisual ? (
        <div className="text-center py-12 text-gray-400">
          <Loader className="w-8 h-8 mx-auto mb-2 animate-spin" />
          <p className="text-sm">Loading coexistence analysis...</p>
        </div>
      ) : null}
    </div>
  );
}
