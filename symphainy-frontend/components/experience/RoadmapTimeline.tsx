"use client";

import React from "react";
import { useSessionBoundary } from "@/shared/state/SessionBoundaryProvider";
import { usePlatformState } from "@/shared/state/PlatformStateProvider";

interface RoadmapPhase {
  phase: string;
  title: string;
  items: string[];
}

interface RoadmapTimelineProps {
  roadmapData?: string;
}

const RoadmapTimeline: React.FC<RoadmapTimelineProps> = ({ roadmapData }) => {
  // ✅ PHASE 1: Migrated to PlatformStateProvider
  const { getRealmState } = usePlatformState();
  const experienceState = getRealmState("outcomes", "roadmap") || {};
  
  // Use provided roadmapData or fall back to outcomes realm state
  const roadmap = roadmapData || experienceState.roadmapResult?.roadmap || experienceState.roadmap;

  // Parse roadmap string into structured data
  const parseRoadmap = (roadmapText: string): RoadmapPhase[] => {
    if (!roadmapText) return [];
    
    const phases: RoadmapPhase[] = [];
    const phaseBlocks = roadmapText.split(/\n\n+/);
    
    phaseBlocks.forEach((block) => {
      const lines = block.trim().split('\n').filter(line => line.trim());
      if (lines.length < 2) return;
      
      const phaseLine = lines[0];
      const items = lines.slice(1).filter(line => line.trim().startsWith('-'));
      
      if (phaseLine && items.length > 0) {
        // Extract phase info from line like "Phase 1: Foundation (Weeks X-Y)"
        const phaseMatch = phaseLine.match(/Phase \d+: (.+?) \(Weeks (.+?)\)/);
        const title = phaseMatch ? phaseMatch[1] : phaseLine;
        const phase = phaseMatch ? `Phase ${phaseMatch[1]} (Weeks ${phaseMatch[2]})` : phaseLine;
        
        phases.push({
          phase,
          title,
          items: items.map(item => item.replace(/^-\s*/, '').trim())
        });
      }
    });
    
    return phases;
  };

  const timelineData = parseRoadmap(roadmap);

  // Fallback to default data if no roadmap is available
  if (timelineData.length === 0) {
    return (
      <div className="space-y-6">
        <div className="text-center py-8">
          <h3 className="text-lg font-semibold mb-2">Experience Roadmap</h3>
          <p className="text-muted-foreground mb-4">
            No roadmap data available. Please analyze a file to generate a roadmap.
          </p>
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-700 rounded-lg">
            <span className="text-sm">💡</span>
            <span className="text-sm">Select a file above and click "Analyze" to generate your roadmap</span>
          </div>
        </div>
        
        {/* Placeholder roadmap structure */}
        <div className="space-y-8 opacity-50">
          <div className="pl-8 relative border-l-2 border-gray-200">
            <div className="absolute w-4 h-4 bg-gray-300 rounded-full -left-2 top-1 border-4 border-white"></div>
            <p className="text-sm font-semibold text-gray-400">Phase 1: Foundation (Weeks 1-4)</p>
            <h3 className="text-lg font-semibold text-gray-400 mt-1">Data Integration & Initial Insights</h3>
            <ul className="list-disc pl-5 mt-2 space-y-1 text-gray-400">
              <li>Upload and validate data sources</li>
              <li>Establish baseline metrics</li>
              <li>Identify key stakeholders</li>
            </ul>
          </div>
          
          <div className="pl-8 relative border-l-2 border-gray-200">
            <div className="absolute w-4 h-4 bg-gray-300 rounded-full -left-2 top-1 border-4 border-white"></div>
            <p className="text-sm font-semibold text-gray-400">Phase 2: Automation (Weeks 5-8)</p>
            <h3 className="text-lg font-semibold text-gray-400 mt-1">Process Optimization & AI Integration</h3>
            <ul className="list-disc pl-5 mt-2 space-y-1 text-gray-400">
              <li>Implement automated workflows</li>
              <li>Deploy AI assistance tools</li>
              <li>Monitor performance metrics</li>
            </ul>
          </div>
          
          <div className="pl-8 relative border-l-2 border-gray-200">
            <div className="absolute w-4 h-4 bg-gray-300 rounded-full -left-2 top-1 border-4 border-white"></div>
            <p className="text-sm font-semibold text-gray-400">Phase 3: Coexistence (Weeks 9-12)</p>
            <h3 className="text-lg font-semibold text-gray-400 mt-1">Human-AI Collaboration & Scaling</h3>
            <ul className="list-disc pl-5 mt-2 space-y-1 text-gray-400">
              <li>Optimize human-AI workflows</li>
              <li>Scale successful patterns</li>
              <li>Establish continuous improvement</li>
            </ul>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {timelineData.map((event, index) => (
        <div
          key={index}
          className="pl-8 relative border-l-2 border-gray-200 dark:border-gray-700"
        >
          <div className="absolute w-4 h-4 bg-blue-500 rounded-full -left-2 top-1 border-4 border-white dark:border-gray-900"></div>
          <p className="text-sm font-semibold text-gray-500">{event.phase}</p>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mt-1">
            {event.title}
          </h3>
          <ul className="list-disc pl-5 mt-2 space-y-1 text-gray-600 dark:text-gray-400">
            {event.items.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
};

export default RoadmapTimeline;
