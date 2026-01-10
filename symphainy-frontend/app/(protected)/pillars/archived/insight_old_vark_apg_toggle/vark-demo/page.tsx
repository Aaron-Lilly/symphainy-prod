"use client";

import React from "react";

// Force dynamic rendering to avoid SSR issues
export const dynamic = 'force-dynamic';
import { VARKInsightsPanel } from "@/components/insights/VARKInsightsPanel";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Lightbulb, 
  Users, 
  TrendingUp, 
  FileText,
  BarChart3,
  Table as TableIcon
} from "lucide-react";

export default function VARKDemoPage() {
  return (
    <div className="flex-grow space-y-8 min-h-screen">
      {/* Header */}
      <div className="text-center py-8">
        <h1 className="text-3xl font-bold mb-4">VARK-Aligned Insights Demo</h1>
        <p className="text-lg text-gray-600 max-w-3xl mx-auto">
          Experience our revolutionary learning-style optimized data exploration interface. 
          This demo showcases how we've transformed the insights pillar from a confusing 
          four-tab interface into an intuitive, VARK-aligned experience.
        </p>
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

      {/* Demo Component */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lightbulb className="h-5 w-5 text-yellow-600" />
            Interactive VARK Insights Demo
          </CardTitle>
          <p className="text-sm text-gray-600">
            Try the new VARK-aligned interface below. Select a parsed file, choose your 
            learning style, and explore insights in a way that matches your preferences.
          </p>
        </CardHeader>
        <CardContent>
          <VARKInsightsPanel />
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