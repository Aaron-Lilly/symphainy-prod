"use client";

import React, { useEffect, useState } from "react";

// Force dynamic rendering to avoid SSR issues
export const dynamic = 'force-dynamic';
import { VARKInsightsPanel } from "./components/VARKInsightsPanel";
import { APGInsightsPanel } from "./components/APGInsightsPanel";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
// import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { 
  Lightbulb, 
  Users, 
  TrendingUp, 
  FileText,
  BarChart3,
  Table as TableIcon,
  Brain,
  Shield
} from "lucide-react";
import { useSetAtom } from "jotai";
import { chatbotAgentInfoAtom, mainChatbotOpenAtom } from "@/shared/atoms/chatbot-atoms";
import { SecondaryChatbotAgent, SecondaryChatbotTitle } from "@/shared/types/secondaryChatbot";

export default function InsightsPillar() {
  const setAgentInfo = useSetAtom(chatbotAgentInfoAtom);
  const setMainChatbotOpen = useSetAtom(mainChatbotOpenAtom);
  const [activeMode, setActiveMode] = useState<'vark' | 'apg'>('vark');

  // Set up Insights Liaison Agent as secondary option (not default)
  useEffect(() => {
    // Configure the secondary agent but don't show it by default
    setAgentInfo({
      agent: SecondaryChatbotAgent.INSIGHTS_LIAISON,
      title: SecondaryChatbotTitle.INSIGHTS_LIAISON,
      file_url: "",
      additional_info: "Insights analysis and VARK learning style assistance"
    });
    // Keep main chatbot open by default - GuideAgent will be shown
    setMainChatbotOpen(true);
  }, [setAgentInfo, setMainChatbotOpen]);

  return (
    <div className="flex-grow space-y-8 min-h-screen" data-testid="insights-pillar">
      {/* Header */}
      <div className="text-center py-8">
        <h1 className="text-3xl font-bold mb-4">
          {activeMode === 'vark' ? 'VARK-Aligned Insights' : 'APG Exercise Planning Intelligence'}
        </h1>
        <p className="text-lg text-gray-600 max-w-3xl mx-auto mb-6">
          {activeMode === 'vark' 
            ? 'Experience our revolutionary learning-style optimized data exploration interface. This interface transforms insights from a confusing four-tab experience into an intuitive, VARK-aligned journey.'
            : 'Process After Action Reports (AARs) to extract lessons learned, assess risks, and generate exercise planning insights for the Autonomous Proving Ground with cost-optimized AI processing.'
          }
        </p>
        
        {/* Mode Toggle */}
        <div className="flex justify-center" data-testid="apg-mode-toggle">
          <div className="flex bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setActiveMode('vark')}
              className={`flex items-center gap-2 px-4 py-2 rounded-md transition-colors ${
                activeMode === 'vark' 
                  ? 'bg-white text-blue-600 shadow-sm' 
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              <BarChart3 className="h-4 w-4" />
              VARK Analysis
            </button>
            <button
              onClick={() => setActiveMode('apg')}
              className={`flex items-center gap-2 px-4 py-2 rounded-md transition-colors ${
                activeMode === 'apg' 
                  ? 'bg-white text-blue-600 shadow-sm' 
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              <Brain className="h-4 w-4" />
              APG Exercise Planning
            </button>
          </div>
        </div>
      </div>

      {/* Key Features Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-blue-600" />
              File Selection
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600 mb-3">
              Only shows parsed files from the Content pillar, ensuring users have 
              progressed through the proper workflow.
            </p>
            <Badge variant="secondary">Smart City Integration</Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5 text-green-600" />
              VARK Display
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600 mb-3">
              Two elements side by side: Business Summary (auditory proxy) and 
              Learning Style Selector with dynamic panels.
            </p>
            <Badge variant="secondary">Learning-Style Optimized</Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lightbulb className="h-5 w-5 text-purple-600" />
              Summary Section
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600 mb-3">
              Business analysis summary with visual/tabular output, ready to save 
              and share with the Experience pillar.
            </p>
            <Badge variant="secondary">Cross-Pillar Integration</Badge>
          </CardContent>
        </Card>
      </div>

      {/* Learning Styles Explanation */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            VARK Learning Styles Explained
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h4 className="font-semibold text-gray-800">Visual Learners</h4>
              <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg">
                <BarChart3 className="h-6 w-6 text-blue-600" />
                <div>
                  <p className="text-sm font-medium">Charts & Graphs</p>
                  <p className="text-xs text-gray-600">Prefer visual representations of data</p>
                </div>
              </div>
              <p className="text-sm text-gray-600">
                Our visual panel provides interactive charts, trend analysis, and 
                distribution graphs that adapt based on data depth exploration.
              </p>
            </div>

            <div className="space-y-4">
              <h4 className="font-semibold text-gray-800">Read/Write Learners</h4>
              <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg">
                <TableIcon className="h-6 w-6 text-green-600" />
                <div>
                  <p className="text-sm font-medium">Tabular Data</p>
                  <p className="text-xs text-gray-600">Prefer structured, text-based information</p>
                </div>
              </div>
              <p className="text-sm text-gray-600">
                Our tabular panel provides organized data tables with expandable 
                detail levels and export capabilities.
              </p>
            </div>
          </div>

          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <h4 className="font-semibold text-gray-800 mb-2">Auditory-Friendly Business Summary</h4>
            <p className="text-sm text-gray-600">
              The business analysis summary serves as an auditory proxy, providing 
              narrative insights that can be easily understood when read aloud or 
              discussed in meetings.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Interactive VARK Insights Component */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lightbulb className="h-5 w-5 text-yellow-600" />
            Interactive VARK Insights
          </CardTitle>
          <p className="text-sm text-gray-600">
            Select a parsed file, choose your learning style, and explore insights 
            in a way that matches your preferences.
          </p>
        </CardHeader>
        <CardContent>
          {activeMode === 'vark' ? <VARKInsightsPanel /> : <APGInsightsPanel />}
        </CardContent>
      </Card>

      {/* Benefits Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">What We Fixed</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-start gap-2">
                <div className="w-1.5 h-1.5 bg-red-500 rounded-full mt-2 flex-shrink-0"></div>
                Eliminated confusing four-tab interface
              </li>
              <li className="flex items-start gap-2">
                <div className="w-1.5 h-1.5 bg-red-500 rounded-full mt-2 flex-shrink-0"></div>
                Removed non-MECE analytic capabilities
              </li>
              <li className="flex items-start gap-2">
                <div className="w-1.5 h-1.5 bg-red-500 rounded-full mt-2 flex-shrink-0"></div>
                Fixed impractical user experience
              </li>
              <li className="flex items-start gap-2">
                <div className="w-1.5 h-1.5 bg-red-500 rounded-full mt-2 flex-shrink-0"></div>
                Resolved "ridiculous" UI design
              </li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">What We Achieved</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-start gap-2">
                <div className="w-1.5 h-1.5 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                VARK-aligned learning experience
              </li>
              <li className="flex items-start gap-2">
                <div className="w-1.5 h-1.5 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                Intuitive three-section layout
              </li>
              <li className="flex items-start gap-2">
                <div className="w-1.5 h-1.5 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                Smart City architecture integration
              </li>
              <li className="flex items-start gap-2">
                <div className="w-1.5 h-1.5 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                Cross-pillar data sharing capabilities
              </li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
